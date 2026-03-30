# Chapter 26: What Is Kubernetes?

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Explain why managing many containers by hand becomes impossible at scale
- Describe what container orchestration means and why it exists
- Understand the Kubernetes architecture: control plane and worker nodes
- Name and explain every major Kubernetes component
- Compare Kubernetes with Docker Swarm
- Decide when Kubernetes is the right tool for your project

---

## Why This Chapter Matters

In the previous chapters, you learned how to build Docker images, run containers, and use Docker Compose to manage multi-container applications on a single machine. That works great for development and small projects.

But what happens when your application grows? What happens when you need to run 50, 100, or 1,000 containers across multiple servers? What happens when a server crashes at 3 AM and your containers go down with it?

You need a system that manages containers for you automatically. That system is called a **container orchestrator**, and the most popular one is **Kubernetes**. This chapter introduces you to Kubernetes and explains why it has become the industry standard for running containers in production.

---

## The Problem: Managing Containers at Scale

### A Small Application

Imagine you have a simple web application:

- 1 web server container
- 1 database container
- 1 cache container

You can manage this with Docker Compose on a single machine. You run `docker compose up`, and everything works. Life is good.

### A Growing Application

Now imagine your application becomes popular. You need:

- 20 web server containers (to handle more traffic)
- 3 database containers (primary plus replicas for reliability)
- 5 cache containers (to speed up responses)
- 10 background worker containers (to process jobs)
- 3 message queue containers (to coordinate workers)

That is 41 containers. Can you manage them with Docker Compose on a single machine? Maybe, but that single machine is now a **single point of failure**. If it crashes, your entire application goes down.

### A Production Application

Now imagine a real production setup:

- 200+ containers running across 30 servers
- Containers need to be restarted automatically when they crash
- New versions need to be deployed without downtime
- Traffic needs to be distributed evenly across containers
- Some containers need more CPU, others need more memory
- You need to scale up during peak hours and scale down at night

Managing this by hand is impossible. You would need a team of people watching dashboards 24 hours a day, restarting crashed containers, moving workloads between servers, and updating configurations. One mistake could take down your entire application.

This is the problem that **container orchestration** solves.

---

## What Is Container Orchestration?

**Container orchestration** is the automatic management of containerized applications across multiple servers. An orchestrator handles:

| Task | What It Means |
|------|--------------|
| **Scheduling** | Deciding which server should run each container |
| **Scaling** | Adding or removing container copies based on demand |
| **Self-healing** | Restarting crashed containers automatically |
| **Load balancing** | Distributing traffic evenly across containers |
| **Rolling updates** | Deploying new versions without downtime |
| **Service discovery** | Letting containers find and talk to each other |
| **Storage management** | Attaching persistent storage to containers |
| **Configuration** | Managing secrets and settings across containers |

### The Orchestra Analogy

Think of a symphony orchestra:

- The **musicians** are your containers. Each one plays a specific part (web server, database, cache).
- The **instruments** are the servers. Multiple musicians can share an instrument section.
- The **conductor** is the orchestrator. The conductor does not play any instrument. Instead, the conductor:
  - Tells each musician when to start and stop
  - Makes sure all musicians play in harmony
  - Brings in more musicians when the music needs to be louder
  - Replaces a musician who gets sick (without stopping the performance)
  - Coordinates tempo changes (rolling updates) smoothly

**Kubernetes is the conductor of your container orchestra.**

---

## What Is Kubernetes?

**Kubernetes** (often written as **K8s** — the "8" stands for the eight letters between "K" and "s") is an open-source container orchestration platform. It was originally designed by Google, based on over 15 years of experience running containers in production. Google donated it to the **Cloud Native Computing Foundation (CNCF)** in 2014, and it has since become the industry standard.

### What Kubernetes Does

You tell Kubernetes: "I want 5 copies of my web server running at all times."

Kubernetes then:

1. Finds servers with enough resources to run those 5 copies
2. Starts the containers on those servers
3. Monitors them continuously
4. If one container crashes, starts a replacement automatically
5. If a server goes down, moves the containers to healthy servers
6. If you change the number to 10, starts 5 more containers
7. If you deploy a new version, replaces old containers one at a time

You describe the **desired state** (what you want), and Kubernetes makes it happen and keeps it that way. This is called **declarative configuration**.

### Declarative vs. Imperative

This distinction is important:

```
Imperative (telling Kubernetes what to do step by step):
  "Start a container. Now start another one. Now stop the first one."

Declarative (telling Kubernetes what you want):
  "I want 3 containers running version 2.0 of my app."
```

With the declarative approach, Kubernetes figures out the steps to get from the current state to your desired state. If you currently have 2 containers running version 1.0, Kubernetes will:

1. Start 1 new container (to reach 3 total)
2. Replace each version 1.0 container with a version 2.0 container
3. Ensure 3 healthy version 2.0 containers are running

You do not need to write the steps. You just describe the end result.

---

## Kubernetes Architecture

Kubernetes runs as a **cluster** — a group of machines working together. Every Kubernetes cluster has two types of machines:

1. **Control plane nodes** (the brain) — they make decisions about the cluster
2. **Worker nodes** (the muscle) — they run your actual containers

Here is how they fit together:

```
┌─────────────────────────────────────────────────────────────────┐
│                      KUBERNETES CLUSTER                         │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    CONTROL PLANE                          │  │
│  │                   (The Brain)                             │  │
│  │                                                           │  │
│  │  ┌─────────────┐  ┌───────────┐  ┌──────────────────┐   │  │
│  │  │ API Server  │  │ Scheduler │  │ Controller       │   │  │
│  │  │             │  │           │  │ Manager          │   │  │
│  │  │ Front door  │  │ Decides   │  │ Keeps desired    │   │  │
│  │  │ for all     │  │ where to  │  │ state matching   │   │  │
│  │  │ requests    │  │ run pods  │  │ actual state     │   │  │
│  │  └─────────────┘  └───────────┘  └──────────────────┘   │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │                      etcd                           │ │  │
│  │  │         Cluster database (stores all state)         │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                    kubectl commands                               │
│                    travel through                                 │
│                    the API Server                                 │
│                              │                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │   WORKER NODE 1  │  │   WORKER NODE 2  │  │ WORKER NODE 3│   │
│  │   (The Muscle)   │  │   (The Muscle)   │  │ (The Muscle) │   │
│  │                  │  │                  │  │              │   │
│  │ ┌──────────────┐│  │ ┌──────────────┐│  │ ┌──────────┐ │   │
│  │ │   kubelet    ││  │ │   kubelet    ││  │ │  kubelet │ │   │
│  │ │ (node agent) ││  │ │ (node agent) ││  │ │(node agt)│ │   │
│  │ └──────────────┘│  │ └──────────────┘│  │ └──────────┘ │   │
│  │ ┌──────────────┐│  │ ┌──────────────┐│  │ ┌──────────┐ │   │
│  │ │  kube-proxy  ││  │ │  kube-proxy  ││  │ │kube-proxy│ │   │
│  │ │ (networking) ││  │ │ (networking) ││  │ │(network) │ │   │
│  │ └──────────────┘│  │ └──────────────┘│  │ └──────────┘ │   │
│  │ ┌──────────────┐│  │ ┌──────────────┐│  │ ┌──────────┐ │   │
│  │ │  Container   ││  │ │  Container   ││  │ │Container │ │   │
│  │ │  Runtime     ││  │ │  Runtime     ││  │ │ Runtime  │ │   │
│  │ │  (containerd)││  │ │  (containerd)││  │ │(cntrd)   │ │   │
│  │ └──────────────┘│  │ └──────────────┘│  │ └──────────┘ │   │
│  │                  │  │                  │  │              │   │
│  │  ┌────┐ ┌────┐  │  │  ┌────┐ ┌────┐  │  │  ┌────┐     │   │
│  │  │Pod │ │Pod │  │  │  │Pod │ │Pod │  │  │  │Pod │     │   │
│  │  │ A  │ │ B  │  │  │  │ C  │ │ D  │  │  │  │ E  │     │   │
│  │  └────┘ └────┘  │  │  └────┘ └────┘  │  │  └────┘     │   │
│  └──────────────────┘  └──────────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

Let us examine each component.

---

## Control Plane Components

The control plane is the brain of the cluster. It makes all the decisions but does not run your application containers. In production, the control plane usually runs on dedicated servers (often 3 or 5 for high availability).

### API Server (kube-apiserver)

The **API Server** is the front door to the Kubernetes cluster. Every command, every request, every piece of communication goes through the API Server.

Think of it as the **receptionist at a large company**. Whether you are a visitor (a developer running kubectl), an employee (a component inside the cluster), or a delivery person (an external system), you go through the receptionist first. The receptionist validates your identity, checks if you are allowed in, and directs you to the right place.

**What it does:**

- Receives all requests (from kubectl, from other components, from external tools)
- Validates requests (checks if the YAML is correct, if you have permission)
- Stores the validated data in etcd
- Notifies other components about changes

```bash
# When you run this command:
kubectl get pods

# Here is what happens:
# 1. kubectl sends an HTTPS request to the API Server
# 2. The API Server checks your credentials
# 3. The API Server reads the pod data from etcd
# 4. The API Server sends the data back to kubectl
# 5. kubectl displays it in your terminal
```

### Scheduler (kube-scheduler)

The **Scheduler** decides which worker node should run each new container (technically, each new Pod — we will explain Pods in Chapter 28).

Think of it as a **hotel front desk clerk** assigning rooms to guests. When a new guest arrives, the clerk checks:

- Which rooms are available?
- Does the guest need a room with a king bed (specific CPU/memory requirements)?
- Does the guest want a room on a high floor (specific node preferences)?
- Which floor has the fewest guests right now (load balancing)?

**What it does:**

- Watches for new Pods that have no assigned node
- Evaluates which nodes have enough resources (CPU, memory, disk)
- Considers constraints (some Pods must run on specific nodes)
- Assigns the Pod to the best available node

```
Scheduler Decision Process:

  New Pod needs:          Node A          Node B          Node C
  2 CPU, 4GB RAM         8 CPU free      1 CPU free      4 CPU free
                         16GB free       2GB free        8GB free

  Can it fit?            YES             NO              YES
  Current load:          3 pods          7 pods          2 pods

  Decision: ──────────────────────────────────────► Node C
  (fits and has the lightest load)
```

### etcd

**etcd** (pronounced "et-see-dee") is a distributed key-value database that stores all cluster data. It is the **single source of truth** for the entire cluster.

Think of it as the **filing cabinet** in that large company. Every employee record, every policy document, every piece of important information is stored there. If the filing cabinet is destroyed, the company loses everything.

**What it stores:**

- What nodes exist in the cluster
- What Pods are running and where
- What configurations and secrets exist
- The desired state of every resource
- The current state of every resource

**Why it matters:**

- If etcd loses data, the entire cluster loses its memory
- In production, etcd is always backed up and replicated across multiple machines
- etcd uses the Raft consensus protocol to ensure all copies agree on the data

### Controller Manager (kube-controller-manager)

The **Controller Manager** runs a collection of controllers — background loops that continuously compare the desired state with the actual state and take action to fix any differences.

Think of it as a **thermostat**. You set the thermostat to 72 degrees Fahrenheit (the desired state). The thermostat continuously checks the actual temperature. If it is too cold, it turns on the heater. If it is too hot, it turns on the air conditioning. It never stops checking.

**Some controllers inside the Controller Manager:**

| Controller | What It Does |
|-----------|-------------|
| **Replication Controller** | Ensures the correct number of Pod copies are running |
| **Node Controller** | Detects when a node goes down and responds |
| **Job Controller** | Manages one-time tasks that run to completion |
| **Endpoint Controller** | Connects Services to Pods |

**Example of the control loop:**

```
Desired State: 3 replicas of web-server

Control Loop:
  1. Check: How many web-server pods are running?  → 3
     Action: Nothing. Everything is fine.

  2. Check: How many web-server pods are running?  → 2 (one crashed)
     Action: Start 1 new web-server pod.

  3. Check: How many web-server pods are running?  → 3
     Action: Nothing. Back to normal.

  (This loop runs continuously, every few seconds)
```

---

## Worker Node Components

Worker nodes are the machines that actually run your application containers. A cluster can have 1 worker node or 1,000 — you add more as your application grows.

### kubelet

The **kubelet** is an agent that runs on every worker node. It is the **node's representative** in the cluster.

Think of it as a **site manager on a construction site**. The headquarters (control plane) sends blueprints (Pod specifications). The site manager makes sure the buildings (containers) are built according to the blueprints and reports back on progress.

**What it does:**

- Receives Pod specifications from the API Server
- Tells the container runtime to start or stop containers
- Monitors containers and reports their health back to the control plane
- Mounts volumes and manages storage for Pods

### kube-proxy

**kube-proxy** runs on every worker node and manages network rules. It makes sure that network traffic reaches the right containers.

Think of it as a **mail room clerk**. When mail (network traffic) arrives at the building (node), the mail room clerk knows which office (container) it should go to. If a container moves to a different node, kube-proxy updates its routing rules so traffic follows the container to its new location.

**What it does:**

- Maintains network rules on each node
- Forwards traffic to the correct Pods
- Enables communication between Pods across different nodes
- Implements load balancing for Services

### Container Runtime

The **container runtime** is the software that actually runs containers. Kubernetes does not run containers directly — it tells the container runtime to do it.

Think of it as the **engine in a car**. Kubernetes is the driver who decides where to go and when. The container runtime is the engine that actually makes the car move.

**Common container runtimes:**

- **containerd** — the most common runtime (Docker uses this under the hood)
- **CRI-O** — a lightweight runtime built specifically for Kubernetes

```
How a container starts:

  API Server                kubelet              containerd         Container
      │                        │                     │                  │
      │  "Run this Pod"        │                     │                  │
      │───────────────────────►│                     │                  │
      │                        │  "Start container"  │                  │
      │                        │────────────────────►│                  │
      │                        │                     │  Pull image      │
      │                        │                     │  Create container│
      │                        │                     │─────────────────►│
      │                        │                     │                  │ Running
      │                        │  "Container ready"  │                  │
      │                        │◄────────────────────│                  │
      │  "Pod is running"      │                     │                  │
      │◄───────────────────────│                     │                  │
```

---

## How Everything Works Together

Let us walk through what happens when you deploy an application to Kubernetes:

**Step 1: You submit a request**

```bash
kubectl apply -f my-app.yaml
```

This sends your YAML file to the API Server.

**Step 2: API Server validates and stores**

The API Server checks the YAML for errors, verifies you have permission, and stores the desired state in etcd.

**Step 3: Controller Manager detects work to do**

The Controller Manager notices: "The user wants 3 replicas of my-app, but 0 exist. I need to create 3 Pods."

**Step 4: Scheduler assigns nodes**

For each new Pod, the Scheduler finds the best worker node based on available resources.

**Step 5: kubelet starts containers**

The kubelet on each assigned node receives the Pod specification and tells the container runtime to pull the image and start the container.

**Step 6: Continuous monitoring**

The kubelet reports container health to the API Server. The Controller Manager continuously checks that the desired state matches the actual state. If a container crashes, the cycle repeats from Step 3.

```
The Full Flow:

  You (kubectl)
      │
      ▼
  ┌──────────┐     ┌─────────────────┐     ┌───────────┐
  │API Server │────►│ Controller Mgr  │────►│ Scheduler │
  └──────────┘     └─────────────────┘     └───────────┘
      │                                         │
      │              ┌──────┐                   │
      └─────────────►│ etcd │◄──────────────────┘
                     └──────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
     ┌─────────┐  ┌─────────┐  ┌─────────┐
     │ kubelet │  │ kubelet │  │ kubelet │
     │ Node 1  │  │ Node 2  │  │ Node 3  │
     └─────────┘  └─────────┘  └─────────┘
          │             │             │
     ┌────┴────┐  ┌────┴────┐  ┌────┴────┐
     │Container│  │Container│  │Container│
     │ Runtime │  │ Runtime │  │ Runtime │
     └─────────┘  └─────────┘  └─────────┘
```

---

## kubectl: Your Way to Talk to Kubernetes

**kubectl** (pronounced "kube-control" or "kube-C-T-L") is the command-line tool you use to communicate with a Kubernetes cluster. Every command you type in kubectl is sent to the API Server.

Think of kubectl as **your remote control** for the Kubernetes cluster. You do not log into the cluster machines directly. Instead, you use kubectl from your own computer to send commands.

```bash
# Some basic kubectl commands (we will use these in later chapters):

kubectl get pods           # List all running Pods
kubectl get nodes          # List all nodes in the cluster
kubectl get services       # List all Services
kubectl describe pod my-pod  # Show detailed info about a Pod
kubectl logs my-pod        # View container logs
kubectl apply -f file.yaml # Apply a configuration file
kubectl delete pod my-pod  # Delete a Pod
```

---

## Kubernetes vs. Docker Swarm

In Chapter 24, you learned about Docker Swarm. Both Swarm and Kubernetes are container orchestrators, but they differ significantly:

| Feature | Docker Swarm | Kubernetes |
|---------|-------------|------------|
| **Setup complexity** | Very easy (built into Docker) | More complex (separate installation) |
| **Learning curve** | Gentle | Steep |
| **Scaling** | Good for small to medium | Excellent for any size |
| **Auto-scaling** | Manual scaling only | Supports automatic scaling |
| **Self-healing** | Basic (restarts containers) | Advanced (restarts, reschedules, replaces) |
| **Rolling updates** | Supported | Advanced (canary, blue-green, rollback) |
| **Networking** | Simple overlay networks | Advanced (network policies, ingress) |
| **Storage** | Basic volume support | Advanced (PV, PVC, storage classes) |
| **Community** | Smaller | Massive (largest open-source community) |
| **Cloud support** | Limited | All major clouds (AWS EKS, Google GKE, Azure AKS) |
| **Ecosystem** | Few add-ons | Thousands of tools and extensions |
| **Production use** | Small to medium deployments | Small to massive deployments |

### When to Use Docker Swarm

- You have a small team and a simple application
- You want to get up and running quickly
- You do not need advanced features like auto-scaling
- You are already comfortable with Docker Compose
- Your application runs on fewer than 10-20 nodes

### When to Use Kubernetes

- You need to run containers at large scale (dozens to thousands of nodes)
- You need automatic scaling based on traffic
- You need advanced deployment strategies (canary releases, blue-green deployments)
- You want a rich ecosystem of tools and integrations
- Your cloud provider offers managed Kubernetes (EKS, GKE, AKS)
- Your team is willing to invest time in learning

### The Industry Trend

Kubernetes has become the dominant container orchestrator. Most companies that run containers in production use Kubernetes. Major cloud providers offer **managed Kubernetes services** that handle the complex setup for you:

- **Amazon EKS** (Elastic Kubernetes Service)
- **Google GKE** (Google Kubernetes Engine)
- **Azure AKS** (Azure Kubernetes Service)
- **DigitalOcean Kubernetes**

These managed services let you focus on deploying your applications while the cloud provider manages the control plane.

```
Managed Kubernetes:

  ┌─────────────────────────────────────────┐
  │         Cloud Provider Manages          │
  │  ┌───────────────────────────────────┐  │
  │  │         Control Plane             │  │
  │  │  API Server, Scheduler, etcd,     │  │
  │  │  Controller Manager               │  │
  │  └───────────────────────────────────┘  │
  └─────────────────────────────────────────┘

  ┌─────────────────────────────────────────┐
  │           You Manage                    │
  │  ┌──────────┐ ┌──────────┐ ┌────────┐  │
  │  │ Worker   │ │ Worker   │ │ Worker │  │
  │  │ Node 1   │ │ Node 2   │ │ Node 3 │  │
  │  │ (Your    │ │ (Your    │ │ (Your  │  │
  │  │  apps)   │ │  apps)   │ │  apps) │  │
  │  └──────────┘ └──────────┘ └────────┘  │
  └─────────────────────────────────────────┘
```

---

## Key Kubernetes Terminology

Here is a quick reference of terms you will encounter throughout the Kubernetes chapters:

| Term | Meaning |
|------|---------|
| **Cluster** | A group of machines running Kubernetes |
| **Node** | A single machine in the cluster (physical or virtual) |
| **Control Plane** | The set of components that manage the cluster |
| **Worker Node** | A machine that runs your application containers |
| **Pod** | The smallest deployable unit (one or more containers) |
| **Deployment** | Manages multiple copies of a Pod |
| **Service** | A stable network endpoint to access Pods |
| **Namespace** | A way to divide cluster resources between projects |
| **kubectl** | The command-line tool for interacting with Kubernetes |
| **YAML manifest** | A file describing the desired state of a resource |
| **Desired state** | What you want the cluster to look like |
| **Actual state** | What the cluster currently looks like |

---

## Common Mistakes

1. **Thinking Kubernetes replaces Docker.** Kubernetes does not replace Docker. Kubernetes uses a container runtime (like containerd) to run containers. Docker builds the images; Kubernetes orchestrates the containers made from those images. They work together.

2. **Using Kubernetes for everything.** Not every application needs Kubernetes. If you have a simple application running on one server, Docker Compose is simpler and faster. Kubernetes adds complexity. Use it when you actually need its features.

3. **Ignoring the learning curve.** Kubernetes has many concepts and components. Do not try to learn everything at once. Start with the basics (Pods, Deployments, Services) and gradually add more knowledge.

4. **Confusing control plane and worker nodes.** The control plane makes decisions. Worker nodes run your containers. In development (Minikube), both run on the same machine. In production, they are separate machines.

5. **Thinking you need to manage your own cluster.** Most companies use managed Kubernetes services (EKS, GKE, AKS). These handle the control plane for you. Unless you have specific reasons, use a managed service.

---

## Best Practices

1. **Start with managed Kubernetes.** Unless you are learning Kubernetes administration specifically, use a managed service. It saves enormous amounts of time and effort.

2. **Learn the fundamentals first.** Master Pods, Deployments, and Services before moving to advanced topics like custom resources, operators, or service meshes.

3. **Use declarative configuration.** Always use YAML files with `kubectl apply` rather than imperative commands like `kubectl run`. YAML files can be version-controlled and reviewed.

4. **Version-control your YAML files.** Store all your Kubernetes manifests in Git. This gives you a history of changes and the ability to roll back.

5. **Use namespaces to organize.** Separate different environments (dev, staging, production) and different teams using namespaces.

---

## Quick Summary

Kubernetes is a container orchestration platform that automates the deployment, scaling, and management of containerized applications across clusters of machines. It has a control plane (API Server, Scheduler, Controller Manager, etcd) that makes decisions and worker nodes (kubelet, kube-proxy, container runtime) that run containers. You interact with Kubernetes using kubectl, and you describe your desired state in YAML files. Kubernetes continuously works to make the actual state match your desired state.

---

## Key Points

- Container orchestration automates the management of containers across multiple servers
- Kubernetes uses a **declarative model**: you describe what you want, and it makes it happen
- The **control plane** (API Server, Scheduler, Controller Manager, etcd) is the brain of the cluster
- **Worker nodes** (kubelet, kube-proxy, container runtime) run your application containers
- **kubectl** is the command-line tool for communicating with the cluster
- Kubernetes is more powerful but more complex than Docker Swarm
- Most companies use **managed Kubernetes services** from cloud providers
- Kubernetes does not replace Docker — they complement each other

---

## Practice Questions

1. You have a web application with 3 containers running via Docker Compose. A colleague suggests migrating to Kubernetes. What questions would you ask before deciding?

2. Explain the role of the Scheduler. What information does it use to decide where to place a Pod?

3. What happens when a container crashes in Kubernetes? Walk through the sequence of events, naming each component involved.

4. A colleague says "We do not need Docker anymore because we have Kubernetes." Why is this statement incorrect?

5. What is the difference between the desired state and the actual state? Give an example of a situation where they might differ.

---

## Exercises

### Exercise 1: Architecture Diagram

Draw the Kubernetes architecture diagram from memory. Include:

- Control plane with all four components
- At least two worker nodes with all three components
- Arrows showing how kubectl communicates with the cluster

Check your diagram against the one in this chapter. Did you miss any components?

### Exercise 2: Component Matching

Match each scenario with the Kubernetes component responsible:

| Scenario | Component |
|----------|-----------|
| A new Pod needs to be placed on a node | ? |
| A Pod's container crashed and needs restarting | ? |
| A developer runs `kubectl get pods` | ? |
| Cluster state needs to be stored persistently | ? |
| Network traffic needs to reach the right Pod | ? |
| A container image needs to be pulled and started | ? |

### Exercise 3: Kubernetes vs. Swarm Decision

For each scenario, decide whether Docker Swarm or Kubernetes is the better choice. Explain your reasoning:

1. A startup with 2 developers running 5 containers on a single server
2. An e-commerce company expecting 10x traffic during holiday sales
3. A team that already uses Docker Compose and wants minimal changes

---

## What Is Next?

Now that you understand what Kubernetes is and how its components work together, you need a way to run it on your own machine. In the next chapter, you will install and set up a local Kubernetes environment using Minikube. You will run your first kubectl commands and see a real cluster in action.
