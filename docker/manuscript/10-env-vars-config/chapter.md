# Chapter 10: Environment Variables and Configuration

## What You Will Learn

By the end of this chapter, you will be able to:

- Explain why configuration should live outside your code
- Pass environment variables to containers using the `-e` flag
- Pass multiple environment variables at once
- Use `.env` files to organize environment variables
- Load environment variables from a file with `--env-file`
- Set default environment variables in a Dockerfile with `ENV`
- Use build arguments with `ARG` and `--build-arg`
- Understand the difference between runtime and build-time configuration
- Configure a database connection string using environment variables

## Why This Chapter Matters

Imagine you build a web application that connects to a database. In development, the database runs on your laptop at `localhost:5432`. In production, it runs on a cloud server at `db.mycompany.com:5432`. How do you handle this difference?

The wrong answer is to hardcode the database address in your code and change it every time you deploy. That is error-prone, insecure, and makes your application impossible to share.

The right answer is **environment variables**. You store the database address in an environment variable and read it at runtime. The same Docker image works everywhere -- you just change the environment variable.

**Real-life analogy:** Think of environment variables as the settings on your phone. The same phone (your Docker image) can work on different cell networks (environments) just by changing the settings (environment variables). You do not need a different phone for each network.

This chapter teaches you how to use environment variables -- one of the most fundamental skills for building professional, production-ready containers.

---

## Why Configuration Belongs Outside Code

### The Twelve-Factor App

The **Twelve-Factor App** is a set of principles for building modern applications. Factor number three states:

> Store configuration in the environment.

**Configuration** means anything that changes between environments:
- Database connection strings
- API keys and secrets
- Port numbers
- Feature flags (on/off switches for features)
- Log levels (how much detail to log)
- External service URLs

### What Happens When You Hardcode Configuration

```javascript
// BAD: Configuration hardcoded in the source code
const db = require('pg');
const connection = db.connect({
  host: 'localhost',       // Only works on your laptop!
  port: 5432,
  database: 'myapp',
  user: 'admin',
  password: 'secret123'   // Password visible in source code!
});
```

Problems with this approach:

1. **It only works in one environment.** Change from development to production and the app breaks.
2. **Secrets are exposed.** The password is visible in the source code, in version control, and in the Docker image.
3. **You need different code for each environment.** Development, staging, production -- three different versions of the same file.

### The Right Way: Environment Variables

```javascript
// GOOD: Configuration read from environment variables
const db = require('pg');
const connection = db.connect({
  host: process.env.DB_HOST,       // Read from environment
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD
});
```

Now the same code works everywhere. You just change the environment variables:

```
+--------------------------------------------------+
|    Same Code, Different Environments             |
+--------------------------------------------------+
|                                                  |
|    Development:                                  |
|    DB_HOST=localhost                              |
|    DB_PORT=5432                                   |
|    DB_PASSWORD=devpass123                         |
|                                                  |
|    Staging:                                      |
|    DB_HOST=staging-db.internal                   |
|    DB_PORT=5432                                   |
|    DB_PASSWORD=stagingP@ss                       |
|                                                  |
|    Production:                                   |
|    DB_HOST=prod-db.mycompany.com                 |
|    DB_PORT=5432                                   |
|    DB_PASSWORD=sup3rS3cur3P@ss!                  |
|                                                  |
|    Same Docker image, same code,                 |
|    different configuration.                      |
|                                                  |
+--------------------------------------------------+
```

---

## The -e Flag: Setting Environment Variables

The simplest way to pass an environment variable to a container is the `-e` (or `--env`) flag.

### Syntax

```bash
$ docker run -e VARIABLE_NAME=value image_name
```

### Example

```bash
# Set a single environment variable
$ docker run -e MY_NAME=Alice alpine echo "Hello, my name is $MY_NAME"
Hello, my name is Alice
```

Let us use a more practical example. Create a simple Node.js app that reads environment variables:

```javascript
// server.js
const express = require('express');
const app = express();

const PORT = process.env.PORT || 3000;
const APP_ENV = process.env.APP_ENV || 'development';
const DB_HOST = process.env.DB_HOST || 'localhost';

app.get('/', (req, res) => {
  res.json({
    environment: APP_ENV,
    port: PORT,
    database_host: DB_HOST
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running in ${APP_ENV} mode on port ${PORT}`);
});
```

Now run it with different configurations:

```bash
# Development configuration
$ docker run -d -p 3000:3000 \
  -e APP_ENV=development \
  -e DB_HOST=localhost \
  --name dev-app my-app

$ curl http://localhost:3000
{
  "environment": "development",
  "port": "3000",
  "database_host": "localhost"
}

$ docker stop dev-app && docker rm dev-app

# Production configuration (same image, different env vars)
$ docker run -d -p 3000:3000 \
  -e APP_ENV=production \
  -e DB_HOST=prod-db.mycompany.com \
  --name prod-app my-app

$ curl http://localhost:3000
{
  "environment": "production",
  "port": "3000",
  "database_host": "prod-db.mycompany.com"
}
```

Same image, different behavior -- all controlled by environment variables.

### Passing a Variable from Your Host

If the variable already exists on your computer, you can pass it without a value:

```bash
# Set a variable on your computer
$ export MY_SECRET=abc123

# Pass it to the container (Docker reads it from your environment)
$ docker run -e MY_SECRET alpine echo $MY_SECRET
abc123
```

When you write `-e MY_SECRET` without `=value`, Docker passes the value from your host's environment.

---

## Multiple Environment Variables

You can set multiple variables by using multiple `-e` flags:

```bash
$ docker run -d -p 3000:3000 \
  -e APP_ENV=production \
  -e DB_HOST=db.example.com \
  -e DB_PORT=5432 \
  -e DB_NAME=myapp \
  -e DB_USER=admin \
  -e DB_PASSWORD=s3cret \
  -e LOG_LEVEL=info \
  -e CACHE_TTL=3600 \
  --name my-app my-app
```

This works, but as you can see, it gets long and hard to manage. This is where `.env` files come in.

---

## .env Files: Organizing Environment Variables

A `.env` file is a simple text file where each line contains one environment variable in the format `KEY=VALUE`.

**Real-life analogy:** A `.env` file is like a settings sheet. Instead of telling someone each setting one by one, you hand them a sheet of paper with all the settings listed.

### Creating a .env File

```bash
# .env
APP_ENV=production
PORT=3000

# Database configuration
DB_HOST=db.example.com
DB_PORT=5432
DB_NAME=myapp
DB_USER=admin
DB_PASSWORD=s3cret

# Application settings
LOG_LEVEL=info
CACHE_TTL=3600
MAX_CONNECTIONS=100
```

### Rules for .env Files

```
+--------------------------------------------------+
|    .env File Syntax Rules                        |
+--------------------------------------------------+
|                                                  |
|    KEY=VALUE          Basic format               |
|    KEY=               Empty value (valid)        |
|    # This is a        Comments start with #      |
|    comment                                       |
|    KEY="hello world"  Quotes for spaces          |
|    KEY='hello world'  Single quotes work too     |
|                                                  |
|    NOT supported:                                |
|    export KEY=VALUE   (no export keyword)        |
|    KEY = VALUE        (no spaces around =)       |
|                                                  |
+--------------------------------------------------+
```

---

## The --env-file Flag: Loading From a File

Instead of listing each variable with `-e`, you can load all variables from a file:

### Syntax

```bash
$ docker run --env-file path/to/.env image_name
```

### Example

Create different `.env` files for different environments:

```bash
# .env.development
APP_ENV=development
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_dev
DB_USER=dev_user
DB_PASSWORD=dev_password
LOG_LEVEL=debug
```

```bash
# .env.production
APP_ENV=production
PORT=3000
DB_HOST=prod-db.mycompany.com
DB_PORT=5432
DB_NAME=myapp_prod
DB_USER=prod_user
DB_PASSWORD=sup3rS3cur3P@ss
LOG_LEVEL=warn
```

Now run with different environments:

```bash
# Run with development settings
$ docker run -d -p 3000:3000 --env-file .env.development --name dev my-app

# Run with production settings
$ docker run -d -p 3001:3000 --env-file .env.production --name prod my-app
```

### Using Multiple .env Files

You can combine `--env-file` with `-e` flags, and use multiple `--env-file` flags:

```bash
# Load base config, then override specific values
$ docker run -d -p 3000:3000 \
  --env-file .env.base \
  --env-file .env.production \
  -e LOG_LEVEL=debug \
  --name my-app my-app
```

When the same variable appears multiple times, the last one wins:

```
+--------------------------------------------------+
|    Variable Precedence (Last Wins)               |
+--------------------------------------------------+
|                                                  |
|    .env.base:        LOG_LEVEL=info              |
|    .env.production:  LOG_LEVEL=warn     (wins    |
|    -e flag:          LOG_LEVEL=debug     over    |
|                                          these)  |
|                                                  |
|    Result: LOG_LEVEL=debug                       |
|    (the -e flag was last, so it wins)            |
|                                                  |
+--------------------------------------------------+
```

### Verifying Environment Variables Inside a Container

```bash
# Check all environment variables
$ docker exec my-app env
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
APP_ENV=production
DB_HOST=prod-db.mycompany.com
DB_PORT=5432
LOG_LEVEL=debug
...

# Check a specific variable
$ docker exec my-app printenv DB_HOST
prod-db.mycompany.com
```

---

## ENV in Dockerfile: Setting Default Values

The `ENV` instruction in a Dockerfile sets default values for environment variables. These defaults can be overridden at runtime with `-e`.

**Real-life analogy:** `ENV` in a Dockerfile is like the factory settings on your phone. They give you reasonable defaults, but you can change them anytime.

### Syntax

```dockerfile
# Single variable
ENV KEY=value

# Multiple variables (old syntax, still works)
ENV KEY1=value1 \
    KEY2=value2 \
    KEY3=value3
```

### Example Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Set default environment variables
# These can be overridden with docker run -e
ENV NODE_ENV=production \
    PORT=3000 \
    LOG_LEVEL=info

COPY package.json package-lock.json ./
RUN npm ci --only=production

COPY . .

USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

### How ENV Defaults Work

```
+--------------------------------------------------+
|    ENV Default Behavior                          |
+--------------------------------------------------+
|                                                  |
|    Dockerfile:    ENV PORT=3000                   |
|                                                  |
|    docker run my-app                             |
|    => PORT=3000 (uses default from Dockerfile)   |
|                                                  |
|    docker run -e PORT=8080 my-app                |
|    => PORT=8080 (override wins)                  |
|                                                  |
|    Priority:                                     |
|    1. -e flag (highest)                          |
|    2. --env-file                                 |
|    3. ENV in Dockerfile (lowest, default)        |
|                                                  |
+--------------------------------------------------+
```

### ENV Variables Are Visible in the Image

**Important security note:** Variables set with `ENV` are baked into the image. Anyone who has access to the image can see them:

```bash
$ docker inspect my-app | grep -A 5 "Env"
"Env": [
    "NODE_ENV=production",
    "PORT=3000",
    "LOG_LEVEL=info",
    "PATH=/usr/local/sbin:..."
]
```

**Never put secrets (passwords, API keys, tokens) in ENV instructions.** Use runtime `-e` flags or `--env-file` instead.

```dockerfile
# BAD: Secret is visible in the image!
ENV DB_PASSWORD=my_secret_password

# GOOD: Set a placeholder. Override at runtime.
ENV DB_PASSWORD=changeme

# Or better yet, do not set it at all.
# Let the application fail clearly if the variable is missing.
```

---

## ARG and --build-arg: Build-Time Variables

`ARG` defines variables that are only available during the **build process**. They are not available when the container runs.

**Real-life analogy:** `ARG` is like instructions you give to a contractor while building your house. "Use oak for the floors" and "Paint the walls blue" are building instructions. Once the house is built, the contractor's instructions are gone. The homeowner (the running container) does not see them.

### Syntax

```dockerfile
# In the Dockerfile
ARG VARIABLE_NAME
ARG VARIABLE_NAME=default_value
```

```bash
# When building
$ docker build --build-arg VARIABLE_NAME=value -t image_name .
```

### Example: Choosing a Node.js Version at Build Time

```dockerfile
# ARG defines a build-time variable
ARG NODE_VERSION=18

# Use the ARG value in FROM
FROM node:${NODE_VERSION}-alpine

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production
COPY . .

EXPOSE 3000
CMD ["node", "server.js"]
```

Now you can build with different Node.js versions without changing the Dockerfile:

```bash
# Build with Node.js 18 (the default)
$ docker build -t my-app:node18 .

# Build with Node.js 20
$ docker build --build-arg NODE_VERSION=20 -t my-app:node20 .

# Build with Node.js 16
$ docker build --build-arg NODE_VERSION=16 -t my-app:node16 .
```

### ARG vs ENV: The Key Difference

```
+--------------------------------------------------+
|    ARG vs ENV Comparison                         |
+--------------------------------------------------+
|                                                  |
|    Feature          ARG            ENV            |
|    ------------------------------------------    |
|    Available when   Build only     Build + Run   |
|    Set by           --build-arg    -e / --env    |
|    In Dockerfile    ARG NAME=val   ENV NAME=val  |
|    Visible in       Build output   Image + Run   |
|    running container   No          Yes           |
|    Persists in image   No          Yes           |
|    Use for          Version nums,  App config,   |
|                     build opts     ports, modes  |
|                                                  |
+--------------------------------------------------+
```

### Visualizing Build-Time vs Runtime

```
+--------------------------------------------------+
|    Build Time vs Runtime                         |
+--------------------------------------------------+
|                                                  |
|    BUILD TIME (docker build)                     |
|    +------------------------------------------+  |
|    |  ARG variables available here             |  |
|    |  ENV variables set here                   |  |
|    |  RUN commands execute here                |  |
|    +------------------------------------------+  |
|                                                  |
|         Image is created                         |
|              |                                   |
|              v                                   |
|                                                  |
|    RUNTIME (docker run)                          |
|    +------------------------------------------+  |
|    |  ARG variables are GONE                   |  |
|    |  ENV variables available here             |  |
|    |  -e variables available here              |  |
|    |  CMD/ENTRYPOINT executes here             |  |
|    +------------------------------------------+  |
|                                                  |
+--------------------------------------------------+
```

### Using ARG and ENV Together

A common pattern is to use ARG to set a build-time default that becomes an ENV variable:

```dockerfile
# Accept a version at build time
ARG APP_VERSION=1.0.0

# Make it available at runtime too
ENV APP_VERSION=${APP_VERSION}

# Now APP_VERSION is available both during build and at runtime
```

```bash
# Build with a custom version
$ docker build --build-arg APP_VERSION=2.1.0 -t my-app:2.1.0 .

# The version is available inside the running container
$ docker run my-app:2.1.0 printenv APP_VERSION
2.1.0
```

### ARG Scope

ARG has a specific scope. An ARG defined before FROM is only available in the FROM instruction:

```dockerfile
# This ARG is only available for the FROM line
ARG NODE_VERSION=18
FROM node:${NODE_VERSION}-alpine

# This will NOT work -- NODE_VERSION is out of scope!
RUN echo "Building with Node ${NODE_VERSION}"

# You need to re-declare it after FROM
ARG NODE_VERSION
RUN echo "Building with Node ${NODE_VERSION}"
```

---

## Runtime vs Build-Time Configuration

Understanding when to use each type of configuration is crucial:

### Build-Time Configuration (ARG)

Use ARG for things that affect how the image is **built**:

```dockerfile
# Which version of the base image to use
ARG NODE_VERSION=18
FROM node:${NODE_VERSION}-alpine

# Whether to install development dependencies
ARG INSTALL_DEV_DEPS=false
RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
      npm ci; \
    else \
      npm ci --only=production; \
    fi

# Which registry to pull packages from
ARG NPM_REGISTRY=https://registry.npmjs.org
RUN npm config set registry ${NPM_REGISTRY} && npm ci
```

### Runtime Configuration (ENV / -e)

Use ENV or -e for things that affect how the application **runs**:

```dockerfile
ENV NODE_ENV=production \
    PORT=3000 \
    LOG_LEVEL=info
```

```bash
$ docker run -e DB_HOST=prod-db.example.com \
             -e DB_PASSWORD=s3cret \
             -e REDIS_URL=redis://cache:6379 \
             my-app
```

### Decision Guide

```
+--------------------------------------------------+
|    When to Use ARG vs ENV vs -e                  |
+--------------------------------------------------+
|                                                  |
|    Question: Does the value affect how the        |
|    image is built?                               |
|                                                  |
|    YES -> Use ARG                                |
|           Examples:                              |
|           - Base image version                   |
|           - Build-time flags                     |
|           - Package registry URLs                |
|                                                  |
|    NO -> Does the value contain a secret?        |
|                                                  |
|      YES -> Use -e or --env-file at runtime      |
|             NEVER put secrets in ENV or ARG      |
|             Examples:                            |
|             - Database passwords                 |
|             - API keys                           |
|             - Auth tokens                        |
|                                                  |
|      NO -> Does it have a sensible default?      |
|                                                  |
|        YES -> Use ENV in Dockerfile              |
|               Override with -e when needed       |
|               Examples:                          |
|               - PORT=3000                        |
|               - LOG_LEVEL=info                   |
|               - NODE_ENV=production              |
|                                                  |
|        NO -> Use -e at runtime                   |
|              Examples:                           |
|              - DB_HOST (different per env)        |
|              - API_URL (different per env)        |
|                                                  |
+--------------------------------------------------+
```

---

## Practical Example: Database Connection String

Let us put it all together with a realistic example. We will build an application that connects to a PostgreSQL database using environment variables.

### The Application Code

```javascript
// server.js
const express = require('express');
const app = express();

// Read ALL configuration from environment variables
const config = {
  port: process.env.PORT || 3000,
  env: process.env.NODE_ENV || 'development',
  db: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    name: process.env.DB_NAME || 'myapp',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || 'postgres',
  }
};

// Construct the connection string from individual variables
const connectionString =
  `postgresql://${config.db.user}:${config.db.password}` +
  `@${config.db.host}:${config.db.port}/${config.db.name}`;

app.get('/', (req, res) => {
  res.json({
    environment: config.env,
    database: {
      host: config.db.host,
      port: config.db.port,
      name: config.db.name,
      // Never expose the password in API responses!
      password: '********'
    }
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(config.port, '0.0.0.0', () => {
  console.log(`Server running on port ${config.port}`);
  console.log(`Environment: ${config.env}`);
  console.log(`Database: ${config.db.host}:${config.db.port}/${config.db.name}`);
  // Never log the password!
});
```

### The Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Set defaults for non-sensitive configuration
# These can be overridden at runtime with -e
ENV NODE_ENV=production \
    PORT=3000 \
    DB_PORT=5432

# Do NOT set defaults for sensitive values like DB_PASSWORD
# The app should fail clearly if they are not provided

COPY package.json package-lock.json ./
RUN npm ci --only=production

COPY . .

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

### Environment Files

```bash
# .env.development
NODE_ENV=development
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_dev
DB_USER=dev_user
DB_PASSWORD=dev_password_123
```

```bash
# .env.production
NODE_ENV=production
PORT=3000
DB_HOST=prod-db.mycompany.com
DB_PORT=5432
DB_NAME=myapp_production
DB_USER=prod_admin
DB_PASSWORD=Pr0d_Sup3r_S3cur3!
```

### Running in Different Environments

```bash
# Build the image once
$ docker build -t my-app:1.0 .

# Run in development
$ docker run -d -p 3000:3000 \
  --env-file .env.development \
  --name app-dev my-app:1.0

$ curl http://localhost:3000
{
  "environment": "development",
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "myapp_dev",
    "password": "********"
  }
}

$ docker stop app-dev && docker rm app-dev

# Run in production
$ docker run -d -p 3000:3000 \
  --env-file .env.production \
  --name app-prod my-app:1.0

$ curl http://localhost:3000
{
  "environment": "production",
  "database": {
    "host": "prod-db.mycompany.com",
    "port": 5432,
    "name": "myapp_production",
    "password": "********"
  }
}
```

### The Complete Configuration Flow

```
+--------------------------------------------------+
|    Configuration Flow                            |
+--------------------------------------------------+
|                                                  |
|    1. Dockerfile (ENV) sets defaults             |
|       NODE_ENV=production                        |
|       PORT=3000                                  |
|       DB_PORT=5432                               |
|                                                  |
|    2. .env file provides environment-specific    |
|       values (--env-file)                        |
|       DB_HOST=prod-db.mycompany.com              |
|       DB_USER=prod_admin                         |
|       DB_PASSWORD=Pr0d_Sup3r_S3cur3!             |
|                                                  |
|    3. -e flags override individual values        |
|       -e LOG_LEVEL=debug                         |
|                                                  |
|    4. Application reads process.env.*            |
|       and uses the final merged values           |
|                                                  |
|    Priority: -e > --env-file > ENV (Dockerfile)  |
|                                                  |
+--------------------------------------------------+
```

---

## Security Best Practices for Environment Variables

```
+--------------------------------------------------+
|    Environment Variable Security                 |
+--------------------------------------------------+
|                                                  |
|  DO:                                             |
|  - Use --env-file for secrets at runtime         |
|  - Add .env files to .gitignore                  |
|  - Use different credentials per environment     |
|  - Use Docker secrets or vault in production     |
|  - Set non-sensitive defaults in Dockerfile ENV  |
|                                                  |
|  DO NOT:                                         |
|  - Put secrets in Dockerfile ENV instructions    |
|  - Commit .env files to version control          |
|  - Log or print secret values                    |
|  - Return secrets in API responses               |
|  - Use ARG for secrets (visible in build history)|
|                                                  |
+--------------------------------------------------+
```

### Why ARG Is Not Safe for Secrets

```bash
# BAD: Using ARG for a secret
$ docker build --build-arg DB_PASSWORD=s3cret -t my-app .

# Anyone can see the build arg in the image history!
$ docker history my-app
IMAGE        CREATED    SIZE   COMMENT
a1b2c3d4     1 min      0B     ARG DB_PASSWORD=s3cret  <-- EXPOSED!
```

Build arguments are visible in `docker history`. Never use them for secrets.

---

## Common Mistakes

### Mistake 1: Hardcoding Configuration in Source Code

```javascript
// BAD: Hardcoded values
const DB_HOST = 'localhost';
const DB_PASSWORD = 'my_password';

// GOOD: Read from environment
const DB_HOST = process.env.DB_HOST;
const DB_PASSWORD = process.env.DB_PASSWORD;
```

### Mistake 2: Putting Secrets in Dockerfile ENV

```dockerfile
# BAD: Secret is baked into the image
ENV DB_PASSWORD=my_super_secret_password

# GOOD: No default for secrets. Set at runtime with -e
# ENV DB_PASSWORD is intentionally omitted
```

### Mistake 3: Committing .env Files to Git

```bash
# Always add .env files to .gitignore!
$ echo ".env" >> .gitignore
$ echo ".env.*" >> .gitignore
```

### Mistake 4: Not Providing Required Variables

```bash
# Your app expects DB_HOST but you forgot to set it
$ docker run my-app
# App crashes: "Error: DB_HOST environment variable is required"

# Solution: Always validate required environment variables
```

Here is how to validate in code:

```javascript
// Validate required environment variables at startup
const required = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME'];

for (const varName of required) {
  if (!process.env[varName]) {
    console.error(`ERROR: Required environment variable ${varName} is not set`);
    process.exit(1);
  }
}
```

### Mistake 5: Using the Wrong Type of Variable

```dockerfile
# BAD: Using ARG for runtime config
ARG PORT=3000
# PORT is NOT available when the container runs!

# GOOD: Using ENV for runtime config
ENV PORT=3000
# PORT IS available when the container runs
```

---

## Best Practices

1. **Read all configuration from environment variables.** Never hardcode values that change between environments.

2. **Set sensible defaults with ENV** for non-sensitive configuration like PORT and LOG_LEVEL.

3. **Never put secrets in ENV or ARG.** Pass them at runtime with `-e` or `--env-file`.

4. **Use separate .env files** for each environment (development, staging, production).

5. **Add .env files to .gitignore** to prevent accidentally committing secrets.

6. **Validate required variables** at application startup and fail fast with clear error messages.

7. **Never log or expose secrets** in responses, error messages, or console output.

8. **Use ARG for build-time decisions** only, like choosing a base image version.

---

## Quick Summary

Environment variables are the standard way to configure Docker containers. The `ENV` instruction in a Dockerfile sets defaults that can be overridden at runtime. The `-e` flag sets individual variables, while `--env-file` loads them from a file. Build-time variables use `ARG` and `--build-arg` and are only available during the build process. Following the Twelve-Factor App principle, configuration should always live outside your code.

---

## Key Points

- Configuration should live outside your code (Twelve-Factor App, Factor 3)
- `-e KEY=VALUE` sets a single environment variable at runtime
- `--env-file .env` loads multiple variables from a file
- `ENV` in a Dockerfile sets defaults that can be overridden at runtime
- `ARG` in a Dockerfile defines build-time variables (not available at runtime)
- Priority order: `-e` flag > `--env-file` > `ENV` in Dockerfile
- Never put secrets in `ENV` or `ARG` instructions
- Never commit `.env` files to version control
- Always validate required environment variables at application startup
- Use separate `.env` files for each environment

---

## Practice Questions

1. What is the Twelve-Factor App principle about configuration? Why should configuration live outside your code?

2. What is the difference between `ARG` and `ENV` in a Dockerfile? Give an example of when you would use each.

3. You have a Dockerfile with `ENV PORT=3000` and you run the container with `docker run -e PORT=8080 my-app`. What port does the application see? Why?

4. Why should you never put passwords or API keys in a Dockerfile's `ENV` instruction? What should you do instead?

5. You run `docker build --build-arg SECRET_KEY=abc123 -t my-app .`. Is this safe? Why or why not?

---

## Exercises

### Exercise 1: Environment Variable Basics

1. Create a simple application that reads three environment variables: `APP_NAME`, `APP_VERSION`, and `GREETING`
2. Write a Dockerfile with `ENV` defaults for `APP_NAME` and `APP_VERSION`
3. Build the image and run it three ways:
   - With no overrides (use defaults)
   - With `-e` overriding `GREETING`
   - With `--env-file` providing all three values

### Exercise 2: Multi-Environment Setup

1. Create an application that connects to a database (you can fake the connection)
2. Create three `.env` files: `.env.development`, `.env.staging`, `.env.production`
3. Each file should have different values for `DB_HOST`, `DB_NAME`, and `DB_USER`
4. Run the same image with each `.env` file and verify the different configurations

### Exercise 3: Build Arguments

1. Create a Dockerfile that uses `ARG` to specify the Node.js version
2. Build the image three times with different Node.js versions (16, 18, 20)
3. Verify each image uses the correct version by running `docker run image node --version`
4. Try to access the ARG variable at runtime. What happens?

---

## What Is Next?

Now you know how to configure your containers without hardcoding values. But there is another important problem to solve: data persistence. When a container is removed, all its data is lost. In the next chapter, you will learn about Docker volumes -- the solution for persistent data. You will learn how to keep your database data, uploaded files, and logs safe even when containers come and go.
