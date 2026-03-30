# Chapter 5: Docker Images

## What You Will Learn

- What is inside a Docker image
- How to list images on your computer
- How to download images from Docker Hub
- How tags work (:latest, :3.9, :alpine, and more)
- What image IDs and digests are
- How to inspect image details
- How to remove images
- How to browse Docker Hub effectively
- The difference between official and community images
- How to compare image sizes and choose wisely

## Why This Chapter Matters

Images are the foundation of Docker. Every container starts from an image. Every deployment ships an image. Every team shares images.

If images are the ingredients in your kitchen, this chapter teaches you how to shop. Where to find the best ingredients. How to read the labels. How to pick the right version. How to clean out your fridge when it gets full.

You already know that images exist. Now you will learn to manage them like a professional.

---

## What Is Inside a Docker Image?

An image contains everything your application needs to run. Let us look at what a typical Python web application image includes:

```
Docker Image: my-python-app
+-------------------------------------------+
|  Layer 5: Your application code           |
|           app.py, requirements.txt        |
+-------------------------------------------+
|  Layer 4: Python packages                 |
|           Flask, requests, gunicorn       |
+-------------------------------------------+
|  Layer 3: Python runtime                  |
|           python3, pip                    |
+-------------------------------------------+
|  Layer 2: System packages                 |
|           libssl, libffi, gcc             |
+-------------------------------------------+
|  Layer 1: Base operating system           |
|           Debian slim (minimal Linux)     |
+-------------------------------------------+
```

An image does NOT contain:
- A full operating system kernel (it uses the host's kernel)
- Hardware drivers
- A boot loader
- System services like SSH or cron (unless you specifically add them)

This is why images are small compared to virtual machine disks.

### Concrete Examples

Here is what common images contain:

**Node.js image (`node:20`):**
- Debian Linux (base)
- Node.js 20 runtime
- npm package manager
- Common build tools

**Python image (`python:3.12`):**
- Debian Linux (base)
- Python 3.12 interpreter
- pip package manager
- Common C libraries for building packages

**Nginx image (`nginx:latest`):**
- Debian Linux (base)
- Nginx web server
- Default configuration files
- Default HTML page

**Alpine image (`alpine:latest`):**
- Alpine Linux (minimal, ~7 MB)
- BusyBox utilities (basic Linux commands)
- apk package manager
- Almost nothing else

---

## Listing Images: docker images

To see all images stored on your computer:

```bash
docker images
```

**Expected output:**

```
REPOSITORY    TAG       IMAGE ID       CREATED        SIZE
nginx         latest    a8758716bb6a   2 weeks ago    187MB
python        3.12      dfb5b0152abc   3 weeks ago    1.01GB
alpine        latest    05455a08881e   4 weeks ago    7.38MB
node          20-slim   b1d4de7d95e2   4 weeks ago    220MB
hello-world   latest    d2c94e258dcb   9 months ago   13.3kB
```

**Column explanations:**

| Column | Meaning |
|---|---|
| `REPOSITORY` | The name of the image (like `nginx` or `python`) |
| `TAG` | The version or variant (like `latest` or `3.12`) |
| `IMAGE ID` | A unique 12-character identifier (short form) |
| `CREATED` | When the image was built (not when you downloaded it) |
| `SIZE` | How much disk space the image uses |

### Alternative Command

You can also use:

```bash
docker image ls
```

This does the same thing. Docker has both older-style commands (`docker images`) and newer-style commands (`docker image ls`). Both work.

---

## Downloading Images: docker pull

When you run `docker run nginx`, Docker automatically downloads the image if you do not have it. But you can also download images manually with `docker pull`.

```bash
docker pull python:3.12
```

**Expected output:**

```
3.12: Pulling from library/python
6a299ae1ccee: Pull complete
839dbcc8d89f: Pull complete
d3cd37f7e8c1: Pull complete
7c5af6fa66a5: Pull complete
c5f20a7b5a88: Pull complete
Digest: sha256:3966b81808d864099f802080d897cef36c01550472ab3955fdd716d1c665acd6
Status: Downloaded newer image for python:3.12
docker.io/library/python:3.12
```

**Line-by-line explanation:**
- `3.12: Pulling from library/python` -- Docker is downloading version 3.12 from the official Python repository on Docker Hub.
- `6a299ae1ccee: Pull complete` -- Each line represents a layer being downloaded. The hex string is the layer's unique ID.
- `Digest: sha256:3966b8...` -- A cryptographic hash that uniquely identifies this exact image. Think of it as a fingerprint.
- `Status: Downloaded newer image` -- Confirms the download is complete.
- `docker.io/library/python:3.12` -- The full address of the image. `docker.io` is Docker Hub. `library` means it is an official image.

### Why Pull Manually?

You might want to pull an image ahead of time:
- To speed up `docker run` later (no download needed)
- To make sure you have the latest version
- To prepare a machine before deploying containers
- To download during off-peak hours

---

## Understanding Tags

Tags are labels attached to images. They usually indicate a version, a variant, or both.

### The :latest Tag

If you do not specify a tag, Docker uses `:latest` by default.

```bash
docker pull nginx
```

This is the same as:

```bash
docker pull nginx:latest
```

**Warning:** `:latest` does not always mean "the newest version." It is just a tag name. Most image maintainers point it to the newest stable version, but this is a convention, not a guarantee.

### Version Tags

Version tags specify an exact version:

```bash
docker pull python:3.12
docker pull python:3.11
docker pull python:3.10
docker pull node:20
docker pull node:18
```

These are the most common tags. They tell you exactly which version you are getting.

### Variant Tags

Some images have variants. The most common ones:

**`:slim`** -- A smaller version with fewer pre-installed packages.

```bash
docker pull python:3.12-slim
```

**`:alpine`** -- Built on Alpine Linux. Very small. Minimal packages.

```bash
docker pull python:3.12-alpine
docker pull node:20-alpine
```

**`:bookworm` or `:bullseye`** -- Built on specific Debian Linux releases.

```bash
docker pull python:3.12-bookworm
docker pull python:3.12-bullseye
```

### Combining Version and Variant

Tags can combine version and variant information:

```bash
docker pull python:3.12-slim-bookworm
```

This means: Python 3.12, slim variant, on Debian Bookworm.

### Tag Comparison Example

Let us see how tags affect image size for the Python image:

```bash
docker pull python:3.12
docker pull python:3.12-slim
docker pull python:3.12-alpine
docker images | grep python
```

**Expected output:**

```
REPOSITORY   TAG            IMAGE ID       CREATED       SIZE
python       3.12           dfb5b0152abc   3 weeks ago   1.01GB
python       3.12-slim      a1b2c3d4e5f6   3 weeks ago   143MB
python       3.12-alpine    f6e5d4c3b2a1   3 weeks ago   51.8MB
```

```
Image Size Comparison:

python:3.12          [================================================] 1.01 GB
python:3.12-slim     [=======]                                          143 MB
python:3.12-alpine   [===]                                              51.8 MB

The alpine variant is about 20x smaller than the full image!
```

### Which Tag Should You Use?

| Tag | Use When |
|---|---|
| `:latest` | Quick experiments, testing (NOT production) |
| `:3.12` (version) | Production, when you need a specific version |
| `:3.12-slim` | Production, when you want smaller images |
| `:3.12-alpine` | When size matters most, and you can handle Alpine's differences |

**Best practice:** Always specify a version tag in production. Never use `:latest` in production because it can change without warning.

```
Bad:   docker run python              # What version? Who knows!
Good:  docker run python:3.12-slim    # Python 3.12, slim variant. Clear.
```

---

## Image IDs and Digests

Every image has two types of identifiers: an **ID** and a **digest**.

### Image ID

The image ID is a unique identifier generated from the image contents. You see it in `docker images` output:

```
REPOSITORY   TAG      IMAGE ID       CREATED       SIZE
nginx        latest   a8758716bb6a   2 weeks ago   187MB
```

`a8758716bb6a` is the short form. The full ID is much longer:

```bash
docker inspect nginx:latest --format='{{.Id}}'
```

**Expected output:**

```
sha256:a8758716bb6aa4d90071160d27028fe4eaee7ce8166221a97d30440c8eac2be6
```

The short ID is the first 12 characters of the full ID.

### Image Digest

A digest is a cryptographic hash of the image manifest. It uniquely identifies the image on a registry (like Docker Hub).

```bash
docker images --digests
```

**Expected output:**

```
REPOSITORY  TAG     DIGEST                                                           IMAGE ID      SIZE
nginx       latest  sha256:56b388b0d79c738f4cf51bbaf184a14fa82d...  a8758716bb6a  187MB
```

### Why Digests Matter

Tags can change. Today `python:3.12` points to one image. Tomorrow, when a security patch is released, `python:3.12` might point to a different image.

Digests never change. The digest `sha256:3966b818...` will always refer to the exact same image. If you need absolute certainty about which image you are running, use the digest:

```bash
docker pull python@sha256:3966b81808d864099f802080d897cef36c01550472ab3955fdd716d1c665acd6
```

This guarantees you get the exact same image every time, no matter what.

```
Tags can move:                    Digests are permanent:

python:3.12                       python@sha256:abc123...
  |                                |
  v                                v
  Image A (Jan 2024)              Image A (forever)
  |
  v (tag updated!)
  Image B (Feb 2024)              Digest never changes.
                                  It always points to
Tag now points to a               the same image.
different image!
```

---

## Inspecting Images: docker image inspect

Want to see the details of an image? Use `docker image inspect`.

```bash
docker image inspect nginx:latest
```

**Expected output (abbreviated):**

```json
[
    {
        "Id": "sha256:a8758716bb6a...",
        "Created": "2024-01-10T00:00:00.000000000Z",
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 187365382,
        "Config": {
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:...",
                "NGINX_VERSION=1.25.3"
            ],
            "ExposedPorts": {
                "80/tcp": {}
            },
            "Cmd": ["nginx", "-g", "daemon off;"]
        },
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:7292cf786aa8...",
                "sha256:43d8c25e73d4...",
                "sha256:5e99f539e0d2...",
                "sha256:02b80e18f1b4...",
                "sha256:6d1f20c1c6fd...",
                "sha256:29db1f0a7b32...",
                "sha256:e3c2f1048ab6..."
            ]
        }
    }
]
```

**Key fields explained:**

| Field | Meaning |
|---|---|
| `Id` | The full image ID |
| `Created` | When the image was built |
| `Architecture` | What CPU architecture it is built for (amd64, arm64) |
| `Os` | What operating system (always `linux` for Docker) |
| `Size` | Image size in bytes |
| `Env` | Environment variables set in the image |
| `ExposedPorts` | Ports the application listens on |
| `Cmd` | The default command that runs when you start a container |
| `Layers` | List of layer hashes that make up the image |

### Getting Specific Information

You can extract specific fields:

```bash
# Get the default command
docker image inspect nginx:latest --format='{{.Config.Cmd}}'
```

**Output:**

```
[nginx -g daemon off;]
```

```bash
# Get the number of layers
docker image inspect nginx:latest --format='{{len .RootFS.Layers}}'
```

**Output:**

```
7
```

```bash
# Get the architecture
docker image inspect nginx:latest --format='{{.Architecture}}'
```

**Output:**

```
amd64
```

---

## Removing Images: docker rmi

Images take up disk space. You will want to remove ones you no longer need.

### Remove a Specific Image

```bash
docker rmi hello-world
```

**Expected output:**

```
Untagged: hello-world:latest
Untagged: hello-world@sha256:c41088499908a59aae30...
Deleted: sha256:d2c94e258dcb3c5ac2798d32e1249e42ef01cba4841c2234249495f87264ac5a
Deleted: sha256:ac28800ec8bb38d5c35b49d45a6ac4777544941199075dff8c4eb63e093aa81e
```

**Line-by-line explanation:**
- `Untagged: hello-world:latest` -- Removes the tag from the image.
- `Untagged: hello-world@sha256:...` -- Removes the digest reference.
- `Deleted: sha256:d2c94e...` -- Deletes the image layer from disk.
- `Deleted: sha256:ac2880...` -- Deletes another layer.

### You Cannot Remove an Image That Is in Use

If a container (even a stopped one) was created from an image, Docker will refuse to remove the image:

```bash
docker rmi nginx
```

**Error output:**

```
Error response from daemon: conflict: unable to remove repository reference
"nginx:latest" (must force) - container a1b2c3d4 is using its referenced image
```

**Fix:** Remove the container first, then the image:

```bash
docker rm a1b2c3d4
docker rmi nginx
```

Or force it:

```bash
docker rmi -f nginx
```

### Remove Multiple Images

```bash
docker rmi python:3.12 node:20 alpine:latest
```

### Remove All Unused Images

```bash
docker image prune
```

**Expected output:**

```
WARNING! This will remove all dangling images.
Are you sure you want to continue? [y/N] y
Deleted Images:
deleted: sha256:f6e5d4c3b2a1...
deleted: sha256:a1b2c3d4e5f6...

Total reclaimed space: 250MB
```

**What is a "dangling" image?** A dangling image is one that has no tag. This happens when you build a new version of an image with the same tag. The old version loses its tag and becomes dangling.

### Remove ALL Unused Images (More Aggressive)

```bash
docker image prune -a
```

This removes ALL images that are not used by at least one container. It reclaims more space but removes more images. You will need to pull them again if you need them.

---

## Browsing Docker Hub

Docker Hub (https://hub.docker.com) is the largest public registry of Docker images. Let us learn how to navigate it effectively.

### Searching from the Command Line

```bash
docker search python
```

**Expected output:**

```
NAME                         DESCRIPTION                                     STARS   OFFICIAL
python                       Python is an interpreted, interactive, ...       9456    [OK]
pypy                         PyPy is a fast, compliant alternative ...        380     [OK]
circleci/python              Python is a high-level programming ...           55
cimg/python                  Community-maintained Python images ...           19
bitnami/python               Bitnami container image for Python              26
```

**Column explanations:**

| Column | Meaning |
|---|---|
| `NAME` | Image name |
| `DESCRIPTION` | A short description |
| `STARS` | How many users have "starred" this image (like GitHub stars) |
| `OFFICIAL` | Whether this is an official image maintained by Docker or the software vendor |

### Using the Docker Hub Website

The website gives you much more information than the command line:

1. **Overview tab:** Description, quick start instructions, supported tags.
2. **Tags tab:** All available versions and variants with their sizes and architectures.
3. **Docker Pull Command:** A copy-paste command to download the image.
4. **Source:** Link to the Dockerfile (the recipe used to build the image).
5. **Vulnerability scanning:** Security reports showing known vulnerabilities.

---

## Official vs Community Images

This is an important distinction. Choose wisely.

### Official Images

Official images are curated and maintained by Docker in partnership with the software vendors (or by dedicated maintainers).

**How to recognize them:**
- The name has no prefix: `python`, `nginx`, `node`, `postgres`
- They show `[OK]` in the OFFICIAL column when you search
- On Docker Hub, they have a "Docker Official Image" badge

**Why use them:**
- Regularly updated with security patches
- Follow best practices
- Well-documented
- Scanned for vulnerabilities
- Trusted by the community

**Examples:**

```bash
docker pull python        # Official Python image
docker pull nginx         # Official Nginx image
docker pull node          # Official Node.js image
docker pull postgres      # Official PostgreSQL image
docker pull redis         # Official Redis image
docker pull openjdk       # Official Java image
```

### Community Images

Community images are created by individuals or organizations. They have a username or organization prefix.

```bash
docker pull bitnami/python     # Bitnami's Python image
docker pull circleci/python    # CircleCI's Python image
docker pull myuser/myapp       # Someone's custom image
```

**When to use them:**
- When no official image exists for the software you need
- When a community image has specific features you need (like pre-configured tools)
- When a trusted organization maintains it (like Bitnami, CircleCI, or Google)

**When to be careful:**
- Unknown authors
- Low star counts
- Images not updated in a long time
- No documentation
- No linked source code (Dockerfile)

```
Choosing an Image:

Official Images                    Community Images
+----------------------+          +----------------------+
| python               |          | randomuser/python    |
| nginx                |          | myorg/custom-nginx   |
| node                 |          | bitnami/node         |
+----------------------+          +----------------------+
| - Trusted            |          | - May have extras    |
| - Updated regularly  |          | - Quality varies     |
| - Scanned for bugs   |          | - Check the author   |
| - Well documented    |          | - Check last update  |
+----------------------+          +----------------------+
| USE FIRST            |          | USE WHEN NEEDED      |
+----------------------+          +----------------------+
```

---

## Image Size Comparison

Image size matters. Smaller images mean:
- Faster downloads
- Faster deployments
- Less disk space used
- Smaller attack surface (fewer packages means fewer potential vulnerabilities)

Here is a real comparison of common images:

```bash
docker pull ubuntu:22.04
docker pull debian:bookworm-slim
docker pull alpine:latest
docker images
```

**Expected output:**

```
REPOSITORY   TAG              SIZE
ubuntu       22.04            77.9MB
debian       bookworm-slim    74.8MB
alpine       latest           7.38MB
```

```
Base Image Size Comparison:

ubuntu:22.04         [==========================]           77.9 MB
debian:bookworm-slim [=========================]            74.8 MB
alpine:latest        [===]                                  7.38 MB

Alpine is about 10x smaller than Ubuntu or Debian!
```

### Application Image Sizes

The same application can have dramatically different sizes depending on the base image:

```
Node.js Image Variants:

node:20              [================================================]  1.1 GB
node:20-slim         [==========]                                        220 MB
node:20-alpine       [======]                                            135 MB

Python Image Variants:

python:3.12          [================================================]  1.01 GB
python:3.12-slim     [=======]                                           143 MB
python:3.12-alpine   [===]                                               51.8 MB

Java Image Variants:

eclipse-temurin:21   [================================================]  422 MB
eclipse-temurin:21-alpine [========]                                     185 MB
```

### When to Use Alpine

Alpine images are the smallest, but there are trade-offs:

**Advantages:**
- Tiny size (7 MB base)
- Faster to download and deploy
- Smaller attack surface

**Disadvantages:**
- Uses `musl` instead of `glibc` (a different C library). Some software may not work.
- Uses `apk` instead of `apt` (different package manager). Package names are different.
- Fewer pre-installed tools. You may need to install more things manually.
- Some Python packages need extra compilation steps on Alpine.

**Rule of thumb:** Start with slim variants. Try Alpine if you need smaller images and are willing to handle compatibility issues.

---

## Checking Disk Space

Over time, images accumulate and use significant disk space. Check how much space Docker is using:

```bash
docker system df
```

**Expected output:**

```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          8         3         3.2GB     2.1GB (65%)
Containers      5         2         50MB      30MB (60%)
Local Volumes   3         2         500MB     200MB (40%)
Build Cache     0         0         0B        0B
```

**Column explanations:**

| Column | Meaning |
|---|---|
| `TOTAL` | Total number of items |
| `ACTIVE` | Number currently in use by running containers |
| `SIZE` | Total disk space used |
| `RECLAIMABLE` | Space you could free up by removing unused items |

In this example, you could free up 2.1 GB by removing unused images.

---

## A Complete Image Workflow

Here is a typical workflow for working with images:

```bash
# 1. Search for an image
docker search postgres

# 2. Pull a specific version
docker pull postgres:16

# 3. List your images
docker images

# 4. Inspect the image
docker image inspect postgres:16

# 5. Run a container from it
docker run -d --name my-db -e POSTGRES_PASSWORD=mysecret postgres:16

# 6. When done, stop and remove the container
docker stop my-db
docker rm my-db

# 7. If you no longer need the image, remove it
docker rmi postgres:16

# 8. Clean up all unused images
docker image prune
```

---

## Command Reference

| Command | What It Does |
|---|---|
| `docker images` | List all images |
| `docker image ls` | List all images (alternative syntax) |
| `docker pull IMAGE:TAG` | Download an image |
| `docker image inspect IMAGE` | Show detailed image information |
| `docker rmi IMAGE` | Remove an image |
| `docker rmi -f IMAGE` | Force remove an image |
| `docker image prune` | Remove dangling images |
| `docker image prune -a` | Remove all unused images |
| `docker search TERM` | Search Docker Hub |
| `docker images --digests` | List images with digests |
| `docker system df` | Show Docker disk usage |

---

## Common Mistakes

1. **Using `:latest` in production.** The `:latest` tag can change at any time. Always pin to a specific version like `:3.12` or `:3.12-slim` in production environments.

2. **Not cleaning up old images.** Images accumulate quickly. A developer's machine can easily have 20-50 GB of Docker images. Run `docker image prune` regularly.

3. **Choosing the full image when slim would work.** The full `python:3.12` image is over 1 GB. The slim version is 143 MB. Unless you specifically need the extra packages, use slim.

4. **Pulling images without checking the source.** Always verify that an image is official or from a trusted publisher before using it. Unverified images could contain malware.

5. **Confusing image ID with container ID.** They look similar (both are hex strings) but refer to different things. Use `docker images` for images and `docker ps` for containers.

---

## Best Practices

1. **Always specify a tag.** Use `python:3.12-slim`, not `python`. This ensures reproducibility. Your container will be the same today, tomorrow, and next year.

2. **Use official images as your starting point.** Even if you need a custom image, start from an official base. Build on top of `python:3.12-slim`, not some random image.

3. **Choose the smallest image that works.** Start with `-slim`. Try `-alpine` if you can. Only use the full image if you need specific tools that are not in the slim version.

4. **Clean up regularly.** Add `docker system prune` to your weekly routine. Or set up automatic cleanup in your CI/CD pipeline.

5. **Use digests for critical deployments.** When deploying to production, consider using the image digest instead of a tag for absolute certainty about what is running.

6. **Check image vulnerabilities.** Docker Hub shows vulnerability scans for official images. Review them before using an image in production.

---

## Quick Summary

Docker images are read-only templates stored as layers. You list them with `docker images`, download them with `docker pull`, and remove them with `docker rmi`. Tags identify specific versions and variants (`:latest`, `:3.12`, `:3.12-slim`, `:3.12-alpine`). Image IDs are unique hashes. Digests provide immutable references that never change. Official images are maintained by Docker and software vendors and should be your first choice. Image size varies dramatically by variant -- Alpine images are the smallest but have compatibility trade-offs.

---

## Key Points

- Images are read-only templates made of layers. Containers are running instances.
- `docker images` lists all images on your computer.
- `docker pull IMAGE:TAG` downloads an image from Docker Hub.
- Tags identify versions and variants: `:latest`, `:3.12`, `:slim`, `:alpine`.
- Always use explicit version tags in production. Never rely on `:latest`.
- Image IDs are unique identifiers. Digests are immutable references.
- `docker image inspect` shows detailed metadata about an image.
- `docker rmi` removes images. `docker image prune` removes unused images.
- Official images are trusted, regularly updated, and your best starting point.
- Slim and Alpine variants are much smaller than full images.
- `docker system df` shows how much disk space Docker is using.

---

## Practice Questions

1. What is the difference between `docker pull python:3.12` and `docker pull python:3.12-alpine`? Which one is smaller and why?

2. Why should you avoid using the `:latest` tag in production? What could go wrong?

3. What is the difference between an image ID and a digest? When would you use a digest instead of a tag?

4. You run `docker rmi nginx` and get an error about a container using the image. What should you do?

5. How would you find out the default command that an image runs when you start a container from it?

---

## Exercises

### Exercise 1: Compare Image Sizes

Pull these three variants of the Node.js image:

```bash
docker pull node:20
docker pull node:20-slim
docker pull node:20-alpine
```

Use `docker images` to compare their sizes. Calculate how much smaller the Alpine variant is compared to the full image (as a percentage).

### Exercise 2: Inspect and Compare

Inspect the `nginx:latest` and `python:3.12-slim` images:

```bash
docker image inspect nginx:latest
docker image inspect python:3.12-slim
```

For each image, find:
- How many layers does it have?
- What is the default command?
- What environment variables are set?

### Exercise 3: Clean Up Challenge

1. Run `docker system df` to see your current disk usage.
2. Pull five different images (your choice).
3. Run `docker system df` again. How much did the disk usage increase?
4. Remove all the images you just pulled.
5. Run `docker image prune` to clean up any dangling images.
6. Run `docker system df` one final time. Is your disk usage back to where it started?

---

## What Is Next?

You now understand Docker images -- how to find them, inspect them, manage them, and choose the right ones. In the next chapter, you will learn how to create your OWN images by writing a Dockerfile. You will package your own application into a Docker image and share it with the world. That is where Docker starts to become truly powerful.
