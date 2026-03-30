# Chapter 7: The Adapter Pattern

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand the Adapter pattern and why it exists
- Recognize when two interfaces are incompatible and need bridging
- Implement both class adapters and object adapters
- Build a `LegacyPaymentAdapter` in Java that wraps an old payment API behind a new interface
- Create an XML-to-JSON adapter in Python for data format translation
- Distinguish between class adapters and object adapters and choose the right one
- Apply the Adapter pattern to real-world scenarios like third-party API integration and legacy system migration
- Avoid common pitfalls when writing adapters

---

## Why This Chapter Matters

Every backend system eventually faces this problem: you have code that works, and you have new code that expects a different interface. Maybe you are integrating a third-party payment gateway that uses XML while your system speaks JSON. Maybe you inherited a legacy billing system that cannot be rewritten, but your new microservice expects a clean, modern API. Maybe a vendor changed their SDK, and now nothing compiles.

The Adapter pattern solves all of these problems without modifying the existing code. It is one of the most practical design patterns you will use in your career.

Think of it this way. You travel from the United States to Europe. Your laptop charger has a US plug, but European outlets have a different shape. You do not rewire your charger or modify the wall outlet. You buy a **plug adapter** that sits between the two and makes them compatible.

```
  US Plug               Adapter              EU Outlet
  ┌─────┐           ┌───────────┐           ┌─────────┐
  │ | | │──────────>│  | |  ○○  │──────────>│  ○   ○  │
  │     │           │  US   EU  │           │    ○    │
  └─────┘           └───────────┘           └─────────┘
  (Your code)    (Adapter class)      (Incompatible interface)
```

The Adapter pattern does exactly this for software interfaces. It wraps an existing class with a new interface so that incompatible classes can work together.

---

## The Problem

Suppose you are building an e-commerce platform. Your payment processing module defines a clean interface:

```java
public interface PaymentProcessor {
    PaymentResult processPayment(String customerId, double amount, String currency);
    PaymentStatus checkStatus(String transactionId);
    RefundResult refund(String transactionId, double amount);
}
```

Your application code uses this interface everywhere. Controllers, services, tests -- everything depends on `PaymentProcessor`.

Now your company acquires a smaller business that uses a completely different payment system:

```java
public class LegacyPaymentGateway {
    public int makePayment(String xmlPayload) { /* ... */ }
    public String getPaymentInfo(int paymentCode) { /* ... */ }
    public int reverseTransaction(int paymentCode, String xmlPayload) { /* ... */ }
}
```

The legacy system:
- Uses XML strings instead of typed parameters
- Returns integer status codes instead of result objects
- Uses different method names
- Has a completely different calling convention

You cannot change `PaymentProcessor` because dozens of classes depend on it. You cannot rewrite `LegacyPaymentGateway` because it is a third-party library with no source code. You need something in between.

---

## The Solution: Adapter Pattern

The Adapter pattern creates a wrapper class that translates calls from one interface into calls on another.

```
┌─────────────────────────────────────────────────────────────┐
│                    Adapter Pattern Structure                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────┐        ┌──────────────┐      ┌────────────┐ │
│   │  Client   │───────>│   Target     │      │  Adaptee   │ │
│   │          │        │  Interface   │      │  (Legacy)  │ │
│   └──────────┘        └──────┬───────┘      └─────┬──────┘ │
│                              │                     │        │
│                              │   implements        │        │
│                              │                     │        │
│                        ┌─────┴───────┐             │        │
│                        │   Adapter    │─────────────┘        │
│                        │             │    wraps / delegates  │
│                        └─────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Four participants:**

1. **Target** -- the interface the client expects (`PaymentProcessor`)
2. **Adaptee** -- the existing class with an incompatible interface (`LegacyPaymentGateway`)
3. **Adapter** -- the class that bridges the two (`LegacyPaymentAdapter`)
4. **Client** -- the code that uses the Target interface (your services, controllers)

---

## Class Adapter vs Object Adapter

There are two ways to implement the Adapter pattern:

### Object Adapter (Composition)

The adapter holds a reference to the adaptee and delegates calls to it.

```
┌──────────────────┐         ┌──────────────────┐
│  <<interface>>   │         │  LegacyGateway   │
│ PaymentProcessor │         │                  │
├──────────────────┤         ├──────────────────┤
│ + processPayment │         │ + makePayment()  │
│ + checkStatus()  │         │ + getPaymentInfo │
│ + refund()       │         │ + reverseTx()    │
└────────┬─────────┘         └────────┬─────────┘
         │ implements                  │
         │                             │ has-a (composition)
    ┌────┴──────────────┐              │
    │ LegacyPayment     │──────────────┘
    │ Adapter            │
    ├───────────────────┤
    │ - legacyGateway   │
    ├───────────────────┤
    │ + processPayment()│  --> calls legacyGateway.makePayment()
    │ + checkStatus()   │  --> calls legacyGateway.getPaymentInfo()
    │ + refund()        │  --> calls legacyGateway.reverseTx()
    └───────────────────┘
```

### Class Adapter (Inheritance)

The adapter extends the adaptee and implements the target interface.

```
┌──────────────────┐         ┌──────────────────┐
│  <<interface>>   │         │  LegacyGateway   │
│ PaymentProcessor │         │                  │
└────────┬─────────┘         └────────┬─────────┘
         │ implements                  │ extends
         │                             │
    ┌────┴─────────────────────────────┴──┐
    │   LegacyPaymentAdapter              │
    ├─────────────────────────────────────┤
    │ + processPayment()│  --> calls this.makePayment()
    │ + checkStatus()   │  --> calls this.getPaymentInfo()
    │ + refund()        │  --> calls this.reverseTx()
    └─────────────────────────────────────┘
```

**Which one should you use?**

| Criteria | Object Adapter | Class Adapter |
|---|---|---|
| Flexibility | Can adapt multiple adaptees | Can only adapt one class |
| Language support | Works in any language | Requires multiple inheritance |
| Runtime swapping | Can swap adaptee at runtime | Fixed at compile time |
| Access to adaptee internals | Only public methods | Can override protected methods |
| Recommendation | **Preferred in most cases** | Rarely used in Java/Python |

In Java (single inheritance) and Python (duck typing), the **object adapter** is almost always the right choice.

---

## Java Example: LegacyPaymentAdapter

Let us build a complete, working example.

### Step 1: Define the Target Interface

```java
// The interface your application expects
public interface PaymentProcessor {

    PaymentResult processPayment(String customerId, double amount, String currency);

    PaymentStatus checkStatus(String transactionId);

    RefundResult refund(String transactionId, double amount);
}
```

### Step 2: Define the Result Types

```java
public class PaymentResult {
    private final boolean success;
    private final String transactionId;
    private final String message;

    public PaymentResult(boolean success, String transactionId, String message) {
        this.success = success;
        this.transactionId = transactionId;
        this.message = message;
    }

    public boolean isSuccess() { return success; }
    public String getTransactionId() { return transactionId; }
    public String getMessage() { return message; }

    @Override
    public String toString() {
        return "PaymentResult{success=" + success
            + ", transactionId='" + transactionId + "'"
            + ", message='" + message + "'}";
    }
}

public enum PaymentStatus {
    PENDING, COMPLETED, FAILED, REFUNDED, UNKNOWN
}

public class RefundResult {
    private final boolean success;
    private final String message;

    public RefundResult(boolean success, String message) {
        this.success = success;
        this.message = message;
    }

    public boolean isSuccess() { return success; }
    public String getMessage() { return message; }

    @Override
    public String toString() {
        return "RefundResult{success=" + success + ", message='" + message + "'}";
    }
}
```

### Step 3: The Legacy System (Adaptee)

This is the old system you cannot modify. It uses XML, integer codes, and completely different method signatures.

```java
// Third-party legacy code -- you CANNOT modify this
public class LegacyPaymentGateway {

    public int makePayment(String xmlPayload) {
        // Parses XML, processes payment, returns status code
        System.out.println("  [Legacy] Processing XML payload: " + xmlPayload);

        // Simulate: 0 = success, 1 = insufficient funds, 2 = error
        if (xmlPayload.contains("amount=\"0\"")) {
            return 2; // error for zero amount
        }
        return 0; // success
    }

    public String getPaymentInfo(int paymentCode) {
        // Returns XML string with payment details
        System.out.println("  [Legacy] Looking up payment code: " + paymentCode);
        return "<payment><code>" + paymentCode
            + "</code><status>COMPLETED</status></payment>";
    }

    public int reverseTransaction(int paymentCode, String xmlPayload) {
        System.out.println("  [Legacy] Reversing payment code: " + paymentCode);
        return 0; // success
    }

    // Legacy method to generate a payment code from a transaction
    public int generatePaymentCode(String customerId) {
        return Math.abs(customerId.hashCode() % 100000);
    }
}
```

### Step 4: The Adapter

This is where the magic happens. The adapter implements `PaymentProcessor` and delegates to `LegacyPaymentGateway`.

```java
public class LegacyPaymentAdapter implements PaymentProcessor {

    private final LegacyPaymentGateway legacyGateway;

    // Store mapping between our transaction IDs and legacy payment codes
    private final Map<String, Integer> transactionToCodeMap = new HashMap<>();

    public LegacyPaymentAdapter(LegacyPaymentGateway legacyGateway) {
        this.legacyGateway = legacyGateway;
    }

    @Override
    public PaymentResult processPayment(String customerId, double amount, String currency) {
        // Step 1: Convert our parameters to XML (what the legacy system expects)
        String xmlPayload = buildPaymentXml(customerId, amount, currency);

        // Step 2: Call the legacy system
        int resultCode = legacyGateway.makePayment(xmlPayload);

        // Step 3: Convert the legacy result to our result type
        String transactionId = generateTransactionId();
        int paymentCode = legacyGateway.generatePaymentCode(customerId);
        transactionToCodeMap.put(transactionId, paymentCode);

        return convertToPaymentResult(resultCode, transactionId);
    }

    @Override
    public PaymentStatus checkStatus(String transactionId) {
        // Look up the legacy payment code from our transaction ID
        Integer paymentCode = transactionToCodeMap.get(transactionId);
        if (paymentCode == null) {
            return PaymentStatus.UNKNOWN;
        }

        // Call legacy system and parse the XML response
        String xmlResponse = legacyGateway.getPaymentInfo(paymentCode);
        return parseStatusFromXml(xmlResponse);
    }

    @Override
    public RefundResult refund(String transactionId, double amount) {
        Integer paymentCode = transactionToCodeMap.get(transactionId);
        if (paymentCode == null) {
            return new RefundResult(false, "Transaction not found");
        }

        String xmlPayload = "<refund><amount>" + amount + "</amount></refund>";
        int resultCode = legacyGateway.reverseTransaction(paymentCode, xmlPayload);

        if (resultCode == 0) {
            return new RefundResult(true, "Refund processed successfully");
        }
        return new RefundResult(false, "Refund failed with code: " + resultCode);
    }

    // --- Private helper methods for translation ---

    private String buildPaymentXml(String customerId, double amount, String currency) {
        return "<payment>"
            + "<customer>" + customerId + "</customer>"
            + "<amount=\"" + amount + "\"/>"
            + "<currency>" + currency + "</currency>"
            + "</payment>";
    }

    private String generateTransactionId() {
        return "TXN-" + System.currentTimeMillis();
    }

    private PaymentResult convertToPaymentResult(int legacyCode, String transactionId) {
        switch (legacyCode) {
            case 0:
                return new PaymentResult(true, transactionId, "Payment successful");
            case 1:
                return new PaymentResult(false, transactionId, "Insufficient funds");
            default:
                return new PaymentResult(false, transactionId,
                    "Payment failed with legacy code: " + legacyCode);
        }
    }

    private PaymentStatus parseStatusFromXml(String xml) {
        if (xml.contains("COMPLETED")) return PaymentStatus.COMPLETED;
        if (xml.contains("PENDING"))   return PaymentStatus.PENDING;
        if (xml.contains("FAILED"))    return PaymentStatus.FAILED;
        if (xml.contains("REFUNDED"))  return PaymentStatus.REFUNDED;
        return PaymentStatus.UNKNOWN;
    }
}
```

### Step 5: Using the Adapter

```java
public class PaymentService {

    private final PaymentProcessor paymentProcessor;

    // The service only knows about PaymentProcessor -- it has no idea
    // whether it is talking to the new system or the legacy one
    public PaymentService(PaymentProcessor paymentProcessor) {
        this.paymentProcessor = paymentProcessor;
    }

    public void checkout(String customerId, double total) {
        System.out.println("Processing checkout for customer: " + customerId);

        PaymentResult result = paymentProcessor.processPayment(
            customerId, total, "USD"
        );
        System.out.println("Payment result: " + result);

        if (result.isSuccess()) {
            PaymentStatus status = paymentProcessor.checkStatus(
                result.getTransactionId()
            );
            System.out.println("Payment status: " + status);
        }
    }
}

public class Main {
    public static void main(String[] args) {
        // Create the legacy system (cannot modify this)
        LegacyPaymentGateway legacyGateway = new LegacyPaymentGateway();

        // Wrap it with our adapter
        PaymentProcessor adapter = new LegacyPaymentAdapter(legacyGateway);

        // Use it in our service -- the service does not know about the legacy system
        PaymentService service = new PaymentService(adapter);
        service.checkout("CUST-42", 99.99);
    }
}
```

**Output:**

```
Processing checkout for customer: CUST-42
  [Legacy] Processing XML payload: <payment><customer>CUST-42</customer>...
Payment result: PaymentResult{success=true, transactionId='TXN-1703001234567', message='Payment successful'}
  [Legacy] Looking up payment code: 28456
Payment status: COMPLETED
```

### Before vs After

**Before (without adapter) -- tight coupling to legacy system:**

```java
// Every service that needs payments must deal with XML and integer codes
public class CheckoutService {
    private LegacyPaymentGateway gateway = new LegacyPaymentGateway();

    public void checkout(String customerId, double total) {
        // Build XML manually in every service method
        String xml = "<payment><customer>" + customerId + "</customer>"
            + "<amount>" + total + "</amount></payment>";
        int code = gateway.makePayment(xml);

        // Interpret integer codes in every service method
        if (code == 0) {
            System.out.println("Success");
        } else if (code == 1) {
            System.out.println("Insufficient funds");
        }
        // XML parsing scattered everywhere...
    }
}
```

**After (with adapter) -- clean separation:**

```java
public class CheckoutService {
    private PaymentProcessor processor; // clean interface

    public CheckoutService(PaymentProcessor processor) {
        this.processor = processor;
    }

    public void checkout(String customerId, double total) {
        PaymentResult result = processor.processPayment(customerId, total, "USD");
        if (result.isSuccess()) {
            System.out.println("Payment confirmed: " + result.getTransactionId());
        }
    }
}
```

---

## Python Example: XML-to-JSON Adapter

Python's duck typing makes adapters even more natural. Here is a real-world scenario: you have an analytics service that consumes JSON, but a legacy reporting system produces XML.

### The Problem

```python
# Your modern analytics service expects data like this:
class AnalyticsService:
    """Processes analytics data in JSON (dict) format."""

    def process_report(self, data: dict) -> None:
        """Expects a dict with keys: 'report_id', 'metrics', 'timestamp'."""
        print(f"Processing report: {data['report_id']}")
        for metric, value in data['metrics'].items():
            print(f"  {metric}: {value}")
        print(f"  Generated at: {data['timestamp']}")

    def aggregate_reports(self, reports: list[dict]) -> dict:
        """Combines multiple report dicts into a summary."""
        total_metrics = {}
        for report in reports:
            for metric, value in report['metrics'].items():
                total_metrics[metric] = total_metrics.get(metric, 0) + value
        return {"summary": total_metrics, "report_count": len(reports)}
```

```python
# But the legacy reporting system produces XML strings
class LegacyReportingSystem:
    """Old system that generates reports as XML strings."""

    def generate_daily_report(self) -> str:
        return """<?xml version="1.0"?>
        <report>
            <report_id>RPT-2024-001</report_id>
            <timestamp>2024-01-15T10:30:00Z</timestamp>
            <metrics>
                <metric name="page_views" value="15234"/>
                <metric name="unique_visitors" value="4521"/>
                <metric name="bounce_rate" value="34"/>
                <metric name="avg_session_minutes" value="7"/>
            </metrics>
        </report>"""

    def generate_weekly_report(self) -> str:
        return """<?xml version="1.0"?>
        <report>
            <report_id>RPT-2024-W03</report_id>
            <timestamp>2024-01-21T00:00:00Z</timestamp>
            <metrics>
                <metric name="page_views" value="98432"/>
                <metric name="unique_visitors" value="28910"/>
                <metric name="bounce_rate" value="31"/>
                <metric name="avg_session_minutes" value="8"/>
            </metrics>
        </report>"""
```

These two systems cannot talk to each other directly.

### The Adapter

```python
import xml.etree.ElementTree as ET


class XMLToJSONReportAdapter:
    """Adapts the LegacyReportingSystem to produce JSON-compatible dicts."""

    def __init__(self, legacy_system: LegacyReportingSystem):
        self._legacy = legacy_system

    def get_daily_report(self) -> dict:
        """Gets the daily report as a dict (JSON-compatible)."""
        xml_string = self._legacy.generate_daily_report()
        return self._xml_to_dict(xml_string)

    def get_weekly_report(self) -> dict:
        """Gets the weekly report as a dict (JSON-compatible)."""
        xml_string = self._legacy.generate_weekly_report()
        return self._xml_to_dict(xml_string)

    def get_all_reports(self) -> list[dict]:
        """Gets all available reports as a list of dicts."""
        return [self.get_daily_report(), self.get_weekly_report()]

    def _xml_to_dict(self, xml_string: str) -> dict:
        """Converts an XML report string to a dict matching the expected format."""
        root = ET.fromstring(xml_string)

        # Extract report_id and timestamp
        report_id = root.find("report_id").text
        timestamp = root.find("timestamp").text

        # Extract metrics into a flat dict
        metrics = {}
        for metric_elem in root.findall(".//metric"):
            name = metric_elem.get("name")
            value = int(metric_elem.get("value"))
            metrics[name] = value

        return {
            "report_id": report_id,
            "timestamp": timestamp,
            "metrics": metrics,
        }
```

### Using the Adapter

```python
def main():
    # The legacy system (cannot modify)
    legacy = LegacyReportingSystem()

    # The adapter (bridges the gap)
    adapter = XMLToJSONReportAdapter(legacy)

    # The modern service (expects dicts)
    analytics = AnalyticsService()

    # Now they work together seamlessly
    print("=== Daily Report ===")
    daily = adapter.get_daily_report()
    analytics.process_report(daily)

    print("\n=== Weekly Report ===")
    weekly = adapter.get_weekly_report()
    analytics.process_report(weekly)

    print("\n=== Aggregated Summary ===")
    all_reports = adapter.get_all_reports()
    summary = analytics.aggregate_reports(all_reports)
    print(f"Total reports: {summary['report_count']}")
    for metric, total in summary['summary'].items():
        print(f"  {metric}: {total}")


if __name__ == "__main__":
    main()
```

**Output:**

```
=== Daily Report ===
Processing report: RPT-2024-001
  page_views: 15234
  unique_visitors: 4521
  bounce_rate: 34
  avg_session_minutes: 7
  Generated at: 2024-01-15T10:30:00Z

=== Weekly Report ===
Processing report: RPT-2024-W03
  page_views: 98432
  unique_visitors: 28910
  bounce_rate: 31
  avg_session_minutes: 8
  Generated at: 2024-01-21T00:00:00Z

=== Aggregated Summary ===
Total reports: 2
  page_views: 113666
  unique_visitors: 33431
  bounce_rate: 65
  avg_session_minutes: 15
```

---

## Real-World Backend Use Cases

### Use Case 1: Third-Party API Integration

You build a notification service with a clean `NotificationSender` interface. Later, you need to integrate with Twilio (SMS), SendGrid (email), and Firebase (push notifications). Each has a completely different API. You write an adapter for each:

```
┌───────────────────┐
│ NotificationSender│
│   (interface)     │
└────────┬──────────┘
         │
    ┌────┴────────────────────────────────────┐
    │              │                           │
┌───┴────────┐  ┌──┴──────────┐  ┌────────────┴──┐
│TwilioAdapter│ │SendGridAdapter│ │FirebaseAdapter │
│            │  │              │  │               │
│wraps Twilio│  │wraps SendGrid│  │wraps Firebase │
│   SDK      │  │    SDK       │  │     SDK       │
└────────────┘  └──────────────┘  └───────────────┘
```

### Use Case 2: Legacy System Migration

You are migrating from a monolith to microservices. During the transition, some services still call the monolith's database directly. You write adapters that expose the monolith's data through the new microservice interfaces:

```
┌──────────────────┐          ┌──────────────────┐
│  New Microservice │         │  Legacy Monolith  │
│  UserService API  │         │  UserDAO          │
│                  │         │                  │
│  getUser(id)     │         │  findByPK(table,  │
│  createUser(dto) │         │    column, value) │
│  updateUser(dto) │         │  insertRow(table, │
└────────┬─────────┘         │    data)          │
         │                    └────────┬─────────┘
         │ implements                   │ delegates to
    ┌────┴────────────────┐            │
    │ LegacyUserAdapter   │────────────┘
    │                     │
    │ Translates clean    │
    │ API calls to raw    │
    │ monolith queries    │
    └─────────────────────┘
```

### Use Case 3: Database Driver Abstraction

Your application uses a `DataStore` interface. You need to support PostgreSQL, MongoDB, and Redis. Each driver has different APIs:

```java
public interface DataStore {
    void save(String key, Object value);
    Object find(String key);
    void delete(String key);
}

public class MongoAdapter implements DataStore {
    private MongoCollection<Document> collection;

    @Override
    public void save(String key, Object value) {
        // Translates to MongoDB's insertOne / replaceOne
        Document doc = new Document("_id", key).append("data", value);
        collection.replaceOne(eq("_id", key), doc, new ReplaceOptions().upsert(true));
    }

    @Override
    public Object find(String key) {
        // Translates to MongoDB's find
        Document doc = collection.find(eq("_id", key)).first();
        return doc != null ? doc.get("data") : null;
    }

    @Override
    public void delete(String key) {
        collection.deleteOne(eq("_id", key));
    }
}
```

---

## When to Use / When NOT to Use

### Use the Adapter Pattern When:

- You need to use an existing class whose interface does not match what you need
- You want to create a reusable class that cooperates with unrelated classes
- You need to integrate a third-party library or legacy system
- You are migrating from one API to another and need a transition layer
- You want to isolate your code from external dependencies for easier testing

### Do NOT Use the Adapter Pattern When:

- You can simply modify the existing interface (and it is your code)
- The interfaces are already compatible -- do not add unnecessary layers
- You need to add new behavior, not just translate interfaces (use Decorator instead)
- The adaptation is trivial -- a simple method call does not need a full adapter class
- You are adapting too many things -- if everything needs an adapter, rethink your architecture

---

## Common Mistakes

### Mistake 1: Making the Adapter Too Smart

```java
// BAD: The adapter is doing business logic, not just translating
public class BadAdapter implements PaymentProcessor {
    @Override
    public PaymentResult processPayment(String customerId, double amount, String currency) {
        // Adapter should NOT validate business rules
        if (amount > 10000) {
            throw new IllegalArgumentException("Amount too high");
        }
        // Adapter should NOT apply discounts
        double discountedAmount = amount * 0.95;
        return convertResult(legacy.makePayment(buildXml(customerId, discountedAmount, currency)));
    }
}

// GOOD: The adapter only translates between interfaces
public class GoodAdapter implements PaymentProcessor {
    @Override
    public PaymentResult processPayment(String customerId, double amount, String currency) {
        String xml = buildXml(customerId, amount, currency);
        int legacyResult = legacy.makePayment(xml);
        return convertResult(legacyResult);
    }
}
```

An adapter translates. It does not add business logic.

### Mistake 2: Leaking the Adaptee's Interface

```java
// BAD: Exposing legacy details through the adapter
public class LeakyAdapter implements PaymentProcessor {
    public LegacyPaymentGateway getLegacyGateway() {
        return this.legacyGateway; // Clients can bypass the adapter
    }

    public int getRawLegacyCode(String transactionId) {
        return this.legacyGateway.getPaymentInfo(/* ... */); // Legacy types leak out
    }
}
```

If clients can access the adaptee directly, the adapter is pointless.

### Mistake 3: Creating One Adapter per Method Instead of per Interface

```java
// BAD: Separate adapter for each operation
public class PaymentAdapter { /* ... */ }
public class StatusAdapter { /* ... */ }
public class RefundAdapter { /* ... */ }

// GOOD: One adapter per incompatible interface
public class LegacyPaymentAdapter implements PaymentProcessor {
    // Handles all payment operations in one place
}
```

---

## Best Practices

1. **One adapter per incompatible interface.** Group related translations together.

2. **Keep adapters thin.** Translation logic only. No business rules, no validation, no side effects beyond what the adaptee does.

3. **Use composition over inheritance.** Object adapters (wrapping via a field) are more flexible than class adapters (extending the adaptee).

4. **Name adapters clearly.** `LegacyPaymentAdapter`, `TwilioNotificationAdapter`, `MongoDataStoreAdapter`. The name should say what is being adapted.

5. **Write integration tests for adapters.** Adapters are boundary code. Test that the translation is correct, especially edge cases (null values, empty results, error codes).

6. **Consider a two-way adapter** when both systems need to communicate. Sometimes you need to translate in both directions.

7. **Document the mapping.** A comment or table showing which target method maps to which adaptee method helps the next developer understand the translation.

---

## Quick Summary

The Adapter pattern wraps an existing class with a new interface, allowing incompatible classes to work together without modifying either one. It acts as a translator between two interfaces, just like a power plug adapter lets you use a US device in a European outlet.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client     │────>│   Adapter   │────>│   Adaptee   │
│ (your code)  │     │ (translator)│     │ (legacy/3rd │
│              │     │             │     │   party)    │
│ Calls target │     │ Implements  │     │ Has its own │
│ interface    │     │ target,     │     │ interface   │
│              │     │ wraps       │     │             │
│              │     │ adaptee     │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Key Points

- The Adapter pattern converts the interface of a class into another interface that clients expect
- Object adapters use composition (preferred); class adapters use inheritance
- Adapters should be thin -- they translate, they do not add business logic
- The pattern is essential for integrating third-party libraries and legacy systems
- Name your adapters clearly: describe what is being adapted
- Keep the adaptee hidden behind the adapter -- do not leak its interface
- Adapters make your code testable by allowing you to mock external dependencies

---

## Practice Questions

1. You have a `FileStorage` interface with `upload(filename, bytes)` and `download(filename)` methods. You need to integrate with an AWS S3 SDK that uses `putObject(PutObjectRequest)` and `getObject(GetObjectRequest)`. Sketch the adapter class. What translations does it perform?

2. Your team is debating whether to use a class adapter or an object adapter. The adaptee has several protected methods that contain useful logic. Which approach would you recommend, and why?

3. A colleague suggests putting input validation inside the adapter (for example, checking that the payment amount is positive before calling the legacy system). Is this a good idea? Why or why not?

4. You have three different payment gateways, each with its own SDK. How would the Adapter pattern help you support all three? Draw the class diagram.

5. How does the Adapter pattern improve testability? Give a concrete example of how you would unit test a service that uses a `PaymentProcessor` without needing the actual legacy system.

---

## Exercises

### Exercise 1: Build a Temperature Sensor Adapter

You have a `TemperatureSensor` interface that returns temperature in Celsius. You receive a third-party sensor library that only returns Fahrenheit with a different method signature:

```java
// Your interface
public interface TemperatureSensor {
    double readCelsius();
    String getSensorId();
}

// Third-party library (cannot modify)
public class FahrenheitSensor {
    public float getTemperatureF() { return 72.5f; }
    public int getDeviceCode() { return 1042; }
}
```

Write a `FahrenheitSensorAdapter` that makes `FahrenheitSensor` work with your `TemperatureSensor` interface. Include the Fahrenheit-to-Celsius conversion.

### Exercise 2: Python REST-to-GraphQL Adapter

You have a `DataFetcher` protocol that uses REST-style calls:

```python
class DataFetcher(Protocol):
    def get(self, endpoint: str, params: dict) -> dict: ...
    def post(self, endpoint: str, data: dict) -> dict: ...
```

Write a `GraphQLAdapter` that translates these REST-style calls into GraphQL queries against a GraphQL client. For `get("/users", {"id": 5})`, it should build and execute a GraphQL query.

### Exercise 3: Multi-Adapter Registry

Design a system where you can register multiple adapters for different legacy systems and select the right one at runtime based on a configuration flag. Use the Factory pattern (from Chapter 3) together with the Adapter pattern.

---

## What Is Next?

You now know how to make incompatible interfaces work together. But what if you want to add new behavior to an existing object without modifying it? What if you want to layer logging on top of caching on top of authentication -- all without changing the original class?

In the next chapter, you will learn the **Decorator pattern**, which lets you wrap objects with new behavior like Russian nesting dolls. Where the Adapter changes an interface, the Decorator enhances it.
