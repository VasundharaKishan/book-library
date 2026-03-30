# Chapter 30: Docker and Deployment

## What You Will Learn

- What Docker is and why it matters (the shipping container analogy).
- How to write a Dockerfile with multi-stage builds.
- How to build and run Docker images with `docker build` and `docker run`.
- How to use Docker Compose to run your app with a database.
- How to pass environment variables to Docker containers.
- How to add health checks to your containers.
- How to package your Spring Boot app with `mvn package`.
- How Spring Boot layers work for faster Docker builds.
- What deployment options are available for Spring Boot apps.
- How to set up a basic CI/CD pipeline with GitHub Actions.

## Why This Chapter Matters

You have built a Spring Boot application. It works perfectly on your laptop. But your laptop is not a production server. You need to get your application running on a server where real users can access it.

Here is the problem. You tell your operations team, "Just install Java 17, Maven, set these 12 environment variables, configure the database connection, and run this command." They respond, "It does not work on our server."

This is the classic "it works on my machine" problem. Docker solves it.

Docker packages your application and everything it needs (Java, libraries, configuration) into a single container that runs the same way everywhere. Your laptop, your colleague's laptop, a staging server, a production server. Same container, same behavior.

This chapter teaches you how to containerize your Spring Boot application and deploy it to the real world.

---

## 30.1 What Is Docker? The Shipping Container Analogy

Before shipping containers were invented, loading cargo onto a ship was chaos. Each item had a different shape and size. Barrels, crates, bags, furniture. Workers had to figure out how to pack everything together. It was slow, expensive, and things got damaged.

Then someone invented the shipping container. A standardized metal box. Any cargo goes inside the container. The container fits on any ship, any truck, any train. Nobody cares what is inside. They just move the container.

```
Before Containers (Shipping):        After Containers:

+--ship---------+                    +--ship---------+
| [barrel]      |                    | [container]   |
|   [crate]     |  Messy!            | [container]   |  Clean!
| [bag] [chair] |  Slow!             | [container]   |  Fast!
|  [box]        |  Fragile!          | [container]   |  Reliable!
+---------------+                    +---------------+
```

Docker works the same way for software:

```
Before Docker (Software):            After Docker:

Server needs:                        Server needs:
- Java 17                            - Docker
- Maven
- PostgreSQL driver                  That is it!
- 12 environment variables
- Specific OS libraries              Everything else is inside
- Correct file permissions           the container.
- Prayer

"It works on my machine!"            "It works everywhere."
```

### Docker Vocabulary

| Term | Analogy | Description |
|---|---|---|
| **Image** | Blueprint | A template containing your app and all its dependencies |
| **Container** | Running instance | A running copy of an image (like a process) |
| **Dockerfile** | Recipe | Instructions for building an image |
| **Docker Hub** | App Store | A public repository for sharing images |
| **Volume** | External storage | Persistent data storage outside the container |

```
Dockerfile        docker build       Image          docker run        Container
(recipe)    ------>  (cook)   ------>  (dish)  ------>  (serve)  ------> (running)

You write          Docker reads       A packaged      Docker starts     Your app
instructions       instructions       snapshot        a new instance    is running!
                   and creates        of your app
                   the image
```

---

## 30.2 Installing Docker

Before we continue, make sure Docker is installed on your machine.

### Verify Installation

```bash
docker --version
```

**Output:**

```
Docker version 24.0.7, build afdd53b
```

```bash
docker compose version
```

**Output:**

```
Docker Compose version v2.23.0
```

If Docker is not installed, download Docker Desktop from `https://docs.docker.com/get-docker/`.

---

## 30.3 Building Your Spring Boot App with Maven

Before dockerizing, let us package our application into a JAR file.

### The mvn package Command

```bash
./mvnw clean package -DskipTests
```

This command:
1. **clean**: Deletes the `target/` directory (starts fresh).
2. **package**: Compiles your code, runs tests, and creates a JAR file.
3. **-DskipTests**: Skips tests (for faster builds during development).

**Output:**

```
[INFO] Building BookStore 1.0.0
[INFO] --- spring-boot-maven-plugin:3.4.0:repackage ---
[INFO] Replacing main artifact with repackaged archive
[INFO] BUILD SUCCESS
[INFO] Total time: 8.234 s
```

The JAR file is created at:

```
target/bookstore-1.0.0.jar
```

### Running the JAR

```bash
java -jar target/bookstore-1.0.0.jar
```

This starts your application without Maven or an IDE. The JAR contains everything: your code, all dependencies, and an embedded Tomcat server.

```
What is inside the JAR?

bookstore-1.0.0.jar
  |
  +-- BOOT-INF/
  |     +-- classes/          Your compiled code
  |     +-- lib/              All dependencies (100+ JARs)
  |
  +-- META-INF/
  |     +-- MANIFEST.MF       Points to the main class
  |
  +-- org/springframework/boot/loader/
        +-- JarLauncher.class  Starts the application
```

---

## 30.4 Writing a Dockerfile

A Dockerfile is a text file with instructions for building a Docker image. Think of it as a recipe.

### Simple Dockerfile

```dockerfile
# Dockerfile

# Step 1: Start with a Java 17 base image
FROM eclipse-temurin:17-jre                          # 1

# Step 2: Set the working directory inside the container
WORKDIR /app                                          # 2

# Step 3: Copy the JAR file into the container
COPY target/bookstore-1.0.0.jar app.jar              # 3

# Step 4: Expose the port your app uses
EXPOSE 8080                                           # 4

# Step 5: Define the command to run the application
ENTRYPOINT ["java", "-jar", "app.jar"]               # 5
```

**Line-by-line explanation:**

- **Line 1**: `FROM eclipse-temurin:17-jre` starts with a pre-built image that has Java 17 installed. Think of it as "start with a computer that already has Java."
- **Line 2**: `WORKDIR /app` creates and switches to the `/app` directory inside the container.
- **Line 3**: `COPY target/bookstore-1.0.0.jar app.jar` copies your JAR from your computer into the container.
- **Line 4**: `EXPOSE 8080` documents that the app listens on port 8080. This is informational; it does not actually open the port.
- **Line 5**: `ENTRYPOINT` defines the command that runs when the container starts.

### Multi-Stage Dockerfile (Recommended)

The simple Dockerfile requires you to build the JAR first. A multi-stage Dockerfile builds the JAR inside Docker, so the build is reproducible.

```dockerfile
# Dockerfile (Multi-Stage Build)

# ===== Stage 1: Build =====
FROM eclipse-temurin:17-jdk AS builder                # 1

WORKDIR /app

# Copy Maven wrapper and pom.xml first (for caching)
COPY mvnw .                                           # 2
COPY .mvn .mvn                                        # 3
COPY pom.xml .                                        # 4

# Download dependencies (cached if pom.xml unchanged)
RUN chmod +x mvnw && ./mvnw dependency:resolve        # 5

# Copy source code
COPY src src                                          # 6

# Build the application
RUN ./mvnw clean package -DskipTests                  # 7

# ===== Stage 2: Run =====
FROM eclipse-temurin:17-jre                           # 8

WORKDIR /app

# Copy only the JAR from the build stage
COPY --from=builder /app/target/*.jar app.jar          # 9

# Create a non-root user for security
RUN addgroup --system appgroup && \                   # 10
    adduser --system --ingroup appgroup appuser
USER appuser                                          # 11

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Why two stages?**

```
Stage 1 (Builder):                 Stage 2 (Final):
+-------------------------+       +-------------------------+
| JDK (large, 400MB)     |       | JRE (small, 200MB)     |
| Maven                  |       | app.jar                 |
| Source code             |       |                         |
| Dependencies            |       | That is it!             |
| Compiled classes        |       |                         |
| app.jar                 |       |                         |
+-------------------------+       +-------------------------+
   ~800MB                            ~250MB

The final image is MUCH smaller because it only
contains what is needed to RUN the app.
```

**Key lines explained:**

- **Line 1**: Use the JDK (Java Development Kit) for building. `AS builder` names this stage.
- **Line 2-4**: Copy Maven files first. Docker caches layers, so if `pom.xml` does not change, dependencies are not re-downloaded.
- **Line 5**: Download all dependencies. This layer is cached.
- **Line 6**: Copy your source code. This changes frequently, so it is a separate layer.
- **Line 7**: Build the JAR inside Docker.
- **Line 8**: Start a new stage with only the JRE (Java Runtime Environment). Much smaller.
- **Line 9**: `COPY --from=builder` copies the JAR from the first stage to the second stage.
- **Line 10-11**: Create a non-root user. Never run containers as root in production.

### Docker Caching Strategy

```
Layers that change RARELY (cached):
  FROM eclipse-temurin:17-jdk
  COPY pom.xml .
  RUN ./mvnw dependency:resolve    <-- Only re-runs if pom.xml changes

Layers that change OFTEN (rebuilt):
  COPY src src                     <-- Changes with every code change
  RUN ./mvnw clean package         <-- Rebuilds the JAR

Result: Fast rebuilds! Only your code is recompiled.
```

---

## 30.5 Building and Running Docker Images

### Building the Image

```bash
docker build -t bookstore:1.0 .
```

- `-t bookstore:1.0`: Tags the image with a name and version.
- `.`: Use the current directory (where the Dockerfile is).

**Output:**

```
[+] Building 45.2s (14/14) FINISHED
 => [builder 1/6] FROM eclipse-temurin:17-jdk
 => [builder 2/6] COPY mvnw .
 => [builder 3/6] COPY .mvn .mvn
 => [builder 4/6] COPY pom.xml .
 => [builder 5/6] RUN ./mvnw dependency:resolve
 => [builder 6/6] COPY src src
 => [builder 7/7] RUN ./mvnw clean package -DskipTests
 => [stage-1 1/3] FROM eclipse-temurin:17-jre
 => [stage-1 2/3] COPY --from=builder /app/target/*.jar app.jar
 => [stage-1 3/3] RUN addgroup --system appgroup ...
 => exporting to image
 => => naming to docker.io/library/bookstore:1.0
```

### Running the Container

```bash
docker run -p 8080:8080 bookstore:1.0
```

- `-p 8080:8080`: Maps port 8080 on your machine to port 8080 in the container.

```
Port Mapping:

Your Machine                    Docker Container
+------------------+           +------------------+
| localhost:8080   |---------->| container:8080   |
| (you access      |   -p     | (app listens     |
|  this port)      | mapping  |  on this port)    |
+------------------+           +------------------+
```

Now visit `http://localhost:8080/api/books` and your app is running inside Docker.

### Running in the Background

```bash
# Run in detached mode (background)
docker run -d -p 8080:8080 --name bookstore bookstore:1.0
```

- `-d`: Detached mode (runs in background).
- `--name bookstore`: Give the container a name.

### Useful Docker Commands

```bash
# List running containers
docker ps

# View container logs
docker logs bookstore

# Follow logs in real-time
docker logs -f bookstore

# Stop a container
docker stop bookstore

# Remove a container
docker rm bookstore

# List all images
docker images

# Remove an image
docker rmi bookstore:1.0
```

---

## 30.6 Passing Environment Variables

In Chapter 29, you learned about externalized configuration. Docker makes passing environment variables easy.

### Using -e Flag

```bash
docker run -d -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=prod \
  -e DB_HOST=prod-database.example.com \
  -e DB_PORT=5432 \
  -e DB_USERNAME=bookstore_user \
  -e DB_PASSWORD=superSecretPassword \
  -e JWT_SECRET=myProductionJwtSecret \
  --name bookstore \
  bookstore:1.0
```

### Using an Environment File

For many variables, use a file:

```bash
# docker.env
SPRING_PROFILES_ACTIVE=prod
DB_HOST=prod-database.example.com
DB_PORT=5432
DB_USERNAME=bookstore_user
DB_PASSWORD=superSecretPassword
JWT_SECRET=myProductionJwtSecret
```

```bash
docker run -d -p 8080:8080 \
  --env-file docker.env \
  --name bookstore \
  bookstore:1.0
```

> **Important**: Add `docker.env` to your `.gitignore`. Never commit environment files with secrets.

### JVM Options

You can pass JVM options through environment variables:

```bash
docker run -d -p 8080:8080 \
  -e JAVA_OPTS="-Xms256m -Xmx512m" \
  --name bookstore \
  bookstore:1.0
```

Update your ENTRYPOINT to use JAVA_OPTS:

```dockerfile
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

---

## 30.7 Docker Compose

Docker Compose lets you define and run multiple containers together. Your application needs a database? Define both in one file.

### docker-compose.yml

```yaml
# docker-compose.yml

version: '3.8'                                        # 1

services:
  # ===== Database Service =====
  database:                                            # 2
    image: postgres:16                                 # 3
    container_name: bookstore-db
    environment:                                       # 4
      POSTGRES_DB: bookstore
      POSTGRES_USER: bookstore_user
      POSTGRES_PASSWORD: bookstore_password
    ports:
      - "5432:5432"                                    # 5
    volumes:
      - db-data:/var/lib/postgresql/data               # 6
    healthcheck:                                       # 7
      test: ["CMD-SHELL",
             "pg_isready -U bookstore_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ===== Application Service =====
  app:                                                 # 8
    build: .                                           # 9
    container_name: bookstore-app
    ports:
      - "8080:8080"
    environment:                                       # 10
      SPRING_PROFILES_ACTIVE: prod
      DB_HOST: database                                # 11
      DB_PORT: 5432
      DB_USERNAME: bookstore_user
      DB_PASSWORD: bookstore_password
      JWT_SECRET: myDockerComposeSecret
    depends_on:                                        # 12
      database:
        condition: service_healthy                     # 13
    healthcheck:                                       # 14
      test: ["CMD", "curl", "-f",
             "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s                                # 15

volumes:                                               # 16
  db-data:
```

**Line-by-line explanation:**

- **Line 1**: Docker Compose file version.
- **Line 2**: Define a service called "database".
- **Line 3**: Use the official PostgreSQL 16 image.
- **Line 4**: Set environment variables for PostgreSQL (database name, user, password).
- **Line 5**: Map port 5432 so you can connect from your machine.
- **Line 6**: Mount a volume for persistent data. Without this, data is lost when the container stops.
- **Line 7**: Health check that runs `pg_isready` every 10 seconds.
- **Line 8**: Define the application service.
- **Line 9**: `build: .` means "build the image from the Dockerfile in the current directory."
- **Line 10**: Environment variables for the Spring Boot app.
- **Line 11**: `DB_HOST: database` uses the service name as the hostname. Docker networking resolves this automatically.
- **Line 12**: `depends_on` means the app waits for the database.
- **Line 13**: `condition: service_healthy` waits until the database health check passes.
- **Line 14**: Health check for the Spring Boot app using the Actuator endpoint.
- **Line 15**: `start_period` gives the app 40 seconds to start before health checks begin.
- **Line 16**: Named volume for database persistence.

```
Docker Compose Network:

+---docker-compose-network-------------------+
|                                            |
|  +----------+       +------------------+  |
|  | database |       | app              |  |
|  | :5432    |<------| :8080            |  |
|  |          |  DNS  |                  |  |
|  | Postgres |  name | Spring Boot      |  |
|  +----------+  =    +------------------+  |
|               "database"                   |
+--------------------------------------------+

External Access:
  localhost:8080 -> app container
  localhost:5432 -> database container
```

### Docker Compose Commands

```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# Build and start (rebuild images)
docker compose up --build

# View logs
docker compose logs

# Follow logs for a specific service
docker compose logs -f app

# Stop all services
docker compose down

# Stop and remove volumes (deletes database data!)
docker compose down -v

# Check status
docker compose ps
```

### Testing with Docker Compose

```bash
# Start everything
docker compose up -d --build

# Wait for the app to be healthy
docker compose ps

# Test the API
curl http://localhost:8080/api/books

# Check health
curl http://localhost:8080/actuator/health

# View app logs
docker compose logs -f app

# Shut down
docker compose down
```

---

## 30.8 Health Checks in Docker

Health checks tell Docker whether your container is working properly. Without health checks, Docker only knows if the process is running, not if it is actually healthy.

```
Without Health Check:                With Health Check:

Container Status:                   Container Status:
  "Running"                           "Healthy" or "Unhealthy"

Docker knows:                       Docker knows:
  "Process is alive"                  "App is responding to requests"

Problem: App might be frozen         Docker can restart unhealthy
but process is still running.        containers automatically.
```

### Health Check in Dockerfile

```dockerfile
# Add to your Dockerfile
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --retries=3 \
            --start-period=40s \
    CMD curl -f http://localhost:8080/actuator/health || exit 1
```

Make sure curl is available in your image. If not, use wget or a Java-based check:

```dockerfile
# Alternative: Use wget (available in most images)
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --retries=3 \
    CMD wget -qO- http://localhost:8080/actuator/health || exit 1
```

### Health Check Parameters

| Parameter | Default | Description |
|---|---|---|
| `--interval` | 30s | Time between health checks |
| `--timeout` | 30s | Maximum time for a health check to complete |
| `--retries` | 3 | How many failures before marking "unhealthy" |
| `--start-period` | 0s | Grace period for the app to start |

---

## 30.9 Spring Boot Layers for Faster Docker Builds

Spring Boot 3 supports a layered JAR format that makes Docker builds much faster by taking advantage of Docker's layer caching.

### The Problem

Every time you change one line of code, Docker rebuilds the entire JAR layer, even though your dependencies (100+ MB) have not changed.

### The Solution: Layered JARs

Spring Boot splits the JAR into layers:

```
Layer 1: dependencies         (rarely changes)     ~100 MB
Layer 2: spring-boot-loader   (rarely changes)     ~1 MB
Layer 3: snapshot-dependencies (sometimes changes)  ~5 MB
Layer 4: application          (changes often)       ~1 MB

Docker caches layers 1-3. Only layer 4 is rebuilt.
Result: Builds go from 2 minutes to 5 seconds!
```

### Dockerfile with Layers

```dockerfile
# Dockerfile with Spring Boot Layers

# ===== Stage 1: Build =====
FROM eclipse-temurin:17-jdk AS builder
WORKDIR /app
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .
RUN chmod +x mvnw && ./mvnw dependency:resolve
COPY src src
RUN ./mvnw clean package -DskipTests

# ===== Stage 2: Extract Layers =====
FROM eclipse-temurin:17-jdk AS extractor                # 1
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
RUN java -Djarmode=layertools -jar app.jar extract      # 2

# ===== Stage 3: Run =====
FROM eclipse-temurin:17-jre
WORKDIR /app

# Copy layers in order (least to most frequently changing)
COPY --from=extractor /app/dependencies/ ./              # 3
COPY --from=extractor /app/spring-boot-loader/ ./        # 4
COPY --from=extractor /app/snapshot-dependencies/ ./     # 5
COPY --from=extractor /app/application/ ./               # 6

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8080

ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]  # 7
```

- **Line 1-2**: Extract the JAR into layers using Spring Boot's built-in tool.
- **Line 3-6**: Copy each layer separately. Docker caches unchanged layers.
- **Line 7**: Use `JarLauncher` instead of `java -jar` since the app is no longer a single JAR.

---

## 30.10 Deployment Options

There are many ways to deploy a Spring Boot application. Here are the most common:

```
+--------------------------------------------------+
|               Deployment Options                  |
+--------------------------------------------------+
|                                                  |
|  Simple:                                         |
|    1. JAR on a VPS (DigitalOcean, Linode)       |
|    2. Docker on a VPS                            |
|                                                  |
|  Platform as a Service (PaaS):                   |
|    3. Heroku / Railway / Render                  |
|    4. AWS Elastic Beanstalk                      |
|    5. Google App Engine                          |
|    6. Azure App Service                          |
|                                                  |
|  Container Orchestration:                        |
|    7. AWS ECS / Fargate                          |
|    8. Google Cloud Run                           |
|    9. Kubernetes (EKS, GKE, AKS)                |
|                                                  |
|  Complexity ------>                               |
|  Simple                            Enterprise    |
+--------------------------------------------------+
```

### Option 1: JAR on a VPS (Simplest)

```bash
# On your server
# 1. Install Java
sudo apt update && sudo apt install -y openjdk-17-jre-headless

# 2. Copy the JAR to the server
scp target/bookstore-1.0.0.jar user@server:/opt/bookstore/

# 3. Run the application
java -jar /opt/bookstore/bookstore-1.0.0.jar \
  --spring.profiles.active=prod
```

### Option 2: Docker on a VPS

```bash
# On your server
# 1. Install Docker
curl -fsSL https://get.docker.com | sh

# 2. Copy docker-compose.yml and Dockerfile
scp docker-compose.yml Dockerfile user@server:/opt/bookstore/

# 3. Start the application
cd /opt/bookstore
docker compose up -d --build
```

### Option 3: Cloud Run (Serverless Containers)

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/my-project/bookstore

# Deploy to Cloud Run
gcloud run deploy bookstore \
  --image gcr.io/my-project/bookstore \
  --port 8080 \
  --allow-unauthenticated
```

---

## 30.11 CI/CD with GitHub Actions

CI/CD (Continuous Integration / Continuous Deployment) automates building, testing, and deploying your application every time you push code.

```
Developer pushes code
        |
        v
+---GitHub Actions-------------------+
|                                    |
|  1. Checkout code                  |
|  2. Set up Java 17                 |
|  3. Run tests                      |
|  4. Build Docker image             |
|  5. Push to registry               |
|  6. Deploy to server               |
|                                    |
+------------------------------------+
        |
        v
Application is live!
```

### Basic CI Pipeline

```yaml
# .github/workflows/ci.yml

name: CI Pipeline                                      # 1

on:                                                    # 2
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:                                      # 3
    runs-on: ubuntu-latest                             # 4

    steps:
      - name: Checkout code                            # 5
        uses: actions/checkout@v4

      - name: Set up Java 17                           # 6
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'                               # 7

      - name: Run tests                                # 8
        run: ./mvnw test

      - name: Build application                        # 9
        run: ./mvnw clean package -DskipTests
```

**Line-by-line explanation:**

- **Line 1**: Name of the workflow (shown in GitHub UI).
- **Line 2**: Trigger on pushes to `main` and on pull requests targeting `main`.
- **Line 3**: Define a job called "build-and-test".
- **Line 4**: Run on the latest Ubuntu virtual machine.
- **Line 5**: Check out the repository code.
- **Line 6**: Install Java 17 (Temurin distribution).
- **Line 7**: Cache Maven dependencies for faster builds.
- **Line 8**: Run all tests.
- **Line 9**: Build the application JAR.

### CI/CD Pipeline with Docker

```yaml
# .github/workflows/ci-cd.yml

name: CI/CD Pipeline

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Java 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: Run tests
        run: ./mvnw test

  build-and-push:
    needs: test                                        # 1
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Log in to Docker Hub                     # 2
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}      # 3
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Docker image              # 4
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/bookstore:latest
            ${{ secrets.DOCKER_USERNAME }}/bookstore:${{ github.sha }}

  deploy:
    needs: build-and-push                              # 5
    runs-on: ubuntu-latest

    steps:
      - name: Deploy to server                         # 6
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            docker pull ${{ secrets.DOCKER_USERNAME }}/bookstore:latest
            docker compose down
            docker compose up -d
```

- **Line 1**: `needs: test` means this job only runs if tests pass.
- **Line 2-3**: Log in to Docker Hub using secrets stored in GitHub.
- **Line 4**: Build the Docker image and push it to Docker Hub.
- **Line 5**: Deploy only after the image is built and pushed.
- **Line 6**: SSH into the server and pull the latest image.

### Setting Up GitHub Secrets

In your GitHub repository, go to Settings > Secrets and variables > Actions, and add:

| Secret | Value |
|---|---|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | Your Docker Hub password or access token |
| `SERVER_HOST` | Your server's IP address |
| `SERVER_USER` | SSH username |
| `SERVER_SSH_KEY` | SSH private key |

```
GitHub Actions Flow:

   Push to main
       |
       v
  +----+----+
  |  Test   |  Run ./mvnw test
  |  Job    |  All tests must pass
  +----+----+
       |
       v (only if tests pass)
  +----+----+
  |  Build  |  docker build
  |  & Push |  docker push
  +----+----+
       |
       v (only if push succeeds)
  +----+----+
  | Deploy  |  SSH to server
  |  Job    |  docker pull & restart
  +---------+
```

---

## 30.12 A .dockerignore File

Just like `.gitignore` keeps files out of Git, `.dockerignore` keeps files out of Docker builds.

```dockerignore
# .dockerignore

# Build artifacts
target/
!target/*.jar

# IDE files
.idea/
.vscode/
*.iml

# Git
.git/
.gitignore

# Docker
docker-compose.yml
Dockerfile

# Environment files (NEVER include in image!)
.env
*.env

# Documentation
*.md
docs/

# Test files
src/test/
```

Without `.dockerignore`, Docker copies everything into the build context, making builds slower and images larger.

---

## Common Mistakes

### Mistake 1: Running Containers as Root

```dockerfile
# WRONG: Running as root (security risk)
FROM eclipse-temurin:17-jre
COPY app.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
# Runs as root by default!
```

```dockerfile
# CORRECT: Create and use a non-root user
FROM eclipse-temurin:17-jre
RUN addgroup --system app && adduser --system --ingroup app app
USER app
COPY app.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Mistake 2: Using latest Tag in Production

```bash
# WRONG: "latest" can change without warning
docker pull bookstore:latest
```

```bash
# CORRECT: Use specific versions
docker pull bookstore:1.0.0
# OR use the Git commit SHA
docker pull bookstore:abc123f
```

### Mistake 3: Storing Data Inside Containers

```yaml
# WRONG: Data is lost when container is removed
services:
  database:
    image: postgres:16
    # No volume! Data is gone when container stops.
```

```yaml
# CORRECT: Use volumes for persistent data
services:
  database:
    image: postgres:16
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:  # Named volume persists across restarts
```

### Mistake 4: No Health Checks

```yaml
# WRONG: No health check
services:
  app:
    build: .
    ports:
      - "8080:8080"
    # Docker has no idea if the app is healthy
```

```yaml
# CORRECT: Add a health check
services:
  app:
    build: .
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "-f",
             "http://localhost:8080/actuator/health"]
      interval: 30s
      retries: 3
```

### Mistake 5: Not Using Multi-Stage Builds

```dockerfile
# WRONG: JDK in final image (400MB larger than needed)
FROM eclipse-temurin:17-jdk
COPY target/app.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
# Image: ~600MB (includes compiler, not needed at runtime)
```

```dockerfile
# CORRECT: Use JRE in final image
FROM eclipse-temurin:17-jre
COPY target/app.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
# Image: ~250MB (only runtime, much smaller)
```

---

## Best Practices

1. **Use multi-stage builds.** Keep your final image small by separating the build stage from the run stage.

2. **Never run containers as root.** Create a dedicated user in your Dockerfile.

3. **Use specific version tags.** Avoid `latest` in production. Use semantic versions or Git SHAs.

4. **Add health checks.** Docker and orchestrators need to know if your app is healthy.

5. **Use Docker Compose for local development.** Define your app, database, and other services in one file.

6. **Use volumes for persistent data.** Database data must survive container restarts.

7. **Add a `.dockerignore` file.** Keep builds fast and images clean.

8. **Use CI/CD pipelines.** Automate testing, building, and deployment with GitHub Actions.

9. **Set memory limits.** Use `-Xms` and `-Xmx` JVM flags to control memory usage inside containers.

10. **Keep secrets out of images.** Use environment variables or secrets managers. Never bake secrets into Docker images.

---

## Quick Summary

In this chapter, you learned how to containerize and deploy your Spring Boot application. You started with the Docker shipping container analogy and understood why Docker solves the "it works on my machine" problem. You wrote Dockerfiles, starting with a simple version and progressing to optimized multi-stage builds. You built and ran Docker images with `docker build` and `docker run`. You used Docker Compose to run your application with a PostgreSQL database. You passed environment variables to configure your containerized app. You added health checks so Docker knows when your app is truly healthy. You learned about Spring Boot's layered JAR format for faster Docker builds. You explored deployment options from simple VPS hosting to cloud platforms. Finally, you set up a CI/CD pipeline with GitHub Actions to automate the entire build-test-deploy process.

---

## Key Points

| Concept | Description |
|---|---|
| Docker | Packages your app and dependencies into portable containers |
| Dockerfile | Instructions for building a Docker image |
| Multi-stage build | Two-phase build: compile in stage 1, run in stage 2 (smaller image) |
| `docker build` | Creates an image from a Dockerfile |
| `docker run` | Starts a container from an image |
| Docker Compose | Defines and runs multi-container applications |
| `-p 8080:8080` | Maps a host port to a container port |
| `-e VAR=value` | Passes environment variables to a container |
| Volume | Persistent storage that survives container restarts |
| Health check | Lets Docker know if your app is actually healthy |
| `mvn package` | Builds a runnable JAR file |
| Spring Boot layers | Splits the JAR for faster Docker caching |
| GitHub Actions | Automates CI/CD pipelines (test, build, deploy) |
| `.dockerignore` | Excludes files from the Docker build context |

---

## Practice Questions

1. Explain the Docker shipping container analogy. How does Docker solve the "it works on my machine" problem?

2. What is the difference between a Docker image and a Docker container? How do you create each one?

3. Why should you use multi-stage builds in your Dockerfile? What are the two stages, and what goes in each one?

4. In a `docker-compose.yml` file, how does the Spring Boot app connect to the database? Why can you use the service name as the hostname?

5. What is the purpose of a health check in Docker? What happens to a container that fails its health check?

---

## Exercises

### Exercise 1: Dockerize a Simple App

Create a simple Spring Boot application with a `/hello` endpoint. Write a multi-stage Dockerfile, build the image, and run it. Verify you can access the endpoint at `http://localhost:8080/hello`.

### Exercise 2: Docker Compose with Database

Extend Exercise 1 by adding a PostgreSQL database using Docker Compose. Create a `Book` entity and REST API. Configure the app to connect to the PostgreSQL container. Verify that:
- The app starts after the database is healthy.
- You can create and retrieve books through the API.
- Data persists after stopping and restarting the containers (using volumes).

### Exercise 3: CI/CD Pipeline

Set up a GitHub Actions workflow that:
1. Runs tests on every push to `main` and on pull requests.
2. Builds a Docker image when tests pass.
3. Tags the image with the Git commit SHA.
4. Pushes the image to Docker Hub (you will need a free Docker Hub account).

Verify by pushing a commit and checking that the workflow completes successfully.

---

## What Is Next?

Congratulations! You have completed the main chapters of this book. You now know how to build, test, document, monitor, configure, and deploy Spring Boot applications. You have the skills to build production-ready applications from scratch.

Check out the appendices for additional topics like WebSockets, a complete project walkthrough, and a glossary of terms. Keep building, keep learning, and keep shipping great software.
