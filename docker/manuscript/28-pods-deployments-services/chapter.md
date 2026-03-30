# Chapter 28: Pods, Deployments, and Services

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Explain what a Pod is and why it is the smallest unit in Kubernetes
- Write a Pod YAML manifest from scratch
- Use kubectl to create, inspect, and troubleshoot Pods
- Explain why you rarely create Pods directly in production
- Understand what a Deployment is and how it manages Pods for you
- Scale Pods up and down using Deployments
- Perform rolling updates and rollbacks
- Explain what a Service is and why Pods need one
- Distinguish between ClusterIP, NodePort, and LoadBalancer services
- Deploy a complete application with replicas and a Service

---

## Why This Chapter Matters

In the previous chapter, you set up a local Kubernetes cluster. You ran kubectl commands and explored namespaces. But the cluster was empty — no applications were running.

This chapter changes that. Pods, Deployments, and Services are the three most fundamental building blocks of Kubernetes. Nearly everything you do with Kubernetes involves at least one of these three. If Kubernetes is a house, Pods are the bricks, Deployments are the construction crew, and Services are the doors.

You cannot use Kubernetes effectively without understanding these three concepts deeply. By the end of this chapter, you will have a real application running in your cluster and accessible from your browser.

---

## Pods: The Smallest Unit in Kubernetes

### What Is a Pod?

A **Pod** is the smallest thing you can deploy in Kubernetes. A Pod is a wrapper around one or more containers. In most cases, a Pod contains exactly one container.

Think of a Pod as a **lunch box**. The food inside is your container (your application). The lunch box provides a wrapper that gives the food:

- A place to exist (an IP address)
- Protection (isolation from other Pods)
- Shared resources (all containers in the same Pod share the same network and storage)

```
A Pod with one container (most common):

  ┌─────────────────────┐
  │  Pod                │
  │  ┌───────────────┐  │
  │  │  Container    │  │
  │  │  (your app)   │  │
  │  └───────────────┘  │
  │                     │
  │  IP: 10.244.0.5     │
  └─────────────────────┘

A Pod with multiple containers (advanced use case):

  ┌──────────────────────────────┐
  │  Pod                         │
  │  ┌────────────┐ ┌──────────┐│
  │  │  Container │ │ Container││
  │  │  (main app)│ │ (log     ││
  │  │            │ │  shipper)││
  │  └────────────┘ └──────────┘│
  │                              │
  │  IP: 10.244.0.6              │
  │  Shared network and storage  │
  └──────────────────────────────┘
```

### Why Not Just Use Containers?

You might wonder: "Why add a Pod wrapper around a container? Why not just run containers directly?"

The Pod exists because Kubernetes needs a higher-level concept that provides:

1. **A unique IP address.** Every Pod gets its own IP address. Containers inside the same Pod share this IP.
2. **Shared storage.** Containers in the same Pod can share files through volumes.
3. **Lifecycle management.** Kubernetes manages Pods, not individual containers. It starts them, monitors them, and restarts them as a unit.
4. **Co-location of tightly coupled containers.** Sometimes two containers need to work together closely (like a web app and a log collector). Putting them in the same Pod ensures they always run on the same node.

### Writing Your First Pod YAML

Kubernetes uses YAML files to describe what you want. These files are called **manifests**. Let us write a manifest for a simple Pod running an Nginx web server.

Create a file called `pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-first-pod
  labels:
    app: nginx
spec:
  containers:
    - name: nginx-container
      image: nginx:1.25
      ports:
        - containerPort: 80
```

Let us break this down line by line:

| Line | Meaning |
|------|---------|
| `apiVersion: v1` | Which version of the Kubernetes API to use. Pods are part of the core API, so this is `v1`. |
| `kind: Pod` | What type of resource you are creating. |
| `metadata:` | Information about this Pod. |
| `name: my-first-pod` | The name of the Pod. Must be unique within the namespace. |
| `labels:` | Key-value pairs attached to the Pod. Labels are like tags — they help you organize and select Pods. |
| `app: nginx` | A label that says this Pod belongs to the "nginx" app. |
| `spec:` | The specification — what the Pod should contain. |
| `containers:` | A list of containers to run inside this Pod. |
| `- name: nginx-container` | The name of this container. The dash (`-`) means this is an item in a list. |
| `image: nginx:1.25` | The Docker image to use. Kubernetes will pull this image (just like `docker pull`). |
| `ports:` | Which ports the container listens on. |
| `containerPort: 80` | This container listens on port 80 (the standard HTTP port). |

### The Structure of Every Kubernetes YAML

Almost every Kubernetes YAML file has the same four top-level sections:

```yaml
apiVersion:  # Which API version to use
kind:        # What type of resource (Pod, Deployment, Service, etc.)
metadata:    # Name, labels, annotations — info ABOUT the resource
spec:        # The actual specification — what the resource SHOULD be
```

```
Every Kubernetes YAML:

  ┌──────────────────────┐
  │  apiVersion: v1      │◄── Which API to talk to
  ├──────────────────────┤
  │  kind: Pod           │◄── What to create
  ├──────────────────────┤
  │  metadata:           │◄── Info about it (name, labels)
  │    name: my-pod      │
  │    labels:           │
  │      app: myapp      │
  ├──────────────────────┤
  │  spec:               │◄── What it should contain/do
  │    containers:       │
  │      - name: ...     │
  │        image: ...    │
  └──────────────────────┘
```

### Creating the Pod

Now let us create the Pod in your cluster:

```bash
kubectl apply -f pod.yaml
```

```
pod/my-first-pod created
```

**What just happened?**

1. kubectl read your YAML file.
2. It sent the file to the Kubernetes API Server.
3. The API Server validated the YAML (checked for errors).
4. The API Server stored the desired state in etcd.
5. The Scheduler found a node with enough resources and assigned the Pod to it.
6. The kubelet on that node pulled the `nginx:1.25` image and started the container.

### Inspecting Your Pod

**List all Pods:**

```bash
kubectl get pods
```

```
NAME           READY   STATUS    RESTARTS   AGE
my-first-pod   1/1     Running   0          30s
```

| Column | Meaning |
|--------|---------|
| **NAME** | The Pod name from your YAML. |
| **READY** | How many containers are ready out of total. `1/1` means 1 container running out of 1 total. |
| **STATUS** | The current state. `Running` means everything is fine. |
| **RESTARTS** | How many times containers have been restarted. `0` means no crashes. |
| **AGE** | How long the Pod has been running. |

**Get more details:**

```bash
kubectl get pods -o wide
```

```
NAME           READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE
my-first-pod   1/1     Running   0          1m    10.244.0.5   minikube   <none>
```

The `-o wide` flag shows extra columns, including the Pod's IP address and which node it is running on.

**Describe the Pod (full details):**

```bash
kubectl describe pod my-first-pod
```

```
Name:             my-first-pod
Namespace:        default
Priority:         0
Service Account:  default
Node:             minikube/192.168.49.2
Start Time:       Mon, 15 Jan 2024 10:45:00 -0500
Labels:           app=nginx
Status:           Running
IP:               10.244.0.5
Containers:
  nginx-container:
    Image:          nginx:1.25
    Port:           80/TCP
    State:          Running
      Started:      Mon, 15 Jan 2024 10:45:02 -0500
    Ready:          True
    Restart Count:  0
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  2m    default-scheduler  Successfully assigned default/my-first-pod to minikube
  Normal  Pulling    2m    kubelet            Pulling image "nginx:1.25"
  Normal  Pulled     1m    kubelet            Successfully pulled image "nginx:1.25"
  Normal  Created    1m    kubelet            Created container nginx-container
  Normal  Started    1m    kubelet            Started container nginx-container
```

The **Events** section at the bottom is extremely useful for troubleshooting. It shows you the step-by-step history of what happened to this Pod:

1. The Scheduler assigned it to the minikube node
2. The kubelet pulled the nginx image
3. The container was created
4. The container was started

**View container logs:**

```bash
kubectl logs my-first-pod
```

```
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt
to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
...
2024/01/15 15:45:02 [notice] 1#1: nginx/1.25.3
2024/01/15 15:45:02 [notice] 1#1: built by gcc 12.2.0
```

This is the same output you would see with `docker logs`. It shows what the Nginx container printed when it started.

**Run a command inside the Pod:**

```bash
kubectl exec -it my-first-pod -- /bin/bash
```

```
root@my-first-pod:/#
```

This is similar to `docker exec`. The `--` separates kubectl flags from the command to run. `-i` means interactive (keep stdin open), `-t` means allocate a terminal. Type `exit` to leave.

### Deleting a Pod

```bash
kubectl delete pod my-first-pod
```

```
pod "my-first-pod" deleted
```

Or delete using the YAML file:

```bash
kubectl delete -f pod.yaml
```

```
pod "my-first-pod" deleted
```

---

## Why You Rarely Create Pods Directly

Here is an important lesson: **in production, you almost never create Pods directly.**

Why? Because Pods are **mortal**. They do not self-heal.

If a Pod crashes, it is gone. Kubernetes does not automatically create a replacement when you create Pods directly. If the node where your Pod is running goes down, the Pod goes down with it.

```
Pod created directly:

  Pod crashes ──► Pod is gone ──► Nobody creates a new one
                                   You must do it manually!

Pod created by a Deployment:

  Pod crashes ──► Deployment notices ──► Deployment creates
                                           a new Pod automatically!
```

This is like the difference between hiring a single worker with no manager versus hiring through a staffing agency. If the single worker calls in sick, nobody shows up. If you hire through an agency (a Deployment), they send a replacement.

So what do you use instead of creating Pods directly? You use a **Deployment**.

---

## Deployments: Managing Pods at Scale

### What Is a Deployment?

A **Deployment** is a Kubernetes resource that manages Pods for you. Think of it as a **manager** who ensures a certain number of workers (Pods) are always on the job.

You tell the Deployment: "I want 3 copies of my web server running at all times."

The Deployment then:

1. Creates 3 Pods
2. Monitors them continuously
3. If one Pod crashes, creates a replacement
4. If a node goes down, reschedules the Pods to healthy nodes
5. Handles rolling updates when you deploy a new version
6. Supports rollback if the new version has problems

### How Deployments Work

A Deployment does not manage Pods directly. It creates an intermediate resource called a **ReplicaSet**, and the ReplicaSet manages the Pods.

```
Deployment ──creates──► ReplicaSet ──creates──► Pods

  ┌────────────┐     ┌─────────────┐     ┌───────┐
  │ Deployment │────►│ ReplicaSet  │────►│ Pod 1 │
  │            │     │             │     │ Pod 2 │
  │ replicas: 3│     │ replicas: 3 │     │ Pod 3 │
  └────────────┘     └─────────────┘     └───────┘
```

You do not need to create ReplicaSets yourself. Deployments handle them automatically. Think of the ReplicaSet as the Deployment's assistant.

### Writing a Deployment YAML

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
```

This is longer than the Pod YAML. Let us break it down section by section:

**Top section (same as any Kubernetes resource):**

| Line | Meaning |
|------|---------|
| `apiVersion: apps/v1` | Deployments are in the `apps` API group, version `v1`. |
| `kind: Deployment` | We are creating a Deployment. |
| `metadata: name: nginx-deployment` | The name of this Deployment. |

**Spec section (what makes a Deployment special):**

| Line | Meaning |
|------|---------|
| `replicas: 3` | Run 3 copies (replicas) of the Pod at all times. |
| `selector: matchLabels: app: nginx` | The Deployment manages Pods that have the label `app: nginx`. This is how the Deployment finds its Pods. |
| `template:` | The Pod template — a blueprint for creating Pods. |

**The template section** is basically a Pod definition embedded inside the Deployment. It has its own `metadata` (with labels) and its own `spec` (with containers).

```
Deployment YAML structure:

  ┌────────────────────────────────────┐
  │  Deployment                        │
  │  ┌──────────────────────────────┐  │
  │  │  apiVersion, kind, metadata  │  │
  │  ├──────────────────────────────┤  │
  │  │  spec:                       │  │
  │  │    replicas: 3               │  │
  │  │    selector: app=nginx       │  │
  │  │  ┌────────────────────────┐  │  │
  │  │  │  template (Pod spec)   │  │  │
  │  │  │  ┌──────────────────┐  │  │  │
  │  │  │  │  metadata:       │  │  │  │
  │  │  │  │    labels:       │  │  │  │
  │  │  │  │      app: nginx  │  │  │  │
  │  │  │  ├──────────────────┤  │  │  │
  │  │  │  │  spec:           │  │  │  │
  │  │  │  │    containers:   │  │  │  │
  │  │  │  │    - nginx:1.25  │  │  │  │
  │  │  │  └──────────────────┘  │  │  │
  │  │  └────────────────────────┘  │  │
  │  └──────────────────────────────┘  │
  └────────────────────────────────────┘
```

**Important:** The labels in `selector.matchLabels` must match the labels in `template.metadata.labels`. This is how the Deployment knows which Pods belong to it. If they do not match, Kubernetes will reject the YAML with an error.

### Creating the Deployment

```bash
kubectl apply -f deployment.yaml
```

```
deployment.apps/nginx-deployment created
```

### Inspecting the Deployment

```bash
kubectl get deployments
```

```
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3/3     3            3           30s
```

| Column | Meaning |
|--------|---------|
| **READY** | How many Pods are ready out of the desired number. `3/3` means all 3 are running. |
| **UP-TO-DATE** | How many Pods have been updated to the latest version. |
| **AVAILABLE** | How many Pods are available to serve traffic. |

**List the Pods created by the Deployment:**

```bash
kubectl get pods
```

```
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-7c79c4bf97-abc12   1/1     Running   0          45s
nginx-deployment-7c79c4bf97-def34   1/1     Running   0          45s
nginx-deployment-7c79c4bf97-ghi56   1/1     Running   0          45s
```

Notice the Pod names. They follow the pattern: `deployment-name` + `replicaset-hash` + `random-suffix`. The random suffix ensures each Pod has a unique name.

**List the ReplicaSet (created automatically):**

```bash
kubectl get replicasets
```

```
NAME                          DESIRED   CURRENT   READY   AGE
nginx-deployment-7c79c4bf97   3         3         3       1m
```

The ReplicaSet was created by the Deployment. You did not write any YAML for it.

### Self-Healing in Action

Now let us see self-healing in action. Delete one of the Pods:

```bash
kubectl delete pod nginx-deployment-7c79c4bf97-abc12
```

```
pod "nginx-deployment-7c79c4bf97-abc12" deleted
```

Immediately check the Pods again:

```bash
kubectl get pods
```

```
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-7c79c4bf97-def34   1/1     Running   0          2m
nginx-deployment-7c79c4bf97-ghi56   1/1     Running   0          2m
nginx-deployment-7c79c4bf97-jkl78   1/1     Running   0          3s
```

The Deployment noticed that only 2 Pods existed but the desired state was 3. It created a new Pod (`jkl78`) to replace the deleted one. The entire process took seconds and required no manual intervention.

This is the power of Deployments. **They ensure your desired state is always maintained.**

### Scaling: Changing the Number of Replicas

**Scale up (more Pods):**

```bash
kubectl scale deployment nginx-deployment --replicas=5
```

```
deployment.apps/nginx-deployment scaled
```

```bash
kubectl get pods
```

```
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-7c79c4bf97-def34   1/1     Running   0          5m
nginx-deployment-7c79c4bf97-ghi56   1/1     Running   0          5m
nginx-deployment-7c79c4bf97-jkl78   1/1     Running   0          3m
nginx-deployment-7c79c4bf97-mno90   1/1     Running   0          10s
nginx-deployment-7c79c4bf97-pqr12   1/1     Running   0          10s
```

Two new Pods appeared. Kubernetes found resources on the cluster and started them.

**Scale down (fewer Pods):**

```bash
kubectl scale deployment nginx-deployment --replicas=2
```

```
deployment.apps/nginx-deployment scaled
```

```bash
kubectl get pods
```

```
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-7c79c4bf97-def34   1/1     Running   0          6m
nginx-deployment-7c79c4bf97-ghi56   1/1     Running   0          6m
```

Kubernetes terminated 3 Pods, leaving only 2. It chose which ones to stop based on internal criteria (like how long they have been running and their current load).

### Rolling Updates: Deploying a New Version

One of the most powerful features of Deployments is **rolling updates**. When you deploy a new version of your application, Kubernetes replaces old Pods with new Pods one at a time, ensuring your application is never fully down.

**Update the image version:**

```bash
kubectl set image deployment/nginx-deployment nginx=nginx:1.26
```

```
deployment.apps/nginx-deployment image updated
```

Let us break down this command:

- `set image` — Change the container image.
- `deployment/nginx-deployment` — The Deployment to update.
- `nginx=nginx:1.26` — Change the container named "nginx" to use the image `nginx:1.26`.

**Watch the rollout progress:**

```bash
kubectl rollout status deployment/nginx-deployment
```

```
Waiting for deployment "nginx-deployment" rollout to finish: 1 out of 2
new replicas have been updated...
Waiting for deployment "nginx-deployment" rollout to finish: 1 old replicas
are pending termination...
deployment "nginx-deployment" successfully rolled out
```

**What happened behind the scenes:**

```
Rolling Update Process:

  Step 1: Original state
  ┌──────────┐  ┌──────────┐
  │ Pod v1.25│  │ Pod v1.25│
  └──────────┘  └──────────┘

  Step 2: Create new Pod, keep old ones running
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ Pod v1.25│  │ Pod v1.25│  │ Pod v1.26│
  └──────────┘  └──────────┘  └──────────┘
                                  NEW

  Step 3: New Pod is healthy, terminate one old Pod
  ┌──────────┐  ┌──────────┐
  │ Pod v1.25│  │ Pod v1.26│
  └──────────┘  └──────────┘

  Step 4: Create another new Pod
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ Pod v1.25│  │ Pod v1.26│  │ Pod v1.26│
  └──────────┘  └──────────┘  └──────────┘
                                  NEW

  Step 5: Terminate last old Pod
  ┌──────────┐  ┌──────────┐
  │ Pod v1.26│  │ Pod v1.26│
  └──────────┘  └──────────┘
                  ALL UPDATED
```

Kubernetes created new Pods with the updated image and gradually terminated old Pods. At no point were all Pods down simultaneously. Your users would not have experienced any downtime.

**Check the rollout history:**

```bash
kubectl rollout history deployment/nginx-deployment
```

```
deployment.apps/nginx-deployment
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

Each revision represents a version of your Deployment. Revision 1 was `nginx:1.25`, Revision 2 is `nginx:1.26`.

### Rollback: Undoing a Bad Update

What if the new version has a bug? You can roll back to the previous version:

```bash
kubectl rollout undo deployment/nginx-deployment
```

```
deployment.apps/nginx-deployment rolled back
```

This performs another rolling update, but in reverse — replacing the new version Pods with old version Pods. Your users experience zero downtime.

**Roll back to a specific revision:**

```bash
kubectl rollout undo deployment/nginx-deployment --to-revision=1
```

```
deployment.apps/nginx-deployment rolled back
```

This is like an "undo" button for your deployments. In a real production scenario, this can save you from a disaster.

---

## Services: Giving Pods a Stable Address

### The Problem: Pod IPs Change

You know that every Pod gets an IP address. But here is the problem: **Pod IPs are not permanent.**

When a Pod crashes and a new one replaces it, the new Pod gets a different IP address. When you scale up, the new Pods get new IPs. When you do a rolling update, all the Pods get new IPs.

If another application is trying to reach your Pods, how does it know what IP to use? It cannot hard-code the IP because the IP keeps changing.

```
The Problem:

  App ──► Pod (10.244.0.5)
                │
                ▼ Pod crashes
  App ──► ???   New Pod (10.244.0.9)
                │
                │ Where did it go?
```

### What Is a Service?

A **Service** is a stable network endpoint that provides a permanent address for a group of Pods. Think of it as a **phone number that never changes**.

You and your friends might change phone companies, move to different cities, and get new phones. But if you have a permanent office phone number, people can always reach you by calling that number. The phone number stays the same even if the person answering changes.

A Service works the same way. It has a permanent IP address and DNS name. When traffic comes to the Service, it forwards it to one of the healthy Pods behind it. If Pods change, the Service keeps working — it simply updates its list of Pods.

```
The Solution — a Service:

  ┌──────────────────────────────────────────┐
  │                                          │
  │  App ──► Service (10.96.0.1)             │
  │           "my-service"                   │
  │              │                           │
  │         ┌────┼────┐                      │
  │         ▼    ▼    ▼                      │
  │       Pod1  Pod2  Pod3                   │
  │                                          │
  │  Pods come and go.                       │
  │  Service IP stays the same.              │
  └──────────────────────────────────────────┘
```

### How Services Find Their Pods

Services use **labels** to find Pods. Remember the `labels:` section in our Pod template? The Service uses a **selector** that matches those labels.

```yaml
# In the Deployment template:
labels:
  app: nginx    # ◄── Pod has this label

# In the Service:
selector:
  app: nginx    # ◄── Service looks for Pods with this label
```

When a new Pod is created with the label `app: nginx`, the Service automatically discovers it and starts sending traffic to it. When a Pod with that label is deleted, the Service stops sending traffic to it. This happens automatically — you do not need to update anything.

### Service Types

Kubernetes has three main types of Services, each for a different use case:

```
Service Types:

  ClusterIP (internal only):
  ┌─────────────────────────────────┐
  │  Kubernetes Cluster              │
  │                                  │
  │  App A ──► Service ──► Pods      │
  │            (internal)            │
  │                                  │
  │  Only accessible from inside     │
  │  the cluster.                    │
  └─────────────────────────────────┘

  NodePort (accessible from outside):
  ┌─────────────────────────────────┐
  │  Kubernetes Cluster              │
  │                                  │
  │  Service ──► Pods                │
  │  Port 30080                      │
  │     ▲                            │
  └─────┼───────────────────────────┘
        │
  Your Browser ──► Node IP:30080

  LoadBalancer (cloud provider assigns an external IP):
  ┌─────────────────────────────────┐
  │  Cloud Provider                  │
  │  ┌───────────────────────────┐  │
  │  │ Load Balancer              │  │
  │  │ External IP: 34.56.78.90  │  │
  │  └────────────┬──────────────┘  │
  │               │                  │
  │  ┌────────────▼──────────────┐  │
  │  │  Kubernetes Cluster        │  │
  │  │  Service ──► Pods          │  │
  │  └───────────────────────────┘  │
  └─────────────────────────────────┘
```

| Type | What It Does | When to Use |
|------|-------------|-------------|
| **ClusterIP** | Creates an internal IP. Only accessible from inside the cluster. | Communication between services inside the cluster (e.g., app talks to database). |
| **NodePort** | Opens a port (30000-32767) on every node. Accessible from outside. | Development and testing. Quick way to access your app from your browser. |
| **LoadBalancer** | Asks the cloud provider to create an external load balancer. | Production on cloud providers (AWS, GCP, Azure). The standard way to expose apps to the internet. |

### ClusterIP Service (Default)

This is the default type. It creates an internal-only IP address.

```yaml
# service-clusterip.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-internal
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
```

| Line | Meaning |
|------|---------|
| `type: ClusterIP` | Internal-only Service. This is the default — you can omit this line and it will still be ClusterIP. |
| `selector: app: nginx` | Send traffic to Pods with the label `app: nginx`. |
| `port: 80` | The port the Service listens on. |
| `targetPort: 80` | The port on the Pod to forward traffic to. |

Use ClusterIP when you have a database or internal API that only other Pods need to access.

### NodePort Service

This opens a port on every node in the cluster so you can access the Service from outside.

```yaml
# service-nodeport.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-external
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

| Line | Meaning |
|------|---------|
| `type: NodePort` | Make this Service accessible from outside the cluster. |
| `nodePort: 30080` | The port to open on the node. Must be between 30000 and 32767. If you omit this, Kubernetes picks a random port in that range. |

```
NodePort traffic flow:

  Your Browser
      │
      │ http://node-ip:30080
      ▼
  ┌──────────┐
  │   Node   │
  │ Port     │
  │ 30080    │
  │    │     │
  │    ▼     │
  │ Service  │
  │ Port 80  │
  │    │     │
  │ ┌──┼──┐  │
  │ ▼  ▼  ▼  │
  │ P1 P2 P3 │  ◄── Pods on port 80
  └──────────┘
```

### LoadBalancer Service

On cloud providers, this creates a real load balancer with an external IP:

```yaml
# service-loadbalancer.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-public
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
```

On Minikube, LoadBalancer does not work the same way as on a cloud provider because there is no cloud load balancer. Minikube provides a workaround with `minikube service <service-name>`, which opens the Service in your browser.

---

## Complete Example: Nginx with 3 Replicas and a NodePort Service

Let us put everything together. We will deploy Nginx with 3 replicas and expose it via a NodePort Service so you can access it from your browser.

### Step 1: Create the Deployment

```yaml
# nginx-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-web
  labels:
    app: nginx-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx-web
  template:
    metadata:
      labels:
        app: nginx-web
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
```

### Step 2: Create the Service

```yaml
# nginx-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-web-service
spec:
  type: NodePort
  selector:
    app: nginx-web
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

### Step 3: Apply Both Files

```bash
kubectl apply -f nginx-deployment.yaml
```

```
deployment.apps/nginx-web created
```

```bash
kubectl apply -f nginx-service.yaml
```

```
service/nginx-web-service created
```

### Step 4: Verify Everything Is Running

```bash
kubectl get all
```

```
NAME                             READY   STATUS    RESTARTS   AGE
pod/nginx-web-5d4f8b7c69-abc12  1/1     Running   0          30s
pod/nginx-web-5d4f8b7c69-def34  1/1     Running   0          30s
pod/nginx-web-5d4f8b7c69-ghi56  1/1     Running   0          30s

NAME                        TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/kubernetes          ClusterIP   10.96.0.1      <none>        443/TCP        1h
service/nginx-web-service   NodePort    10.96.45.123   <none>        80:30080/TCP   30s

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nginx-web   3/3     3            3           30s

NAME                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/nginx-web-5d4f8b7c69   3         3         3       30s
```

The `kubectl get all` command shows everything: Pods, Services, Deployments, and ReplicaSets.

### Step 5: Access the Application

**On Minikube:**

```bash
minikube service nginx-web-service
```

```
|-----------|-------------------|-------------|---------------------------|
| NAMESPACE |       NAME        | TARGET PORT |            URL            |
|-----------|-------------------|-------------|---------------------------|
| default   | nginx-web-service |          80 | http://192.168.49.2:30080 |
|-----------|-------------------|-------------|---------------------------|
🎉  Opening service default/nginx-web-service in default browser...
```

Your browser opens and you see the Nginx welcome page. You have a web server running in Kubernetes!

**On Docker Desktop Kubernetes:**

```bash
curl http://localhost:30080
```

Or open `http://localhost:30080` in your browser.

### Step 6: Test Self-Healing

Delete one of the Pods and watch Kubernetes replace it:

```bash
kubectl delete pod nginx-web-5d4f8b7c69-abc12
```

```bash
kubectl get pods
```

```
NAME                             READY   STATUS    RESTARTS   AGE
nginx-web-5d4f8b7c69-def34      1/1     Running   0          5m
nginx-web-5d4f8b7c69-ghi56      1/1     Running   0          5m
nginx-web-5d4f8b7c69-jkl78      1/1     Running   0          5s
```

A new Pod was created within seconds. The Service automatically routes traffic to the remaining healthy Pods — your users would not notice a thing.

### Step 7: Clean Up

```bash
kubectl delete -f nginx-deployment.yaml
kubectl delete -f nginx-service.yaml
```

```
deployment.apps "nginx-web" deleted
service "nginx-web-service" deleted
```

---

## Common Mistakes

1. **Creating Pods directly instead of using Deployments.** Direct Pods do not self-heal. Always use Deployments unless you have a specific reason not to (like running a one-time batch job).

2. **Mismatched labels between Deployment selector and template.** The `selector.matchLabels` in the Deployment must match the `template.metadata.labels`. If they do not match, Kubernetes rejects the YAML.

3. **Mismatched labels between Service selector and Pod labels.** If the Service selector does not match any Pod labels, the Service will have no endpoints and traffic will go nowhere. Use `kubectl describe service <name>` to check the Endpoints field.

4. **Forgetting `containerPort` does not publish a port.** Unlike Docker's `-p` flag, `containerPort` in a Pod spec is informational only. It documents which port the container listens on. To actually access the Pod from outside, you need a Service.

5. **Using NodePort in production.** NodePort is great for development, but in production you should use LoadBalancer or Ingress. NodePort exposes a high-numbered port on every node, which is not user-friendly and can be a security concern.

6. **Not checking Pod events when a Pod is stuck.** If a Pod is in `Pending`, `ImagePullBackOff`, or `CrashLoopBackOff` status, run `kubectl describe pod <name>` and read the Events section. It tells you exactly what went wrong.

---

## Best Practices

1. **Always use Deployments.** Even if you only need one Pod, create a Deployment with `replicas: 1`. This gives you self-healing, rolling updates, and rollback for free.

2. **Use meaningful labels.** Labels like `app: nginx-web`, `environment: production`, and `team: backend` make it easy to organize and filter resources.

3. **Store YAML files in version control.** Put your Deployment and Service YAML files in Git. This creates a history of changes and lets you reproduce your setup on any cluster.

4. **Use `kubectl apply` instead of `kubectl create`.** The `apply` command is idempotent — you can run it multiple times, and it will update the resource if it exists or create it if it does not. The `create` command fails if the resource already exists.

5. **Set resource requests and limits.** In production, always specify how much CPU and memory your containers need. We will cover this in later chapters, but it prevents one application from consuming all the resources on a node.

---

## Quick Summary

Pods are the smallest deployable units in Kubernetes, wrapping one or more containers with a shared IP and storage. Deployments manage Pods by maintaining a desired number of replicas, handling self-healing, rolling updates, and rollbacks. Services provide stable network endpoints for accessing Pods, with three types: ClusterIP for internal communication, NodePort for external access during development, and LoadBalancer for production on cloud providers. Together, these three resources form the foundation of every Kubernetes application.

---

## Key Points

- A **Pod** is the smallest unit in Kubernetes — a wrapper around one or more containers
- Pods are mortal — they do not self-heal when created directly
- A **Deployment** manages Pods, ensuring the desired number of replicas are always running
- Deployments provide **self-healing**, **scaling**, **rolling updates**, and **rollback**
- `kubectl scale` changes the number of Pod replicas
- `kubectl set image` triggers a rolling update to a new version
- `kubectl rollout undo` reverts to a previous version
- A **Service** provides a stable IP and DNS name for accessing a group of Pods
- **ClusterIP** is for internal communication (default)
- **NodePort** exposes a port on every node (development/testing)
- **LoadBalancer** creates an external load balancer (production on cloud)
- Services find their Pods using **label selectors**

---

## Practice Questions

1. What is the difference between a Pod and a container? Why does Kubernetes use Pods instead of managing containers directly?

2. You create a Pod directly (without a Deployment). The Pod crashes at 2 AM. What happens? How would the outcome differ if you had used a Deployment?

3. Explain what happens step by step when you run `kubectl set image deployment/myapp myapp=myapp:v2`. Which components are involved?

4. You have a Deployment with `replicas: 3` and a Service with `selector: app: myapp`. You notice the Service is not routing traffic to any Pods. What is the most likely cause? How would you diagnose the issue?

5. When would you use a ClusterIP Service versus a NodePort Service? Give a real-world example of each.

---

## Exercises

### Exercise 1: Pod Lifecycle

1. Create a Pod YAML for an Nginx container (you can use the one from this chapter)
2. Apply it and verify it is running
3. View the Pod's logs
4. Run `kubectl exec` to get a shell inside the Pod
5. Delete the Pod and verify it does not come back

### Exercise 2: Deployment and Scaling

1. Create a Deployment YAML with `replicas: 2` using the `httpd:2.4` (Apache) image on port 80
2. Apply it and verify 2 Pods are running
3. Scale the Deployment to 5 replicas using `kubectl scale`
4. Delete one of the Pods and watch Kubernetes recreate it
5. Update the image to `httpd:2.4-alpine` and watch the rolling update
6. Roll back to the previous version

### Exercise 3: Complete Application

1. Create a Deployment for Nginx with 3 replicas
2. Create a NodePort Service for the Deployment on port 30080
3. Access the application from your browser (use `minikube service` or `curl localhost:30080`)
4. Scale the Deployment to 1 replica — does the Service still work?
5. Scale back to 3 replicas
6. Clean up all resources using `kubectl delete -f`

---

## What Is Next?

You now know how to deploy applications to Kubernetes with Deployments and expose them with Services. But real applications need more than just containers — they need configuration (database URLs, feature flags), secrets (passwords, API keys), and persistent storage (so data survives Pod restarts).

In the next chapter, you will learn about ConfigMaps (for configuration), Secrets (for sensitive data), and PersistentVolumes (for storage). These three resources turn simple containers into production-ready applications.
