# Chapter 27: Logging and Observability

## What You Will Learn

- What to log and, critically, what never to log
- How to use log levels (DEBUG, INFO, WARN, ERROR) effectively
- How structured logging (JSON) makes logs searchable and actionable
- How correlation IDs let you trace a request across multiple services
- The difference between metrics, logs, and traces
- How to replace println debugging with proper logging
- How log rotation prevents disk space disasters
- How centralized logging (ELK stack) works
- How to set up alerting so errors wake the right people

## Why This Chapter Matters

Your application is running in production. A customer reports that their order
failed, but they cannot tell you when or what they ordered. You open the server
and find a single file called `app.log` that is 47 gigabytes. You search for
"error" and get 200,000 results. None of them include the customer ID.

This scenario is painfully common. Good logging is the difference between
diagnosing a production issue in five minutes and spending an entire weekend
guessing. Observability goes further: it means your system can tell you what is
wrong before your customers do.

Yet most developers learn logging by accident. They scatter `System.out.println`
or `print()` calls throughout their code, leave them in production, and wonder
why their logs are useless. This chapter teaches you to treat logging as a
first-class engineering concern.

---

## Section 1: Why println Debugging Fails in Production

Every developer starts here:

### BEFORE: println Debugging

```java
// Java - The "I'll just print it" approach
public class OrderService {
    public void processOrder(Order order) {
        System.out.println("Processing order");
        System.out.println("Order: " + order);

        try {
            validateOrder(order);
            System.out.println("Validation passed");

            chargePayment(order);
            System.out.println("Payment charged");

            sendConfirmation(order);
            System.out.println("Confirmation sent");

        } catch (Exception e) {
            System.out.println("Something went wrong: " + e);
        }
    }
}
```

```python
# Python - The "I'll just print it" approach
class OrderService:
    def process_order(self, order):
        print("Processing order")
        print(f"Order: {order}")

        try:
            self.validate_order(order)
            print("Validation passed")

            self.charge_payment(order)
            print("Payment charged")

            self.send_confirmation(order)
            print("Confirmation sent")

        except Exception as e:
            print(f"Something went wrong: {e}")
```

This produces output like:

```
Processing order
Order: Order@3f2a1c
Validation passed
Payment charged
Something went wrong: java.lang.NullPointerException
Processing order
Order: Order@7b4a2d
Validation passed
Payment charged
Confirmation sent
```

Problems with this approach:

```
+----------------------------------------------------------+
|  Why println Fails in Production                         |
+----------------------------------------------------------+
|                                                          |
|  1. No timestamps   - When did the error happen?         |
|  2. No severity     - Is this fatal or informational?    |
|  3. No context      - Which user? Which order?           |
|  4. No filtering    - Cannot turn off noisy messages     |
|  5. No structure    - Cannot search or aggregate         |
|  6. Goes to stdout  - Lost when process restarts         |
|  7. Not thread-safe - Messages interleave randomly       |
|  8. No rotation     - File grows until disk is full      |
|                                                          |
+----------------------------------------------------------+
```

### AFTER: Proper Logging

```java
// Java - Professional logging with SLF4J + Logback
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class OrderService {
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);

    public void processOrder(Order order) {
        MDC.put("orderId", order.getId());
        MDC.put("customerId", order.getCustomerId());

        log.info("Starting order processing");

        try {
            validateOrder(order);
            log.debug("Order validation passed");

            chargePayment(order);
            log.info("Payment charged successfully, amount={}",
                     order.getTotal());

            sendConfirmation(order);
            log.info("Order processing completed");

        } catch (PaymentDeclinedException e) {
            log.warn("Payment declined for order, reason={}",
                     e.getReason());
            throw e;

        } catch (Exception e) {
            log.error("Unexpected error processing order", e);
            throw new OrderProcessingException(
                "Failed to process order " + order.getId(), e);

        } finally {
            MDC.clear();
        }
    }
}
```

```python
# Python - Professional logging
import logging
import structlog

log = structlog.get_logger()

class OrderService:
    def process_order(self, order):
        logger = log.bind(
            order_id=order.id,
            customer_id=order.customer_id
        )

        logger.info("starting_order_processing")

        try:
            self.validate_order(order)
            logger.debug("order_validation_passed")

            self.charge_payment(order)
            logger.info("payment_charged",
                       amount=order.total)

            self.send_confirmation(order)
            logger.info("order_processing_completed")

        except PaymentDeclinedError as e:
            logger.warning("payment_declined",
                          reason=str(e))
            raise

        except Exception as e:
            logger.error("unexpected_error_processing_order",
                        error=str(e),
                        exc_info=True)
            raise OrderProcessingError(
                f"Failed to process order {order.id}"
            ) from e
```

This produces:

```json
{
  "timestamp": "2024-01-15T10:23:45.123Z",
  "level": "INFO",
  "logger": "com.shop.OrderService",
  "message": "Payment charged successfully",
  "orderId": "ORD-12345",
  "customerId": "CUST-789",
  "amount": 49.99,
  "thread": "http-nio-8080-exec-3"
}
```

Now you can answer: What happened? When? To whom? How bad was it?

---

## Section 2: What to Log and What NEVER to Log

### What to Log

```
+------------------------------------------------------------------+
|  LOG THIS                          |  EXAMPLE                     |
+------------------------------------+------------------------------+
|  Request received                  |  "Received POST /orders"     |
|  Request completed (with timing)   |  "Completed in 234ms"        |
|  Business events                   |  "Order placed"              |
|  State transitions                 |  "Order PENDING -> SHIPPED"  |
|  Integration calls (start/end)     |  "Calling payment gateway"   |
|  Authentication events             |  "User logged in"            |
|  Errors and exceptions             |  Full stack trace             |
|  Configuration at startup          |  "DB pool size: 10"          |
|  Decisions with reasons            |  "Retry #2, backoff 400ms"   |
+------------------------------------+------------------------------+
```

### What NEVER to Log

This is not optional. Logging sensitive data can violate laws (GDPR, HIPAA,
PCI-DSS) and create security vulnerabilities.

```
+------------------------------------------------------------------+
|  NEVER LOG THIS                    |  WHY                         |
+------------------------------------+------------------------------+
|  Passwords                         |  Obvious security risk       |
|  API keys / tokens                 |  Attacker reads logs = pwned |
|  Credit card numbers               |  PCI-DSS violation           |
|  Social security numbers           |  Identity theft risk         |
|  Session IDs / JWTs                |  Session hijacking           |
|  Full request bodies (user data)   |  May contain PII             |
|  Database connection strings       |  Contains credentials        |
|  Encryption keys                   |  Defeats encryption          |
|  Health information                |  HIPAA violation             |
|  Personal email / phone            |  GDPR / privacy violation    |
+------------------------------------------------------------------+
```

### BEFORE: Logging Sensitive Data (DANGEROUS)

```java
// Java - NEVER DO THIS
public class AuthService {
    public User login(String username, String password) {
        // SECURITY VULNERABILITY: password in logs!
        log.info("Login attempt: user={}, password={}", username, password);

        User user = userRepository.findByUsername(username);

        // SECURITY VULNERABILITY: token in logs!
        String token = generateToken(user);
        log.info("Generated token: {}", token);

        // SECURITY VULNERABILITY: full user object may contain PII
        log.debug("User details: {}", user);

        return user;
    }
}
```

```python
# Python - NEVER DO THIS
class AuthService:
    def login(self, username, password):
        # SECURITY VULNERABILITY: password in logs!
        logger.info(f"Login attempt: user={username}, password={password}")

        user = self.user_repository.find_by_username(username)

        # SECURITY VULNERABILITY: token in logs!
        token = self.generate_token(user)
        logger.info(f"Generated token: {token}")

        # SECURITY VULNERABILITY: full user object may contain PII
        logger.debug(f"User details: {user}")

        return user
```

### AFTER: Safe Logging

```java
// Java - Safe logging practices
public class AuthService {
    public User login(String username, String password) {
        // Log the event, not the credentials
        log.info("Login attempt, username={}", username);

        User user = userRepository.findByUsername(username);
        if (user == null) {
            log.warn("Login failed: unknown username={}", username);
            throw new AuthenticationException("Invalid credentials");
        }

        if (!passwordEncoder.matches(password, user.getPasswordHash())) {
            log.warn("Login failed: invalid password for username={}",
                     username);
            throw new AuthenticationException("Invalid credentials");
        }

        String token = generateToken(user);
        // Log that a token was generated, not the token itself
        log.info("Login successful, username={}, tokenPrefix={}",
                 username, token.substring(0, 8) + "...");

        return user;
    }
}
```

```python
# Python - Safe logging practices
class AuthService:
    def login(self, username: str, password: str) -> User:
        # Log the event, not the credentials
        logger.info("login_attempt", username=username)

        user = self.user_repository.find_by_username(username)
        if user is None:
            logger.warning("login_failed_unknown_user",
                          username=username)
            raise AuthenticationError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            logger.warning("login_failed_invalid_password",
                          username=username)
            raise AuthenticationError("Invalid credentials")

        token = self.generate_token(user)
        # Log that a token was generated, not the token itself
        logger.info("login_successful",
                    username=username,
                    token_prefix=token[:8] + "...")

        return user
```

**Rule of thumb:** Before logging any variable, ask yourself: "If an attacker
read this log line, could they use this information to compromise the system or
a user?" If yes, do not log it.

---

## Section 3: Log Levels -- When to Use Each One

Log levels are not decoration. They are a filtering mechanism that lets you
control how much detail you see in different environments.

```
+---------------------------------------------------------------+
|  Log Level Pyramid                                            |
+---------------------------------------------------------------+
|                                                               |
|        /\          FATAL  - Application cannot continue       |
|       /  \         (Use sparingly: JVM out of memory,         |
|      /    \         unrecoverable startup failure)            |
|     /------\                                                  |
|    / ERROR  \      Something broke that should not have.      |
|   /   (Fix   \     An operation failed. Needs attention.      |
|  /   ASAP)    \    Example: Payment gateway unreachable.      |
| /--------------\                                              |
| |    WARN      |   Something unexpected but recoverable.      |
| |  (Investigate|   Example: Retry succeeded on attempt 3.     |
| |   soon)      |   Example: Deprecated API still in use.      |
| |--------------|                                              |
| |    INFO      |   Normal business events.                    |
| |  (Default    |   Example: Order placed, user logged in.     |
| |   in prod)   |   This is your production baseline.          |
| |--------------|                                              |
| |    DEBUG     |   Detailed technical information.             |
| |  (Dev/       |   Example: SQL queries, cache hits/misses.   |
| |   staging)   |   Too noisy for production normally.         |
| |--------------|                                              |
| |    TRACE     |   Extremely detailed: method entry/exit,     |
| |  (Rarely     |   variable values at each step.              |
| |   used)      |   Only for deep debugging sessions.          |
| |______________|                                              |
+---------------------------------------------------------------+
```

### Setting Log Levels by Environment

```java
// Java - logback.xml configuration
// Production: INFO and above
// <root level="INFO">

// Staging: DEBUG for your code, INFO for libraries
// <logger name="com.yourcompany" level="DEBUG" />
// <logger name="org.springframework" level="INFO" />
// <logger name="org.hibernate" level="WARN" />
```

```python
# Python - logging configuration
import logging

# Production
logging.basicConfig(level=logging.INFO)

# Development
logging.basicConfig(level=logging.DEBUG)

# Suppress noisy libraries
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
```

### Common Log Level Mistakes

```java
// WRONG: Using ERROR for expected business cases
log.error("User not found: {}", username);  // This is a WARN or INFO

// WRONG: Using INFO for debugging details
log.info("SQL query: {}", sql);  // This is DEBUG

// WRONG: Using DEBUG for critical failures
log.debug("Database connection failed", e);  // This is ERROR

// CORRECT usage:
log.info("User login successful, userId={}", userId);
log.warn("Payment retry attempt {}/3", attempt);
log.error("Database connection pool exhausted", e);
log.debug("Cache miss for key={}, fetching from DB", key);
```

---

## Section 4: Structured Logging

Traditional logs are strings. Structured logs are data.

### BEFORE: Unstructured Logging

```
2024-01-15 10:23:45 INFO Processing order #12345 for customer John Smith, total $49.99
2024-01-15 10:23:45 ERROR Failed to charge payment for order #12345: Connection timeout
```

Try searching these logs for "all failed payments over $100 in the last hour."
You would need complex regex, and it would break when someone changes the
message format.

### AFTER: Structured Logging (JSON)

```json
{
  "timestamp": "2024-01-15T10:23:45.123Z",
  "level": "INFO",
  "event": "order_processing_started",
  "orderId": "12345",
  "customerId": "CUST-789",
  "customerName": "John Smith",
  "total": 49.99,
  "currency": "USD",
  "service": "order-service",
  "host": "prod-web-03"
}
{
  "timestamp": "2024-01-15T10:23:46.456Z",
  "level": "ERROR",
  "event": "payment_charge_failed",
  "orderId": "12345",
  "customerId": "CUST-789",
  "total": 49.99,
  "error": "Connection timeout",
  "gateway": "stripe",
  "retryCount": 0,
  "service": "order-service",
  "host": "prod-web-03"
}
```

Now the query "all failed payments over $100" is trivial:

```
event:payment_charge_failed AND total:>100
```

### Setting Up Structured Logging

```java
// Java - Logback with JSON encoder (logback.xml)
// Add dependency: net.logstash.logback:logstash-logback-encoder

/*
<appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
        <includeMdcKeyName>orderId</includeMdcKeyName>
        <includeMdcKeyName>customerId</includeMdcKeyName>
        <includeMdcKeyName>correlationId</includeMdcKeyName>
    </encoder>
</appender>
*/

// In code, use MDC for context:
import org.slf4j.MDC;

public class OrderService {
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);

    public void processOrder(Order order) {
        MDC.put("orderId", order.getId());
        MDC.put("customerId", order.getCustomerId());

        log.info("Order processing started");
        // Output: {"timestamp":"...","level":"INFO",
        //          "message":"Order processing started",
        //          "orderId":"12345","customerId":"CUST-789"}
    }
}
```

```python
# Python - structlog for structured logging
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ]
)

log = structlog.get_logger()

class OrderService:
    def process_order(self, order):
        logger = log.bind(
            order_id=order.id,
            customer_id=order.customer_id
        )
        logger.info("order_processing_started", total=order.total)
        # Output: {"timestamp":"...","level":"info",
        #          "event":"order_processing_started",
        #          "order_id":"12345","customer_id":"CUST-789",
        #          "total":49.99}
```

---

## Section 5: Correlation IDs -- Tracing Requests Across Services

In a microservices architecture, a single user request may pass through five or
more services. Without a correlation ID, connecting the logs from each service
is nearly impossible.

```
+---------------------------------------------------------------+
|  Request Flow Without Correlation ID                          |
+---------------------------------------------------------------+
|                                                               |
|  API Gateway     Order Service     Payment Service    Email   |
|  ----------      -------------     ---------------    -----   |
|  "Request in"    "Processing"      "Charging card"    "Send"  |
|  "Request in"    "Processing"      "Charging card"    "Send"  |
|  "Request in"    "Validating"      "Refunding"        "Send"  |
|                                                               |
|  Which "Charging card" goes with which "Request in"?          |
|  IMPOSSIBLE TO TELL.                                          |
+---------------------------------------------------------------+

+---------------------------------------------------------------+
|  Request Flow WITH Correlation ID                             |
+---------------------------------------------------------------+
|                                                               |
|  API Gateway        Order Service        Payment Service      |
|  [corr=abc-123]     [corr=abc-123]       [corr=abc-123]      |
|  "Request in"  -->  "Processing"    -->  "Charging $49.99"    |
|                                                               |
|  [corr=def-456]     [corr=def-456]       [corr=def-456]      |
|  "Request in"  -->  "Processing"    -->  "Charging $29.99"    |
|                                                               |
|  Search for corr=abc-123 and get the COMPLETE story.          |
+---------------------------------------------------------------+
```

### Implementing Correlation IDs

```java
// Java - Servlet filter that creates/propagates correlation IDs
import javax.servlet.*;
import javax.servlet.http.*;
import org.slf4j.MDC;
import java.util.UUID;

public class CorrelationIdFilter implements Filter {

    private static final String CORRELATION_HEADER = "X-Correlation-ID";

    @Override
    public void doFilter(ServletRequest req, ServletResponse res,
                         FilterChain chain) throws Exception {
        HttpServletRequest request = (HttpServletRequest) req;
        HttpServletResponse response = (HttpServletResponse) res;

        // Use existing ID from upstream service, or generate new one
        String correlationId = request.getHeader(CORRELATION_HEADER);
        if (correlationId == null || correlationId.isBlank()) {
            correlationId = UUID.randomUUID().toString();
        }

        // Put it in MDC so every log message includes it automatically
        MDC.put("correlationId", correlationId);

        // Pass it downstream in the response
        response.setHeader(CORRELATION_HEADER, correlationId);

        try {
            chain.doFilter(req, res);
        } finally {
            MDC.clear();
        }
    }
}
```

```python
# Python - Middleware for correlation IDs (FastAPI example)
import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

correlation_id_var: ContextVar[str] = ContextVar("correlation_id",
                                                  default="")

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Use existing ID or generate a new one
        correlation_id = request.headers.get(
            "X-Correlation-ID",
            str(uuid.uuid4())
        )

        # Store in context variable
        correlation_id_var.set(correlation_id)

        # Bind to structlog so every log includes it
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id
        )

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id

        return response
```

When calling another service, always forward the correlation ID:

```java
// Java - Forwarding correlation ID to downstream services
public class PaymentClient {
    public PaymentResult charge(Order order) {
        String correlationId = MDC.get("correlationId");

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(paymentUrl + "/charge"))
            .header("X-Correlation-ID", correlationId)
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(toJson(order)))
            .build();

        return httpClient.send(request, ...);
    }
}
```

---

## Section 6: Metrics vs Logs vs Traces

These three tools are called the "three pillars of observability." They serve
different purposes and complement each other.

```
+---------------------------------------------------------------+
|  The Three Pillars of Observability                           |
+---------------------------------------------------------------+
|                                                               |
|  LOGS            METRICS          TRACES                      |
|  ----            -------          ------                      |
|  What happened   How much/many    Where time was spent        |
|                                                               |
|  Discrete        Aggregated       Distributed                 |
|  events          numbers          request flows               |
|                                                               |
|  "Order 123      "50 orders/min"  "Order 123 took 2.3s:      |
|   failed at       "p99 = 1.2s"     - API: 50ms               |
|   10:23:45        "error rate 2%"  - Validation: 20ms         |
|   because..."                      - DB query: 800ms          |
|                                     - Payment: 1400ms"        |
|                                                               |
|  High detail,    Low detail,      Medium detail,              |
|  high volume     low volume       medium volume               |
|                                                               |
|  grep / search   Dashboards /     Flame graphs /              |
|  (ELK, Splunk)   alerts           waterfall charts            |
|                  (Prometheus,     (Jaeger, Zipkin)             |
|                   Datadog)                                     |
+---------------------------------------------------------------+
```

### When to Use Each

- **Logs**: "Why did order 12345 fail?" -- You need the specific details.
- **Metrics**: "Are we healthy right now?" -- You need aggregated numbers.
- **Traces**: "Why is the checkout page slow?" -- You need to see where time
  is spent across services.

### Basic Metrics Example

```java
// Java - Micrometer metrics (works with Prometheus, Datadog, etc.)
import io.micrometer.core.instrument.*;

public class OrderService {
    private final Counter ordersPlaced;
    private final Counter ordersFailed;
    private final Timer orderProcessingTime;

    public OrderService(MeterRegistry registry) {
        this.ordersPlaced = Counter.builder("orders.placed")
            .description("Total orders placed")
            .register(registry);

        this.ordersFailed = Counter.builder("orders.failed")
            .description("Total failed orders")
            .tag("reason", "unknown")
            .register(registry);

        this.orderProcessingTime = Timer.builder("orders.processing.time")
            .description("Time to process an order")
            .register(registry);
    }

    public void processOrder(Order order) {
        orderProcessingTime.record(() -> {
            try {
                doProcessOrder(order);
                ordersPlaced.increment();
            } catch (Exception e) {
                ordersFailed.increment();
                throw e;
            }
        });
    }
}
```

```python
# Python - Prometheus metrics
from prometheus_client import Counter, Histogram

orders_placed = Counter(
    "orders_placed_total",
    "Total number of orders placed"
)
orders_failed = Counter(
    "orders_failed_total",
    "Total number of failed orders",
    ["reason"]
)
order_processing_seconds = Histogram(
    "order_processing_seconds",
    "Time spent processing orders"
)

class OrderService:
    @order_processing_seconds.time()
    def process_order(self, order):
        try:
            self._do_process_order(order)
            orders_placed.inc()
        except PaymentError as e:
            orders_failed.labels(reason="payment").inc()
            raise
        except Exception as e:
            orders_failed.labels(reason="unknown").inc()
            raise
```

---

## Section 7: Log Rotation -- Preventing Disk Disasters

Without log rotation, your log files grow until the disk fills up. When the
disk is full, your application crashes. This is not a theoretical concern; it
happens regularly.

```
+---------------------------------------------------------------+
|  Log Rotation Strategy                                        |
+---------------------------------------------------------------+
|                                                               |
|  app.log  (current, max 100MB)                               |
|    |                                                          |
|    | When full, rotate:                                       |
|    v                                                          |
|  app.2024-01-15.log.gz  (compressed, ~10MB)                  |
|  app.2024-01-14.log.gz                                       |
|  app.2024-01-13.log.gz                                       |
|  ...                                                         |
|  app.2024-01-01.log.gz                                       |
|    |                                                          |
|    | After 30 days, auto-delete                               |
|    v                                                          |
|  (deleted)                                                    |
|                                                               |
+---------------------------------------------------------------+
```

### Java - Logback Rolling File Configuration

```xml
<!-- logback.xml -->
<appender name="FILE"
          class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>logs/app.log</file>

    <rollingPolicy
        class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
        <!-- Daily rotation -->
        <fileNamePattern>
            logs/app.%d{yyyy-MM-dd}.%i.log.gz
        </fileNamePattern>
        <!-- Each file max 100MB -->
        <maxFileSize>100MB</maxFileSize>
        <!-- Keep 30 days of history -->
        <maxHistory>30</maxHistory>
        <!-- Total max 5GB -->
        <totalSizeCap>5GB</totalSizeCap>
    </rollingPolicy>

    <encoder class="net.logstash.logback.encoder.LogstashEncoder" />
</appender>
```

### Python - Rotating File Handler

```python
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Size-based rotation
handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=100 * 1024 * 1024,  # 100MB
    backupCount=30               # Keep 30 old files
)

# Time-based rotation (daily)
handler = TimedRotatingFileHandler(
    "logs/app.log",
    when="midnight",
    interval=1,
    backupCount=30
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
```

---

## Section 8: Centralized Logging with the ELK Stack

When you have 20 servers, you cannot SSH into each one to read log files. You
need centralized logging.

```
+---------------------------------------------------------------+
|  ELK Stack Architecture                                       |
+---------------------------------------------------------------+
|                                                               |
|  Server 1 ----\                                               |
|  (app.log)     \                                              |
|                 \    +-----------+    +---------------+        |
|  Server 2 ------+--> | Logstash  |--> | Elasticsearch |       |
|  (app.log)      |    | (process  |    | (store and    |       |
|                 /    |  & parse) |    |  index)       |       |
|  Server 3 ----/     +-----------+    +-------+-------+        |
|  (app.log)                                   |                |
|                                       +------+------+        |
|                                       |   Kibana    |        |
|                                       | (visualize  |        |
|                                       |  & search)  |        |
|                                       +-------------+        |
|                                                               |
|  Modern alternative: Filebeat (lightweight shipper)           |
|  Server -> Filebeat -> Elasticsearch -> Kibana                |
+---------------------------------------------------------------+
```

**Elasticsearch** stores and indexes logs for fast searching.
**Logstash** (or Filebeat) ships logs from your servers to Elasticsearch.
**Kibana** provides a web UI for searching and visualizing logs.

Modern alternatives include:
- **Grafana Loki** (lightweight, indexes labels not content)
- **Datadog** (managed service)
- **AWS CloudWatch** (if on AWS)
- **Google Cloud Logging** (if on GCP)

---

## Section 9: Alerting on Errors

Logs are useless if nobody reads them. Alerting bridges the gap between
"something went wrong" and "someone knows about it."

### What to Alert On

```
+---------------------------------------------------------------+
|  Alert Severity Guide                                         |
+---------------------------------------------------------------+
|                                                               |
|  PAGE (wake someone up):                                      |
|    - Error rate > 5% for 5 minutes                            |
|    - Response time p99 > 5 seconds for 10 minutes             |
|    - Health check failing on 2+ servers                       |
|    - Zero orders processed in 30 minutes (during business     |
|      hours)                                                   |
|    - Database connection pool exhausted                       |
|                                                               |
|  TICKET (fix during business hours):                          |
|    - Error rate > 1% for 15 minutes                           |
|    - Disk usage > 80%                                         |
|    - Deprecated API calls detected                            |
|    - Certificate expiring within 30 days                      |
|                                                               |
|  LOG ONLY (review periodically):                              |
|    - Individual request failures (retried successfully)       |
|    - Cache miss rates                                         |
|    - Slow queries under threshold                             |
|                                                               |
+---------------------------------------------------------------+
```

### Alert Fatigue

The biggest risk with alerting is alert fatigue. If your team gets 50 alerts a
day and most are false positives, they will start ignoring all alerts --
including the real ones.

Rules for healthy alerting:
1. Every alert must be actionable. If nobody needs to do anything, it is not an
   alert.
2. Every alert should have a runbook. "What do I do when I get this alert?"
3. Review and tune alerts monthly. Delete alerts nobody acts on.
4. Use escalation policies. If the primary on-call does not acknowledge in 15
   minutes, escalate.

---

## Section 10: Putting It All Together -- A Real-World Logging Setup

Here is a complete example showing how all these concepts work together in a
production-ready service.

```java
// Java - Complete production logging setup
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import io.micrometer.core.instrument.*;

public class OrderService {
    private static final Logger log =
        LoggerFactory.getLogger(OrderService.class);

    private final Timer processingTimer;
    private final Counter successCounter;
    private final Counter failureCounter;

    public OrderService(MeterRegistry metrics) {
        this.processingTimer = Timer.builder("order.processing.duration")
            .description("Order processing duration")
            .register(metrics);
        this.successCounter = Counter.builder("order.processed")
            .tag("result", "success")
            .register(metrics);
        this.failureCounter = Counter.builder("order.processed")
            .tag("result", "failure")
            .register(metrics);
    }

    public OrderResult processOrder(Order order) {
        // Structured context for all log messages in this operation
        MDC.put("orderId", order.getId());
        MDC.put("customerId", order.getCustomerId());
        MDC.put("orderTotal", String.valueOf(order.getTotal()));

        long startTime = System.currentTimeMillis();
        log.info("Order processing started");

        try {
            // Step 1: Validate
            log.debug("Validating order, itemCount={}",
                      order.getItems().size());
            validateOrder(order);

            // Step 2: Calculate price
            BigDecimal finalPrice = calculatePrice(order);
            log.info("Price calculated, originalTotal={}, finalTotal={}, " +
                     "discountApplied={}",
                     order.getTotal(), finalPrice,
                     !finalPrice.equals(order.getTotal()));

            // Step 3: Charge payment
            log.info("Initiating payment charge");
            PaymentResult payment = chargePayment(order, finalPrice);
            log.info("Payment completed, transactionId={}, gateway={}",
                     payment.getTransactionId(), payment.getGateway());

            // Step 4: Send confirmation
            sendConfirmation(order, payment);

            // Record metrics
            long duration = System.currentTimeMillis() - startTime;
            processingTimer.record(duration, TimeUnit.MILLISECONDS);
            successCounter.increment();

            log.info("Order processing completed, durationMs={}", duration);

            return OrderResult.success(payment.getTransactionId());

        } catch (ValidationException e) {
            failureCounter.increment();
            log.warn("Order validation failed, reason={}", e.getMessage());
            return OrderResult.failure("VALIDATION_ERROR", e.getMessage());

        } catch (PaymentDeclinedException e) {
            failureCounter.increment();
            log.warn("Payment declined, reason={}, gateway={}",
                     e.getReason(), e.getGateway());
            return OrderResult.failure("PAYMENT_DECLINED", e.getReason());

        } catch (Exception e) {
            failureCounter.increment();
            log.error("Unexpected error processing order", e);
            return OrderResult.failure("INTERNAL_ERROR",
                                       "An unexpected error occurred");
        } finally {
            MDC.clear();
        }
    }
}
```

```python
# Python - Complete production logging setup
import time
import structlog
from prometheus_client import Counter, Histogram

log = structlog.get_logger()

processing_duration = Histogram(
    "order_processing_duration_seconds",
    "Order processing duration"
)
orders_processed = Counter(
    "orders_processed_total",
    "Orders processed",
    ["result"]
)

class OrderService:
    def process_order(self, order) -> OrderResult:
        logger = log.bind(
            order_id=order.id,
            customer_id=order.customer_id,
            order_total=float(order.total)
        )

        start_time = time.monotonic()
        logger.info("order_processing_started")

        try:
            # Step 1: Validate
            logger.debug("validating_order",
                        item_count=len(order.items))
            self.validate_order(order)

            # Step 2: Calculate price
            final_price = self.calculate_price(order)
            logger.info("price_calculated",
                       original_total=float(order.total),
                       final_total=float(final_price),
                       discount_applied=final_price != order.total)

            # Step 3: Charge payment
            logger.info("initiating_payment_charge")
            payment = self.charge_payment(order, final_price)
            logger.info("payment_completed",
                       transaction_id=payment.transaction_id,
                       gateway=payment.gateway)

            # Step 4: Send confirmation
            self.send_confirmation(order, payment)

            # Record metrics
            duration = time.monotonic() - start_time
            processing_duration.observe(duration)
            orders_processed.labels(result="success").inc()

            logger.info("order_processing_completed",
                       duration_seconds=round(duration, 3))

            return OrderResult.success(payment.transaction_id)

        except ValidationError as e:
            orders_processed.labels(result="failure").inc()
            logger.warning("order_validation_failed", reason=str(e))
            return OrderResult.failure("VALIDATION_ERROR", str(e))

        except PaymentDeclinedError as e:
            orders_processed.labels(result="failure").inc()
            logger.warning("payment_declined",
                          reason=e.reason, gateway=e.gateway)
            return OrderResult.failure("PAYMENT_DECLINED", e.reason)

        except Exception as e:
            orders_processed.labels(result="failure").inc()
            logger.error("unexpected_error_processing_order",
                        error=str(e), exc_info=True)
            return OrderResult.failure("INTERNAL_ERROR",
                                       "An unexpected error occurred")
```

---

## Common Mistakes

1. **Logging sensitive data.** Passwords, tokens, credit card numbers, and PII
   must never appear in logs. This is a security vulnerability and often a legal
   violation.

2. **Using the wrong log level.** Logging expected business events (like "user
   not found") as ERROR creates alert fatigue. Save ERROR for things that
   genuinely need developer attention.

3. **Logging without context.** A message that says "Error occurred" is useless.
   Always include what was being attempted, for whom, and with what parameters
   (excluding sensitive data).

4. **Not using structured logging.** Plain text logs are nearly impossible to
   search and aggregate at scale. Switching to JSON structured logging is one of
   the highest-value improvements you can make.

5. **Forgetting log rotation.** Logs that grow without bound will eventually
   fill the disk and crash your application.

6. **Logging too much in production.** Setting DEBUG level in production creates
   enormous volumes of data, slows the application, and makes it harder to find
   important messages.

7. **No correlation IDs.** Without a way to trace a request across services,
   debugging distributed systems is guesswork.

8. **Alert fatigue.** Too many alerts, or alerts that are not actionable, teach
   the team to ignore alerts entirely.

---

## Best Practices

1. **Use a logging framework, never println/print.** Logging frameworks give you
   levels, formatting, rotation, and output control.

2. **Always include correlation IDs.** Generate one at the entry point and
   propagate it through every service call.

3. **Log at the right level.** INFO for business events, WARN for recoverable
   issues, ERROR for failures needing attention, DEBUG for development details.

4. **Use structured logging from day one.** It is much harder to retrofit later.

5. **Set up centralized logging early.** Even a simple ELK or Loki setup saves
   hours of debugging.

6. **Create actionable alerts.** Every alert should have a runbook and a clear
   owner.

7. **Review what you log.** Periodically audit log statements to ensure no
   sensitive data has crept in.

8. **Log the "why," not just the "what."** Instead of "Retrying request," log
   "Retrying request, attempt 2/3, previous failure: connection timeout,
   backoff: 400ms."

---

## Quick Summary

Logging and observability transform your application from a black box into a
system you can understand, debug, and operate with confidence. Replace println
debugging with structured logging using proper log levels. Never log sensitive
data. Use correlation IDs to trace requests across services. Combine logs with
metrics and traces for complete observability. Set up centralized logging and
meaningful alerts so problems are found before customers report them.

---

## Key Points

- **Structured logging** (JSON) makes logs searchable and machine-readable.
- **Log levels** (DEBUG, INFO, WARN, ERROR) are a filtering mechanism, not
  decoration. Use them consistently.
- **Never log sensitive data:** passwords, tokens, credit cards, PII.
- **Correlation IDs** let you trace a single request across multiple services.
- **Metrics** answer "how much," **logs** answer "what happened," **traces**
  answer "where did time go."
- **Log rotation** prevents disk space disasters.
- **Centralized logging** (ELK, Loki, Datadog) is essential for multi-server
  deployments.
- **Alerts must be actionable.** If nobody needs to respond, it should not be
  an alert.

---

## Practice Questions

1. You are debugging a production issue where a customer's order failed. Your
   logs show the error, but you cannot determine which of the 50 concurrent
   requests it belongs to. What concept would solve this problem, and how would
   you implement it?

2. A junior developer adds `log.info("User password: " + password)` to the
   authentication service for debugging. Explain why this is dangerous and what
   they should log instead.

3. Your team receives 80 alerts per day and has started ignoring them. Three
   real incidents were missed last month. What steps would you take to fix the
   alerting system?

4. Explain the difference between metrics, logs, and traces. Give a specific
   scenario where each one is the best tool for the job.

5. Your production log file is 200GB and the disk is 95% full. The application
   is at risk of crashing. What immediate steps do you take, and what long-term
   solution do you implement?

---

## Exercises

### Exercise 1: Add Proper Logging to a Service

Take the following println-based code and refactor it to use proper logging
with appropriate levels, structured context, and safe practices.

```java
public class UserService {
    public User register(String email, String password, String name) {
        System.out.println("Registering user: " + email +
                           ", password: " + password);
        try {
            User user = new User(email, password, name);
            database.save(user);
            System.out.println("User saved: " + user);
            emailService.sendWelcome(email);
            System.out.println("Welcome email sent");
            return user;
        } catch (Exception e) {
            System.out.println("Registration failed: " + e);
            return null;
        }
    }
}
```

### Exercise 2: Design a Logging Strategy

You are building an e-commerce platform with the following services: API
Gateway, User Service, Product Service, Order Service, Payment Service, and
Notification Service. Design a complete logging strategy covering: what each
service should log, what log levels to use, how to implement correlation IDs,
what metrics to track, and what alerts to set up.

### Exercise 3: Set Up Structured Logging

Create a small application (in Java or Python) that:
1. Uses structured JSON logging
2. Includes a correlation ID middleware/filter
3. Logs request start and completion with timing
4. Demonstrates proper use of all log levels
5. Includes at least two custom metrics (counter, histogram)

---

## What Is Next?

Now that you understand how to make your systems observable, the next chapter
tackles a concept every developer encounters but few handle well: **Technical
Debt**. You will learn how shortcuts taken today become interest payments
tomorrow, how to measure and communicate debt, and when taking on debt is
actually the right decision.
