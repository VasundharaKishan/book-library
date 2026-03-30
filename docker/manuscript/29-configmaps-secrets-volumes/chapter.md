# Chapter 29: ConfigMaps, Secrets, and Persistent Volumes

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Explain what a ConfigMap is and why you need one
- Create ConfigMaps from literal values, from files, and from YAML manifests
- Mount ConfigMaps as environment variables and as files inside a container
- Explain what a Secret is and how it differs from a ConfigMap
- Create Secrets and understand base64 encoding
- Mount Secrets as environment variables and as files
- Explain why Kubernetes Secrets are not truly secret by default
- Understand PersistentVolumes (PV) and PersistentVolumeClaims (PVC)
- Create a PVC and mount it in a Pod to store persistent data
- Build a complete application with ConfigMap, Secret, and PVC

---

## Why This Chapter Matters

In the previous chapter, you deployed Nginx to Kubernetes with a Deployment and Service. That works for a simple web server. But real applications need more:

- **Configuration.** Your application needs to know the database URL, the log level, and the feature flags. These settings change between environments (development, staging, production). You do not want to rebuild the Docker image every time a setting changes.

- **Secrets.** Your application needs passwords, API keys, and TLS certificates. These are sensitive. You cannot put them in your Docker image or in plain-text configuration files that end up in Git.

- **Persistent storage.** When a Pod is deleted and recreated, all data inside the container is lost. If your database runs in a Pod and the Pod restarts, all your data is gone. You need storage that survives Pod restarts.

ConfigMaps, Secrets, and PersistentVolumes solve these three problems. Every production Kubernetes application uses at least one of them. Most use all three.

---

## ConfigMaps: Externalized Configuration

### What Is a ConfigMap?

A **ConfigMap** is a Kubernetes resource that stores configuration data as key-value pairs. Think of it as a **settings file that lives outside your application**.

In traditional software development, configuration is often baked into the application:

```
Without ConfigMap:

  ┌─────────────────────────────┐
  │  Docker Image               │
  │  ┌───────────────────────┐  │
  │  │  Application Code     │  │
  │  │  + config.json         │  │
  │  │  + database_url        │  │
  │  │  + log_level           │  │
  │  └───────────────────────┘  │
  └─────────────────────────────┘

  Problem: To change a setting, you must
  rebuild the image and redeploy!
```

With a ConfigMap, configuration lives separately:

```
With ConfigMap:

  ┌─────────────────────┐     ┌──────────────────┐
  │  Docker Image        │     │  ConfigMap        │
  │  ┌───────────────┐  │     │                    │
  │  │  Application  │◄─┼─────┤  database_url=...  │
  │  │  Code         │  │     │  log_level=debug    │
  │  │  (no config)  │  │     │  feature_x=true     │
  │  └───────────────┘  │     └──────────────────┘
  └─────────────────────┘

  Benefit: Change settings without rebuilding
  the image or restarting the container!
```

### Why Use ConfigMaps?

1. **Separate configuration from code.** This is a fundamental best practice in software engineering. Your Docker image should contain only the application code. Configuration should be injected at runtime.

2. **Different settings per environment.** The same Docker image can run in development with debug logging and in production with error-only logging. You just change the ConfigMap.

3. **No rebuilds for config changes.** Changing a database URL or feature flag does not require building a new Docker image.

### Creating a ConfigMap from Literal Values

The simplest way to create a ConfigMap is from the command line:

```bash
kubectl create configmap app-config \
  --from-literal=DATABASE_HOST=postgres \
  --from-literal=DATABASE_PORT=5432 \
  --from-literal=LOG_LEVEL=debug
```

```
configmap/app-config created
```

Let us break this down:

- `kubectl create configmap` — Create a new ConfigMap resource.
- `app-config` — The name of the ConfigMap.
- `--from-literal=KEY=VALUE` — Add a key-value pair. You can add as many as you need.

**Verify the ConfigMap:**

```bash
kubectl get configmaps
```

```
NAME               DATA   AGE
app-config         3      10s
kube-root-ca.crt   1      1h
```

**View the ConfigMap contents:**

```bash
kubectl describe configmap app-config
```

```
Name:         app-config
Namespace:    default
Labels:       <none>
Annotations:  <none>

Data
====
DATABASE_HOST:
----
postgres
DATABASE_PORT:
----
5432
LOG_LEVEL:
----
debug

Events:  <none>
```

You can see all three key-value pairs stored in the ConfigMap.

### Creating a ConfigMap from a File

You can also create a ConfigMap from an existing file. This is useful when you have a configuration file like `app.properties` or `config.json`.

Create a file called `app.properties`:

```
# app.properties
database.host=postgres
database.port=5432
database.name=myapp
log.level=debug
feature.new_ui=true
```

Create the ConfigMap from this file:

```bash
kubectl create configmap app-file-config --from-file=app.properties
```

```
configmap/app-file-config created
```

The entire file becomes a single entry in the ConfigMap, with the filename as the key and the file contents as the value.

```bash
kubectl describe configmap app-file-config
```

```
Name:         app-file-config
Namespace:    default

Data
====
app.properties:
----
# app.properties
database.host=postgres
database.port=5432
database.name=myapp
log.level=debug
feature.new_ui=true

Events:  <none>
```

### Creating a ConfigMap from YAML

The declarative approach (recommended for production):

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_HOST: postgres
  DATABASE_PORT: "5432"
  LOG_LEVEL: debug
  APP_NAME: my-application
```

Let us break this down:

| Line | Meaning |
|------|---------|
| `apiVersion: v1` | ConfigMaps are part of the core API. |
| `kind: ConfigMap` | We are creating a ConfigMap. |
| `metadata: name: app-config` | The name of the ConfigMap. |
| `data:` | The key-value pairs. |
| `DATABASE_HOST: postgres` | A configuration entry. The key is `DATABASE_HOST`, the value is `postgres`. |
| `DATABASE_PORT: "5432"` | Note the quotes around `5432`. YAML treats unquoted numbers as integers, but ConfigMap values must be strings. Always quote numbers. |

Apply it:

```bash
kubectl apply -f configmap.yaml
```

```
configmap/app-config created
```

### Using ConfigMaps as Environment Variables

The most common way to use a ConfigMap is to inject its values as environment variables into your container.

```yaml
# pod-with-configmap-env.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-config
spec:
  containers:
    - name: myapp
      image: busybox
      command: ["sh", "-c", "echo DB=$DATABASE_HOST:$DATABASE_PORT LOG=$LOG_LEVEL && sleep 3600"]
      envFrom:
        - configMapRef:
            name: app-config
```

| Line | Meaning |
|------|---------|
| `envFrom:` | Load environment variables from an external source. |
| `configMapRef:` | The source is a ConfigMap. |
| `name: app-config` | Use the ConfigMap named "app-config". |

This injects **all** key-value pairs from the ConfigMap as environment variables. The container can access them like normal environment variables.

```bash
kubectl apply -f pod-with-configmap-env.yaml
```

```bash
kubectl logs app-with-config
```

```
DB=postgres:5432 LOG=debug
```

The application received the configuration values as environment variables.

**Injecting specific values (instead of all):**

If you only want some values from the ConfigMap, use `env` with `valueFrom`:

```yaml
# pod-with-selective-env.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-selective-config
spec:
  containers:
    - name: myapp
      image: busybox
      command: ["sh", "-c", "echo Host=$DB_HOST Level=$LOG && sleep 3600"]
      env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: DATABASE_HOST
        - name: LOG
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL
```

This gives you more control. You can rename the environment variables (the ConfigMap key is `DATABASE_HOST`, but inside the container it becomes `DB_HOST`) and only inject what you need.

### Mounting ConfigMaps as Files

Sometimes your application reads configuration from a file instead of environment variables. You can mount a ConfigMap as a file inside the container.

```yaml
# pod-with-configmap-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-config-file
spec:
  containers:
    - name: myapp
      image: busybox
      command: ["sh", "-c", "cat /etc/config/DATABASE_HOST && sleep 3600"]
      volumeMounts:
        - name: config-volume
          mountPath: /etc/config
  volumes:
    - name: config-volume
      configMap:
        name: app-config
```

Let us break down the volume parts:

| Section | Meaning |
|---------|---------|
| `volumes:` | Define a volume. A volume is a directory that is accessible to containers. |
| `name: config-volume` | Give this volume a name. |
| `configMap: name: app-config` | The volume's content comes from the ConfigMap "app-config". |
| `volumeMounts:` | Attach the volume to the container. |
| `name: config-volume` | Which volume to mount (matches the name above). |
| `mountPath: /etc/config` | Where to mount it inside the container. |

Each key in the ConfigMap becomes a file inside `/etc/config/`:

```
/etc/config/
├── DATABASE_HOST    (contains "postgres")
├── DATABASE_PORT    (contains "5432")
├── LOG_LEVEL        (contains "debug")
└── APP_NAME         (contains "my-application")
```

```
ConfigMap as Volume:

  ┌───────────────────────────────┐
  │  Pod                          │
  │  ┌─────────────────────────┐  │
  │  │  Container              │  │
  │  │                         │  │
  │  │  /etc/config/           │  │
  │  │    ├── DATABASE_HOST    │  │
  │  │    ├── DATABASE_PORT    │◄─┼── ConfigMap
  │  │    ├── LOG_LEVEL        │  │   "app-config"
  │  │    └── APP_NAME         │  │
  │  └─────────────────────────┘  │
  └───────────────────────────────┘
```

---

## Secrets: Sensitive Data

### What Is a Secret?

A **Secret** is like a ConfigMap, but designed for sensitive data — passwords, API keys, TLS certificates, and database credentials.

Think of it this way: a ConfigMap is like a **bulletin board** in your office. Anyone can see it, and that is fine because it contains general information. A Secret is like a **locked drawer** — it contains sensitive information that should be handled with care.

```
ConfigMap vs. Secret:

  ConfigMap                     Secret
  ┌───────────────────┐        ┌───────────────────┐
  │ LOG_LEVEL=debug   │        │ DB_PASSWORD=s3cr3t│
  │ APP_NAME=myapp    │        │ API_KEY=abc123xyz │
  │ FEATURE_X=true    │        │ TLS_CERT=...      │
  │                   │        │                   │
  │ Non-sensitive      │        │ Sensitive!         │
  │ Plain text in etcd │        │ Base64 in etcd     │
  └───────────────────┘        └───────────────────┘
```

### Creating a Secret from the Command Line

```bash
kubectl create secret generic db-credentials \
  --from-literal=DB_USERNAME=admin \
  --from-literal=DB_PASSWORD=supersecretpassword123
```

```
secret/db-credentials created
```

Let us break this down:

- `kubectl create secret generic` — Create a new Secret of type "generic" (the most common type for arbitrary key-value pairs).
- `db-credentials` — The name of the Secret.
- `--from-literal=KEY=VALUE` — Add a key-value pair.

**Verify the Secret:**

```bash
kubectl get secrets
```

```
NAME              TYPE     DATA   AGE
db-credentials    Opaque   2      10s
```

**View the Secret details:**

```bash
kubectl describe secret db-credentials
```

```
Name:         db-credentials
Namespace:    default
Type:         Opaque

Data
====
DB_PASSWORD:  23 bytes
DB_USERNAME:  5 bytes
```

Notice that `kubectl describe` does not show the Secret values — it only shows their sizes. This is a safety feature to prevent accidental exposure in terminal output.

### Base64 Encoding

Kubernetes stores Secret values as **base64-encoded** strings. Base64 is not encryption — it is just an encoding format that converts any data (including binary data like TLS certificates) into a text-safe format.

**What is base64?** Think of base64 as writing a message in pig latin. It looks different, but anyone who knows the rules can read it. Base64 is not secure. It is just a way to represent binary data as text.

You can see the base64-encoded values:

```bash
kubectl get secret db-credentials -o yaml
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  DB_PASSWORD: c3VwZXJzZWNyZXRwYXNzd29yZDEyMw==
  DB_USERNAME: YWRtaW4=
```

You can decode these values easily:

```bash
echo "c3VwZXJzZWNyZXRwYXNzd29yZDEyMw==" | base64 --decode
```

```
supersecretpassword123
```

**Important:** Base64 encoding is NOT encryption. Anyone with access to the cluster can decode Secrets. This is a common source of confusion — see the section on "Why Secrets Are Not Truly Secret" below.

### Creating a Secret from YAML

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  DB_USERNAME: YWRtaW4=
  DB_PASSWORD: c3VwZXJzZWNyZXRwYXNzd29yZDEyMw==
```

The values under `data:` must be base64-encoded. To encode a value:

```bash
echo -n "admin" | base64
```

```
YWRtaW4=
```

The `-n` flag prevents echo from adding a newline character at the end. This is important — without `-n`, your encoded value will include a hidden newline, and your password will not match.

**Using `stringData` (easier):**

If you do not want to manually encode values, use `stringData` instead of `data`:

```yaml
# secret-plain.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
stringData:
  DB_USERNAME: admin
  DB_PASSWORD: supersecretpassword123
```

With `stringData`, you write plain text. Kubernetes encodes it for you automatically. This is more convenient but has a risk: if you store this YAML file in Git, the passwords are visible in plain text. Never commit Secret YAML files with `stringData` to version control.

### Using Secrets as Environment Variables

```yaml
# pod-with-secret-env.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-secrets
spec:
  containers:
    - name: myapp
      image: busybox
      command: ["sh", "-c", "echo Connected as $DB_USERNAME && sleep 3600"]
      envFrom:
        - secretRef:
            name: db-credentials
```

This works exactly like ConfigMap environment variables. All key-value pairs from the Secret become environment variables inside the container.

**Selective environment variables:**

```yaml
env:
  - name: DATABASE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-credentials
        key: DB_PASSWORD
```

### Mounting Secrets as Files

```yaml
# pod-with-secret-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-secret-files
spec:
  containers:
    - name: myapp
      image: busybox
      command: ["sh", "-c", "cat /etc/secrets/DB_PASSWORD && sleep 3600"]
      volumeMounts:
        - name: secret-volume
          mountPath: /etc/secrets
          readOnly: true
  volumes:
    - name: secret-volume
      secret:
        secretName: db-credentials
```

Each key becomes a file:

```
/etc/secrets/
├── DB_USERNAME    (contains "admin")
└── DB_PASSWORD    (contains "supersecretpassword123")
```

Notice the `readOnly: true` on the volume mount. This is a best practice for Secrets — it prevents the container from accidentally modifying the secret files.

### Why Secrets Are Not Truly Secret by Default

This is an important warning that trips up many beginners:

**Kubernetes Secrets are only base64-encoded, not encrypted.** By default:

1. Secrets are stored **unencrypted** in etcd (the cluster database).
2. Anyone with API access to the cluster can read Secrets.
3. Secrets are passed to Pods as plain text (after decoding).
4. Secrets can be seen in Pod environment variables via `kubectl exec`.

```
The Security Reality:

  ┌───────────────┐
  │   etcd        │
  │               │
  │  password:    │◄── Stored as base64 (NOT encrypted)
  │  YWJjMTIz    │    Anyone with cluster access can read it
  └───────┬───────┘
          │
          ▼
  ┌───────────────┐
  │   Pod         │
  │               │
  │  $DB_PASSWORD │◄── Available as plain text
  │  = abc123     │    Can be seen with kubectl exec
  └───────────────┘
```

**How to make Secrets more secure:**

1. **Enable encryption at rest** — Configure Kubernetes to encrypt Secrets in etcd.
2. **Use RBAC** — Restrict who can read Secrets using Role-Based Access Control.
3. **Use external secret managers** — Tools like HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault provide real encryption and access control. They integrate with Kubernetes through operators.
4. **Never commit Secrets to Git** — Use tools like Sealed Secrets or External Secrets Operator to safely manage Secrets in version control.

For learning purposes, Kubernetes Secrets are fine. But for production, take the extra steps to secure them properly.

---

## Persistent Volumes: Storage That Survives

### The Problem: Containers Are Ephemeral

By default, all data inside a container is lost when the container stops. This is the same behavior you learned about in the Docker chapters.

In Kubernetes, the problem is worse because Pods are constantly being created and destroyed — during scaling, updates, or self-healing. If your database is running in a Pod and the Pod restarts, all your data is gone.

```
Without Persistent Storage:

  Pod (running database)
  ┌───────────────────┐
  │  PostgreSQL       │
  │  ┌─────────────┐  │
  │  │  Data:      │  │
  │  │  users      │  │
  │  │  orders     │  │
  │  │  products   │  │
  │  └─────────────┘  │
  └───────────────────┘
          │
          ▼ Pod restarts
  ┌───────────────────┐
  │  PostgreSQL       │
  │  ┌─────────────┐  │
  │  │  Data:      │  │
  │  │  (empty!)   │  │
  │  │             │  │
  │  └─────────────┘  │
  └───────────────────┘
  All data is gone!
```

### The Solution: PersistentVolumes and PersistentVolumeClaims

Kubernetes solves this with two resources:

1. **PersistentVolume (PV)** — A piece of storage in the cluster. Think of it as a **hard drive** available for use. PVs are created by administrators or automatically by the storage system.

2. **PersistentVolumeClaim (PVC)** — A request for storage. Think of it as a **storage request form**. Your Pod says "I need 1 GB of storage," and Kubernetes finds a matching PV and assigns it.

### The Landlord Analogy

Think of storage like renting an apartment:

- The **PersistentVolume** is the apartment itself — it exists, has a certain size, and is available for rent.
- The **PersistentVolumeClaim** is your rental application — you specify how much space you need and what type of apartment you want.
- **Kubernetes** is the real estate agent — it matches your application (PVC) with an available apartment (PV).

```
Storage Flow:

  1. PV exists (storage is available)
  ┌───────────────────┐
  │  PersistentVolume  │
  │  Size: 5Gi         │
  │  Status: Available  │
  └───────────────────┘

  2. Pod creates a PVC (requests storage)
  ┌───────────────────┐
  │  PVC               │
  │  Request: 1Gi      │
  │  Status: Pending    │
  └───────────────────┘

  3. Kubernetes binds PVC to PV
  ┌───────────────────┐     ┌───────────────────┐
  │  PVC               │────►│  PV                │
  │  Request: 1Gi      │     │  Size: 5Gi         │
  │  Status: Bound     │     │  Status: Bound     │
  └───────────────────┘     └───────────────────┘

  4. Pod uses the PVC
  ┌─────────────────────────────────┐
  │  Pod                             │
  │  ┌───────────────┐              │
  │  │  Container    │              │
  │  │  /data ──────►│── PVC ──► PV │
  │  └───────────────┘              │
  └─────────────────────────────────┘

  Data survives Pod restarts!
```

### Dynamic Provisioning

In modern Kubernetes (including Minikube), you usually do not need to create PVs manually. Kubernetes can **dynamically provision** storage — when you create a PVC, Kubernetes automatically creates a matching PV. This is like an apartment building that constructs a new unit whenever someone submits a rental application.

Minikube comes with a default **StorageClass** that handles dynamic provisioning automatically. You only need to create a PVC.

### Creating a PersistentVolumeClaim

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Let us break this down:

| Line | Meaning |
|------|---------|
| `kind: PersistentVolumeClaim` | We are requesting storage. |
| `name: my-data-pvc` | The name of this storage claim. |
| `accessModes:` | How the storage can be accessed. |
| `ReadWriteOnce` | One node can read and write. This is the most common mode. |
| `resources: requests: storage: 1Gi` | We want 1 gigabyte of storage. |

**Access modes explained:**

| Mode | Abbreviation | Meaning |
|------|-------------|---------|
| ReadWriteOnce | RWO | Can be mounted as read-write by a single node |
| ReadOnlyMany | ROX | Can be mounted as read-only by multiple nodes |
| ReadWriteMany | RWX | Can be mounted as read-write by multiple nodes |

`ReadWriteOnce` is the most commonly used mode. It works with most storage types.

**Apply the PVC:**

```bash
kubectl apply -f pvc.yaml
```

```
persistentvolumeclaim/my-data-pvc created
```

**Check the PVC status:**

```bash
kubectl get pvc
```

```
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
my-data-pvc   Bound    pvc-a1b2c3d4-e5f6-7890-abcd-ef1234567890   1Gi        RWO            standard       10s
```

The status is `Bound`, which means Kubernetes created a PV and linked it to our PVC. The storage is ready to use.

### Mounting a PVC in a Pod

```yaml
# pod-with-pvc.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-storage
spec:
  containers:
    - name: myapp
      image: busybox
      command: ["sh", "-c", "echo 'Hello from persistent storage!' > /data/hello.txt && cat /data/hello.txt && sleep 3600"]
      volumeMounts:
        - name: data-volume
          mountPath: /data
  volumes:
    - name: data-volume
      persistentVolumeClaim:
        claimName: my-data-pvc
```

| Section | Meaning |
|---------|---------|
| `volumes:` | Define a volume for the Pod. |
| `persistentVolumeClaim: claimName: my-data-pvc` | This volume uses storage from our PVC. |
| `volumeMounts: mountPath: /data` | Mount the volume at `/data` inside the container. |

```bash
kubectl apply -f pod-with-pvc.yaml
```

```bash
kubectl logs app-with-storage
```

```
Hello from persistent storage!
```

Now delete the Pod and recreate it:

```bash
kubectl delete pod app-with-storage
kubectl apply -f pod-with-pvc.yaml
```

```bash
kubectl exec app-with-storage -- cat /data/hello.txt
```

```
Hello from persistent storage!
```

The data survived the Pod deletion! The PVC kept the storage alive, and when the new Pod mounted the same PVC, the data was still there.

```
Data Persistence:

  Pod v1 writes data ──► PVC ──► Disk
       │
       ▼ Pod deleted

  Pod v2 starts ──► PVC ──► Disk (data still there!)
       │
       ▼ reads data

  "Hello from persistent storage!"
```

---

## Complete Example: App with ConfigMap, Secret, and PVC

Let us build a complete example that ties everything together. We will create:

1. A ConfigMap for application settings
2. A Secret for the database password
3. A PVC for persistent data storage
4. A Pod that uses all three

### Step 1: ConfigMap for Application Settings

```yaml
# app-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: webapp-config
data:
  APP_NAME: "My Web App"
  APP_ENV: development
  LOG_LEVEL: debug
  DB_HOST: localhost
  DB_PORT: "5432"
  DB_NAME: webapp_db
```

```bash
kubectl apply -f app-configmap.yaml
```

```
configmap/webapp-config created
```

### Step 2: Secret for Database Password

```yaml
# app-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: webapp-secret
type: Opaque
stringData:
  DB_USERNAME: webapp_user
  DB_PASSWORD: MyS3cur3P@ssw0rd
```

```bash
kubectl apply -f app-secret.yaml
```

```
secret/webapp-secret created
```

### Step 3: PVC for Data Storage

```yaml
# app-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: webapp-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
```

```bash
kubectl apply -f app-pvc.yaml
```

```
persistentvolumeclaim/webapp-data created
```

### Step 4: Pod Using All Three

```yaml
# app-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: webapp
  labels:
    app: webapp
spec:
  containers:
    - name: webapp
      image: busybox
      command:
        - sh
        - -c
        - |
          echo "=== Application Configuration ==="
          echo "App: $APP_NAME"
          echo "Environment: $APP_ENV"
          echo "Log Level: $LOG_LEVEL"
          echo "Database: $DB_HOST:$DB_PORT/$DB_NAME"
          echo "DB User: $DB_USERNAME"
          echo "DB Pass: [hidden]"
          echo ""
          echo "=== Writing to persistent storage ==="
          echo "App started at $(date)" >> /data/app.log
          cat /data/app.log
          echo ""
          echo "=== Config file from volume ==="
          ls /etc/app-config/
          sleep 3600
      envFrom:
        - configMapRef:
            name: webapp-config
        - secretRef:
            name: webapp-secret
      volumeMounts:
        - name: data-volume
          mountPath: /data
        - name: config-volume
          mountPath: /etc/app-config
          readOnly: true
  volumes:
    - name: data-volume
      persistentVolumeClaim:
        claimName: webapp-data
    - name: config-volume
      configMap:
        name: webapp-config
```

```bash
kubectl apply -f app-pod.yaml
```

```bash
kubectl logs webapp
```

```
=== Application Configuration ===
App: My Web App
Environment: development
Log Level: debug
Database: localhost:5432/webapp_db
DB User: webapp_user
DB Pass: [hidden]

=== Writing to persistent storage ===
App started at Mon Jan 15 16:00:00 UTC 2024

=== Config file from volume ===
APP_ENV
APP_NAME
DB_HOST
DB_NAME
DB_PORT
LOG_LEVEL
```

Let us look at what this Pod uses:

```
Complete Application:

  ┌─────────────────────────────────────────┐
  │  Pod "webapp"                            │
  │  ┌───────────────────────────────────┐  │
  │  │  Container "webapp"               │  │
  │  │                                   │  │
  │  │  Environment Variables:           │  │
  │  │  ├── APP_NAME ◄── ConfigMap       │  │
  │  │  ├── LOG_LEVEL ◄── ConfigMap      │  │
  │  │  ├── DB_HOST ◄── ConfigMap        │  │
  │  │  ├── DB_USERNAME ◄── Secret       │  │
  │  │  └── DB_PASSWORD ◄── Secret       │  │
  │  │                                   │  │
  │  │  Volume Mounts:                   │  │
  │  │  ├── /data ◄── PVC (persistent)   │  │
  │  │  └── /etc/app-config ◄── ConfigMap│  │
  │  └───────────────────────────────────┘  │
  └─────────────────────────────────────────┘
```

Now delete the Pod and recreate it:

```bash
kubectl delete pod webapp
kubectl apply -f app-pod.yaml
```

```bash
kubectl logs webapp
```

```
=== Application Configuration ===
App: My Web App
Environment: development
...

=== Writing to persistent storage ===
App started at Mon Jan 15 16:00:00 UTC 2024
App started at Mon Jan 15 16:05:00 UTC 2024
...
```

Notice that the app.log now has two entries — the data from the first run survived! The ConfigMap and Secret values are also correctly injected.

### Clean Up

```bash
kubectl delete pod webapp
kubectl delete configmap webapp-config
kubectl delete secret webapp-secret
kubectl delete pvc webapp-data
```

---

## Common Mistakes

1. **Forgetting to quote numbers in ConfigMaps.** YAML treats `5432` as an integer, but ConfigMap values must be strings. Always write `"5432"` with quotes.

2. **Committing Secret YAML files to Git.** Never store Secret manifests with `stringData` (or decoded `data`) in version control. Use tools like Sealed Secrets or External Secrets Operator for production.

3. **Thinking Secrets are encrypted.** Secrets are base64-encoded, not encrypted. Anyone with cluster access can decode them. For real security, enable encryption at rest and use RBAC.

4. **Forgetting `-n` when encoding base64.** When creating base64 values manually, always use `echo -n "value" | base64`. Without `-n`, a newline character is included, which corrupts your Secret value.

5. **Deleting a PVC that is still in use.** If a Pod is using a PVC, deleting the PVC puts it in a "Terminating" state. It will not actually be deleted until all Pods stop using it. Delete the Pod first, then the PVC.

6. **Mounting a volume over an existing directory.** When you mount a volume at `/etc/config`, any existing files in that directory are hidden. Be careful not to overwrite important system directories.

7. **Using ReadWriteMany when you only need ReadWriteOnce.** Not all storage backends support ReadWriteMany. Use `ReadWriteOnce` unless you specifically need multiple nodes to write to the same volume.

---

## Best Practices

1. **Always use ConfigMaps for non-sensitive configuration.** Do not hardcode values in your Docker image. Make your images configurable through environment variables or config files.

2. **Use Secrets for all sensitive data.** Even if you think "it is just a development password," build the habit of using Secrets. It makes transitioning to production easier.

3. **Use `stringData` during development, `data` in production.** `stringData` is more convenient for writing YAML by hand. But in production, use a secret management tool that handles encoding.

4. **Always set `readOnly: true` on Secret volume mounts.** This prevents the container from accidentally modifying the secret files.

5. **Use meaningful names for PVCs.** Names like `postgres-data` or `uploads-storage` make it clear what the storage is for. Names like `pvc-1` do not.

6. **Always specify storage size in PVCs.** Even if dynamic provisioning adjusts the size, specifying a size documents your intent and helps with capacity planning.

---

## Quick Summary

ConfigMaps store non-sensitive configuration as key-value pairs and can be injected into Pods as environment variables or mounted as files. Secrets store sensitive data like passwords and API keys using base64 encoding (not encryption). PersistentVolumeClaims request storage from the cluster, and the claimed storage survives Pod restarts. Together, these three resources let you separate configuration, secrets, and data from your application code, following best practices for containerized applications.

---

## Key Points

- **ConfigMaps** store non-sensitive configuration data as key-value pairs
- ConfigMaps can be created from literals, files, or YAML manifests
- ConfigMaps can be injected as **environment variables** (`envFrom`) or mounted as **files** (volumes)
- **Secrets** store sensitive data (passwords, API keys, certificates)
- Secrets are **base64-encoded, not encrypted** — they are not truly secret by default
- Secrets can be injected as environment variables or mounted as files (with `readOnly: true`)
- Use `echo -n "value" | base64` to encode values (the `-n` prevents a trailing newline)
- **PersistentVolumeClaims (PVC)** request storage that survives Pod restarts
- `ReadWriteOnce` is the most common access mode for PVCs
- Minikube supports **dynamic provisioning** — PVs are created automatically when you create a PVC
- Never commit Secret YAML files with plain-text values to Git

---

## Practice Questions

1. What is the difference between a ConfigMap and a Secret? When would you use each one?

2. You create a Secret with `stringData: PASSWORD: abc123` and apply it. Then you run `kubectl get secret -o yaml`. Will you see `abc123` in the output? Why or why not?

3. Explain the relationship between a PersistentVolume and a PersistentVolumeClaim using a real-life analogy.

4. Your application stores uploaded files at `/uploads` inside the container. After every Pod restart, the files disappear. How would you fix this?

5. A colleague says "Our passwords are safe because we store them in Kubernetes Secrets." Is this statement accurate? What additional steps would you recommend?

---

## Exercises

### Exercise 1: ConfigMap Practice

1. Create a ConfigMap called `game-config` with these values:
   - `GAME_NAME: Space Invaders`
   - `MAX_PLAYERS: "4"`
   - `DIFFICULTY: medium`
2. Create a Pod that uses this ConfigMap as environment variables and prints all three values
3. Modify the ConfigMap to change `DIFFICULTY` to `hard`
4. Delete and recreate the Pod — does it pick up the new value?

### Exercise 2: Secret Handling

1. Encode the string `my-secret-password` in base64 using the command line
2. Create a Secret YAML file using the encoded value
3. Create a Pod that mounts the Secret as a file at `/etc/secrets/password`
4. Verify the file contents using `kubectl exec`
5. Delete the Secret and recreate it with `stringData` instead — verify the Pod still works the same way

### Exercise 3: Persistent Storage

1. Create a PVC requesting 200Mi of storage
2. Create a Pod that mounts this PVC at `/data`
3. Write a file to `/data/test.txt` using `kubectl exec`
4. Delete the Pod (not the PVC)
5. Create a new Pod mounting the same PVC
6. Verify that `/data/test.txt` still exists with the correct content

---

## What Is Next?

You now have all the building blocks: Deployments to manage Pods, Services to expose them, ConfigMaps for configuration, Secrets for sensitive data, and PersistentVolumes for storage.

In the next chapter, you will put everything together to deploy a real application — a Node.js API backed by PostgreSQL — to Kubernetes. You will create namespaces, ConfigMaps, Secrets, PVCs, Deployments, and Services, all working together as a complete system. This is the capstone of your Kubernetes journey.
