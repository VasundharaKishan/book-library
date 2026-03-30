# Chapter 8: Properties and Profiles

## What You Will Learn

In this chapter, you will learn:

- The difference between `.properties` and `.yml` configuration files
- The most common Spring Boot properties
- How to read property values using `@Value`
- How to group related properties using `@ConfigurationProperties`
- What profiles are and why you need them
- How to create profile-specific configuration files
- How to activate profiles
- The order in which Spring resolves properties

## Why This Chapter Matters

Imagine you are building a house. The blueprint is the same, but the materials change depending on where you build. In a cold climate, you use thick insulation. In a warm climate, you use lighter materials. The house design stays the same. Only the materials change.

Software works the same way. Your code stays the same. But the configuration changes depending on where the application runs. On your laptop, you connect to a local test database. On the production server, you connect to the real database. On a test server, you connect to a mock database.

Without proper configuration management, you would need to change your code every time you deploy to a different environment. That is risky and error-prone. Spring Boot profiles and properties solve this problem elegantly.

---

## 8.1 Properties Files: .properties vs .yml

Spring Boot reads configuration from files in your `src/main/resources` folder. You have two format choices.

### The .properties Format

This is the traditional Java format. Each setting is a key-value pair on its own line.

```properties
# src/main/resources/application.properties

# Server settings
server.port=8081
server.servlet.context-path=/api

# Application info
app.name=BookStore
app.version=1.0.0

# Database settings
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.username=sa
spring.datasource.password=
```

**Key-value pair** means a setting name (key) and its value, separated by an equals sign. `server.port=8081` means "the server port is 8081."

The `#` symbol starts a comment. Spring ignores everything after it on that line.

### The .yml (YAML) Format

YAML stands for "YAML Ain't Markup Language." It uses indentation instead of dots to show hierarchy.

```yaml
# src/main/resources/application.yml

# Server settings
server:
  port: 8081
  servlet:
    context-path: /api

# Application info
app:
  name: BookStore
  version: 1.0.0

# Database settings
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    username: sa
    password:
```

### Side-by-Side Comparison

```
.properties                          .yml
─────────────────────               ─────────────────────
server.port=8081                    server:
server.servlet.context-path=/api      port: 8081
                                      servlet:
                                        context-path: /api

app.name=BookStore                  app:
app.version=1.0.0                     name: BookStore
                                      version: 1.0.0
```

### Which Format Should You Choose?

| Feature            | .properties              | .yml                    |
|--------------------|--------------------------|-------------------------|
| Readability        | Good for flat settings   | Better for nested settings |
| Hierarchy          | Uses dots                | Uses indentation        |
| Learning curve     | Easier for beginners     | Slightly harder         |
| Multiple docs      | Not supported            | Supports `---` separator |
| Whitespace matters | No                       | Yes (indentation)       |

> **Recommendation for beginners:** Start with `.properties`. It is simpler and harder to mess up. Indentation errors in YAML can cause hard-to-find bugs.

> **Important:** Do not use both `application.properties` and `application.yml` at the same time. Pick one format and stick with it. If both exist, `.properties` takes priority.

---

## 8.2 Common Spring Boot Properties

Here are the most frequently used properties. You do not need to memorize them. Bookmark this page and come back when needed.

### Server Properties

```properties
# Change the port (default is 8080)
server.port=8081

# Add a base path to all URLs
server.servlet.context-path=/api

# Set connection timeout
server.tomcat.connection-timeout=5000
```

**Port** is a number that identifies your application on the network. Think of it like an apartment number. The computer is the building. The port is the apartment. Port 8080 is the default apartment where Spring Boot lives.

### Database Properties

```properties
# H2 in-memory database
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# Enable H2 web console
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
```

### JPA and Hibernate Properties

```properties
# Show SQL queries in the console
spring.jpa.show-sql=true

# Format SQL output for readability
spring.jpa.properties.hibernate.format_sql=true

# Auto-create database tables from entity classes
spring.jpa.hibernate.ddl-auto=update
```

**JPA** stands for Java Persistence API. It is the standard way Java applications talk to databases. **Hibernate** is the most popular implementation of JPA. Think of JPA as the job description, and Hibernate as the person doing the job.

### Logging Properties

```properties
# Set the overall logging level
logging.level.root=INFO

# Set logging level for your package
logging.level.com.example.demo=DEBUG

# Log to a file
logging.file.name=app.log
```

**Logging levels** control how much detail you see in the output. From most to least detail: TRACE > DEBUG > INFO > WARN > ERROR. Setting the level to `INFO` means you see INFO, WARN, and ERROR messages, but not DEBUG or TRACE.

### Application Properties

```properties
# Custom application name
spring.application.name=bookstore-api

# Jackson JSON settings
spring.jackson.date-format=yyyy-MM-dd HH:mm:ss
spring.jackson.time-zone=UTC
```

---

## 8.3 Reading Properties with @Value

The `@Value` annotation injects a property value into a field in your bean.

```java
package com.example.demo.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class AppInfoService {

    @Value("${app.name}")
    private String appName;

    @Value("${app.version}")
    private String appVersion;

    @Value("${app.max-users:100}")
    private int maxUsers;

    public String getAppInfo() {
        return appName + " v" + appVersion +
               " (max users: " + maxUsers + ")";
    }
}
```

**Line-by-line explanation:**

- `@Value("${app.name}")` -- Tells Spring: "Find the property called `app.name` and put its value into this field." The `${}` syntax means "look up this property."
- `@Value("${app.version}")` -- Same thing for the version property.
- `@Value("${app.max-users:100}")` -- The `:100` part is a **default value**. If `app.max-users` is not defined anywhere, Spring uses `100` instead. This prevents your application from crashing when a property is missing.

**Properties file:**

```properties
# src/main/resources/application.properties
app.name=BookStore
app.version=2.1.0
# app.max-users is not set, so the default value 100 will be used
```

**Output:**

```
BookStore v2.1.0 (max users: 100)
```

### @Value with Different Types

Spring automatically converts property strings to the right Java type.

```java
@Value("${server.port}")
private int port;              // Converts "8081" to int 8081

@Value("${app.debug:false}")
private boolean debugMode;     // Converts "true"/"false" to boolean

@Value("${app.tags:}")
private String tags;           // Empty string as default

@Value("${app.rate:0.05}")
private double taxRate;        // Converts to double
```

### @Value Limitations

`@Value` is fine for simple values. But if you have many related properties, it becomes messy:

```java
// This gets messy with many properties
@Value("${mail.host}")
private String mailHost;

@Value("${mail.port}")
private int mailPort;

@Value("${mail.username}")
private String mailUsername;

@Value("${mail.password}")
private String mailPassword;

@Value("${mail.from}")
private String mailFrom;
```

That is five annotations for five related properties. There is a better way.

---

## 8.4 Grouping Properties with @ConfigurationProperties

`@ConfigurationProperties` binds a group of related properties to a Java class. It is cleaner than using multiple `@Value` annotations.

### Step 1: Define Your Properties

```properties
# src/main/resources/application.properties
mail.host=smtp.example.com
mail.port=587
mail.username=noreply@example.com
mail.password=secret123
mail.from=BookStore <noreply@example.com>
mail.enabled=true
```

### Step 2: Create a Properties Class

```java
package com.example.demo.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "mail")
public class MailProperties {

    private String host;
    private int port;
    private String username;
    private String password;
    private String from;
    private boolean enabled;

    // Getters and setters (required for binding)
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

    public String getFrom() { return from; }
    public void setFrom(String from) { this.from = from; }

    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    @Override
    public String toString() {
        return "MailProperties{" +
                "host='" + host + '\'' +
                ", port=" + port +
                ", username='" + username + '\'' +
                ", from='" + from + '\'' +
                ", enabled=" + enabled +
                '}';
    }
}
```

**Line-by-line explanation:**

- `@ConfigurationProperties(prefix = "mail")` -- Tells Spring: "Take every property that starts with `mail.` and map it to fields in this class." The property `mail.host` maps to the `host` field. The property `mail.port` maps to the `port` field.
- `@Component` -- Makes this class a Spring Bean so it can be injected into other beans.
- Getter and setter methods are **required**. Spring uses the setters to put the property values into the fields.

### Step 3: Use the Properties Class

```java
package com.example.demo.service;

import com.example.demo.config.MailProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class EmailService {

    private static final Logger log =
            LoggerFactory.getLogger(EmailService.class);

    private final MailProperties mailProperties;

    public EmailService(MailProperties mailProperties) {
        this.mailProperties = mailProperties;
    }

    public void sendEmail(String to, String subject, String body) {
        if (!mailProperties.isEnabled()) {
            log.info("Email sending is disabled. Skipping.");
            return;
        }

        log.info("Connecting to {} on port {}",
                mailProperties.getHost(),
                mailProperties.getPort());
        log.info("From: {}", mailProperties.getFrom());
        log.info("To: {}", to);
        log.info("Subject: {}", subject);
        log.info("Email sent successfully!");
    }
}
```

Much cleaner. One injection instead of five separate `@Value` fields.

### Nested Properties

You can nest properties using inner classes:

```properties
# application.properties
app.name=BookStore
app.security.enabled=true
app.security.token-expiry=3600
app.security.secret-key=mySecret123
```

```java
@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {

    private String name;
    private Security security = new Security();

    // Getters and setters for name...
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public Security getSecurity() { return security; }
    public void setSecurity(Security security) {
        this.security = security;
    }

    public static class Security {
        private boolean enabled;
        private int tokenExpiry;
        private String secretKey;

        // Getters and setters
        public boolean isEnabled() { return enabled; }
        public void setEnabled(boolean enabled) {
            this.enabled = enabled;
        }
        public int getTokenExpiry() { return tokenExpiry; }
        public void setTokenExpiry(int tokenExpiry) {
            this.tokenExpiry = tokenExpiry;
        }
        public String getSecretKey() { return secretKey; }
        public void setSecretKey(String secretKey) {
            this.secretKey = secretKey;
        }
    }
}
```

Notice that `token-expiry` in the properties file maps to `tokenExpiry` in Java. Spring Boot automatically converts **kebab-case** (words-with-dashes) to **camelCase** (wordsWithCapitals).

### @Value vs @ConfigurationProperties

| Feature                   | @Value              | @ConfigurationProperties |
|---------------------------|---------------------|--------------------------|
| Number of properties      | One at a time       | Group of related ones    |
| Type safety               | Basic               | Full                     |
| Validation support        | No                  | Yes (with @Validated)    |
| Default values            | Yes (:default)      | Yes (field initializers) |
| Nested properties         | No                  | Yes                      |
| Best for                  | 1-3 simple values   | 4+ related properties    |

---

## 8.5 Understanding Profiles

A **profile** is a named set of configuration that applies only in a specific environment.

Think of profiles like outfits. You wear different clothes for different situations. Business suit for work. Casual clothes at home. Sports gear at the gym. The person is the same. The outfit changes.

```
+-------------------+    +-------------------+    +-------------------+
|   Development     |    |     Testing       |    |    Production     |
|   (dev profile)   |    |   (test profile)  |    |  (prod profile)  |
+-------------------+    +-------------------+    +-------------------+
| H2 in-memory DB   |    | H2 file-based DB  |    | PostgreSQL DB    |
| Debug logging      |    | Warn logging      |    | Error logging    |
| Port 8080          |    | Port 9090         |    | Port 80          |
| No email sending   |    | Mock email        |    | Real email       |
+-------------------+    +-------------------+    +-------------------+

Same application. Different configurations.
```

### Why You Need Profiles

Without profiles, you would have to:

1. Change the database URL before every deployment
2. Change the logging level manually
3. Remember to turn off debug features in production
4. Risk deploying with wrong settings

Profiles automate all of this. You set the profile once, and Spring loads the right configuration.

---

## 8.6 Creating Profile-Specific Files

Spring Boot looks for configuration files with a specific naming pattern.

### File Naming Convention

```
application.properties            <-- Default (always loaded)
application-dev.properties        <-- Loaded when "dev" profile is active
application-test.properties       <-- Loaded when "test" profile is active
application-prod.properties       <-- Loaded when "prod" profile is active
```

The pattern is: `application-{profile}.properties`

### Example: Three Environments

**Default configuration (always loaded):**

```properties
# src/main/resources/application.properties
app.name=BookStore
app.version=1.0.0
spring.application.name=bookstore
```

**Development profile:**

```properties
# src/main/resources/application-dev.properties
server.port=8080

# H2 in-memory database for quick development
spring.datasource.url=jdbc:h2:mem:devdb
spring.datasource.username=sa
spring.datasource.password=
spring.h2.console.enabled=true

# Show all SQL queries
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# Detailed logging
logging.level.com.example.demo=DEBUG
logging.level.org.springframework=INFO

# Custom app settings
app.email.enabled=false
app.debug-mode=true
```

**Test profile:**

```properties
# src/main/resources/application-test.properties
server.port=9090

# H2 file-based database for persistent test data
spring.datasource.url=jdbc:h2:file:./testdb
spring.datasource.username=sa
spring.datasource.password=

# Moderate logging
logging.level.com.example.demo=INFO
logging.level.org.springframework=WARN

# Custom app settings
app.email.enabled=false
app.debug-mode=false
```

**Production profile:**

```properties
# src/main/resources/application-prod.properties
server.port=80

# Real database
spring.datasource.url=jdbc:postgresql://db-server:5432/bookstore
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}

# Minimal logging
logging.level.root=WARN
logging.level.com.example.demo=INFO

# Custom app settings
app.email.enabled=true
app.debug-mode=false
```

Notice `${DB_USERNAME}` and `${DB_PASSWORD}` in the production file. These are **environment variable placeholders**. Spring replaces them with values from the operating system environment. This way, passwords never appear in your configuration files.

**Environment variable** means a value stored in your operating system, outside your application. It is like a sticky note on your computer's desktop. Your application can read it, but it is not part of your code.

### File Structure

```
src/main/resources/
├── application.properties          <-- Common settings
├── application-dev.properties      <-- Dev overrides
├── application-test.properties     <-- Test overrides
└── application-prod.properties     <-- Prod overrides
```

---

## 8.7 Activating Profiles

You have created profile-specific files. Now how do you tell Spring which profile to use?

### Method 1: In application.properties

```properties
# src/main/resources/application.properties
spring.profiles.active=dev
```

This is the simplest way. But it means you have to change this line before deploying.

### Method 2: Command Line Argument (Recommended for Deployment)

```bash
java -jar bookstore.jar --spring.profiles.active=prod
```

This overrides whatever is in `application.properties`. It is the most common way to set profiles in production.

### Method 3: Environment Variable

```bash
export SPRING_PROFILES_ACTIVE=prod
java -jar bookstore.jar
```

Spring Boot automatically reads the `SPRING_PROFILES_ACTIVE` environment variable.

### Method 4: In Your IDE

In IntelliJ IDEA:
1. Open Run Configuration
2. Find "Active profiles" field
3. Type `dev`

In VS Code (launch.json):
```json
{
    "env": {
        "SPRING_PROFILES_ACTIVE": "dev"
    }
}
```

### Method 5: In Maven (for Tests)

```xml
<!-- pom.xml -->
<properties>
    <spring.profiles.active>test</spring.profiles.active>
</properties>
```

### Multiple Active Profiles

You can activate more than one profile:

```bash
java -jar bookstore.jar --spring.profiles.active=prod,email,metrics
```

Spring loads all three profile files:
- `application-prod.properties`
- `application-email.properties`
- `application-metrics.properties`

### Verifying the Active Profile

When your application starts, Spring prints the active profiles in the console:

```
The following 1 profile is active: "dev"
```

You can also check it programmatically:

```java
package com.example.demo.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class ProfileInfoService {

    private static final Logger log =
            LoggerFactory.getLogger(ProfileInfoService.class);

    private final Environment environment;

    public ProfileInfoService(Environment environment) {
        this.environment = environment;
    }

    @PostConstruct
    public void logActiveProfiles() {
        String[] profiles = environment.getActiveProfiles();
        if (profiles.length == 0) {
            log.info("No active profiles. Using default configuration.");
        } else {
            log.info("Active profiles: {}",
                    String.join(", ", profiles));
        }
    }
}
```

**Output with dev profile:**

```
Active profiles: dev
```

---

## 8.8 Property Resolution Order

What happens when the same property is defined in multiple places? Spring has a clear order of priority. Higher priority wins.

```
Priority (highest to lowest):
──────────────────────────────────────────────────────────
1. Command line arguments
   --server.port=9999

2. Environment variables
   SERVER_PORT=9999

3. Profile-specific properties file
   application-dev.properties

4. Default properties file
   application.properties

5. @PropertySource annotations

6. Default values in @Value
   @Value("${server.port:8080}")
──────────────────────────────────────────────────────────
```

### Example: Resolution in Action

```properties
# application.properties
server.port=8080

# application-dev.properties
server.port=8081
```

```bash
# Running with dev profile and command line override
java -jar app.jar --spring.profiles.active=dev --server.port=9999
```

What port does the application use?

```
Step 1: application.properties says 8080
Step 2: application-dev.properties overrides to 8081
Step 3: Command line overrides to 9999

Result: Port 9999 (command line wins)
```

### Environment Variable Naming

Spring Boot maps properties to environment variables using this pattern:

```
Property name:       spring.datasource.url
Environment variable: SPRING_DATASOURCE_URL

Rules:
- Replace dots (.) with underscores (_)
- Replace dashes (-) with underscores (_)
- Convert to UPPERCASE
```

More examples:

```
server.port                  --> SERVER_PORT
app.max-users                --> APP_MAX_USERS
spring.jpa.show-sql          --> SPRING_JPA_SHOW_SQL
mail.smtp.auth               --> MAIL_SMTP_AUTH
```

---

## 8.9 Profile-Specific Beans

You can create beans that only exist in certain profiles using `@Profile`.

```java
package com.example.demo.service;

public interface EmailSender {
    void send(String to, String subject, String body);
}
```

```java
package com.example.demo.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Service;

@Service
@Profile("dev")
public class MockEmailSender implements EmailSender {

    private static final Logger log =
            LoggerFactory.getLogger(MockEmailSender.class);

    @Override
    public void send(String to, String subject, String body) {
        log.info("[MOCK] Email to: {} | Subject: {} | Body: {}",
                to, subject, body);
        // Does not actually send an email
    }
}
```

```java
package com.example.demo.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Service;

@Service
@Profile("prod")
public class SmtpEmailSender implements EmailSender {

    private static final Logger log =
            LoggerFactory.getLogger(SmtpEmailSender.class);

    @Override
    public void send(String to, String subject, String body) {
        log.info("Sending real email to: {}", to);
        // Real SMTP logic here
    }
}
```

```
Profile = dev  --> MockEmailSender is created (logs but does not send)
Profile = prod --> SmtpEmailSender is created (sends real email)
```

This is powerful. In development, you never accidentally send real emails. In production, you use the real email service. The code that uses `EmailSender` does not know or care which implementation is active.

---

## 8.10 Putting It All Together

Let us create a complete example with properties, profiles, and configuration properties.

### Properties Files

```properties
# src/main/resources/application.properties
spring.application.name=bookstore
app.name=BookStore
app.version=2.0.0
app.support-email=support@bookstore.com
```

```properties
# src/main/resources/application-dev.properties
server.port=8080
spring.datasource.url=jdbc:h2:mem:devdb
spring.h2.console.enabled=true
spring.jpa.show-sql=true
logging.level.com.example.demo=DEBUG
app.environment=Development
app.email.enabled=false
```

```properties
# src/main/resources/application-prod.properties
server.port=80
spring.datasource.url=jdbc:postgresql://localhost:5432/bookstore
spring.jpa.show-sql=false
logging.level.com.example.demo=INFO
app.environment=Production
app.email.enabled=true
```

### Configuration Properties Class

```java
package com.example.demo.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {

    private String name;
    private String version;
    private String supportEmail;
    private String environment;
    private Email email = new Email();

    // Getters and setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }

    public String getSupportEmail() { return supportEmail; }
    public void setSupportEmail(String supportEmail) {
        this.supportEmail = supportEmail;
    }

    public String getEnvironment() { return environment; }
    public void setEnvironment(String environment) {
        this.environment = environment;
    }

    public Email getEmail() { return email; }
    public void setEmail(Email email) { this.email = email; }

    public static class Email {
        private boolean enabled;

        public boolean isEnabled() { return enabled; }
        public void setEnabled(boolean enabled) {
            this.enabled = enabled;
        }
    }
}
```

### Info Endpoint

```java
package com.example.demo.controller;

import com.example.demo.config.AppProperties;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class AppInfoController {

    private final AppProperties appProperties;

    public AppInfoController(AppProperties appProperties) {
        this.appProperties = appProperties;
    }

    @GetMapping("/info")
    public Map<String, Object> getInfo() {
        return Map.of(
            "name", appProperties.getName(),
            "version", appProperties.getVersion(),
            "environment", appProperties.getEnvironment(),
            "support", appProperties.getSupportEmail(),
            "emailEnabled", appProperties.getEmail().isEnabled()
        );
    }
}
```

**Output when running with dev profile:**

```json
{
    "name": "BookStore",
    "version": "2.0.0",
    "environment": "Development",
    "support": "support@bookstore.com",
    "emailEnabled": false
}
```

**Output when running with prod profile:**

```json
{
    "name": "BookStore",
    "version": "2.0.0",
    "environment": "Production",
    "support": "support@bookstore.com",
    "emailEnabled": true
}
```

Same code. Different output. That is the power of profiles.

---

## Common Mistakes

### Mistake 1: YAML Indentation Errors

```yaml
# WRONG: Inconsistent indentation
server:
  port: 8080
    servlet:    # <-- Wrong! Extra indent
      context-path: /api
```

```yaml
# CORRECT: Consistent two-space indentation
server:
  port: 8080
  servlet:
    context-path: /api
```

YAML is very strict about indentation. Always use spaces, never tabs. Use consistent indentation (two spaces is standard).

### Mistake 2: Missing Setter Methods with @ConfigurationProperties

```java
// WRONG: No setters -- Spring cannot set the values
@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String name;
    // Missing setName() method!
}
```

```java
// CORRECT: Include setters
@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String name;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}
```

### Mistake 3: Wrong Property Name Format

```properties
# WRONG: Using camelCase in properties
app.maxUsers=100
app.supportEmail=help@example.com

# CORRECT: Using kebab-case (recommended by Spring Boot)
app.max-users=100
app.support-email=help@example.com
```

Spring Boot recommends **kebab-case** for property names. It automatically maps `app.support-email` to `supportEmail` in Java.

### Mistake 4: Forgetting to Set an Active Profile

If you do not set a profile, Spring uses only `application.properties`. Your profile-specific settings will not apply.

Always set a profile:
- In `application.properties`: `spring.profiles.active=dev`
- On the command line: `--spring.profiles.active=dev`
- As an environment variable: `SPRING_PROFILES_ACTIVE=dev`

### Mistake 5: Putting Secrets in Properties Files

```properties
# WRONG: Passwords in source code
spring.datasource.password=MySecretPassword123!
api.key=sk-abc123def456
```

```properties
# CORRECT: Use environment variables
spring.datasource.password=${DB_PASSWORD}
api.key=${API_KEY}
```

Never commit passwords, API keys, or secrets to your code repository. Use environment variables instead.

---

## Best Practices

1. **Use kebab-case** for property names: `app.max-retries` instead of `app.maxRetries`.

2. **Use `@ConfigurationProperties`** when you have four or more related properties. It is cleaner and supports validation.

3. **Always set a default profile** in `application.properties` with `spring.profiles.active=dev` for local development.

4. **Keep secrets out of property files.** Use environment variables for passwords, API keys, and tokens.

5. **Use the same format everywhere.** Pick either `.properties` or `.yml` and use it consistently across all environments.

6. **Put common settings in `application.properties`** and only overrides in profile-specific files. Do not duplicate settings.

7. **Name your profiles clearly.** Use `dev`, `test`, `prod`. Avoid vague names like `profile1` or `local2`.

8. **Document custom properties.** Add comments explaining what each custom property does and what values are acceptable.

---

## Quick Summary

- Spring Boot reads configuration from `application.properties` or `application.yml`.
- `.properties` uses key=value format. `.yml` uses indentation-based hierarchy.
- `@Value("${property.name}")` injects a single property value. Use `:default` for fallback values.
- `@ConfigurationProperties(prefix = "group")` maps a group of properties to a Java class.
- **Profiles** let you have different settings for different environments (dev, test, prod).
- Profile-specific files follow the pattern `application-{profile}.properties`.
- Activate profiles via command line, environment variable, or properties file.
- Command line arguments have the highest priority. Default `@Value` values have the lowest.

---

## Key Points

- Configuration should change between environments. Code should not.
- Use `@ConfigurationProperties` over `@Value` for groups of related settings.
- Never put secrets in property files. Use environment variables.
- Always know which profile is active. Check the startup log.
- Properties follow a strict resolution order. Command line always wins.
- YAML requires careful indentation. Properties files are more forgiving.

---

## Practice Questions

1. What is the difference between `application.properties` and `application-dev.properties`? When does each file get loaded?

2. You have a property `app.retry-count=3` in `application.properties` and `app.retry-count=5` in `application-prod.properties`. You run the app with `--spring.profiles.active=prod --app.retry-count=10`. What value does `app.retry-count` have? Why?

3. Explain the difference between `@Value` and `@ConfigurationProperties`. When would you use each?

4. How does Spring Boot convert a property name like `app.max-retry-count` to a Java field name?

5. You want to use a real email service in production but a mock in development. How would you achieve this using profiles?

---

## Exercises

### Exercise 1: Multi-Profile Application

Create a Spring Boot application with:

- Three profiles: `dev`, `staging`, `prod`
- A `@ConfigurationProperties` class for settings: `app.name`, `app.environment`, `app.max-connections`, `app.cache.enabled`, `app.cache.ttl-seconds`
- An endpoint `GET /config` that returns all the current configuration values
- Different values for each profile

Test by switching profiles and hitting the endpoint.

### Exercise 2: External Configuration

Create an application that reads database connection properties using `@ConfigurationProperties`. Configure it to work with:

- H2 in-memory database for `dev` profile
- H2 file-based database for `test` profile
- Environment variable placeholders for `prod` profile

Log the active profile and database URL at startup using `@PostConstruct`.

### Exercise 3: Feature Flags

Create a feature flag system using profiles and properties:

- Define properties: `feature.dark-mode`, `feature.beta-search`, `feature.new-checkout`
- Create a `FeatureFlags` class with `@ConfigurationProperties`
- Create a `GET /features` endpoint that returns which features are enabled
- Enable different features in different profiles

---

## What Is Next?

You now know how to configure your Spring Boot application for different environments. But an application without a web interface is not very useful. In the next chapter, you will build your **first REST controller**. You will create endpoints that accept HTTP requests and return JSON responses. This is where your application starts talking to the outside world.
