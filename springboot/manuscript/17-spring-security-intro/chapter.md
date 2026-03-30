# Chapter 17: Introduction to Spring Security

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand the difference between authentication and authorization
- Add Spring Security to a Spring Boot application
- Understand the default security behavior
- Configure a `SecurityFilterChain` bean
- Define permitted (public) and protected routes
- Create in-memory users with roles
- Configure HTTP Basic and form-based login
- Understand CSRF protection and when to disable it
- Read the security filter chain diagram

## Why This Chapter Matters

Imagine you built a beautiful house with no locks on the doors. Anyone can walk in, eat your food, rearrange your furniture, or take your valuables. That is what your API looks like right now. Every endpoint is wide open. Anyone can create, read, update, or delete data.

Security is not optional. Every real application needs it. You need to verify who is making requests (authentication) and what they are allowed to do (authorization).

Spring Security is the standard framework for securing Spring Boot applications. It is powerful but can be intimidating for beginners because it does a lot automatically. This chapter breaks it down step by step so you understand exactly what happens when you add security to your application.

---

## Authentication vs Authorization

These two concepts are the foundation of security. They sound similar but are very different.

```
+-------------------------------------------------------------------+
|                                                                   |
|   AUTHENTICATION                    AUTHORIZATION                 |
|   "Who are you?"                    "What can you do?"            |
|                                                                   |
|   +------------------+             +------------------+           |
|   | Show me your ID  |             | What's your role?|           |
|   |                  |             |                  |           |
|   | Username: alice  |             | Role: ADMIN      |           |
|   | Password: ****   |             |                  |           |
|   +------------------+             +------------------+           |
|                                                                   |
|   Verifies identity               Checks permissions              |
|   Happens FIRST                   Happens AFTER authentication    |
|   "Are you really Alice?"         "Can Alice delete products?"    |
|                                                                   |
+-------------------------------------------------------------------+
```

### Real-Life Analogy

Think of an office building:

1. **Authentication** = The security guard at the entrance checks your employee badge. They verify you are who you claim to be.
2. **Authorization** = Your badge has a color code. Green badges can access floors 1-3. Red badges can access all floors. The badge color determines what rooms you can enter.

Just because you are authenticated (the guard let you in) does not mean you are authorized for everything (you might not have access to the server room).

```
+----------------------------------------------------------+
|  Step 1: AUTHENTICATION                                  |
|  Guard: "Badge please." (checking identity)              |
|  You: Show badge                                         |
|  Guard: "OK, you are Alice. Come in."                    |
+----------------------------------------------------------+
                    |
                    v
+----------------------------------------------------------+
|  Step 2: AUTHORIZATION                                   |
|  You try to open the server room door                    |
|  System: "Alice has role USER, not ADMIN"                |
|  System: "Access DENIED"                                 |
+----------------------------------------------------------+
```

---

## Adding Spring Security

### Step 1: Add the Dependency

Add `spring-boot-starter-security` to your `pom.xml`:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

That is it. Just one dependency. No version needed -- Spring Boot manages it.

### What Happens Immediately

The moment you add this dependency and restart your application, **everything changes**:

1. **All endpoints are protected** -- Every URL requires authentication
2. **A login page appears** -- Going to any URL redirects you to `/login`
3. **A default user is created** -- Username is `user`, password is printed in the console
4. **CSRF protection is enabled** -- POST, PUT, DELETE requests need a CSRF token
5. **Session management is enabled** -- After login, a session cookie tracks you

### Finding the Default Password

Look in the console for a line like this:

```
Using generated security password: 8f32a1b4-5678-9abc-def0-123456789abc

This generated password is for development use only. Your security
configuration must be updated before running your application in production.
```

You can now log in with:
- **Username:** `user`
- **Password:** (the generated password from the console)

### Testing Default Security

Try accessing your API:

```
GET http://localhost:8080/api/products
```

**Without authentication:**

```
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Basic realm="Realm"
```

**With HTTP Basic authentication:**

```
GET http://localhost:8080/api/products
Authorization: Basic dXNlcjo4ZjMyYTFiNC01Njc4LTlhYmMtZGVmMC0xMjM0NTY3ODlhYmM=
```

Response: `200 OK` with your data.

---

## The Security Filter Chain

Spring Security works through a chain of filters that process every request. This is one of the most important concepts to understand.

```
+------------------------------------------------------------------+
|                     INCOMING HTTP REQUEST                        |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                   SPRING SECURITY FILTER CHAIN                   |
|                                                                  |
|  +------------------------------------------------------------+ |
|  | 1. SecurityContextPersistenceFilter                         | |
|  |    Load security context from session                       | |
|  +------------------------------------------------------------+ |
|  | 2. HeaderWriterFilter                                       | |
|  |    Add security headers (X-Frame-Options, etc.)             | |
|  +------------------------------------------------------------+ |
|  | 3. CsrfFilter                                               | |
|  |    Validate CSRF token for POST/PUT/DELETE                  | |
|  +------------------------------------------------------------+ |
|  | 4. LogoutFilter                                             | |
|  |    Handle /logout requests                                  | |
|  +------------------------------------------------------------+ |
|  | 5. UsernamePasswordAuthenticationFilter                     | |
|  |    Handle form login (/login POST)                          | |
|  +------------------------------------------------------------+ |
|  | 6. BasicAuthenticationFilter                                | |
|  |    Handle HTTP Basic auth (Authorization header)            | |
|  +------------------------------------------------------------+ |
|  | 7. RequestCacheAwareFilter                                  | |
|  |    Cache requests during authentication redirects           | |
|  +------------------------------------------------------------+ |
|  | 8. SecurityContextHolderAwareRequestFilter                  | |
|  |    Wrap request with security methods                       | |
|  +------------------------------------------------------------+ |
|  | 9. AnonymousAuthenticationFilter                            | |
|  |    Assign anonymous identity if not authenticated           | |
|  +------------------------------------------------------------+ |
|  | 10. SessionManagementFilter                                 | |
|  |     Handle session fixation, concurrent sessions            | |
|  +------------------------------------------------------------+ |
|  | 11. ExceptionTranslationFilter                              | |
|  |     Convert security exceptions to HTTP responses           | |
|  +------------------------------------------------------------+ |
|  | 12. FilterSecurityInterceptor (AuthorizationFilter)         | |
|  |     Check if user has permission for this URL               | |
|  +------------------------------------------------------------+ |
|                                                                  |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                      YOUR CONTROLLER                             |
|                  (Only reached if authorized)                     |
+------------------------------------------------------------------+
```

Every request passes through all these filters. Think of it as an airport security line with multiple checkpoints. If you fail any checkpoint, you are turned away.

---

## Configuring SecurityFilterChain

The default behavior protects everything. But most applications need some endpoints to be public (like a login page or product listing) and others to be protected (like admin pages or user profiles).

### Step 2: Create a Security Configuration

```java
package com.example.demo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration                                               // Line 1
@EnableWebSecurity                                           // Line 2
public class SecurityConfig {

    @Bean                                                    // Line 3
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http) throws Exception {            // Line 4

        http
            .authorizeHttpRequests(auth -> auth              // Line 5
                .requestMatchers("/api/public/**").permitAll() // Line 6
                .requestMatchers("/h2-console/**").permitAll() // Line 7
                .requestMatchers("/api/admin/**")
                    .hasRole("ADMIN")                        // Line 8
                .requestMatchers("/api/products/**")
                    .hasAnyRole("USER", "ADMIN")             // Line 9
                .anyRequest().authenticated()                // Line 10
            )
            .httpBasic(basic -> {})                          // Line 11
            .formLogin(form -> {})                           // Line 12
            .csrf(csrf -> csrf.disable());                   // Line 13

        // Allow H2 console frames
        http.headers(headers ->
            headers.frameOptions(frame ->
                frame.sameOrigin()));                        // Line 14

        return http.build();                                 // Line 15
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `@Configuration` | Marks this as a configuration class processed at startup |
| 2 | `@EnableWebSecurity` | Enables Spring Security's web security support |
| 3 | `@Bean` | Registers the `SecurityFilterChain` as a Spring bean |
| 4 | `HttpSecurity http` | The builder object for configuring security rules. Spring injects it |
| 5 | `authorizeHttpRequests(auth -> ...)` | Starts defining URL-based authorization rules |
| 6 | `.requestMatchers("/api/public/**").permitAll()` | URLs starting with `/api/public/` are accessible by everyone, no login needed |
| 7 | `.requestMatchers("/h2-console/**").permitAll()` | Allows access to the H2 console without authentication |
| 8 | `.hasRole("ADMIN")` | Only users with the ADMIN role can access `/api/admin/**` |
| 9 | `.hasAnyRole("USER", "ADMIN")` | Users with either USER or ADMIN role can access `/api/products/**` |
| 10 | `.anyRequest().authenticated()` | Everything else requires the user to be authenticated (any role) |
| 11 | `.httpBasic(basic -> {})` | Enables HTTP Basic authentication (credentials in the Authorization header) |
| 12 | `.formLogin(form -> {})` | Enables form-based login (Spring provides a default login page) |
| 13 | `.csrf(csrf -> csrf.disable())` | Disables CSRF protection. We will discuss why below |
| 14 | `.frameOptions(frame -> frame.sameOrigin())` | Allows H2 console to work (it uses HTML frames) |
| 15 | `http.build()` | Builds and returns the configured `SecurityFilterChain` |

### Understanding Authorization Rules

```
+-----------------------------------------------+
|  Rule Matching Order (TOP to BOTTOM)          |
+-----------------------------------------------+
|                                               |
|  /api/public/**     -->  Everyone (no login)  |
|  /h2-console/**     -->  Everyone (no login)  |
|  /api/admin/**       -->  ADMIN role only     |
|  /api/products/**    -->  USER or ADMIN role  |
|  Everything else     -->  Any logged-in user  |
|                                               |
+-----------------------------------------------+
|  IMPORTANT: Rules are checked in ORDER.       |
|  First matching rule wins. Put specific       |
|  rules BEFORE general ones.                   |
+-----------------------------------------------+
```

### Common Authorization Methods

```
+--------------------------------+---------------------------------------------+
| Method                         | Who Can Access                              |
+--------------------------------+---------------------------------------------+
| .permitAll()                   | Everyone (no authentication needed)         |
| .authenticated()               | Any authenticated user (any role)           |
| .hasRole("ADMIN")              | Only users with ADMIN role                  |
| .hasAnyRole("USER", "ADMIN")   | Users with USER OR ADMIN role               |
| .hasAuthority("WRITE")         | Users with WRITE authority                  |
| .denyAll()                     | Nobody (useful for disabling endpoints)     |
+--------------------------------+---------------------------------------------+
```

**What is the difference between Role and Authority?**

- A **Role** is a group of authorities. Roles are prefixed with `ROLE_` internally (e.g., `ROLE_ADMIN`).
- An **Authority** is a specific permission (e.g., `READ`, `WRITE`, `DELETE`).

When you say `hasRole("ADMIN")`, Spring internally checks for `ROLE_ADMIN`.

---

## In-Memory Users

For development and testing, you can define users directly in your configuration. These users exist only in memory and are lost when the application restarts.

### Step 3: Define In-Memory Users

```java
package com.example.demo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/h2-console/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/products/**")
                    .hasAnyRole("USER", "ADMIN")
                .anyRequest().authenticated()
            )
            .httpBasic(basic -> {})
            .csrf(csrf -> csrf.disable())
            .headers(headers ->
                headers.frameOptions(frame -> frame.sameOrigin()));

        return http.build();
    }

    @Bean
    public UserDetailsService userDetailsService() {          // Line 1

        UserDetails user = User.builder()                     // Line 2
            .username("alice")                                // Line 3
            .password(passwordEncoder().encode("password123")) // Line 4
            .roles("USER")                                    // Line 5
            .build();

        UserDetails admin = User.builder()
            .username("bob")
            .password(passwordEncoder().encode("admin456"))
            .roles("ADMIN")                                   // Line 6
            .build();

        UserDetails superUser = User.builder()
            .username("charlie")
            .password(passwordEncoder().encode("super789"))
            .roles("USER", "ADMIN")                           // Line 7
            .build();

        return new InMemoryUserDetailsManager(
            user, admin, superUser);                          // Line 8
    }

    @Bean
    public PasswordEncoder passwordEncoder() {                // Line 9
        return new BCryptPasswordEncoder();                   // Line 10
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `UserDetailsService` | A Spring Security interface that loads user data. Returns a bean that Spring uses for authentication |
| 2 | `User.builder()` | Starts building a user using Spring Security's `User` class (not your custom `User` entity) |
| 3 | `.username("alice")` | Sets the username for authentication |
| 4 | `.password(passwordEncoder().encode(...))` | Encodes the password using BCrypt. **Never store plain text passwords!** |
| 5 | `.roles("USER")` | Assigns the USER role. Internally stored as `ROLE_USER` |
| 6 | `.roles("ADMIN")` | Assigns the ADMIN role |
| 7 | `.roles("USER", "ADMIN")` | A user can have multiple roles |
| 8 | `InMemoryUserDetailsManager(...)` | Stores users in memory. Pass all users as arguments |
| 9 | `PasswordEncoder` bean | Defines how passwords are encoded and verified |
| 10 | `BCryptPasswordEncoder()` | BCrypt is a strong one-way hashing algorithm. The industry standard for password hashing |

### Why BCrypt?

```
Plain text:     "password123"
                     |
                     v (BCrypt encode)
BCrypt hash:    "$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy"

Key properties:
1. One-way: Cannot reverse the hash to get the password
2. Salted: Same password produces different hashes each time
3. Slow: Intentionally slow to prevent brute-force attacks
```

---

## HTTP Basic Authentication

HTTP Basic is the simplest authentication method. The client sends credentials in the `Authorization` header with every request.

```
+------------------------------------------------------------------+
|  HTTP BASIC AUTHENTICATION FLOW                                  |
+------------------------------------------------------------------+
|                                                                  |
|  1. Client sends request WITHOUT credentials                     |
|     GET /api/products                                            |
|                                                                  |
|  2. Server responds with 401 Unauthorized                        |
|     WWW-Authenticate: Basic realm="Realm"                        |
|                                                                  |
|  3. Client sends request WITH credentials                        |
|     GET /api/products                                            |
|     Authorization: Basic YWxpY2U6cGFzc3dvcmQxMjM=               |
|                    |      |                                      |
|                    |      +-- Base64("alice:password123")         |
|                    +--------- Authentication type                |
|                                                                  |
|  4. Server validates credentials                                 |
|     - Decode Base64 to get "alice:password123"                   |
|     - Look up user "alice"                                       |
|     - Verify password matches                                    |
|     - Check if alice has permission for /api/products            |
|                                                                  |
|  5. Server responds with 200 OK and data                         |
|                                                                  |
+------------------------------------------------------------------+
```

### Testing with curl

```bash
# Without authentication - 401 Unauthorized
curl -v http://localhost:8080/api/products

# With authentication (alice has USER role)
curl -u alice:password123 http://localhost:8080/api/products
# 200 OK - alice can access /api/products (requires USER or ADMIN)

# Admin endpoint (alice has USER role, not ADMIN)
curl -u alice:password123 http://localhost:8080/api/admin/dashboard
# 403 Forbidden - alice does not have ADMIN role

# Admin endpoint (bob has ADMIN role)
curl -u bob:admin456 http://localhost:8080/api/admin/dashboard
# 200 OK - bob has ADMIN role

# Public endpoint (no authentication needed)
curl http://localhost:8080/api/public/health
# 200 OK - public endpoints are accessible by everyone
```

---

## Form Login

Form login provides a browser-based login page. When enabled, Spring Security generates a default HTML login form.

```
+------------------------------------------------------------------+
|  FORM LOGIN FLOW                                                 |
+------------------------------------------------------------------+
|                                                                  |
|  1. User visits /api/products in browser                         |
|     (not authenticated)                                          |
|                                                                  |
|  2. Spring redirects to /login                                   |
|     Shows the default login form                                 |
|                                                                  |
|  3. User enters username and password                            |
|     Form submits POST /login                                     |
|                                                                  |
|  4. Spring validates credentials                                 |
|     If valid: Redirect to the original URL (/api/products)       |
|     If invalid: Redirect to /login?error                         |
|                                                                  |
|  5. Spring creates a session cookie (JSESSIONID)                 |
|     All subsequent requests use this cookie                      |
|     User does not need to log in again                           |
|                                                                  |
+------------------------------------------------------------------+
```

### Customizing the Form Login

```java
http
    .formLogin(form -> form
        .loginPage("/custom-login")          // Custom login page URL
        .loginProcessingUrl("/perform-login") // URL to submit the form to
        .defaultSuccessUrl("/dashboard")     // Redirect after successful login
        .failureUrl("/custom-login?error")   // Redirect after failed login
    );
```

For REST APIs, you typically use HTTP Basic or JWT (next chapter) instead of form login.

---

## CSRF Protection

CSRF (Cross-Site Request Forgery) is an attack where a malicious website tricks your browser into making requests to your application using your existing session.

```
+------------------------------------------------------------------+
|  CSRF ATTACK SCENARIO                                            |
+------------------------------------------------------------------+
|                                                                  |
|  1. Alice logs into yourbank.com                                 |
|     Browser stores session cookie                                |
|                                                                  |
|  2. Alice visits evil-site.com (in another tab)                  |
|     evil-site.com has hidden form:                               |
|     <form action="yourbank.com/transfer" method="POST">          |
|       <input name="to" value="hacker" />                         |
|       <input name="amount" value="10000" />                      |
|     </form>                                                      |
|     <script>document.forms[0].submit()</script>                  |
|                                                                  |
|  3. Browser sends the POST to yourbank.com                       |
|     WITH Alice's session cookie (automatic!)                     |
|                                                                  |
|  4. yourbank.com thinks Alice is making the transfer             |
|     $10,000 goes to the hacker                                   |
|                                                                  |
+------------------------------------------------------------------+
```

**How CSRF protection works:**

Spring Security generates a random CSRF token for each session. Every form submission (POST, PUT, DELETE) must include this token. Since the evil site cannot access the token, it cannot forge valid requests.

### When to Disable CSRF

For REST APIs that use token-based authentication (like JWT), you typically disable CSRF because:

1. REST APIs do not use browser sessions
2. JWT tokens are not automatically sent by the browser (unlike cookies)
3. The client must explicitly include the token in headers

```java
// For REST APIs with JWT - disable CSRF
.csrf(csrf -> csrf.disable())

// For traditional web applications with sessions - keep CSRF enabled
.csrf(csrf -> {})  // Enabled by default
```

---

## Creating Test Controllers

Let us create controllers to test our security configuration:

```java
package com.example.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/public")
public class PublicController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of(
            "status", "UP",
            "message", "Application is running"
        );
    }

    @GetMapping("/info")
    public Map<String, String> info() {
        return Map.of(
            "app", "Spring Security Demo",
            "version", "1.0.0"
        );
    }
}
```

```java
package com.example.demo.controller;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/user")
public class UserController {

    @GetMapping("/profile")
    public Map<String, Object> getProfile() {
        Authentication auth =
            SecurityContextHolder.getContext()
                .getAuthentication();                         // Line 1

        return Map.of(
            "username", auth.getName(),                       // Line 2
            "authorities", auth.getAuthorities().toString()   // Line 3
        );
    }
}
```

**Line-by-line explanation:**

| Line | Code | What It Does |
|------|------|-------------|
| 1 | `SecurityContextHolder.getContext().getAuthentication()` | Gets the currently authenticated user's details from the security context |
| 2 | `auth.getName()` | Returns the username of the authenticated user |
| 3 | `auth.getAuthorities()` | Returns the user's roles/authorities (e.g., `[ROLE_USER]`) |

You can also inject `Authentication` directly as a method parameter:

```java
@GetMapping("/profile")
public Map<String, Object> getProfile(Authentication auth) {
    return Map.of(
        "username", auth.getName(),
        "authorities", auth.getAuthorities().toString()
    );
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
            "message", "Welcome to the admin dashboard",
            "stats", Map.of(
                "totalUsers", 150,
                "totalProducts", 45,
                "totalOrders", 320
            )
        );
    }
}
```

### Testing Results

```
# Public - No auth needed
GET /api/public/health        -> 200 OK

# User profile - requires authentication
GET /api/user/profile
  as alice (USER)             -> 200 OK {"username":"alice","authorities":"[ROLE_USER]"}
  as bob (ADMIN)              -> 200 OK {"username":"bob","authorities":"[ROLE_ADMIN]"}
  no auth                     -> 401 Unauthorized

# Products - requires USER or ADMIN role
GET /api/products
  as alice (USER)             -> 200 OK
  as bob (ADMIN)              -> 200 OK
  no auth                     -> 401 Unauthorized

# Admin - requires ADMIN role
GET /api/admin/dashboard
  as alice (USER)             -> 403 Forbidden
  as bob (ADMIN)              -> 200 OK
  as charlie (USER+ADMIN)     -> 200 OK
  no auth                     -> 401 Unauthorized
```

Notice the difference between 401 and 403:
- **401 Unauthorized** = You have not proven who you are (not authenticated)
- **403 Forbidden** = We know who you are, but you do not have permission (not authorized)

---

## Complete Project Structure

```
src/main/java/com/example/demo/
├── DemoApplication.java
├── config/
│   └── SecurityConfig.java
├── controller/
│   ├── AdminController.java
│   ├── ProductController.java
│   ├── PublicController.java
│   └── UserController.java
├── entity/
│   └── Product.java
├── repository/
│   └── ProductRepository.java
└── service/
    └── ProductService.java

src/main/resources/
├── application.properties
└── data.sql
```

**application.properties:**

```properties
spring.application.name=security-demo
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=false
spring.jpa.defer-datasource-initialization=true

# Logging security events
logging.level.org.springframework.security=DEBUG
```

Setting `logging.level.org.springframework.security=DEBUG` will show you exactly what Spring Security does with each request. Very helpful for learning and debugging.

---

## Security Flow Summary

```
+-----------------------------------------------------------------+
|  Complete Security Flow for a Request                           |
+-----------------------------------------------------------------+
|                                                                 |
|  Client -> GET /api/products                                    |
|  Authorization: Basic YWxpY2U6cGFzc3dvcmQxMjM=                 |
|                                                                 |
|  Step 1: Security Filter Chain                                  |
|  +---------------------------------------------------------+   |
|  | BasicAuthenticationFilter:                               |   |
|  |   - Extract "alice:password123" from header              |   |
|  |   - Look up user "alice" via UserDetailsService          |   |
|  |   - Verify password with BCryptPasswordEncoder           |   |
|  |   - Password matches! Create Authentication object       |   |
|  |   - Store in SecurityContextHolder                       |   |
|  +---------------------------------------------------------+   |
|                                                                 |
|  Step 2: Authorization                                          |
|  +---------------------------------------------------------+   |
|  | AuthorizationFilter:                                     |   |
|  |   - URL: /api/products/** -> requires USER or ADMIN      |   |
|  |   - Alice has role: ROLE_USER                            |   |
|  |   - ROLE_USER matches! Access GRANTED                    |   |
|  +---------------------------------------------------------+   |
|                                                                 |
|  Step 3: Controller                                             |
|  +---------------------------------------------------------+   |
|  | ProductController.getAllProducts() executes               |   |
|  | Returns list of products                                 |   |
|  +---------------------------------------------------------+   |
|                                                                 |
|  Response: 200 OK + product data                                |
|                                                                 |
+-----------------------------------------------------------------+
```

---

## Common Mistakes

### Mistake 1: Putting General Rules Before Specific Ones

```java
// WRONG - anyRequest().authenticated() matches everything first
// The admin and public rules never get checked
http.authorizeHttpRequests(auth -> auth
    .anyRequest().authenticated()              // Catches everything!
    .requestMatchers("/api/public/**").permitAll()  // Never reached
    .requestMatchers("/api/admin/**").hasRole("ADMIN") // Never reached
);

// CORRECT - Put specific rules first, general rule last
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/api/public/**").permitAll()
    .requestMatchers("/api/admin/**").hasRole("ADMIN")
    .anyRequest().authenticated()              // Catches the rest
);
```

### Mistake 2: Not Encoding Passwords

```java
// WRONG - Storing plain text password
// Spring Security 5+ REQUIRES encoded passwords
UserDetails user = User.builder()
    .username("alice")
    .password("password123")  // Will throw error!
    .roles("USER")
    .build();

// CORRECT - Encode password with BCrypt
UserDetails user = User.builder()
    .username("alice")
    .password(passwordEncoder.encode("password123"))
    .roles("USER")
    .build();
```

### Mistake 3: Forgetting H2 Console Configuration

```java
// WRONG - H2 console will not work
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/h2-console/**").permitAll()
    // Missing: frame options and CSRF configuration
);

// CORRECT - H2 console needs frame options and CSRF exceptions
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/h2-console/**").permitAll()
)
.csrf(csrf -> csrf.disable())  // or csrf.ignoringRequestMatchers("/h2-console/**")
.headers(headers ->
    headers.frameOptions(frame -> frame.sameOrigin()));
```

### Mistake 4: Using hasRole with ROLE_ Prefix

```java
// WRONG - Do not include the ROLE_ prefix
.requestMatchers("/api/admin/**").hasRole("ROLE_ADMIN")
// This checks for "ROLE_ROLE_ADMIN" internally!

// CORRECT - Spring adds ROLE_ automatically
.requestMatchers("/api/admin/**").hasRole("ADMIN")
// This checks for "ROLE_ADMIN" internally
```

---

## Best Practices

1. **Always use BCrypt**: Never store passwords in plain text. BCrypt is the recommended password encoder.

2. **Order rules from specific to general**: Put specific URL patterns before `anyRequest()`.

3. **Disable CSRF for REST APIs**: If you use stateless authentication (like JWT), disable CSRF. Keep it enabled for session-based web applications.

4. **Use roles for coarse-grained access**: Roles like USER, ADMIN, MODERATOR work well for most applications.

5. **Enable security logging for development**: Set `logging.level.org.springframework.security=DEBUG` to see exactly what Spring Security does.

6. **Do not use in-memory users in production**: In-memory users are for development only. In production, load users from a database.

7. **Return proper HTTP status codes**: 401 for unauthenticated, 403 for unauthorized. Spring Security handles this automatically.

8. **Keep security configuration in one place**: Have a single `SecurityConfig` class that contains all your security rules.

---

## Quick Summary

```
+------------------------------------------+
|  Spring Security Quick Reference         |
+------------------------------------------+
|                                          |
|  DEPENDENCY:                             |
|  spring-boot-starter-security            |
|                                          |
|  DEFAULT BEHAVIOR:                       |
|  - All endpoints protected               |
|  - Default user: "user"                 |
|  - Password: printed in console         |
|  - Login page at /login                 |
|                                          |
|  KEY CLASSES:                            |
|  SecurityFilterChain -> security rules  |
|  UserDetailsService  -> user storage    |
|  PasswordEncoder     -> password hashing|
|                                          |
|  AUTHORIZATION:                          |
|  .permitAll()     -> no auth needed     |
|  .authenticated() -> any logged in user |
|  .hasRole("X")    -> specific role      |
|  .hasAnyRole(..") -> any of the roles   |
|                                          |
|  AUTH METHODS:                           |
|  .httpBasic()     -> Authorization hdr  |
|  .formLogin()     -> login page         |
|                                          |
|  STATUS CODES:                           |
|  401 = Not authenticated                |
|  403 = Not authorized                   |
|                                          |
+------------------------------------------+
```

---

## Key Points

1. **Authentication** verifies identity ("who are you?"). **Authorization** checks permissions ("what can you do?").

2. Adding `spring-boot-starter-security` immediately protects all endpoints and generates a default user.

3. `SecurityFilterChain` is configured through a `@Bean` method using `HttpSecurity`. Rules are matched top to bottom.

4. `permitAll()` makes endpoints public. `hasRole("ADMIN")` restricts to specific roles. `authenticated()` requires any logged-in user.

5. Passwords must be encoded with `BCryptPasswordEncoder`. Never store plain text passwords.

6. In-memory users are for development only. Production applications should load users from a database.

7. CSRF protection should be disabled for stateless REST APIs but kept enabled for session-based web applications.

8. 401 means "not authenticated" (no credentials). 403 means "not authorized" (credentials valid but insufficient permissions).

---

## Practice Questions

1. What is the difference between authentication and authorization? Give a real-world analogy.

2. What happens by default when you add `spring-boot-starter-security` to a project? List at least three changes.

3. Why must authorization rules be ordered from specific to general? What happens if you put `anyRequest().authenticated()` first?

4. Why does Spring Security require passwords to be encoded? What would happen if you used plain text?

5. When should you disable CSRF protection? When should you keep it enabled?

---

## Exercises

### Exercise 1: Multi-Role API

Create a REST API with three roles: USER, MODERATOR, ADMIN. Configure these access rules:
- `/api/public/**` - accessible by everyone
- `/api/posts/**` - accessible by USER, MODERATOR, ADMIN
- `/api/moderate/**` - accessible by MODERATOR, ADMIN
- `/api/admin/**` - accessible by ADMIN only

Create in-memory users for each role and test all combinations.

### Exercise 2: Custom Access Rules

Create a product API where:
- GET endpoints are public (anyone can view products)
- POST and PUT endpoints require the USER role
- DELETE endpoints require the ADMIN role

Hint: Use `.requestMatchers(HttpMethod.GET, "/api/products/**").permitAll()`.

### Exercise 3: Security Debugging

Enable `DEBUG` logging for Spring Security and send requests to different endpoints. Trace each request through the log output and document:
- Which filters process the request
- Where authentication happens
- Where authorization is checked
- What happens when authentication fails vs. authorization fails

---

## What Is Next?

In-memory users and HTTP Basic authentication work for learning, but production applications need a more robust approach. In the next chapter, you will learn about **JWT Authentication** -- the industry standard for securing REST APIs. You will build a complete login and registration flow with JSON Web Tokens.
