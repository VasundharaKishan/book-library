# Chapter 19: Password Encoding and Roles

## What You Will Learn

- Why storing plain-text passwords is dangerous.
- What password hashing is and how BCrypt works.
- How to encode passwords during user registration.
- What roles and authorities are in Spring Security.
- How to assign roles like USER and ADMIN to users.
- How to restrict endpoints based on roles using @PreAuthorize.
- How to configure role-based access in SecurityFilterChain.
- How to build a complete registration and admin system.

## Why This Chapter Matters

Imagine a bank that writes your PIN number on a sticky note and tapes it to the front of the vault. Anyone who walks by can see it. That is exactly what happens when you store passwords as plain text in a database.

In 2012, LinkedIn suffered a data breach that exposed over 6 million passwords. The passwords were hashed, but with a weak algorithm and no salt. Attackers cracked most of them within days.

Password encoding and role management are not optional features. They are the foundation of any secure application. In this chapter, you will learn how to store passwords safely using BCrypt and how to control what different users can do using roles.

---

## 19.1 The Problem with Plain-Text Passwords

Let us start with a simple question. What happens if you store passwords like this in your database?

| id | username | password   |
|----|----------|------------|
| 1  | alice    | secret123  |
| 2  | bob      | mypassword |
| 3  | carol    | qwerty     |

If an attacker gains access to your database (through a SQL injection, a misconfigured server, or a stolen backup), they can read every single password. They can log in as any user. They can even try these passwords on other websites since many people reuse passwords.

> **Plain text**: Storing data exactly as it was entered, without any transformation or protection.

This is why you must never store passwords in plain text. Ever.

---

## 19.2 What Is Password Hashing?

**Hashing** is a one-way transformation. You take a password, run it through a hashing function, and get a scrambled string. The key word is "one-way." You cannot reverse the process to get the original password back.

```
Password: "secret123"
    |
    v
[Hashing Function]
    |
    v
Hash: "$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy"
```

Think of hashing like putting meat through a meat grinder. You can turn a steak into ground beef, but you cannot turn ground beef back into a steak.

### How Login Works with Hashing

When a user logs in, you do not decrypt the stored hash. Instead, you hash the password they just typed and compare the two hashes:

```
+---------------------------------------------+
|            LOGIN PROCESS                     |
+---------------------------------------------+
|                                              |
|  User types: "secret123"                     |
|       |                                      |
|       v                                      |
|  [Hash "secret123"]                          |
|       |                                      |
|       v                                      |
|  Computed: "$2a$10$N9qo8u..."                |
|       |                                      |
|       v                                      |
|  [Compare with stored hash]                  |
|       |                                      |
|       +---> Match? --> Login successful       |
|       +---> No match? --> Login failed        |
|                                              |
+---------------------------------------------+
```

### What Is a Salt?

A **salt** is a random string added to the password before hashing. This means that even if two users have the same password, their hashes will be different.

```
User Alice: "secret123" + "random_salt_1" --> Hash A
User Bob:   "secret123" + "random_salt_2" --> Hash B

Hash A != Hash B (even though the passwords are the same)
```

Without a salt, an attacker could pre-compute hashes for common passwords (called a "rainbow table") and look up matches. Salting defeats this attack.

---

## 19.3 BCrypt: The Industry Standard

**BCrypt** is a password hashing algorithm designed specifically for passwords. It has three important features:

1. **It is slow on purpose.** This makes brute-force attacks impractical. A regular hash function can compute billions of hashes per second. BCrypt is designed to be slow.
2. **It includes a salt automatically.** You do not need to generate and store salts separately.
3. **It has a configurable work factor.** You can make it slower as computers get faster.

Here is what a BCrypt hash looks like:

```
$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
 |  |  |                                                      |
 |  |  +--- Salt (22 characters) ---+                         |
 |  +------ Work factor (10 = 2^10 = 1024 iterations)         |
 +--------- Algorithm version (2a = BCrypt)                    |
            +--- Hash value (31 characters) -------------------+
```

Spring Security provides `BCryptPasswordEncoder` which handles all of this for you.

---

## 19.4 Setting Up the Project

Let us build a complete user registration system with password encoding and roles. Here is the Maven dependency section:

```xml
<!-- pom.xml -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

And the application properties:

```properties
# src/main/resources/application.properties

spring.datasource.url=jdbc:h2:mem:securitydb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.jpa.hibernate.ddl-auto=create-drop
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
```

---

## 19.5 Creating the User Entity

Our User entity will store the username, encoded password, and role:

```java
// src/main/java/com/example/security/entity/User.java
package com.example.security.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Column;

@Entity
@Table(name = "app_user")  // "user" is a reserved word in H2
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private String role;  // e.g., "ROLE_USER" or "ROLE_ADMIN"

    public User() {
    }

    public User(String username, String password, String role) {
        this.username = username;
        this.password = password;
        this.role = role;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
}
```

**Line-by-line explanation:**

- `@Table(name = "app_user")` -- We use "app_user" because "user" is a reserved keyword in H2 and many other databases.
- `@Column(nullable = false, unique = true)` on username -- Each username must be unique and cannot be null.
- `private String role` -- We store the role as a string. Spring Security expects roles to start with "ROLE_" (like "ROLE_USER" or "ROLE_ADMIN").

---

## 19.6 The User Repository

```java
// src/main/java/com/example/security/repository/UserRepository.java
package com.example.security.repository;

import com.example.security.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByUsername(String username);

    boolean existsByUsername(String username);
}
```

**Line-by-line explanation:**

- `findByUsername` -- Spring Data JPA generates the SQL query automatically. Returns an Optional because the user might not exist.
- `existsByUsername` -- Returns true if a user with that username already exists. Useful for checking duplicates during registration.

---

## 19.7 Configuring BCryptPasswordEncoder

You need to tell Spring Security to use BCrypt. You do this by creating a bean:

```java
// src/main/java/com/example/security/config/SecurityConfig.java
package com.example.security.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

**Line-by-line explanation:**

- `@Bean` -- This method creates a PasswordEncoder object and registers it with Spring's container.
- `new BCryptPasswordEncoder()` -- Creates a BCrypt encoder with the default strength of 10 (meaning 2^10 = 1024 hashing iterations).
- The return type is `PasswordEncoder` (the interface), not `BCryptPasswordEncoder` (the implementation). This follows the programming-to-interfaces principle.

### What Happens When You Encode a Password

```java
PasswordEncoder encoder = new BCryptPasswordEncoder();

String rawPassword = "secret123";
String encodedPassword = encoder.encode(rawPassword);

System.out.println(encodedPassword);
// Output: $2a$10$dXJ3SW6G7P50lGmMQoeM0uO8Kd3FdGqBm/LqoC7Lxxx0n6PfGmRi2

// Verify a password
boolean matches = encoder.matches("secret123", encodedPassword);
System.out.println(matches);  // true

boolean wrong = encoder.matches("wrongpassword", encodedPassword);
System.out.println(wrong);  // false
```

Notice that you never decrypt the hash. You use `matches()` to check if a raw password matches the stored hash.

---

## 19.8 The Registration DTO

We use a Data Transfer Object to receive registration data. This keeps our entity separate from the API input:

```java
// src/main/java/com/example/security/dto/RegistrationRequest.java
package com.example.security.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class RegistrationRequest {

    @NotBlank(message = "Username is required")
    @Size(min = 3, max = 50, message = "Username must be 3-50 characters")
    private String username;

    @NotBlank(message = "Password is required")
    @Size(min = 8, message = "Password must be at least 8 characters")
    private String password;

    public RegistrationRequest() {
    }

    public RegistrationRequest(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
```

---

## 19.9 The User Service with Password Encoding

This is where the magic happens. The service encodes the password before saving:

```java
// src/main/java/com/example/security/service/UserService.java
package com.example.security.service;

import com.example.security.dto.RegistrationRequest;
import com.example.security.entity.User;
import com.example.security.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository,
                       PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public User registerUser(RegistrationRequest request) {
        // Check if username already exists
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("Username already taken: "
                + request.getUsername());
        }

        // Create user with encoded password and default USER role
        User user = new User(
            request.getUsername(),
            passwordEncoder.encode(request.getPassword()),  // ENCODE here!
            "ROLE_USER"
        );

        return userRepository.save(user);
    }

    public User registerAdmin(RegistrationRequest request) {
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("Username already taken: "
                + request.getUsername());
        }

        User user = new User(
            request.getUsername(),
            passwordEncoder.encode(request.getPassword()),
            "ROLE_ADMIN"
        );

        return userRepository.save(user);
    }
}
```

**Line-by-line explanation:**

- `passwordEncoder.encode(request.getPassword())` -- This is the critical line. The raw password "secret123" gets transformed into a BCrypt hash like "$2a$10$dXJ3SW6G7P..." before being saved to the database.
- `"ROLE_USER"` -- The default role for regular users. The "ROLE_" prefix is a Spring Security convention.
- `registerAdmin` -- A separate method for creating admin users. In a real application, only existing admins should be able to call this.

Here is what the flow looks like:

```
+---------------------------------------------------+
|           REGISTRATION FLOW                        |
+---------------------------------------------------+
|                                                    |
|  User sends: { "username": "alice",                |
|                "password": "secret123" }           |
|       |                                            |
|       v                                            |
|  [Check: username "alice" exists?]                 |
|       |                                            |
|       +--> Yes --> Throw "Username taken"           |
|       |                                            |
|       +--> No --> Continue                          |
|       |                                            |
|       v                                            |
|  [Encode "secret123" with BCrypt]                  |
|       |                                            |
|       v                                            |
|  Result: "$2a$10$N9qo8uLO..."                     |
|       |                                            |
|       v                                            |
|  [Save to database]                                |
|  id=1, username="alice",                           |
|  password="$2a$10$N9qo8uLO...",                    |
|  role="ROLE_USER"                                  |
|                                                    |
+---------------------------------------------------+
```

---

## 19.10 The Custom UserDetailsService

Spring Security needs a way to load users during login. You provide this by implementing `UserDetailsService`:

```java
// src/main/java/com/example/security/service/CustomUserDetailsService.java
package com.example.security.service;

import com.example.security.entity.User;
import com.example.security.repository.UserRepository;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.Collections;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    public CustomUserDetailsService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public UserDetails loadUserByUsername(String username)
            throws UsernameNotFoundException {

        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException(
                "User not found: " + username));

        return new org.springframework.security.core.userdetails.User(
            user.getUsername(),
            user.getPassword(),
            Collections.singletonList(
                new SimpleGrantedAuthority(user.getRole())
            )
        );
    }
}
```

**Line-by-line explanation:**

- `implements UserDetailsService` -- This interface has one method: `loadUserByUsername`. Spring Security calls it automatically when someone tries to log in.
- `orElseThrow(...)` -- If the user is not found in the database, throw an exception. Spring Security catches this and returns a "bad credentials" response.
- `new org.springframework.security.core.userdetails.User(...)` -- We create a Spring Security `User` object (different from our entity). It holds the username, encoded password, and authorities.
- `new SimpleGrantedAuthority(user.getRole())` -- Converts our role string (like "ROLE_ADMIN") into a Spring Security authority object.

---

## 19.11 Understanding Roles and Authorities

In Spring Security, **roles** and **authorities** are closely related but slightly different:

| Concept | Description | Example |
|---------|-------------|---------|
| **Authority** | A permission string | "ROLE_USER", "READ_PRIVILEGE" |
| **Role** | An authority with the "ROLE_" prefix | "ROLE_ADMIN" |

When you use `hasRole("ADMIN")` in Spring Security, it automatically checks for the authority "ROLE_ADMIN". This is why we store roles with the "ROLE_" prefix.

```
+----------------------------------------+
|       ROLES vs AUTHORITIES              |
+----------------------------------------+
|                                        |
|  hasRole("ADMIN")                      |
|       |                                |
|       v                                |
|  Checks for authority "ROLE_ADMIN"     |
|                                        |
|  hasAuthority("ROLE_ADMIN")            |
|       |                                |
|       v                                |
|  Checks for authority "ROLE_ADMIN"     |
|                                        |
|  Both do the same thing!               |
+----------------------------------------+
```

Think of it this way. A role is like a job title (Manager, Employee). An authority is a specific permission (CAN_APPROVE_EXPENSES, CAN_VIEW_REPORTS). In simple applications, roles are enough. In complex applications, you might use fine-grained authorities.

---

## 19.12 Role-Based SecurityFilterChain

Now let us configure which endpoints each role can access:

```java
// src/main/java/com/example/security/config/SecurityConfig.java
package com.example.security.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity  // Enables @PreAuthorize
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                // Public endpoints - anyone can access
                .requestMatchers("/api/auth/register").permitAll()
                .requestMatchers("/h2-console/**").permitAll()

                // Admin-only endpoints
                .requestMatchers("/api/admin/**").hasRole("ADMIN")

                // User and Admin can access
                .requestMatchers("/api/user/**").hasAnyRole("USER", "ADMIN")

                // Everything else requires authentication
                .anyRequest().authenticated()
            )
            .httpBasic(httpBasic -> {});  // Use HTTP Basic for simplicity

        // Allow H2 console frames
        http.headers(headers ->
            headers.frameOptions(frame -> frame.disable()));

        return http.build();
    }
}
```

**Line-by-line explanation:**

- `@EnableMethodSecurity` -- Enables method-level security annotations like `@PreAuthorize`. Without this, those annotations are ignored.
- `.csrf(csrf -> csrf.disable())` -- Disables CSRF protection. Necessary for stateless REST APIs. We covered this in Chapter 17.
- `.requestMatchers("/api/auth/register").permitAll()` -- The registration endpoint is public. Anyone can create an account.
- `.requestMatchers("/api/admin/**").hasRole("ADMIN")` -- Only users with ROLE_ADMIN can access URLs starting with "/api/admin/". The `**` matches any path under "/api/admin/".
- `.requestMatchers("/api/user/**").hasAnyRole("USER", "ADMIN")` -- Both regular users and admins can access these endpoints.
- `.anyRequest().authenticated()` -- Any URL not listed above requires the user to be logged in, regardless of role.
- `.httpBasic(httpBasic -> {})` -- Enables HTTP Basic authentication. The browser sends username:password encoded in Base64 with each request.

Here is a visual summary of the access rules:

```
+---------------------------------------------+
|         ENDPOINT ACCESS MATRIX               |
+---------------------------------------------+
|                                              |
|  Endpoint              Anonymous  USER  ADMIN|
|  ------------------------------------------------
|  POST /api/auth/register    OK     OK    OK  |
|  GET  /h2-console           OK     OK    OK  |
|  GET  /api/user/profile     --     OK    OK  |
|  GET  /api/admin/users      --     --    OK  |
|  DELETE /api/admin/users/1  --     --    OK  |
|  GET  /api/anything-else    --     OK    OK  |
|                                              |
|  OK = Allowed, -- = Denied (403 Forbidden)   |
+---------------------------------------------+
```

---

## 19.13 Using @PreAuthorize for Method-Level Security

Sometimes you want to control access at the method level instead of the URL level. The `@PreAuthorize` annotation does this:

```java
// src/main/java/com/example/security/controller/AdminController.java
package com.example.security.controller;

import com.example.security.entity.User;
import com.example.security.repository.UserRepository;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

    private final UserRepository userRepository;

    public AdminController(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @GetMapping("/users")
    @PreAuthorize("hasRole('ADMIN')")
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    @DeleteMapping("/users/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public String deleteUser(@PathVariable Long id) {
        userRepository.deleteById(id);
        return "User deleted successfully";
    }

    @GetMapping("/dashboard")
    @PreAuthorize("hasRole('ADMIN') or hasRole('MANAGER')")
    public String adminDashboard() {
        return "Welcome to the Admin Dashboard";
    }
}
```

**Line-by-line explanation:**

- `@PreAuthorize("hasRole('ADMIN')")` -- Before this method runs, Spring checks if the logged-in user has the ADMIN role. If not, it returns 403 Forbidden.
- `hasRole('ADMIN') or hasRole('MANAGER')` -- You can combine conditions. This method is accessible by admins OR managers.
- The `@PreAuthorize` annotation uses Spring Expression Language (SpEL). Common expressions include:
  - `hasRole('ADMIN')` -- Has a specific role.
  - `hasAnyRole('ADMIN', 'MANAGER')` -- Has any of the listed roles.
  - `hasAuthority('ROLE_ADMIN')` -- Has a specific authority (same as hasRole but you include the ROLE_ prefix).
  - `isAuthenticated()` -- Is logged in.
  - `permitAll()` -- Everyone can access.

---

## 19.14 The Registration Controller

```java
// src/main/java/com/example/security/controller/AuthController.java
package com.example.security.controller;

import com.example.security.dto.RegistrationRequest;
import com.example.security.entity.User;
import com.example.security.service.UserService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final UserService userService;

    public AuthController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/register")
    public ResponseEntity<Map<String, String>> register(
            @Valid @RequestBody RegistrationRequest request) {

        User user = userService.registerUser(request);

        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(Map.of(
                "message", "User registered successfully",
                "username", user.getUsername(),
                "role", user.getRole()
            ));
    }
}
```

---

## 19.15 The User Controller

```java
// src/main/java/com/example/security/controller/UserController.java
package com.example.security.controller;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/user")
public class UserController {

    @GetMapping("/profile")
    public Map<String, Object> getProfile(Authentication authentication) {
        return Map.of(
            "username", authentication.getName(),
            "authorities", authentication.getAuthorities().toString()
        );
    }

    @GetMapping("/dashboard")
    public String userDashboard() {
        return "Welcome to your dashboard!";
    }
}
```

**Line-by-line explanation:**

- `Authentication authentication` -- Spring Security injects the current user's authentication object automatically. You can get the username and authorities from it.
- `authentication.getName()` -- Returns the username of the logged-in user.
- `authentication.getAuthorities()` -- Returns the list of roles/authorities the user has.

---

## 19.16 Testing the Complete System

Start the application and test with curl commands.

### Step 1: Register a Regular User

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'
```

**Output:**

```json
{
    "message": "User registered successfully",
    "username": "alice",
    "role": "ROLE_USER"
}
```

### Step 2: Access User Profile (with credentials)

```bash
curl -u alice:password123 http://localhost:8080/api/user/profile
```

**Output:**

```json
{
    "username": "alice",
    "authorities": "[ROLE_USER]"
}
```

### Step 3: Try to Access Admin Endpoint as Regular User

```bash
curl -u alice:password123 http://localhost:8080/api/admin/users
```

**Output:**

```json
{
    "status": 403,
    "error": "Forbidden"
}
```

Alice has the USER role, so she cannot access admin endpoints. This is exactly what we want.

### Step 4: Check the Database

Open `http://localhost:8080/h2-console` and connect. Run:

```sql
SELECT * FROM APP_USER;
```

**Output:**

```
ID | USERNAME | PASSWORD                                              | ROLE
1  | alice    | $2a$10$dXJ3SW6G7P50lGmMQoeM0uO8Kd3FdGqBm/LqoC7... | ROLE_USER
```

Notice that the password is stored as a BCrypt hash, not as "password123". Even if someone reads the database, they cannot determine the original password.

---

## 19.17 Creating an Admin Setup with CommandLineRunner

In many applications, you need a default admin user when the application starts. You can use `CommandLineRunner`:

```java
// src/main/java/com/example/security/config/DataInitializer.java
package com.example.security.config;

import com.example.security.entity.User;
import com.example.security.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(UserRepository userRepository,
                           PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) {
        // Create default admin if not exists
        if (!userRepository.existsByUsername("admin")) {
            User admin = new User(
                "admin",
                passwordEncoder.encode("admin123"),
                "ROLE_ADMIN"
            );
            userRepository.save(admin);
            System.out.println("Default admin user created");
        }
    }
}
```

**Line-by-line explanation:**

- `implements CommandLineRunner` -- Spring Boot calls the `run` method after the application starts.
- `if (!userRepository.existsByUsername("admin"))` -- Only creates the admin if one does not already exist. This prevents duplicates on restart.
- `passwordEncoder.encode("admin123")` -- Even the default admin password gets encoded. Never store it in plain text.

Now you can test admin access:

```bash
curl -u admin:admin123 http://localhost:8080/api/admin/users
```

**Output:**

```json
[
    {
        "id": 1,
        "username": "admin",
        "password": "$2a$10$...",
        "role": "ROLE_ADMIN"
    }
]
```

> **Warning**: The password hash is visible in the response. In a real application, you should create a response DTO that excludes the password field. Never send password hashes to the client.

---

## 19.18 The Complete Request Flow

Here is what happens when a user makes a request to a protected endpoint:

```
+---------------------------------------------------------------+
|                    REQUEST FLOW                                |
+---------------------------------------------------------------+
|                                                                |
|  1. Client sends request with credentials                      |
|     GET /api/admin/users                                       |
|     Authorization: Basic YWRtaW46YWRtaW4xMjM=                 |
|         |                                                      |
|         v                                                      |
|  2. SecurityFilterChain intercepts the request                 |
|         |                                                      |
|         v                                                      |
|  3. Extract credentials from Authorization header              |
|     username: "admin", password: "admin123"                    |
|         |                                                      |
|         v                                                      |
|  4. Call CustomUserDetailsService.loadUserByUsername("admin")   |
|     --> Load user from database                                |
|         |                                                      |
|         v                                                      |
|  5. BCryptPasswordEncoder.matches("admin123", storedHash)      |
|     --> Compare raw password with stored BCrypt hash            |
|         |                                                      |
|         v                                                      |
|  6. Check: Does user have required role?                       |
|     /api/admin/** requires ROLE_ADMIN                          |
|     User has ROLE_ADMIN --> GRANTED                             |
|         |                                                      |
|         v                                                      |
|  7. Execute controller method                                  |
|     --> Return list of users                                   |
|                                                                |
+---------------------------------------------------------------+
```

---

## Common Mistakes

1. **Storing passwords in plain text.** Always use `passwordEncoder.encode()` before saving passwords. Never store raw passwords in the database.

2. **Forgetting the "ROLE_" prefix.** When storing roles, use "ROLE_USER" not "USER". When checking with `hasRole("USER")`, Spring automatically adds the "ROLE_" prefix. If you use `hasAuthority()`, you must include the prefix yourself.

3. **Encoding the password twice.** Do not call `encode()` when the user logs in. Only encode during registration. Spring Security calls `matches()` automatically during authentication.

4. **Not adding @EnableMethodSecurity.** If you use `@PreAuthorize` but forget `@EnableMethodSecurity` on your config class, the annotations are silently ignored. Your endpoints will be unprotected.

5. **Returning password hashes in API responses.** Always create a response DTO that excludes the password field. Leaking hashes, while not as bad as plain text, still gives attackers material to work with.

6. **Using a weak work factor.** The default BCrypt strength of 10 is fine for most applications. Going below 10 is too weak. Going above 14 makes login painfully slow.

---

## Best Practices

1. **Always use BCrypt or Argon2 for password hashing.** Never use MD5 or SHA-256 for passwords. They are too fast and designed for data integrity, not password storage.

2. **Set minimum password length to at least 8 characters.** Use validation annotations to enforce this.

3. **Use the PasswordEncoder interface, not the concrete class.** This makes it easy to switch algorithms later.

4. **Create an admin account programmatically, not through SQL scripts.** Use CommandLineRunner to ensure the admin password is properly encoded.

5. **Apply the principle of least privilege.** Give users the minimum role they need. Most users should be USER, not ADMIN.

6. **Use @PreAuthorize for fine-grained control.** It is easier to read and maintain than complex URL patterns in SecurityFilterChain.

---

## Quick Summary

Password encoding protects user credentials by transforming them into irreversible hashes before storing them in the database. BCryptPasswordEncoder is the industry standard for Spring Boot applications. It automatically handles salting and uses a configurable work factor to resist brute-force attacks. Roles like USER and ADMIN control what different users can do. You define access rules in SecurityFilterChain using methods like hasRole() and hasAnyRole(). For method-level control, @PreAuthorize lets you specify role requirements directly on controller methods. Always encode passwords during registration, never store plain text, and never return password hashes in API responses.

---

## Key Points

- Never store passwords in plain text. Always hash them with BCrypt.
- BCryptPasswordEncoder handles salting automatically.
- Use `encode()` during registration and `matches()` during login.
- Roles must have the "ROLE_" prefix when stored (e.g., "ROLE_USER").
- `hasRole("USER")` automatically checks for "ROLE_USER".
- @EnableMethodSecurity is required for @PreAuthorize to work.
- SecurityFilterChain defines URL-level access rules.
- @PreAuthorize defines method-level access rules.
- Use CommandLineRunner to create default admin users on startup.

---

## Practice Questions

1. Why is BCrypt preferred over SHA-256 for password hashing?

2. What is the purpose of a salt in password hashing, and does BCrypt handle it automatically?

3. What happens if you store a role as "USER" instead of "ROLE_USER" and then use `hasRole("USER")` in your security configuration?

4. What is the difference between `hasRole("ADMIN")` and `hasAuthority("ROLE_ADMIN")`?

5. Why should you never call `passwordEncoder.encode()` during the login process?

---

## Exercises

### Exercise 1: Add a MANAGER Role

Extend the application to support a third role called MANAGER. Create a new endpoint at `/api/manager/reports` that only MANAGER and ADMIN users can access. Regular USERs should get a 403 Forbidden response.

### Exercise 2: Create a User Response DTO

The current admin endpoint returns user objects with password hashes. Create a `UserResponse` DTO that includes only the id, username, and role. Modify the admin controller to return this DTO instead of the entity.

### Exercise 3: Password Strength Validation

Add custom validation to the registration endpoint that requires passwords to contain at least one uppercase letter, one lowercase letter, one digit, and one special character. Return helpful error messages when validation fails.

---

## What Is Next?

Your application is now secure with password encoding and role-based access control. But what happens when a frontend application running on a different domain tries to call your API? The browser will block it because of CORS (Cross-Origin Resource Sharing). In Chapter 20, you will learn what CORS is, why browsers enforce it, and how to configure it in Spring Boot so your API can serve requests from any trusted frontend.
