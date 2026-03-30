# Chapter 30: Deploying a Real Application to Kubernetes

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Plan and deploy a multi-component application to Kubernetes
- Build a Docker image and make it available to your cluster
- Create a Kubernetes namespace for your project
- Configure an application using ConfigMaps and Secrets
- Set up persistent storage for a database
- Deploy PostgreSQL as a backend database with a ClusterIP Service
- Deploy a Node.js API with a NodePort Service
- Inspect all resources running in a namespace
- Test your application end to end with curl
- Scale your application by adding more replicas
- Perform a rolling update to deploy a new version
- Roll back a deployment when something goes wrong
- Understand what Ingress is and why you would use it
- Monitor resource usage with kubectl top

---

## Why This Chapter Matters

In the previous chapters, you learned about Pods, Deployments, Services, ConfigMaps, Secrets, and PersistentVolumes — each one individually. That is like learning individual ingredients in cooking. You know what flour is. You know what eggs are. You know what sugar does.

But knowing ingredients is different from baking a cake. This chapter is where you bake the cake.

You will deploy a complete, real-world application: a Node.js REST API backed by a PostgreSQL database. You will use every Kubernetes concept from the previous chapters, all working together. By the end, you will have a fully functional application running in your local Kubernetes cluster, and you will have the confidence to deploy applications to any Kubernetes environment.

---

## The Application Architecture

Here is what we are building:

```
Application Architecture:

  Your Browser / curl
        │
        │ HTTP request (port 30001)
        ▼
  ┌──────────────────────────────────────────────┐
  │  Kubernetes Cluster                           │
  │  Namespace: myapp                             │
  │                                               │
  │  ┌─────────────────────────────────────────┐  │
  │  │  NodePort Service (port 30001)           │  │
  │  │  "api-service"                           │  │
  │  └────────────────┬────────────────────────┘  │
  │                   │                            │
  │         ┌─────────┼─────────┐                  │
  │         ▼         ▼         ▼                  │
  │    ┌─────────┐ ┌─────────┐ ┌─────────┐        │
  │    │ API Pod │ │ API Pod │ │ API Pod │        │
  │    │ (v1.0)  │ │ (v1.0)  │ │ (v1.0)  │        │
  │    └────┬────┘ └────┬────┘ └────┬────┘        │
  │         │           │           │              │
  │         └───────────┼───────────┘              │
  │                     │                          │
  │  ┌──────────────────▼──────────────────────┐  │
  │  │  ClusterIP Service                       │  │
  │  │  "postgres-service"                      │  │
  │  └──────────────────┬──────────────────────┘  │
  │                     │                          │
  │               ┌─────▼─────┐                    │
  │               │ Postgres  │                    │
  │               │ Pod       │                    │
  │               │    │      │                    │
  │               │ ┌──▼───┐  │                    │
  │               │ │ PVC  │  │                    │
  │               │ │ Data │  │                    │
  │               │ └──────┘  │                    │
  │               └───────────┘                    │
  │                                               │
  │  ConfigMap: app-config (DB host, port, name)  │
  │  Secret: db-secret (DB password)              │
  └──────────────────────────────────────────────┘
```

The components:

| Component | Purpose |
|-----------|---------|
| **Namespace** | Isolates our app from other workloads in the cluster |
| **ConfigMap** | Stores application configuration (database host, port, name) |
| **Secret** | Stores the database password securely |
| **PVC** | Provides persistent storage for PostgreSQL data |
| **PostgreSQL Deployment** | Runs the database |
| **PostgreSQL ClusterIP Service** | Lets the API Pods reach the database (internal only) |
| **API Deployment** | Runs 3 replicas of the Node.js API |
| **API NodePort Service** | Exposes the API to the outside world |

---

## The Application Code

Before deploying to Kubernetes, we need a simple Node.js application. Here is a minimal REST API that connects to PostgreSQL.

### Project Structure

```
myapp/
├── server.js
├── package.json
└── Dockerfile
```

### server.js

```javascript
// server.js
const http = require('http');
const { Pool } = require('pg');

const PORT = process.env.PORT || 3000;
const APP_VERSION = process.env.APP_VERSION || '1.0.0';

// Database connection using environment variables
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'myapp',
  user: process.env.DB_USERNAME || 'postgres',
  password: process.env.DB_PASSWORD || 'password',
});

// Initialize database table
async function initDB() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        text VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    console.log('Database initialized');
  } catch (err) {
    console.error('Database init error:', err.message);
  }
}

const server = http.createServer(async (req, res) => {
  res.setHeader('Content-Type', 'application/json');

  // Health check endpoint
  if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({
      status: 'healthy',
      version: APP_VERSION,
    }));
    return;
  }

  // Get all messages
  if (req.url === '/messages' && req.method === 'GET') {
    try {
      const result = await pool.query(
        'SELECT * FROM messages ORDER BY created_at DESC'
      );
      res.writeHead(200);
      res.end(JSON.stringify(result.rows));
    } catch (err) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  // Create a message
  if (req.url === '/messages' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', async () => {
      try {
        const { text } = JSON.parse(body);
        const result = await pool.query(
          'INSERT INTO messages (text) VALUES ($1) RETURNING *',
          [text]
        );
        res.writeHead(201);
        res.end(JSON.stringify(result.rows[0]));
      } catch (err) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  // Default: 404
  res.writeHead(404);
  res.end(JSON.stringify({ error: 'Not found' }));
});

initDB().then(() => {
  server.listen(PORT, () => {
    console.log(`Server v${APP_VERSION} running on port ${PORT}`);
  });
});
```

Let us understand what this application does:

- It is a simple REST API with three endpoints:
  - `GET /health` — Returns the app version and health status
  - `GET /messages` — Lists all messages from the database
  - `POST /messages` — Saves a new message to the database
- It reads all configuration from **environment variables** (DB_HOST, DB_PORT, etc.)
- It connects to PostgreSQL using the `pg` library

### package.json

```json
{
  "name": "myapp",
  "version": "1.0.0",
  "description": "Simple API for Kubernetes demo",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "pg": "^8.11.0"
  }
}
```

### Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY server.js ./

EXPOSE 3000

CMD ["npm", "start"]
```

This Dockerfile follows the best practices from earlier chapters:

- Uses a small base image (`node:20-alpine`)
- Copies `package.json` first for better layer caching
- Installs only production dependencies
- Copies the application code last (so code changes do not trigger a full reinstall)

---

## Step 1: Build and Load the Docker Image

Before Kubernetes can run your application, it needs the Docker image. In a production environment, you would push the image to a registry (Docker Hub, ECR, GCR). For local development with Minikube, we have a shortcut.

### Option A: Minikube's Docker Environment

Minikube has its own Docker daemon running inside the cluster. You can point your local Docker client to Minikube's Docker daemon and build images directly there:

```bash
eval $(minikube docker-env)
```

```
# This command sets several environment variables that tell your
# Docker client to connect to Minikube's Docker daemon instead
# of your local Docker daemon.
```

Now build the image:

```bash
docker build -t myapp-api:1.0.0 ./myapp/
```

```
[+] Building 15.2s (10/10) FINISHED
 => [1/5] FROM docker.io/library/node:20-alpine
 => [2/5] WORKDIR /app
 => [3/5] COPY package*.json ./
 => [4/5] RUN npm install --production
 => [5/5] COPY server.js ./
 => exporting to image
 => => naming to docker.io/library/myapp-api:1.0.0
```

### Option B: Using minikube image load

If you prefer to build with your regular Docker and then load the image into Minikube:

```bash
docker build -t myapp-api:1.0.0 ./myapp/
minikube image load myapp-api:1.0.0
```

```
# This copies the image from your local Docker into Minikube's
# Docker daemon. It may take a minute for large images.
```

### Option C: Docker Desktop Kubernetes

If you are using Docker Desktop's Kubernetes, you do not need to do anything special. Docker Desktop shares images between Docker and Kubernetes automatically. Just build the image normally:

```bash
docker build -t myapp-api:1.0.0 ./myapp/
```

---

## Step 2: Create the Namespace

We will put all our resources in a dedicated namespace called `myapp`. This keeps everything organized and isolated.

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
```

```bash
kubectl apply -f k8s/namespace.yaml
```

```
namespace/myapp created
```

Set this namespace as the default so we do not have to type `-n myapp` with every command:

```bash
kubectl config set-context --current --namespace=myapp
```

```
Context "minikube" modified.
```

---

## Step 3: Create the ConfigMap

The ConfigMap stores our application's non-sensitive configuration:

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: myapp
data:
  DB_HOST: postgres-service
  DB_PORT: "5432"
  DB_NAME: myapp
  APP_VERSION: "1.0.0"
```

Notice that `DB_HOST` is set to `postgres-service`. This is the name of the Kubernetes Service we will create for PostgreSQL. Inside the cluster, Pods can reach each other using Service names as hostnames — Kubernetes' built-in DNS handles the resolution.

```bash
kubectl apply -f k8s/configmap.yaml
```

```
configmap/app-config created
```

---

## Step 4: Create the Secret

The Secret stores the database credentials:

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: myapp
type: Opaque
stringData:
  DB_USERNAME: appuser
  DB_PASSWORD: K8sD3moP@ss2024
  POSTGRES_USER: appuser
  POSTGRES_PASSWORD: K8sD3moP@ss2024
  POSTGRES_DB: myapp
```

We include both the `DB_*` variables (for our Node.js app) and the `POSTGRES_*` variables (which the official PostgreSQL Docker image uses to initialize the database).

```bash
kubectl apply -f k8s/secret.yaml
```

```
secret/db-secret created
```

**Reminder:** In a real project, do not commit this file to Git with plain-text passwords. Use Sealed Secrets, External Secrets Operator, or your cloud provider's secret management tool.

---

## Step 5: Create the PVC for Database Storage

PostgreSQL needs persistent storage so data survives Pod restarts:

```yaml
# k8s/postgres-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: myapp
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```bash
kubectl apply -f k8s/postgres-pvc.yaml
```

```
persistentvolumeclaim/postgres-data created
```

Verify it:

```bash
kubectl get pvc
```

```
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   AGE
postgres-data   Bound    pvc-abc12345-def6-7890-abcd-ef1234567890   1Gi        RWO            5s
```

Status is `Bound` — Minikube dynamically provisioned a PersistentVolume and linked it to our claim.

---

## Step 6: Deploy PostgreSQL

Now we deploy the database. PostgreSQL runs as a Deployment with 1 replica (databases are typically not scaled horizontally without special tools) and a ClusterIP Service (because only the API Pods need to access it, not the outside world).

### PostgreSQL Deployment

```yaml
# k8s/postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: myapp
  labels:
    app: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          ports:
            - containerPort: 5432
          envFrom:
            - secretRef:
                name: db-secret
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
              subPath: pgdata
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-data
```

Let us examine the new parts:

| Section | Meaning |
|---------|---------|
| `envFrom: secretRef: name: db-secret` | Injects all Secret values as environment variables. PostgreSQL uses `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` to create the initial database and user. |
| `mountPath: /var/lib/postgresql/data` | Where PostgreSQL stores its data files. |
| `subPath: pgdata` | Creates a subdirectory inside the PVC. PostgreSQL requires that its data directory is empty on first start. The `subPath` prevents the PVC's root directory (which may contain a "lost+found" folder) from interfering. |
| `resources: requests:` | How much CPU and memory the container needs at minimum. The Scheduler uses this to find a node with enough resources. |
| `resources: limits:` | The maximum CPU and memory the container can use. If it exceeds the memory limit, Kubernetes kills it. |

**Understanding resource values:**

- `250m` means 250 millicores = 0.25 CPU cores (one quarter of a CPU)
- `256Mi` means 256 mebibytes of memory (approximately 268 megabytes)

```bash
kubectl apply -f k8s/postgres-deployment.yaml
```

```
deployment.apps/postgres created
```

### PostgreSQL Service

```yaml
# k8s/postgres-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: myapp
spec:
  type: ClusterIP
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
```

We use **ClusterIP** because the database should only be accessible from inside the cluster. The API Pods will connect to it using the DNS name `postgres-service` (which is the Service name).

```bash
kubectl apply -f k8s/postgres-service.yaml
```

```
service/postgres-service created
```

### Verify PostgreSQL Is Running

```bash
kubectl get pods
```

```
NAME                        READY   STATUS    RESTARTS   AGE
postgres-7f9b8c6d45-x2k9m  1/1     Running   0          30s
```

Check the logs to make sure PostgreSQL initialized successfully:

```bash
kubectl logs deployment/postgres
```

```
PostgreSQL init process complete; ready for start up.
2024-01-15 17:00:00.000 UTC [1] LOG:  starting PostgreSQL 16.1
2024-01-15 17:00:00.000 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2024-01-15 17:00:00.000 UTC [1] LOG:  database system is ready to accept connections
```

PostgreSQL is running and ready.

---

## Step 7: Deploy the Node.js API

### API Deployment

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: myapp
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: myapp-api:1.0.0
          imagePullPolicy: Never
          ports:
            - containerPort: 3000
          envFrom:
            - configMapRef:
                name: app-config
            - secretRef:
                name: db-secret
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "200m"
```

Important details:

| Line | Meaning |
|------|---------|
| `replicas: 3` | Run 3 copies of the API for load distribution and reliability. |
| `imagePullPolicy: Never` | Do not try to pull this image from Docker Hub. We built it locally. Without this, Kubernetes would try to download `myapp-api:1.0.0` from the internet and fail. |
| `envFrom: configMapRef` | Injects ConfigMap values (DB_HOST, DB_PORT, etc.) as environment variables. |
| `envFrom: secretRef` | Injects Secret values (DB_USERNAME, DB_PASSWORD) as environment variables. |

The API container receives all the configuration it needs from the ConfigMap and Secret. It does not contain any hardcoded database URLs or passwords.

```bash
kubectl apply -f k8s/api-deployment.yaml
```

```
deployment.apps/api created
```

### API Service

```yaml
# k8s/api-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: myapp
spec:
  type: NodePort
  selector:
    app: api
  ports:
    - port: 3000
      targetPort: 3000
      nodePort: 30001
```

We use **NodePort** so you can access the API from your browser. Port 30001 on your node will forward traffic to port 3000 on the API Pods.

```bash
kubectl apply -f k8s/api-service.yaml
```

```
service/api-service created
```

---

## Step 8: Inspect Everything

Now let us see all the resources we created:

```bash
kubectl get all -n myapp
```

```
NAME                            READY   STATUS    RESTARTS   AGE
pod/api-6d8f9b7c54-abc12       1/1     Running   0          1m
pod/api-6d8f9b7c54-def34       1/1     Running   0          1m
pod/api-6d8f9b7c54-ghi56       1/1     Running   0          1m
pod/postgres-7f9b8c6d45-x2k9m  1/1     Running   0          3m

NAME                       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
service/api-service        NodePort    10.96.123.45    <none>        3000:30001/TCP   1m
service/postgres-service   ClusterIP   10.96.67.89     <none>        5432/TCP         3m

NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/api        3/3     3            3           1m
deployment.apps/postgres   1/1     1            1           3m

NAME                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/api-6d8f9b7c54       3         3         3       1m
replicaset.apps/postgres-7f9b8c6d45  1         1         1       3m
```

Let us also check our other resources:

```bash
kubectl get configmaps -n myapp
```

```
NAME               DATA   AGE
app-config         4      5m
kube-root-ca.crt   1      5m
```

```bash
kubectl get secrets -n myapp
```

```
NAME        TYPE     DATA   AGE
db-secret   Opaque   5      5m
```

```bash
kubectl get pvc -n myapp
```

```
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   AGE
postgres-data   Bound    pvc-abc12345-def6-7890-abcd-ef1234567890   1Gi        RWO            5m
```

Everything is running. Let us count what we have:

```
Resources in namespace "myapp":

  Namespace:    1  (myapp)
  ConfigMap:    1  (app-config)
  Secret:       1  (db-secret)
  PVC:          1  (postgres-data)
  Deployments:  2  (api, postgres)
  Pods:         4  (3 API + 1 PostgreSQL)
  Services:     2  (api-service, postgres-service)
  ReplicaSets:  2  (created automatically by Deployments)
  ─────────────────
  Total:       10  Kubernetes resources
```

---

## Step 9: Test the Application

### Get the Application URL

**On Minikube:**

```bash
minikube service api-service -n myapp --url
```

```
http://192.168.49.2:30001
```

**On Docker Desktop:**

The URL is `http://localhost:30001`.

### Test the Health Endpoint

```bash
curl http://192.168.49.2:30001/health
```

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

The API is running and reports itself as healthy with version 1.0.0.

### Create a Message

```bash
curl -X POST http://192.168.49.2:30001/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Kubernetes!"}'
```

```json
{
  "id": 1,
  "text": "Hello from Kubernetes!",
  "created_at": "2024-01-15T17:10:00.000Z"
}
```

### List All Messages

```bash
curl http://192.168.49.2:30001/messages
```

```json
[
  {
    "id": 1,
    "text": "Hello from Kubernetes!",
    "created_at": "2024-01-15T17:10:00.000Z"
  }
]
```

### Add More Messages

```bash
curl -X POST http://192.168.49.2:30001/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "Kubernetes is managing my app!"}'

curl -X POST http://192.168.49.2:30001/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "Data persists across Pod restarts!"}'
```

```bash
curl http://192.168.49.2:30001/messages
```

```json
[
  {
    "id": 3,
    "text": "Data persists across Pod restarts!",
    "created_at": "2024-01-15T17:12:00.000Z"
  },
  {
    "id": 2,
    "text": "Kubernetes is managing my app!",
    "created_at": "2024-01-15T17:11:00.000Z"
  },
  {
    "id": 1,
    "text": "Hello from Kubernetes!",
    "created_at": "2024-01-15T17:10:00.000Z"
  }
]
```

The application is fully functional. Data is stored in PostgreSQL, which uses a PersistentVolume. Even if the PostgreSQL Pod restarts, the data will survive.

---

## Step 10: Scale the Application

Your API is getting popular. Let us add more replicas:

```bash
kubectl scale deployment api -n myapp --replicas=5
```

```
deployment.apps/api scaled
```

```bash
kubectl get pods -n myapp -l app=api
```

```
NAME                   READY   STATUS    RESTARTS   AGE
api-6d8f9b7c54-abc12   1/1     Running   0          10m
api-6d8f9b7c54-def34   1/1     Running   0          10m
api-6d8f9b7c54-ghi56   1/1     Running   0          10m
api-6d8f9b7c54-jkl78   1/1     Running   0          15s
api-6d8f9b7c54-mno90   1/1     Running   0          15s
```

The `-l app=api` flag filters Pods by label, showing only API Pods. Two new Pods started in 15 seconds.

The Service automatically discovers the new Pods (because they have the label `app: api`) and starts routing traffic to them. No configuration change needed.

```
After Scaling:

  api-service (NodePort 30001)
        │
  ┌─────┼─────┬─────┬─────┬─────┐
  ▼     ▼     ▼     ▼     ▼     │
  Pod1  Pod2  Pod3  Pod4  Pod5   │
                                  │
  Traffic distributed across      │
  all 5 Pods automatically        │
```

Scale back down when traffic decreases:

```bash
kubectl scale deployment api -n myapp --replicas=3
```

```
deployment.apps/api scaled
```

---

## Step 11: Rolling Update (Deploy a New Version)

Let us say you have improved your application. Version 2.0.0 adds a timestamp to the health endpoint. In a real project, you would modify the code, rebuild the image, and push it. For this example, we will simulate a rolling update.

### Build the New Version

Modify `server.js` to change `APP_VERSION` to `2.0.0` (or set it via the ConfigMap). Then rebuild:

```bash
# If using Minikube docker-env:
docker build -t myapp-api:2.0.0 ./myapp/

# If using minikube image load:
docker build -t myapp-api:2.0.0 ./myapp/
minikube image load myapp-api:2.0.0
```

### Update the ConfigMap

```bash
kubectl patch configmap app-config -n myapp \
  --type merge -p '{"data":{"APP_VERSION":"2.0.0"}}'
```

```
configmap/app-config patched
```

### Trigger the Rolling Update

```bash
kubectl set image deployment/api -n myapp api=myapp-api:2.0.0
```

```
deployment.apps/api image updated
```

### Watch the Rolling Update

```bash
kubectl rollout status deployment/api -n myapp
```

```
Waiting for deployment "api" rollout to finish: 1 out of 3 new replicas
have been updated...
Waiting for deployment "api" rollout to finish: 2 out of 3 new replicas
have been updated...
Waiting for deployment "api" rollout to finish: 1 old replicas are
pending termination...
deployment "api" successfully rolled out
```

### Verify the New Version

```bash
curl http://192.168.49.2:30001/health
```

```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

The application has been updated to version 2.0.0 with zero downtime. During the update, at least 2 of the 3 Pods were always running, so users experienced no interruption.

### Check the Rollout History

```bash
kubectl rollout history deployment/api -n myapp
```

```
deployment.apps/api
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

---

## Step 12: Rollback

Something is wrong with version 2.0.0. Users are reporting errors. You need to roll back immediately.

```bash
kubectl rollout undo deployment/api -n myapp
```

```
deployment.apps/api rolled back
```

```bash
kubectl rollout status deployment/api -n myapp
```

```
deployment "api" successfully rolled out
```

```bash
curl http://192.168.49.2:30001/health
```

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

Back to version 1.0.0. The rollback performed another rolling update in reverse — replacing version 2.0.0 Pods with version 1.0.0 Pods. The entire process took seconds and happened with zero downtime.

```
Rollback Flow:

  v2.0.0  v2.0.0  v2.0.0   ◄── Current (broken)
     │
     ▼  kubectl rollout undo
  v1.0.0  v2.0.0  v2.0.0   ◄── Rolling back...
     │
     ▼
  v1.0.0  v1.0.0  v2.0.0   ◄── Almost done...
     │
     ▼
  v1.0.0  v1.0.0  v1.0.0   ◄── Rollback complete!
```

---

## Ingress: A Brief Introduction

So far, you have been accessing your application through NodePort (a high-numbered port like 30001). This works for development, but in production you want users to access your application through a real domain name like `api.mycompany.com` on port 80 (HTTP) or 443 (HTTPS).

This is where **Ingress** comes in.

### What Is Ingress?

An **Ingress** is a Kubernetes resource that manages external HTTP and HTTPS access to your Services. Think of it as a **front desk** at a building — visitors tell the front desk which department they want (which Service), and the front desk directs them to the right floor.

```
Without Ingress:

  User ──► NodePort 30001 ──► API Service
  User ──► NodePort 30002 ──► Web Service
  User ──► NodePort 30003 ──► Admin Service

  Ugly URLs: http://mysite.com:30001, :30002, :30003

With Ingress:

  User ──► api.mysite.com    ──► Ingress ──► API Service
  User ──► www.mysite.com    ──► Ingress ──► Web Service
  User ──► admin.mysite.com  ──► Ingress ──► Admin Service

  Clean URLs: http://api.mysite.com (port 80)
```

### A Simple Ingress Example

```yaml
# This is for reference — we will not apply this in our local setup
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: myapp
spec:
  rules:
    - host: api.mysite.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 3000
```

This tells Kubernetes: "When someone visits `api.mysite.com`, send the traffic to the `api-service` Service on port 3000."

Ingress requires an **Ingress Controller** (like Nginx Ingress Controller or Traefik) to be installed in the cluster. Managed Kubernetes services (EKS, GKE, AKS) provide their own Ingress Controllers. We will not set one up here, but you now know what Ingress is and when you would use it.

---

## Monitoring with kubectl top

Kubernetes can show you how much CPU and memory your Pods are using with the `kubectl top` command.

### Enable Metrics (Minikube)

First, enable the metrics server:

```bash
minikube addons enable metrics-server
```

```
💡  metrics-server is an addon maintained by Kubernetes. For any concerns
    contact minikube on GitHub.
🌟  The 'metrics-server' addon is enabled
```

Wait about a minute for the metrics server to start collecting data.

### View Node Resource Usage

```bash
kubectl top nodes
```

```
NAME       CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
minikube   250m         12%    1200Mi          30%
```

This shows your Minikube node is using 250 millicores (12% of its CPU) and 1200 mebibytes of memory (30% of total).

### View Pod Resource Usage

```bash
kubectl top pods -n myapp
```

```
NAME                        CPU(cores)   MEMORY(bytes)
api-6d8f9b7c54-abc12       2m           45Mi
api-6d8f9b7c54-def34       1m           42Mi
api-6d8f9b7c54-ghi56       2m           44Mi
postgres-7f9b8c6d45-x2k9m  5m           120Mi
```

Each API Pod is using about 2 millicores of CPU and 44 megabytes of memory. PostgreSQL is using more — 5 millicores and 120 megabytes. These numbers help you tune the resource requests and limits in your Deployment YAML.

---

## Cleaning Up

When you are done, clean up all resources:

### Option 1: Delete the Namespace (removes everything)

```bash
kubectl delete namespace myapp
```

```
namespace "myapp" deleted
```

This deletes the namespace and **everything inside it** — all Pods, Deployments, Services, ConfigMaps, Secrets, and PVCs. One command to clean up everything.

### Option 2: Delete Resources Individually

```bash
kubectl delete -f k8s/api-service.yaml -n myapp
kubectl delete -f k8s/api-deployment.yaml -n myapp
kubectl delete -f k8s/postgres-service.yaml -n myapp
kubectl delete -f k8s/postgres-deployment.yaml -n myapp
kubectl delete -f k8s/postgres-pvc.yaml -n myapp
kubectl delete -f k8s/secret.yaml -n myapp
kubectl delete -f k8s/configmap.yaml -n myapp
kubectl delete -f k8s/namespace.yaml
```

### Reset the Default Namespace

```bash
kubectl config set-context --current --namespace=default
```

```
Context "minikube" modified.
```

---

## Congratulations!

You have successfully deployed a real, multi-component application to Kubernetes. Let us recap everything you accomplished:

1. Built a Docker image for a Node.js API
2. Created a Kubernetes namespace to isolate your project
3. Used a ConfigMap to externalize application configuration
4. Used a Secret to protect database credentials
5. Used a PersistentVolumeClaim to give PostgreSQL durable storage
6. Deployed PostgreSQL with a ClusterIP Service for internal access
7. Deployed a Node.js API with 3 replicas and a NodePort Service
8. Tested the application end to end with curl
9. Scaled the API from 3 to 5 replicas and back
10. Performed a rolling update to deploy a new version with zero downtime
11. Rolled back when the new version had issues
12. Learned about Ingress for production-grade URL routing
13. Monitored resource usage with kubectl top

You have gone from knowing nothing about Kubernetes to deploying and managing a real application. That is a significant achievement.

---

## What to Learn Next

Kubernetes is a vast ecosystem. Here are the most important topics to explore after mastering the basics:

| Topic | What It Is | Why It Matters |
|-------|-----------|----------------|
| **Helm** | A package manager for Kubernetes (like npm for Node.js or apt for Linux) | Lets you install complex applications with one command and manage configuration templates |
| **Terraform** | Infrastructure as Code tool | Lets you create and manage Kubernetes clusters and cloud resources using code |
| **Service Mesh (Istio, Linkerd)** | Advanced networking layer | Provides traffic management, security, and observability between services |
| **CI/CD Pipelines** | Automated build and deploy | Automates building images, running tests, and deploying to Kubernetes when you push code |
| **Horizontal Pod Autoscaler** | Automatic scaling | Automatically adjusts the number of Pod replicas based on CPU, memory, or custom metrics |
| **Network Policies** | Firewall rules for Pods | Controls which Pods can communicate with each other |
| **RBAC** | Role-Based Access Control | Controls who can do what in the cluster |
| **Prometheus + Grafana** | Monitoring and dashboards | Collects metrics from your applications and displays them in visual dashboards |

---

## Common Mistakes

1. **Forgetting `imagePullPolicy: Never` for local images.** Without this, Kubernetes tries to pull the image from Docker Hub, fails, and the Pod enters `ImagePullBackOff` status.

2. **Not setting the namespace in YAML files.** If you forget to set `namespace: myapp` in your YAML, resources get created in the `default` namespace. Always include the namespace in the metadata section.

3. **Wrong Service name in DB_HOST.** The ConfigMap's `DB_HOST` must exactly match the PostgreSQL Service name. If the Service is called `postgres-service` but you set `DB_HOST=postgres`, the API cannot find the database.

4. **Not using `subPath` for PostgreSQL volumes.** PostgreSQL requires its data directory to be empty on initialization. Without `subPath: pgdata`, the PVC's root directory might contain a `lost+found` folder that causes PostgreSQL to fail.

5. **Deleting the PVC without backing up data.** Deleting a PVC permanently destroys the data on the underlying PersistentVolume (depending on the reclaim policy). Always back up important data before deleting PVCs.

6. **Scaling the database Deployment.** Do not run `kubectl scale deployment postgres --replicas=3`. PostgreSQL is not designed to be scaled this way. Multiple PostgreSQL instances writing to separate volumes would result in separate, inconsistent databases. Database scaling requires specialized tools like Patroni or CrunchyData Postgres Operator.

---

## Best Practices

1. **Use namespaces for every project.** Namespaces keep resources organized and make cleanup easy (`kubectl delete namespace` removes everything).

2. **Always set resource requests and limits.** Without them, a single Pod can consume all resources on a node and starve other Pods.

3. **Use health checks (readiness and liveness probes).** We did not cover these in detail, but production Deployments should define probes so Kubernetes knows when a container is healthy and ready to receive traffic.

4. **Use declarative YAML files for everything.** Store all your manifests in Git. This makes your infrastructure reproducible and auditable.

5. **Tag your images with specific versions.** Use `myapp:1.0.0`, not `myapp:latest`. The `latest` tag makes it unclear which version is running and can cause unexpected behavior during rollbacks.

6. **Separate database Deployments from application Deployments.** Databases have different lifecycle requirements (single replica, persistent storage, careful upgrades). Keep them in separate YAML files.

---

## Quick Summary

Deploying a real application to Kubernetes involves creating multiple interconnected resources: a Namespace for isolation, ConfigMaps for settings, Secrets for credentials, PVCs for storage, Deployments for running Pods, and Services for networking. The database uses a ClusterIP Service for internal access, while the API uses a NodePort Service for external access. Kubernetes provides scaling, rolling updates, and rollback out of the box, enabling zero-downtime deployments and quick recovery from bad releases.

---

## Key Points

- A complete Kubernetes application typically requires: Namespace, ConfigMap, Secret, PVC, Deployments, and Services
- Use `imagePullPolicy: Never` for locally built images in Minikube
- Kubernetes DNS lets Pods reach Services by name (e.g., `postgres-service`)
- Use **ClusterIP** for internal services (databases) and **NodePort** or **LoadBalancer** for external services (APIs)
- `kubectl get all -n <namespace>` shows all resources in a namespace
- `kubectl scale` adjusts the number of Pod replicas instantly
- `kubectl set image` triggers a rolling update with zero downtime
- `kubectl rollout undo` rolls back to the previous version immediately
- **Ingress** provides production-grade HTTP routing with domain names
- `kubectl top` shows CPU and memory usage for nodes and Pods
- Always set **resource requests and limits** in production
- Use **specific image tags** (not `latest`) for reproducible deployments

---

## Practice Questions

1. You deploy an API with 3 replicas and a database with 1 replica. Why should you not scale the database Deployment to 3 replicas the same way you scaled the API?

2. Your API Pods are in `ImagePullBackOff` status. You built the image locally with Docker. What did you forget to do? How do you fix it?

3. After a rolling update, users report errors. Walk through the steps to roll back the deployment. What commands would you run, and what would you check afterwards?

4. Explain why the PostgreSQL Service uses ClusterIP while the API Service uses NodePort. What would happen if you used NodePort for the database?

5. You change a value in the ConfigMap, but the running Pods still use the old value. Why? What do you need to do to make the Pods pick up the new configuration?

---

## Exercises

### Exercise 1: Deploy Your Own Application

1. Create a simple application in any language (Python Flask, Go, Ruby Sinatra, or even a static HTML site with Nginx)
2. Write a Dockerfile and build the image
3. Create the full set of Kubernetes manifests (Namespace, ConfigMap, Deployment, Service)
4. Deploy it to your local cluster
5. Access it from your browser
6. Scale it to 5 replicas and verify all Pods are running

### Exercise 2: Rolling Update Practice

1. Deploy the Nginx image version `1.24` with 3 replicas
2. Create a NodePort Service for it
3. Perform a rolling update to `nginx:1.25`
4. Check the rollout history
5. Roll back to `nginx:1.24`
6. Verify the rollback was successful

### Exercise 3: Full Stack Application

1. Using the Node.js + PostgreSQL example from this chapter as a guide, deploy a different stack:
   - A Python Flask or Go API
   - A Redis or MySQL database
   - ConfigMaps for application settings
   - Secrets for database credentials
   - PVC for database storage
2. Test all endpoints
3. Perform a rolling update and rollback
4. Clean up by deleting the namespace

---

## What Is Next?

You have completed the Kubernetes section of this book. You can now build Docker images, compose multi-container applications, and deploy them to Kubernetes with confidence.

The skills you have learned — containerization with Docker and orchestration with Kubernetes — are the foundation of modern cloud-native development. Companies around the world use these tools every day to run applications at scale.

Here is your roadmap for continued learning:

1. **Helm** — Learn to package and share Kubernetes applications as reusable charts
2. **CI/CD** — Set up automated pipelines (GitHub Actions, GitLab CI, Jenkins) that build, test, and deploy to Kubernetes on every code push
3. **Terraform** — Manage your Kubernetes clusters and cloud infrastructure as code
4. **Monitoring** — Set up Prometheus and Grafana to watch your applications in real time
5. **Service Mesh** — Explore Istio or Linkerd for advanced traffic management and security between microservices

Congratulations on finishing this journey. You started with "What is Docker?" and ended with a fully deployed, scalable application on Kubernetes. Keep building, keep learning, and keep deploying.
