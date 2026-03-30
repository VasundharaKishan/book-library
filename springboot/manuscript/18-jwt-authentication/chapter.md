# Chapter 18: JWT Authentication

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand what a JWT is and how it works
- Know the three parts of a JWT: header, payload, and signature
- Add the jjwt dependency for JWT operations
- Create a `JwtUtil` class to generate and validate tokens
- Build a `JwtAuthenticationFilter` that intercepts every request
- Create login and registration endpoints
- Build a complete authentication flow from registration to protected API access

## Why This Chapter Matters

In the previous chapter, you learned about HTTP Basic authentication. It works, but it has a major problem: the client must send the username and password with **every single request**. That is like showing your passport at every door in the airport, not just at the security checkpoint.

JWT (JSON Web Token) solves this elegantly. You show your credentials once at login, and in return you get a **token** -- a signed digital pass. For every subsequent request, you just show this token. No need to send your password again.

### The Concert Wristband Analogy

Imagine you buy a ticket to a music concert:

1. **At the gate** (login), you show your ticket and ID. The staff verifies them.
2. **They give you a wristband** (JWT token). The wristband has your name, your ticket type (VIP or General), and a holographic stamp that proves it is real.
3. **Inside the venue**, you just flash your wristband to enter different areas. No one asks for your ticket or ID again.
4. **The wristband expires** at the end of the concert. After that, it is useless.

A JWT works exactly like this wristband:

```
+---------------------------------------------------+
|                    JWT TOKEN                      |
|  (Your digital concert wristband)                 |
+---------------------------------------------------+
|                                                   |
|  WHO you are:      alice                          |
|  WHAT you can do:  ROLE_USER                      |
|  WHEN it expires:  2 hours from now               |
|  PROOF it's real:  Cryptographic signature        |
|                                                   |
+---------------------------------------------------+
```

---

## What Is a JWT?

A JWT (pronounced "jot") is a compact, self-contained token used for securely transmitting information between parties. It is a string of text that looks like this:

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbGljZSIsInJvbGUiOiJVU0VSIiwiaWF0IjoxNzA5MjM0NTY3LCJleHAiOjE3MDkyNDE3Njd9.K8vJx2QfbPn3hS4dF2zj7wR9nL1mX6pY5tG3kH8cN0o
```

It looks like gibberish, but it has three distinct parts separated by dots.

### The Three Parts of a JWT

```
HEADER.PAYLOAD.SIGNATURE
  |       |        |
  |       |        +-- Verifies the token has not been tampered with
  |       +----------- Contains the actual data (claims)
  +------------------- Describes the token type and algorithm
```

Let us break each part down:

**1. Header** (Algorithm and token type)

```json
{
    "alg": "HS256",
    "typ": "JWT"
}
```

This says: "This is a JWT, and it was signed using the HMAC-SHA256 algorithm."

**2. Payload** (Claims -- the actual data)

```json
{
    "sub": "alice",
    "role": "USER",
    "iat": 1709234567,
    "exp": 1709241767
}
```

This contains:
- `sub` (subject): who the token belongs to
- `role`: what the user can do
- `iat` (issued at): when the token was created
- `exp` (expiration): when the token expires

**3. Signature** (Proof of authenticity)

```
HMACSHA256(
    base64UrlEncode(header) + "." + base64UrlEncode(payload),
    your-secret-key
)
```

The signature is created by combining the header and payload with a secret key. If anyone changes the payload (for example, changing `role` from `USER` to `ADMIN`), the signature will not match and the token will be rejected.

```
+----------------------------------------------------------+
|  WHY THE SIGNATURE MATTERS                               |
+----------------------------------------------------------+
|                                                          |
|  Original token:                                         |
|  Header.Payload("role":"USER").Signature_A               |
|                                                          |
|  Hacker modifies payload:                                |
|  Header.Payload("role":"ADMIN").Signature_A              |
|                                                          |
|  Server recalculates signature:                          |
|  Expected: Signature_B (based on modified payload)       |
|  Actual:   Signature_A (from original token)             |
|                                                          |
|  Signature_A != Signature_B                              |
|  TOKEN REJECTED! Tampering detected.                     |
|                                                          |
+----------------------------------------------------------+
```

---

## JWT Authentication Flow

```
+------------------------------------------------------------------+
|  COMPLETE JWT AUTHENTICATION FLOW                                |
+------------------------------------------------------------------+
|                                                                  |
|  STEP 1: REGISTER                                                |
|  POST /api/auth/register                                         |
|  {"username":"alice","password":"pass123","email":"a@b.com"}      |
|  Server: Save user to database with BCrypt-hashed password       |
|  Response: 201 Created                                           |
|                                                                  |
|  STEP 2: LOGIN                                                   |
|  POST /api/auth/login                                            |
|  {"username":"alice","password":"pass123"}                        |
|  Server: Verify credentials, generate JWT token                  |
|  Response: {"token":"eyJhbG..."}                                 |
|                                                                  |
|  STEP 3: ACCESS PROTECTED RESOURCES                              |
|  GET /api/products                                               |
|  Authorization: Bearer eyJhbG...                                 |
|  Server: Validate token, extract user, check permissions         |
|  Response: 200 OK + data                                         |
|                                                                  |
|  STEP 4: TOKEN EXPIRES                                           |
|  GET /api/products                                               |
|  Authorization: Bearer eyJhbG... (expired token)                 |
|  Server: Token expired!                                          |
|  Response: 401 Unauthorized                                      |
|  Client must login again to get a new token                      |
|                                                                  |
+------------------------------------------------------------------+
```

---

## Setting Up the Project

### Step 1: Add Dependencies

```xml
<dependencies>
    <!-- Spring Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- Spring Security -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>

    <!-- Spring Data JPA -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <!-- H2 Database -->
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- JJWT - Java JWT library -->
    <dependency>                                              <!-- Line 1 -->
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-api</artifactId>                     <!-- Line 2 -->
        <version>0.12.6</version>
    </dependency>
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-impl</artifactId>                    <!-- Line 3 -->
        <version>0.12.6</version>
        <scope>runtime</scope>
    </dependency>
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-jackson</artifactId>                 <!-- Line 4 -->
        <version>0.12.6</version>
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

**Line-by-line explanation:**

| Line | Artifact | What It Does |
|------|----------|-------------|
| 1-2 | `jjwt-api` | The JJWT API interfaces. Your code compiles against this |
| 3 | `jjwt-impl` | The JJWT implementation. Needed at runtime to create and parse tokens |
| 4 | `jjwt-jackson` | JSON serialization support for JJWT. Uses Jackson (which Spring Boot already includes) |

### Step 2: Configure application.properties

```properties
spring.application.name=jwt-demo
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# JWT Configuration
jwt.secret=mySecretKeyThatIsAtLeast256BitsLongForHS256Algorithm123456  # Line 1
jwt.expiration=7200000                                                 # Line 2
```

| Line | Property | What It Does |
|------|----------|-------------|
| 1 | `jwt.secret` | The secret key used to sign tokens. Must be at least 256 bits (32 characters) for HS256. **In production, use environment variables!** |
| 2 | `jwt.expiration` | Token validity duration in milliseconds. 7200000 = 2 hours |

---

## Building the JWT System

### Project Structure

```
src/main/java/com/example/demo/
├── DemoApplication.java
├── config/
│   └── SecurityConfig.java
├── controller/
│   ├── AuthController.java
│   └── ProductController.java
├── dto/
│   ├── LoginRequest.java
│   ├── LoginResponse.java
│   └── RegisterRequest.java
├── entity/
│   ├── Product.java
│   └── AppUser.java
├── filter/
│   └── JwtAuthenticationFilter.java
├── repository/
│   ├── ProductRepository.java
│   └── AppUserRepository.java
├── security/
│   └── JwtUtil.java
└── service/
    ├── AuthService.java
    └── ProductService.java
```

### Step 3: Create the User Entity

```java
package com.example.demo.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "app_users")                                   // Line 1
public class AppUser {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;

    @Column(nullable = false)
    private String password;                                  // Line 2

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(nullable = false, length = 20)
    private String role = "USER";                             // Line 3

    public AppUser() {}

    public AppUser(String username, String password,
                   String email) {
        this.username = username;
        this.password = password;
        this.email = email;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
}
```

**Key points:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `@Table(name = "app_users")` | Named `app_users` to avoid conflict with H2's reserved word `USER` |
| 2 | `private String password` | This will store the BCrypt-hashed password, never plain text |
| 3 | `private String role = "USER"` | Default role for new users |

### Step 4: Create the User Repository

```java
package com.example.demo.repository;

import com.example.demo.entity.AppUser;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AppUserRepository extends JpaRepository<AppUser, Long> {

    Optional<AppUser> findByUsername(String username);

    boolean existsByUsername(String username);

    boolean existsByEmail(String email);
}
```

### Step 5: Create DTOs (Data Transfer Objects)

DTOs are simple classes used to transfer data between the client and server. They keep your entity classes separate from your API contract.

```java
package com.example.demo.dto;

public class RegisterRequest {

    private String username;
    private String password;
    private String email;

    // Default constructor
    public RegisterRequest() {}

    public RegisterRequest(String username, String password,
                          String email) {
        this.username = username;
        this.password = password;
        this.email = email;
    }

    // Getters and setters
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
}
```

```java
package com.example.demo.dto;

public class LoginRequest {

    private String username;
    private String password;

    public LoginRequest() {}

    public LoginRequest(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
```

```java
package com.example.demo.dto;

public class LoginResponse {

    private String token;
    private String username;
    private String role;
    private long expiresIn;

    public LoginResponse() {}

    public LoginResponse(String token, String username,
                         String role, long expiresIn) {
        this.token = token;
        this.username = username;
        this.role = role;
        this.expiresIn = expiresIn;
    }

    // Getters and setters
    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
    public long getExpiresIn() { return expiresIn; }
    public void setExpiresIn(long expiresIn) { this.expiresIn = expiresIn; }
}
```

---

## Step 6: Create the JwtUtil Class

This is the heart of the JWT system. It creates tokens, validates them, and extracts information from them.

```java
package com.example.demo.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Component
public class JwtUtil {

    private final SecretKey key;                              // Line 1
    private final long expirationMs;                          // Line 2

    public JwtUtil(
            @Value("${jwt.secret}") String secret,            // Line 3
            @Value("${jwt.expiration}") long expirationMs     // Line 4
    ) {
        this.key = Keys.hmacShaKeyFor(
            secret.getBytes(StandardCharsets.UTF_8));          // Line 5
        this.expirationMs = expirationMs;
    }

    /**
     * Generate a JWT token for a user.
     */
    public String generateToken(String username, String role) { // Line 6
        Date now = new Date();                                // Line 7
        Date expiration = new Date(
            now.getTime() + expirationMs);                    // Line 8

        return Jwts.builder()                                 // Line 9
            .subject(username)                                // Line 10
            .claim("role", role)                              // Line 11
            .issuedAt(now)                                    // Line 12
            .expiration(expiration)                           // Line 13
            .signWith(key)                                    // Line 14
            .compact();                                       // Line 15
    }

    /**
     * Extract the username from a JWT token.
     */
    public String extractUsername(String token) {             // Line 16
        return extractAllClaims(token).getSubject();
    }

    /**
     * Extract the role from a JWT token.
     */
    public String extractRole(String token) {                 // Line 17
        return extractAllClaims(token)
            .get("role", String.class);
    }

    /**
     * Check if a token is valid (not expired, not tampered).
     */
    public boolean isTokenValid(String token) {               // Line 18
        try {
            extractAllClaims(token);                          // Line 19
            return true;
        } catch (JwtException | IllegalArgumentException e) { // Line 20
            return false;
        }
    }

    /**
     * Parse the token and extract all claims.
     * This also validates the signature and expiration.
     */
    private Claims extractAllClaims(String token) {           // Line 21
        return Jwts.parser()                                  // Line 22
            .verifyWith(key)                                  // Line 23
            .build()
            .parseSignedClaims(token)                         // Line 24
            .getPayload();                                    // Line 25
    }

    /**
     * Get the expiration time in milliseconds.
     */
    public long getExpirationMs() {
        return expirationMs;
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `SecretKey key` | The cryptographic key used for signing and verifying tokens |
| 2 | `long expirationMs` | How long tokens are valid (in milliseconds) |
| 3 | `@Value("${jwt.secret}")` | Reads the secret from `application.properties` |
| 4 | `@Value("${jwt.expiration}")` | Reads the expiration time from properties |
| 5 | `Keys.hmacShaKeyFor(...)` | Creates a proper HMAC-SHA key from the secret string |
| 6 | `generateToken(...)` | Creates a new JWT token for a given user |
| 7 | `new Date()` | Current timestamp |
| 8 | `now.getTime() + expirationMs` | Calculates the expiration time (now + 2 hours) |
| 9 | `Jwts.builder()` | Starts building a JWT token |
| 10 | `.subject(username)` | Sets the `sub` claim (who the token is for) |
| 11 | `.claim("role", role)` | Adds a custom claim for the user's role |
| 12 | `.issuedAt(now)` | Sets the `iat` claim (when the token was created) |
| 13 | `.expiration(expiration)` | Sets the `exp` claim (when the token expires) |
| 14 | `.signWith(key)` | Signs the token with the secret key. This creates the signature |
| 15 | `.compact()` | Builds the final JWT string (header.payload.signature) |
| 16 | `extractUsername(...)` | Gets the username from a token by reading the `sub` claim |
| 17 | `extractRole(...)` | Gets the role from a token by reading the custom `role` claim |
| 18 | `isTokenValid(...)` | Checks if a token is valid. If parsing succeeds, the token is valid |
| 19 | `extractAllClaims(token)` | If this throws an exception, the token is invalid |
| 20 | `JwtException` | Catches expired tokens, tampered tokens, and malformed tokens |
| 21 | `extractAllClaims(...)` | The core parsing method that validates and extracts token data |
| 22 | `Jwts.parser()` | Creates a JWT parser |
| 23 | `.verifyWith(key)` | Tells the parser to verify the signature with our secret key |
| 24 | `.parseSignedClaims(token)` | Parses the token, verifies the signature, checks expiration |
| 25 | `.getPayload()` | Extracts the claims (payload data) from the verified token |

---

## Step 7: Create the JwtAuthenticationFilter

This filter intercepts every request, checks for a JWT token in the Authorization header, and sets up the security context if the token is valid.

```java
package com.example.demo.filter;

import com.example.demo.security.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication
    .UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority
    .SimpleGrantedAuthority;
import org.springframework.security.core.context
    .SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
public class JwtAuthenticationFilter
        extends OncePerRequestFilter {                       // Line 1

    private final JwtUtil jwtUtil;

    public JwtAuthenticationFilter(JwtUtil jwtUtil) {        // Line 2
        this.jwtUtil = jwtUtil;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        // Step 1: Get the Authorization header
        String authHeader =
            request.getHeader("Authorization");              // Line 3

        // Step 2: Check if it starts with "Bearer "
        if (authHeader == null
                || !authHeader.startsWith("Bearer ")) {      // Line 4
            filterChain.doFilter(request, response);         // Line 5
            return;
        }

        // Step 3: Extract the token (remove "Bearer " prefix)
        String token = authHeader.substring(7);              // Line 6

        // Step 4: Validate the token
        if (jwtUtil.isTokenValid(token)) {                   // Line 7
            // Step 5: Extract user information from token
            String username = jwtUtil.extractUsername(token); // Line 8
            String role = jwtUtil.extractRole(token);        // Line 9

            // Step 6: Create an authentication object
            UsernamePasswordAuthenticationToken authToken =
                new UsernamePasswordAuthenticationToken(
                    username,                                // Line 10
                    null,                                    // Line 11
                    List.of(new SimpleGrantedAuthority(
                        "ROLE_" + role))                     // Line 12
                );

            // Step 7: Set the authentication in the
            // security context
            SecurityContextHolder.getContext()
                .setAuthentication(authToken);                // Line 13
        }

        // Step 8: Continue the filter chain
        filterChain.doFilter(request, response);             // Line 14
    }

    @Override
    protected boolean shouldNotFilter(
            HttpServletRequest request) {
        String path = request.getRequestURI();
        return path.startsWith("/api/auth/")
            || path.startsWith("/h2-console");               // Line 15
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `extends OncePerRequestFilter` | Ensures this filter runs exactly once per request |
| 2 | Constructor injection | Injects the `JwtUtil` for token operations |
| 3 | `request.getHeader("Authorization")` | Gets the Authorization header from the HTTP request |
| 4 | `!authHeader.startsWith("Bearer ")` | JWT tokens are sent as `Bearer <token>`. If the header is missing or does not start with "Bearer ", skip this filter |
| 5 | `filterChain.doFilter(...)` and `return` | No token found -- let the request continue. Other security rules will handle it |
| 6 | `authHeader.substring(7)` | Removes the "Bearer " prefix (7 characters) to get the actual token |
| 7 | `jwtUtil.isTokenValid(token)` | Validates the token's signature and checks if it is expired |
| 8 | `jwtUtil.extractUsername(token)` | Gets the username from the token's payload |
| 9 | `jwtUtil.extractRole(token)` | Gets the role from the token's payload |
| 10 | `username` | The principal (who the user is) |
| 11 | `null` | Credentials (not needed since we already verified the token) |
| 12 | `"ROLE_" + role` | The user's authorities. Spring Security requires the `ROLE_` prefix |
| 13 | `SecurityContextHolder...setAuthentication(...)` | Tells Spring Security that this request is authenticated. Now the user's identity is available throughout the request |
| 14 | `filterChain.doFilter(...)` | Continues processing the request with authentication set |
| 15 | `shouldNotFilter(...)` | Skips the JWT filter for auth endpoints (login/register) and H2 console |

### How the Filter Fits in the Chain

```
+------------------------------------------------------------------+
|  Request with Authorization: Bearer eyJhbG...                    |
+------------------------------------------------------------------+
        |
        v
+------------------------------------------------------------------+
|  JwtAuthenticationFilter (your custom filter)                    |
|  1. Extract token from "Bearer eyJhbG..."                        |
|  2. Validate token (signature + expiration)                      |
|  3. Extract username and role                                    |
|  4. Create Authentication and set in SecurityContext             |
+------------------------------------------------------------------+
        |
        v
+------------------------------------------------------------------+
|  AuthorizationFilter (Spring Security's built-in)                |
|  1. Check: Does this URL require authentication?                 |
|  2. Check: Does the user have the required role?                 |
|  3. If yes -> proceed to controller                              |
|  4. If no  -> 403 Forbidden                                      |
+------------------------------------------------------------------+
        |
        v
+------------------------------------------------------------------+
|  Your Controller                                                 |
+------------------------------------------------------------------+
```

---

## Step 8: Create the Auth Service

```java
package com.example.demo.service;

import com.example.demo.dto.LoginRequest;
import com.example.demo.dto.LoginResponse;
import com.example.demo.dto.RegisterRequest;
import com.example.demo.entity.AppUser;
import com.example.demo.repository.AppUserRepository;
import com.example.demo.security.JwtUtil;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final AppUserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public AuthService(AppUserRepository userRepository,
                       PasswordEncoder passwordEncoder,
                       JwtUtil jwtUtil) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
    }

    /**
     * Register a new user.
     */
    public AppUser register(RegisterRequest request) {        // Line 1

        // Check if username already exists
        if (userRepository.existsByUsername(
                request.getUsername())) {                      // Line 2
            throw new RuntimeException(
                "Username already exists");
        }

        // Check if email already exists
        if (userRepository.existsByEmail(
                request.getEmail())) {                        // Line 3
            throw new RuntimeException(
                "Email already exists");
        }

        // Create new user with hashed password
        AppUser user = new AppUser();
        user.setUsername(request.getUsername());
        user.setPassword(
            passwordEncoder.encode(
                request.getPassword()));                      // Line 4
        user.setEmail(request.getEmail());
        user.setRole("USER");                                 // Line 5

        return userRepository.save(user);                     // Line 6
    }

    /**
     * Authenticate a user and return a JWT token.
     */
    public LoginResponse login(LoginRequest request) {        // Line 7

        // Find user by username
        AppUser user = userRepository
            .findByUsername(request.getUsername())
            .orElseThrow(() -> new RuntimeException(
                "Invalid username or password"));             // Line 8

        // Verify password
        if (!passwordEncoder.matches(
                request.getPassword(),
                user.getPassword())) {                        // Line 9
            throw new RuntimeException(
                "Invalid username or password");              // Line 10
        }

        // Generate JWT token
        String token = jwtUtil.generateToken(
            user.getUsername(), user.getRole());               // Line 11

        // Return response with token
        return new LoginResponse(
            token,
            user.getUsername(),
            user.getRole(),
            jwtUtil.getExpirationMs()                         // Line 12
        );
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `register(...)` | Handles new user registration |
| 2 | `existsByUsername(...)` | Checks for duplicate usernames before registration |
| 3 | `existsByEmail(...)` | Checks for duplicate emails |
| 4 | `passwordEncoder.encode(...)` | Hashes the password with BCrypt before storing. The plain text password is never saved |
| 5 | `user.setRole("USER")` | New users get the USER role by default |
| 6 | `userRepository.save(user)` | Saves the user to the database |
| 7 | `login(...)` | Handles user authentication |
| 8 | `findByUsername(...).orElseThrow(...)` | Finds the user or throws an error. The error message is intentionally vague to prevent username enumeration |
| 9 | `passwordEncoder.matches(rawPassword, hashedPassword)` | Compares the provided password with the stored hash. BCrypt handles the comparison |
| 10 | Same error message | We use the same error for both wrong username and wrong password. This prevents attackers from knowing whether a username exists |
| 11 | `jwtUtil.generateToken(...)` | Creates a JWT token for the authenticated user |
| 12 | `jwtUtil.getExpirationMs()` | Tells the client when the token will expire |

---

## Step 9: Create the Auth Controller

```java
package com.example.demo.controller;

import com.example.demo.dto.LoginRequest;
import com.example.demo.dto.LoginResponse;
import com.example.demo.dto.RegisterRequest;
import com.example.demo.entity.AppUser;
import com.example.demo.service.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(
            @RequestBody RegisterRequest request) {           // Line 1
        try {
            AppUser user = authService.register(request);
            return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(Map.of(
                    "message", "User registered successfully",
                    "username", user.getUsername()
                ));
        } catch (RuntimeException e) {
            return ResponseEntity
                .badRequest()
                .body(Map.of("error", e.getMessage()));       // Line 2
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(
            @RequestBody LoginRequest request) {              // Line 3
        try {
            LoginResponse response = authService.login(request);
            return ResponseEntity.ok(response);               // Line 4
        } catch (RuntimeException e) {
            return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED)
                .body(Map.of("error", e.getMessage()));       // Line 5
        }
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `ResponseEntity<?>` | The `?` wildcard allows returning different response types (success or error) |
| 2 | `badRequest()` | Returns 400 Bad Request for registration errors (duplicate username/email) |
| 3 | `@RequestBody LoginRequest` | Deserializes the JSON request body into a `LoginRequest` object |
| 4 | `ResponseEntity.ok(response)` | Returns 200 OK with the JWT token |
| 5 | `HttpStatus.UNAUTHORIZED` | Returns 401 for invalid credentials |

---

## Step 10: Configure Security

```java
package com.example.demo.config;

import com.example.demo.filter.JwtAuthenticationFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication
    .UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtFilter;

    public SecurityConfig(JwtAuthenticationFilter jwtFilter) {
        this.jwtFilter = jwtFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http) throws Exception {

        http
            .csrf(csrf -> csrf.disable())                    // Line 1

            .sessionManagement(session -> session
                .sessionCreationPolicy(
                    SessionCreationPolicy.STATELESS))         // Line 2

            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()  // Line 3
                .requestMatchers("/h2-console/**").permitAll()
                .requestMatchers("/api/admin/**")
                    .hasRole("ADMIN")                        // Line 4
                .anyRequest().authenticated()                // Line 5
            )

            .addFilterBefore(jwtFilter,
                UsernamePasswordAuthenticationFilter.class)   // Line 6

            .headers(headers ->
                headers.frameOptions(frame ->
                    frame.sameOrigin()));

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `csrf.disable()` | Disables CSRF because we use stateless JWT authentication, not sessions |
| 2 | `SessionCreationPolicy.STATELESS` | Tells Spring to never create HTTP sessions. Every request must include a JWT token. This is key for REST APIs |
| 3 | `"/api/auth/**".permitAll()` | Login and registration endpoints are public (no token needed) |
| 4 | `hasRole("ADMIN")` | Only admin users can access admin endpoints |
| 5 | `anyRequest().authenticated()` | Everything else requires a valid JWT token |
| 6 | `addFilterBefore(jwtFilter, ...)` | Inserts your JWT filter before Spring's default authentication filter. This ensures JWT tokens are processed before any other authentication |

---

## Step 11: Create a Protected Controller

```java
package com.example.demo.controller;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    @GetMapping
    public List<Map<String, Object>> getAllProducts(
            Authentication auth) {

        return List.of(
            Map.of("id", 1, "name", "Laptop",
                   "price", 999.99,
                   "requestedBy", auth.getName()),
            Map.of("id", 2, "name", "Phone",
                   "price", 699.99,
                   "requestedBy", auth.getName())
        );
    }
}
```

```java
package com.example.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

    @GetMapping("/dashboard")
    public Map<String, Object> dashboard() {
        return Map.of(
            "message", "Admin Dashboard",
            "stats", Map.of(
                "users", 150,
                "products", 45
            )
        );
    }
}
```

---

## Testing the Complete Flow

### Step 1: Register a New User

```
POST http://localhost:8080/api/auth/register
Content-Type: application/json

{
    "username": "alice",
    "password": "password123",
    "email": "alice@example.com"
}
```

**Response (201 Created):**

```json
{
    "message": "User registered successfully",
    "username": "alice"
}
```

**Console SQL output:**

```sql
Hibernate:
    insert into app_users (email, password, role, username)
    values (?, ?, ?, ?)
```

### Step 2: Log In

```
POST http://localhost:8080/api/auth/login
Content-Type: application/json

{
    "username": "alice",
    "password": "password123"
}
```

**Response (200 OK):**

```json
{
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbGljZSIsInJvbGUiOiJVU0VSIiwiaWF0IjoxNzA5MjM0NTY3LCJleHAiOjE3MDkyNDE3Njd9.K8vJx2QfbPn3hS4dF2zj7wR9nL1mX6pY5tG3kH8cN0o",
    "username": "alice",
    "role": "USER",
    "expiresIn": 7200000
}
```

### Step 3: Access a Protected Endpoint

```
GET http://localhost:8080/api/products
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbGljZSIsInJvbGUiOiJVU0VSIiwiaWF0IjoxNzA5MjM0NTY3LCJleHAiOjE3MDkyNDE3Njd9.K8vJx2QfbPn3hS4dF2zj7wR9nL1mX6pY5tG3kH8cN0o
```

**Response (200 OK):**

```json
[
    {"id": 1, "name": "Laptop", "price": 999.99, "requestedBy": "alice"},
    {"id": 2, "name": "Phone", "price": 699.99, "requestedBy": "alice"}
]
```

### Step 4: Access Without Token

```
GET http://localhost:8080/api/products
```

**Response (401 Unauthorized):**

```json
{
    "error": "Unauthorized",
    "status": 401
}
```

### Step 5: Access Admin Endpoint (alice has USER role, not ADMIN)

```
GET http://localhost:8080/api/admin/dashboard
Authorization: Bearer eyJhbG...(alice's token)
```

**Response (403 Forbidden):**

```json
{
    "error": "Forbidden",
    "status": 403
}
```

---

## Complete Authentication Flow Diagram

```
+-----------------------------------------------------------------+
|                                                                 |
|  REGISTRATION FLOW                                              |
|  ================                                               |
|                                                                 |
|  Client                    Server                               |
|    |                         |                                  |
|    |  POST /api/auth/register|                                  |
|    |  {username, password,   |                                  |
|    |   email}                |                                  |
|    |------------------------>|                                  |
|    |                         |  1. Check username not taken     |
|    |                         |  2. Check email not taken        |
|    |                         |  3. Hash password (BCrypt)       |
|    |                         |  4. Save user to database       |
|    |   201 Created           |                                  |
|    |<------------------------|                                  |
|                                                                 |
|                                                                 |
|  LOGIN FLOW                                                     |
|  ==========                                                     |
|                                                                 |
|  Client                    Server                               |
|    |                         |                                  |
|    |  POST /api/auth/login   |                                  |
|    |  {username, password}   |                                  |
|    |------------------------>|                                  |
|    |                         |  1. Find user by username        |
|    |                         |  2. Verify password (BCrypt)     |
|    |                         |  3. Generate JWT token           |
|    |   200 OK                |                                  |
|    |   {token, username,     |                                  |
|    |    role, expiresIn}     |                                  |
|    |<------------------------|                                  |
|    |                         |                                  |
|    |  (Client stores token)  |                                  |
|                                                                 |
|                                                                 |
|  AUTHENTICATED REQUEST FLOW                                     |
|  ==========================                                     |
|                                                                 |
|  Client                    Server                               |
|    |                         |                                  |
|    |  GET /api/products      |                                  |
|    |  Authorization:         |                                  |
|    |  Bearer eyJhbG...       |                                  |
|    |------------------------>|                                  |
|    |                         |  1. JwtFilter extracts token     |
|    |                         |  2. Validate signature           |
|    |                         |  3. Check not expired            |
|    |                         |  4. Extract username + role      |
|    |                         |  5. Set SecurityContext          |
|    |                         |  6. AuthorizationFilter checks   |
|    |                         |     role permissions             |
|    |                         |  7. Controller handles request   |
|    |   200 OK + data         |                                  |
|    |<------------------------|                                  |
|                                                                 |
+-----------------------------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Storing JWT Secret in Code

```java
// WRONG - Secret key hardcoded in source code
private static final String SECRET = "mySecretKey123";
// Anyone who sees your code knows the secret!

// CORRECT - Use application properties or environment variables
@Value("${jwt.secret}")
private String secret;

// BEST - Use environment variables in production
// Set JWT_SECRET=... in your deployment environment
// application.properties:
// jwt.secret=${JWT_SECRET}
```

### Mistake 2: Not Adding "ROLE_" Prefix in the Filter

```java
// WRONG - Missing ROLE_ prefix
new SimpleGrantedAuthority(role)  // role = "USER"
// Spring checks for "ROLE_USER" but finds "USER"
// Authorization will fail!

// CORRECT - Add the ROLE_ prefix
new SimpleGrantedAuthority("ROLE_" + role)  // becomes "ROLE_USER"
```

### Mistake 3: Using Sessions with JWT

```java
// WRONG - Creating sessions defeats the purpose of JWT
// If you use JWT, the server should be stateless
http.sessionManagement(session -> session
    .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED));

// CORRECT - Stateless session management with JWT
http.sessionManagement(session -> session
    .sessionCreationPolicy(SessionCreationPolicy.STATELESS));
```

### Mistake 4: Not Handling Token Expiration on the Client

```javascript
// WRONG - Client ignores token expiration
// Keeps using an expired token and gets 401 errors

// CORRECT - Client checks expiration and refreshes
// Store expiresIn from the login response
// Before each request, check if the token is about to expire
// If so, redirect to login or use a refresh token
```

### Mistake 5: Sending Token in URL

```
// WRONG - Token visible in URL, browser history, server logs
GET /api/products?token=eyJhbG...

// CORRECT - Token in Authorization header (not logged by default)
GET /api/products
Authorization: Bearer eyJhbG...
```

---

## Best Practices

1. **Use environment variables for secrets**: Never hardcode JWT secrets. Use environment variables or a secrets manager in production.

2. **Set reasonable expiration times**: Short-lived tokens (15 minutes to 2 hours) are more secure. Use refresh tokens for longer sessions.

3. **Use HTTPS in production**: JWTs are not encrypted -- they are only signed. Without HTTPS, anyone can read the token contents (including the username and role).

4. **Do not store sensitive data in the payload**: Remember, the JWT payload is Base64-encoded, not encrypted. Anyone can decode it. Never put passwords, credit card numbers, or other secrets in the payload.

5. **Use a strong secret key**: The secret must be at least 256 bits (32 characters) for HS256. Use a randomly generated key, not something guessable.

6. **Return generic error messages**: Do not say "username not found" or "wrong password." Say "invalid credentials" to prevent attackers from enumerating valid usernames.

7. **Use stateless sessions**: When using JWT, set `SessionCreationPolicy.STATELESS`. This ensures the server does not create sessions, and each request is independently authenticated.

8. **Always validate tokens server-side**: Never trust a token just because it exists. Always verify the signature and check the expiration.

---

## Quick Summary

```
+------------------------------------------+
|  JWT Authentication Quick Reference      |
+------------------------------------------+
|                                          |
|  JWT STRUCTURE:                          |
|  Header.Payload.Signature               |
|                                          |
|  FLOW:                                   |
|  1. Register -> POST /api/auth/register |
|  2. Login    -> POST /api/auth/login    |
|     Response: {token: "eyJhbG..."}      |
|  3. Access   -> GET /api/products       |
|     Header: Authorization: Bearer token |
|                                          |
|  KEY CLASSES:                            |
|  JwtUtil    -> generate/validate tokens |
|  JwtFilter  -> intercept requests       |
|  AuthService -> login/register logic    |
|                                          |
|  DEPENDENCIES:                           |
|  jjwt-api + jjwt-impl + jjwt-jackson   |
|                                          |
|  SECURITY CONFIG:                        |
|  - CSRF disabled                        |
|  - Sessions stateless                   |
|  - Auth endpoints public                |
|  - JWT filter added before default      |
|                                          |
+------------------------------------------+
```

---

## Key Points

1. A JWT is a self-contained token with three parts: header (algorithm), payload (claims/data), and signature (proof of authenticity).

2. The flow is: register, login (get token), and use the token in the `Authorization: Bearer <token>` header for all subsequent requests.

3. `JwtUtil` handles token generation and validation using the jjwt library.

4. `JwtAuthenticationFilter` extends `OncePerRequestFilter` and intercepts every request to extract and validate JWT tokens.

5. The security configuration must be stateless (`SessionCreationPolicy.STATELESS`) when using JWT.

6. Passwords are always hashed with BCrypt before storage. The plain text password is never saved.

7. JWT tokens are signed, not encrypted. Do not put sensitive data in the payload.

8. Use environment variables for the JWT secret key in production. Never hardcode it.

---

## Practice Questions

1. What are the three parts of a JWT? What does each part contain?

2. Why is the signature important? What happens if someone modifies the payload of a JWT?

3. Explain the difference between `SessionCreationPolicy.STATELESS` and `SessionCreationPolicy.IF_REQUIRED`. Why must you use `STATELESS` with JWT?

4. Why do we use the same error message for both "user not found" and "wrong password" during login?

5. What is the purpose of `addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)`? Why does the JWT filter need to run before the default authentication filter?

---

## Exercises

### Exercise 1: Refresh Token System

Implement a refresh token system:
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (7 days) stored in the database
- `POST /api/auth/refresh` endpoint that accepts a refresh token and returns a new access token
- Invalidate refresh tokens on logout

### Exercise 2: Role-Based Registration

Modify the registration to support creating ADMIN users:
- Only existing ADMIN users can create new ADMIN accounts
- Regular registration creates USER accounts
- Add a `POST /api/admin/create-admin` endpoint that requires ADMIN role

### Exercise 3: Token Blacklisting

Implement a logout system:
- `POST /api/auth/logout` endpoint that invalidates the current token
- Store blacklisted tokens in an in-memory set or database table
- Check the blacklist in `JwtAuthenticationFilter` before accepting a token
- Clean up expired tokens from the blacklist periodically

---

## What Is Next?

Congratulations! You now have a complete, secured Spring Boot application with JWT authentication. You can register users, log them in, and protect your API endpoints with role-based access control. In the chapters ahead, you will learn about exception handling, validation, testing, and deploying your application to production.
