# Chapter 20: Image Tagging Strategies

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand why image tagging matters for reliable deployments
- Apply semantic versioning to Docker images
- Explain the dangers of relying on the `:latest` tag
- Use Git commit SHAs as image tags for traceability
- Implement immutable tags for production safety
- Design tagging strategies that work for teams
- Apply multi-tag approaches (v1.2.3, v1.2, v1, latest)
- Set up automated tagging in CI/CD pipelines

---

## Why This Chapter Matters

Imagine you deploy an application to production using the tag `myapp:latest`. Everything works. A week later, someone pushes a new version — also tagged `latest`. Your production server pulls the image, and the application breaks.

What version was running before? What changed? You have no idea, because `latest` was overwritten.

Tags are the **version labels** on your Docker images. Good tagging is like labeling moving boxes clearly: "Kitchen - Plates" tells you exactly what is inside, while "Stuff" tells you nothing. In production, unclear tags lead to broken deployments, wasted debugging hours, and sleepless nights.

This chapter teaches you how to tag images so that every deployment is traceable, repeatable, and safe.

---

## What Is an Image Tag?

A **tag** is a label attached to a Docker image that identifies a specific version. The full image reference looks like this:

```
repository:tag

Examples:
  nginx:1.25.3
  node:20-alpine
  myapp:v2.1.0
  myapp:abc123f
```

If you omit the tag, Docker assumes `:latest`:

```bash
docker pull nginx          # Same as: docker pull nginx:latest
docker build -t myapp .    # Same as: docker build -t myapp:latest .
```

### Tags Are Pointers, Not Copies

A tag is like a **bookmark** in a book. The bookmark points to a specific page. You can move the bookmark to a different page at any time — the pages themselves do not change.

```
+--------------------------------------------+
|            Tags Are Pointers                |
|                                             |
|   Tag "v1.0"  -----> Image abc123           |
|   Tag "v1.1"  -----> Image def456           |
|   Tag "latest" ----> Image def456           |
|                                             |
|   "latest" and "v1.1" point to the SAME     |
|   image. Moving "latest" does not delete     |
|   the old image.                             |
+--------------------------------------------+
```

This means you can have multiple tags pointing to the same image, and you can reassign a tag to point to a different image at any time.

---

## The :latest Trap

The `:latest` tag is the most misunderstood concept in Docker. Let us clear up the confusion.

### What :latest Actually Is

`:latest` is NOT:
- Automatically updated to the newest version
- A guarantee that you have the most recent image
- Special or magical in any way

`:latest` IS:
- Just the default tag when no tag is specified
- A regular, mutable tag that can point to any image
- Frequently overwritten, making it unreliable

### Why :latest Is Dangerous in Production

```
+----------------------------------------------------------+
|              The :latest Problem                          |
|                                                           |
|   Monday:    myapp:latest --> Image A (v1.0, works fine)  |
|   Tuesday:   myapp:latest --> Image B (v1.1, has a bug)   |
|   Wednesday: myapp:latest --> Image C (v1.2, different bug)|
|                                                           |
|   Which version is running on your server?                |
|   When did it change?                                     |
|   How do you roll back?                                   |
|                                                           |
|   Answer: You have NO IDEA.                               |
+----------------------------------------------------------+
```

**Problem 1: No traceability.** If production breaks, you cannot tell which version of the code is running.

**Problem 2: No reproducibility.** Running `docker pull myapp:latest` on Monday gives you a different image than on Tuesday.

**Problem 3: No safe rollback.** You cannot roll back to "the previous latest" because it has been overwritten.

**Problem 4: Cache confusion.** If a server already has `myapp:latest` cached, it might not pull the new version unless you force it.

### When :latest Is Acceptable

- **Local development** — You are the only user and you know what version you are running
- **Quick testing** — Pulling an image to try it out
- **Tutorials and examples** — Simplicity matters more than precision

### When :latest Is NOT Acceptable

- **Production deployments** — Always use specific version tags
- **Docker Compose files** — Pin exact versions for reproducibility
- **CI/CD pipelines** — Use commit SHAs or semantic versions
- **Shared environments** — Team members need to know what version they are running

---

## Semantic Versioning for Docker Images

**Semantic versioning** (SemVer) is a widely-used system for version numbers. It uses three numbers separated by dots:

```
MAJOR.MINOR.PATCH

Examples:
  1.0.0   - First release
  1.0.1   - Bug fix
  1.1.0   - New feature, backward compatible
  2.0.0   - Breaking change
```

### What Each Number Means

```
+--------------------------------------------------+
|           Semantic Versioning Explained            |
|                                                    |
|   v 2 . 3 . 1                                     |
|     |   |   |                                      |
|     |   |   +-- PATCH: Bug fixes only              |
|     |   |       "We fixed a crash."                |
|     |   |       Safe to update.                    |
|     |   |                                          |
|     |   +------ MINOR: New features added          |
|     |           "We added dark mode."              |
|     |           Old features still work.           |
|     |           Usually safe to update.            |
|     |                                              |
|     +---------- MAJOR: Breaking changes            |
|                 "We redesigned the API."           |
|                 Old code might break.              |
|                 Read the changelog first.          |
+--------------------------------------------------+
```

### Applying SemVer to Docker Images

```bash
# Initial release
docker build -t myapp:1.0.0 .

# Bug fix — increment PATCH
docker build -t myapp:1.0.1 .

# New feature — increment MINOR, reset PATCH
docker build -t myapp:1.1.0 .

# Breaking change — increment MAJOR, reset MINOR and PATCH
docker build -t myapp:2.0.0 .
```

### Real-World Example

Suppose you have a web API. Here is how versions might progress:

| Version | What Changed                    | Impact on Users           |
|---------|--------------------------------|--------------------------|
| 1.0.0   | Initial release                | First version             |
| 1.0.1   | Fixed login timeout bug        | No changes needed         |
| 1.0.2   | Fixed memory leak              | No changes needed         |
| 1.1.0   | Added search endpoint          | New feature, old API works|
| 1.2.0   | Added pagination to list API   | New feature, old API works|
| 2.0.0   | Changed authentication to OAuth| Clients must update       |

---

## Git SHA Tags

A **Git SHA tag** uses the Git commit hash as the image tag. This creates a direct link between an image and the exact source code that produced it.

```bash
# Get the short Git commit hash
GIT_SHA=$(git rev-parse --short HEAD)
echo $GIT_SHA
# Output: a1b2c3d

# Use it as the image tag
docker build -t myapp:$GIT_SHA .
docker build -t myapp:a1b2c3d .
```

### Why Git SHAs Are Useful

```
+----------------------------------------------------------+
|           Git SHA Traceability                            |
|                                                           |
|   Image tag:  myapp:a1b2c3d                               |
|                  |                                         |
|                  v                                         |
|   Git commit: a1b2c3d "Fix payment processing bug"        |
|                  |                                         |
|                  v                                         |
|   Exact code: You can see EVERY line of code               |
|               that went into this image.                   |
|                                                           |
|   Production breaks? Check commit a1b2c3d.                |
|   Need to reproduce? Build from commit a1b2c3d.           |
+----------------------------------------------------------+
```

**Advantage 1: Perfect traceability.** Given an image tag, you can find the exact commit, see the diff, read the commit message, and know who made the change.

**Advantage 2: Unique by nature.** Every commit has a unique hash, so every image tag is unique. No overwrites.

**Advantage 3: Easy debugging.** If production has `myapp:a1b2c3d`, you run `git log a1b2c3d` to see what changed.

### Limitations of Git SHAs

- **Not human-readable.** `myapp:a1b2c3d` tells you nothing about the version or features
- **No ordering.** You cannot tell if `a1b2c3d` is newer than `f4e5d6c` just by looking at them
- **Best combined with semantic versions.** Use both: `myapp:1.2.3` and `myapp:a1b2c3d`

---

## Immutable Tags

An **immutable tag** is a tag that, once assigned, cannot be overwritten. If you try to push a new image with the same tag, the registry rejects it.

### Why Immutability Matters

```
+----------------------------------------------------------+
|          Mutable vs Immutable Tags                        |
|                                                           |
|   Mutable (default):                                      |
|     Push myapp:v1.0 (Image A)                             |
|     Push myapp:v1.0 (Image B)  <-- Overwrites Image A!   |
|     Anyone pulling v1.0 gets Image B now.                 |
|                                                           |
|   Immutable:                                              |
|     Push myapp:v1.0 (Image A)                             |
|     Push myapp:v1.0 (Image B)  <-- REJECTED by registry  |
|     v1.0 ALWAYS means Image A. Forever.                   |
+----------------------------------------------------------+
```

### Enabling Immutable Tags

**AWS ECR** supports immutable tags natively:

```bash
aws ecr put-image-tag-mutability \
  --repository-name my-webapp \
  --image-tag-mutability IMMUTABLE
```

**Other registries** may not support immutable tags at the registry level. In that case, enforce immutability through your CI/CD pipeline by checking if a tag exists before pushing:

```bash
# Check if tag already exists on Docker Hub
check_tag() {
  local image=$1
  local tag=$2
  if docker manifest inspect "${image}:${tag}" > /dev/null 2>&1; then
    echo "ERROR: Tag ${tag} already exists. Cannot overwrite."
    exit 1
  fi
}

check_tag "myusername/myapp" "v1.0.0"
docker push myusername/myapp:v1.0.0
```

### Which Tags Should Be Immutable?

| Tag Type   | Should Be Immutable? | Why                                      |
|-----------|---------------------|------------------------------------------|
| v1.2.3    | Yes                 | Release versions must never change       |
| a1b2c3d   | Yes                 | Git SHAs are inherently unique           |
| latest    | No                  | Meant to be updated with each release    |
| v1.2      | No                  | Points to latest patch (v1.2.0 then v1.2.1) |
| dev       | No                  | Updated with every development build     |

---

## Tagging Strategies for Teams

When multiple developers work on the same project, you need a consistent tagging strategy. Here are the most common approaches.

### Strategy 1: SemVer Only

```
myapp:1.0.0
myapp:1.0.1
myapp:1.1.0
myapp:2.0.0
```

**Best for:** Small teams with manual releases.
**Downside:** No link to source code. Requires discipline to bump versions correctly.

### Strategy 2: Git SHA Only

```
myapp:a1b2c3d
myapp:b2c3d4e
myapp:c3d4e5f
```

**Best for:** Teams that deploy every commit. Works well with continuous deployment.
**Downside:** Not human-readable. Hard to tell which version is "stable."

### Strategy 3: SemVer + Git SHA (Recommended)

```
myapp:1.2.3
myapp:a1b2c3d
```

Both tags point to the same image. You get the best of both worlds:

- Use `1.2.3` for human communication ("deploy version 1.2.3")
- Use `a1b2c3d` for debugging ("what code is in production?")

### Strategy 4: Branch-Based Tags

```
myapp:main-a1b2c3d      <-- Built from main branch
myapp:develop-b2c3d4e   <-- Built from develop branch
myapp:feature-auth-c3d  <-- Built from feature branch
```

**Best for:** Teams using GitFlow or similar branching strategies.
**Downside:** Tags get long and numerous. Feature branch tags may never be used in production.

### Strategy 5: Environment-Based Tags

```
myapp:staging
myapp:production
```

**Warning:** This approach has the same problems as `:latest`. The tag `staging` gets overwritten with every deployment. Avoid this in favor of SemVer or Git SHAs.

---

## Multi-Tag Strategy

The most robust approach is to apply **multiple tags** to the same image. This gives users flexibility in how they pin their versions.

### How Multi-Tagging Works

When you release version `1.2.3`, you create four tags:

```bash
docker build -t myapp:1.2.3 .
docker tag myapp:1.2.3 myapp:1.2
docker tag myapp:1.2.3 myapp:1
docker tag myapp:1.2.3 myapp:latest
```

All four tags point to the same image:

```
+----------------------------------------------------------+
|              Multi-Tag Strategy                           |
|                                                           |
|   myapp:1.2.3  ----+                                      |
|   myapp:1.2    ----+--> Same Image (abc123)               |
|   myapp:1      ----+                                      |
|   myapp:latest ----+                                      |
|                                                           |
|   Users choose their risk level:                          |
|     :1.2.3   = "I want exactly this version"             |
|     :1.2     = "Give me the latest patch for 1.2"        |
|     :1       = "Give me the latest 1.x version"          |
|     :latest  = "Give me whatever is newest"              |
+----------------------------------------------------------+
```

### What Happens When You Release 1.2.4

```bash
docker build -t myapp:1.2.4 .
docker tag myapp:1.2.4 myapp:1.2      # Now points to 1.2.4
docker tag myapp:1.2.4 myapp:1        # Now points to 1.2.4
docker tag myapp:1.2.4 myapp:latest   # Now points to 1.2.4
# myapp:1.2.3 still points to the OLD image — it is NOT overwritten
```

```
+----------------------------------------------------------+
|           After Releasing 1.2.4                           |
|                                                           |
|   myapp:1.2.3  ---------> Old Image (abc123)             |
|                                                           |
|   myapp:1.2.4  ----+                                      |
|   myapp:1.2    ----+--> New Image (def456)                |
|   myapp:1      ----+                                      |
|   myapp:latest ----+                                      |
|                                                           |
|   Users pinned to :1.2.3 are unaffected.                 |
|   Users on :1.2 automatically get 1.2.4.                 |
+----------------------------------------------------------+
```

### Real-World Example: Node.js Tags

The official `node` image on Docker Hub demonstrates this perfectly:

```
node:20.10.0          <-- Exact version
node:20.10            <-- Latest patch for 20.10
node:20               <-- Latest 20.x version
node:lts              <-- Current long-term support
node:latest           <-- Most recent release
node:20.10.0-alpine   <-- Exact version, Alpine base
node:20-alpine        <-- Latest 20.x, Alpine base
```

---

## Automated Tagging in CI/CD

Manually tagging images is error-prone. Automate it in your CI/CD pipeline.

### GitHub Actions Example

```yaml
# .github/workflows/docker-tag.yml
name: Build and Tag Docker Image

on:
  push:
    branches: [main]
    tags: ['v*']  # Trigger on version tags like v1.2.3

env:
  IMAGE_NAME: myusername/myapp

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract metadata for tagging
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_NAME }}
          tags: |
            # Tag with Git SHA for every push
            type=sha,prefix=
            # Tag with branch name
            type=ref,event=branch
            # Tag with semver from Git tag (v1.2.3 -> 1.2.3, 1.2, 1)
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            # Tag as latest for default branch
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
```

**What this does:**

When you push to `main`:
- Tags with the Git SHA: `myapp:a1b2c3d`
- Tags with the branch name: `myapp:main`
- Tags as `myapp:latest`

When you create a Git tag `v1.2.3`:
- Tags as `myapp:1.2.3`
- Tags as `myapp:1.2`
- Tags as `myapp:1`
- Tags with the Git SHA: `myapp:a1b2c3d`

### Automated Tagging Script (Without CI/CD)

If you are not using a CI/CD system, here is a shell script:

```bash
#!/bin/bash
# tag-and-push.sh — Tag and push a Docker image with multiple tags

set -e

IMAGE="myusername/myapp"
VERSION=$1  # Pass version as argument: ./tag-and-push.sh 1.2.3

if [ -z "$VERSION" ]; then
  echo "Usage: ./tag-and-push.sh <version>"
  echo "Example: ./tag-and-push.sh 1.2.3"
  exit 1
fi

# Extract major and minor versions
MAJOR=$(echo "$VERSION" | cut -d. -f1)
MINOR=$(echo "$VERSION" | cut -d. -f1-2)
GIT_SHA=$(git rev-parse --short HEAD)

echo "Building image..."
docker build -t "$IMAGE:$VERSION" .

echo "Creating additional tags..."
docker tag "$IMAGE:$VERSION" "$IMAGE:$MINOR"
docker tag "$IMAGE:$VERSION" "$IMAGE:$MAJOR"
docker tag "$IMAGE:$VERSION" "$IMAGE:$GIT_SHA"
docker tag "$IMAGE:$VERSION" "$IMAGE:latest"

echo "Pushing all tags..."
docker push "$IMAGE" --all-tags

echo "Done! Pushed tags: $VERSION, $MINOR, $MAJOR, $GIT_SHA, latest"
```

**Usage:**

```bash
chmod +x tag-and-push.sh
./tag-and-push.sh 1.2.3
```

**Output:**

```
Building image...
Creating additional tags...
Pushing all tags...
Done! Pushed tags: 1.2.3, 1.2, 1, a1b2c3d, latest
```

---

## Common Mistakes

### Mistake 1: Using :latest in Production

```yaml
# docker-compose.yml — DO NOT DO THIS
services:
  web:
    image: myapp:latest  # Which version is this? Nobody knows.
```

**Fix:**

```yaml
# docker-compose.yml — DO THIS
services:
  web:
    image: myapp:1.2.3  # Exact version, reproducible
```

### Mistake 2: Forgetting to Tag Before Pushing

```bash
docker build -t myapp .
docker push myapp  # Pushes as "myapp:latest" — not versioned!
```

**Fix:**

```bash
docker build -t myusername/myapp:1.0.0 .
docker push myusername/myapp:1.0.0
```

### Mistake 3: Overwriting Release Tags

```bash
# Version 1.0.0 already exists on the registry
docker build -t myapp:1.0.0 .   # Different code!
docker push myapp:1.0.0         # Overwrites the original!
```

**Fix:** Never reuse a release tag. If you need to fix a bug, release `1.0.1`.

### Mistake 4: Inconsistent Tagging Across the Team

Developer A uses `v1.2.3`, Developer B uses `1.2.3`, Developer C uses `release-1.2.3`. Chaos.

**Fix:** Document your tagging convention and enforce it in CI/CD:

```
# Our tagging convention (document this in your README):
# Release tags: 1.2.3 (no "v" prefix)
# Git SHA tags: a1b2c3d (short SHA, 7 characters)
# Branch tags: main, develop (branch name only)
```

### Mistake 5: Not Cleaning Up Old Tags

Over time, hundreds of tags accumulate in your registry, consuming storage and making it hard to find relevant versions.

**Fix:** Set up a retention policy. Most registries support lifecycle rules:

```bash
# AWS ECR lifecycle policy — keep only last 30 images
aws ecr put-lifecycle-policy \
  --repository-name myapp \
  --lifecycle-policy-text '{
    "rules": [{
      "rulePriority": 1,
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 30
      },
      "action": { "type": "expire" }
    }]
  }'
```

---

## Best Practices

1. **Never use `:latest` in production** — Always pin a specific version tag
2. **Use semantic versioning** — MAJOR.MINOR.PATCH communicates the type of change
3. **Add Git SHA tags** — Create a direct link between images and source code
4. **Apply multiple tags** — Give users flexibility (exact version, minor, major, latest)
5. **Make release tags immutable** — Once `1.2.3` is pushed, it should never change
6. **Document your tagging convention** — Write it down so the whole team follows it
7. **Automate tagging in CI/CD** — Humans make mistakes; automation does not
8. **Clean up old tags** — Set retention policies to avoid unbounded storage growth
9. **Use consistent formats** — Choose `1.2.3` or `v1.2.3` and stick with it everywhere

---

## Quick Summary

Image tags identify specific versions of Docker images. The `:latest` tag is a trap in production because it is mutable and provides no traceability. Semantic versioning (MAJOR.MINOR.PATCH) communicates the impact of changes. Git SHA tags link images to exact source code commits. Immutable tags prevent accidental overwrites of release versions. The multi-tag strategy (1.2.3 + 1.2 + 1 + latest) gives users flexibility while maintaining precision. Automate tagging in CI/CD pipelines to ensure consistency and eliminate human error.

---

## Key Points

- **Tags are pointers** — Multiple tags can point to the same image, and tags can be moved
- **`:latest` is not special** — It is just the default tag, and it is mutable (overwritable)
- **Semantic versioning** uses MAJOR.MINOR.PATCH to communicate the type of change
- **Git SHA tags** create a traceable link from an image to its source code
- **Immutable tags** prevent release versions from being overwritten
- **Multi-tagging** (1.2.3, 1.2, 1, latest) gives users control over their update risk
- **Automate tagging** in CI/CD to ensure consistency
- **Document your convention** so the team follows the same rules

---

## Practice Questions

1. What does the `:latest` tag actually mean? Why is it dangerous to use in production?

2. In semantic versioning, what does it mean when the MAJOR version number changes? Give an example with Docker image tags.

3. What is a Git SHA tag, and what problem does it solve that semantic version tags do not?

4. You release version `1.2.3` of your application. Which tags should you create following the multi-tag strategy?

5. What is an immutable tag? Which types of tags should be immutable and which should remain mutable?

---

## Exercises

### Exercise 1: Multi-Tag a Release

1. Build a simple Docker image from any previous chapter
2. Pretend this is version `2.1.0` of your application
3. Create all four tags: `2.1.0`, `2.1`, `2`, and `latest`
4. Run `docker images` and verify all four tags show the same IMAGE ID
5. Now pretend you release `2.1.1` (a bug fix). Create tags for `2.1.1` and update `2.1`, `2`, and `latest`
6. Run `docker images` again. Which tags now point to the new image? Which still point to the old one?

### Exercise 2: Git SHA Tagging

1. Initialize a Git repository in a project directory (or use an existing one)
2. Make a commit with a simple change
3. Get the short Git SHA with `git rev-parse --short HEAD`
4. Build a Docker image tagged with this SHA
5. Make another commit and build again with the new SHA
6. You now have two images. Given an image tag, can you find the exact commit?

### Exercise 3: Write a Tagging Convention

1. Write a document (plain text is fine) that defines your team's tagging convention
2. Include: what format to use for release tags, whether to include a "v" prefix, when to use Git SHAs, what `:latest` should point to, and how often to clean up old tags
3. Create a simple shell script that enforces this convention (validates that the tag matches your pattern before pushing)

---

## What Is Next?

You now know how to tag images for clarity, safety, and traceability. But tagging is only one piece of the puzzle. In the next chapter, we explore **CI/CD with Docker** — how to automate the entire process of building, tagging, and pushing images every time you push code. No more manual builds. No more forgotten tags. Just push your code and let the pipeline handle the rest.
