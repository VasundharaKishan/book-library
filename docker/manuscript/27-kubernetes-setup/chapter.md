# Chapter 27: Setting Up Kubernetes Locally

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Install Minikube on Mac, Windows, or Linux
- Install kubectl and verify it works
- Start and stop a local Kubernetes cluster
- Run your first kubectl commands to inspect the cluster
- Understand what namespaces are and how to create them
- Switch between different Kubernetes contexts
- Open the Kubernetes Dashboard to see your cluster visually
- Troubleshoot common setup problems

---

## Why This Chapter Matters

In the previous chapter, you learned what Kubernetes is and how its architecture works. You know about the control plane, worker nodes, the API Server, the Scheduler, etcd, and kubelet. That is a lot of theory.

Now it is time to get your hands dirty. You need a real Kubernetes cluster to practice with, but you do not need a fleet of expensive servers. You can run a fully functional Kubernetes cluster right on your laptop.

This chapter walks you through the setup step by step. By the end, you will have a working cluster and you will have run your first kubectl commands. Every chapter after this one builds on this setup.

---

## Your Options for Running Kubernetes Locally

There are several ways to run Kubernetes on your own machine. Think of these as different ways to set up a practice gym — some are simple, some offer more features, but they all let you practice.

| Tool | Description | Best For |
|------|-------------|----------|
| **Minikube** | Runs a single-node cluster in a virtual machine or container | Learning and development |
| **Docker Desktop** | Includes a built-in Kubernetes option | Docker users who want a quick setup |
| **kind** | Kubernetes in Docker — runs cluster nodes as Docker containers | Testing and CI/CD |
| **k3s** | Lightweight Kubernetes distribution | Raspberry Pi, edge computing |

We will focus on **Minikube** because it is the most popular tool for learning Kubernetes. It works on all operating systems and gives you a complete Kubernetes cluster with one command. We will also cover the Docker Desktop option for those who prefer a simpler setup.

---

## Option A: Installing Minikube

Minikube creates a tiny Kubernetes cluster inside a virtual machine or a Docker container on your laptop. Think of it as a **miniature data center** that fits inside your computer.

### Prerequisites

Before installing Minikube, you need two things:

1. **A container or virtual machine manager.** Minikube needs something to run the cluster inside. If you have Docker installed (which you do if you have been following this book), that is enough.

2. **At least 2 CPUs, 2 GB of free memory, and 20 GB of free disk space.** Kubernetes is not a lightweight tool. Make sure your computer meets these requirements.

### Installing on macOS

**Using Homebrew (recommended):**

```bash
brew install minikube
```

```
==> Downloading https://ghcr.io/v2/homebrew/core/minikube/blobs/sha256:...
==> Installing minikube
==> Pouring minikube--1.32.0.arm64_sonoma.bottle.tar.gz
==> Summary
  /opt/homebrew/Cellar/minikube/1.32.0: 9 files, 93.2MB
```

**What just happened?** Homebrew is a package manager for macOS (like an app store for command-line tools). It downloaded the Minikube binary and placed it in your system path so you can run it from any terminal window.

**Using direct download (if you do not have Homebrew):**

```bash
# For Apple Silicon (M1, M2, M3 Macs):
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-arm64
sudo install minikube-darwin-arm64 /usr/local/bin/minikube

# For Intel Macs:
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
sudo install minikube-darwin-amd64 /usr/local/bin/minikube
```

Let us break down those commands:

- `curl -LO` — Downloads a file from the internet. `-L` follows redirects, `-O` saves the file with its original name.
- `sudo install` — Copies the downloaded file to `/usr/local/bin/` and makes it executable. `sudo` is needed because `/usr/local/bin/` is a system directory.

### Installing on Windows

**Using Windows Package Manager (winget):**

```powershell
winget install Kubernetes.minikube
```

**Using Chocolatey:**

```powershell
choco install minikube
```

**Using direct download:**

1. Download the installer from https://minikube.sigs.k8s.io/docs/start/
2. Run the `.exe` installer
3. Follow the installation wizard

After installation, open a **new** terminal window (this is important — the old terminal will not know about the new command).

### Installing on Linux

**Using direct download:**

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**Using package manager (Debian/Ubuntu):**

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
sudo dpkg -i minikube_latest_amd64.deb
```

**Using package manager (Fedora/RHEL):**

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-latest.x86_64.rpm
sudo rpm -Uvh minikube-latest.x86_64.rpm
```

### Verifying the Installation

After installing, verify it works:

```bash
minikube version
```

```
minikube version: v1.32.0
commit: 8220a6eb95f0a4d75f7f2d7b14cef975f050512d
```

If you see a version number, Minikube is installed correctly.

---

## Option B: Enabling Kubernetes in Docker Desktop

If you already have Docker Desktop installed, you can enable Kubernetes with a few clicks. No additional installation required.

### Steps

1. Open Docker Desktop
2. Click the **gear icon** (Settings)
3. Click **Kubernetes** in the left sidebar
4. Check the box that says **Enable Kubernetes**
5. Click **Apply & Restart**

```
Docker Desktop Settings:

  ┌────────────────────────────────────────────┐
  │  General                                    │
  │  Resources                                  │
  │  Docker Engine                              │
  │  ► Kubernetes  ◄── Click this               │
  │  Software Updates                           │
  │                                             │
  │  ┌──────────────────────────────────┐       │
  │  │ [✓] Enable Kubernetes            │       │
  │  │                                  │       │
  │  │ Kubernetes is starting...        │       │
  │  └──────────────────────────────────┘       │
  │                                             │
  │  [Apply & Restart]                          │
  └────────────────────────────────────────────┘
```

Docker Desktop will download the Kubernetes components and start the cluster. This takes a few minutes the first time. When the Kubernetes icon in the bottom-left corner turns green, the cluster is ready.

### Pros and Cons of Docker Desktop Kubernetes

| Pros | Cons |
|------|------|
| No extra installation needed | Fewer configuration options than Minikube |
| Starts automatically with Docker Desktop | Uses more memory (Docker + Kubernetes) |
| Simple on/off toggle | Cannot easily create multiple clusters |
| Shares Docker's images and resources | Harder to reset if something breaks |

---

## Installing kubectl

**kubectl** (pronounced "kube-control" or "kube-C-T-L") is the command-line tool you use to talk to your Kubernetes cluster. Think of it as the **remote control** for your cluster. Without kubectl, you cannot give commands to Kubernetes.

> **Note:** If you installed Minikube, it comes with its own kubectl. You can use `minikube kubectl -- <command>` instead of `kubectl <command>`. However, installing kubectl separately is recommended because it is more convenient.

### Installing kubectl on macOS

```bash
brew install kubectl
```

```
==> Downloading https://ghcr.io/v2/homebrew/core/kubernetes-cli/blobs/...
==> Installing kubernetes-cli
==> Summary
  /opt/homebrew/Cellar/kubernetes-cli/1.29.2: 236 files, 58.3MB
```

### Installing kubectl on Windows

```powershell
winget install Kubernetes.kubectl
```

Or with Chocolatey:

```powershell
choco install kubernetes-cli
```

### Installing kubectl on Linux

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
```

Let us break this down:

- The inner `curl` command (`curl -L -s https://dl.k8s.io/release/stable.txt`) fetches the latest stable version number (like "v1.29.2").
- The outer `curl` command uses that version number to download the matching kubectl binary.
- `sudo install` makes it executable and moves it to the right location.

### Verifying kubectl

```bash
kubectl version --client
```

```
Client Version: v1.29.2
Kustomize Version: v5.0.4-0.20230601165947-6ce0bf390ce3
```

The `--client` flag tells kubectl to only show its own version, not try to connect to a cluster (which might not be running yet).

---

## Starting Your First Cluster

Now comes the exciting part. Let us start a Kubernetes cluster.

### Starting Minikube

```bash
minikube start
```

```
😄  minikube v1.32.0 on Darwin 14.0 (arm64)
✨  Automatically selected the docker driver. Other choices: qemu2, ssh
📌  Using Docker Desktop driver with root privileges
👍  Starting control plane node minikube in cluster minikube
🚜  Pulling base image ...
💾  Downloading Kubernetes v1.28.3 preload ...
🔥  Creating docker container (CPUs=2, Memory=4096MB, Disk=20000MB) ...
🐳  Preparing Kubernetes v1.28.3 on Docker 24.0.7 ...
    ▪ Generating certificates and keys ...
    ▪ Booting up control plane ...
    ▪ Configuring RBAC rules ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔎  Verifying Kubernetes components...
    ▪ Using image gcr.io/k8s-minikube/storage-provisioner:v5
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and
    "default" namespace by default
```

**What just happened?** Let us walk through each line:

1. Minikube detected your operating system and chose Docker as the driver (the tool to create the virtual environment).
2. It downloaded the Kubernetes base image — a pre-built package containing all Kubernetes components.
3. It created a Docker container with 2 CPUs and 4 GB of memory to act as your cluster node.
4. It installed Kubernetes v1.28.3 inside that container.
5. It generated security certificates (like ID cards for cluster components to identify themselves).
6. It started the control plane (API Server, Scheduler, Controller Manager, etcd).
7. It configured networking so Pods can communicate.
8. It verified everything is working.
9. It configured kubectl to talk to this new cluster.

Your local Kubernetes cluster is now running. All the components from Chapter 26 — the API Server, Scheduler, Controller Manager, etcd, kubelet, and kube-proxy — are all running inside a single Docker container on your machine.

```
Your Laptop
┌─────────────────────────────────────────────┐
│                                             │
│   Docker                                    │
│   ┌───────────────────────────────────────┐ │
│   │  Minikube Container                   │ │
│   │  ┌─────────────────────────────────┐  │ │
│   │  │     Control Plane               │  │ │
│   │  │  API Server  Scheduler          │  │ │
│   │  │  Controller  etcd               │  │ │
│   │  │  Manager                        │  │ │
│   │  ├─────────────────────────────────┤  │ │
│   │  │     Worker Node                 │  │ │
│   │  │  kubelet  kube-proxy            │  │ │
│   │  │  Container Runtime              │  │ │
│   │  └─────────────────────────────────┘  │ │
│   └───────────────────────────────────────┘ │
│                                             │
│   kubectl  ◄── You type commands here       │
└─────────────────────────────────────────────┘
```

In a real production cluster, the control plane and worker nodes would be on separate machines. Minikube puts everything on one machine for simplicity.

---

## Your First kubectl Commands

Now that the cluster is running, let us explore it.

### Checking Cluster Information

```bash
kubectl cluster-info
```

```
Kubernetes control plane is running at https://127.0.0.1:55000
CoreDNS is running at https://127.0.0.1:55000/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

**What does this tell you?**

- The **control plane** (API Server) is running on your local machine (`127.0.0.1`) on port 55000.
- **CoreDNS** is running — this is Kubernetes' built-in DNS service that lets Pods find each other by name (like a phone book for your cluster).

### Listing Nodes

```bash
kubectl get nodes
```

```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   2m    v1.28.3
```

Let us break down each column:

| Column | Meaning |
|--------|---------|
| **NAME** | The name of the node. Minikube creates one node called "minikube". |
| **STATUS** | Whether the node is healthy. "Ready" means it can accept workloads. |
| **ROLES** | What role this node plays. "control-plane" means it runs the brain of the cluster. In Minikube, the same node also acts as a worker. |
| **AGE** | How long the node has been running. |
| **VERSION** | The version of Kubernetes running on this node. |

In a real cluster, you would see multiple nodes:

```bash
# What a production cluster might look like:
kubectl get nodes
```

```
NAME              STATUS   ROLES           AGE   VERSION
master-1          Ready    control-plane   30d   v1.28.3
worker-1          Ready    <none>          30d   v1.28.3
worker-2          Ready    <none>          30d   v1.28.3
worker-3          Ready    <none>          25d   v1.28.3
```

### Getting More Details About a Node

```bash
kubectl describe node minikube
```

```
Name:               minikube
Roles:              control-plane
Labels:             kubernetes.io/hostname=minikube
                    node-role.kubernetes.io/control-plane=
Annotations:        kubeadm.alpha.kubernetes.io/cri-socket: ...
CreationTimestamp:   Mon, 15 Jan 2024 10:30:00 -0500
Conditions:
  Type             Status
  ----             ------
  MemoryPressure   False
  DiskPressure     False
  PIDPressure      False
  Ready            True
Capacity:
  cpu:                2
  memory:             4046788Ki
  pods:               110
Allocatable:
  cpu:                2
  memory:             4046788Ki
  pods:               110
...
```

This shows detailed information about the node:

- **Conditions** — Is the node under memory pressure? Disk pressure? Is it ready? All False/True values look healthy here.
- **Capacity** — The total resources available: 2 CPUs, about 4 GB of memory, and room for up to 110 Pods.
- **Allocatable** — How much of those resources Kubernetes can actually use for your workloads.

---

## Understanding Namespaces

### What Is a Namespace?

A **namespace** is a way to divide your Kubernetes cluster into separate sections. Think of it as **folders on your computer**. You do not put every file on your desktop — you organize them into folders like "Work," "Personal," and "Projects." Namespaces do the same thing for Kubernetes resources.

```
Without Namespaces (messy):
┌────────────────────────────────────────┐
│  Kubernetes Cluster                     │
│                                         │
│  frontend-pod    backend-pod            │
│  database-pod    test-frontend-pod      │
│  test-backend    staging-database       │
│  monitoring-pod  logging-pod            │
│                                         │
│  Everything mixed together!             │
└────────────────────────────────────────┘

With Namespaces (organized):
┌────────────────────────────────────────┐
│  Kubernetes Cluster                     │
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ production   │  │ staging      │    │
│  │              │  │              │    │
│  │ frontend-pod │  │ frontend-pod │    │
│  │ backend-pod  │  │ backend-pod  │    │
│  │ database-pod │  │ database-pod │    │
│  └──────────────┘  └──────────────┘    │
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ monitoring   │  │ testing      │    │
│  │              │  │              │    │
│  │ prometheus   │  │ test-runner  │    │
│  │ grafana      │  │ test-db      │    │
│  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────┘
```

### Why Use Namespaces?

1. **Organization** — Keep different projects or environments separate.
2. **Access control** — Limit who can access resources in each namespace.
3. **Resource limits** — Set CPU and memory limits per namespace so one team cannot use all the resources.
4. **Name reuse** — You can have a Pod called "database" in the "production" namespace and another Pod called "database" in the "staging" namespace. They do not conflict.

### Default Namespaces

Kubernetes creates several namespaces automatically. Let us see them:

```bash
kubectl get namespaces
```

```
NAME              STATUS   AGE
default           Active   5m
kube-node-lease   Active   5m
kube-public       Active   5m
kube-system       Active   5m
```

| Namespace | Purpose |
|-----------|---------|
| **default** | Where your resources go if you do not specify a namespace. This is your "home folder." |
| **kube-system** | Where Kubernetes' own components run (DNS, proxy, dashboard). Do not put your stuff here. |
| **kube-public** | Readable by everyone. Rarely used directly. |
| **kube-node-lease** | Used internally for node heartbeats. You can ignore this. |

### Seeing What Runs in kube-system

Curious what Kubernetes is running behind the scenes? Let us look:

```bash
kubectl get pods -n kube-system
```

```
NAME                               READY   STATUS    RESTARTS   AGE
coredns-5dd5756b68-abcde           1/1     Running   0          5m
etcd-minikube                      1/1     Running   0          5m
kube-apiserver-minikube            1/1     Running   0          5m
kube-controller-manager-minikube   1/1     Running   0          5m
kube-proxy-xyz12                   1/1     Running   0          5m
kube-scheduler-minikube            1/1     Running   0          5m
storage-provisioner                1/1     Running   0          5m
```

Look at that! Those are all the components from Chapter 26 running as Pods: the API Server, Controller Manager, Scheduler, etcd, kube-proxy, and CoreDNS.

The `-n kube-system` flag tells kubectl to look in the `kube-system` namespace instead of the `default` namespace.

### Creating Your Own Namespace

```bash
kubectl create namespace my-project
```

```
namespace/my-project created
```

Let us verify it:

```bash
kubectl get namespaces
```

```
NAME              STATUS   AGE
default           Active   10m
kube-node-lease   Active   10m
kube-public       Active   10m
kube-system       Active   10m
my-project        Active   5s
```

Your new namespace "my-project" is now ready to use.

### Creating a Namespace with YAML

You can also define a namespace in a YAML file. This is the **declarative** approach we discussed in Chapter 26:

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-project
```

Let us break down each line:

| Line | Meaning |
|------|---------|
| `apiVersion: v1` | Which version of the Kubernetes API to use. `v1` is the stable, core API. |
| `kind: Namespace` | What type of resource you are creating. In this case, a Namespace. |
| `metadata:` | Information about the resource. |
| `name: my-project` | The name you want to give this namespace. |

Apply it with:

```bash
kubectl apply -f namespace.yaml
```

```
namespace/my-project created
```

### Deleting a Namespace

```bash
kubectl delete namespace my-project
```

```
namespace "my-project" deleted
```

**Warning:** Deleting a namespace deletes **everything inside it** — all Pods, Services, ConfigMaps, and other resources. This is like deleting a folder on your computer. Everything inside is gone. Be careful with this command.

---

## kubectl Context: Talking to the Right Cluster

### What Is a Context?

A **context** tells kubectl which cluster to talk to and which namespace to use by default. Think of it as a **phone contact** — it stores the number (cluster address), the name (cluster name), and some preferences (default namespace).

If you only have one cluster (Minikube), you only have one context. But in the real world, developers often have access to multiple clusters — a development cluster, a staging cluster, and a production cluster. Contexts let you switch between them.

### Viewing Your Current Context

```bash
kubectl config current-context
```

```
minikube
```

This tells you that kubectl is currently talking to the "minikube" cluster.

### Viewing All Contexts

```bash
kubectl config get-contexts
```

```
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         minikube   minikube   minikube   default
```

| Column | Meaning |
|--------|---------|
| **CURRENT** | The asterisk (*) marks the active context. |
| **NAME** | The name of the context. |
| **CLUSTER** | Which cluster this context points to. |
| **AUTHINFO** | The credentials used to authenticate. |
| **NAMESPACE** | The default namespace for this context. |

### Switching Contexts

If you had multiple clusters, you would switch between them like this:

```bash
# Switch to a different context
kubectl config use-context my-production-cluster
```

```
Switched to context "my-production-cluster".
```

### Setting a Default Namespace

Tired of typing `-n my-project` every time? Set a default namespace for your current context:

```bash
kubectl config set-context --current --namespace=my-project
```

```
Context "minikube" modified.
```

Now every kubectl command will use the `my-project` namespace by default, so you do not need to add `-n my-project` to every command.

To switch back to the default namespace:

```bash
kubectl config set-context --current --namespace=default
```

```
Context "minikube" modified.
```

```
Context Switching:

  You (kubectl)
      │
      │  current-context = "minikube"
      │
      ├──► minikube cluster  (development)
      │
      ├──► staging cluster   (testing)
      │
      └──► production cluster (live users)

  Only ONE context is active at a time.
  kubectl sends commands to the active context.
```

---

## The Kubernetes Dashboard

The Kubernetes Dashboard is a web-based user interface that lets you see your cluster visually. It is like switching from a command-line file manager to a graphical file manager — same information, easier to browse.

### Opening the Dashboard with Minikube

```bash
minikube dashboard
```

```
🔌  Enabling dashboard ...
    ▪ Using image docker.io/kubernetesui/dashboard:v2.7.0
    ▪ Using image docker.io/kubernetesui/metrics-scraper:v1.0.8
💡  Some dashboard features require the metrics-server addon.
    To enable all features please run:

    minikube addons enable metrics-server

🤔  Verifying dashboard health ...
🚀  Launching proxy ...
🤔  Verifying proxy health ...
🎉  Opening http://127.0.0.1:54321/api/v1/namespaces/kubernetes-dashboard/...
    in your default browser...
```

Your web browser will open automatically and show the Kubernetes Dashboard:

```
Kubernetes Dashboard:

  ┌──────────────────────────────────────────────────┐
  │  ☸ Kubernetes Dashboard                           │
  ├──────────┬───────────────────────────────────────┤
  │          │                                        │
  │ Cluster  │   Namespace: default                   │
  │  Nodes   │                                        │
  │          │   Workloads                             │
  │ Workloads│   ┌──────────┬────────┬────────────┐   │
  │  Pods    │   │ Resource │ Status │ Count      │   │
  │  Deploy  │   ├──────────┼────────┼────────────┤   │
  │  Replica │   │ Pods     │ 0/0   │ All good   │   │
  │  Sets    │   │ Deploys  │ 0/0   │ All good   │   │
  │          │   │ Services │ 1     │ kubernetes │   │
  │ Services │   └──────────┴────────┴────────────┘   │
  │          │                                        │
  │ Config   │                                        │
  │  ConfigMaps                                       │
  │  Secrets │                                        │
  │          │                                        │
  │ Storage  │                                        │
  │  PVCs    │                                        │
  └──────────┴───────────────────────────────────────┘
```

The Dashboard lets you:

- View all resources (Pods, Deployments, Services) in your cluster
- See resource status and health
- View container logs
- Execute commands inside containers
- Create resources from the UI (though we recommend using YAML files instead)

Press `Ctrl+C` in the terminal to stop the Dashboard proxy when you are done.

### Docker Desktop Dashboard

If you are using Docker Desktop's Kubernetes, you do not get the Minikube Dashboard command. You can install the Dashboard manually or use Docker Desktop's own interface, which shows basic Kubernetes information.

---

## Stopping and Starting Minikube

### Stopping the Cluster

When you are done working, stop Minikube to free up your computer's resources:

```bash
minikube stop
```

```
✋  Stopping node "minikube"  ...
🛑  Powering off "minikube" via SSH ...
🛑  1 node stopped.
```

This does not delete anything. Your cluster, its configuration, and any resources you created are all saved. Think of it as putting your cluster to sleep.

### Starting Again

```bash
minikube start
```

```
😄  minikube v1.32.0 on Darwin 14.0 (arm64)
✨  Using the docker driver based on existing profile
👍  Starting control plane node minikube in cluster minikube
🏄  Done! kubectl is now configured to use "minikube" cluster
```

Notice it says "based on existing profile" — Minikube remembered your configuration and started the same cluster.

### Checking Minikube Status

```bash
minikube status
```

```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

All components are running. If any line says "Stopped," your cluster is not fully running.

### Deleting the Cluster

If you want to completely remove the cluster and start fresh:

```bash
minikube delete
```

```
🔥  Deleting "minikube" in docker ...
🔥  Deleting container "minikube" ...
🔥  Removing /Users/yourname/.minikube/machines/minikube ...
💀  Removed all traces of the "minikube" cluster.
```

This removes everything — the virtual machine, all resources, and all data. Use this only if you want a completely fresh start.

---

## Common Mistakes

1. **Forgetting to start the cluster.** If you see "The connection to the server was refused," your cluster is not running. Run `minikube start` first.

2. **Not enough resources.** Minikube needs at least 2 CPUs and 2 GB of memory. If your computer is low on resources, Minikube will fail to start or run slowly. Close other applications to free up memory.

3. **Wrong context.** If you have multiple clusters, kubectl might be pointing to the wrong one. Always check with `kubectl config current-context` before running commands.

4. **Docker not running.** Minikube with the Docker driver needs Docker to be running. If you see "docker is not running," start Docker Desktop first.

5. **Using kube-system namespace for your apps.** The `kube-system` namespace is for Kubernetes' own components. Create your own namespaces for your applications. Putting your Pods in `kube-system` can cause confusion and potential conflicts.

6. **Forgetting the namespace flag.** If you created resources in a specific namespace but cannot find them, you are probably looking in the wrong namespace. Use `kubectl get pods -n your-namespace` or `kubectl get pods --all-namespaces` to search everywhere.

7. **Not closing the Dashboard properly.** The `minikube dashboard` command runs in the foreground. Use `Ctrl+C` to stop it. Do not just close the terminal window, or the proxy process may keep running.

---

## Best Practices

1. **Stop Minikube when not in use.** Kubernetes consumes CPU and memory even when idle. Run `minikube stop` when you are done to free up resources.

2. **Use namespaces from the start.** Even in local development, get into the habit of creating namespaces for your projects. It will make transitioning to production easier.

3. **Set a default namespace.** Use `kubectl config set-context --current --namespace=my-project` to avoid typing `-n my-project` repeatedly.

4. **Use YAML files for everything.** Even for namespaces, use YAML files and `kubectl apply`. This creates a record of what you did and makes it reproducible.

5. **Bookmark useful kubectl commands.** You will use `kubectl get`, `kubectl describe`, and `kubectl logs` constantly. Practice them until they become muscle memory.

---

## Quick Summary

To run Kubernetes locally, install Minikube and kubectl. Start a cluster with `minikube start`, which creates a single-node Kubernetes cluster inside a Docker container on your machine. Use kubectl to interact with the cluster: `kubectl get nodes` shows your nodes, `kubectl get namespaces` shows your namespaces, and `kubectl config current-context` shows which cluster you are connected to. Namespaces organize resources like folders organize files. The Kubernetes Dashboard provides a visual interface for browsing your cluster.

---

## Key Points

- **Minikube** creates a single-node Kubernetes cluster on your laptop for learning and development
- **kubectl** is the command-line tool for communicating with any Kubernetes cluster
- `minikube start` starts the cluster; `minikube stop` pauses it; `minikube delete` removes it
- `kubectl get nodes` shows the machines in your cluster
- `kubectl cluster-info` shows where the control plane is running
- **Namespaces** divide your cluster into separate sections, like folders on a computer
- Every cluster has a `default` namespace and a `kube-system` namespace (for Kubernetes internals)
- **Contexts** tell kubectl which cluster and namespace to use
- `kubectl config current-context` shows which cluster you are connected to
- The **Dashboard** provides a web-based visual interface for your cluster

---

## Practice Questions

1. What is the difference between `minikube stop` and `minikube delete`? When would you use each one?

2. You run `kubectl get pods` and see no results, but you know you created Pods earlier. What might be wrong? How would you investigate?

3. Explain what a Kubernetes namespace is using a real-life analogy. Why would you use multiple namespaces instead of putting everything in the default namespace?

4. You have three clusters: development, staging, and production. How do you switch kubectl between them? How do you verify which cluster you are currently connected to?

5. A teammate says "I ran `kubectl get pods` and I see all the Kubernetes system Pods mixed with my application Pods." What advice would you give them?

---

## Exercises

### Exercise 1: Cluster Setup and Exploration

1. Install Minikube (or enable Kubernetes in Docker Desktop)
2. Start a cluster with `minikube start`
3. Run `kubectl cluster-info` and note the control plane URL
4. Run `kubectl get nodes` and note the node name, status, and Kubernetes version
5. Run `kubectl get pods -n kube-system` and identify which Pod corresponds to which component from Chapter 26

### Exercise 2: Namespace Management

1. Create three namespaces: `development`, `staging`, and `production`
2. Verify all three exist with `kubectl get namespaces`
3. Set your default namespace to `development` using `kubectl config set-context`
4. Verify the change with `kubectl config get-contexts`
5. Delete the `staging` namespace
6. Reset your default namespace back to `default`

### Exercise 3: Context Practice

1. Run `kubectl config get-contexts` and note all the columns
2. Run `kubectl config view` and examine the output — try to identify the cluster server address, the user credentials, and the context definition
3. Create a YAML file for a namespace called "practice" and apply it with `kubectl apply -f`
4. Delete it with `kubectl delete -f` using the same YAML file

---

## What Is Next?

You now have a working Kubernetes cluster on your machine and you know how to interact with it using kubectl. But the cluster is empty — there are no applications running in it yet.

In the next chapter, you will deploy your first application to Kubernetes. You will learn about Pods (the smallest unit in Kubernetes), Deployments (which manage groups of Pods), and Services (which let you access your Pods over the network). You will write YAML manifests and watch Kubernetes bring your application to life.
