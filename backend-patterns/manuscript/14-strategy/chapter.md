# Chapter 14: Strategy Pattern -- Swap Algorithms at Runtime

## What You Will Learn

- How to replace tangled `if/else` chains with interchangeable algorithm objects
- Implementing the Strategy pattern in Java and Python
- Using Spring's `@Qualifier` to inject strategies automatically
- Applying strategies to real-world problems like payment processing, compression, and authentication
- Deciding when Strategy is the right tool and when it is overkill

## Why This Chapter Matters

Every backend developer eventually writes code like this: a growing pile of `if/else` or `switch` statements that pick different behaviors based on some condition. Add a new payment method? Another branch. Support a new compression algorithm? Another branch. Every change risks breaking existing logic, and the method grows until nobody wants to touch it.

The Strategy pattern solves this by pulling each algorithm into its own object. You pick the one you need at runtime, plug it in, and the rest of your code never changes. It is one of the most practical patterns you will use in backend development.

---

## The Problem: The Growing If/Else Chain

Imagine you are building a pricing service. Different customer types get different discounts.

### The Painful Way (Before Strategy)

```java
// Java -- PricingService.java (BEFORE)
public class PricingService {

    public double calculatePrice(String customerType, double basePrice) {
        if ("REGULAR".equals(customerType)) {
            return basePrice;
        } else if ("PREMIUM".equals(customerType)) {
            return basePrice * 0.9;  // 10% off
        } else if ("VIP".equals(customerType)) {
            return basePrice * 0.8;  // 20% off
        } else if ("EMPLOYEE".equals(customerType)) {
            return basePrice * 0.7;  // 30% off
        } else {
            throw new IllegalArgumentException("Unknown type: " + customerType);
        }
        // New customer type? Add ANOTHER branch here.
        // Testing? You must test the ENTIRE method every time.
    }
}
```

```
Problems with this approach:
+------------------------------------------+
| 1. Every new type modifies this class     |
| 2. Violates Open/Closed Principle         |
| 3. Hard to test individual strategies     |
| 4. String-based type checking is fragile  |
| 5. Logic for ALL types lives in ONE place |
+------------------------------------------+
```

---

## The Solution: Strategy Pattern

The Strategy pattern says: **define a family of algorithms, put each in its own class, and make them interchangeable.**

```
+------------------------------------------------------+
|                   HOW STRATEGY WORKS                  |
+------------------------------------------------------+

  Client (PricingService)
      |
      | uses
      v
  +-----------------------+
  | PricingStrategy       |  <--- Interface
  | + calculatePrice()    |
  +-----------------------+
      ^         ^         ^
      |         |         |
  +--------+ +--------+ +--------+
  |Regular | |Premium | | VIP    |  <--- Concrete Strategies
  |Strategy| |Strategy| |Strategy|
  +--------+ +--------+ +--------+

  The client does NOT know which strategy it holds.
  You can swap strategies at runtime without changing
  the client code.
```

---

## Java Implementation: PricingStrategy

### Step 1: Define the Strategy Interface

```java
// PricingStrategy.java
public interface PricingStrategy {
    double calculatePrice(double basePrice);
    String getStrategyName();
}
```

### Step 2: Implement Concrete Strategies

```java
// RegularPricingStrategy.java
public class RegularPricingStrategy implements PricingStrategy {

    @Override
    public double calculatePrice(double basePrice) {
        return basePrice;  // No discount
    }

    @Override
    public String getStrategyName() {
        return "REGULAR";
    }
}

// PremiumPricingStrategy.java
public class PremiumPricingStrategy implements PricingStrategy {

    @Override
    public double calculatePrice(double basePrice) {
        return basePrice * 0.9;  // 10% discount
    }

    @Override
    public String getStrategyName() {
        return "PREMIUM";
    }
}

// VIPPricingStrategy.java
public class VIPPricingStrategy implements PricingStrategy {

    @Override
    public double calculatePrice(double basePrice) {
        return basePrice * 0.8;  // 20% discount
    }

    @Override
    public String getStrategyName() {
        return "VIP";
    }
}
```

### Step 3: Use the Strategy in a Service

```java
// PricingService.java (AFTER -- Strategy Pattern)
public class PricingService {
    private PricingStrategy strategy;

    public PricingService(PricingStrategy strategy) {
        this.strategy = strategy;
    }

    public void setStrategy(PricingStrategy strategy) {
        this.strategy = strategy;
    }

    public double calculatePrice(double basePrice) {
        return strategy.calculatePrice(basePrice);
    }
}
```

### Step 4: Client Code

```java
// Main.java
public class Main {
    public static void main(String[] args) {
        PricingService service = new PricingService(new RegularPricingStrategy());

        double price = 100.0;
        System.out.println("Regular: $" + service.calculatePrice(price));

        // Swap strategy at runtime -- no if/else needed
        service.setStrategy(new PremiumPricingStrategy());
        System.out.println("Premium: $" + service.calculatePrice(price));

        service.setStrategy(new VIPPricingStrategy());
        System.out.println("VIP:     $" + service.calculatePrice(price));
    }
}
```

**Output:**
```
Regular: $100.0
Premium: $90.0
VIP:     $80.0
```

---

## Before vs After Comparison

```
BEFORE (if/else):                    AFTER (Strategy):
+---------------------------+        +---------------------------+
| PricingService            |        | PricingService            |
|                           |        |   - strategy: Strategy    |
| if (type == "REGULAR")    |        |   + calculatePrice()      |
|   return basePrice;       |        +---------------------------+
| else if (type == "PREMIUM"|                   |
|   return basePrice * 0.9; |                   v
| else if (type == "VIP")   |        +---------------------------+
|   return basePrice * 0.8; |        | <<interface>>             |
| else if ...               |        | PricingStrategy           |
| // KEEPS GROWING          |        |   + calculatePrice()      |
+---------------------------+        +---------------------------+
                                        ^       ^       ^
  Adding a new type:                    |       |       |
  - Modify existing class          Regular  Premium   VIP
  - Risk breaking other types
  - Retest everything               Adding a new type:
                                     - Add a new class
                                     - Existing code untouched
                                     - Test ONLY the new class
```

---

## Java Implementation: SortingStrategy

Here is another common backend scenario -- choosing a sorting algorithm based on data characteristics.

```java
// SortingStrategy.java
public interface SortingStrategy<T extends Comparable<T>> {
    void sort(List<T> data);
    String getName();
}

// QuickSortStrategy.java
public class QuickSortStrategy<T extends Comparable<T>> implements SortingStrategy<T> {

    @Override
    public void sort(List<T> data) {
        Collections.sort(data);  // Java uses TimSort internally
        System.out.println("  [QuickSort applied to " + data.size() + " elements]");
    }

    @Override
    public String getName() {
        return "QuickSort";
    }
}

// BubbleSortStrategy.java
public class BubbleSortStrategy<T extends Comparable<T>> implements SortingStrategy<T> {

    @Override
    public void sort(List<T> data) {
        for (int i = 0; i < data.size() - 1; i++) {
            for (int j = 0; j < data.size() - i - 1; j++) {
                if (data.get(j).compareTo(data.get(j + 1)) > 0) {
                    T temp = data.get(j);
                    data.set(j, data.get(j + 1));
                    data.set(j + 1, temp);
                }
            }
        }
        System.out.println("  [BubbleSort applied to " + data.size() + " elements]");
    }

    @Override
    public String getName() {
        return "BubbleSort";
    }
}

// DataProcessor.java
public class DataProcessor<T extends Comparable<T>> {
    private SortingStrategy<T> sortingStrategy;

    public DataProcessor(SortingStrategy<T> sortingStrategy) {
        this.sortingStrategy = sortingStrategy;
    }

    public void setSortingStrategy(SortingStrategy<T> strategy) {
        this.sortingStrategy = strategy;
    }

    public List<T> process(List<T> data) {
        List<T> copy = new ArrayList<>(data);
        System.out.println("Processing with " + sortingStrategy.getName() + ":");
        sortingStrategy.sort(copy);
        return copy;
    }
}
```

```java
// Main.java
public class Main {
    public static void main(String[] args) {
        List<Integer> data = Arrays.asList(42, 17, 93, 5, 28, 61);

        DataProcessor<Integer> processor = new DataProcessor<>(new QuickSortStrategy<>());
        List<Integer> result1 = processor.process(data);
        System.out.println("Result: " + result1);

        // Switch to BubbleSort for small datasets
        processor.setSortingStrategy(new BubbleSortStrategy<>());
        List<Integer> smallData = Arrays.asList(3, 1, 2);
        List<Integer> result2 = processor.process(smallData);
        System.out.println("Result: " + result2);
    }
}
```

**Output:**
```
Processing with QuickSort:
  [QuickSort applied to 6 elements]
Result: [5, 17, 28, 42, 61, 93]
Processing with BubbleSort:
  [BubbleSort applied to 3 elements]
Result: [1, 2, 3]
```

---

## Python Implementation: AuthStrategy

Authentication is a perfect use case. Different endpoints may need different authentication methods.

```python
# auth_strategy.py
from abc import ABC, abstractmethod
import hashlib
import hmac
import base64
import time


class AuthStrategy(ABC):
    """Base strategy for authentication."""

    @abstractmethod
    def authenticate(self, request: dict) -> bool:
        """Return True if the request is authenticated."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class APIKeyAuthStrategy(AuthStrategy):
    """Authenticate using an API key in the header."""

    VALID_KEYS = {"sk-abc123", "sk-def456", "sk-ghi789"}

    def authenticate(self, request: dict) -> bool:
        api_key = request.get("headers", {}).get("X-API-Key", "")
        return api_key in self.VALID_KEYS

    def get_name(self) -> str:
        return "API Key"


class JWTAuthStrategy(AuthStrategy):
    """Authenticate using a JWT token."""

    SECRET = "my-secret-key"

    def authenticate(self, request: dict) -> bool:
        auth_header = request.get("headers", {}).get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False

        token = auth_header[7:]  # Remove "Bearer "
        # Simplified JWT validation (real apps use a JWT library)
        try:
            parts = token.split(".")
            return len(parts) == 3 and len(token) > 20
        except Exception:
            return False

    def get_name(self) -> str:
        return "JWT"


class HMACAuthStrategy(AuthStrategy):
    """Authenticate using HMAC signature."""

    SECRET = b"shared-secret-key"

    def authenticate(self, request: dict) -> bool:
        signature = request.get("headers", {}).get("X-Signature", "")
        body = request.get("body", "")

        expected = hmac.new(
            self.SECRET, body.encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    def get_name(self) -> str:
        return "HMAC"


class AuthService:
    """Service that delegates authentication to a strategy."""

    def __init__(self, strategy: AuthStrategy):
        self._strategy = strategy

    @property
    def strategy(self) -> AuthStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, new_strategy: AuthStrategy):
        self._strategy = new_strategy

    def authenticate(self, request: dict) -> bool:
        print(f"  Authenticating with {self._strategy.get_name()}...", end=" ")
        result = self._strategy.authenticate(request)
        print("OK" if result else "FAILED")
        return result


# --- Usage ---
if __name__ == "__main__":
    # API Key authentication
    service = AuthService(APIKeyAuthStrategy())

    request_with_key = {
        "headers": {"X-API-Key": "sk-abc123"},
        "body": '{"action": "list_users"}'
    }
    service.authenticate(request_with_key)

    # Switch to JWT authentication at runtime
    service.strategy = JWTAuthStrategy()

    request_with_jwt = {
        "headers": {"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.payload.signature"},
        "body": '{"action": "get_profile"}'
    }
    service.authenticate(request_with_jwt)

    # Switch to HMAC for webhook verification
    service.strategy = HMACAuthStrategy()

    body = '{"event": "payment.completed"}'
    signature = hmac.new(
        b"shared-secret-key", body.encode(), hashlib.sha256
    ).hexdigest()

    request_with_hmac = {
        "headers": {"X-Signature": signature},
        "body": body
    }
    service.authenticate(request_with_hmac)
```

**Output:**
```
  Authenticating with API Key... OK
  Authenticating with JWT... OK
  Authenticating with HMAC... OK
```

---

## Spring Boot: Strategy with @Qualifier

Spring makes the Strategy pattern even more powerful with dependency injection.

```java
// PricingStrategy.java
public interface PricingStrategy {
    double calculatePrice(double basePrice);
    String getType();
}

// RegularPricing.java
@Component
@Qualifier("regular")
public class RegularPricing implements PricingStrategy {

    @Override
    public double calculatePrice(double basePrice) {
        return basePrice;
    }

    @Override
    public String getType() {
        return "REGULAR";
    }
}

// PremiumPricing.java
@Component
@Qualifier("premium")
public class PremiumPricing implements PricingStrategy {

    @Override
    public double calculatePrice(double basePrice) {
        return basePrice * 0.9;
    }

    @Override
    public String getType() {
        return "PREMIUM";
    }
}

// VIPPricing.java
@Component
@Qualifier("vip")
public class VIPPricing implements PricingStrategy {

    @Override
    public double calculatePrice(double basePrice) {
        return basePrice * 0.8;
    }

    @Override
    public String getType() {
        return "VIP";
    }
}
```

### Strategy Registry Pattern (Spring-Powered)

```java
// PricingStrategyRegistry.java
@Component
public class PricingStrategyRegistry {

    private final Map<String, PricingStrategy> strategies;

    // Spring injects ALL PricingStrategy beans automatically
    @Autowired
    public PricingStrategyRegistry(List<PricingStrategy> strategyList) {
        strategies = strategyList.stream()
            .collect(Collectors.toMap(
                PricingStrategy::getType,
                Function.identity()
            ));
        System.out.println("Registered strategies: " + strategies.keySet());
    }

    public PricingStrategy getStrategy(String customerType) {
        PricingStrategy strategy = strategies.get(customerType);
        if (strategy == null) {
            throw new IllegalArgumentException(
                "No strategy for type: " + customerType
                + ". Available: " + strategies.keySet()
            );
        }
        return strategy;
    }
}

// PricingController.java
@RestController
@RequestMapping("/api/pricing")
public class PricingController {

    private final PricingStrategyRegistry registry;

    public PricingController(PricingStrategyRegistry registry) {
        this.registry = registry;
    }

    @GetMapping("/calculate")
    public Map<String, Object> calculate(
            @RequestParam String customerType,
            @RequestParam double basePrice) {

        PricingStrategy strategy = registry.getStrategy(customerType);
        double finalPrice = strategy.calculatePrice(basePrice);

        return Map.of(
            "customerType", customerType,
            "basePrice", basePrice,
            "finalPrice", finalPrice,
            "discount", (1 - finalPrice / basePrice) * 100 + "%"
        );
    }
}
```

```
How Spring Strategy Registry Works:

  Spring Container
  +-----------------------------------------------+
  |                                                |
  |  @Component         @Component     @Component  |
  |  RegularPricing     PremiumPricing VIPPricing  |
  |       |                  |             |        |
  |       +------------------+-------------+        |
  |                     |                           |
  |                     v                           |
  |        PricingStrategyRegistry                  |
  |        Map<String, PricingStrategy>             |
  |        {                                        |
  |          "REGULAR" -> RegularPricing,            |
  |          "PREMIUM" -> PremiumPricing,            |
  |          "VIP"     -> VIPPricing                 |
  |        }                                        |
  |                     |                           |
  |                     v                           |
  |           PricingController                     |
  |           GET /api/pricing/calculate            |
  +-----------------------------------------------+

  To add a new strategy:
  1. Create a new @Component class
  2. Implement PricingStrategy
  3. Done! Spring auto-discovers it.
```

---

## Real-World Use Case: Payment Processing

```java
// PaymentStrategy.java
public interface PaymentStrategy {
    PaymentResult process(PaymentRequest request);
    boolean supports(String paymentMethod);
    int getRetryLimit();
}

// CreditCardPayment.java
@Component
public class CreditCardPayment implements PaymentStrategy {

    @Override
    public PaymentResult process(PaymentRequest request) {
        // Connect to credit card gateway
        System.out.println("Processing credit card: **** " +
            request.getCardNumber().substring(12));
        // Charge the card...
        return new PaymentResult(true, "CC-" + System.currentTimeMillis());
    }

    @Override
    public boolean supports(String paymentMethod) {
        return "CREDIT_CARD".equals(paymentMethod);
    }

    @Override
    public int getRetryLimit() {
        return 3;  // Allow retries for network issues
    }
}

// PayPalPayment.java
@Component
public class PayPalPayment implements PaymentStrategy {

    @Override
    public PaymentResult process(PaymentRequest request) {
        System.out.println("Redirecting to PayPal for: $" + request.getAmount());
        // Initiate PayPal flow...
        return new PaymentResult(true, "PP-" + System.currentTimeMillis());
    }

    @Override
    public boolean supports(String paymentMethod) {
        return "PAYPAL".equals(paymentMethod);
    }

    @Override
    public int getRetryLimit() {
        return 1;  // No retries -- user must restart
    }
}

// BankTransferPayment.java
@Component
public class BankTransferPayment implements PaymentStrategy {

    @Override
    public PaymentResult process(PaymentRequest request) {
        System.out.println("Initiating bank transfer: $" + request.getAmount());
        // Queue bank transfer...
        return new PaymentResult(true, "BT-" + System.currentTimeMillis());
    }

    @Override
    public boolean supports(String paymentMethod) {
        return "BANK_TRANSFER".equals(paymentMethod);
    }

    @Override
    public int getRetryLimit() {
        return 0;  // Never retry bank transfers
    }
}

// PaymentService.java
@Service
public class PaymentService {

    private final List<PaymentStrategy> strategies;

    @Autowired
    public PaymentService(List<PaymentStrategy> strategies) {
        this.strategies = strategies;
    }

    public PaymentResult processPayment(PaymentRequest request) {
        PaymentStrategy strategy = strategies.stream()
            .filter(s -> s.supports(request.getPaymentMethod()))
            .findFirst()
            .orElseThrow(() -> new UnsupportedOperationException(
                "No strategy for: " + request.getPaymentMethod()
            ));

        int attempts = 0;
        while (attempts <= strategy.getRetryLimit()) {
            try {
                return strategy.process(request);
            } catch (Exception e) {
                attempts++;
                System.out.println("Attempt " + attempts + " failed: " + e.getMessage());
            }
        }
        return new PaymentResult(false, "FAILED after " + attempts + " attempts");
    }
}
```

---

## Real-World Use Case: Compression Strategy

```python
# compression_strategy.py
from abc import ABC, abstractmethod
import gzip
import zlib
import json


class CompressionStrategy(ABC):

    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        pass

    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class GzipCompression(CompressionStrategy):

    def compress(self, data: bytes) -> bytes:
        return gzip.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return gzip.decompress(data)

    def get_name(self) -> str:
        return "gzip"


class ZlibCompression(CompressionStrategy):

    def compress(self, data: bytes) -> bytes:
        return zlib.compress(data, level=9)

    def decompress(self, data: bytes) -> bytes:
        return zlib.decompress(data)

    def get_name(self) -> str:
        return "zlib"


class NoCompression(CompressionStrategy):

    def compress(self, data: bytes) -> bytes:
        return data  # Pass-through

    def decompress(self, data: bytes) -> bytes:
        return data

    def get_name(self) -> str:
        return "none"


class DataStore:
    """Stores data using a pluggable compression strategy."""

    def __init__(self, strategy: CompressionStrategy):
        self._strategy = strategy
        self._storage: dict[str, bytes] = {}

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, new_strategy: CompressionStrategy):
        self._strategy = new_strategy

    def store(self, key: str, data: str) -> None:
        raw = data.encode("utf-8")
        compressed = self._strategy.compress(raw)
        self._storage[key] = compressed
        ratio = len(compressed) / len(raw) * 100
        print(f"  Stored '{key}': {len(raw)}B -> {len(compressed)}B "
              f"({ratio:.1f}%) using {self._strategy.get_name()}")

    def retrieve(self, key: str) -> str:
        compressed = self._storage[key]
        raw = self._strategy.decompress(compressed)
        return raw.decode("utf-8")


# --- Usage ---
if __name__ == "__main__":
    store = DataStore(GzipCompression())

    large_data = json.dumps({"users": [{"name": f"User {i}"} for i in range(100)]})
    store.store("users", large_data)

    # Switch to zlib for different data
    store.strategy = ZlibCompression()
    store.store("config", large_data)

    # Retrieve data
    retrieved = store.retrieve("users")
    print(f"  Retrieved 'users': {len(retrieved)} bytes")
```

**Output:**
```
  Stored 'users': 2090B -> bytes 138B (6.6%) using gzip
  Stored 'config': 2090B -> 126B (6.0%) using zlib
  Retrieved 'users': 2090 bytes
```

---

## When to Use / When NOT to Use

### Use Strategy When

| Scenario | Why Strategy Helps |
|---|---|
| Multiple algorithms for the same task | Each algorithm is isolated and testable |
| Behavior selected at runtime | Swap strategies without code changes |
| Complex conditional logic | Replace if/else chains with objects |
| Algorithms evolve independently | Change one without affecting others |
| Different clients need different behaviors | Inject the right strategy per client |

### Do NOT Use Strategy When

| Scenario | Why Not |
|---|---|
| Only two simple options | A simple `if/else` is clearer |
| Algorithm never changes at runtime | Direct implementation is simpler |
| Strategies share lots of state | They become tightly coupled anyway |
| You have only one algorithm | Do not over-engineer a non-problem |

---

## Common Mistakes

### Mistake 1: Strategies That Know About Each Other

```java
// BAD -- Strategy depends on another strategy
public class PremiumPricing implements PricingStrategy {
    @Override
    public double calculatePrice(double basePrice) {
        // This couples Premium to Regular -- WRONG
        RegularPricing regular = new RegularPricing();
        return regular.calculatePrice(basePrice) * 0.9;
    }
}

// GOOD -- Each strategy is self-contained
public class PremiumPricing implements PricingStrategy {
    @Override
    public double calculatePrice(double basePrice) {
        return basePrice * 0.9;
    }
}
```

### Mistake 2: Passing Too Much Context to Strategies

```java
// BAD -- Strategy knows about the entire service
public interface PricingStrategy {
    double calculatePrice(PricingService service, Order order,
                          Customer customer, Inventory inventory);
}

// GOOD -- Strategy receives only what it needs
public interface PricingStrategy {
    double calculatePrice(double basePrice);
}
```

### Mistake 3: Forgetting a Default Strategy

```java
// BAD -- Crashes when strategy is null
public class PricingService {
    private PricingStrategy strategy;  // Could be null!

    public double calculate(double price) {
        return strategy.calculatePrice(price);  // NullPointerException
    }
}

// GOOD -- Always has a fallback
public class PricingService {
    private PricingStrategy strategy = new RegularPricingStrategy();

    public double calculate(double price) {
        return strategy.calculatePrice(price);  // Always safe
    }
}
```

---

## Best Practices

1. **Name strategies after what they do**, not how they are selected. `GzipCompression` is better than `Option3`.

2. **Use a registry or factory** to map identifiers to strategies instead of hard-coding the mapping.

3. **Keep the strategy interface small.** One or two methods. If you need more, you might need a different pattern.

4. **Make strategies stateless when possible.** Stateless strategies can be shared across threads safely.

5. **Provide a default strategy** so the system works even without explicit configuration.

6. **Let Spring auto-discover strategies** by implementing a common interface and using `List<Strategy>` injection.

7. **Document which strategy to use when.** The pattern makes code flexible, but someone still has to pick the right one.

---

## Quick Summary

```
+---------------------------------------------------------------+
|                    STRATEGY PATTERN SUMMARY                    |
+---------------------------------------------------------------+
| Intent:     Define a family of algorithms, encapsulate each    |
|             one, and make them interchangeable.                |
+---------------------------------------------------------------+
| Problem:    if/else chains that grow with every new algorithm  |
| Solution:   One interface, many implementations, swap freely  |
+---------------------------------------------------------------+
| Key parts:                                                     |
|   - Strategy interface (the contract)                          |
|   - Concrete strategies (the algorithms)                       |
|   - Context (the class that uses a strategy)                   |
+---------------------------------------------------------------+
| Runtime behavior: Change strategy = change behavior            |
| Compile-time safety: Interface guarantees compatibility        |
+---------------------------------------------------------------+
```

---

## Key Points

- The Strategy pattern replaces conditional logic with polymorphism.
- Each algorithm lives in its own class, making it easy to test and modify independently.
- The context class holds a reference to a strategy and delegates work to it.
- Strategies can be swapped at runtime without modifying client code.
- Spring's dependency injection and `@Qualifier` make strategy selection automatic.
- Strategy is one of the most frequently used patterns in backend services.

---

## Practice Questions

1. You have a notification service that sends alerts via email, SMS, and push notifications. How would you apply the Strategy pattern? What would the strategy interface look like?

2. A colleague argues that an `enum` with a method per value is simpler than Strategy. When is the colleague right, and when does Strategy become the better choice?

3. In the Spring Strategy Registry example, what happens if two strategies return the same value from `getType()`? How would you prevent this?

4. How does the Strategy pattern relate to the Open/Closed Principle? Give a concrete example from the payment processing use case.

5. If strategies need access to shared resources (like a database connection), how should you provide that access without coupling strategies to infrastructure?

---

## Exercises

### Exercise 1: Shipping Cost Calculator

Build a shipping cost calculator with three strategies: `StandardShipping` (flat $5), `ExpressShipping` ($5 + $2 per kg), and `FreeShipping` (returns 0). Write a `ShippingService` that accepts a strategy and calculates the cost. Write tests that verify swapping strategies at runtime changes the output.

### Exercise 2: Text Formatter

Create a `TextFormatterStrategy` with implementations for `MarkdownFormatter`, `HTMLFormatter`, and `PlainTextFormatter`. Each takes a title and a list of bullet points and formats them differently. Build a report generator that uses these strategies to produce output in any format.

### Exercise 3: Rate Limiter (Advanced)

Implement a rate-limiting system with strategies: `FixedWindowLimiter` (N requests per minute), `SlidingWindowLimiter` (smooth rate limiting), and `TokenBucketLimiter` (burst-friendly). Use the Strategy pattern so the API gateway can switch rate-limiting algorithms per endpoint.

---

## What Is Next?

You have seen how Strategy lets you swap algorithms at runtime. But what if you need to notify multiple parts of your system when something changes? In the next chapter, we will explore the **Observer pattern** -- a way to broadcast events so that many listeners can react without the sender knowing who they are. This pattern powers everything from order notifications to cache invalidation in modern backends.
