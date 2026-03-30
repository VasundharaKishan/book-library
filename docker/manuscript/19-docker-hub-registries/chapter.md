# Chapter 19: Docker Hub and Container Registries

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand what Docker Hub is and why it exists
- Create a Docker Hub account and log in from the terminal
- Tag images correctly for pushing to a registry
- Push your own images to Docker Hub
- Create and manage repositories on Docker Hub
- Set up automated builds from GitHub
- Work with private repositories
- Use alternative registries like GitHub Container Registry, AWS ECR, and Google GCR
- Run your own self-hosted registry

---

## Why This Chapter Matters

Up until now, every image you have built lives only on your computer. If your hard drive crashes, those images are gone. If a teammate needs your image, they cannot get it. If you want to deploy to a server, you have no way to transfer the image.

Container registries solve all of these problems. Think of a registry as an **app store for Docker images**. Just like you download apps from the App Store or Google Play, Docker pulls images from registries. And just like developers publish apps to those stores, you can publish your images to a registry.

Docker Hub is the default registry — the one Docker talks to when you run `docker pull nginx` without specifying a location. But it is not the only option. Understanding registries is essential because every production deployment starts with pushing an image to a registry and pulling it on the target server.

---

## What Is Docker Hub?

**Docker Hub** is a cloud-based registry service provided by Docker, Inc. It is the world's largest container image library and the default registry for Docker.

Think of it this way:

```
+--------------------------------------------------+
|              The App Store Analogy                |
|                                                   |
|   App Store / Google Play  =  Docker Hub          |
|   Apps                     =  Docker Images       |
|   App Developer            =  Image Publisher      |
|   Downloading an App       =  docker pull          |
|   Publishing an App        =  docker push          |
|   App Listing              =  Repository           |
+--------------------------------------------------+
```

When you run `docker pull nginx`, Docker contacts Docker Hub at `hub.docker.com`, finds the `nginx` repository, and downloads the image. You have been using Docker Hub all along without realizing it.

### Official Images vs User Images

Docker Hub hosts two types of images:

**Official images** have no username prefix. They are maintained by Docker or the software vendor:

```
nginx           <-- Official NGINX image
postgres        <-- Official PostgreSQL image
node            <-- Official Node.js image
python          <-- Official Python image
```

**User images** include a username or organization prefix:

```
myusername/webapp        <-- Your personal image
companyname/api-server   <-- An organization's image
bitnami/redis            <-- Bitnami's Redis image
```

The naming pattern is:

```
[registry-host/] [username/] image-name [:tag]

Examples:
  nginx:latest                              <-- Official, Docker Hub (default)
  myuser/webapp:v1.0                        <-- User image, Docker Hub
  ghcr.io/myuser/webapp:v1.0               <-- GitHub Container Registry
  123456789.dkr.ecr.us-east-1.amazonaws.com/webapp:v1.0  <-- AWS ECR
```

---

## Creating a Docker Hub Account

Before you can push images, you need a free Docker Hub account.

**Step 1:** Go to `https://hub.docker.com` and click "Sign Up."

**Step 2:** Choose a Docker ID (username). This becomes your namespace for all images. Choose carefully — it is hard to change later.

**Step 3:** Verify your email address.

Your Docker ID is important because every image you push will be prefixed with it:

```
your-docker-id/image-name:tag
```

---

## Logging In from the Terminal

To push images, you must authenticate with Docker Hub from your terminal.

### docker login

```bash
docker login
```

**Output:**

```
Login with your Docker ID to push and pull images from Docker Hub.
If you don't have a Docker ID, head over to https://hub.docker.com

Username: myusername
Password:
Login Succeeded
```

**Line-by-line explanation:**

- `docker login` — Tells Docker to authenticate with the default registry (Docker Hub)
- `Username:` — Enter the Docker ID you created during sign-up
- `Password:` — Enter your password (characters will not appear as you type — this is normal and a security feature)
- `Login Succeeded` — You are now authenticated and can push images

### Where Are Credentials Stored?

Docker stores your login credentials in a configuration file:

```bash
cat ~/.docker/config.json
```

**Output:**

```json
{
  "auths": {
    "https://index.docker.io/v1/": {
      "auth": "bXl1c2VybmFtZTpteXBhc3N3b3Jk"
    }
  }
}
```

> **Security Warning:** The `auth` field is your username and password encoded in Base64 — it is NOT encrypted. Anyone who can read this file can decode your credentials. On shared machines, use `docker login` only when needed and `docker logout` when finished.

### Using Access Tokens (Recommended)

Instead of your password, use a **Personal Access Token (PAT)**. Tokens are safer because:

- You can revoke a token without changing your password
- You can create tokens with limited permissions (read-only, read-write)
- You can create separate tokens for different machines or CI systems

**To create a token:**

1. Go to Docker Hub → Account Settings → Security → New Access Token
2. Give it a description (like "My Laptop" or "CI Server")
3. Choose the access level (Read, Read/Write, or Read/Write/Delete)
4. Copy the token immediately (you will not see it again)

**Use the token instead of your password:**

```bash
docker login -u myusername
```

When prompted for a password, paste the access token.

### Logging Out

```bash
docker logout
```

**Output:**

```
Removing login credentials for https://index.docker.io/v1/
```

This removes the stored credentials from `~/.docker/config.json`.

---

## Tagging Images for a Registry

Before you can push an image, it must be tagged with the correct name format. The tag tells Docker where to push the image.

### The Tagging Format

```
registry-host/username/image-name:tag
```

For Docker Hub, the registry host is optional (it is the default):

```
username/image-name:tag
```

### Using docker tag

The `docker tag` command creates a new name (tag) that points to an existing image. It does NOT create a copy — both names point to the same image data.

```bash
# First, build your image with any name
docker build -t my-webapp .

# Then tag it for Docker Hub
docker tag my-webapp myusername/my-webapp:v1.0
```

**Think of it like a file shortcut or alias.** The image data stays the same — you are just giving it an additional name that includes your Docker Hub username.

```
+-------------------------------------------+
|          Image Tagging Analogy             |
|                                            |
|   Original name:   my-webapp               |
|   Tagged name:     myusername/my-webapp:v1.0|
|                                            |
|   Both names point to the SAME image.      |
|   Like two shortcuts to the same file.     |
+-------------------------------------------+
```

### Verify the Tag

```bash
docker images
```

**Output:**

```
REPOSITORY               TAG       IMAGE ID       CREATED          SIZE
my-webapp                latest    a1b2c3d4e5f6   5 minutes ago    150MB
myusername/my-webapp      v1.0      a1b2c3d4e5f6   5 minutes ago    150MB
```

Notice that both entries have the **same IMAGE ID**. They are the same image with two different names.

### Tag During Build

You can skip the separate tagging step by using the correct name during the build:

```bash
docker build -t myusername/my-webapp:v1.0 .
```

This builds the image and immediately gives it the registry-ready name.

---

## Pushing Images to Docker Hub

Once your image is tagged correctly, pushing is straightforward.

### docker push

```bash
docker push myusername/my-webapp:v1.0
```

**Output:**

```
The push refers to repository [docker.io/myusername/my-webapp]
5f70bf18a086: Pushed
a3ed95caeb02: Pushed
e3b0c44298fc: Mounted from library/node
v1.0: digest: sha256:abc123def456... size: 1572
```

**Line-by-line explanation:**

- `The push refers to repository` — Confirms where the image is being sent
- `Pushed` — This layer was uploaded to Docker Hub
- `Mounted from library/node` — This layer already exists on Docker Hub (from the base image). Docker does not re-upload it — saving time and bandwidth
- `v1.0: digest: sha256:...` — A unique fingerprint for this exact image version

```
+-------------------------------------------------------+
|              Push Flow                                 |
|                                                        |
|   Your Computer              Docker Hub                |
|   +-------------+           +------------------+       |
|   | my-webapp   |  push --> | myusername/      |       |
|   | v1.0        |           | my-webapp:v1.0   |       |
|   +-------------+           +------------------+       |
|                                                        |
|   Only NEW layers are uploaded.                        |
|   Layers from base images are shared (mounted).        |
+-------------------------------------------------------+
```

### Pushing Multiple Tags

You can push multiple tags for the same image:

```bash
docker tag my-webapp myusername/my-webapp:v1.0
docker tag my-webapp myusername/my-webapp:latest

docker push myusername/my-webapp:v1.0
docker push myusername/my-webapp:latest
```

Or push all tags at once:

```bash
docker push myusername/my-webapp --all-tags
```

---

## Understanding Repositories

A **repository** on Docker Hub is a collection of related images, identified by different tags. Think of it as a folder that holds all versions of one application.

```
+------------------------------------------+
|   Repository: myusername/my-webapp        |
|                                           |
|   Tags (versions):                        |
|     v1.0    - First release               |
|     v1.1    - Bug fix                     |
|     v2.0    - Major update                |
|     latest  - Most recent                 |
|                                           |
|   All these are in ONE repository.        |
+------------------------------------------+
```

### Creating a Repository on Docker Hub

Repositories are created automatically when you push an image. But you can also create them manually through the web interface:

1. Go to Docker Hub → Repositories → Create Repository
2. Enter a name (like `my-webapp`)
3. Add a description
4. Choose visibility: **Public** (anyone can pull) or **Private** (only you)
5. Click Create

### Repository Settings

Each repository has settings you can configure:

- **Description** — What this image does
- **README** — Detailed documentation (supports Markdown)
- **Collaborators** — Other users who can push to this repository
- **Webhooks** — Trigger actions when a new image is pushed
- **Build settings** — Configure automated builds from source code

---

## Automated Builds

**Automated builds** link a Docker Hub repository to a source code repository on GitHub or Bitbucket. Whenever you push code changes, Docker Hub automatically builds a new image.

```
+----------------------------------------------------------+
|              Automated Build Flow                         |
|                                                           |
|   GitHub Repo          Docker Hub                         |
|   +-----------+        +------------------+               |
|   | Push code | -----> | Detect change    |               |
|   | to main   |        | Build image      |               |
|   +-----------+        | Push to registry |               |
|                        +------------------+               |
|                                                           |
|   You push code. Docker Hub builds the image for you.     |
+----------------------------------------------------------+
```

### Setting Up Automated Builds

1. Go to Docker Hub → Your Repository → Builds
2. Link your GitHub or Bitbucket account
3. Select the source repository
4. Configure build rules:
   - **Source branch:** `main` → **Docker tag:** `latest`
   - **Source branch:** `/^v[0-9.]+$/` → **Docker tag:** `{sourceref}`
5. Enable "Build on push"

### Build Rules Example

| Source Type | Source    | Docker Tag | Dockerfile Location |
|-------------|----------|------------|---------------------|
| Branch      | main     | latest     | /Dockerfile         |
| Tag         | /^v.*$/  | {sourceref}| /Dockerfile         |
| Branch      | develop  | dev        | /Dockerfile         |

**What this means:**

- Pushing to the `main` branch builds an image tagged `latest`
- Creating a Git tag like `v1.2.3` builds an image tagged `v1.2.3`
- Pushing to `develop` builds an image tagged `dev`

> **Note:** Docker Hub's free automated builds have been limited. Many teams now use GitHub Actions or other CI systems to build and push images instead. We cover this approach in Chapter 21.

---

## Private Repositories

By default, Docker Hub repositories are **public** — anyone can pull your images. For proprietary applications, you need **private** repositories.

### Free Tier Limitations

Docker Hub's free tier includes:

- Unlimited public repositories
- One private repository (this may change — check Docker Hub for current limits)

Paid plans offer more private repositories and additional features like team management and vulnerability scanning.

### Creating a Private Repository

When creating a repository, select **Private** for visibility:

```bash
# This will push to a private repo (if configured on Docker Hub)
docker push myusername/my-secret-app:v1.0
```

### Pulling from a Private Repository

Anyone pulling a private image must be logged in and have access:

```bash
# Must be logged in first
docker login

# Now you can pull
docker pull myusername/my-secret-app:v1.0
```

Without logging in, you get an error:

```
Error response from daemon: pull access denied for myusername/my-secret-app,
repository does not exist or may require 'docker login'
```

---

## Alternative Registries

Docker Hub is not the only registry. Here are the most popular alternatives and when to use each.

### GitHub Container Registry (GHCR)

**GitHub Container Registry** stores images alongside your source code on GitHub. It integrates naturally with GitHub Actions for CI/CD.

```
Registry URL: ghcr.io
Image format: ghcr.io/username/image-name:tag
```

**Login:**

```bash
# Create a Personal Access Token on GitHub with "write:packages" scope
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

**Tag and push:**

```bash
docker tag my-webapp ghcr.io/myusername/my-webapp:v1.0
docker push ghcr.io/myusername/my-webapp:v1.0
```

**Why choose GHCR:**

- Your code and images live in the same place
- GitHub Actions can push images without extra credentials
- Free for public repositories
- Generous free tier for private repositories

### AWS Elastic Container Registry (ECR)

**AWS ECR** is Amazon's fully managed registry. It integrates with other AWS services like ECS, EKS, and Lambda.

```
Registry URL: <account-id>.dkr.ecr.<region>.amazonaws.com
Image format: 123456789.dkr.ecr.us-east-1.amazonaws.com/my-webapp:v1.0
```

**Login (requires AWS CLI):**

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS \
  --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
```

**Create a repository first (ECR requires this):**

```bash
aws ecr create-repository --repository-name my-webapp --region us-east-1
```

**Tag and push:**

```bash
docker tag my-webapp 123456789.dkr.ecr.us-east-1.amazonaws.com/my-webapp:v1.0
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-webapp:v1.0
```

**Why choose AWS ECR:**

- You deploy to AWS services (ECS, EKS, Fargate)
- You need fine-grained IAM permissions
- You want images stored close to your AWS infrastructure

### Google Container Registry (GCR) / Artifact Registry

**Google Artifact Registry** (successor to GCR) stores images for Google Cloud deployments.

```
Registry URL: us-docker.pkg.dev (Artifact Registry)
              gcr.io (legacy GCR)
Image format: us-docker.pkg.dev/project-id/repo-name/image-name:tag
```

**Login:**

```bash
gcloud auth configure-docker us-docker.pkg.dev
```

**Tag and push:**

```bash
docker tag my-webapp us-docker.pkg.dev/my-project/my-repo/my-webapp:v1.0
docker push us-docker.pkg.dev/my-project/my-repo/my-webapp:v1.0
```

**Why choose Artifact Registry:**

- You deploy to Google Cloud (GKE, Cloud Run)
- You need vulnerability scanning integrated with Google Cloud
- You want multi-format support (Docker, npm, Maven, etc.)

### Comparison Table

| Feature            | Docker Hub | GHCR     | AWS ECR   | Google AR  |
|--------------------|-----------|----------|-----------|------------|
| Free public repos  | Yes       | Yes      | No        | No         |
| Free private repos | Limited   | Yes      | No        | No         |
| CI/CD integration  | Limited   | GitHub   | AWS       | Google     |
| Vulnerability scan | Paid      | Free     | Free      | Free       |
| Custom domains     | No        | No       | Yes       | Yes        |
| Best for           | Open source| GitHub projects | AWS deploys | GCP deploys |

---

## Running a Self-Hosted Registry

Sometimes you need a registry that runs on your own servers. Reasons include:

- **Air-gapped environments** — No internet access
- **Compliance** — Data must stay in your network
- **Speed** — Local registry for faster pulls in your data center
- **Cost** — No per-image charges

### Starting a Local Registry

Docker provides an official registry image. Setting up a basic registry takes one command:

```bash
docker run -d \
  --name my-registry \
  -p 5000:5000 \
  --restart always \
  registry:2
```

**Line-by-line explanation:**

- `docker run -d` — Run in detached mode (background)
- `--name my-registry` — Give it a readable name
- `-p 5000:5000` — Map port 5000 on your machine to port 5000 in the container
- `--restart always` — Automatically restart if it crashes or if Docker restarts
- `registry:2` — Use version 2 of the official Docker registry image

### Using the Local Registry

```bash
# Tag an image for the local registry
docker tag my-webapp localhost:5000/my-webapp:v1.0

# Push to the local registry
docker push localhost:5000/my-webapp:v1.0

# Pull from the local registry
docker pull localhost:5000/my-webapp:v1.0
```

### Adding Persistent Storage

Without a volume, pushed images are lost when the container stops:

```bash
docker run -d \
  --name my-registry \
  -p 5000:5000 \
  --restart always \
  -v registry-data:/var/lib/registry \
  registry:2
```

The `-v registry-data:/var/lib/registry` flag stores image data in a named volume that survives container restarts.

### Checking What Is in the Registry

```bash
# List all repositories
curl http://localhost:5000/v2/_catalog
```

**Output:**

```json
{"repositories":["my-webapp"]}
```

```bash
# List tags for a repository
curl http://localhost:5000/v2/my-webapp/tags/list
```

**Output:**

```json
{"name":"my-webapp","tags":["v1.0"]}
```

```
+-----------------------------------------------------+
|           Self-Hosted Registry Architecture           |
|                                                       |
|   Developer Machine        Your Server                |
|   +----------------+      +------------------+        |
|   | docker push    | ---> | Registry:2       |        |
|   | localhost:5000 |      | Port 5000        |        |
|   +----------------+      | Volume: data     |        |
|                            +------------------+        |
|                                  |                     |
|   Production Server              |                     |
|   +----------------+             |                     |
|   | docker pull    | <-----------+                     |
|   | server:5000    |                                   |
|   +----------------+                                   |
+-----------------------------------------------------+
```

> **Security Warning:** A local registry on `localhost:5000` works without HTTPS. If you expose the registry to a network, you MUST configure TLS (HTTPS) and authentication. Without them, anyone on your network can push and pull images.

---

## Common Mistakes

### Mistake 1: Forgetting to Log In Before Pushing

```bash
docker push myusername/my-webapp:v1.0
```

**Error:**

```
denied: requested access to the resource is denied
```

**Fix:** Run `docker login` first and enter your credentials.

### Mistake 2: Pushing Without the Correct Tag Format

```bash
# This will NOT work — no username prefix
docker push my-webapp:v1.0
```

**Error:**

```
An image does not exist locally with the tag: my-webapp
```

**Fix:** Tag the image with your username first:

```bash
docker tag my-webapp myusername/my-webapp:v1.0
docker push myusername/my-webapp:v1.0
```

### Mistake 3: Using the Wrong Registry URL

```bash
# Trying to push to GHCR without the correct prefix
docker push myusername/my-webapp:v1.0  # Goes to Docker Hub, not GHCR
```

**Fix:** Include the full registry URL:

```bash
docker push ghcr.io/myusername/my-webapp:v1.0  # Goes to GHCR
```

### Mistake 4: Leaving Credentials on Shared Machines

After using `docker login` on a shared server, your credentials remain in `~/.docker/config.json`. Anyone with access to that file can use your account.

**Fix:** Always run `docker logout` when finished on shared machines.

### Mistake 5: Pushing Sensitive Data in Image Layers

If your Dockerfile copies `.env` files or secrets into the image, those secrets are visible to anyone who pulls the image — even if you delete them in a later layer.

**Fix:** Use `.dockerignore` to exclude sensitive files, and use Docker secrets or environment variables for configuration.

---

## Best Practices

1. **Use access tokens instead of passwords** — Tokens can be revoked individually and scoped to specific permissions
2. **Always log out on shared machines** — Protect your credentials with `docker logout`
3. **Tag images with specific versions** — Avoid relying solely on `latest` (more on this in Chapter 20)
4. **Use private repositories for proprietary code** — Never publish internal applications to public repositories
5. **Add a README to your Docker Hub repositories** — Help users understand what your image does and how to use it
6. **Set up webhooks** — Notify your deployment pipeline when new images are pushed
7. **Choose the registry closest to your infrastructure** — AWS ECR for AWS deployments, GHCR for GitHub projects, and so on
8. **Scan images for vulnerabilities** — Enable scanning on your registry (covered in Chapter 22)
9. **Use `.dockerignore`** — Prevent sensitive files from being included in images

---

## Quick Summary

Docker Hub is the default registry for Docker images, acting like an app store where you can publish and download container images. You log in with `docker login`, tag images with your username prefix, and push with `docker push`. Repositories hold multiple tagged versions of an image. For private or proprietary images, use private repositories. Alternative registries like GitHub Container Registry, AWS ECR, and Google Artifact Registry integrate with their respective platforms. For air-gapped or compliance scenarios, you can run a self-hosted registry with the official `registry:2` image.

---

## Key Points

- **Docker Hub** is the default registry — `docker pull nginx` talks to Docker Hub automatically
- **docker login** authenticates you with a registry
- **docker tag** creates a new name for an image — it does not copy the image
- **docker push** uploads an image to a registry, sending only new layers
- **Repositories** group multiple tagged versions of one image
- **Private repositories** require authentication to pull
- **GHCR, AWS ECR, and Google Artifact Registry** are popular alternatives, each integrated with their cloud platform
- **Self-hosted registries** run on your own servers using the `registry:2` image
- **Access tokens** are safer than passwords for authentication
- Never store **sensitive data** in image layers

---

## Practice Questions

1. What command do you use to authenticate with Docker Hub from the terminal? What is a safer alternative to using your password?

2. If your Docker Hub username is `devjane` and you have an image called `api-server`, what is the correct tag format to push it to Docker Hub with version `2.1.0`?

3. You run `docker push myapp:v1.0` and get a "denied" error. What are two possible reasons for this error?

4. What is the difference between a public and private repository on Docker Hub? How does a private repository affect `docker pull`?

5. You need to store Docker images inside your company network with no internet access. What solution would you use?

---

## Exercises

### Exercise 1: Push Your First Image

1. Create a Docker Hub account if you do not have one
2. Log in from the terminal using `docker login`
3. Build a simple image (use any Dockerfile from a previous chapter)
4. Tag it with your Docker Hub username and version `v1.0`
5. Push it to Docker Hub
6. Verify it appears on your Docker Hub profile page
7. Log out with `docker logout`
8. Pull the image to confirm it works: `docker pull yourusername/image:v1.0`

### Exercise 2: Set Up a Local Registry

1. Start a local registry using `docker run -d -p 5000:5000 registry:2`
2. Tag an existing image for the local registry: `docker tag nginx localhost:5000/my-nginx:v1.0`
3. Push the image to your local registry
4. Delete the local image: `docker rmi localhost:5000/my-nginx:v1.0`
5. Pull it back from the local registry
6. Use `curl` to list the repositories in your local registry

### Exercise 3: Explore Alternative Registries

1. Create a GitHub Personal Access Token with `write:packages` scope
2. Log in to GitHub Container Registry using the token
3. Tag an image for GHCR and push it
4. Verify the image appears in your GitHub profile under "Packages"
5. Compare the experience with pushing to Docker Hub

---

## What Is Next?

You now know how to share images through registries. But we glossed over an important detail: how to choose the right tags for your images. In the next chapter, we dive deep into **image tagging strategies** — why `latest` can be dangerous, how semantic versioning works for Docker images, and how teams organize their tags for reliable deployments.
