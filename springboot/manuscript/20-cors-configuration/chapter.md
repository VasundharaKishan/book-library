# Chapter 20: CORS Configuration

## What You Will Learn

- What CORS is and why browsers enforce it.
- What the Same-Origin Policy is.
- What preflight requests are and when they happen.
- How to use @CrossOrigin for controller-level CORS.
- How to configure global CORS with WebMvcConfigurer.
- How to make CORS work with Spring Security.
- Common CORS errors and how to fix them.

## Why This Chapter Matters

Imagine you are at a restaurant. You order food, and the waiter brings it to your table. Everything works perfectly. Now imagine you try to reach over to the next table and grab their food. The waiter would stop you. That is not your table. That is not your order.

Browsers work the same way. When your frontend application at `http://localhost:3000` tries to call your Spring Boot API at `http://localhost:8080`, the browser says "Wait. Those are different origins. I am not sure you are allowed to do that." This is CORS -- Cross-Origin Resource Sharing.

If you have ever seen the error "Access to XMLHttpRequest has been blocked by CORS policy," this chapter will show you exactly what causes it and how to fix it. Almost every modern web application involves a frontend and backend running on different origins, so understanding CORS is essential.

---

## 20.1 Understanding the Same-Origin Policy

Before we talk about CORS, we need to understand the **Same-Origin Policy**. This is a security feature built into every web browser.

An **origin** is defined by three parts:

```
https://www.example.com:443/products
  |          |              |
  |          |              +-- Port (443)
  |          +----------------- Host (www.example.com)
  +---------------------------- Protocol (https)
```

Two URLs have the **same origin** only if all three parts match:

| URL A | URL B | Same Origin? | Why? |
|-------|-------|-------------|------|
| `http://example.com` | `http://example.com/about` | Yes | Same protocol, host, port |
| `http://example.com` | `https://example.com` | No | Different protocol |
| `http://example.com` | `http://api.example.com` | No | Different host |
| `http://example.com` | `http://example.com:8080` | No | Different port |
| `http://localhost:3000` | `http://localhost:8080` | No | Different port |

The Same-Origin Policy says: **A web page can only make requests to the same origin it came from.**

This means a React app running at `http://localhost:3000` cannot call a Spring Boot API at `http://localhost:8080`. The browser blocks it.

### Why Does This Policy Exist?

Think about this scenario without the Same-Origin Policy:

```
+------------------------------------------------------------+
|  WITHOUT SAME-ORIGIN POLICY (DANGEROUS)                     |
+------------------------------------------------------------+
|                                                              |
|  1. You log into your bank at bank.com                       |
|     Browser stores your session cookie                       |
|          |                                                   |
|          v                                                   |
|  2. You visit evil-site.com in another tab                   |
|          |                                                   |
|          v                                                   |
|  3. evil-site.com runs JavaScript:                           |
|     fetch("https://bank.com/api/transfer",                   |
|       { method: "POST",                                      |
|         body: "amount=10000&to=evil-account" })              |
|          |                                                   |
|          v                                                   |
|  4. Browser sends the request WITH your bank cookie          |
|     Bank thinks it is YOU making the transfer                |
|          |                                                   |
|          v                                                   |
|  5. Your money is gone!                                      |
|                                                              |
+------------------------------------------------------------+
```

The Same-Origin Policy prevents step 3. The browser blocks evil-site.com from making requests to bank.com.

---

## 20.2 What Is CORS?

**CORS** stands for **Cross-Origin Resource Sharing**. It is a mechanism that allows a server to say "I trust requests from these specific origins."

Think of CORS like a bouncer at a club. The Same-Origin Policy is the default rule: "Nobody gets in unless they are on the list." CORS is the VIP list. The server (the club owner) decides who gets on the list.

```
+----------------------------------------------+
|              CORS FLOW                        |
+----------------------------------------------+
|                                               |
|  React App                  Spring Boot API   |
|  (localhost:3000)           (localhost:8080)   |
|       |                          |            |
|       |  GET /api/products       |            |
|       |  Origin: localhost:3000  |            |
|       |------------------------->|            |
|       |                          |            |
|       |                   [Check CORS config] |
|       |                   Is localhost:3000    |
|       |                   allowed?             |
|       |                          |            |
|       |  200 OK                  |            |
|       |  Access-Control-Allow-   |            |
|       |  Origin: localhost:3000  |            |
|       |<-------------------------|            |
|       |                          |            |
|  [Browser checks header]        |            |
|  Origin matches? YES            |            |
|  --> Allow response              |            |
|                                               |
+----------------------------------------------+
```

The key CORS headers are:

| Header | Purpose | Example |
|--------|---------|---------|
| `Access-Control-Allow-Origin` | Which origins are allowed | `http://localhost:3000` |
| `Access-Control-Allow-Methods` | Which HTTP methods are allowed | `GET, POST, PUT, DELETE` |
| `Access-Control-Allow-Headers` | Which request headers are allowed | `Content-Type, Authorization` |
| `Access-Control-Allow-Credentials` | Whether cookies are allowed | `true` |
| `Access-Control-Max-Age` | How long to cache the preflight result | `3600` (seconds) |

---

## 20.3 Preflight Requests

For "simple" requests (GET with no custom headers), the browser sends the request directly and checks the CORS headers in the response.

But for "complex" requests (POST with JSON body, requests with custom headers like Authorization), the browser sends a **preflight request** first. This is an OPTIONS request that asks the server "Am I allowed to do this?"

```
+--------------------------------------------------------+
|               PREFLIGHT FLOW                            |
+--------------------------------------------------------+
|                                                         |
|  Browser                        Spring Boot API         |
|     |                                |                  |
|     |  1. OPTIONS /api/products      |                  |
|     |  Origin: localhost:3000        |                  |
|     |  Access-Control-Request-       |                  |
|     |    Method: POST                |                  |
|     |  Access-Control-Request-       |                  |
|     |    Headers: Content-Type       |                  |
|     |------------------------------->|                  |
|     |                                |                  |
|     |  2. 200 OK                     |                  |
|     |  Access-Control-Allow-Origin:  |                  |
|     |    http://localhost:3000       |                  |
|     |  Access-Control-Allow-Methods: |                  |
|     |    GET, POST, PUT, DELETE      |                  |
|     |  Access-Control-Allow-Headers: |                  |
|     |    Content-Type                |                  |
|     |<-------------------------------|                  |
|     |                                |                  |
|     |  [Preflight passed!]           |                  |
|     |                                |                  |
|     |  3. POST /api/products         |                  |
|     |  Content-Type: application/json|                  |
|     |  Origin: localhost:3000        |                  |
|     |  {"name": "Widget"}            |                  |
|     |------------------------------->|                  |
|     |                                |                  |
|     |  4. 201 Created                |                  |
|     |  Access-Control-Allow-Origin:  |                  |
|     |    http://localhost:3000       |                  |
|     |<-------------------------------|                  |
|                                                         |
+--------------------------------------------------------+
```

### When Does a Preflight Happen?

A preflight request is triggered when:

1. The HTTP method is anything other than GET, HEAD, or POST.
2. The Content-Type header is anything other than `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain`.
3. Custom headers are present (like `Authorization` or `X-Custom-Header`).

Since most REST APIs use `Content-Type: application/json` and `Authorization` headers, almost every API call triggers a preflight.

---

## 20.4 CORS with @CrossOrigin (Controller Level)

The simplest way to enable CORS is to add the `@CrossOrigin` annotation to your controller or method:

```java
// src/main/java/com/example/cors/controller/ProductController.java
package com.example.cors.controller;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;

@RestController
@RequestMapping("/api/products")
@CrossOrigin(origins = "http://localhost:3000")  // Allow this origin
public class ProductController {

    private final List<Map<String, String>> products = new ArrayList<>();

    @GetMapping
    public List<Map<String, String>> getAllProducts() {
        return products;
    }

    @PostMapping
    public Map<String, String> addProduct(
            @RequestBody Map<String, String> product) {
        products.add(product);
        return product;
    }
}
```

**Line-by-line explanation:**

- `@CrossOrigin(origins = "http://localhost:3000")` -- This tells Spring to add CORS headers to all responses from this controller, allowing requests from `http://localhost:3000`.

### More @CrossOrigin Options

```java
@CrossOrigin(
    origins = {"http://localhost:3000", "https://myapp.com"},
    methods = {RequestMethod.GET, RequestMethod.POST},
    allowedHeaders = {"Content-Type", "Authorization"},
    exposedHeaders = {"X-Custom-Header"},
    allowCredentials = "true",
    maxAge = 3600
)
```

| Attribute | Purpose | Default |
|-----------|---------|---------|
| `origins` | Allowed origin URLs | All origins (`*`) |
| `methods` | Allowed HTTP methods | All methods from the mapping |
| `allowedHeaders` | Headers the client can send | All headers (`*`) |
| `exposedHeaders` | Headers the client can read from the response | None |
| `allowCredentials` | Allow cookies and authorization headers | `false` |
| `maxAge` | How long to cache preflight results (seconds) | 1800 (30 minutes) |

### Method-Level @CrossOrigin

You can also apply CORS to individual methods:

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    @GetMapping
    @CrossOrigin(origins = "http://localhost:3000")
    public List<Map<String, String>> getAllProducts() {
        return List.of(Map.of("name", "Widget"));
    }

    @PostMapping
    // No @CrossOrigin here -- only same-origin requests allowed
    public Map<String, String> addProduct(
            @RequestBody Map<String, String> product) {
        return product;
    }
}
```

In this example, `GET /api/products` allows cross-origin requests, but `POST /api/products` does not.

---

## 20.5 Global CORS Configuration with WebMvcConfigurer

Using `@CrossOrigin` on every controller gets repetitive. For global configuration, implement `WebMvcConfigurer`:

```java
// src/main/java/com/example/cors/config/CorsConfig.java
package com.example.cors.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")           // Apply to all /api/ URLs
            .allowedOrigins(
                "http://localhost:3000",          // React dev server
                "https://myapp.com"              // Production frontend
            )
            .allowedMethods(
                "GET", "POST", "PUT", "DELETE", "OPTIONS"
            )
            .allowedHeaders("*")                 // Allow all headers
            .allowCredentials(true)              // Allow cookies
            .maxAge(3600);                       // Cache preflight for 1 hour
    }
}
```

**Line-by-line explanation:**

- `implements WebMvcConfigurer` -- This interface lets you customize Spring MVC behavior. We override `addCorsMappings` to set CORS rules.
- `registry.addMapping("/api/**")` -- Apply these CORS rules to all URLs that start with "/api/". The `**` matches any path underneath.
- `.allowedOrigins(...)` -- List the exact origins that are allowed. You can list multiple origins.
- `.allowedMethods(...)` -- Which HTTP methods are allowed. Include "OPTIONS" for preflight requests.
- `.allowedHeaders("*")` -- Accept any header from the client. You could list specific headers instead.
- `.allowCredentials(true)` -- Allow cookies and Authorization headers. Important: When this is true, you cannot use `"*"` for allowedOrigins. You must list specific origins.
- `.maxAge(3600)` -- The browser can cache the preflight response for 3600 seconds (1 hour). This reduces the number of OPTIONS requests.

### Multiple Path Patterns

You can define different CORS rules for different paths:

```java
@Override
public void addCorsMappings(CorsRegistry registry) {
    // Public API - allow any origin
    registry.addMapping("/api/public/**")
        .allowedOrigins("*")
        .allowedMethods("GET");

    // Protected API - only specific origins
    registry.addMapping("/api/protected/**")
        .allowedOrigins("https://myapp.com")
        .allowedMethods("GET", "POST", "PUT", "DELETE")
        .allowCredentials(true);
}
```

---

## 20.6 CORS with Spring Security

Here is the tricky part. If you are using Spring Security (and you should be), the CORS configuration from `WebMvcConfigurer` alone is **not enough**. Spring Security has its own filter chain that runs before your controllers. If CORS is not configured in the security filter chain, preflight OPTIONS requests will be blocked with a 401 or 403.

```
+------------------------------------------------------+
|  WITHOUT CORS IN SECURITY CONFIG                      |
+------------------------------------------------------+
|                                                       |
|  Browser sends OPTIONS preflight                      |
|       |                                               |
|       v                                               |
|  [Spring Security Filter Chain]                       |
|  "This request has no credentials!"                   |
|  --> 401 Unauthorized                                 |
|                                                       |
|  The actual request never reaches your controller     |
|  and WebMvcConfigurer CORS config is never applied    |
|                                                       |
+------------------------------------------------------+
```

The fix is to configure CORS in your SecurityFilterChain:

```java
// src/main/java/com/example/cors/config/SecurityConfig.java
package com.example.cors.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .cors(cors -> cors
                .configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .httpBasic(httpBasic -> {});

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();

        // Which origins are allowed
        configuration.setAllowedOrigins(List.of(
            "http://localhost:3000",
            "https://myapp.com"
        ));

        // Which HTTP methods are allowed
        configuration.setAllowedMethods(List.of(
            "GET", "POST", "PUT", "DELETE", "OPTIONS"
        ));

        // Which headers are allowed
        configuration.setAllowedHeaders(List.of("*"));

        // Allow cookies and authorization headers
        configuration.setAllowCredentials(true);

        // Cache preflight for 1 hour
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source =
            new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", configuration);

        return source;
    }
}
```

**Line-by-line explanation:**

- `.cors(cors -> cors.configurationSource(corsConfigurationSource()))` -- This tells Spring Security to use our CORS configuration. It processes CORS before authentication, so preflight requests are handled correctly.
- `new CorsConfiguration()` -- Creates a CORS configuration object where we set our rules.
- `configuration.setAllowedOrigins(...)` -- Same as `allowedOrigins` in WebMvcConfigurer, but configured for Spring Security.
- `new UrlBasedCorsConfigurationSource()` -- Maps URL patterns to CORS configurations. You can have different CORS rules for different paths.
- `source.registerCorsConfiguration("/api/**", configuration)` -- Apply our CORS configuration to all URLs starting with "/api/".

```
+------------------------------------------------------+
|  WITH CORS IN SECURITY CONFIG                         |
+------------------------------------------------------+
|                                                       |
|  Browser sends OPTIONS preflight                      |
|       |                                               |
|       v                                               |
|  [Spring Security Filter Chain]                       |
|  [CorsFilter] <-- Handles CORS before auth            |
|  "Origin http://localhost:3000 is allowed"            |
|  --> 200 OK with CORS headers                         |
|       |                                               |
|       v                                               |
|  Browser sends actual request                         |
|       |                                               |
|       v                                               |
|  [Authentication Filter]                              |
|  [Authorization Filter]                               |
|       |                                               |
|       v                                               |
|  [Controller] --> Response with CORS headers          |
|                                                       |
+------------------------------------------------------+
```

---

## 20.7 Using Properties for CORS Configuration

Hard-coding origins in your Java code is not ideal. You might want different origins for development and production. You can use application properties:

```properties
# src/main/resources/application.properties

cors.allowed-origins=http://localhost:3000,http://localhost:5173
cors.allowed-methods=GET,POST,PUT,DELETE,OPTIONS
cors.max-age=3600
```

```properties
# src/main/resources/application-prod.properties

cors.allowed-origins=https://myapp.com,https://www.myapp.com
cors.allowed-methods=GET,POST,PUT,DELETE,OPTIONS
cors.max-age=3600
```

Then read these properties in your configuration:

```java
// src/main/java/com/example/cors/config/CorsProperties.java
package com.example.cors.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
@ConfigurationProperties(prefix = "cors")
public class CorsProperties {

    private List<String> allowedOrigins;
    private List<String> allowedMethods;
    private long maxAge;

    // Getters and setters
    public List<String> getAllowedOrigins() { return allowedOrigins; }
    public void setAllowedOrigins(List<String> allowedOrigins) {
        this.allowedOrigins = allowedOrigins;
    }

    public List<String> getAllowedMethods() { return allowedMethods; }
    public void setAllowedMethods(List<String> allowedMethods) {
        this.allowedMethods = allowedMethods;
    }

    public long getMaxAge() { return maxAge; }
    public void setMaxAge(long maxAge) { this.maxAge = maxAge; }
}
```

```java
// Updated SecurityConfig.java
@Bean
public CorsConfigurationSource corsConfigurationSource(
        CorsProperties corsProperties) {

    CorsConfiguration configuration = new CorsConfiguration();
    configuration.setAllowedOrigins(corsProperties.getAllowedOrigins());
    configuration.setAllowedMethods(corsProperties.getAllowedMethods());
    configuration.setAllowedHeaders(List.of("*"));
    configuration.setAllowCredentials(true);
    configuration.setMaxAge(corsProperties.getMaxAge());

    UrlBasedCorsConfigurationSource source =
        new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", configuration);

    return source;
}
```

Now you can change CORS settings without modifying code, and use different settings per environment.

---

## 20.8 Testing CORS

### Testing with curl

You can simulate a CORS preflight request with curl:

```bash
# Simulate a preflight request
curl -v -X OPTIONS http://localhost:8080/api/products \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```

**Expected Output (CORS configured correctly):**

```
< HTTP/1.1 200
< Access-Control-Allow-Origin: http://localhost:3000
< Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
< Access-Control-Allow-Headers: *
< Access-Control-Allow-Credentials: true
< Access-Control-Max-Age: 3600
```

**Expected Output (CORS NOT configured):**

```
< HTTP/1.1 403
```

No CORS headers in the response means the browser will block the request.

### Testing with a Simple HTML Page

Create a simple HTML file to test CORS from the browser:

```html
<!-- test-cors.html (open this in a browser) -->
<!DOCTYPE html>
<html>
<body>
    <h1>CORS Test</h1>
    <button onclick="testCors()">Test CORS</button>
    <pre id="result"></pre>

    <script>
        async function testCors() {
            try {
                const response = await fetch(
                    'http://localhost:8080/api/products',
                    {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    }
                );
                const data = await response.json();
                document.getElementById('result').textContent =
                    JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').textContent =
                    'CORS Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
```

Open this file in your browser (it will have the origin `null` or `file://`). If CORS is not configured to allow that origin, you will see the error.

---

## 20.9 Common CORS Errors and Solutions

### Error 1: "No 'Access-Control-Allow-Origin' header is present"

```
Access to XMLHttpRequest at 'http://localhost:8080/api/products'
from origin 'http://localhost:3000' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Cause**: CORS is not configured on the server, or the origin is not in the allowed list.

**Fix**: Add CORS configuration and include the origin.

### Error 2: "The value of 'Access-Control-Allow-Credentials' header must be 'true'"

```
Access to XMLHttpRequest at 'http://localhost:8080/api/products'
from origin 'http://localhost:3000' has been blocked by CORS policy:
The value of the 'Access-Control-Allow-Credentials' header in the response
is '' which must be 'true' when the request's credentials mode is 'include'.
```

**Cause**: Your frontend sends `credentials: 'include'` but the server does not set `allowCredentials(true)`.

**Fix**: Add `.allowCredentials(true)` to your CORS configuration.

### Error 3: "Wildcard '*' cannot be used with credentials"

```
Access to XMLHttpRequest has been blocked by CORS policy:
The value of the 'Access-Control-Allow-Origin' header must not be the
wildcard '*' when the request's credentials mode is 'include'.
```

**Cause**: You set `allowCredentials(true)` with `allowedOrigins("*")`. This is not allowed for security reasons.

**Fix**: List specific origins instead of using the wildcard:

```java
// Wrong
configuration.setAllowedOrigins(List.of("*"));
configuration.setAllowCredentials(true);

// Correct
configuration.setAllowedOrigins(List.of(
    "http://localhost:3000"
));
configuration.setAllowCredentials(true);

// Or use allowedOriginPatterns for wildcard with credentials
configuration.setAllowedOriginPatterns(List.of("*"));
configuration.setAllowCredentials(true);
```

### Error 4: "Method PUT is not allowed"

```
Access to XMLHttpRequest has been blocked by CORS policy:
Method PUT is not allowed by Access-Control-Allow-Methods
in preflight response.
```

**Cause**: Your CORS configuration does not include PUT in the allowed methods.

**Fix**: Add PUT to the allowed methods list:

```java
configuration.setAllowedMethods(List.of(
    "GET", "POST", "PUT", "DELETE", "OPTIONS"
));
```

### Error 5: CORS Works Locally but Not in Production

**Cause**: Your production configuration does not include the production frontend origin.

**Fix**: Make sure your production properties include the correct production URL:

```properties
# application-prod.properties
cors.allowed-origins=https://myapp.com,https://www.myapp.com
```

---

## 20.10 CORS Decision Flowchart

Use this flowchart to decide how to configure CORS:

```
+--------------------------------------------------+
|     Do you need CORS?                             |
+--------------------------------------------------+
|                                                   |
|  Is your frontend on a different                  |
|  origin than your backend?                        |
|       |                                           |
|       +--> No --> You do not need CORS            |
|       |                                           |
|       +--> Yes --> Continue                       |
|       |                                           |
|       v                                           |
|  Are you using Spring Security?                   |
|       |                                           |
|       +--> No --> Use WebMvcConfigurer             |
|       |          or @CrossOrigin                   |
|       |                                           |
|       +--> Yes --> Configure CORS in               |
|                    SecurityFilterChain              |
|                    (CorsConfigurationSource)        |
|       |                                           |
|       v                                           |
|  Do you need credentials (cookies,                |
|  Authorization headers)?                          |
|       |                                           |
|       +--> No --> allowedOrigins("*") is fine       |
|       |                                           |
|       +--> Yes --> List specific origins            |
|                    and set allowCredentials(true)   |
|                                                   |
+--------------------------------------------------+
```

---

## Common Mistakes

1. **Configuring CORS only in WebMvcConfigurer when using Spring Security.** Spring Security processes requests before your controllers. You must configure CORS in the SecurityFilterChain or your preflight requests will get 401/403 responses.

2. **Using `allowedOrigins("*")` with `allowCredentials(true)`.** This is not allowed by the CORS specification. Use `allowedOriginPatterns("*")` or list specific origins.

3. **Forgetting to include OPTIONS in allowedMethods.** Preflight requests use the OPTIONS method. If you do not allow it, preflights will fail.

4. **Adding the trailing slash to origins.** `http://localhost:3000/` (with slash) and `http://localhost:3000` (without slash) are different. Use the version without the trailing slash.

5. **Not testing with the browser.** Testing with curl or Postman does not test CORS because those tools do not enforce the Same-Origin Policy. Only browsers enforce CORS. Always test with an actual browser.

6. **Setting allowedOrigins to "*" in production.** This allows any website to call your API. Always list specific, trusted origins in production.

---

## Best Practices

1. **Always configure CORS in SecurityFilterChain when using Spring Security.** This ensures preflight requests are handled before authentication.

2. **Use externalized configuration for origins.** Put allowed origins in application properties so you can change them per environment without code changes.

3. **List specific origins instead of using wildcards.** In production, only allow your actual frontend domains.

4. **Set a reasonable maxAge.** A value of 3600 (1 hour) reduces unnecessary preflight requests. Do not set it too high because you cannot revoke cached preflights.

5. **Include only the HTTP methods you actually use.** Do not allow DELETE if your API only uses GET and POST.

6. **Test CORS from the browser, not from curl.** Curl does not enforce CORS. Use a real browser or a simple HTML test page.

---

## Quick Summary

CORS (Cross-Origin Resource Sharing) is a browser security mechanism that controls which origins can access your API. Browsers enforce the Same-Origin Policy, which blocks requests between different origins (different protocol, host, or port). For complex requests, the browser sends a preflight OPTIONS request to check if the cross-origin request is allowed. In Spring Boot, you can configure CORS at the controller level with @CrossOrigin or globally with WebMvcConfigurer. When using Spring Security, you must configure CORS through CorsConfigurationSource in the SecurityFilterChain to ensure preflight requests are handled before authentication. Never use wildcard origins in production, and always externalize your CORS configuration for different environments.

---

## Key Points

- Same-Origin Policy blocks requests between different origins (protocol + host + port).
- CORS lets the server specify which origins are allowed to make cross-origin requests.
- Preflight OPTIONS requests are sent for complex requests (POST with JSON, custom headers).
- @CrossOrigin provides controller-level or method-level CORS configuration.
- WebMvcConfigurer provides global CORS configuration.
- When using Spring Security, configure CORS in SecurityFilterChain with CorsConfigurationSource.
- `allowedOrigins("*")` cannot be used with `allowCredentials(true)`.
- Always test CORS from a browser, not from curl or Postman.
- Externalize allowed origins in application properties for different environments.

---

## Practice Questions

1. What three parts make up an origin, and when do two URLs have the same origin?

2. What is a preflight request, and when does the browser send one?

3. Why is it not enough to configure CORS only in WebMvcConfigurer when using Spring Security?

4. Why can you not use `allowedOrigins("*")` together with `allowCredentials(true)`?

5. A developer tests their API with Postman and everything works. When they try the same request from their React app, they get a CORS error. Why?

---

## Exercises

### Exercise 1: Configure CORS for Multiple Frontends

Create a Spring Boot application with two sets of CORS rules:
- `/api/public/**` allows requests from any origin but only GET requests.
- `/api/private/**` allows requests only from `http://localhost:3000` and `http://localhost:5173`, all HTTP methods, and credentials.

Test both configurations using curl to simulate preflight requests.

### Exercise 2: Environment-Specific CORS

Set up a Spring Boot project with two profiles: `dev` and `prod`. In the dev profile, allow `http://localhost:3000`. In the prod profile, allow `https://myapp.com`. Verify that switching profiles changes the CORS behavior.

### Exercise 3: Debug a CORS Problem

Create a Spring Boot API with Spring Security enabled. Intentionally configure CORS only in WebMvcConfigurer (not in SecurityFilterChain). Observe the CORS error from a browser. Then fix it by adding CORS to the security configuration.

---

## What Is Next?

Your API is now accessible from frontend applications running on different origins. But users often need to do more than send JSON data. They need to upload files like profile pictures, documents, and spreadsheets. In Chapter 21, you will learn how to handle file uploads and downloads in Spring Boot, including validating file types, generating unique filenames, and serving files back to users.
