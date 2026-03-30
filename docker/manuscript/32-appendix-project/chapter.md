# Appendix B: Complete Project — Microservices App

## What You Will Learn

In this appendix, you will learn:

- How to build a complete microservices application from scratch
- How to write Dockerfiles for Node.js, Python, and Java services
- How to wire everything together with Docker Compose
- How to deploy the same application to Kubernetes
- How all the concepts from this book come together in a real project

## Why This Chapter Matters

Throughout this book, you have learned Docker concepts one at a time — like learning individual musical notes. Now it is time to play a full song. This appendix walks you through building, connecting, and deploying a complete application made of multiple services, just like professional teams do every day.

By the end, you will have a working microservices application that you built, tested locally, and deployed to Kubernetes. This is not a toy example. It is the same architecture pattern used by companies like Netflix, Uber, and Spotify.

```
+------------------------------------------------------------------+
|                    WHAT WE ARE BUILDING                           |
|                                                                   |
|   Browser / Client                                                |
|        │                                                          |
|        ▼                                                          |
|   ┌──────────────────────────────────────────┐                    |
|   │           API Gateway (Nginx)            │                    |
|   │           Port 80                        │                    |
|   └─────┬──────────────┬──────────────┬──────┘                    |
|         │              │              │                           |
|         ▼              ▼              ▼                           |
|   ┌──────────┐  ┌──────────┐  ┌──────────┐                      |
|   │  User    │  │ Product  │  │  Order   │                      |
|   │ Service  │  │ Service  │  │ Service  │                      |
|   │ (Node.js)│  │ (Python) │  │  (Java)  │                      |
|   │ Port 3001│  │ Port 5000│  │ Port 8080│                      |
|   └────┬─────┘  └────┬─────┘  └────┬─────┘                      |
|        │              │              │                           |
|        ▼              ▼              ▼                           |
|   ┌──────────────────────────────────────────┐                    |
|   │           PostgreSQL Database            │                    |
|   │           Port 5432                      │                    |
|   └──────────────────────────────────────────┘                    |
|                        │                                          |
|   ┌──────────────────────────────────────────┐                    |
|   │           Redis Cache                    │                    |
|   │           Port 6379                      │                    |
|   └──────────────────────────────────────────┘                    |
+------------------------------------------------------------------+
```

---

## Project Structure

First, let us set up the folder structure. Think of each service as its own mini-project living in its own folder.

```bash
mkdir -p microservices-app/{user-service,product-service,order-service,api-gateway,k8s,db}
cd microservices-app
```

Your project will look like this:

```
microservices-app/
├── docker-compose.yml
├── api-gateway/
│   └── nginx.conf
├── user-service/
│   ├── Dockerfile
│   ├── package.json
│   └── server.js
├── product-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── order-service/
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/
│       └── main/
│           └── java/
│               └── com/
│                   └── orders/
│                       └── OrderServiceApplication.java
├── db/
│   └── init.sql
└── k8s/
    ├── namespace.yaml
    ├── postgres.yaml
    ├── redis.yaml
    ├── user-service.yaml
    ├── product-service.yaml
    ├── order-service.yaml
    └── api-gateway.yaml
```

---

## Step 1: The Database

Every application needs data. We will use PostgreSQL and initialize it with tables for all three services.

### db/init.sql

```sql
-- Create databases for each service
CREATE DATABASE userdb;
CREATE DATABASE productdb;
CREATE DATABASE orderdb;

-- Connect to userdb and create tables
\c userdb;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, email) VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com');

-- Connect to productdb and create tables
\c productdb;

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (name, description, price, stock) VALUES
    ('Laptop', 'High-performance laptop', 999.99, 50),
    ('Headphones', 'Wireless noise-canceling headphones', 149.99, 200),
    ('Keyboard', 'Mechanical keyboard with RGB', 79.99, 150),
    ('Mouse', 'Ergonomic wireless mouse', 49.99, 300);

-- Connect to orderdb and create tables
\c orderdb;

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    total_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
    (1, 1, 1, 999.99, 'completed'),
    (2, 2, 2, 299.98, 'pending'),
    (1, 3, 1, 79.99, 'shipped');
```

This single SQL file creates three separate databases — one for each service. This is a common pattern in microservices: each service owns its own data.

```
+----------------------------------------------+
|         ONE POSTGRES, THREE DATABASES         |
|                                               |
|  ┌────────────┐ ┌────────────┐ ┌──────────┐  |
|  │  userdb    │ │ productdb  │ │ orderdb  │  |
|  │            │ │            │ │          │  |
|  │  users     │ │  products  │ │  orders  │  |
|  │  table     │ │  table     │ │  table   │  |
|  └────────────┘ └────────────┘ └──────────┘  |
|                                               |
|         PostgreSQL Server (port 5432)         |
+----------------------------------------------+
```

---

## Step 2: User Service (Node.js)

The User Service manages user accounts. We will build it with Node.js and Express.

### user-service/package.json

```json
{
  "name": "user-service",
  "version": "1.0.0",
  "description": "User microservice",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "pg": "^8.11.3",
    "redis": "^4.6.10"
  }
}
```

### user-service/server.js

```javascript
const express = require('express');
const { Pool } = require('pg');
const { createClient } = require('redis');

const app = express();
app.use(express.json());

// PostgreSQL connection
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'userdb',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
});

// Redis connection
let redisClient;

async function connectRedis() {
  redisClient = createClient({
    url: `redis://${process.env.REDIS_HOST || 'localhost'}:${process.env.REDIS_PORT || 6379}`,
  });
  redisClient.on('error', (err) => console.log('Redis error:', err.message));
  await redisClient.connect();
  console.log('Connected to Redis');
}

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'user-service' });
});

// Get all users
app.get('/api/users', async (req, res) => {
  try {
    // Check Redis cache first
    const cached = await redisClient.get('users:all');
    if (cached) {
      console.log('Returning users from cache');
      return res.json(JSON.parse(cached));
    }

    // Query database
    const result = await pool.query('SELECT * FROM users ORDER BY id');

    // Cache for 60 seconds
    await redisClient.setEx('users:all', 60, JSON.stringify(result.rows));

    console.log('Returning users from database');
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching users:', error.message);
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

// Get user by ID
app.get('/api/users/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Check cache
    const cached = await redisClient.get(`users:${id}`);
    if (cached) {
      return res.json(JSON.parse(cached));
    }

    const result = await pool.query('SELECT * FROM users WHERE id = $1', [id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    await redisClient.setEx(`users:${id}`, 60, JSON.stringify(result.rows[0]));
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error fetching user:', error.message);
    res.status(500).json({ error: 'Failed to fetch user' });
  }
});

// Create a new user
app.post('/api/users', async (req, res) => {
  try {
    const { username, email } = req.body;
    const result = await pool.query(
      'INSERT INTO users (username, email) VALUES ($1, $2) RETURNING *',
      [username, email]
    );

    // Invalidate cache
    await redisClient.del('users:all');

    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Error creating user:', error.message);
    res.status(500).json({ error: 'Failed to create user' });
  }
});

// Start server
const PORT = process.env.PORT || 3001;

async function start() {
  await connectRedis();
  app.listen(PORT, () => {
    console.log(`User Service running on port ${PORT}`);
  });
}

start();
```

### user-service/Dockerfile

```dockerfile
# Stage 1: Install dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Production image
FROM node:18-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy dependencies and source code
COPY --from=deps /app/node_modules ./node_modules
COPY server.js .
COPY package.json .

# Switch to non-root user
USER appuser

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3001/health || exit 1

CMD ["node", "server.js"]
```

Let us break down why this Dockerfile is structured this way:

```
+---------------------------------------------------+
|        MULTI-STAGE BUILD EXPLAINED                 |
|                                                    |
|  Stage 1 (deps):                                   |
|  ┌──────────────────────────────────┐              |
|  │  Full Node.js + npm              │              |
|  │  Install ALL dependencies        │              |
|  │  This stage is thrown away        │              |
|  └──────────────────────────────────┘              |
|                    │                               |
|                    │ copy node_modules              |
|                    ▼                               |
|  Stage 2 (production):                             |
|  ┌──────────────────────────────────┐              |
|  │  Slim Node.js (no npm needed)    │              |
|  │  Only production dependencies    │              |
|  │  Non-root user (security)        │              |
|  │  Health check built in           │              |
|  │  MUCH smaller final image        │              |
|  └──────────────────────────────────┘              |
+---------------------------------------------------+
```

---

## Step 3: Product Service (Python Flask)

The Product Service manages the product catalog. We will build it with Python and Flask.

### product-service/requirements.txt

```
flask==3.0.0
psycopg2-binary==2.9.9
redis==5.0.1
gunicorn==21.2.0
```

### product-service/app.py

```python
import os
import json
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import redis

app = Flask(__name__)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', 5432),
        database=os.environ.get('DB_NAME', 'productdb'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        cursor_factory=RealDictCursor
    )

# Redis connection
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    decode_responses=True
)


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'product-service'})


@app.route('/api/products', methods=['GET'])
def get_products():
    # Check cache
    cached = redis_client.get('products:all')
    if cached:
        app.logger.info('Returning products from cache')
        return jsonify(json.loads(cached))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products ORDER BY id')
    products = cur.fetchall()
    cur.close()
    conn.close()

    # Convert Decimal to float for JSON serialization
    products_list = []
    for p in products:
        product = dict(p)
        product['price'] = float(product['price'])
        product['created_at'] = str(product['created_at'])
        products_list.append(product)

    # Cache for 60 seconds
    redis_client.setex('products:all', 60, json.dumps(products_list))

    app.logger.info('Returning products from database')
    return jsonify(products_list)


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # Check cache
    cached = redis_client.get(f'products:{product_id}')
    if cached:
        return jsonify(json.loads(cached))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cur.fetchone()
    cur.close()
    conn.close()

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    product = dict(product)
    product['price'] = float(product['price'])
    product['created_at'] = str(product['created_at'])

    redis_client.setex(f'products:{product_id}', 60, json.dumps(product))
    return jsonify(product)


@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO products (name, description, price, stock) '
        'VALUES (%s, %s, %s, %s) RETURNING *',
        (data['name'], data.get('description', ''),
         data['price'], data.get('stock', 0))
    )
    product = dict(cur.fetchone())
    conn.commit()
    cur.close()
    conn.close()

    product['price'] = float(product['price'])
    product['created_at'] = str(product['created_at'])

    # Invalidate cache
    redis_client.delete('products:all')

    return jsonify(product), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### product-service/Dockerfile

```dockerfile
# Stage 1: Install dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim
WORKDIR /app

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app.py .

# Switch to non-root user
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
```

---

## Step 4: Order Service (Java Spring Boot)

The Order Service handles order creation and tracking. We will build it with Java and Spring Boot.

### order-service/pom.xml

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

    <groupId>com.orders</groupId>
    <artifactId>order-service</artifactId>
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
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
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

### order-service/src/main/resources/application.yml

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:orderdb}
    username: ${DB_USER:postgres}
    password: ${DB_PASSWORD:postgres}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: none
    show-sql: false
  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: ${REDIS_PORT:6379}

management:
  endpoints:
    web:
      exposure:
        include: health
  endpoint:
    health:
      show-details: always
```

### order-service/src/main/java/com/orders/OrderServiceApplication.java

```java
package com.orders;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}
```

### order-service/src/main/java/com/orders/model/Order.java

```java
package com.orders.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "orders")
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "product_id", nullable = false)
    private Long productId;

    @Column(nullable = false)
    private Integer quantity = 1;

    @Column(name = "total_price", nullable = false)
    private BigDecimal totalPrice;

    @Column(length = 50)
    private String status = "pending";

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }

    public Integer getQuantity() { return quantity; }
    public void setQuantity(Integer quantity) { this.quantity = quantity; }

    public BigDecimal getTotalPrice() { return totalPrice; }
    public void setTotalPrice(BigDecimal totalPrice) { this.totalPrice = totalPrice; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
```

### order-service/src/main/java/com/orders/repository/OrderRepository.java

```java
package com.orders.repository;

import com.orders.model.Order;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByUserIdOrderByCreatedAtDesc(Long userId);
    List<Order> findByStatusOrderByCreatedAtDesc(String status);
}
```

### order-service/src/main/java/com/orders/controller/OrderController.java

```java
package com.orders.controller;

import com.orders.model.Order;
import com.orders.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class OrderController {

    @Autowired
    private OrderRepository orderRepository;

    @GetMapping("/health")
    public Map<String, String> health() {
        Map<String, String> status = new HashMap<>();
        status.put("status", "healthy");
        status.put("service", "order-service");
        return status;
    }

    @GetMapping("/api/orders")
    public List<Order> getAllOrders() {
        return orderRepository.findAll();
    }

    @GetMapping("/api/orders/{id}")
    public ResponseEntity<?> getOrder(@PathVariable Long id) {
        return orderRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/api/orders/user/{userId}")
    public List<Order> getOrdersByUser(@PathVariable Long userId) {
        return orderRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    @PostMapping("/api/orders")
    public ResponseEntity<Order> createOrder(@RequestBody Order order) {
        order.setStatus("pending");
        Order saved = orderRepository.save(order);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    @PutMapping("/api/orders/{id}/status")
    public ResponseEntity<?> updateStatus(
            @PathVariable Long id,
            @RequestBody Map<String, String> body) {
        return orderRepository.findById(id)
                .map(order -> {
                    order.setStatus(body.get("status"));
                    orderRepository.save(order);
                    return ResponseEntity.ok(order);
                })
                .orElse(ResponseEntity.notFound().build());
    }
}
```

### order-service/Dockerfile

```dockerfile
# Stage 1: Build the application
FROM maven:3.9-eclipse-temurin-17-alpine AS builder
WORKDIR /app
COPY pom.xml .
# Download dependencies first (cached if pom.xml doesn't change)
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests -B

# Stage 2: Production image
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy the built JAR from the builder stage
COPY --from=builder /app/target/*.jar app.jar

# Switch to non-root user
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
```

Notice that the Java Dockerfile has a longer `start-period` in the health check. Java applications take longer to start up than Node.js or Python.

```
+---------------------------------------------------+
|     JAVA MULTI-STAGE BUILD                         |
|                                                    |
|  Stage 1 (builder) ~500MB:                         |
|  ┌──────────────────────────────────┐              |
|  │  Full JDK + Maven               │              |
|  │  All source code                 │              |
|  │  All build tools                 │              |
|  │  Compiles to a single JAR file   │              |
|  └──────────────────────────────────┘              |
|                    │                               |
|                    │ copy app.jar only              |
|                    ▼                               |
|  Stage 2 (production) ~200MB:                      |
|  ┌──────────────────────────────────┐              |
|  │  JRE only (no compiler needed)   │              |
|  │  Just the JAR file               │              |
|  │  Non-root user                   │              |
|  │  60% smaller than Stage 1        │              |
|  └──────────────────────────────────┘              |
+---------------------------------------------------+
```

---

## Step 5: API Gateway (Nginx)

The API Gateway is the front door. All requests from the outside world come through here, and Nginx routes them to the correct service.

### api-gateway/nginx.conf

```nginx
upstream user_service {
    server user-service:3001;
}

upstream product_service {
    server product-service:5000;
}

upstream order_service {
    server order-service:8080;
}

server {
    listen 80;
    server_name localhost;

    # Health check for the gateway itself
    location /health {
        return 200 '{"status": "healthy", "service": "api-gateway"}';
        add_header Content-Type application/json;
    }

    # Route user requests to the User Service
    location /api/users {
        proxy_pass http://user_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Route product requests to the Product Service
    location /api/products {
        proxy_pass http://product_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Route order requests to the Order Service
    location /api/orders {
        proxy_pass http://order_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Default: return info about available endpoints
    location / {
        return 200 '{
            "service": "microservices-api-gateway",
            "endpoints": {
                "users": "/api/users",
                "products": "/api/products",
                "orders": "/api/orders",
                "health": "/health"
            }
        }';
        add_header Content-Type application/json;
    }
}
```

Here is how routing works:

```
+---------------------------------------------------+
|              HOW THE GATEWAY ROUTES                |
|                                                    |
|  Request: GET /api/users                           |
|     └──> Nginx sees "/api/users"                   |
|          └──> Forward to user-service:3001         |
|                                                    |
|  Request: GET /api/products/1                      |
|     └──> Nginx sees "/api/products"                |
|          └──> Forward to product-service:5000      |
|                                                    |
|  Request: POST /api/orders                         |
|     └──> Nginx sees "/api/orders"                  |
|          └──> Forward to order-service:8080        |
|                                                    |
|  The client only talks to port 80.                 |
|  It never knows about the internal services.       |
+---------------------------------------------------+
```

---

## Step 6: Docker Compose — Bringing It All Together

Now we wire everything together with a single `docker-compose.yml` file. This is the orchestra conductor.

### docker-compose.yml

```yaml
version: '3.8'

services:
  # ──────────────────────────────────────────────
  # Infrastructure Services
  # ──────────────────────────────────────────────

  postgres:
    image: postgres:16-alpine
    container_name: microservices-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - microservices-network

  redis:
    image: redis:7-alpine
    container_name: microservices-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - microservices-network

  # ──────────────────────────────────────────────
  # Application Services
  # ──────────────────────────────────────────────

  user-service:
    build:
      context: ./user-service
      dockerfile: Dockerfile
    container_name: microservices-user-service
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: userdb
      DB_USER: postgres
      DB_PASSWORD: postgres
      REDIS_HOST: redis
      REDIS_PORT: 6379
      PORT: 3001
    ports:
      - "3001:3001"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - microservices-network
    restart: unless-stopped

  product-service:
    build:
      context: ./product-service
      dockerfile: Dockerfile
    container_name: microservices-product-service
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: productdb
      DB_USER: postgres
      DB_PASSWORD: postgres
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - microservices-network
    restart: unless-stopped

  order-service:
    build:
      context: ./order-service
      dockerfile: Dockerfile
    container_name: microservices-order-service
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: orderdb
      DB_USER: postgres
      DB_PASSWORD: postgres
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - microservices-network
    restart: unless-stopped

  # ──────────────────────────────────────────────
  # API Gateway
  # ──────────────────────────────────────────────

  api-gateway:
    image: nginx:1.25-alpine
    container_name: microservices-api-gateway
    ports:
      - "80:80"
    volumes:
      - ./api-gateway/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - user-service
      - product-service
      - order-service
    networks:
      - microservices-network
    restart: unless-stopped

# ──────────────────────────────────────────────
# Volumes (persistent data)
# ──────────────────────────────────────────────

volumes:
  postgres-data:
  redis-data:

# ──────────────────────────────────────────────
# Networks
# ──────────────────────────────────────────────

networks:
  microservices-network:
    driver: bridge
```

Let us understand the startup order:

```
+---------------------------------------------------+
|            STARTUP ORDER (depends_on)              |
|                                                    |
|  Step 1:  postgres + redis start                   |
|           (they have no dependencies)              |
|                │                                   |
|                │ wait until healthy                 |
|                ▼                                   |
|  Step 2:  user-service + product-service            |
|           + order-service start                    |
|           (they need postgres and redis)           |
|                │                                   |
|                │ wait until running                 |
|                ▼                                   |
|  Step 3:  api-gateway starts                       |
|           (it needs all three services)            |
+---------------------------------------------------+
```

---

## Step 7: Build and Test Locally

Now let us build and run everything.

### Build all images

```bash
docker compose build
```

```
[+] Building 45.2s (35/35) FINISHED
 => [user-service] Building...
 => [product-service] Building...
 => [order-service] Building...
```

### Start all services

```bash
docker compose up -d
```

```
[+] Running 6/6
 ✔ Network microservices-app_microservices-network  Created
 ✔ Container microservices-postgres                 Started
 ✔ Container microservices-redis                    Started
 ✔ Container microservices-user-service             Started
 ✔ Container microservices-product-service          Started
 ✔ Container microservices-order-service            Started
 ✔ Container microservices-api-gateway              Started
```

### Check that everything is running

```bash
docker compose ps
```

```
NAME                            IMAGE                    STATUS                   PORTS
microservices-api-gateway       nginx:1.25-alpine        Up 30 seconds            0.0.0.0:80->80/tcp
microservices-order-service     order-service:latest      Up 30 seconds (healthy)  0.0.0.0:8080->8080/tcp
microservices-postgres          postgres:16-alpine        Up 45 seconds (healthy)  0.0.0.0:5432->5432/tcp
microservices-product-service   product-service:latest    Up 30 seconds (healthy)  0.0.0.0:5000->5000/tcp
microservices-redis             redis:7-alpine            Up 45 seconds (healthy)  0.0.0.0:6379->6379/tcp
microservices-user-service      user-service:latest       Up 30 seconds (healthy)  0.0.0.0:3001->3001/tcp
```

### Test the API Gateway

```bash
# Check the gateway itself
curl http://localhost/health
```

```json
{"status": "healthy", "service": "api-gateway"}
```

### Test the User Service

```bash
# Get all users (through the gateway)
curl http://localhost/api/users
```

```json
[
  {"id": 1, "username": "alice", "email": "alice@example.com", "created_at": "2024-01-15T10:30:00.000Z"},
  {"id": 2, "username": "bob", "email": "bob@example.com", "created_at": "2024-01-15T10:30:00.000Z"},
  {"id": 3, "username": "charlie", "email": "charlie@example.com", "created_at": "2024-01-15T10:30:00.000Z"}
]
```

```bash
# Create a new user
curl -X POST http://localhost/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "diana", "email": "diana@example.com"}'
```

```json
{"id": 4, "username": "diana", "email": "diana@example.com", "created_at": "2024-01-15T11:00:00.000Z"}
```

### Test the Product Service

```bash
# Get all products
curl http://localhost/api/products
```

```json
[
  {"id": 1, "name": "Laptop", "description": "High-performance laptop", "price": 999.99, "stock": 50},
  {"id": 2, "name": "Headphones", "description": "Wireless noise-canceling headphones", "price": 149.99, "stock": 200},
  {"id": 3, "name": "Keyboard", "description": "Mechanical keyboard with RGB", "price": 79.99, "stock": 150},
  {"id": 4, "name": "Mouse", "description": "Ergonomic wireless mouse", "price": 49.99, "stock": 300}
]
```

### Test the Order Service

```bash
# Get all orders
curl http://localhost/api/orders
```

```json
[
  {"id": 1, "userId": 1, "productId": 1, "quantity": 1, "totalPrice": 999.99, "status": "completed"},
  {"id": 2, "userId": 2, "productId": 2, "quantity": 2, "totalPrice": 299.98, "status": "pending"},
  {"id": 3, "userId": 1, "productId": 3, "quantity": 1, "totalPrice": 79.99, "status": "shipped"}
]
```

```bash
# Create a new order
curl -X POST http://localhost/api/orders \
  -H "Content-Type: application/json" \
  -d '{"userId": 3, "productId": 4, "quantity": 2, "totalPrice": 99.98}'
```

```json
{"id": 4, "userId": 3, "productId": 4, "quantity": 2, "totalPrice": 99.98, "status": "pending"}
```

### View logs

```bash
# See logs from all services
docker compose logs

# Follow logs from a specific service
docker compose logs -f user-service
```

### Stop everything

```bash
docker compose down
```

---

## Step 8: Kubernetes Manifests

Now let us deploy the same application to Kubernetes. We need to translate our Compose file into Kubernetes YAML manifests.

```
+---------------------------------------------------+
|    COMPOSE vs KUBERNETES TRANSLATION               |
|                                                    |
|    Compose                 Kubernetes              |
|    ───────                 ──────────              |
|    service:          -->   Deployment + Service     |
|    ports:            -->   Service (type: NodePort) |
|    environment:      -->   ConfigMap or Secret      |
|    volumes:          -->   PersistentVolumeClaim    |
|    depends_on:       -->   (handled by readiness    |
|                             probes and retry logic) |
|    networks:         -->   (built-in networking)    |
+---------------------------------------------------+
```

### k8s/namespace.yaml

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: microservices
  labels:
    app: microservices-demo
```

### k8s/postgres.yaml

```yaml
# ConfigMap for initialization SQL
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-init
  namespace: microservices
data:
  init.sql: |
    CREATE DATABASE userdb;
    CREATE DATABASE productdb;
    CREATE DATABASE orderdb;

    \c userdb;
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO users (username, email) VALUES
        ('alice', 'alice@example.com'),
        ('bob', 'bob@example.com'),
        ('charlie', 'charlie@example.com');

    \c productdb;
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        stock INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO products (name, description, price, stock) VALUES
        ('Laptop', 'High-performance laptop', 999.99, 50),
        ('Headphones', 'Wireless noise-canceling headphones', 149.99, 200),
        ('Keyboard', 'Mechanical keyboard with RGB', 79.99, 150),
        ('Mouse', 'Ergonomic wireless mouse', 49.99, 300);

    \c orderdb;
    CREATE TABLE orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        total_price DECIMAL(10, 2) NOT NULL,
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
        (1, 1, 1, 999.99, 'completed'),
        (2, 2, 2, 299.98, 'pending'),
        (1, 3, 1, 79.99, 'shipped');
---
# Secret for database credentials
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: microservices
type: Opaque
stringData:
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
---
# PersistentVolumeClaim for data storage
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: microservices
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: microservices
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
                name: postgres-secret
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
            - name: init-scripts
              mountPath: /docker-entrypoint-initdb.d
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "postgres"]
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            exec:
              command: ["pg_isready", "-U", "postgres"]
            initialDelaySeconds: 15
            periodSeconds: 20
      volumes:
        - name: postgres-data
          persistentVolumeClaim:
            claimName: postgres-pvc
        - name: init-scripts
          configMap:
            name: postgres-init
---
# Service (so other pods can reach PostgreSQL)
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: microservices
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
  type: ClusterIP
```

### k8s/redis.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: microservices
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
          readinessProbe:
            exec:
              command: ["redis-cli", "ping"]
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            exec:
              command: ["redis-cli", "ping"]
            initialDelaySeconds: 15
            periodSeconds: 20
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: microservices
spec:
  selector:
    app: redis
  ports:
    - port: 6379
      targetPort: 6379
  type: ClusterIP
```

### k8s/user-service.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: user-service-config
  namespace: microservices
data:
  DB_HOST: postgres
  DB_PORT: "5432"
  DB_NAME: userdb
  DB_USER: postgres
  REDIS_HOST: redis
  REDIS_PORT: "6379"
  PORT: "3001"
---
apiVersion: v1
kind: Secret
metadata:
  name: user-service-secret
  namespace: microservices
type: Opaque
stringData:
  DB_PASSWORD: postgres
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: microservices
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
        - name: user-service
          image: user-service:1.0
          ports:
            - containerPort: 3001
          envFrom:
            - configMapRef:
                name: user-service-config
            - secretRef:
                name: user-service-secret
          readinessProbe:
            httpGet:
              path: /health
              port: 3001
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 3001
            initialDelaySeconds: 10
            periodSeconds: 20
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 250m
              memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: microservices
spec:
  selector:
    app: user-service
  ports:
    - port: 3001
      targetPort: 3001
  type: ClusterIP
```

### k8s/product-service.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: product-service-config
  namespace: microservices
data:
  DB_HOST: postgres
  DB_PORT: "5432"
  DB_NAME: productdb
  DB_USER: postgres
  REDIS_HOST: redis
  REDIS_PORT: "6379"
---
apiVersion: v1
kind: Secret
metadata:
  name: product-service-secret
  namespace: microservices
type: Opaque
stringData:
  DB_PASSWORD: postgres
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-service
  namespace: microservices
spec:
  replicas: 2
  selector:
    matchLabels:
      app: product-service
  template:
    metadata:
      labels:
        app: product-service
    spec:
      containers:
        - name: product-service
          image: product-service:1.0
          ports:
            - containerPort: 5000
          envFrom:
            - configMapRef:
                name: product-service-config
            - secretRef:
                name: product-service-secret
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 10
            periodSeconds: 20
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 250m
              memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: product-service
  namespace: microservices
spec:
  selector:
    app: product-service
  ports:
    - port: 5000
      targetPort: 5000
  type: ClusterIP
```

### k8s/order-service.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-service-config
  namespace: microservices
data:
  DB_HOST: postgres
  DB_PORT: "5432"
  DB_NAME: orderdb
  DB_USER: postgres
  REDIS_HOST: redis
  REDIS_PORT: "6379"
---
apiVersion: v1
kind: Secret
metadata:
  name: order-service-secret
  namespace: microservices
type: Opaque
stringData:
  DB_PASSWORD: postgres
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  namespace: microservices
spec:
  replicas: 2
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
        - name: order-service
          image: order-service:1.0
          ports:
            - containerPort: 8080
          envFrom:
            - configMapRef:
                name: order-service-config
            - secretRef:
                name: order-service-secret
          readinessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 60
            periodSeconds: 20
          resources:
            requests:
              cpu: 200m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: order-service
  namespace: microservices
spec:
  selector:
    app: order-service
  ports:
    - port: 8080
      targetPort: 8080
  type: ClusterIP
```

### k8s/api-gateway.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: microservices
data:
  default.conf: |
    upstream user_service {
        server user-service:3001;
    }
    upstream product_service {
        server product-service:5000;
    }
    upstream order_service {
        server order-service:8080;
    }
    server {
        listen 80;
        server_name localhost;

        location /health {
            return 200 '{"status": "healthy", "service": "api-gateway"}';
            add_header Content-Type application/json;
        }
        location /api/users {
            proxy_pass http://user_service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        location /api/products {
            proxy_pass http://product_service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        location /api/orders {
            proxy_pass http://order_service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        location / {
            return 200 '{"service": "microservices-api-gateway", "endpoints": {"users": "/api/users", "products": "/api/products", "orders": "/api/orders"}}';
            add_header Content-Type application/json;
        }
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: microservices
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
        - name: nginx
          image: nginx:1.25-alpine
          ports:
            - containerPort: 80
          volumeMounts:
            - name: nginx-config
              mountPath: /etc/nginx/conf.d
          readinessProbe:
            httpGet:
              path: /health
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 20
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 100m
              memory: 128Mi
      volumes:
        - name: nginx-config
          configMap:
            name: nginx-config
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: microservices
spec:
  selector:
    app: api-gateway
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
  type: NodePort
```

---

## Step 9: Deploy to Kubernetes

Now let us deploy the same application to Kubernetes, step by step.

### Build and tag images for Kubernetes

If you are using Minikube, you need to point your Docker client to Minikube's Docker daemon:

```bash
# For Minikube users
eval $(minikube docker-env)
```

Build the images:

```bash
docker build -t user-service:1.0 ./user-service/
docker build -t product-service:1.0 ./product-service/
docker build -t order-service:1.0 ./order-service/
```

### Create the namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

```
namespace/microservices created
```

### Deploy infrastructure first

```bash
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
```

```
configmap/postgres-init created
secret/postgres-secret created
persistentvolumeclaim/postgres-pvc created
deployment.apps/postgres created
service/postgres created
deployment.apps/redis created
service/redis created
```

Wait for infrastructure to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=postgres -n microservices --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n microservices --timeout=120s
```

```
pod/postgres-7d4b8c9f-x2k9 condition met
pod/redis-5c6d7e8f-j4k2 condition met
```

### Deploy application services

```bash
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/product-service.yaml
kubectl apply -f k8s/order-service.yaml
kubectl apply -f k8s/api-gateway.yaml
```

```
configmap/user-service-config created
secret/user-service-secret created
deployment.apps/user-service created
service/user-service created
configmap/product-service-config created
secret/product-service-secret created
deployment.apps/product-service created
service/product-service created
configmap/order-service-config created
secret/order-service-secret created
deployment.apps/order-service created
service/order-service created
configmap/nginx-config created
deployment.apps/api-gateway created
service/api-gateway created
```

### Verify everything is running

```bash
kubectl get all -n microservices
```

```
NAME                                   READY   STATUS    RESTARTS   AGE
pod/api-gateway-6b8c9d-m3p7            1/1     Running   0          60s
pod/api-gateway-6b8c9d-x2k9            1/1     Running   0          60s
pod/order-service-7d4b8c-j4k2          1/1     Running   0          65s
pod/order-service-7d4b8c-n5o6          1/1     Running   0          65s
pod/postgres-5c6d7e-p7q8               1/1     Running   0          90s
pod/product-service-8e9f0a-r9s0        1/1     Running   0          70s
pod/product-service-8e9f0a-t1u2        1/1     Running   0          70s
pod/redis-4b5c6d-v3w4                  1/1     Running   0          85s
pod/user-service-9f0a1b-x5y6           1/1     Running   0          75s
pod/user-service-9f0a1b-z7a8           1/1     Running   0          75s

NAME                       TYPE        CLUSTER-IP      PORT(S)        AGE
service/api-gateway        NodePort    10.96.100.1     80:30080/TCP   60s
service/order-service      ClusterIP   10.96.100.2     8080/TCP       65s
service/postgres           ClusterIP   10.96.100.3     5432/TCP       90s
service/product-service    ClusterIP   10.96.100.4     5000/TCP       70s
service/redis              ClusterIP   10.96.100.5     6379/TCP       85s
service/user-service       ClusterIP   10.96.100.6     3001/TCP       75s

NAME                              READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/api-gateway       2/2     2            2           60s
deployment.apps/order-service     2/2     2            2           65s
deployment.apps/postgres          1/1     1            1           90s
deployment.apps/product-service   2/2     2            2           70s
deployment.apps/redis             1/1     1            1           85s
deployment.apps/user-service      2/2     2            2           75s
```

### Test the Kubernetes deployment

```bash
# For Minikube
minikube service api-gateway -n microservices --url
```

```
http://192.168.49.2:30080
```

```bash
# Test the endpoints
curl http://192.168.49.2:30080/api/users
curl http://192.168.49.2:30080/api/products
curl http://192.168.49.2:30080/api/orders
```

### Scale services

```bash
# Scale the user service to 4 replicas
kubectl scale deployment user-service --replicas=4 -n microservices
```

```
deployment.apps/user-service scaled
```

```bash
# Verify
kubectl get pods -l app=user-service -n microservices
```

```
NAME                            READY   STATUS    RESTARTS   AGE
user-service-9f0a1b-x5y6       1/1     Running   0          5m
user-service-9f0a1b-z7a8       1/1     Running   0          5m
user-service-9f0a1b-b9c0       1/1     Running   0          10s
user-service-9f0a1b-d1e2       1/1     Running   0          10s
```

### View logs in Kubernetes

```bash
# Logs from a specific pod
kubectl logs user-service-9f0a1b-x5y6 -n microservices

# Follow logs
kubectl logs -f user-service-9f0a1b-x5y6 -n microservices

# Logs from all pods of a deployment
kubectl logs deployment/user-service -n microservices
```

### Clean up Kubernetes deployment

```bash
# Delete everything in the namespace
kubectl delete namespace microservices
```

```
namespace "microservices" deleted
```

---

## The Complete Architecture — One Final Look

Here is the full picture of what you built:

```
+==================================================================+
||                 MICROSERVICES APPLICATION                       ||
||                                                                 ||
||   ┌──────────────────────────────────────────────────────────┐  ||
||   │                     INTERNET                             │  ||
||   └────────────────────────┬─────────────────────────────────┘  ||
||                            │                                    ||
||                            ▼                                    ||
||   ┌──────────────────────────────────────────────────────────┐  ||
||   │              API GATEWAY (Nginx)                         │  ||
||   │              Port 80 / NodePort 30080                    │  ||
||   │                                                          │  ||
||   │   /api/users  ──>  user-service:3001                     │  ||
||   │   /api/products ──> product-service:5000                 │  ||
||   │   /api/orders ──>  order-service:8080                    │  ||
||   └────┬──────────────────┬──────────────────┬───────────────┘  ||
||        │                  │                  │                   ||
||        ▼                  ▼                  ▼                   ||
||   ┌──────────┐     ┌──────────┐      ┌──────────┐              ||
||   │  USER    │     │ PRODUCT  │      │  ORDER   │              ||
||   │ SERVICE  │     │ SERVICE  │      │ SERVICE  │              ||
||   │          │     │          │      │          │              ||
||   │ Node.js  │     │  Python  │      │   Java   │              ||
||   │ Express  │     │  Flask   │      │  Spring  │              ||
||   │ 2 pods   │     │  2 pods  │      │  2 pods  │              ||
||   └────┬─────┘     └────┬─────┘      └────┬─────┘              ||
||        │                │                  │                    ||
||        └────────────────┼──────────────────┘                    ||
||                         │                                       ||
||              ┌──────────┴──────────┐                            ||
||              │                     │                            ||
||              ▼                     ▼                            ||
||   ┌──────────────────┐  ┌──────────────────┐                   ||
||   │   PostgreSQL     │  │     Redis        │                   ||
||   │   3 databases    │  │     Cache        │                   ||
||   │   (userdb,       │  │                  │                   ||
||   │    productdb,    │  │   Speeds up      │                   ||
||   │    orderdb)      │  │   read queries   │                   ||
||   └──────────────────┘  └──────────────────┘                   ||
||                                                                 ||
+==================================================================+
```

---

## Congratulations

You have built a complete microservices application from scratch. Let us take a moment to appreciate what you accomplished:

- You wrote three services in three different programming languages (Node.js, Python, Java)
- Each service has its own optimized, multi-stage Dockerfile
- You connected them all through a shared database and Redis cache
- You set up an API Gateway to route traffic
- You deployed everything locally with Docker Compose
- You translated the entire application to Kubernetes manifests
- You deployed to Kubernetes with proper health checks, resource limits, and scaling

This is not a toy project. This is the same architecture pattern used by professional engineering teams around the world.

---

## What to Learn Next

Your Docker and Kubernetes journey does not end here. Here are the roads ahead:

### Helm — Package Manager for Kubernetes

Helm lets you package your Kubernetes manifests into reusable charts. Instead of applying seven YAML files one by one, you run a single command. Think of Helm as what `apt-get` or `brew` is for your computer, but for Kubernetes.

```
helm install my-app ./my-chart
```

### Terraform — Infrastructure as Code

Terraform lets you define your entire cloud infrastructure (servers, networks, databases, Kubernetes clusters) in code. Instead of clicking buttons in a cloud console, you write configuration files and run `terraform apply`. Your infrastructure becomes versioned, reviewable, and repeatable.

```
terraform apply    # Creates your entire cloud setup
terraform destroy  # Tears it all down cleanly
```

### Service Mesh (Istio, Linkerd)

As your microservices grow, you need advanced networking features: traffic encryption between services, load balancing, circuit breakers, and observability. A service mesh handles all of this without changing your application code. Think of it as a smart highway system between your services.

### Cloud Providers

Once you are comfortable with Docker and Kubernetes locally, take your skills to the cloud:

- **AWS** — ECS (Elastic Container Service) or EKS (Elastic Kubernetes Service)
- **Google Cloud** — GKE (Google Kubernetes Engine)
- **Azure** — AKS (Azure Kubernetes Service)
- **DigitalOcean** — DOKS (DigitalOcean Kubernetes Service)

Each provider offers managed Kubernetes clusters, so you do not have to manage the control plane yourself.

### Monitoring and Observability

Learn Prometheus for metrics collection, Grafana for dashboards, and tools like Jaeger for distributed tracing. When you have dozens of services, you need to see what is happening inside your system at all times.

```
+---------------------------------------------------+
|             YOUR LEARNING ROADMAP                  |
|                                                    |
|   You Are Here                                     |
|       │                                            |
|       ├── Helm (package K8s apps)                  |
|       │                                            |
|       ├── Terraform (infrastructure as code)       |
|       │                                            |
|       ├── Service Mesh (advanced networking)       |
|       │                                            |
|       ├── Cloud Providers (AWS, GCP, Azure)        |
|       │                                            |
|       ├── Monitoring (Prometheus, Grafana)          |
|       │                                            |
|       └── CI/CD Pipelines (GitHub Actions,          |
|           GitLab CI, Jenkins)                      |
|                                                    |
|   Each step builds on what you already know.       |
|   You have a strong foundation. Keep building.     |
+---------------------------------------------------+
```

---

## Key Points

- A microservices architecture splits an application into small, independent services that each do one thing well.
- Each service gets its own Dockerfile, its own database, and its own deployment configuration.
- An API Gateway (Nginx) routes external traffic to the correct internal service.
- Docker Compose orchestrates multi-container applications locally with a single YAML file.
- Kubernetes manifests define the same application for production deployment, with added benefits like scaling, self-healing, and rolling updates.
- Multi-stage Docker builds keep images small and secure by separating build tools from runtime.
- Health checks (in Docker) and readiness/liveness probes (in Kubernetes) ensure traffic only reaches healthy services.
- Secrets and ConfigMaps in Kubernetes separate sensitive data from application code.
- Scaling in Kubernetes is as simple as changing the replica count.
- The skills you learned in this book — images, containers, volumes, networks, Compose, and Kubernetes — all come together in real-world applications exactly like this one.
