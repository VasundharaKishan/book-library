# Chapter 27: Circuit Breaker Pattern

## What You Will Learn

- What the Circuit Breaker pattern is and how it prevents cascading failures
- How the three states work: Closed, Open, and Half-Open
- How to implement a Circuit Breaker in Java using Resilience4j
- How to build a custom Circuit Breaker in Python
- How to design fallback strategies for degraded service
- How Circuit Breaker compares to simple retry logic
- Real-world application in microservice communication

## Why This Chapter Matters

In a microservice architecture, your service depends on other services. Your order service calls the payment service, which calls the fraud detection service, which calls an external credit check API. When that external API goes down, the fraud service starts timing out. The payment service is waiting for the fraud service. The order service is waiting for the payment service. Every request piles up, threads exhaust, and your entire system grinds to a halt -- even though your order service itself is perfectly healthy.

This is a cascading failure, and it is one of the most dangerous problems in distributed systems. The Circuit Breaker pattern prevents it by detecting when a downstream service is failing and short-circuiting requests to it. Instead of waiting 30 seconds for a timeout, the Circuit Breaker fails immediately and returns a fallback response. This protects your service from being dragged down by someone else's outage.

The name comes from electrical circuit breakers. When a short circuit occurs, the breaker trips to prevent the wiring from catching fire. In software, when a service fails repeatedly, the circuit breaker trips to prevent your system from overloading.

---

## The Problem

### Before: No Circuit Breaker

```
Order Service --> Payment Service --> Fraud Service --> External API (DOWN)
     |                  |                  |
     |  Waiting...      |  Waiting...      |  Timeout: 30s
     |  Waiting...      |  Waiting...      |
     |  Waiting...      |  Waiting...      |
     |                  |                  |
     v                  v                  v
  Thread pool          Thread pool        Connection pool
  exhausted            exhausted          exhausted

  Result: ALL services are DOWN because ONE external API is down
```

```java
// Without circuit breaker: every request waits for timeout
@Service
public class PaymentService {

    private final RestTemplate restTemplate;

    public PaymentResult processPayment(PaymentRequest request) {
        try {
            // This call hangs for 30 seconds when fraud service is down
            FraudCheckResult fraudCheck = restTemplate.postForObject(
                "http://fraud-service/check",
                request,
                FraudCheckResult.class
            );
            // Process payment...
            return new PaymentResult("SUCCESS");
        } catch (Exception e) {
            // After 30 seconds of waiting, we get here
            // But by then, 100 other requests are also waiting
            throw new PaymentException("Payment failed: " + e.getMessage());
        }
    }
}
```

**What happens:**
1. Request 1 waits 30 seconds for the fraud service -- timeout
2. Request 2 waits 30 seconds -- timeout
3. Requests 3-100 pile up, all waiting 30 seconds each
4. Thread pool exhausted -- order service stops responding
5. Services calling order service also start timing out
6. Entire system cascades into failure

---

## The Solution: Circuit Breaker

The Circuit Breaker monitors failures and prevents calls to a failing service.

```
                    +------------------+
            +------>|     CLOSED       |<------+
            |       | (Normal: calls   |       |
            |       |  pass through)   |       |
            |       +--------+---------+       |
            |                |                 |
            |     Failure threshold            |
            |     reached (e.g., 5             |
            |     failures in 10 calls)        |
            |                |                 |
            |                v                 |
            |       +------------------+       |
            |       |      OPEN        |       |
            |       | (Tripped: calls  |       |
            |       |  rejected fast)  |       |
            |       +--------+---------+       |
            |                |                 |
            |     Wait timeout expires         |
            |     (e.g., 60 seconds)           |  Success:
            |                |                 |  reset to
            |                v                 |  CLOSED
            |       +------------------+       |
            +-------+   HALF-OPEN      +-------+
              Fail  | (Testing: allow  |  Pass
                    |  a few calls     |
                    |  through)        |
                    +------------------+
```

### The Three States

```
+-------------+-----------------------------------------------+
| State       | Behavior                                      |
+-------------+-----------------------------------------------+
| CLOSED      | Normal operation. All calls pass through.     |
|             | Failures are counted. If failures exceed the   |
|             | threshold, transition to OPEN.                 |
+-------------+-----------------------------------------------+
| OPEN        | Circuit is tripped. All calls fail immediately |
|             | without reaching the downstream service.       |
|             | After a timeout period, transition to          |
|             | HALF-OPEN.                                     |
+-------------+-----------------------------------------------+
| HALF-OPEN   | Testing the waters. A limited number of calls  |
|             | are allowed through. If they succeed,          |
|             | transition to CLOSED. If they fail, transition |
|             | back to OPEN.                                  |
+-------------+-----------------------------------------------+
```

---

## Java Implementation: Resilience4j CircuitBreaker

Resilience4j is the standard Java library for resilience patterns. Here is how to use its Circuit Breaker.

### Step 1: Add Dependencies

```xml
<!-- Maven -->
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-circuitbreaker</artifactId>
    <version>2.1.0</version>
</dependency>
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-spring-boot3</artifactId>
    <version>2.1.0</version>
</dependency>
```

### Step 2: Configure the Circuit Breaker

```java
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;

import java.time.Duration;

public class CircuitBreakerSetup {

    public static CircuitBreaker createPaymentCircuitBreaker() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            // Percentage of failures to trip the breaker
            .failureRateThreshold(50)
            // Minimum number of calls before evaluating failure rate
            .minimumNumberOfCalls(5)
            // How long to wait in OPEN state before trying HALF-OPEN
            .waitDurationInOpenState(Duration.ofSeconds(30))
            // Number of calls allowed in HALF-OPEN state
            .permittedNumberOfCallsInHalfOpenState(3)
            // Use a sliding window to track call outcomes
            .slidingWindowType(
                CircuitBreakerConfig.SlidingWindowType.COUNT_BASED)
            .slidingWindowSize(10)
            .build();

        CircuitBreakerRegistry registry =
            CircuitBreakerRegistry.of(config);

        return registry.circuitBreaker("paymentService");
    }
}
```

### Step 3: Use the Circuit Breaker

```java
import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CallNotPermittedException;

import java.util.function.Supplier;

@Service
public class PaymentService {

    private final RestTemplate restTemplate;
    private final CircuitBreaker circuitBreaker;

    public PaymentService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
        this.circuitBreaker = CircuitBreakerSetup
            .createPaymentCircuitBreaker();
    }

    public PaymentResult processPayment(PaymentRequest request) {
        // Wrap the call with the circuit breaker
        Supplier<PaymentResult> decoratedSupplier =
            CircuitBreaker.decorateSupplier(circuitBreaker, () -> {
                FraudCheckResult fraudCheck = restTemplate.postForObject(
                    "http://fraud-service/check",
                    request,
                    FraudCheckResult.class
                );
                // Process payment logic...
                return new PaymentResult("SUCCESS", request.getAmount());
            });

        try {
            return decoratedSupplier.get();
        } catch (CallNotPermittedException e) {
            // Circuit is OPEN -- fail fast with fallback
            System.out.println("Circuit OPEN: returning fallback");
            return fallbackPayment(request);
        } catch (Exception e) {
            // Call was attempted but failed
            System.out.println("Call failed: " + e.getMessage());
            return fallbackPayment(request);
        }
    }

    private PaymentResult fallbackPayment(PaymentRequest request) {
        // Queue for later processing instead of failing completely
        System.out.println("Fallback: queueing payment for retry");
        return new PaymentResult("PENDING", request.getAmount());
    }
}
```

### Step 4: Spring Boot Annotation-Based Approach

```java
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.springframework.stereotype.Service;

@Service
public class FraudCheckService {

    private final RestTemplate restTemplate;

    public FraudCheckService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @CircuitBreaker(name = "fraudService",
                    fallbackMethod = "fraudCheckFallback")
    public FraudCheckResult checkFraud(PaymentRequest request) {
        return restTemplate.postForObject(
            "http://fraud-service/check",
            request,
            FraudCheckResult.class
        );
    }

    // Fallback method -- same signature plus Throwable
    private FraudCheckResult fraudCheckFallback(PaymentRequest request,
                                                 Throwable t) {
        System.out.println("Fraud check circuit open, using fallback");
        // Default to allowing the payment with manual review flag
        return new FraudCheckResult(false, "MANUAL_REVIEW_REQUIRED");
    }
}
```

### application.yml Configuration

```yaml
resilience4j:
  circuitbreaker:
    instances:
      fraudService:
        failureRateThreshold: 50
        minimumNumberOfCalls: 5
        waitDurationInOpenState: 30s
        permittedNumberOfCallsInHalfOpenState: 3
        slidingWindowSize: 10
        slidingWindowType: COUNT_BASED
        registerHealthIndicator: true
```

### Step 5: Monitoring Circuit Breaker State

```java
public class CircuitBreakerMonitor {

    public static void printStatus(CircuitBreaker circuitBreaker) {
        CircuitBreaker.Metrics metrics = circuitBreaker.getMetrics();

        System.out.println("=== Circuit Breaker Status ===");
        System.out.println("State: " + circuitBreaker.getState());
        System.out.println("Failure rate: " +
                           metrics.getFailureRate() + "%");
        System.out.println("Total calls: " +
                           metrics.getNumberOfBufferedCalls());
        System.out.println("Failed calls: " +
                           metrics.getNumberOfFailedCalls());
        System.out.println("Successful calls: " +
                           metrics.getNumberOfSuccessfulCalls());
        System.out.println("Not permitted: " +
                           metrics.getNumberOfNotPermittedCalls());
        System.out.println("==============================");
    }

    // Register event listeners
    public static void registerListeners(CircuitBreaker circuitBreaker) {
        circuitBreaker.getEventPublisher()
            .onStateTransition(event ->
                System.out.println("STATE CHANGE: " +
                    event.getStateTransition()))
            .onFailureRateExceeded(event ->
                System.out.println("FAILURE RATE EXCEEDED: " +
                    event.getFailureRate() + "%"))
            .onCallNotPermitted(event ->
                System.out.println("CALL NOT PERMITTED (circuit open)"));
    }
}
```

**Output during a failure scenario:**

```
Call 1: SUCCESS (fraud service responding)
Call 2: SUCCESS
Call 3: FAILED (fraud service error)
Call 4: FAILED
Call 5: FAILED

=== Circuit Breaker Status ===
State: CLOSED
Failure rate: 60.0%

STATE CHANGE: CLOSED -> OPEN
FAILURE RATE EXCEEDED: 60.0%

Call 6: CALL NOT PERMITTED (circuit open) -> Fallback
Call 7: CALL NOT PERMITTED (circuit open) -> Fallback
Call 8: CALL NOT PERMITTED (circuit open) -> Fallback

[30 seconds pass]

STATE CHANGE: OPEN -> HALF_OPEN

Call 9: SUCCESS (fraud service recovered)
Call 10: SUCCESS
Call 11: SUCCESS

STATE CHANGE: HALF_OPEN -> CLOSED

Call 12: SUCCESS (back to normal)
```

---

## Python Implementation: Custom Circuit Breaker

```python
import time
from enum import Enum
from threading import Lock
from datetime import datetime, timedelta
from typing import Callable, Optional, Any

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """
    Circuit Breaker implementation.

    States:
      CLOSED    -> Normal operation, tracking failures
      OPEN      -> Rejecting all calls, waiting for timeout
      HALF_OPEN -> Allowing limited calls to test recovery
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 3,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
        self._last_failure_time: Optional[datetime] = None
        self._lock = Lock()

        # Metrics
        self.total_calls = 0
        self.total_failures = 0
        self.total_rejected = 0

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_try_recovery():
                    self._transition_to(CircuitState.HALF_OPEN)
            return self._state

    def call(self, func: Callable, *args,
             fallback: Optional[Callable] = None, **kwargs) -> Any:
        """Execute a function through the circuit breaker."""

        self.total_calls += 1
        current_state = self.state

        if current_state == CircuitState.OPEN:
            self.total_rejected += 1
            print(f"  [{self.name}] OPEN: Call rejected")
            if fallback:
                return fallback(*args, **kwargs)
            raise CircuitBreakerOpenException(
                f"Circuit breaker '{self.name}' is OPEN")

        if current_state == CircuitState.HALF_OPEN:
            with self._lock:
                if self._half_open_calls >= self.half_open_max_calls:
                    self.total_rejected += 1
                    if fallback:
                        return fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker '{self.name}' HALF_OPEN limit reached")
                self._half_open_calls += 1

        # Attempt the call
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            if fallback:
                return fallback(*args, **kwargs)
            raise

    def _on_success(self):
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.half_open_max_calls:
                    self._transition_to(CircuitState.CLOSED)
            else:
                self._failure_count = max(0, self._failure_count - 1)

    def _on_failure(self):
        with self._lock:
            self.total_failures += 1
            self._failure_count += 1
            self._last_failure_time = datetime.now()

            if self._state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self._failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)

    def _should_try_recovery(self) -> bool:
        if self._last_failure_time is None:
            return False
        elapsed = (datetime.now() - self._last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def _transition_to(self, new_state: CircuitState):
        old_state = self._state
        self._state = new_state
        print(f"  [{self.name}] State: {old_state.value} -> {new_state.value}")

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
            self._success_count = 0

    def get_metrics(self) -> dict:
        return {
            "state": self._state.value,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_rejected": self.total_rejected,
            "failure_count": self._failure_count,
        }


class CircuitBreakerOpenException(Exception):
    pass
```

### Using the Python Circuit Breaker

```python
import random

# Simulate an unreliable external service
class FraudService:
    def __init__(self, failure_rate=0.0):
        self.failure_rate = failure_rate
        self.call_count = 0

    def check(self, transaction_id: str) -> dict:
        self.call_count += 1
        if random.random() < self.failure_rate:
            raise ConnectionError(
                f"Fraud service unavailable (call #{self.call_count})")
        return {"transaction_id": transaction_id, "fraud": False}


# Create circuit breaker and service
cb = CircuitBreaker(
    name="fraud-service",
    failure_threshold=3,
    recovery_timeout=5,   # Short for demo
    half_open_max_calls=2,
)

fraud_service = FraudService(failure_rate=0.0)  # Start healthy


def fallback_fraud_check(transaction_id: str) -> dict:
    """Fallback: allow transaction but flag for manual review."""
    return {"transaction_id": transaction_id,
            "fraud": False, "manual_review": True}


# Demo: normal operation
print("=== Phase 1: Normal operation ===")
for i in range(5):
    result = cb.call(fraud_service.check, f"TX-{i}",
                     fallback=fallback_fraud_check)
    print(f"  TX-{i}: {result}")

# Demo: service starts failing
print("\n=== Phase 2: Service failing ===")
fraud_service.failure_rate = 1.0  # 100% failure
for i in range(5, 12):
    result = cb.call(fraud_service.check, f"TX-{i}",
                     fallback=fallback_fraud_check)
    print(f"  TX-{i}: {result}")

# Demo: wait for recovery timeout
print("\n=== Phase 3: Waiting for recovery ===")
time.sleep(6)

# Demo: service recovers
print("\n=== Phase 4: Service recovered ===")
fraud_service.failure_rate = 0.0  # Healthy again
for i in range(12, 18):
    result = cb.call(fraud_service.check, f"TX-{i}",
                     fallback=fallback_fraud_check)
    print(f"  TX-{i}: {result}")

# Print metrics
print(f"\nMetrics: {cb.get_metrics()}")
```

**Output:**

```
=== Phase 1: Normal operation ===
  TX-0: {'transaction_id': 'TX-0', 'fraud': False}
  TX-1: {'transaction_id': 'TX-1', 'fraud': False}
  TX-2: {'transaction_id': 'TX-2', 'fraud': False}
  TX-3: {'transaction_id': 'TX-3', 'fraud': False}
  TX-4: {'transaction_id': 'TX-4', 'fraud': False}

=== Phase 2: Service failing ===
  TX-5: Call failed (ConnectionError)
  TX-6: Call failed (ConnectionError)
  TX-7: Call failed (ConnectionError)
  [fraud-service] State: CLOSED -> OPEN
  [fraud-service] OPEN: Call rejected
  TX-8: {'transaction_id': 'TX-8', 'fraud': False, 'manual_review': True}
  [fraud-service] OPEN: Call rejected
  TX-9: {'transaction_id': 'TX-9', 'fraud': False, 'manual_review': True}
  [fraud-service] OPEN: Call rejected
  TX-10: {'transaction_id': 'TX-10', 'fraud': False, 'manual_review': True}
  [fraud-service] OPEN: Call rejected
  TX-11: {'transaction_id': 'TX-11', 'fraud': False, 'manual_review': True}

=== Phase 3: Waiting for recovery ===

=== Phase 4: Service recovered ===
  [fraud-service] State: OPEN -> HALF_OPEN
  TX-12: {'transaction_id': 'TX-12', 'fraud': False}
  TX-13: {'transaction_id': 'TX-13', 'fraud': False}
  [fraud-service] State: HALF_OPEN -> CLOSED
  TX-14: {'transaction_id': 'TX-14', 'fraud': False}
  TX-15: {'transaction_id': 'TX-15', 'fraud': False}
  TX-16: {'transaction_id': 'TX-16', 'fraud': False}
  TX-17: {'transaction_id': 'TX-17', 'fraud': False}

Metrics: {'state': 'CLOSED', 'total_calls': 18, 'total_failures': 3, 'total_rejected': 4, 'failure_count': 0}
```

---

## Fallback Strategies

When the circuit is open, you need a fallback. Here are common strategies:

```
+-------------------+------------------------------------------+------------------+
| Strategy          | Description                              | Example          |
+-------------------+------------------------------------------+------------------+
| Default Value     | Return a safe default                    | Empty list,      |
|                   |                                          | cached value     |
+-------------------+------------------------------------------+------------------+
| Cached Response   | Return the last successful response      | Product prices   |
|                   |                                          | from cache       |
+-------------------+------------------------------------------+------------------+
| Queue for Retry   | Accept the request and process later     | Payment queued   |
|                   |                                          | for retry        |
+-------------------+------------------------------------------+------------------+
| Degraded Service  | Provide limited functionality             | Skip fraud check |
|                   |                                          | flag for review  |
+-------------------+------------------------------------------+------------------+
| Alternative       | Call a backup service                    | Secondary payment|
| Service           |                                          | provider         |
+-------------------+------------------------------------------+------------------+
| Fail Fast         | Return error immediately                 | "Service         |
|                   |                                          | unavailable"     |
+-------------------+------------------------------------------+------------------+
```

### Java: Multiple Fallback Strategies

```java
@Service
public class ProductService {

    private final RestTemplate restTemplate;
    private final CacheManager cacheManager;

    @CircuitBreaker(name = "recommendationService",
                    fallbackMethod = "recommendationFallback")
    public List<Product> getRecommendations(Long userId) {
        return restTemplate.exchange(
            "http://recommendation-service/users/" + userId,
            HttpMethod.GET,
            null,
            new ParameterizedTypeReference<List<Product>>() {}
        ).getBody();
    }

    // Fallback: return cached recommendations
    private List<Product> recommendationFallback(Long userId,
                                                  Throwable t) {
        System.out.println("Recommendation service down, using cache");

        // Strategy 1: Try cache
        Cache cache = cacheManager.getCache("recommendations");
        if (cache != null) {
            List<Product> cached = cache.get(userId, List.class);
            if (cached != null) {
                return cached;
            }
        }

        // Strategy 2: Return popular products as default
        return getPopularProducts();
    }

    private List<Product> getPopularProducts() {
        // Return a static or pre-computed list
        return List.of(
            new Product(1L, "Bestseller Book", new BigDecimal("19.99")),
            new Product(2L, "Popular Gadget", new BigDecimal("49.99"))
        );
    }
}
```

---

## Circuit Breaker vs Retry

These patterns are complementary, not alternatives:

```
+------------------+-------------------------------------+
| Retry            | Circuit Breaker                     |
+------------------+-------------------------------------+
| Tries again      | Stops trying                        |
| Hope it works    | Assumes it will not work            |
| Good for         | Good for sustained failures         |
| transient errors |                                     |
| Adds latency     | Reduces latency (fail fast)         |
| per retry        |                                     |
+------------------+-------------------------------------+

Best practice: Use BOTH together

  Request --> Retry (2-3 attempts) --> Circuit Breaker --> Service
                                            |
                                      If open: Fallback
```

### Java: Retry + Circuit Breaker Together

```java
@Service
public class PaymentGateway {

    // Retry wraps Circuit Breaker
    // First: retry up to 3 times
    // If retries exhaust: circuit breaker tracks the failure
    // If circuit opens: retries are skipped entirely

    @Retry(name = "paymentRetry", fallbackMethod = "paymentFallback")
    @CircuitBreaker(name = "paymentCircuit",
                    fallbackMethod = "paymentFallback")
    public PaymentResult charge(String cardToken, BigDecimal amount) {
        return restTemplate.postForObject(
            "http://payment-provider/charge",
            new ChargeRequest(cardToken, amount),
            PaymentResult.class
        );
    }

    private PaymentResult paymentFallback(String cardToken,
                                           BigDecimal amount,
                                           Throwable t) {
        return new PaymentResult("PENDING",
            "Payment queued for processing");
    }
}
```

---

## Real-World: Microservice Communication

```
                        API Gateway
                            |
              +-------------+-------------+
              |             |             |
         Order Service  Product Svc   User Service
              |
    +---------+---------+
    |         |         |
  Payment   Inventory  Shipping
  Service   Service    Service
    |
    |  [Circuit Breaker]
    |
  External
  Payment
  Provider
  (Stripe, PayPal)
```

Each service-to-service call should have its own Circuit Breaker with configuration tuned to the specific dependency:

```yaml
resilience4j:
  circuitbreaker:
    instances:
      # External payment provider: slow, unreliable
      paymentProvider:
        failureRateThreshold: 30
        waitDurationInOpenState: 60s
        slidingWindowSize: 20

      # Internal inventory service: fast, usually reliable
      inventoryService:
        failureRateThreshold: 50
        waitDurationInOpenState: 10s
        slidingWindowSize: 10

      # External shipping API: moderately reliable
      shippingApi:
        failureRateThreshold: 40
        waitDurationInOpenState: 30s
        slidingWindowSize: 15
```

---

## When to Use / When NOT to Use

### Use the Circuit Breaker Pattern When

- Your service depends on external or remote services
- Downstream services can fail or become slow
- You want to fail fast instead of waiting for timeouts
- You need to prevent cascading failures across services
- You want to provide degraded functionality during outages

### Do NOT Use the Circuit Breaker Pattern When

- Calls are to local, in-process components
- The downstream service is always available (embedded database)
- Failures are always transient and a simple retry suffices
- Your system is a monolith with no remote dependencies
- The cost of implementing fallbacks exceeds the benefit

---

## Common Mistakes

1. **Setting thresholds too high.** If the failure threshold is 100, your system makes 100 failing calls before the breaker trips. That is 100 slow requests. Start with lower thresholds (5-10) and tune.

2. **No fallback strategy.** A Circuit Breaker without a fallback just throws a different exception faster. Always provide meaningful fallback behavior.

3. **One Circuit Breaker for all services.** Each dependency should have its own Circuit Breaker with its own configuration. A failing payment service should not affect the recommendation Circuit Breaker.

4. **Ignoring the HALF-OPEN state.** The HALF-OPEN state is critical for recovery. Allow enough test calls to accurately determine if the service has recovered.

5. **Not monitoring Circuit Breaker state.** If you do not know when breakers are tripping, you cannot respond to outages. Export metrics and set up alerts.

---

## Best Practices

1. **Configure per dependency.** Different services have different failure characteristics. Tune thresholds, timeouts, and window sizes individually.

2. **Design meaningful fallbacks.** Cached data, default values, or queued processing are better than error messages.

3. **Combine with retry.** Use retry for transient errors and Circuit Breaker for sustained failures. Retry first, circuit break second.

4. **Monitor and alert.** Track the state of every Circuit Breaker. Alert when a breaker opens. Dashboard the failure rates.

5. **Test your fallbacks.** Inject failures in staging environments to verify that fallbacks work correctly.

6. **Log state transitions.** When a Circuit Breaker changes state, log it with details about why. This is invaluable for debugging.

---

## Quick Summary

The Circuit Breaker pattern prevents cascading failures by detecting when a downstream service is failing and short-circuiting requests to it. It operates in three states: Closed (normal, tracking failures), Open (tripped, rejecting calls fast), and Half-Open (testing if the service has recovered). In Java, Resilience4j provides production-ready Circuit Breakers with annotation-based configuration. In Python, you can implement the pattern with a custom class that tracks failures and manages state transitions. Always pair Circuit Breakers with fallback strategies and monitoring.

---

## Key Points

- Circuit Breaker prevents cascading failures in distributed systems
- Three states: Closed (normal), Open (rejecting), Half-Open (testing recovery)
- Fails fast instead of waiting for timeouts when a service is down
- Each dependency should have its own Circuit Breaker
- Fallback strategies: cached data, default values, queued processing, degraded service
- Combine with retry: retry handles transient errors, Circuit Breaker handles sustained failures
- Resilience4j is the standard Java library for Circuit Breaker
- Monitor and alert on Circuit Breaker state changes
- Test fallbacks by injecting failures in staging environments

---

## Practice Questions

1. Explain the three states of a Circuit Breaker and the conditions that trigger transitions between them.

2. What is the difference between a Circuit Breaker and a retry mechanism? When would you use both together, and in what order?

3. Your payment service depends on three external providers: Stripe, PayPal, and a bank API. How would you configure Circuit Breakers for each? What factors influence your threshold and timeout choices?

4. Describe three different fallback strategies and when you would use each one. Which strategy would you use for a payment service? For a recommendation service?

5. How would you test that your Circuit Breaker works correctly in a staging environment? What scenarios would you simulate?

---

## Exercises

### Exercise 1: Python Circuit Breaker with Decorator

Create a Python decorator `@circuit_breaker(threshold=5, timeout=30)` that wraps any function with Circuit Breaker logic. The decorator should support a `fallback` parameter. Test it with a simulated unreliable HTTP service.

### Exercise 2: Multi-Service Circuit Breakers

Build a Java service that calls three downstream services (user, product, order), each with its own Circuit Breaker configuration. Simulate failures in one service and verify that only its Circuit Breaker opens while the others continue normally.

### Exercise 3: Circuit Breaker Dashboard

Create a monitoring endpoint that exposes the state and metrics of all Circuit Breakers in your application. Include: state, failure rate, total calls, rejected calls, and last state transition time. Display this as a simple text-based dashboard.

---

## What Is Next?

The Circuit Breaker protects individual service calls from cascading failures. But what happens when a business operation spans multiple services and one of them fails? You cannot simply roll back a database transaction across microservices. The next chapter introduces the **Saga** pattern, which coordinates distributed transactions by defining a sequence of local transactions with compensating actions for rollback.
