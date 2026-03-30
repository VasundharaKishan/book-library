# Chapter 8: Building Real Application Images

## What You Will Learn

By the end of this chapter, you will be able to:

- Build a complete Docker image for a Node.js Express API
- Build a complete Docker image for a Python Flask API
- Build a complete Docker image for a Java Spring Boot application
- Use multi-stage builds for compiled languages like Java
- Test each containerized application with curl
- Compare image sizes across different languages and approaches
- Understand how project structure affects Dockerfile design

## Why This Chapter Matters

The previous two chapters taught you how to write Dockerfiles and follow best practices. But real applications are messier than simple examples. They have dependencies, configuration files, build steps, and specific runtime requirements.

This chapter bridges the gap between "hello world" Dockerfiles and real production images. You will build three complete applications from scratch, each in a different programming language. By the end, you will have the confidence to Dockerize any application you encounter.

Think of it this way: the previous chapters taught you how to drive a car in a parking lot. This chapter takes you out on the real road with traffic, intersections, and highway merges.

---

## Application 1: Node.js Express API

Express is the most popular web framework for Node.js. Let us build a simple REST API and package it in Docker.

### Project Structure

```
node-api/
+-- Dockerfile
+-- .dockerignore
+-- package.json
+-- package-lock.json
+-- src/
    +-- server.js
    +-- routes/
        +-- users.js
```

### package.json

```json
{
  "name": "node-docker-api",
  "version": "1.0.0",
  "description": "A Node.js Express API in Docker",
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "dev": "nodemon src/server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.1.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
```

A quick explanation of the dependencies:

- **express** -- The web framework that handles HTTP requests
- **cors** -- Middleware that allows cross-origin requests (when your frontend is on a different domain)
- **helmet** -- Middleware that sets security-related HTTP headers
- **nodemon** -- A development tool that restarts the server when code changes (not needed in production)

### src/server.js

```javascript
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const userRoutes = require('./routes/users');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(helmet());
app.use(express.json());

// Routes
app.get('/', (req, res) => {
  res.json({
    service: 'Node.js Express API',
    version: '1.0.0',
    status: 'running'
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', uptime: process.uptime() });
});

app.use('/api/users', userRoutes);

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
```

### src/routes/users.js

```javascript
const express = require('express');
const router = express.Router();

// In-memory data (in a real app, this would be a database)
const users = [
  { id: 1, name: 'Alice', email: 'alice@example.com' },
  { id: 2, name: 'Bob', email: 'bob@example.com' },
  { id: 3, name: 'Charlie', email: 'charlie@example.com' }
];

// GET all users
router.get('/', (req, res) => {
  res.json(users);
});

// GET user by ID
router.get('/:id', (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json(user);
});

module.exports = router;
```

### .dockerignore

```
node_modules
.git
.gitignore
README.md
.DS_Store
*.log
.env
.env.*
coverage
.nyc_output
Dockerfile
docker-compose.yml
```

### Dockerfile

```dockerfile
# Use Node.js 18 on Alpine Linux for a small image
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy dependency files first (for layer caching)
# If these files do not change, npm ci will be cached
COPY package.json package-lock.json ./

# Install ONLY production dependencies
# npm ci is faster and more reliable than npm install
# --only=production skips devDependencies like nodemon
RUN npm ci --only=production

# Copy the application source code
COPY src/ ./src/

# Add a health check so Docker knows if the app is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

# Run as non-root user (node user is built into the node image)
USER node

# Document the port
EXPOSE 3000

# Start the application using exec form
CMD ["node", "src/server.js"]
```

Let us go through each line:

1. `FROM node:18-alpine` -- We use Alpine Linux to keep the image small (~120 MB base instead of ~350 MB).
2. `WORKDIR /app` -- Sets up our working directory inside the container.
3. `COPY package.json package-lock.json ./` -- Copies dependency files first for caching.
4. `RUN npm ci --only=production` -- Installs only the packages needed to run the app (not dev tools like nodemon).
5. `COPY src/ ./src/` -- Copies only the source code, not the entire project directory.
6. `HEALTHCHECK` -- Uses wget (available on Alpine) to check the /health endpoint.
7. `USER node` -- Switches to the built-in non-root user.
8. `EXPOSE 3000` -- Documents the port.
9. `CMD ["node", "src/server.js"]` -- Starts the server.

### Build and Run

```bash
# Build the image
$ docker build -t node-api:1.0 .
[+] Building 12.3s (10/10) FINISHED
 => [internal] load build definition from Dockerfile          0.0s
 => [internal] load .dockerignore                             0.0s
 => [internal] load metadata for docker.io/library/node:18    0.8s
 => [1/4] FROM docker.io/library/node:18-alpine               0.0s
 => [2/4] WORKDIR /app                                        0.0s
 => [3/4] COPY package.json package-lock.json ./               0.0s
 => [4/4] RUN npm ci --only=production                        9.8s
 => [5/5] COPY src/ ./src/                                    0.1s
 => exporting to image                                        1.6s

# Check image size
$ docker images node-api
REPOSITORY   TAG    SIZE
node-api     1.0    135MB

# Run the container
$ docker run -d -p 3000:3000 --name node-api node-api:1.0
a1b2c3d4e5f6...
```

### Test with curl

```bash
# Test the root endpoint
$ curl http://localhost:3000
{
  "service": "Node.js Express API",
  "version": "1.0.0",
  "status": "running"
}

# Test the health endpoint
$ curl http://localhost:3000/health
{
  "status": "healthy",
  "uptime": 12.345
}

# Get all users
$ curl http://localhost:3000/api/users
[
  { "id": 1, "name": "Alice", "email": "alice@example.com" },
  { "id": 2, "name": "Bob", "email": "bob@example.com" },
  { "id": 3, "name": "Charlie", "email": "charlie@example.com" }
]

# Get a specific user
$ curl http://localhost:3000/api/users/1
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com"
}

# Test a non-existent user
$ curl http://localhost:3000/api/users/99
{
  "error": "User not found"
}
```

### Clean Up

```bash
$ docker stop node-api && docker rm node-api
```

---

## Application 2: Python Flask API

Flask is a lightweight web framework for Python. It is simple to learn and widely used for APIs.

### Project Structure

```
python-api/
+-- Dockerfile
+-- .dockerignore
+-- requirements.txt
+-- app/
    +-- __init__.py
    +-- main.py
    +-- routes/
        +-- __init__.py
        +-- books.py
```

### requirements.txt

```
flask==3.0.0
gunicorn==21.2.0
```

A quick explanation:

- **flask** -- The web framework (like Express for Node.js)
- **gunicorn** -- A production-grade web server for Python apps. Flask's built-in server is only meant for development. Gunicorn can handle multiple requests at the same time.

**Real-life analogy:** Flask's built-in server is like a food truck that can serve one customer at a time. Gunicorn is like a full restaurant with multiple waiters serving many customers simultaneously.

### app/main.py

```python
import os
from flask import Flask, jsonify
from app.routes.books import books_bp

def create_app():
    app = Flask(__name__)

    # Register blueprints (groups of related routes)
    app.register_blueprint(books_bp, url_prefix='/api/books')

    @app.route('/')
    def index():
        return jsonify({
            'service': 'Python Flask API',
            'version': '1.0.0',
            'status': 'running'
        })

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### app/\_\_init\_\_.py

```python
# This file makes the app directory a Python package
```

### app/routes/\_\_init\_\_.py

```python
# This file makes the routes directory a Python package
```

### app/routes/books.py

```python
from flask import Blueprint, jsonify, request

books_bp = Blueprint('books', __name__)

# In-memory data
books = [
    {'id': 1, 'title': 'The Docker Book', 'author': 'James Turnbull', 'year': 2014},
    {'id': 2, 'title': 'Kubernetes in Action', 'author': 'Marko Luksa', 'year': 2018},
    {'id': 3, 'title': 'Site Reliability Engineering', 'author': 'Betsy Beyer', 'year': 2016}
]

@books_bp.route('/', methods=['GET'])
def get_books():
    return jsonify(books)

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book)

@books_bp.route('/', methods=['POST'])
def add_book():
    data = request.get_json()
    if not data or 'title' not in data or 'author' not in data:
        return jsonify({'error': 'Title and author are required'}), 400

    new_book = {
        'id': max(b['id'] for b in books) + 1 if books else 1,
        'title': data['title'],
        'author': data['author'],
        'year': data.get('year', 2024)
    }
    books.append(new_book)
    return jsonify(new_book), 201
```

### .dockerignore

```
__pycache__
*.pyc
*.pyo
.git
.gitignore
.venv
venv
env
.env
.env.*
README.md
Dockerfile
docker-compose.yml
*.log
.pytest_cache
.coverage
tests
```

### Dockerfile

```dockerfile
# Use Python 3.11 slim image
# slim is smaller than the full image but has more tools than Alpine
# Python on Alpine can have compatibility issues with some packages
FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: prevents Python from writing .pyc files
# PYTHONUNBUFFERED: ensures print statements appear in Docker logs immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy dependency file first for caching
COPY requirements.txt .

# Install dependencies
# --no-cache-dir: do not save downloaded packages (saves space)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create a non-root user
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

# Health check using wget (available on slim images)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Switch to non-root user
USER appuser

# Document the port
EXPOSE 5000

# Run with gunicorn (production server)
# -w 4: use 4 worker processes
# -b 0.0.0.0:5000: listen on all interfaces, port 5000
# app.main:app: the Flask app is in app/main.py, variable named "app"
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"]
```

Key differences from the Node.js Dockerfile:

1. **Environment variables:** `PYTHONDONTWRITEBYTECODE` and `PYTHONUNBUFFERED` are Python-specific optimizations for containers.
2. **We use `python:3.11-slim` instead of `alpine`:** Python on Alpine can cause issues because Alpine uses `musl` instead of `glibc`. Some Python packages need to be compiled from source on Alpine, which is slow. The `-slim` variant avoids these problems.
3. **Gunicorn instead of Flask's dev server:** In production, you should always use a proper WSGI server like Gunicorn.

### Build and Run

```bash
# Build the image
$ docker build -t python-api:1.0 .
[+] Building 15.1s (11/11) FINISHED
 => [internal] load build definition from Dockerfile          0.0s
 => [internal] load .dockerignore                             0.0s
 => [1/5] FROM docker.io/library/python:3.11-slim             0.0s
 => [2/5] WORKDIR /app                                        0.0s
 => [3/5] COPY requirements.txt .                             0.0s
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt  12.3s
 => [5/5] COPY app/ ./app/                                    0.1s
 => exporting to image                                        2.5s

# Check image size
$ docker images python-api
REPOSITORY    TAG    SIZE
python-api    1.0    155MB

# Run the container
$ docker run -d -p 5000:5000 --name python-api python-api:1.0
b2c3d4e5f6g7...
```

### Test with curl

```bash
# Test root endpoint
$ curl http://localhost:5000
{
  "service": "Python Flask API",
  "version": "1.0.0",
  "status": "running"
}

# Test health endpoint
$ curl http://localhost:5000/health
{
  "status": "healthy"
}

# Get all books
$ curl http://localhost:5000/api/books
[
  {"author": "James Turnbull", "id": 1, "title": "The Docker Book", "year": 2014},
  {"author": "Marko Luksa", "id": 2, "title": "Kubernetes in Action", "year": 2018},
  {"author": "Betsy Beyer", "id": 3, "title": "Site Reliability Engineering", "year": 2016}
]

# Get a specific book
$ curl http://localhost:5000/api/books/2
{
  "author": "Marko Luksa",
  "id": 2,
  "title": "Kubernetes in Action",
  "year": 2018
}

# Add a new book
$ curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Docker Deep Dive", "author": "Nigel Poulton", "year": 2023}'
{
  "author": "Nigel Poulton",
  "id": 4,
  "title": "Docker Deep Dive",
  "year": 2023
}
```

### Clean Up

```bash
$ docker stop python-api && docker rm python-api
```

---

## Application 3: Java Spring Boot (with Multi-Stage Build)

Java applications are different from Node.js and Python because they need to be **compiled** before they can run. This makes multi-stage builds essential.

**Real-life analogy:** Node.js and Python are like reading a book aloud -- you read the source code directly. Java is like translating a book into another language first (compilation), then reading the translation. You need the translation tools during build time, but not when reading the final book.

### Project Structure

```
java-api/
+-- Dockerfile
+-- .dockerignore
+-- pom.xml
+-- src/
    +-- main/
        +-- java/
        |   +-- com/
        |       +-- example/
        |           +-- api/
        |               +-- Application.java
        |               +-- controller/
        |                   +-- ProductController.java
        |                   +-- HealthController.java
        +-- resources/
            +-- application.properties
```

### pom.xml (Maven Build Configuration)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.1</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>docker-api</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

**What is Maven?** Maven is a build tool for Java (like npm for Node.js or pip for Python). The `pom.xml` file lists your dependencies and tells Maven how to build your project.

**What is a JAR?** A JAR (Java ARchive) file is a compiled Java application packaged into a single file. It contains all your code and is what you actually run. Think of it like a compiled executable.

### Application.java

```java
package com.example.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### controller/ProductController.java

```java
package com.example.api.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final List<Map<String, Object>> products = new ArrayList<>(Arrays.asList(
        createProduct(1, "Laptop", 999.99, "Electronics"),
        createProduct(2, "Headphones", 79.99, "Electronics"),
        createProduct(3, "Coffee Maker", 49.99, "Kitchen")
    ));

    @GetMapping
    public List<Map<String, Object>> getAllProducts() {
        return products;
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getProduct(@PathVariable int id) {
        return products.stream()
            .filter(p -> (int) p.get("id") == id)
            .findFirst()
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    private static Map<String, Object> createProduct(
            int id, String name, double price, String category) {
        Map<String, Object> product = new HashMap<>();
        product.put("id", id);
        product.put("name", name);
        product.put("price", price);
        product.put("category", category);
        return product;
    }
}
```

### controller/HealthController.java

```java
package com.example.api.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class HealthController {

    @GetMapping("/")
    public Map<String, String> index() {
        return Map.of(
            "service", "Java Spring Boot API",
            "version", "1.0.0",
            "status", "running"
        );
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "healthy");
    }
}
```

### application.properties

```properties
server.port=8080
management.endpoints.web.exposure.include=health,info
```

### .dockerignore

```
.git
.gitignore
target
*.class
*.jar
*.log
.idea
*.iml
.vscode
README.md
Dockerfile
docker-compose.yml
.env
```

### Dockerfile (Multi-Stage)

This is where Java Dockerfiles really differ from Node.js and Python. We **must** use a multi-stage build because:

1. We need the JDK (Java Development Kit) and Maven to **build** the application
2. We only need the JRE (Java Runtime Environment) to **run** it
3. The JDK + Maven image is ~400 MB, but the JRE Alpine image is ~100 MB

```dockerfile
# ============================================
# Stage 1: Build the application
# ============================================
# Use Maven with JDK 17 to compile the application
# This stage includes build tools we do NOT need in production
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app

# Copy the Maven configuration file first
# This file lists all dependencies
# If it does not change, Maven will use cached dependencies
COPY pom.xml .

# Download all dependencies (cached if pom.xml unchanged)
# go-offline tells Maven to download everything it needs
RUN mvn dependency:go-offline -B

# Copy the source code
COPY src ./src

# Build the application
# -DskipTests: skip running tests during the build
# The result is a JAR file in /app/target/
RUN mvn package -DskipTests -B

# ============================================
# Stage 2: Run the application
# ============================================
# Use only the Java Runtime (JRE), not the full JDK
# Alpine variant for the smallest possible image
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copy ONLY the compiled JAR from the build stage
# The JAR contains everything the app needs to run
COPY --from=builder /app/target/*.jar app.jar

# Create a non-root user
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8080/health || exit 1

# Switch to non-root user
USER appuser

# Document the port
EXPOSE 8080

# Run the JAR file
# java -jar tells Java to run the compiled application
CMD ["java", "-jar", "app.jar"]
```

Key differences from the previous Dockerfiles:

1. **Two FROM instructions:** Stage 1 uses Maven+JDK for building. Stage 2 uses only the JRE for running.
2. **`mvn dependency:go-offline`:** Downloads all dependencies. Like `npm install`, this is cached if `pom.xml` has not changed.
3. **`mvn package`:** Compiles the Java code into a JAR file.
4. **`COPY --from=builder`:** Copies only the compiled JAR from the build stage.
5. **`--start-period=30s`:** Java applications take longer to start than Node.js or Python, so we give them more time.

```
+--------------------------------------------------+
|    Multi-Stage Build for Java                    |
+--------------------------------------------------+
|                                                  |
|    Stage 1: builder (maven:3.9-eclipse-temurin)  |
|    +---------------------------------------+     |
|    | Maven build tools     150 MB          |     |
|    | JDK (full)            250 MB          |     |
|    | Downloaded deps       100 MB          |     |
|    | Source code            1 MB           |     |
|    | Compiled JAR          30 MB  ---+     |     |
|    +---------------------------------------+ |   |
|                                          |   |   |
|                           Only the JAR   |   |   |
|                           gets copied ---+   |   |
|                                              |   |
|    Stage 2: production (temurin:17-jre)      v   |
|    +---------------------------------------+     |
|    | JRE (runtime only)    100 MB          |     |
|    | app.jar               30 MB           |     |
|    +---------------------------------------+     |
|                                                  |
|    Final image: ~130 MB                          |
|    (instead of ~530 MB with single stage)        |
|                                                  |
+--------------------------------------------------+
```

### Build and Run

```bash
# Build the image (this takes longer because Maven downloads dependencies)
$ docker build -t java-api:1.0 .
[+] Building 85.2s (13/13) FINISHED
 => [builder 1/5] FROM maven:3.9-eclipse-temurin-17           5.2s
 => [builder 2/5] WORKDIR /app                                0.0s
 => [builder 3/5] COPY pom.xml .                              0.0s
 => [builder 4/5] RUN mvn dependency:go-offline               45.3s
 => [builder 5/5] COPY src ./src                              0.1s
 => [builder 6/6] RUN mvn package -DskipTests                 25.1s
 => [stage-1 1/3] FROM eclipse-temurin:17-jre-alpine          3.2s
 => [stage-1 2/3] WORKDIR /app                                0.0s
 => [stage-1 3/3] COPY --from=builder /app/target/*.jar ...   0.5s
 => exporting to image                                        5.8s

# Check image size
$ docker images java-api
REPOSITORY   TAG    SIZE
java-api     1.0    195MB

# Run the container
$ docker run -d -p 8080:8080 --name java-api java-api:1.0
c3d4e5f6g7h8...

# Wait a few seconds for Spring Boot to start
# (Java apps take longer to start than Node.js or Python)
```

### Test with curl

```bash
# Test root endpoint
$ curl http://localhost:8080
{
  "service": "Java Spring Boot API",
  "version": "1.0.0",
  "status": "running"
}

# Test health endpoint
$ curl http://localhost:8080/health
{
  "status": "healthy"
}

# Get all products
$ curl http://localhost:8080/api/products
[
  {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
  {"id": 2, "name": "Headphones", "price": 79.99, "category": "Electronics"},
  {"id": 3, "name": "Coffee Maker", "price": 49.99, "category": "Kitchen"}
]

# Get a specific product
$ curl http://localhost:8080/api/products/1
{
  "id": 1,
  "name": "Laptop",
  "price": 999.99,
  "category": "Electronics"
}

# Test non-existent product
$ curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/products/99
404
```

### Clean Up

```bash
$ docker stop java-api && docker rm java-api
```

---

## Image Size Comparison

Now let us compare all three applications:

```bash
$ docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -E "node-api|python-api|java-api"
```

```
+--------------------------------------------------+
|    Image Size Comparison                         |
+--------------------------------------------------+
|                                                  |
|    Application        Image Size   Base Image    |
|    -------------------------------------------   |
|    Node.js Express    ~135 MB      node:18-alpine|
|    Python Flask       ~155 MB      python:3.11-slim|
|    Java Spring Boot   ~195 MB      temurin:17-jre |
|                                                  |
+--------------------------------------------------+
```

### Why the Sizes Differ

```
+--------------------------------------------------+
|    What Makes Up Each Image                      |
+--------------------------------------------------+
|                                                  |
|    Node.js (135 MB):                             |
|    +-- Alpine Linux base        7 MB             |
|    +-- Node.js runtime        110 MB             |
|    +-- npm packages            15 MB             |
|    +-- Application code         3 MB             |
|                                                  |
|    Python (155 MB):                              |
|    +-- Debian slim base        74 MB             |
|    +-- Python runtime          50 MB             |
|    +-- pip packages            28 MB             |
|    +-- Application code         3 MB             |
|                                                  |
|    Java (195 MB):                                |
|    +-- Alpine base              7 MB             |
|    +-- JRE runtime            100 MB             |
|    +-- Spring Boot JAR         85 MB             |
|    +-- Application code         3 MB             |
|                                                  |
+--------------------------------------------------+
```

### Single Stage vs Multi-Stage Comparison (Java)

The Java application benefits the most from multi-stage builds:

```
+--------------------------------------------------+
|    Java: Single Stage vs Multi-Stage             |
+--------------------------------------------------+
|                                                  |
|    Single stage (maven + JDK):  ~530 MB          |
|    Multi-stage (JRE only):      ~195 MB          |
|    Savings:                     ~335 MB (63%)    |
|                                                  |
|    The single stage includes:                    |
|    - Full JDK (not needed at runtime)            |
|    - Maven (not needed at runtime)               |
|    - Downloaded source dependencies              |
|    - Compiled .class files AND the JAR           |
|                                                  |
+--------------------------------------------------+
```

---

## Side-by-Side Dockerfile Comparison

Here is a quick reference comparing the Dockerfile patterns for each language:

```
+-------------------+-------------------+-------------------+
| Node.js           | Python            | Java              |
+-------------------+-------------------+-------------------+
| FROM node:alpine  | FROM python:slim  | FROM maven AS build|
|                   |                   | FROM jre-alpine    |
+-------------------+-------------------+-------------------+
| COPY package.json | COPY requirements | COPY pom.xml      |
| RUN npm ci        | RUN pip install   | RUN mvn deps      |
+-------------------+-------------------+-------------------+
| COPY . .          | COPY app/ ./app/  | COPY src ./src    |
|                   |                   | RUN mvn package   |
+-------------------+-------------------+-------------------+
| USER node         | USER appuser      | USER appuser      |
+-------------------+-------------------+-------------------+
| CMD ["node",...]  | CMD ["gunicorn",.]| CMD ["java","-jar"|
+-------------------+-------------------+-------------------+
| Multi-stage: No   | Multi-stage: No   | Multi-stage: Yes  |
| (interpreted)     | (interpreted)     | (compiled)        |
+-------------------+-------------------+-------------------+
```

Node.js and Python are **interpreted languages** -- the runtime reads and executes the source code directly. Java is a **compiled language** -- you must compile the source code into bytecode first, then the JRE executes the bytecode.

This is why Java benefits most from multi-stage builds: the compilation tools are large and not needed at runtime.

---

## Common Mistakes

### Mistake 1: Using the Development Server in Production

```dockerfile
# BAD: Flask's built-in server cannot handle production traffic
CMD ["python", "app.py"]

# GOOD: Use gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"]
```

### Mistake 2: Not Using Multi-Stage for Java

```dockerfile
# BAD: Final image includes Maven, JDK, and all build tools
FROM maven:3.9-eclipse-temurin-17
COPY . .
RUN mvn package
CMD ["java", "-jar", "target/app.jar"]
# Image size: ~530 MB

# GOOD: Final image has only JRE and the JAR
# (use multi-stage as shown above)
# Image size: ~195 MB
```

### Mistake 3: Copying Everything Instead of What You Need

```dockerfile
# BAD: Copies tests, docs, config files you do not need
COPY . .

# GOOD: Copy only what the application needs
COPY src/ ./src/
COPY package.json package-lock.json ./
```

### Mistake 4: Not Setting PYTHONDONTWRITEBYTECODE

```dockerfile
# BAD: Python writes .pyc files that waste space in the container
FROM python:3.11-slim

# GOOD: Prevent .pyc files and ensure logs appear immediately
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
```

### Mistake 5: Forgetting That Java Takes Longer to Start

```dockerfile
# BAD: Java may not be ready in 5 seconds
HEALTHCHECK --start-period=5s CMD wget ...

# GOOD: Give Java enough time to start
HEALTHCHECK --start-period=30s CMD wget ...
```

---

## Best Practices

1. **Choose the right base image for your language.** Alpine for Node.js, slim for Python, JRE-alpine for Java runtime.

2. **Use multi-stage builds for compiled languages.** Java and Go applications especially benefit from this.

3. **Use production-grade servers.** Gunicorn for Python, not Flask's dev server. In Node.js, Express is fine for production but consider PM2 for process management.

4. **Copy only what you need.** Specify exact files and directories instead of `COPY . .` when possible.

5. **Set language-specific environment variables.** Like `PYTHONDONTWRITEBYTECODE` for Python or `NODE_ENV=production` for Node.js.

6. **Adjust health check timing for your language.** Java needs a longer `--start-period` than Node.js.

7. **Always test your containerized application with curl** before deploying to make sure all endpoints work correctly.

---

## Quick Summary

In this chapter, you built three complete Docker images for real applications:

1. **Node.js Express API** -- Used a single-stage build with `node:18-alpine`, installed dependencies with `npm ci`, and ran with the default Node.js runtime.

2. **Python Flask API** -- Used `python:3.11-slim` with Gunicorn as the production server. Set Python-specific environment variables for container optimization.

3. **Java Spring Boot API** -- Used a multi-stage build with Maven+JDK for compilation and JRE-alpine for runtime. Multi-stage reduced the image size by 63%.

Each application followed best practices: layer caching, non-root users, health checks, and `.dockerignore` files.

---

## Key Points

- Different languages require different Dockerfile patterns
- Compiled languages (Java, Go) benefit most from multi-stage builds
- Always use production-grade servers (Gunicorn for Python, not Flask's dev server)
- Copy dependency files before source code for optimal caching
- Set language-specific environment variables (PYTHONDONTWRITEBYTECODE, NODE_ENV)
- Adjust health check timing based on application startup speed
- Image sizes vary by language: Node.js (~135 MB) < Python (~155 MB) < Java (~195 MB) in our examples
- Multi-stage builds can reduce Java images from ~530 MB to ~195 MB
- Always test endpoints with curl after building and running

---

## Practice Questions

1. Why do we use `python:3.11-slim` instead of `python:3.11-alpine` for the Flask application? What problems can Alpine cause with Python?

2. Explain why Java applications benefit more from multi-stage builds than Node.js or Python applications. What is different about Java?

3. Why do we use Gunicorn instead of Flask's built-in server in the Dockerfile? What is the real-life analogy?

4. In the Java Dockerfile, what does `COPY --from=builder /app/target/*.jar app.jar` do? What would happen if we did not use multi-stage and just had a single FROM?

5. Looking at the image size comparison, what accounts for most of the size in each image? Is it the application code or something else?

---

## Exercises

### Exercise 1: Build and Test All Three

Follow the instructions in this chapter to build and test all three applications. For each one:
1. Create the project structure and files
2. Build the Docker image
3. Run the container
4. Test all endpoints with curl
5. Check the image size with `docker images`
6. Compare the sizes

### Exercise 2: Add a New Endpoint

Choose one of the three applications and add a new endpoint. For example:
- Node.js: Add a `POST /api/users` endpoint that creates a new user
- Python: Add a `DELETE /api/books/:id` endpoint that removes a book
- Java: Add a `PUT /api/products/:id` endpoint that updates a product

Rebuild the image and test the new endpoint.

### Exercise 3: Optimize the Java Image Further

The Java image we built is ~195 MB. Try these optimizations:
1. Use `eclipse-temurin:17-jre-alpine` with jlink to create a custom JRE
2. Add `spring-boot-maven-plugin` layered JAR support
3. Compare the image sizes

---

## What Is Next?

You now know how to build real application images for three popular languages. But building images is only half the story. In the next chapter, you will learn about the container lifecycle -- how containers are created, started, stopped, restarted, and removed. You will learn essential commands for managing containers in development and production.
