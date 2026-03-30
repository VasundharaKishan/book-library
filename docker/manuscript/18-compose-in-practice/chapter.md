# Chapter 18: Docker Compose in Practice

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Build a complete full-stack application with Docker Compose
- Create a React frontend served by Nginx
- Build a Spring Boot REST API with Gradle
- Set up a PostgreSQL database with initialization scripts
- Configure Nginx as a reverse proxy
- Write production-ready Dockerfiles for each service
- Create environment-specific Compose overrides
- Test the entire stack end-to-end
- Understand how all the pieces fit together in a real project

---

## Why This Chapter Matters

This chapter brings together everything you have learned. You will build a full-stack application that mirrors what you would encounter at a real company. It has a frontend, a backend API, a database, and a reverse proxy — four services working together.

Think of this as your graduation project. You have learned about images, containers, Dockerfiles, volumes, networks, Compose, debugging, and development workflows. Now you are combining all of those skills into one cohesive project. When you finish this chapter, you will have a template you can use for any full-stack project.

---

## The Architecture

We are building a simple bookstore application. Users can browse books and add new ones. Here is how the pieces fit together:

```
┌────────────────────────────────────────────────────────┐
│                     Docker Compose                      │
│                                                         │
│   Browser Request                                       │
│        │                                                │
│        ▼                                                │
│   ┌──────────────┐                                     │
│   │   nginx       │  Reverse Proxy                     │
│   │   Port 80     │  Routes requests:                  │
│   │               │  /api/* ──> api:8080               │
│   │               │  /*     ──> frontend files         │
│   └───┬───────┬───┘                                    │
│       │       │                                         │
│       ▼       ▼                                         │
│   ┌────────┐ ┌──────────────┐                          │
│   │frontend│ │   api         │  Spring Boot             │
│   │ (files)│ │   Port 8080   │  REST API               │
│   │ React  │ │               │  /api/books             │
│   │ static │ └───────┬───────┘                          │
│   │ files  │         │                                  │
│   └────────┘         ▼                                  │
│              ┌──────────────┐                          │
│              │  database     │  PostgreSQL              │
│              │  Port 5432    │  Stores books            │
│              └──────────────┘                          │
│                                                         │
└────────────────────────────────────────────────────────┘
```

**Why Nginx as a reverse proxy?**

A **reverse proxy** is a server that sits in front of your other servers and routes requests to the right place. Without a reverse proxy, your frontend and API would run on different ports (for example, `localhost:3000` for the frontend and `localhost:8080` for the API). This causes cross-origin issues in browsers.

With Nginx as a reverse proxy, everything goes through a single port (80). Nginx decides where to send each request:

- Requests starting with `/api/` go to the Spring Boot API.
- All other requests serve the React frontend files.

```
┌──────────────────────────────────────────────┐
│   Without Reverse Proxy:                     │
│                                               │
│   Browser -> localhost:3000  (frontend)      │
│   Browser -> localhost:8080  (api)           │
│   Problem: Cross-origin! Browser blocks it.  │
│                                               │
├──────────────────────────────────────────────┤
│   With Reverse Proxy:                        │
│                                               │
│   Browser -> localhost:80    (nginx)         │
│   nginx  -> /api/* -> api:8080               │
│   nginx  -> /*     -> static files           │
│   Everything through one port. No CORS!      │
│                                               │
└──────────────────────────────────────────────┘
```

---

## Project Structure

Here is the complete project layout:

```
bookstore/
├── docker-compose.yml
├── compose.override.yml
├── compose.production.yml
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── App.css
│       └── index.js
├── api/
│   ├── Dockerfile
│   ├── build.gradle
│   ├── settings.gradle
│   └── src/
│       └── main/
│           ├── java/
│           │   └── com/
│           │       └── bookstore/
│           │           ├── BookstoreApplication.java
│           │           ├── Book.java
│           │           ├── BookRepository.java
│           │           └── BookController.java
│           └── resources/
│               └── application.properties
├── nginx/
│   └── nginx.conf
└── database/
    └── init.sql
```

Let us build each piece step by step.

---

## Step 1: The Database

### Database Initialization Script

Create `database/init.sql`:

```sql
-- Create the books table
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20),
    published_year INTEGER,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO books (title, author, isbn, published_year, description) VALUES
    ('Clean Code', 'Robert C. Martin', '978-0132350884', 2008,
     'A handbook of agile software craftsmanship'),
    ('The Pragmatic Programmer', 'David Thomas, Andrew Hunt', '978-0135957059', 2019,
     'Your journey to mastery'),
    ('Design Patterns', 'Gang of Four', '978-0201633610', 1994,
     'Elements of reusable object-oriented software'),
    ('Refactoring', 'Martin Fowler', '978-0134757599', 2018,
     'Improving the design of existing code'),
    ('Domain-Driven Design', 'Eric Evans', '978-0321125217', 2003,
     'Tackling complexity in the heart of software');
```

This script runs the first time the PostgreSQL container starts with an empty data volume. It creates the `books` table and inserts five sample books.

---

## Step 2: The Spring Boot API

### Build Configuration

Create `api/build.gradle`:

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.1'
    id 'io.spring.dependency-management' version '1.1.4'
}

group = 'com.bookstore'
version = '1.0.0'

java {
    sourceCompatibility = '17'
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    runtimeOnly 'org.postgresql:postgresql'
}
```

Let us explain each dependency:

- **spring-boot-starter-web**: Provides everything needed to build REST APIs (embedded web server, JSON handling, etc.).
- **spring-boot-starter-data-jpa**: Provides database access using JPA (Java Persistence API), which lets you work with database rows as Java objects.
- **spring-boot-starter-actuator**: Provides health check endpoints (`/actuator/health`) that Docker can use for health checks.
- **postgresql**: The PostgreSQL JDBC driver that lets Java talk to PostgreSQL.

Create `api/settings.gradle`:

```groovy
rootProject.name = 'bookstore-api'
```

### Application Properties

Create `api/src/main/resources/application.properties`:

```properties
# Server configuration
server.port=8080

# Database configuration
# "database" is the Docker Compose service name
spring.datasource.url=jdbc:postgresql://${DB_HOST:database}:${DB_PORT:5432}/${DB_NAME:bookstore}
spring.datasource.username=${DB_USER:bookuser}
spring.datasource.password=${DB_PASSWORD:bookpass}

# JPA configuration
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false

# Actuator health endpoint
management.endpoints.web.exposure.include=health
```

The `${DB_HOST:database}` syntax means "use the `DB_HOST` environment variable, or default to `database` if it is not set." This lets us configure the application through Docker Compose environment variables.

### Java Source Code

Create `api/src/main/java/com/bookstore/BookstoreApplication.java`:

```java
package com.bookstore;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class BookstoreApplication {
    public static void main(String[] args) {
        SpringApplication.run(BookstoreApplication.class, args);
    }
}
```

This is the entry point for the Spring Boot application. The `@SpringBootApplication` annotation tells Spring to auto-configure everything.

Create `api/src/main/java/com/bookstore/Book.java`:

```java
package com.bookstore;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "books")
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String author;

    private String isbn;

    @Column(name = "published_year")
    private Integer publishedYear;

    private String description;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    // Default constructor (required by JPA)
    public Book() {}

    // Constructor for creating new books
    public Book(String title, String author, String isbn,
                Integer publishedYear, String description) {
        this.title = title;
        this.author = author;
        this.isbn = isbn;
        this.publishedYear = publishedYear;
        this.description = description;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }

    public Integer getPublishedYear() { return publishedYear; }
    public void setPublishedYear(Integer publishedYear) {
        this.publishedYear = publishedYear;
    }

    public String getDescription() { return description; }
    public void setDescription(String description) {
        this.description = description;
    }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
```

This is a **JPA entity**. It maps the `books` table in PostgreSQL to a Java class. Each column in the table corresponds to a field in the class. The `@Entity` annotation tells Spring this class represents a database table.

Create `api/src/main/java/com/bookstore/BookRepository.java`:

```java
package com.bookstore;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface BookRepository extends JpaRepository<Book, Long> {
    List<Book> findByAuthorContainingIgnoreCase(String author);
    List<Book> findByTitleContainingIgnoreCase(String title);
}
```

This is a **Spring Data repository**. By extending `JpaRepository`, Spring automatically provides methods like `findAll()`, `findById()`, `save()`, and `deleteById()`. The custom methods (`findByAuthorContainingIgnoreCase`) are automatically implemented by Spring based on the method name.

Create `api/src/main/java/com/bookstore/BookController.java`:

```java
package com.bookstore;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/books")
public class BookController {

    private final BookRepository bookRepository;

    public BookController(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    // GET /api/books — List all books
    @GetMapping
    public List<Book> getAllBooks() {
        return bookRepository.findAll();
    }

    // GET /api/books/{id} — Get a single book
    @GetMapping("/{id}")
    public ResponseEntity<Book> getBook(@PathVariable Long id) {
        return bookRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // POST /api/books — Create a new book
    @PostMapping
    public ResponseEntity<Book> createBook(@RequestBody Book book) {
        Book saved = bookRepository.save(book);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    // DELETE /api/books/{id} — Delete a book
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, String>> deleteBook(@PathVariable Long id) {
        if (!bookRepository.existsById(id)) {
            return ResponseEntity.notFound().build();
        }
        bookRepository.deleteById(id);
        return ResponseEntity.ok(Map.of("message", "Book deleted"));
    }

    // GET /api/books/search?title=xxx — Search books by title
    @GetMapping("/search")
    public List<Book> searchBooks(@RequestParam(required = false) String title,
                                  @RequestParam(required = false) String author) {
        if (title != null) {
            return bookRepository.findByTitleContainingIgnoreCase(title);
        }
        if (author != null) {
            return bookRepository.findByAuthorContainingIgnoreCase(author);
        }
        return bookRepository.findAll();
    }
}
```

This is the REST controller. It defines the API endpoints:

- `GET /api/books` — Returns all books.
- `GET /api/books/{id}` — Returns one book.
- `POST /api/books` — Creates a new book.
- `DELETE /api/books/{id}` — Deletes a book.
- `GET /api/books/search?title=xxx` — Searches by title or author.

### API Dockerfile

Create `api/Dockerfile`:

```dockerfile
# ── Stage 1: Build ──────────────────────────────────
FROM gradle:8-jdk17 AS builder

WORKDIR /app

# Copy build files first (for dependency caching)
COPY build.gradle settings.gradle ./

# Download dependencies (cached unless build files change)
RUN gradle dependencies --no-daemon

# Copy source code
COPY src ./src

# Build the application
RUN gradle bootJar --no-daemon

# ── Stage 2: Run ────────────────────────────────────
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copy the built JAR from the builder stage
COPY --from=builder /app/build/libs/*.jar app.jar

# Expose the application port
EXPOSE 8080

# Health check using Spring Actuator
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# Run the application
CMD ["java", "-jar", "app.jar"]
```

This is a **multi-stage build**. Let us explain:

**Stage 1 (builder)**: Uses a full Gradle image with JDK 17 to compile the Java application into a JAR file. The `gradle bootJar` command creates an executable JAR that contains everything the application needs to run.

**Stage 2 (runtime)**: Uses a minimal JRE image (just the Java runtime, no build tools). It copies only the compiled JAR from Stage 1. This makes the final image much smaller — around 200MB instead of 800MB+.

The `start_period: 30s` gives Spring Boot 30 seconds to start up. Java applications take longer to start than Node.js apps because the JVM needs to initialize.

---

## Step 3: The React Frontend

### Package Configuration

Create `frontend/package.json`:

```json
{
  "name": "bookstore-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version"]
  }
}
```

### HTML Template

Create `frontend/public/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Bookstore</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>
```

### React Application

Create `frontend/src/index.js`:

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

Create `frontend/src/App.js`:

```javascript
import React, { useState, useEffect } from 'react';

function App() {
  const [books, setBooks] = useState([]);
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch books on page load
  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/books');
      if (!response.ok) throw new Error('Failed to fetch books');
      const data = await response.json();
      setBooks(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addBook = async (e) => {
    e.preventDefault();
    if (!title || !author) return;

    try {
      const response = await fetch('/api/books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, author }),
      });
      if (!response.ok) throw new Error('Failed to add book');
      setTitle('');
      setAuthor('');
      fetchBooks();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteBook = async (id) => {
    try {
      const response = await fetch(`/api/books/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete book');
      fetchBooks();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Bookstore</h1>
        <p>A full-stack Docker Compose application</p>
      </header>

      <section className="add-book">
        <h2>Add a Book</h2>
        <form onSubmit={addBook}>
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Author"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            required
          />
          <button type="submit">Add Book</button>
        </form>
      </section>

      <section className="book-list">
        <h2>All Books</h2>
        {loading && <p>Loading books...</p>}
        {error && <p className="error">Error: {error}</p>}
        {!loading && books.length === 0 && <p>No books found.</p>}
        <div className="books">
          {books.map((book) => (
            <div key={book.id} className="book-card">
              <h3>{book.title}</h3>
              <p className="author">by {book.author}</p>
              {book.publishedYear && (
                <p className="year">Published: {book.publishedYear}</p>
              )}
              {book.description && (
                <p className="description">{book.description}</p>
              )}
              <button
                className="delete-btn"
                onClick={() => deleteBook(book.id)}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default App;
```

Notice that the API calls use relative URLs like `/api/books` instead of `http://localhost:8080/api/books`. This works because Nginx (our reverse proxy) handles the routing. The browser sends all requests to Nginx, and Nginx forwards `/api/*` requests to the Spring Boot API.

Create `frontend/src/App.css`:

```css
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f5f5;
  color: #333;
}

.app {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: #2c3e50;
  color: white;
  border-radius: 8px;
}

header h1 {
  margin-bottom: 5px;
}

header p {
  opacity: 0.8;
  font-size: 14px;
}

.add-book {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.add-book h2 {
  margin-bottom: 15px;
}

.add-book form {
  display: flex;
  gap: 10px;
}

.add-book input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.add-book button {
  padding: 10px 20px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.add-book button:hover {
  background: #34495e;
}

.book-list h2 {
  margin-bottom: 15px;
}

.books {
  display: grid;
  gap: 15px;
}

.book-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.book-card h3 {
  margin-bottom: 5px;
  color: #2c3e50;
}

.book-card .author {
  color: #666;
  font-style: italic;
  margin-bottom: 5px;
}

.book-card .year {
  color: #888;
  font-size: 13px;
  margin-bottom: 5px;
}

.book-card .description {
  color: #555;
  font-size: 14px;
  margin-bottom: 10px;
}

.delete-btn {
  padding: 5px 15px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.delete-btn:hover {
  background: #c0392b;
}

.error {
  color: #e74c3c;
  padding: 10px;
  background: #ffeaea;
  border-radius: 4px;
}
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
# ── Stage 1: Build ──────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY public ./public
COPY src ./src

# Build the React app (creates /app/build)
RUN npm run build

# ── Stage 2: Serve ──────────────────────────────────
FROM nginx:alpine

# Copy the built React app to nginx's serve directory
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

This is another multi-stage build:

**Stage 1**: Uses Node.js to build the React application. `npm run build` creates optimized static files (HTML, CSS, JavaScript) in the `/app/build` directory.

**Stage 2**: Uses a minimal Nginx image to serve the static files. The built files are copied to Nginx's default serve directory. The final image contains no Node.js, no source code, and no `node_modules` — just the optimized static files and Nginx.

---

## Step 4: The Nginx Reverse Proxy

Create `nginx/nginx.conf`:

```nginx
# Main Nginx configuration for the Bookstore application

# Run with a single worker process
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    # Include MIME types so files are served with correct Content-Type
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent"';

    access_log /var/log/nginx/access.log main;
    error_log  /var/log/nginx/error.log warn;

    # Performance settings
    sendfile        on;
    keepalive_timeout  65;

    # ── Upstream: Spring Boot API ────────────────────
    # "api" is the Docker Compose service name
    upstream api_backend {
        server api:8080;
    }

    # ── Server Configuration ─────────────────────────
    server {
        listen 80;
        server_name localhost;

        # ── API requests: forward to Spring Boot ─────
        # Any request starting with /api/ goes to the backend
        location /api/ {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # ── Health check endpoint for the API ────────
        location /actuator/ {
            proxy_pass http://api_backend;
        }

        # ── Frontend: serve React static files ───────
        location / {
            root /usr/share/nginx/html;
            index index.html;
            # For single-page app: serve index.html for all routes
            try_files $uri $uri/ /index.html;
        }

        # ── Error pages ──────────────────────────────
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
}
```

Let us walk through the key sections:

**`upstream api_backend`**: Defines the backend server. `api:8080` uses the Compose service name `api` and the port the Spring Boot app listens on. Docker's DNS resolves `api` to the correct container IP.

**`location /api/`**: Any request with a URL starting with `/api/` is forwarded to the Spring Boot API. The `proxy_set_header` lines pass useful information about the original request to the backend.

**`location /`**: All other requests serve files from `/usr/share/nginx/html`, which is where the React build files live. The `try_files` directive is important for single-page apps — if the requested file does not exist, it serves `index.html`, allowing React Router to handle the URL.

---

## Step 5: The Docker Compose Files

### Base Configuration

Create `docker-compose.yml`:

```yaml
services:
  # ──────────────────────────────────────────────────
  # Nginx — Reverse Proxy
  # Routes /api/* to the Spring Boot API
  # Serves React frontend files for everything else
  # ──────────────────────────────────────────────────
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - frontend-build:/usr/share/nginx/html:ro
    depends_on:
      api:
        condition: service_healthy
      frontend:
        condition: service_completed_successfully
    networks:
      - frontend-net

  # ──────────────────────────────────────────────────
  # Frontend — React Application
  # Builds the React app and outputs to a shared volume
  # This is a "build" service that exits after building
  # ──────────────────────────────────────────────────
  frontend:
    build: ./frontend
    volumes:
      - frontend-build:/usr/share/nginx/html

  # ──────────────────────────────────────────────────
  # API — Spring Boot Application
  # REST API at /api/books
  # ──────────────────────────────────────────────────
  api:
    build: ./api
    environment:
      DB_HOST: database
      DB_PORT: 5432
      DB_USER: bookuser
      DB_PASSWORD: bookpass
      DB_NAME: bookstore
    depends_on:
      database:
        condition: service_healthy
    networks:
      - frontend-net
      - backend-net

  # ──────────────────────────────────────────────────
  # Database — PostgreSQL
  # ──────────────────────────────────────────────────
  database:
    image: postgres:16
    environment:
      POSTGRES_USER: bookuser
      POSTGRES_PASSWORD: bookpass
      POSTGRES_DB: bookstore
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bookuser -d bookstore"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - backend-net

# ──────────────────────────────────────────────────
# Volumes
# ──────────────────────────────────────────────────
volumes:
  db-data:             # Persistent database storage
  frontend-build:      # Built React files shared between frontend and nginx

# ──────────────────────────────────────────────────
# Networks
# ──────────────────────────────────────────────────
networks:
  frontend-net:        # nginx <-> api communication
    driver: bridge
  backend-net:         # api <-> database communication
    driver: bridge
```

Let us explain the architecture decisions:

**Network isolation**: Two networks separate concerns. The `frontend-net` connects nginx and the api. The `backend-net` connects the api and the database. Nginx cannot reach the database directly — it must go through the api.

**The frontend service**: This service builds the React app and exits. It uses the `service_completed_successfully` condition in nginx's `depends_on` so nginx waits for the build to finish before starting. The built files are placed in the `frontend-build` volume, which nginx reads from.

**Shared volume for frontend files**: The `frontend-build` volume is shared between the `frontend` (which writes the built files) and `nginx` (which reads and serves them).

### Development Override

Create `compose.override.yml`:

```yaml
services:
  api:
    ports:
      - "8080:8080"      # Direct API access for debugging
    environment:
      SPRING_JPA_SHOW_SQL: "true"     # Show SQL queries in logs

  database:
    ports:
      - "5432:5432"      # Direct database access for GUI tools
```

### Production Configuration

Create `compose.production.yml`:

```yaml
services:
  nginx:
    restart: always

  api:
    restart: always
    environment:
      SPRING_JPA_SHOW_SQL: "false"
    deploy:
      resources:
        limits:
          memory: 512M

  database:
    restart: always
    # No port mapping in production
    deploy:
      resources:
        limits:
          memory: 256M
```

---

## Step 6: Build and Run

### Building Everything

From the `bookstore` directory:

```bash
docker compose up -d --build
```

**Output:**

```
[+] Building 45.2s (25/25) FINISHED
 => [frontend] Building...
 => [api] Building...
[+] Running 5/5
 ✔ Network bookstore_frontend-net  Created
 ✔ Network bookstore_backend-net   Created
 ✔ Container bookstore-database-1  Started
 ✔ Container bookstore-frontend-1  Started
 ✔ Container bookstore-api-1       Started
 ✔ Container bookstore-nginx-1     Started
```

The first build takes a few minutes because it downloads dependencies, compiles Java code, and builds the React app. Subsequent builds are much faster due to Docker's layer caching.

### Checking Status

```bash
docker compose ps
```

**Output:**

```
NAME                     IMAGE              STATUS                      PORTS
bookstore-api-1          bookstore-api      Up 30s (healthy)            0.0.0.0:8080->8080/tcp
bookstore-database-1     postgres:16        Up 45s (healthy)            0.0.0.0:5432->5432/tcp
bookstore-frontend-1     bookstore-frontend Exited (0) 20s ago
bookstore-nginx-1        nginx:alpine       Up 10s                      0.0.0.0:80->80/tcp
```

Notice that the `frontend` service shows "Exited (0)" — this is expected. It built the React app, placed the files in the shared volume, and exited. Exit code 0 means it completed successfully.

---

## Step 7: Testing the Application

### Access the Frontend

Open your browser and go to `http://localhost`. You should see the Bookstore application with the five sample books.

### Test the API Directly

```bash
# List all books
curl http://localhost/api/books
```

**Output:**

```json
[
  {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "publishedYear": 2008,
    "description": "A handbook of agile software craftsmanship",
    "createdAt": "2024-01-15T10:00:00"
  },
  ...
]
```

```bash
# Add a new book
curl -X POST http://localhost/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Docker in Practice", "author": "Ian Miell"}'
```

```bash
# Search for a book
curl "http://localhost/api/books/search?title=clean"
```

```bash
# Check API health
curl http://localhost/actuator/health
```

**Output:**

```json
{
  "status": "UP"
}
```

### Check the Logs

```bash
# All services
docker compose logs --tail 20

# Just the API
docker compose logs api

# Follow nginx access logs
docker compose logs -f nginx
```

### Verify Network Isolation

```bash
# The API can reach the database
docker compose exec api ping -c 1 database
# Should succeed

# Nginx cannot reach the database
docker compose exec nginx ping -c 1 database
# Should fail: "bad address" or "Name does not resolve"
```

---

## Step 8: Environment-Specific Deployment

### Development

```bash
# Uses docker-compose.yml + compose.override.yml automatically
docker compose up -d --build
```

Features: API port exposed, database port exposed, SQL logging enabled.

### Production

```bash
# Explicitly specify production file (skips override)
docker compose -f docker-compose.yml -f compose.production.yml up -d --build
```

Features: Only port 80 exposed, auto-restart enabled, memory limits set, no SQL logging.

---

## How All the Pieces Connect

Let us trace a complete request through the system:

```
1. User opens http://localhost in browser

2. Browser sends GET / to nginx (port 80)

3. nginx sees "/" and serves the React index.html
   from /usr/share/nginx/html

4. Browser loads React app and JavaScript

5. React app calls GET /api/books

6. Browser sends GET /api/books to nginx (port 80)

7. nginx sees "/api/" prefix and forwards to api:8080

8. Spring Boot receives GET /api/books

9. Spring Boot queries PostgreSQL at database:5432

10. PostgreSQL returns the book rows

11. Spring Boot converts rows to JSON and responds

12. nginx forwards the JSON response to the browser

13. React renders the book list on the page
```

```
┌────────────────────────────────────────────────────┐
│                 Request Flow                        │
│                                                     │
│   Browser                                           │
│     │                                               │
│     │ GET /api/books                                │
│     ▼                                               │
│   nginx:80                                          │
│     │                                               │
│     │ proxy_pass (URL starts with /api/)            │
│     ▼                                               │
│   api:8080                                          │
│     │                                               │
│     │ JDBC query                                    │
│     ▼                                               │
│   database:5432                                     │
│     │                                               │
│     │ SQL result                                    │
│     ▼                                               │
│   api:8080                                          │
│     │                                               │
│     │ JSON response                                 │
│     ▼                                               │
│   nginx:80                                          │
│     │                                               │
│     │ Forward response                              │
│     ▼                                               │
│   Browser                                           │
│     │                                               │
│     │ Render book list                              │
│     ▼                                               │
│   User sees the books!                              │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

## Common Mistakes

### Mistake 1: Using Absolute API URLs in React

```javascript
// Wrong: hardcoded URL breaks in Docker
const response = await fetch('http://localhost:8080/api/books');

// Right: relative URL works with reverse proxy
const response = await fetch('/api/books');
```

Relative URLs let Nginx handle the routing. The browser sends the request to wherever the page was loaded from (Nginx on port 80), and Nginx forwards it to the API.

### Mistake 2: Forgetting try_files for Single-Page Apps

```nginx
# Wrong: direct URLs like /about return 404
location / {
    root /usr/share/nginx/html;
}

# Right: fallback to index.html for client-side routing
location / {
    root /usr/share/nginx/html;
    try_files $uri $uri/ /index.html;
}
```

Without `try_files`, if a user navigates directly to `http://localhost/about`, Nginx looks for a file called `/about` which does not exist. `try_files` falls back to `index.html`, which loads the React app, and React Router handles the URL.

### Mistake 3: Not Waiting for Build Services

```yaml
# Wrong: nginx starts before frontend finishes building
nginx:
  depends_on:
    - frontend    # Only waits for the container to start, not finish

# Right: wait for the build to complete
nginx:
  depends_on:
    frontend:
      condition: service_completed_successfully
```

### Mistake 4: Missing Network Connections

```yaml
# Wrong: api and nginx on different networks — nginx cannot reach api
api:
  networks:
    - backend-net

nginx:
  networks:
    - frontend-net

# Right: api must be on both networks
api:
  networks:
    - frontend-net    # So nginx can reach it
    - backend-net     # So it can reach the database
```

### Mistake 5: Exposing Database Ports in Production

```yaml
# DANGER: database accessible from the internet
database:
  ports:
    - "5432:5432"    # Only do this in development!
```

In production, the database should only be accessible from other containers on the same Docker network. Never expose database ports to the host in production.

---

## Best Practices

1. **Use multi-stage builds** for all services. This keeps final images small and production-ready.

2. **Use a reverse proxy** (Nginx) in front of your application. It simplifies URL routing, handles static files efficiently, and avoids cross-origin issues.

3. **Separate networks by tier** — frontend, backend, database. Only the API should bridge between networks.

4. **Use `service_completed_successfully`** for build-only services that need to finish before dependent services start.

5. **Keep credentials in environment variables**, never in source code or Dockerfiles.

6. **Use `.dockerignore` files** in every service directory to exclude unnecessary files from the build context (node_modules, .git, build artifacts).

7. **Use read-only mounts** (`:ro`) for configuration files and frontend assets. Services that only need to read data should not be able to write.

8. **Test each service independently** before assembling the full stack. Verify the API works by itself before adding the frontend and proxy.

9. **Start with simple and add complexity**. Get two services working before adding the third and fourth.

10. **Document your architecture** with diagrams. As the number of services grows, it becomes harder to remember how they connect.

---

## Quick Summary

In this chapter, you built a complete full-stack application using Docker Compose with four services: a React frontend (built and served as static files), a Spring Boot REST API, a PostgreSQL database, and an Nginx reverse proxy. The Nginx reverse proxy routes API requests to Spring Boot and serves the React frontend files for everything else. Network isolation ensures the database is only accessible from the API. Multi-stage builds keep all images small. Environment-specific Compose files let you switch between development and production configurations.

---

## Key Points

- A reverse proxy (Nginx) routes requests to the correct backend service and serves static frontend files.
- Use relative URLs (`/api/books`) in frontend code so the reverse proxy can handle routing.
- Multi-stage Docker builds separate the build environment from the runtime environment.
- The `service_completed_successfully` condition waits for build services to finish.
- Network isolation (separate frontend and backend networks) improves security.
- Shared volumes let build services output files that other services consume.
- Spring Boot uses `application.properties` with `${ENV_VAR:default}` syntax for configuration.
- `try_files $uri $uri/ /index.html` in Nginx is required for single-page app routing.
- Development overrides expose extra ports; production overrides add restart policies and resource limits.
- Never expose database ports in production.

---

## Practice Questions

1. Explain why the frontend service exits after building. How does Nginx get the React build files if the frontend container is no longer running?

2. Why do we use two separate networks (frontend-net and backend-net) instead of putting all services on one network?

3. A user navigates directly to `http://localhost/books/123` in their browser. Trace the request through the system. What role does `try_files` play?

4. The API service is on both `frontend-net` and `backend-net`. Why does it need to be on both networks? What would happen if it were only on `backend-net`?

5. Compare the development and production Compose configurations. What are the key differences, and why does each difference matter?

---

## Exercises

### Exercise 1: Add a Search Feature

1. Start the bookstore application.
2. Modify the React frontend to add a search bar that calls `GET /api/books/search?title=xxx`.
3. Rebuild only the frontend: `docker compose build frontend`.
4. Restart: `docker compose up -d`.
5. Test the search functionality in your browser.

### Exercise 2: Add a Redis Cache

1. Add a Redis service to the `docker-compose.yml`.
2. Put Redis on the `backend-net` network.
3. Configure the Spring Boot API to use Redis for caching (add Spring Cache and Spring Data Redis dependencies).
4. Verify that repeated requests are served from the cache.

### Exercise 3: Add an Admin Dashboard

1. Add an Adminer service to the Compose file for database management.
2. Put it on the `backend-net` network.
3. Optionally add a route in Nginx to proxy `/admin/` to Adminer.
4. Access the admin dashboard and manage books directly in the database.
5. Verify that changes in the database appear in the React frontend.

---

## What Is Next?

Congratulations. You have built a complete, production-ready, full-stack application with Docker Compose. You understand how to create Dockerfiles, configure networks, manage volumes, set up reverse proxies, and handle different environments. In the upcoming chapters, you will learn how to publish your images to Docker Hub and other registries, set up continuous integration and deployment (CI/CD) pipelines, and eventually scale your applications with orchestration tools like Docker Swarm and Kubernetes.
