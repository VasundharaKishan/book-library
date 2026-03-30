# Chapter 5: Deploying to the Cloud

## What You Will Learn

In this chapter, you will learn:

- What cloud computing is and why it matters for ML
- An overview of AWS, GCP, and Azure (simplified)
- How to deploy your ML API using easy platforms like Render and Railway
- How to use environment variables to manage secrets
- The basics of scaling your application

## Why This Chapter Matters

Your ML API works on your laptop. It runs in Docker. But your laptop is not a server. It shuts down when you close it. It has one internet connection. It cannot handle thousands of users at once.

Cloud deployment is like moving from a food truck to a restaurant chain. The food truck (your laptop) makes great food, but it can only serve a few people in one location. A restaurant chain (the cloud) serves millions of people across many locations, stays open 24/7, and can add more kitchens when demand increases.

---

## What Is Cloud Computing?

Cloud computing means using someone else's computers over the internet. Instead of buying and maintaining your own servers, you rent computing power from companies like Amazon, Google, or Microsoft.

```
+--------------------------------------------------+
|  Your Laptop vs The Cloud                         |
|                                                   |
|  Your Laptop:                                    |
|  - 1 computer                                    |
|  - Shuts down when you close it                  |
|  - Limited internet bandwidth                    |
|  - You maintain everything                       |
|                                                   |
|  The Cloud:                                      |
|  - Thousands of computers available              |
|  - Runs 24/7/365                                 |
|  - Fast internet connections                     |
|  - Provider handles hardware maintenance         |
|  - Pay only for what you use                     |
+--------------------------------------------------+
```

---

## The Big Three Cloud Providers

### Overview

```
+--------------------------------------------------+
|  Cloud Provider Comparison (Simplified)           |
|                                                   |
|  AWS (Amazon Web Services)                       |
|  - Largest cloud provider                        |
|  - Most services available                       |
|  - Complex but powerful                          |
|  - Key ML services: SageMaker, Lambda, EC2       |
|                                                   |
|  GCP (Google Cloud Platform)                     |
|  - Strong in data and ML                         |
|  - Good integration with TensorFlow              |
|  - Key ML services: Vertex AI, Cloud Run, GCE    |
|                                                   |
|  Azure (Microsoft)                               |
|  - Popular with enterprises                      |
|  - Good integration with Microsoft tools         |
|  - Key ML services: Azure ML, Functions, VMs     |
+--------------------------------------------------+
```

### Which Should You Choose?

For beginners, the big three can be overwhelming. They have hundreds of services each. Instead, we will focus on simpler platforms that are built on top of these cloud providers:

```
+--------------------------------------------------+
|  Easy Deployment Platforms                        |
|                                                   |
|  Render     -> Simple, free tier, auto-deploy    |
|  Railway    -> Developer-friendly, fast setup    |
|  Fly.io     -> Global deployment, Docker-native  |
|  HuggingFace Spaces -> ML-specific, free GPUs   |
|                                                   |
|  These platforms handle the complex cloud stuff  |
|  for you. You just push your code.               |
+--------------------------------------------------+
```

---

## Deploying to Render (Step by Step)

Render is one of the easiest platforms for deploying web services. It has a free tier and supports Docker, making it perfect for our ML API.

### Step 1: Prepare Your Project

Make sure your project has these files:

```
ml-api-project/
├── main.py              # Your FastAPI application
├── requirements.txt     # Python dependencies
├── models/
│   └── trained_model.pkl
├── src/
│   ├── __init__.py
│   └── model.py
└── render.yaml          # Render configuration (optional)
```

### Step 2: Create a Start Command

Render needs to know how to start your application. Add a `Procfile` or use Render's dashboard:

```
# Procfile - Tells Render how to start your app
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

The `$PORT` variable is set by Render automatically. Your app must listen on this port.

### Step 3: Configuration for Render

```yaml
# render.yaml - Render deployment configuration
services:
  - type: web
    name: ml-prediction-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MODEL_PATH
        value: models/trained_model.pkl
      - key: MODEL_VERSION
        value: "1.0.0"
      - key: PYTHON_VERSION
        value: "3.11.0"
```

### Step 4: Handling the PORT Variable

Your FastAPI app needs to use the port assigned by the cloud platform:

```python
"""
main_cloud.py - FastAPI app configured for cloud deployment.

Cloud platforms assign a random port through the PORT
environment variable. Your app must use this port.
"""

import os
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="ML API")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/")
def root():
    """
    Root endpoint. Many platforms check this to verify
    your app is running.
    """
    return {
        "message": "ML Prediction API is running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    # Get port from environment variable
    # Default to 8000 for local development
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "main_cloud:app",
        host="0.0.0.0",
        port=port,
    )
```

---

## Deploying to Railway

Railway is another beginner-friendly platform. It can deploy directly from a GitHub repository.

### Step 1: Create a railway.json Configuration

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Step 2: Deploy Process

```
+--------------------------------------------------+
|  Railway Deployment Steps                         |
|                                                   |
|  1. Push code to GitHub                          |
|  2. Connect GitHub repo to Railway               |
|  3. Railway detects Python project                |
|  4. Railway installs requirements.txt             |
|  5. Railway starts your app                      |
|  6. You get a public URL!                        |
|                                                   |
|  Every git push triggers automatic redeployment! |
+--------------------------------------------------+
```

---

## Environment Variables

Environment variables are like sealed envelopes that contain secret information. Your code can read them, but they are not stored in your code files. This is important for keeping passwords, API keys, and other secrets safe.

```
+--------------------------------------------------+
|  Why Environment Variables?                       |
|                                                   |
|  WRONG way (secrets in code):                    |
|  password = "my_secret_123"   # Anyone can see!  |
|                                                   |
|  RIGHT way (environment variables):              |
|  password = os.getenv("DB_PASSWORD")  # Hidden!  |
|                                                   |
|  The actual value is set in the cloud platform's |
|  dashboard, not in your code.                    |
+--------------------------------------------------+
```

### Using Environment Variables in Python

```python
"""
env_config.py - Manage configuration with environment variables.

Environment variables are key-value pairs that are set
outside your code. They are the standard way to handle
secrets and configuration in cloud deployments.
"""

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    """
    Application configuration loaded from environment variables.

    Each setting has a default value for local development
    but can be overridden by setting the environment variable.
    """

    # Model settings
    model_path: str = os.getenv(
        "MODEL_PATH", "models/trained_model.pkl"
    )
    model_version: str = os.getenv(
        "MODEL_VERSION", "1.0.0"
    )

    # Server settings
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Optional: Database connection (if needed)
    database_url: str = os.getenv("DATABASE_URL", "")

    # Optional: API key for authentication
    api_key: str = os.getenv("API_KEY", "")


# Create a global config instance
config = AppConfig()

# Print config (never print secrets in production!)
print(f"Model path: {config.model_path}")
print(f"Model version: {config.model_version}")
print(f"Port: {config.port}")
print(f"Debug mode: {config.debug}")
print(f"Log level: {config.log_level}")
# Do NOT print database_url or api_key!
```

```
Output:
Model path: models/trained_model.pkl
Model version: 1.0.0
Port: 8000
Debug mode: False
Log level: INFO
```

### Setting Environment Variables on Cloud Platforms

Each platform has its own way to set environment variables:

```bash
# Render: Set through the dashboard or render.yaml
# Railway: Set through the dashboard or CLI
railway variables set MODEL_PATH=models/trained_model.pkl
railway variables set MODEL_VERSION=2.0.0

# Docker: Set when running the container
docker run -e MODEL_PATH=/app/models/v2.pkl \
           -e MODEL_VERSION=2.0.0 \
           ml-api:latest

# Local development: Use a .env file
# Create a file called .env (add to .gitignore!)
```

### The .env File for Local Development

```
# .env - Local environment variables
# IMPORTANT: Add .env to .gitignore!

MODEL_PATH=models/trained_model.pkl
MODEL_VERSION=1.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///local.db
API_KEY=local-dev-key-not-for-production
```

```python
"""
load_dotenv_example.py - Load environment variables from .env file.

Install: pip install python-dotenv

This is ONLY for local development. In production,
environment variables are set by the platform.
"""

from dotenv import load_dotenv
import os

# Load variables from .env file into the environment
# This has no effect if the variables are already set
# (e.g., by Docker or the cloud platform)
load_dotenv()

# Now os.getenv() can read values from .env
model_path = os.getenv("MODEL_PATH")
print(f"Model path: {model_path}")
```

```
Output:
Model path: models/trained_model.pkl
```

---

## Basic Scaling

Scaling means handling more users. There are two types:

```
+--------------------------------------------------+
|  Types of Scaling                                 |
|                                                   |
|  Vertical Scaling (Scale Up)                     |
|  = Get a bigger computer                         |
|  Like replacing your bike with a motorcycle      |
|                                                   |
|  Before: 2 CPU, 4 GB RAM                        |
|  After:  8 CPU, 32 GB RAM                        |
|                                                   |
|  Simple but has limits (biggest computer only    |
|  has so much power)                               |
|                                                   |
|  -----------------------------------------------  |
|                                                   |
|  Horizontal Scaling (Scale Out)                  |
|  = Get more computers                            |
|  Like hiring more delivery drivers               |
|                                                   |
|  Before: 1 server                                |
|  After:  5 servers (same size)                   |
|                                                   |
|  More complex but virtually unlimited            |
+--------------------------------------------------+
```

### Scaling on Render

```yaml
# render.yaml - Scaling configuration
services:
  - type: web
    name: ml-prediction-api
    env: python
    plan: standard          # Upgrade from free for more resources
    numInstances: 3         # Run 3 copies (horizontal scaling)
    autoDeploy: true        # Auto-deploy on git push
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4
```

### Using Multiple Workers

```bash
# Run with multiple workers (vertical scaling within one server)
# Each worker handles requests independently
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

```
+--------------------------------------------------+
|  Workers and Instances                            |
|                                                   |
|  Instance 1 (Server 1)                           |
|  +-----------+-----------+                       |
|  | Worker 1  | Worker 2  |                       |
|  +-----------+-----------+                       |
|  | Worker 3  | Worker 4  |                       |
|  +-----------+-----------+                       |
|                                                   |
|  Instance 2 (Server 2)                           |
|  +-----------+-----------+                       |
|  | Worker 1  | Worker 2  |                       |
|  +-----------+-----------+                       |
|  | Worker 3  | Worker 4  |                       |
|  +-----------+-----------+                       |
|                                                   |
|  Total capacity: 8 workers handling requests     |
+--------------------------------------------------+
```

### Key Scaling Considerations for ML

```python
"""
scaling_considerations.py - Things to think about when scaling ML APIs.

This is a reference showing common scaling patterns.
"""

scaling_tips = {
    "Model Loading": {
        "problem": "Each worker loads the model separately",
        "solution": "Use shared memory or model serving (Chapter 7)",
        "memory": "100 MB model x 4 workers = 400 MB RAM needed",
    },
    "Stateless Design": {
        "problem": "Requests may go to different workers/instances",
        "solution": "Do not store state in your API. Each request "
                   "should be independent.",
        "example": "Do not use global variables to count requests. "
                  "Use an external database or Redis instead.",
    },
    "Cold Starts": {
        "problem": "First request is slow (loading model, warming up)",
        "solution": "Keep minimum instances running. Pre-warm with "
                   "health checks.",
    },
    "Memory Limits": {
        "problem": "ML models can use a lot of memory",
        "solution": "Choose instance sizes with enough RAM. "
                   "Consider model compression (ONNX, quantization).",
    },
}

for topic, info in scaling_tips.items():
    print(f"\n{topic}:")
    for key, value in info.items():
        print(f"  {key}: {value}")
```

```
Output:

Model Loading:
  problem: Each worker loads the model separately
  solution: Use shared memory or model serving (Chapter 7)
  memory: 100 MB model x 4 workers = 400 MB RAM needed

Stateless Design:
  problem: Requests may go to different workers/instances
  solution: Do not store state in your API. Each request should be independent.
  example: Do not use global variables to count requests. Use an external database or Redis instead.

Cold Starts:
  problem: First request is slow (loading model, warming up)
  solution: Keep minimum instances running. Pre-warm with health checks.

Memory Limits:
  problem: ML models can use a lot of memory
  solution: Choose instance sizes with enough RAM. Consider model compression (ONNX, quantization).
```

---

## Deployment Checklist

```python
"""
deployment_checklist.py - Verify your app is ready for deployment.

Run this before deploying to catch common issues.
"""

import os
import sys


def check_deployment_readiness():
    """Check if the application is ready for cloud deployment."""
    checks = []

    # Check 1: requirements.txt exists
    has_requirements = os.path.exists("requirements.txt")
    checks.append(("requirements.txt exists", has_requirements))

    # Check 2: Main application file exists
    has_main = os.path.exists("main.py")
    checks.append(("main.py exists", has_main))

    # Check 3: Model file exists
    model_path = os.getenv("MODEL_PATH", "models/trained_model.pkl")
    has_model = os.path.exists(model_path)
    checks.append((f"Model file exists ({model_path})", has_model))

    # Check 4: No hardcoded secrets
    # This is a simple check - in practice use tools like git-secrets
    if has_main:
        with open("main.py") as f:
            content = f.read()
        no_secrets = "password" not in content.lower() or "os.getenv" in content
        checks.append(("No hardcoded secrets in main.py", no_secrets))

    # Check 5: PORT is configurable
    if has_main:
        with open("main.py") as f:
            content = f.read()
        port_configurable = "PORT" in content or "port" in content
        checks.append(("PORT is configurable", port_configurable))

    # Check 6: .env is in .gitignore
    if os.path.exists(".gitignore"):
        with open(".gitignore") as f:
            gitignore = f.read()
        env_ignored = ".env" in gitignore
        checks.append((".env in .gitignore", env_ignored))
    else:
        checks.append((".gitignore exists", False))

    # Print results
    print("Deployment Readiness Check")
    print("=" * 50)
    all_passed = True
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        symbol = "[+]" if passed else "[-]"
        print(f"  {symbol} {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("All checks passed! Ready for deployment.")
    else:
        print("Some checks failed. Fix issues before deploying.")

    return all_passed


check_deployment_readiness()
```

```
Output:
Deployment Readiness Check
==================================================
  [+] requirements.txt exists: PASS
  [+] main.py exists: PASS
  [+] Model file exists (models/trained_model.pkl): PASS
  [+] No hardcoded secrets in main.py: PASS
  [+] PORT is configurable: PASS
  [+] .env in .gitignore: PASS
==================================================
All checks passed! Ready for deployment.
```

---

## Common Mistakes

1. **Hardcoding secrets in code.** Never put passwords, API keys, or tokens directly in your code. Use environment variables.

2. **Not using a health check endpoint.** Cloud platforms need to know if your app is running. Without a health check, they cannot restart it when it fails.

3. **Ignoring the PORT environment variable.** Most cloud platforms assign a port dynamically. Your app must use `os.getenv("PORT")`.

4. **Deploying without testing locally.** Always test your app locally (especially in Docker) before deploying to the cloud.

5. **Including large data files in the deployment.** Only include the model file. Training data should not be in the deployment package.

---

## Best Practices

1. **Start with easy platforms.** Use Render or Railway before trying AWS or GCP directly.

2. **Use environment variables for all configuration.** Never hardcode paths, URLs, keys, or passwords.

3. **Add a health check endpoint.** Return at least `{"status": "healthy"}` and whether the model is loaded.

4. **Set up automatic deploys from GitHub.** Push code, and the platform automatically updates your app.

5. **Monitor your deployment.** Check logs regularly and set up alerts for errors.

6. **Start small, then scale.** Begin with one instance and scale up as needed.

---

## Quick Summary

Cloud deployment makes your ML API available to the world, 24/7. Easy platforms like Render and Railway handle the complex infrastructure for you. Environment variables keep secrets safe. Scaling can be vertical (bigger machines) or horizontal (more machines). Always test locally before deploying, and use health checks so the platform knows your app is running.

---

## Key Points

- Cloud computing means renting computers over the internet
- AWS, GCP, and Azure are the big providers, but Render and Railway are easier to start with
- Environment variables keep secrets out of your code
- The PORT environment variable must be used for cloud deployment
- Vertical scaling means bigger machines; horizontal means more machines
- Always include a health check endpoint
- Test locally with Docker before deploying to the cloud

---

## Practice Questions

1. What is the difference between vertical and horizontal scaling? Give a real-world analogy for each.

2. Why should you never hardcode passwords or API keys in your source code?

3. What is the purpose of the PORT environment variable in cloud deployments?

4. Name two advantages of using a platform like Render compared to setting up your own AWS EC2 instance.

5. What is a "cold start" and how does it affect ML API performance?

---

## Exercises

### Exercise 1: Deploy a Simple API

Deploy the FastAPI hello world application to Render or Railway. Verify it works by visiting the public URL.

### Exercise 2: Environment Variable Configuration

Modify your ML API to read all configuration from environment variables:
- MODEL_PATH, MODEL_VERSION, LOG_LEVEL, MAX_BATCH_SIZE
- Provide sensible defaults for local development
- Test by setting different values

### Exercise 3: Scaling Plan

Write a scaling plan for an ML API that receives:
- 100 requests per day initially
- Expected to grow to 10,000 requests per day in 6 months
- Each prediction takes about 50ms

Include: instance type, number of instances, estimated cost, and when to add more capacity.

---

## What Is Next?

You now know how to deploy your ML API to the cloud. But what if you want to create a visual demo of your model that non-technical people can use? In Chapter 6, we will learn about Streamlit and Gradio, two tools that let you build beautiful interactive demos of your ML models in just a few lines of code.
