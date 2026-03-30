# Chapter 21: CI/CD with Docker

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand what CI/CD is and why it matters
- Set up a GitHub Actions workflow that builds Docker images
- Push images to Docker Hub and GitHub Container Registry automatically
- Use caching to speed up Docker builds in CI
- Build multi-platform images for amd64 and arm64 architectures
- Deploy different images to different environments (staging, production)
- Write a complete `.github/workflows/docker.yml` from scratch

---

## Why This Chapter Matters

Up until now, you have been building and pushing Docker images by hand. You run `docker build`, then `docker tag`, then `docker push`. This works for learning, but it falls apart in a real team:

- Someone forgets to build before pushing
- Someone pushes an image without running tests
- Someone tags the image incorrectly
- Someone pushes from their laptop with uncommitted changes

**CI/CD eliminates all of these problems.** It automates the entire process: every time you push code, a server builds the image, runs tests, tags it correctly, and pushes it to a registry. No manual steps. No human errors.

Think of CI/CD as an **assembly line in a factory**:

```
+-----------------------------------------------------------+
|              The Assembly Line Analogy                      |
|                                                            |
|   Raw Materials (code)                                     |
|        |                                                   |
|        v                                                   |
|   [Station 1: Build]        "Assemble the product"         |
|        |                     docker build                   |
|        v                                                   |
|   [Station 2: Test]         "Quality check"                |
|        |                     run tests                      |
|        v                                                   |
|   [Station 3: Package]      "Label and box it"             |
|        |                     docker tag                     |
|        v                                                   |
|   [Station 4: Ship]         "Send to warehouse"            |
|        |                     docker push                    |
|        v                                                   |
|   Registry (warehouse)                                     |
|        |                                                   |
|        v                                                   |
|   Servers pull and deploy                                  |
+-----------------------------------------------------------+
```

You write code and push it to GitHub. The assembly line does everything else.

---

## What Is CI/CD?

**CI** stands for **Continuous Integration**. It means automatically building and testing your code every time someone pushes a change. The word "continuous" means it happens on every push — not once a week or once a month.

**CD** stands for **Continuous Delivery** (or **Continuous Deployment**). It means automatically delivering your tested code to a registry or server.

- **Continuous Delivery** = Automatically prepare a release (build, test, push image). A human clicks a button to deploy.
- **Continuous Deployment** = Automatically deploy to production. No human in the loop.

```
+-----------------------------------------------------------+
|                CI/CD Pipeline                              |
|                                                            |
|   Developer pushes code                                    |
|        |                                                   |
|        v                                                   |
|   +------------------+                                     |
|   | Continuous       |  Build code                         |
|   | Integration (CI) |  Run tests                          |
|   |                  |  Build Docker image                 |
|   +------------------+                                     |
|        |                                                   |
|        v  (tests pass)                                     |
|   +------------------+                                     |
|   | Continuous       |  Tag image                          |
|   | Delivery (CD)    |  Push to registry                   |
|   |                  |  Deploy to staging/production        |
|   +------------------+                                     |
|        |                                                   |
|        v                                                   |
|   Application is live                                      |
+-----------------------------------------------------------+
```

### Popular CI/CD Tools

| Tool            | Where It Runs  | Best For                    |
|-----------------|----------------|-----------------------------|
| GitHub Actions  | GitHub.com     | Projects hosted on GitHub    |
| GitLab CI       | GitLab.com     | Projects hosted on GitLab    |
| Jenkins         | Self-hosted    | Full control, complex pipelines |
| CircleCI        | Cloud          | Fast builds, easy setup      |
| Travis CI       | Cloud          | Open source projects         |

This chapter uses **GitHub Actions** because it is free for public repositories, requires no extra accounts, and integrates directly with GitHub.

---

## GitHub Actions Basics

GitHub Actions is GitHub's built-in CI/CD system. You define **workflows** in YAML files inside the `.github/workflows/` directory of your repository.

### Key Concepts

```
+-----------------------------------------------------------+
|              GitHub Actions Terminology                    |
|                                                            |
|   Workflow:   A YAML file that defines an automation       |
|               (.github/workflows/docker.yml)               |
|                                                            |
|   Event:      What triggers the workflow                   |
|               (push, pull request, schedule, manual)       |
|                                                            |
|   Job:        A set of steps that run on the same machine  |
|               (build, test, deploy)                        |
|                                                            |
|   Step:       A single task within a job                   |
|               (checkout code, build image, push image)     |
|                                                            |
|   Runner:     The machine that executes the job            |
|               (ubuntu-latest, windows-latest, macos-latest)|
|                                                            |
|   Action:     A reusable step created by the community     |
|               (docker/build-push-action, actions/checkout) |
+-----------------------------------------------------------+
```

### Your First Workflow

Create this file in your repository:

```yaml
# .github/workflows/docker.yml
name: Build Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t myapp:test .

      - name: Run tests
        run: docker run --rm myapp:test npm test
```

**Line-by-line explanation:**

- `name: Build Docker Image` — A human-readable name shown in the GitHub Actions UI
- `on: push: branches: [main]` — Run this workflow when code is pushed to the `main` branch
- `jobs: build:` — Define a job called "build"
- `runs-on: ubuntu-latest` — Run on a fresh Ubuntu virtual machine
- `uses: actions/checkout@v4` — Clone your repository onto the runner
- `run: docker build -t myapp:test .` — Build the Docker image
- `run: docker run --rm myapp:test npm test` — Start a container and run tests

This workflow runs on every push to `main`. If the build or tests fail, GitHub shows a red X on the commit. If everything passes, you get a green checkmark.

---

## Building and Pushing to Docker Hub

Let us extend the workflow to push images to Docker Hub.

### Step 1: Add Docker Hub Credentials as Secrets

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add `DOCKERHUB_USERNAME` with your Docker Hub username
4. Add `DOCKERHUB_TOKEN` with your Docker Hub access token (not your password)

**Why secrets?** Secrets are encrypted and never shown in logs. Hardcoding credentials in a YAML file would expose them to anyone who can read your repository.

### Step 2: The Workflow

```yaml
# .github/workflows/docker.yml
name: Build and Push to Docker Hub

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  IMAGE_NAME: myusername/myapp

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      # Step 1: Get the code
      - name: Checkout code
        uses: actions/checkout@v4

      # Step 2: Set up Docker Buildx (needed for advanced features)
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # Step 3: Log in to Docker Hub
      - name: Log in to Docker Hub
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # Step 4: Generate tags and labels
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            type=raw,value=latest,enable={{is_default_branch}}

      # Step 5: Build and push
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

**What each step does:**

1. **Checkout** — Clones your code onto the runner
2. **Setup Buildx** — Enables advanced Docker build features (caching, multi-platform builds)
3. **Login** — Authenticates with Docker Hub. The `if` condition skips login on pull requests (because PRs should not push images)
4. **Metadata** — Automatically generates tags based on the Git context (branch, tag, SHA)
5. **Build and push** — Builds the image and pushes it. On pull requests, it only builds (no push) to verify the build works

### What Tags Are Generated?

| Git Event               | Tags Generated                          |
|-------------------------|----------------------------------------|
| Push to `main`          | `main`, `latest`, `a1b2c3d`            |
| Git tag `v1.2.3`        | `1.2.3`, `1.2`, `1`, `a1b2c3d`         |
| Pull request            | No push (build only)                   |

---

## Building and Pushing to GitHub Container Registry

If you prefer keeping images next to your code on GitHub, push to GHCR instead.

```yaml
# .github/workflows/docker-ghcr.yml
name: Build and Push to GHCR

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

**Key differences from Docker Hub:**

- `registry: ghcr.io` — Points to GitHub Container Registry
- `username: ${{ github.actor }}` — Uses the GitHub username of whoever triggered the workflow
- `password: ${{ secrets.GITHUB_TOKEN }}` — Automatically provided by GitHub Actions (no manual secret needed)
- `permissions: packages: write` — Grants permission to push to GHCR

---

## Caching Docker Builds

Docker builds in CI can be slow because the runner starts fresh every time — there is no layer cache from previous builds. Caching fixes this.

### Why Caching Matters

```
+-----------------------------------------------------------+
|              Without Caching                               |
|                                                            |
|   Build 1: Install dependencies    (2 minutes)             |
|   Build 2: Install dependencies    (2 minutes) <-- again!  |
|   Build 3: Install dependencies    (2 minutes) <-- again!  |
|                                                            |
|              With Caching                                  |
|                                                            |
|   Build 1: Install dependencies    (2 minutes)             |
|   Build 2: Use cached layer        (5 seconds)  <-- fast!  |
|   Build 3: Use cached layer        (5 seconds)  <-- fast!  |
+-----------------------------------------------------------+
```

### GitHub Actions Cache

The `docker/build-push-action` supports caching through GitHub's cache storage:

```yaml
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**What this does:**

- `cache-from: type=gha` — Pull cached layers from GitHub Actions cache
- `cache-to: type=gha,mode=max` — Push all layers to the cache after building
- `mode=max` — Cache ALL layers, not just the final image layers. This maximizes cache hits for multi-stage builds

### Registry-Based Cache

Alternatively, store the cache in the registry itself:

```yaml
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=registry,ref=${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.IMAGE_NAME }}:buildcache,mode=max
```

This stores a special cache image in your registry alongside your regular images.

---

## Multi-Platform Builds

Modern applications need to run on different CPU architectures. The most common are:

- **amd64** (also called x86_64) — Standard Intel/AMD processors (most servers, PCs)
- **arm64** (also called aarch64) — ARM processors (Apple Silicon Macs, AWS Graviton, Raspberry Pi)

### Why Multi-Platform Matters

```
+-----------------------------------------------------------+
|              The Architecture Problem                      |
|                                                            |
|   You build on your Mac (Apple Silicon = arm64)            |
|   You deploy to a server (Intel = amd64)                   |
|                                                            |
|   Without multi-platform:                                  |
|     Your image only works on arm64.                        |
|     The server cannot run it.                              |
|                                                            |
|   With multi-platform:                                     |
|     Docker automatically picks the right version           |
|     for each architecture.                                 |
+-----------------------------------------------------------+
```

### Multi-Platform Workflow

```yaml
      # Required for multi-platform builds
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push multi-platform
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          platforms: linux/amd64,linux/arm64
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**What the new parts do:**

- `docker/setup-qemu-action` — Installs QEMU, which lets the amd64 runner emulate arm64 (and vice versa). QEMU stands for "Quick Emulator."
- `platforms: linux/amd64,linux/arm64` — Build the image for both architectures

When someone runs `docker pull myapp:1.0.0` on an Intel server, Docker automatically downloads the amd64 version. On an Apple Silicon Mac, it downloads the arm64 version. This happens transparently — the user does not need to know.

> **Note:** Multi-platform builds are slower because the runner must emulate the non-native architecture. The arm64 build on an amd64 runner can take 2-5 times longer than a native build.

---

## Environment-Specific Deployments

In real projects, you deploy to multiple environments:

```
+-----------------------------------------------------------+
|              Environment Pipeline                          |
|                                                            |
|   Push to main branch                                      |
|        |                                                   |
|        v                                                   |
|   Build image -> Push to registry                          |
|        |                                                   |
|        v                                                   |
|   Deploy to STAGING (automatic)                            |
|        |                                                   |
|        v                                                   |
|   Manual approval                                          |
|        |                                                   |
|        v                                                   |
|   Deploy to PRODUCTION (after approval)                    |
+-----------------------------------------------------------+
```

### Workflow with Staging and Production

```yaml
# .github/workflows/deploy.yml
name: Build, Push, and Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  IMAGE_NAME: myusername/myapp

jobs:
  # Job 1: Build and push the image
  build:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.version }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=semver,pattern={{version}}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Job 2: Deploy to staging (automatic)
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying ${{ env.IMAGE_NAME }}:${{ needs.build.outputs.image-tag }} to staging"
          # Replace with your actual deployment command:
          # ssh staging-server "docker pull $IMAGE && docker compose up -d"

  # Job 3: Deploy to production (requires manual approval)
  deploy-production:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    environment: production
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Deploy to production
        run: |
          echo "Deploying ${{ env.IMAGE_NAME }}:${{ needs.build.outputs.image-tag }} to production"
          # Replace with your actual deployment command
```

**Key concepts:**

- `needs: build` — The staging job waits for the build job to finish
- `needs: [build, deploy-staging]` — Production waits for both build AND staging
- `environment: production` — You can configure this environment in GitHub to require manual approval
- `if: startsWith(github.ref, 'refs/tags/v')` — Only deploy to production when a version tag is created

### Setting Up Environment Protection

1. Go to GitHub → Repository Settings → Environments
2. Create environments: `staging` and `production`
3. For `production`, enable "Required reviewers" and add your team lead
4. Now, when the pipeline reaches the production step, it pauses and waits for approval

---

## Complete Workflow File

Here is a production-ready workflow that combines everything from this chapter:

```yaml
# .github/workflows/docker.yml
#
# This workflow:
# - Builds a Docker image on every push and PR
# - Runs tests inside the container
# - Pushes to Docker Hub (on main branch and tags only)
# - Builds for both amd64 and arm64
# - Uses caching for faster builds
# - Generates proper semantic version tags

name: Docker CI/CD

on:
  push:
    branches: [main]
    tags: ['v*.*.*']
  pull_request:
    branches: [main]

env:
  IMAGE_NAME: myusername/myapp
  # Set to 'true' to enable multi-platform builds (slower but necessary)
  MULTI_PLATFORM: 'false'

jobs:
  # -------------------------------------------
  # Job 1: Lint and test (fast feedback)
  # -------------------------------------------
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build test image
        run: docker build --target test -t myapp:test . 2>/dev/null || docker build -t myapp:test .

      - name: Run tests
        run: docker run --rm myapp:test npm test 2>/dev/null || echo "No test command found, skipping"

  # -------------------------------------------
  # Job 2: Build and push Docker image
  # -------------------------------------------
  build-and-push:
    runs-on: ubuntu-latest
    needs: test
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Set up QEMU for multi-platform builds
      - name: Set up QEMU
        if: env.MULTI_PLATFORM == 'true'
        uses: docker/setup-qemu-action@v3

      # Set up Buildx for advanced build features
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # Log in to Docker Hub (skip on PRs)
      - name: Log in to Docker Hub
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # Log in to GHCR (skip on PRs)
      - name: Log in to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # Generate tags based on Git context
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: |
            ${{ env.IMAGE_NAME }}
            ghcr.io/${{ github.repository }}
          tags: |
            # Git short SHA
            type=sha,prefix=
            # Branch name
            type=ref,event=branch
            # PR number
            type=ref,event=pr
            # Semantic version tags (from Git tags like v1.2.3)
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            # Latest tag for default branch
            type=raw,value=latest,enable={{is_default_branch}}

      # Build and push the image
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          # Only push on main branch and tags, not on PRs
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          # Multi-platform: uncomment if needed
          platforms: ${{ env.MULTI_PLATFORM == 'true' && 'linux/amd64,linux/arm64' || 'linux/amd64' }}
          # Cache layers in GitHub Actions cache
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # Show what was built
      - name: Image digest
        run: echo "Image digest - ${{ steps.meta.outputs.tags }}"
```

**How to use this workflow:**

1. Copy the file to `.github/workflows/docker.yml` in your repository
2. Replace `myusername/myapp` with your Docker Hub username and image name
3. Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` as repository secrets
4. Push to `main` to trigger the workflow
5. Create a Git tag (`git tag v1.0.0 && git push --tags`) to trigger a release build

---

## Common Mistakes

### Mistake 1: Hardcoding Credentials in the Workflow

```yaml
# NEVER DO THIS
- name: Log in
  run: docker login -u myuser -p SuperSecret123
```

Anyone who can read your repository can see these credentials.

**Fix:** Use GitHub Secrets:

```yaml
- uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### Mistake 2: Pushing Images from Pull Requests

Pull requests can come from anyone, including external contributors. Pushing images from PRs could let attackers publish malicious images to your registry.

**Fix:** Only push from trusted branches:

```yaml
push: ${{ github.event_name != 'pull_request' }}
```

### Mistake 3: Not Using Build Caching

Without caching, every CI build downloads all dependencies from scratch. This wastes time and money.

**Fix:** Add caching:

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

### Mistake 4: Building Only for Your Architecture

You build on an amd64 CI runner, but your team uses Apple Silicon Macs. They pull the image and get an error about architecture mismatch.

**Fix:** Enable multi-platform builds with QEMU and Buildx.

### Mistake 5: No Tests Before Pushing

Pushing an image that fails tests puts a broken image in your registry. Someone might pull and deploy it.

**Fix:** Always run tests before the push step. Use `needs: test` to enforce the dependency.

---

## Best Practices

1. **Never hardcode credentials** — Use repository secrets for all sensitive values
2. **Run tests before pushing** — A broken image in the registry is worse than no image at all
3. **Use caching** — Saves minutes on every build, which adds up to hours over time
4. **Build on PRs without pushing** — Verify the build works before merging
5. **Use the metadata action for tagging** — It handles complex tagging logic correctly
6. **Push to multiple registries** — Docker Hub for public access, GHCR for GitHub integration
7. **Pin action versions** — Use `@v4` or `@v3`, not `@latest`, for reproducible pipelines
8. **Enable multi-platform builds** when your users run different architectures
9. **Use environments with protection rules** for production deployments
10. **Keep workflows DRY** — Extract common steps into reusable workflows or composite actions

---

## Quick Summary

CI/CD automates the process of building, testing, tagging, and pushing Docker images every time you push code. GitHub Actions provides a free, integrated CI/CD system that defines workflows in YAML files. The `docker/build-push-action` handles the Docker-specific steps, while `docker/metadata-action` generates appropriate tags. Caching with GitHub Actions cache dramatically speeds up builds. Multi-platform builds using QEMU and Buildx produce images for both Intel and ARM processors. Environment protection rules add manual approval gates for production deployments.

---

## Key Points

- **CI/CD** automates building, testing, and deploying — like an assembly line
- **GitHub Actions** workflows live in `.github/workflows/` as YAML files
- **Secrets** store credentials securely — never hardcode them
- **docker/build-push-action** builds and pushes images in one step
- **docker/metadata-action** generates smart tags from Git context
- **Caching** (`cache-from: type=gha`) reuses layers between builds
- **Multi-platform builds** use QEMU to build for amd64 and arm64
- **Pull requests build but do not push** — verify before merging
- **Environments** with protection rules gate production deployments
- Always **test before pushing** to avoid broken images in the registry

---

## Practice Questions

1. What is the difference between Continuous Integration and Continuous Deployment? Use the assembly line analogy to explain.

2. Why should you never hardcode Docker Hub credentials in a GitHub Actions workflow file? What should you use instead?

3. What does the `if: github.event_name != 'pull_request'` condition do in the login and push steps? Why is this important?

4. Explain what `cache-from: type=gha` and `cache-to: type=gha,mode=max` do. Why is `mode=max` important for multi-stage builds?

5. What is QEMU and why is it needed for multi-platform Docker builds in CI? What is the trade-off?

---

## Exercises

### Exercise 1: Set Up a Basic CI Pipeline

1. Create a simple Node.js or Python application with a Dockerfile
2. Initialize a Git repository and push it to GitHub
3. Create `.github/workflows/docker.yml` with a workflow that builds the image on every push
4. Push a change and verify the workflow runs in the Actions tab
5. Introduce a build error (like a typo in the Dockerfile) and verify the workflow fails with a red X

### Exercise 2: Push to Docker Hub

1. Create Docker Hub access token (Account Settings → Security → New Access Token)
2. Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` as repository secrets on GitHub
3. Extend your workflow to log in and push to Docker Hub
4. Push to `main` and verify the image appears on Docker Hub
5. Create a Git tag (`git tag v1.0.0 && git push --tags`) and verify the semantic version tags are created

### Exercise 3: Add Caching and Multi-Platform

1. Add caching to your workflow using `cache-from` and `cache-to`
2. Push twice and compare the build times (check the Actions tab for durations)
3. Enable multi-platform builds by adding QEMU setup and `platforms: linux/amd64,linux/arm64`
4. Push and verify the build completes for both platforms
5. On Docker Hub, check that the image shows both architectures

---

## What Is Next?

Your images are now built and pushed automatically. But are they secure? In the next chapter, we explore **Docker Security** — running containers as non-root users, scanning images for vulnerabilities, managing secrets safely, and hardening your containers against attacks. Security is not optional; it is a requirement for any production deployment.
