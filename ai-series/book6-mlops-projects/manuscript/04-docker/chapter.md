# Chapter 4: Docker for ML Applications

## What You Will Learn

In this chapter, you will learn:

- What containers are and why they matter for ML
- How Docker works using a shipping container analogy
- How to write a Dockerfile for an ML application
- How to build and run Docker images
- How to use docker-compose to manage multiple services
- How to containerize a complete ML API

## Why This Chapter Matters

Imagine you bake a perfect cake at home. You share the recipe with a friend. They follow it exactly, but their cake tastes different. Why? Maybe their oven temperature is slightly off. Maybe their flour brand is different. Maybe they have a different altitude.

The same thing happens with software. Your ML API works perfectly on your laptop. But when you try to run it on a server, it breaks. The server has a different Python version. A library is missing. A system package is wrong.

Docker solves this problem by packaging your application with everything it needs: code, libraries, system tools, and settings. It is like giving your friend not just the recipe, but the entire kitchen.

---

## What Are Containers?

A container is a lightweight, standalone package that includes everything needed to run a piece of software. Let us understand this with the shipping container analogy.

### The Shipping Container Analogy

```
+--------------------------------------------------+
|  Before Shipping Containers (Before Docker)      |
|                                                   |
|  Loading a cargo ship was a nightmare:           |
|  - Different shapes and sizes of goods           |
|  - Each item needed special handling             |
|  - Moving cargo between ships was slow           |
|  - Things got damaged or lost                    |
|                                                   |
|  After Shipping Containers (After Docker)        |
|                                                   |
|  Everything goes in standard containers:         |
|  - Any container fits on any ship                |
|  - Easy to move between ships, trucks, trains    |
|  - Contents are protected and isolated           |
|  - Loading and unloading is fast                 |
+--------------------------------------------------+
```

```
+--------------------------------------------------+
|  Docker Container = Shipping Container            |
|                                                   |
|  +-----------------------------+                  |
|  | Your ML Application        |                  |
|  |                             |                  |
|  | Python 3.11                |                  |
|  | scikit-learn 1.3           |                  |
|  | FastAPI 0.104              |                  |
|  | Your model file            |                  |
|  | Your code                  |                  |
|  | Everything it needs        |                  |
|  +-----------------------------+                  |
|                                                   |
|  Runs the same on ANY computer!                  |
+--------------------------------------------------+
```

### Containers vs Virtual Machines

You might have heard of virtual machines (VMs). Both VMs and containers provide isolation, but they work differently:

```
+--------------------------------------------------+
|  Virtual Machine              Container           |
|                                                   |
|  +-------------+    +-------+ +-------+ +-------+|
|  | App         |    | App 1 | | App 2 | | App 3 ||
|  | Libraries   |    | Libs  | | Libs  | | Libs  ||
|  | Guest OS    |    +-------+ +-------+ +-------+|
|  | (Full Linux)|    |       Docker Engine        ||
|  +-------------+    +----------------------------+|
|  | Hypervisor  |    |       Host OS              ||
|  +-------------+    +----------------------------+|
|  | Host OS     |                                  |
|  +-------------+    Containers share the host OS  |
|                      (much lighter and faster!)   |
|  Each VM has a       Containers start in seconds  |
|  full OS copy        VMs take minutes             |
+--------------------------------------------------+
```

---

## Docker Concepts

Before writing a Dockerfile, let us understand the key terms:

```
+--------------------------------------------------+
|  Docker Vocabulary                                |
|                                                   |
|  Image       = A recipe (blueprint)              |
|  Container   = A cake made from the recipe       |
|  Dockerfile  = The recipe instructions           |
|  Registry    = A recipe book (Docker Hub)        |
|  Volume      = Shared storage between containers |
+--------------------------------------------------+
```

- **Image:** A read-only template. Like a recipe card. It describes what goes into the container.
- **Container:** A running instance of an image. Like a cake baked from the recipe. You can have many cakes from one recipe.
- **Dockerfile:** A text file with instructions to build an image. Like the step-by-step recipe.
- **Registry:** A place to store and share images. Docker Hub is the most popular one, like a cookbook library.

---

## Writing a Dockerfile

A Dockerfile is a series of instructions that tell Docker how to build your image. Each instruction creates a layer, like building a cake layer by layer.

### Dockerfile for an ML API

```dockerfile
# Dockerfile - Instructions to build our ML API container
#
# Think of each line as a step in a recipe:
# 1. Start with a base (like starting with flour)
# 2. Add ingredients (install packages)
# 3. Prepare (copy code, configure)
# 4. Set the final instruction (how to serve)

# ============================================================
# Step 1: Choose a base image
# ============================================================
# python:3.11-slim is a lightweight Python image
# "slim" means it has only the essentials (smaller download)
FROM python:3.11-slim

# ============================================================
# Step 2: Set metadata
# ============================================================
# LABEL adds information about the image
LABEL maintainer="your-email@example.com"
LABEL description="ML Prediction API"

# ============================================================
# Step 3: Set the working directory
# ============================================================
# All subsequent commands run in this directory
# Like saying "cd /app" before doing anything
WORKDIR /app

# ============================================================
# Step 4: Install system dependencies (if needed)
# ============================================================
# Some Python packages need system libraries to compile
# We install them, then clean up to keep the image small
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Step 5: Copy and install Python dependencies
# ============================================================
# We copy requirements.txt FIRST, before the rest of the code.
# Why? Docker caches each layer. If requirements.txt hasn't
# changed, Docker reuses the cached layer and skips the
# slow "pip install" step. This makes rebuilds much faster.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# Step 6: Copy the application code
# ============================================================
COPY src/ ./src/
COPY models/ ./models/
COPY main.py .
COPY config.yaml .

# ============================================================
# Step 7: Set environment variables
# ============================================================
# These can be overridden when running the container
ENV MODEL_PATH=/app/models/trained_model.pkl
ENV MODEL_VERSION=1.0.0
ENV PORT=8000

# ============================================================
# Step 8: Expose the port
# ============================================================
# EXPOSE tells Docker which port the app uses
# It does not actually publish the port (that happens at runtime)
EXPOSE ${PORT}

# ============================================================
# Step 9: Define the startup command
# ============================================================
# CMD is what runs when the container starts
# --host 0.0.0.0 means "accept connections from anywhere"
# (not just localhost)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### The requirements.txt File

```
# requirements.txt - Python packages for the ML API
fastapi==0.104.1
uvicorn==0.24.0
scikit-learn==1.3.2
joblib==1.3.2
numpy==1.26.2
pydantic==2.5.2
pyyaml==6.0.1
```

---

## Building and Running Docker Images

### Building an Image

```bash
# Build the Docker image
# -t gives the image a name (tag)
# . tells Docker to look for the Dockerfile in the current directory
docker build -t ml-api:1.0 .
```

```
Output:
[+] Building 45.2s (12/12) FINISHED
 => [1/7] FROM python:3.11-slim
 => [2/7] WORKDIR /app
 => [3/7] RUN apt-get update && ...
 => [4/7] COPY requirements.txt .
 => [5/7] RUN pip install --no-cache-dir -r requirements.txt
 => [6/7] COPY src/ ./src/
 => [7/7] COPY main.py .
 => exporting to image
 => => naming to docker.io/library/ml-api:1.0
```

### Running a Container

```bash
# Run the container
# -d runs in the background (detached mode)
# -p 8000:8000 maps port 8000 on your computer to port 8000 in the container
# --name gives the container a name for easy reference
docker run -d -p 8000:8000 --name my-ml-api ml-api:1.0
```

```
Output:
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

The long string is the container ID. Your API is now running! Test it:

```bash
curl http://localhost:8000/health
```

```json
{"status": "healthy", "model_loaded": true, "uptime_seconds": 3.45}
```

### Useful Docker Commands

```python
"""
docker_commands.py - A reference for common Docker commands.

This is not a Python script to run, but a reference
showing Docker commands with explanations.
"""

# The commands below are meant to be run in a terminal,
# not in Python. They are shown here for reference.

docker_commands = {
    # Building
    "docker build -t ml-api:1.0 .":
        "Build an image from the Dockerfile in current directory",

    # Running
    "docker run -d -p 8000:8000 ml-api:1.0":
        "Run a container in the background, map port 8000",

    "docker run -it ml-api:1.0 bash":
        "Run a container and open a bash shell inside it",

    # Managing containers
    "docker ps":
        "List running containers",

    "docker ps -a":
        "List ALL containers (including stopped ones)",

    "docker stop my-ml-api":
        "Stop a running container",

    "docker start my-ml-api":
        "Start a stopped container",

    "docker rm my-ml-api":
        "Remove a container (must be stopped first)",

    # Viewing logs
    "docker logs my-ml-api":
        "See the container's output logs",

    "docker logs -f my-ml-api":
        "Follow logs in real-time (like tail -f)",

    # Managing images
    "docker images":
        "List all images on your computer",

    "docker rmi ml-api:1.0":
        "Remove an image",

    # Inspecting
    "docker exec -it my-ml-api bash":
        "Open a shell inside a running container",

    "docker inspect my-ml-api":
        "See detailed info about a container",
}

for cmd, desc in docker_commands.items():
    print(f"  {cmd}")
    print(f"    -> {desc}\n")
```

```
Output:
  docker build -t ml-api:1.0 .
    -> Build an image from the Dockerfile in current directory

  docker run -d -p 8000:8000 ml-api:1.0
    -> Run a container in the background, map port 8000

  docker run -it ml-api:1.0 bash
    -> Run a container and open a bash shell inside it

  docker ps
    -> List running containers

  docker ps -a
    -> List ALL containers (including stopped ones)

  docker stop my-ml-api
    -> Stop a running container

  docker start my-ml-api
    -> Start a stopped container

  docker rm my-ml-api
    -> Remove a container (must be stopped first)

  docker logs my-ml-api
    -> See the container's output logs

  docker logs -f my-ml-api
    -> Follow logs in real-time (like tail -f)

  docker images
    -> List all images on your computer

  docker rmi ml-api:1.0
    -> Remove an image

  docker exec -it my-ml-api bash
    -> Open a shell inside a running container

  docker inspect my-ml-api
    -> See detailed info about a container
```

---

## Optimizing Docker Images for ML

ML Docker images can get very large because of libraries like scikit-learn, PyTorch, and TensorFlow. Here are strategies to keep them small:

### Multi-Stage Builds

```dockerfile
# Dockerfile.multistage - Use multi-stage builds for smaller images
#
# Multi-stage builds use two stages:
# 1. Builder stage: install everything, compile packages
# 2. Final stage: copy only what we need from the builder
#
# Like cooking in a messy prep kitchen, then plating
# the clean final dish in the dining room.

# ============================================================
# Stage 1: Builder (the messy kitchen)
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential

# Install Python packages into a specific directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# Stage 2: Final image (the clean dining room)
# ============================================================
FROM python:3.11-slim

WORKDIR /app

# Copy ONLY the installed packages from the builder
# We do not need build-essential or other build tools
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ ./src/
COPY models/ ./models/
COPY main.py .

ENV MODEL_PATH=/app/models/trained_model.pkl
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### The .dockerignore File

Like `.gitignore`, this file tells Docker what to skip when copying files:

```
# .dockerignore - Files to exclude from Docker builds
# These files are not needed in the container

# Virtual environments
venv/
.venv/
env/

# Python cache
__pycache__/
*.pyc
*.pyo

# Git
.git/
.gitignore

# IDE files
.vscode/
.idea/

# Notebooks (not needed in production)
notebooks/
*.ipynb

# Data files (usually too large for containers)
data/raw/
data/external/

# Logs (containers generate their own)
logs/

# Tests (not needed in production image)
tests/

# Documentation
*.md
docs/
```

---

## Docker Compose

When your application has multiple services (like an API, a database, and a monitoring tool), managing them individually is painful. Docker Compose lets you define and run all services together with a single command.

### docker-compose.yml for ML API

```yaml
# docker-compose.yml - Define multiple services
#
# This file describes all the services your application needs
# and how they connect to each other.

version: "3.8"

services:
  # ============================================================
  # ML API Service
  # ============================================================
  ml-api:
    build:
      context: .                    # Build from current directory
      dockerfile: Dockerfile        # Using this Dockerfile
    container_name: ml-prediction-api
    ports:
      - "8000:8000"                 # Map host:container ports
    environment:
      - MODEL_PATH=/app/models/trained_model.pkl
      - MODEL_VERSION=1.0.0
      - LOG_LEVEL=INFO
    volumes:
      - ./models:/app/models        # Share model files
      - ./logs:/app/logs            # Persist log files
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s                 # Check every 30 seconds
      timeout: 10s                  # Wait max 10 seconds
      retries: 3                    # Fail after 3 retries
    restart: unless-stopped         # Auto-restart if it crashes

  # ============================================================
  # Redis Cache (optional, for caching predictions)
  # ============================================================
  redis:
    image: redis:7-alpine           # Use official Redis image
    container_name: ml-cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data            # Persist Redis data

  # ============================================================
  # Monitoring with Prometheus (optional)
  # ============================================================
  prometheus:
    image: prom/prometheus:latest
    container_name: ml-monitoring
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

# Named volumes persist data between container restarts
volumes:
  redis_data:
```

### Running with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs from all services
docker-compose logs

# View logs from a specific service
docker-compose logs ml-api

# Stop all services
docker-compose down

# Rebuild and start (after code changes)
docker-compose up -d --build
```

```
Output (docker-compose up -d):
Creating network "ml-project_default" with the default driver
Creating ml-cache           ... done
Creating ml-monitoring      ... done
Creating ml-prediction-api  ... done
```

---

## Complete ML API in Docker

Let us put together a complete, production-ready ML application in Docker.

### Project Structure

```
ml-docker-project/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
├── main.py
├── src/
│   ├── __init__.py
│   ├── model.py
│   └── schemas.py
├── models/
│   └── trained_model.pkl
├── scripts/
│   └── train_and_save.py
└── tests/
    └── test_api.py
```

### Complete Training and Saving Script

```python
"""
scripts/train_and_save.py - Train a model and save it for Docker.

Run this BEFORE building the Docker image so the model
file exists when Docker copies it into the container.
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import joblib
import json
import os

# Create sample data
X, y = make_classification(
    n_samples=1000,
    n_features=4,       # age, income, credit_score, employment_years
    n_classes=2,
    random_state=42,
)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42,
)

# Train
model = RandomForestClassifier(
    n_estimators=100, random_state=42
)
model.fit(X_train, y_train)

# Evaluate
accuracy = model.score(X_test, y_test)
print(f"Model accuracy: {accuracy:.4f}")

# Save
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/trained_model.pkl")
print("Model saved to models/trained_model.pkl")

# Save metadata
metadata = {
    "accuracy": accuracy,
    "n_features": 4,
    "feature_names": ["age", "income", "credit_score", "employment_years"],
    "model_type": "RandomForestClassifier",
    "n_estimators": 100,
}

with open("models/metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
print("Metadata saved to models/metadata.json")
```

```
Output:
Model accuracy: 0.9350
Model saved to models/trained_model.pkl
Metadata saved to models/metadata.json
```

### Build and Run the Complete Application

```bash
# Step 1: Train the model (run on your laptop)
python scripts/train_and_save.py

# Step 2: Build the Docker image
docker build -t ml-api:latest .

# Step 3: Run the container
docker run -d -p 8000:8000 --name ml-api ml-api:latest

# Step 4: Test it
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 30, "income": 65000, "credit_score": 720, "employment_years": 5}'

# Step 5: Check logs
docker logs ml-api
```

---

## Common Mistakes

1. **Using a large base image.** Use `python:3.11-slim` instead of `python:3.11`. The slim version is much smaller.

2. **Not using .dockerignore.** Without it, Docker copies unnecessary files (like `.git/`, `data/`, `notebooks/`) into the image, making it huge.

3. **Copying code before requirements.** Always copy `requirements.txt` and install dependencies first. Docker caches this layer, making rebuilds faster.

4. **Running as root.** For security, create a non-root user in your Dockerfile. Root access inside containers is a security risk.

5. **Storing data in containers.** Containers are temporary. Use volumes to persist data that should survive container restarts.

---

## Best Practices

1. **Keep images small.** Use slim base images, multi-stage builds, and .dockerignore.

2. **One service per container.** Do not put your API and database in the same container. Use docker-compose for multiple services.

3. **Use health checks.** They help Docker (and orchestrators like Kubernetes) know when your container is healthy.

4. **Pin dependency versions.** Use `scikit-learn==1.3.2` instead of `scikit-learn` in requirements.txt. This prevents surprise updates.

5. **Use environment variables for configuration.** This lets you change settings without rebuilding the image.

6. **Tag your images with versions.** Use `ml-api:1.0`, `ml-api:1.1`, etc., not just `ml-api:latest`.

---

## Quick Summary

Docker packages your ML application with all its dependencies into a container that runs identically on any machine. A Dockerfile describes how to build the container. Docker Compose manages multiple containers together. This eliminates the "it works on my machine" problem and makes deployment predictable and repeatable.

---

## Key Points

- Containers package code and dependencies together
- Containers are lighter and faster than virtual machines
- A Dockerfile is a recipe for building a container image
- Copy requirements.txt before code for faster rebuilds
- Docker Compose manages multiple services together
- Use volumes to persist data outside containers
- Use .dockerignore to keep images small
- Always use health checks in production

---

## Practice Questions

1. What is the difference between a Docker image and a Docker container?

2. Why do we copy requirements.txt and install dependencies before copying the rest of the code?

3. What is the purpose of the .dockerignore file?

4. Explain what `-p 8000:8000` does when running `docker run`.

5. When would you use docker-compose instead of a single Docker container?

---

## Exercises

### Exercise 1: Build Your First Container

Create a Dockerfile for a simple Python script that prints "Hello from Docker!" and run it as a container.

### Exercise 2: Containerize an ML API

Take the FastAPI ML API from Chapter 3 and:
- Write a Dockerfile for it
- Build the image
- Run it and test the endpoints
- Check the container logs

### Exercise 3: Multi-Service Setup

Create a docker-compose.yml that runs:
- Your ML API on port 8000
- A Redis container on port 6379
- Verify both services start and can communicate

---

## What Is Next?

Your ML API is now containerized and runs consistently on any machine. But your machine is still just your laptop. In Chapter 5, we will learn how to deploy your containerized API to the cloud so it can serve predictions to users anywhere in the world, 24 hours a day, 7 days a week.
