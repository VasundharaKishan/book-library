# Chapter 29: Externalized Configuration

## What You Will Learn

- What externalized configuration is and why it matters.
- The complete Spring Boot configuration hierarchy (which source wins).
- How to use environment variables with `${DB_PASSWORD}` syntax.
- How to set default values for missing properties.
- How to use profiles to configure different environments.
- How to create type-safe configuration with `@ConfigurationProperties`.
- How to validate configuration with `@Validated`.
- How to use `.env` files for local development.
- How to manage secrets safely in production.

## Why This Chapter Matters

Imagine you are a chef who works at three restaurants. Each restaurant has a different kitchen, different ovens, and different ingredients. But you cook the same recipes. You do not rewrite your recipes for each restaurant. Instead, you adjust the settings: oven temperature, ingredient quantities, cooking times.

Software applications work the same way. Your code (the recipe) stays the same, but the configuration (the settings) changes for each environment:

- **Development**: Use a local H2 database, show SQL queries, log everything.
- **Staging**: Use a test database, hide SQL, log warnings and errors.
- **Production**: Use the real database, strict security, minimal logging.

Externalized configuration means keeping your settings outside your code. You change the settings without touching, recompiling, or redeploying your code.

This chapter teaches you how to manage configuration like a professional. You will learn the right way to handle database passwords, API keys, and environment-specific settings.

---

## 29.1 The Configuration Hierarchy

Spring Boot reads configuration from many sources. When the same property is defined in multiple places, the one with higher priority wins.

### Priority Order (Highest to Lowest)

```
Priority (highest wins):

  1. Command-line arguments         --server.port=9090
  2. Java system properties         -Dserver.port=9090
  3. OS environment variables       SERVER_PORT=9090
  4. Profile-specific properties    application-prod.properties
  5. application.properties         server.port=8080
  6. @PropertySource annotations    Custom property files
  7. Default properties             SpringApplication defaults

If server.port is set in BOTH environment variables (9090)
AND application.properties (8080), the environment variable
wins because it has higher priority.
```

Think of it like a stack of transparent sheets. Each sheet can have values written on it. You look down through the stack. The first value you see wins.

```
+------------------------------+  <-- Highest Priority
| Command-line arguments       |  --server.port=9090
+------------------------------+
| OS environment variables     |  SERVER_PORT=9090
+------------------------------+
| application-prod.properties  |  server.port=8085
+------------------------------+
| application.properties       |  server.port=8080
+------------------------------+  <-- Lowest Priority

Question: What is server.port?
Answer: 9090 (command-line wins!)
```

### Why This Hierarchy Exists

This hierarchy lets you:

1. Set **default values** in `application.properties` (committed to Git).
2. Override for specific **environments** with profiles (committed to Git).
3. Override **secrets** with environment variables (never in Git).
4. Override **anything** from the command line (for quick fixes).

---

## 29.2 Environment Variables

Environment variables are the most common way to pass configuration in production. They are set outside your application and are available to any process on the system.

### Setting Environment Variables

```bash
# Linux/Mac
export DB_HOST=localhost
export DB_PORT=5432
export DB_USERNAME=admin
export DB_PASSWORD=superSecret123

# Windows (Command Prompt)
set DB_HOST=localhost
set DB_PORT=5432

# Windows (PowerShell)
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
```

### Using Environment Variables in application.properties

```properties
# application.properties

spring.datasource.url=jdbc:postgresql://${DB_HOST}:${DB_PORT}/bookstore
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}
```

The `${...}` syntax tells Spring Boot to look for an environment variable with that name.

```
How ${DB_HOST} Gets Resolved:

application.properties:
  spring.datasource.url=jdbc:postgresql://${DB_HOST}:${DB_PORT}/bookstore

Environment Variables:
  DB_HOST=prod-db.example.com
  DB_PORT=5432

Resolved Value:
  spring.datasource.url=jdbc:postgresql://prod-db.example.com:5432/bookstore
```

### Default Values

What if an environment variable is not set? Your app will fail to start. To prevent this, use default values:

```properties
# Syntax: ${VARIABLE_NAME:defaultValue}

spring.datasource.url=jdbc:h2:mem:bookstore
spring.datasource.username=${DB_USERNAME:sa}
spring.datasource.password=${DB_PASSWORD:}

server.port=${SERVER_PORT:8080}

app.email.from=${EMAIL_FROM:noreply@bookstore.com}
app.max-upload-size=${MAX_UPLOAD_MB:10}
```

The colon (`:`) separates the variable name from the default value. If `DB_USERNAME` is not set, Spring uses `sa`.

```
Default Value Resolution:

${DB_USERNAME:sa}
       |       |
       |       +-- Default value: "sa"
       +---------- Variable name: DB_USERNAME

If DB_USERNAME is set    -> Use its value
If DB_USERNAME is NOT set -> Use "sa"
```

### Environment Variable Naming Convention

Spring Boot automatically maps property names to environment variable names:

| Property Name | Environment Variable |
|---|---|
| `server.port` | `SERVER_PORT` |
| `spring.datasource.url` | `SPRING_DATASOURCE_URL` |
| `app.email.from` | `APP_EMAIL_FROM` |
| `my.custom-property` | `MY_CUSTOM_PROPERTY` or `MY_CUSTOMPROPERTY` |

The rules are simple:
1. Replace dots (`.`) with underscores (`_`).
2. Replace hyphens (`-`) with underscores (`_`).
3. Convert to uppercase.

---

## 29.3 Profiles

Profiles let you have different configurations for different environments, all within the same project.

### How Profiles Work

```
application.properties            <- Always loaded (defaults)
application-dev.properties        <- Loaded when profile = "dev"
application-staging.properties    <- Loaded when profile = "staging"
application-prod.properties       <- Loaded when profile = "prod"

Profile-specific files OVERRIDE application.properties.
```

### Creating Profile-Specific Files

```properties
# src/main/resources/application.properties (defaults)

spring.application.name=BookStore
server.port=8080

# Default: H2 database
spring.datasource.url=jdbc:h2:mem:bookstore
spring.datasource.driver-class-name=org.h2.Driver
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=false

logging.level.root=INFO
```

```properties
# src/main/resources/application-dev.properties

# Development overrides
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.h2.console.enabled=true
logging.level.com.example=DEBUG
logging.level.org.hibernate.SQL=DEBUG
```

```properties
# src/main/resources/application-staging.properties

# Staging overrides
spring.datasource.url=jdbc:postgresql://${DB_HOST:staging-db}:5432/bookstore
spring.datasource.driver-class-name=org.postgresql.Driver
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}
spring.jpa.hibernate.ddl-auto=validate
logging.level.com.example=INFO
```

```properties
# src/main/resources/application-prod.properties

# Production overrides
spring.datasource.url=jdbc:postgresql://${DB_HOST}:5432/bookstore
spring.datasource.driver-class-name=org.postgresql.Driver
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}
spring.jpa.hibernate.ddl-auto=none
spring.jpa.show-sql=false
logging.level.com.example=WARN

# Actuator security
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when-authorized
```

### Activating a Profile

There are several ways to activate a profile:

```properties
# Option 1: In application.properties
spring.profiles.active=dev
```

```bash
# Option 2: Environment variable
export SPRING_PROFILES_ACTIVE=prod
```

```bash
# Option 3: Command-line argument
java -jar bookstore.jar --spring.profiles.active=prod
```

```bash
# Option 4: JVM system property
java -Dspring.profiles.active=prod -jar bookstore.jar
```

### Multiple Active Profiles

You can activate multiple profiles at once:

```bash
# Activate both "prod" and "email" profiles
java -jar bookstore.jar --spring.profiles.active=prod,email
```

### Using @Profile in Java Code

You can make beans available only for specific profiles:

```java
@Configuration
public class DataSourceConfig {

    @Bean
    @Profile("dev")                             // Only in dev
    public DataSource devDataSource() {
        // H2 in-memory database
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .build();
    }

    @Bean
    @Profile("prod")                            // Only in prod
    public DataSource prodDataSource() {
        // Real PostgreSQL database
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl(System.getenv("DB_URL"));
        ds.setUsername(System.getenv("DB_USERNAME"));
        ds.setPassword(System.getenv("DB_PASSWORD"));
        return ds;
    }
}
```

```
Profile-Based Bean Loading:

Profile = "dev":                   Profile = "prod":
+-------------------+             +-------------------+
| devDataSource     | LOADED      | devDataSource     | SKIPPED
| (H2 in-memory)   |             | (H2 in-memory)   |
+-------------------+             +-------------------+
| prodDataSource    | SKIPPED     | prodDataSource    | LOADED
| (PostgreSQL)      |             | (PostgreSQL)      |
+-------------------+             +-------------------+
```

---

## 29.4 Type-Safe Configuration with @ConfigurationProperties

Using `@Value` annotations everywhere is messy and error-prone. `@ConfigurationProperties` is a better approach that maps properties to a Java class.

### The Problem with @Value

```java
// Messy: @Value scattered across multiple classes
@Service
public class EmailService {

    @Value("${app.email.from}")
    private String from;

    @Value("${app.email.host}")
    private String host;

    @Value("${app.email.port}")
    private int port;

    @Value("${app.email.username}")
    private String username;

    // What if you misspell a property name?
    // No error until runtime!
    @Value("${app.email.pasword}")  // Typo! Missing 's'
    private String password;         // Fails at runtime
}
```

### The Solution: @ConfigurationProperties

```java
// src/main/java/com/example/bookstore/config/EmailProperties.java

package com.example.bookstore.config;

import org.springframework.boot.context.properties
    .ConfigurationProperties;                                // 1
import org.springframework.stereotype.Component;

@Component                                                   // 2
@ConfigurationProperties(prefix = "app.email")               // 3
public class EmailProperties {

    private String from;                                     // 4
    private String host;
    private int port;
    private String username;
    private String password;

    // Getters and Setters (required!)                       // 5

    public String getFrom() { return from; }
    public void setFrom(String from) { this.from = from; }

    public String getHost() { return host; }
    public void setHost(String host) { this.host = host; }

    public int getPort() { return port; }
    public void setPort(int port) { this.port = port; }

    public String getUsername() { return username; }
    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() { return password; }
    public void setPassword(String password) {
        this.password = password;
    }
}
```

**Line-by-line explanation:**

- **Line 1**: Import `@ConfigurationProperties`.
- **Line 2**: `@Component` registers this as a Spring bean.
- **Line 3**: `@ConfigurationProperties(prefix = "app.email")` maps all properties starting with `app.email` to fields in this class.
- **Line 4**: Each field maps to a property. `from` maps to `app.email.from`.
- **Line 5**: Getters and setters are required for `@ConfigurationProperties` to bind the values.

### The Properties File

```properties
# application.properties

app.email.from=noreply@bookstore.com
app.email.host=smtp.gmail.com
app.email.port=587
app.email.username=bookstore@gmail.com
app.email.password=${EMAIL_PASSWORD:default}
```

### Property to Field Mapping

```
application.properties:          EmailProperties.java:

app.email.from = noreply@...     private String from;
app.email.host = smtp.gmail...   private String host;
app.email.port = 587             private int port;
app.email.username = book...     private String username;
app.email.password = ${...}      private String password;

The prefix "app.email" is stripped.
The remaining part maps to the field name.
```

### Using the Properties Class

```java
@Service
public class EmailService {

    private final EmailProperties emailProperties;       // 1

    public EmailService(EmailProperties emailProperties) {
        this.emailProperties = emailProperties;          // 2
    }

    public void sendEmail(String to, String subject,
                          String body) {
        System.out.println("Sending from: "
            + emailProperties.getFrom());                // 3
        System.out.println("Using host: "
            + emailProperties.getHost());
        System.out.println("On port: "
            + emailProperties.getPort());
    }
}
```

### Nested Properties

You can nest property groups:

```properties
# application.properties

app.email.from=noreply@bookstore.com
app.email.host=smtp.gmail.com
app.email.retry.max-attempts=3
app.email.retry.delay-ms=1000
```

```java
@Component
@ConfigurationProperties(prefix = "app.email")
public class EmailProperties {

    private String from;
    private String host;
    private Retry retry = new Retry();    // Nested class

    // Getters and setters for from and host...

    public Retry getRetry() { return retry; }
    public void setRetry(Retry retry) { this.retry = retry; }

    public static class Retry {                        // 1
        private int maxAttempts = 3;                   // 2
        private long delayMs = 1000;

        public int getMaxAttempts() { return maxAttempts; }
        public void setMaxAttempts(int maxAttempts) {
            this.maxAttempts = maxAttempts;
        }

        public long getDelayMs() { return delayMs; }
        public void setDelayMs(long delayMs) {
            this.delayMs = delayMs;
        }
    }
}
```

- **Line 1**: A static inner class for the nested group `retry`.
- **Line 2**: Default values are set in the field declaration.

Usage:

```java
int maxRetries = emailProperties.getRetry().getMaxAttempts();
long delay = emailProperties.getRetry().getDelayMs();
```

### List and Map Properties

```properties
# application.properties

# List of allowed email domains
app.email.allowed-domains[0]=gmail.com
app.email.allowed-domains[1]=yahoo.com
app.email.allowed-domains[2]=outlook.com

# Map of rate limits per domain
app.email.rate-limits.gmail.com=100
app.email.rate-limits.yahoo.com=50
app.email.rate-limits.outlook.com=75
```

```java
@Component
@ConfigurationProperties(prefix = "app.email")
public class EmailProperties {

    private List<String> allowedDomains = new ArrayList<>();
    private Map<String, Integer> rateLimits = new HashMap<>();

    public List<String> getAllowedDomains() {
        return allowedDomains;
    }
    public void setAllowedDomains(List<String> allowedDomains) {
        this.allowedDomains = allowedDomains;
    }

    public Map<String, Integer> getRateLimits() {
        return rateLimits;
    }
    public void setRateLimits(Map<String, Integer> rateLimits) {
        this.rateLimits = rateLimits;
    }
}
```

---

## 29.5 Validating Configuration with @Validated

What if someone forgets to set a required property? Without validation, your application starts but fails later with a confusing error. With `@Validated`, Spring checks your configuration at startup and gives a clear error message.

### Add the Validation Dependency

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

### Add Validation Annotations

```java
// src/main/java/com/example/bookstore/config/EmailProperties.java

package com.example.bookstore.config;

import jakarta.validation.constraints.*;                     // 1
import org.springframework.boot.context.properties
    .ConfigurationProperties;
import org.springframework.stereotype.Component;
import org.springframework.validation.annotation.Validated;  // 2

@Component
@ConfigurationProperties(prefix = "app.email")
@Validated                                                   // 3
public class EmailProperties {

    @NotBlank(message = "Email 'from' address is required")  // 4
    private String from;

    @NotBlank(message = "SMTP host is required")
    private String host;

    @Min(value = 1, message = "Port must be at least 1")     // 5
    @Max(value = 65535,
         message = "Port must be at most 65535")
    private int port;

    @NotBlank(message = "Username is required")
    private String username;

    @NotBlank(message = "Password is required")              // 6
    private String password;

    // Getters and setters...
    public String getFrom() { return from; }
    public void setFrom(String from) { this.from = from; }

    public String getHost() { return host; }
    public void setHost(String host) { this.host = host; }

    public int getPort() { return port; }
    public void setPort(int port) { this.port = port; }

    public String getUsername() { return username; }
    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() { return password; }
    public void setPassword(String password) {
        this.password = password;
    }
}
```

**Key annotations:**

- **Line 1**: Import Jakarta Validation constraints.
- **Line 2**: Import `@Validated`.
- **Line 3**: `@Validated` enables validation on this properties class.
- **Line 4**: `@NotBlank` ensures the value is not null, not empty, and not just whitespace.
- **Line 5**: `@Min` and `@Max` set a valid range for numeric fields.
- **Line 6**: If `password` is blank, the app fails to start with a clear error message.

### What Happens When Validation Fails

If `app.email.from` is missing:

```
***************************
APPLICATION FAILED TO START
***************************

Description:

Binding to target org.springframework.boot.context.properties
.bind.BindException: Failed to bind properties under
'app.email' to com.example.bookstore.config.EmailProperties

    Property: app.email.from
    Value: null
    Reason: Email 'from' address is required

Action:

Update your application's configuration
```

This is much better than a `NullPointerException` ten minutes after startup.

```
Without @Validated:                With @Validated:

App starts successfully            App FAILS to start
         |                                 |
   10 minutes later...             Clear error message:
         |                         "Email 'from' is required"
   NullPointerException!                   |
   "What went wrong??"            Fix it immediately!
```

---

## 29.6 Using .env Files for Local Development

In development, you do not want to set environment variables manually every time. A `.env` file stores environment variables in a file that your application reads at startup.

### Step 1: Create a .env File

```bash
# .env (in the project root)

DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=admin
DB_PASSWORD=localDevPassword123
EMAIL_PASSWORD=myAppPassword
API_KEY=dev-api-key-12345
```

### Step 2: Add .env to .gitignore

This is critical. Never commit `.env` files to version control.

```gitignore
# .gitignore

.env
*.env
.env.local
```

### Step 3: Load .env in Spring Boot

Spring Boot does not load `.env` files by default. You have a few options:

**Option A: Use spring-dotenv library**

```xml
<!-- pom.xml -->
<dependency>
    <groupId>me.paulschwarz</groupId>
    <artifactId>spring-dotenv</artifactId>
    <version>4.0.0</version>
</dependency>
```

This automatically loads `.env` files. No additional code needed.

**Option B: Load .env with a shell script**

```bash
# run-dev.sh
#!/bin/bash
export $(cat .env | grep -v '^#' | xargs)
./mvnw spring-boot:run
```

**Option C: Use IntelliJ IDEA / VS Code**

Most IDEs let you specify an `.env` file in the run configuration. Check your IDE's documentation for details.

### Referencing .env Variables

```properties
# application.properties

spring.datasource.url=jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/bookstore
spring.datasource.username=${DB_USERNAME:sa}
spring.datasource.password=${DB_PASSWORD:}

app.api-key=${API_KEY:default-key}
```

```
How .env Works in Development:

+----------+     +-------------------+     +------------------+
| .env     |     | Environment       |     | application      |
| file     |---->| Variables         |---->| .properties      |
|          |     | (loaded into OS)  |     | ${DB_HOST} = ... |
| DB_HOST= |     |                   |     |                  |
| localhost|     | DB_HOST=localhost  |     | Resolved!        |
+----------+     +-------------------+     +------------------+
```

---

## 29.7 Secrets Management

Secrets are sensitive values like database passwords, API keys, and encryption keys. Managing them correctly is critical for security.

### What NOT to Do

```
NEVER DO THESE:

1. Hardcode secrets in Java code
   private String password = "myPassword123";

2. Commit secrets to Git
   spring.datasource.password=productionPassword!

3. Share secrets in chat messages or emails

4. Use the same secrets in development and production

5. Store secrets in plain text on servers
```

### The Secrets Hierarchy

```
+------------------------------------------+
|  Most Secure (Production)                |
|                                          |
|  Secrets Manager (AWS, Azure, Vault)     |
|  - Encrypted at rest                     |
|  - Access control                        |
|  - Audit logging                         |
|  - Automatic rotation                    |
+------------------------------------------+
|  Secure (Staging / CI/CD)                |
|                                          |
|  Environment Variables                   |
|  - Set in CI/CD pipeline                |
|  - Set in container orchestration        |
|  - Not in source code                    |
+------------------------------------------+
|  Acceptable (Development)                |
|                                          |
|  .env files (in .gitignore)              |
|  - Local to developer machine           |
|  - Never committed to Git               |
+------------------------------------------+
|  NEVER (Anywhere)                        |
|                                          |
|  Hardcoded in source code                |
|  Committed to Git                        |
+------------------------------------------+
```

### Strategy 1: Environment Variables (Simple)

```bash
# Set in your deployment environment
export DB_PASSWORD=superSecretProd123
export JWT_SECRET=myJwtSigningKey456
export API_KEY=prod-api-key-789
```

```properties
# application.properties
spring.datasource.password=${DB_PASSWORD}
app.jwt.secret=${JWT_SECRET}
app.api.key=${API_KEY}
```

### Strategy 2: Using Spring Cloud Config

For larger applications, Spring Cloud Config provides a central configuration server:

```
+----------------+       +-----------+       +-----------+
| Config Server  |<----->| Git Repo  |       | App 1     |
| (centralized)  |       | (config   |<----->| reads     |
|                |       |  files)   |       | config    |
+----------------+       +-----------+       +-----------+
        |                                    +-----------+
        +<---------------------------------->| App 2     |
        |                                    | reads     |
        |                                    | config    |
        |                                    +-----------+
        +<---------------------------------->+-----------+
                                             | App 3     |
                                             | reads     |
                                             | config    |
                                             +-----------+
```

### Strategy 3: Vault Integration

HashiCorp Vault is a popular tool for managing secrets:

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-vault-config</artifactId>
</dependency>
```

```properties
# application.properties
spring.cloud.vault.uri=https://vault.example.com:8200
spring.cloud.vault.token=${VAULT_TOKEN}
spring.cloud.vault.kv.backend=secret
```

This is an advanced topic, but knowing it exists is important for production applications.

---

## 29.8 A Complete Configuration Example

Here is a real-world example bringing together everything in this chapter.

### The Configuration Properties Class

```java
// src/main/java/com/example/bookstore/config/AppProperties.java

package com.example.bookstore.config;

import jakarta.validation.constraints.*;
import org.springframework.boot.context.properties
    .ConfigurationProperties;
import org.springframework.stereotype.Component;
import org.springframework.validation.annotation.Validated;

import java.util.List;

@Component
@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {

    @NotBlank
    private String name;

    @NotBlank
    private String version;

    private Security security = new Security();
    private Cors cors = new Cors();

    // Getters and setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getVersion() { return version; }
    public void setVersion(String version) {
        this.version = version;
    }
    public Security getSecurity() { return security; }
    public void setSecurity(Security security) {
        this.security = security;
    }
    public Cors getCors() { return cors; }
    public void setCors(Cors cors) { this.cors = cors; }

    public static class Security {
        @NotBlank
        private String jwtSecret;

        @Min(300)   // At least 5 minutes
        @Max(86400) // At most 24 hours
        private long jwtExpirationSeconds = 3600;

        public String getJwtSecret() { return jwtSecret; }
        public void setJwtSecret(String jwtSecret) {
            this.jwtSecret = jwtSecret;
        }
        public long getJwtExpirationSeconds() {
            return jwtExpirationSeconds;
        }
        public void setJwtExpirationSeconds(
                long jwtExpirationSeconds) {
            this.jwtExpirationSeconds = jwtExpirationSeconds;
        }
    }

    public static class Cors {
        private List<String> allowedOrigins =
            List.of("http://localhost:3000");
        private List<String> allowedMethods =
            List.of("GET", "POST", "PUT", "DELETE");

        public List<String> getAllowedOrigins() {
            return allowedOrigins;
        }
        public void setAllowedOrigins(
                List<String> allowedOrigins) {
            this.allowedOrigins = allowedOrigins;
        }
        public List<String> getAllowedMethods() {
            return allowedMethods;
        }
        public void setAllowedMethods(
                List<String> allowedMethods) {
            this.allowedMethods = allowedMethods;
        }
    }
}
```

### The Properties Files

```properties
# application.properties (defaults)

app.name=BookStore
app.version=1.0.0
app.security.jwt-secret=${JWT_SECRET:dev-secret-key-for-local-only}
app.security.jwt-expiration-seconds=3600
app.cors.allowed-origins=http://localhost:3000

spring.datasource.url=jdbc:h2:mem:bookstore
spring.datasource.driver-class-name=org.h2.Driver
spring.jpa.hibernate.ddl-auto=update
```

```properties
# application-dev.properties

spring.jpa.show-sql=true
spring.h2.console.enabled=true
logging.level.com.example=DEBUG
```

```properties
# application-prod.properties

spring.datasource.url=jdbc:postgresql://${DB_HOST}:${DB_PORT:5432}/bookstore
spring.datasource.driver-class-name=org.postgresql.Driver
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}
spring.jpa.hibernate.ddl-auto=none

app.security.jwt-secret=${JWT_SECRET}
app.security.jwt-expiration-seconds=1800
app.cors.allowed-origins=${CORS_ORIGINS:https://bookstore.com}

logging.level.com.example=WARN
```

### The .env File (Development Only)

```bash
# .env (never committed to Git)

JWT_SECRET=local-dev-secret-key-abc123
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=dev_user
DB_PASSWORD=dev_password
```

### Using the Properties

```java
@RestController
@RequestMapping("/api/config")
public class ConfigCheckController {

    private final AppProperties appProperties;

    public ConfigCheckController(AppProperties appProperties) {
        this.appProperties = appProperties;
    }

    @GetMapping("/info")
    public Map<String, Object> getInfo() {
        return Map.of(
            "name", appProperties.getName(),
            "version", appProperties.getVersion(),
            "jwtExpiration",
                appProperties.getSecurity()
                    .getJwtExpirationSeconds(),
            "corsOrigins",
                appProperties.getCors()
                    .getAllowedOrigins()
        );
    }
}
```

**Output:**

```json
{
  "name": "BookStore",
  "version": "1.0.0",
  "jwtExpiration": 3600,
  "corsOrigins": ["http://localhost:3000"]
}
```

---

## Common Mistakes

### Mistake 1: Committing Secrets to Git

```properties
# WRONG: Real password in version control
spring.datasource.password=prodPassword123!
```

```properties
# CORRECT: Use environment variables
spring.datasource.password=${DB_PASSWORD}
```

Even if you later remove the secret and commit, it is still in the Git history. If this happens, consider the secret compromised and rotate it immediately.

### Mistake 2: No Default Values for Optional Properties

```properties
# WRONG: App crashes if SERVER_PORT is not set
server.port=${SERVER_PORT}
```

```properties
# CORRECT: Provide a sensible default
server.port=${SERVER_PORT:8080}
```

### Mistake 3: Using @Value for Complex Configuration

```java
// WRONG: Scattered @Value annotations
@Value("${app.email.from}") private String from;
@Value("${app.email.host}") private String host;
@Value("${app.email.port}") private int port;
@Value("${app.email.username}") private String username;
@Value("${app.email.password}") private String password;
```

```java
// CORRECT: One @ConfigurationProperties class
private final EmailProperties emailProperties;
// All properties in one place, type-safe, validated
```

### Mistake 4: Same Secrets in All Environments

```
WRONG:
  Dev password:  "password123"
  Staging password: "password123"    <- Same!
  Prod password: "password123"      <- Same!

CORRECT:
  Dev password:  "devLocalPass"
  Staging password: "stg_Xk9mP2vB"  <- Different
  Prod password: "prd_Qw7nR4jT"     <- Different
```

### Mistake 5: Not Validating Required Configuration

```java
// WRONG: No validation, fails at runtime
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String apiKey;  // Could be null!
}
```

```java
// CORRECT: Fails at startup with clear error
@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    @NotBlank(message = "API key is required")
    private String apiKey;
}
```

---

## Best Practices

1. **Use @ConfigurationProperties over @Value.** It is type-safe, supports validation, and keeps configuration organized.

2. **Always provide default values** for properties that have sensible defaults. Use `${VAR:default}` syntax.

3. **Never commit secrets to Git.** Use environment variables, `.env` files (in `.gitignore`), or a secrets manager.

4. **Validate configuration at startup.** Use `@Validated` with Jakarta Validation annotations. Fail fast with a clear error.

5. **Use profiles for environment-specific configuration.** Keep defaults in `application.properties` and overrides in `application-{profile}.properties`.

6. **Use different secrets for each environment.** Development, staging, and production should each have unique passwords and keys.

7. **Document required environment variables.** Maintain a list of required environment variables (without values) so new developers know what to set up.

8. **Use a secrets manager in production.** For serious production applications, use AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault instead of plain environment variables.

---

## Quick Summary

In this chapter, you learned how to manage configuration in Spring Boot applications like a professional. You explored the configuration hierarchy, understanding which source takes priority when the same property is defined in multiple places. You used environment variables with `${DB_PASSWORD}` syntax to keep secrets out of your code. You set default values with `${VAR:default}` to handle missing properties gracefully. You used profiles to create environment-specific configurations for dev, staging, and production. You created type-safe configuration classes with `@ConfigurationProperties` and validated them with `@Validated`. You learned about `.env` files for local development and secrets management strategies for production.

---

## Key Points

| Concept | Description |
|---|---|
| Configuration Hierarchy | Command-line > env vars > profile properties > application.properties |
| `${VAR_NAME}` | References an environment variable in properties files |
| `${VAR:default}` | Provides a default value if the variable is not set |
| Profiles | Environment-specific config (application-dev.properties, etc.) |
| `spring.profiles.active` | Activates a specific profile |
| `@ConfigurationProperties` | Maps a group of properties to a type-safe Java class |
| `@Validated` | Enables Jakarta Validation on a configuration class |
| `.env` file | Stores environment variables for local development |
| `.gitignore` | Must include `.env` to prevent committing secrets |
| Secrets Manager | Production tool for secure secret storage (Vault, AWS SM) |

---

## Practice Questions

1. Explain the Spring Boot configuration hierarchy. If `server.port` is set to `8080` in `application.properties` and to `9090` as an environment variable, which value does the application use? Why?

2. What is the difference between `${DB_PASSWORD}` and `${DB_PASSWORD:secret}` in `application.properties`? When would you use each syntax?

3. How does `@ConfigurationProperties` differ from `@Value`? List at least three advantages of using `@ConfigurationProperties`.

4. Why should you add `@Validated` to your `@ConfigurationProperties` class? What happens when a required property is missing?

5. Why should `.env` files never be committed to version control? What should you use instead in production?

---

## Exercises

### Exercise 1: Multi-Profile Application

Create a Spring Boot application with three profiles: `dev`, `staging`, and `prod`. Each profile should configure:
- A different database (H2 for dev, PostgreSQL for staging and prod).
- Different logging levels (DEBUG for dev, INFO for staging, WARN for prod).
- Different server ports (8080 for dev, 8081 for staging, 80 for prod).

Test each profile by running the application and verifying the correct settings.

### Exercise 2: Type-Safe File Upload Configuration

Create a `@ConfigurationProperties` class called `FileUploadProperties` with:
- `maxFileSize` (validated: between 1 MB and 100 MB).
- `allowedTypes` (a list of strings like "jpg", "png", "pdf").
- `uploadDirectory` (validated: not blank).
- `maxFilesPerUpload` (validated: between 1 and 20).

Add `@Validated` and test that the application fails to start with clear error messages when invalid values are provided.

### Exercise 3: Secrets Setup

Set up a local development environment with:
1. A `.env` file containing `DB_PASSWORD`, `JWT_SECRET`, and `API_KEY`.
2. `application.properties` referencing these variables with defaults.
3. `.gitignore` excluding the `.env` file.
4. A `README-env.md` file documenting all required environment variables (names only, no values).

Verify that the application starts correctly with and without the `.env` file (using defaults).

---

## What Is Next?

You now know how to configure your application for any environment. But how do you actually deploy it? How do you package it so it runs on any server? In the next chapter, we will learn about **Docker and Deployment**. You will containerize your application with Docker, create production-ready builds, and set up automated deployment pipelines.
