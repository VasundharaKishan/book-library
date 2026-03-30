# Chapter 3: The Factory Method Pattern

## What You Will Learn

- What the Factory Method pattern is and the problem it solves
- The difference between Simple Factory and Factory Method
- How to implement Factory Method in Java with a notification system example
- How to implement Factory Method in Python with a payment processing example
- How Spring's `@Bean` annotation acts as a factory method
- How Factory Method applies the Open/Closed Principle
- When to use Factory Method and when simpler approaches are better

## Why This Chapter Matters

Every backend system creates objects. You create database connections, HTTP clients, notification senders, payment processors, serializers, and hundreds of other objects. The question is not whether you create objects but how you create them.

When your code is tightly coupled to concrete classes, adding a new type means modifying existing code. Modify existing code, and you risk breaking what already works. The Factory Method pattern breaks this coupling. It lets subclasses decide which class to instantiate, so you can add new types without touching a single line of existing code.

This is the Open/Closed Principle in action, and it is one of the most frequently used patterns in production backend systems.

---

## The Problem

Imagine you are building a notification service. It starts simple: just send emails.

**Before (Tightly Coupled) - Java:**

```java
public class NotificationService {

    public void send(String type, String recipient, String message) {
        if ("email".equals(type)) {
            System.out.println("Connecting to SMTP server...");
            System.out.println("Sending email to " + recipient);
            System.out.println("Subject: Notification");
            System.out.println("Body: " + message);

        } else if ("sms".equals(type)) {
            System.out.println("Connecting to SMS gateway...");
            System.out.println("Sending SMS to " + recipient);
            System.out.println("Message: " + message);

        } else if ("push".equals(type)) {
            System.out.println("Connecting to push service...");
            System.out.println("Sending push to device " + recipient);
            System.out.println("Payload: " + message);
        }
    }
}
```

**Before (Tightly Coupled) - Python:**

```python
class NotificationService:

    def send(self, notification_type: str, recipient: str, message: str):
        if notification_type == "email":
            print("Connecting to SMTP server...")
            print(f"Sending email to {recipient}")
            print(f"Subject: Notification")
            print(f"Body: {message}")

        elif notification_type == "sms":
            print("Connecting to SMS gateway...")
            print(f"Sending SMS to {recipient}")
            print(f"Message: {message}")

        elif notification_type == "push":
            print("Connecting to push service...")
            print(f"Sending push to device {recipient}")
            print(f"Payload: {message}")
```

What is wrong with this code?

```
PROBLEMS WITH THE IF/ELSE APPROACH:

1. OPEN/CLOSED VIOLATION
   Adding Slack notifications means modifying this class.
   Adding WhatsApp means modifying it again.
   Every new type = change existing, tested code.

2. SINGLE RESPONSIBILITY VIOLATION
   This one method knows how to send emails, SMS, and push.
   It has three reasons to change.

3. TESTING DIFFICULTY
   You cannot test email sending without also loading
   SMS and push code.

4. CODE GROWTH
   After 10 notification types, this method is 200+ lines.

   send()
   +-- if "email"     (30 lines)
   +-- if "sms"       (25 lines)
   +-- if "push"      (20 lines)
   +-- if "slack"     (35 lines)
   +-- if "whatsapp"  (30 lines)
   +-- if "teams"     (25 lines)
   +-- if "webhook"   (40 lines)
   +-- ...
```

---

## The Solution: Factory Method Pattern

The Factory Method pattern defines an interface for creating an object, but lets subclasses decide which class to instantiate. Factory Method lets a class defer instantiation to subclasses.

```
+---------------------------------------------------------------+
|                 FACTORY METHOD PATTERN                        |
+---------------------------------------------------------------+
|                                                               |
|  INTENT: Define an interface for creating an object, but let  |
|          subclasses decide which class to instantiate.         |
|                                                               |
|  CATEGORY: Creational                                         |
|                                                               |
+---------------------------------------------------------------+

  UML-like Structure:

  +-------------------------+          +---------------------+
  |     Creator             |          |     Product         |
  |  (abstract class)       |          |   (interface)       |
  +-------------------------+          +---------------------+
  | + factoryMethod():      |          | + send()            |
  |     Product  {abstract} |          | + validate()        |
  | + someOperation()       |          +---------------------+
  +-------------------------+                   ^
           ^                                    |
           |                          +---------+---------+
  +--------+--------+                |                   |
  |                 |         +------+------+    +-------+------+
  |  EmailCreator   |         | EmailNotif  |    | SMSNotif     |
  |  SMSCreator     |         +-------------+    +--------------+
  |  PushCreator    |
  +-----------------+

  The Creator declares the factory method.
  Each ConcreteCreator overrides it to return
  a different ConcreteProduct.
```

---

## Java Implementation: Notification System

### Step 1: Define the Product Interface

```java
/**
 * Product interface - all notification types implement this.
 */
public interface Notification {

    /**
     * Validate the recipient format for this notification type.
     * Email expects an email address, SMS expects a phone number, etc.
     */
    boolean validate(String recipient);

    /**
     * Send the notification to the recipient.
     */
    void send(String recipient, String message);

    /**
     * Return the notification type name for logging.
     */
    String getType();
}
```

### Step 2: Create Concrete Products

```java
/**
 * Concrete Product: Email notification.
 */
public class EmailNotification implements Notification {

    @Override
    public boolean validate(String recipient) {
        // Simple email validation
        boolean valid = recipient != null && recipient.contains("@");
        if (!valid) {
            System.out.println("Invalid email address: " + recipient);
        }
        return valid;
    }

    @Override
    public void send(String recipient, String message) {
        System.out.println("=== EMAIL NOTIFICATION ===");
        System.out.println("Connecting to SMTP server smtp.example.com:587");
        System.out.println("To: " + recipient);
        System.out.println("Subject: Notification");
        System.out.println("Body: " + message);
        System.out.println("Email sent successfully.");
    }

    @Override
    public String getType() {
        return "EMAIL";
    }
}
```

```java
/**
 * Concrete Product: SMS notification.
 */
public class SMSNotification implements Notification {

    @Override
    public boolean validate(String recipient) {
        boolean valid = recipient != null && recipient.matches("\\+?\\d{10,15}");
        if (!valid) {
            System.out.println("Invalid phone number: " + recipient);
        }
        return valid;
    }

    @Override
    public void send(String recipient, String message) {
        System.out.println("=== SMS NOTIFICATION ===");
        System.out.println("Connecting to Twilio API...");
        System.out.println("To: " + recipient);
        // SMS messages are limited to 160 characters
        String smsBody = message.length() > 160
            ? message.substring(0, 157) + "..."
            : message;
        System.out.println("Message: " + smsBody);
        System.out.println("SMS sent successfully.");
    }

    @Override
    public String getType() {
        return "SMS";
    }
}
```

```java
/**
 * Concrete Product: Push notification.
 */
public class PushNotification implements Notification {

    @Override
    public boolean validate(String recipient) {
        boolean valid = recipient != null && recipient.startsWith("device:");
        if (!valid) {
            System.out.println("Invalid device token: " + recipient);
        }
        return valid;
    }

    @Override
    public void send(String recipient, String message) {
        System.out.println("=== PUSH NOTIFICATION ===");
        System.out.println("Connecting to Firebase Cloud Messaging...");
        System.out.println("Device: " + recipient);
        System.out.println("Payload: {\"title\": \"Notification\", "
            + "\"body\": \"" + message + "\"}");
        System.out.println("Push notification sent successfully.");
    }

    @Override
    public String getType() {
        return "PUSH";
    }
}
```

### Step 3: Define the Creator (Factory Method)

```java
/**
 * Creator - declares the factory method.
 *
 * The key insight: the Creator does NOT know which concrete
 * Notification it will create. That decision is deferred to
 * subclasses.
 */
public abstract class NotificationCreator {

    /**
     * The Factory Method - subclasses override this to create
     * the appropriate Notification type.
     */
    public abstract Notification createNotification();

    /**
     * Business logic that uses the factory method.
     * This method does NOT change when new notification types
     * are added.
     */
    public void sendNotification(String recipient, String message) {
        // The factory method creates the right type
        Notification notification = createNotification();

        System.out.println("Preparing " + notification.getType()
            + " notification...");

        // Validate before sending
        if (!notification.validate(recipient)) {
            System.out.println("Notification not sent: "
                + "invalid recipient.");
            return;
        }

        // Send the notification
        notification.send(recipient, message);

        System.out.println("Notification logged to audit trail.");
    }
}
```

### Step 4: Create Concrete Creators

```java
public class EmailNotificationCreator extends NotificationCreator {
    @Override
    public Notification createNotification() {
        return new EmailNotification();
    }
}

public class SMSNotificationCreator extends NotificationCreator {
    @Override
    public Notification createNotification() {
        return new SMSNotification();
    }
}

public class PushNotificationCreator extends NotificationCreator {
    @Override
    public Notification createNotification() {
        return new PushNotification();
    }
}
```

### Step 5: Usage

```java
public class Main {
    public static void main(String[] args) {
        // The client code works with creators through the base class
        NotificationCreator emailCreator = new EmailNotificationCreator();
        NotificationCreator smsCreator = new SMSNotificationCreator();
        NotificationCreator pushCreator = new PushNotificationCreator();

        emailCreator.sendNotification(
            "user@example.com",
            "Your order has been shipped!"
        );

        System.out.println();

        smsCreator.sendNotification(
            "+15551234567",
            "Your order has been shipped!"
        );

        System.out.println();

        pushCreator.sendNotification(
            "device:abc123xyz",
            "Your order has been shipped!"
        );
    }
}
```

**Output:**

```
Preparing EMAIL notification...
=== EMAIL NOTIFICATION ===
Connecting to SMTP server smtp.example.com:587
To: user@example.com
Subject: Notification
Body: Your order has been shipped!
Email sent successfully.
Notification logged to audit trail.

Preparing SMS notification...
=== SMS NOTIFICATION ===
Connecting to Twilio API...
To: +15551234567
Message: Your order has been shipped!
SMS sent successfully.
Notification logged to audit trail.

Preparing PUSH notification...
=== PUSH NOTIFICATION ===
Connecting to Firebase Cloud Messaging...
Device: device:abc123xyz
Payload: {"title": "Notification", "body": "Your order has been shipped!"}
Push notification sent successfully.
Notification logged to audit trail.
```

### The Open/Closed Principle in Action

Now, suppose you need to add Slack notifications. Here is what you change:

```
FILES MODIFIED:  0   (zero!)
FILES CREATED:   2   (SlackNotification.java, SlackNotificationCreator.java)

BEFORE                              AFTER
+---------------------+            +---------------------+
| Notification (intf) |            | Notification (intf) |  <-- unchanged
+---------------------+            +---------------------+
| EmailNotification   |            | EmailNotification   |  <-- unchanged
| SMSNotification     |            | SMSNotification     |  <-- unchanged
| PushNotification    |            | PushNotification    |  <-- unchanged
+---------------------+            | SlackNotification   |  <-- NEW
                                   +---------------------+
+---------------------+            +---------------------+
| NotificationCreator |            | NotificationCreator |  <-- unchanged
+---------------------+            +---------------------+
| EmailCreator        |            | EmailCreator        |  <-- unchanged
| SMSCreator          |            | SMSCreator          |  <-- unchanged
| PushCreator         |            | PushCreator         |  <-- unchanged
+---------------------+            | SlackCreator        |  <-- NEW
                                   +---------------------+
```

```java
// NEW FILE: SlackNotification.java
public class SlackNotification implements Notification {
    @Override
    public boolean validate(String recipient) {
        return recipient != null && recipient.startsWith("#");
    }

    @Override
    public void send(String recipient, String message) {
        System.out.println("=== SLACK NOTIFICATION ===");
        System.out.println("Channel: " + recipient);
        System.out.println("Message: " + message);
    }

    @Override
    public String getType() {
        return "SLACK";
    }
}

// NEW FILE: SlackNotificationCreator.java
public class SlackNotificationCreator extends NotificationCreator {
    @Override
    public Notification createNotification() {
        return new SlackNotification();
    }
}
```

Zero existing files changed. Zero risk of breaking existing functionality. This is the power of Factory Method.

---

## Python Implementation: Payment Processing

```python
from abc import ABC, abstractmethod


# ---- Product Interface ----

class PaymentProcessor(ABC):
    """Abstract product: all payment processors implement this."""

    @abstractmethod
    def validate_payment(self, amount: float) -> bool:
        """Check if the payment details are valid."""
        pass

    @abstractmethod
    def process(self, amount: float, currency: str) -> dict:
        """Process the payment and return a result."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the processor name for logging."""
        pass


# ---- Concrete Products ----

class StripeProcessor(PaymentProcessor):
    """Concrete product: Stripe payment processing."""

    def validate_payment(self, amount: float) -> bool:
        if amount <= 0:
            print(f"Stripe: Invalid amount ${amount:.2f}")
            return False
        if amount > 999999.99:
            print("Stripe: Amount exceeds maximum")
            return False
        return True

    def process(self, amount: float, currency: str) -> dict:
        print(f"Stripe: Connecting to api.stripe.com...")
        print(f"Stripe: Processing ${amount:.2f} {currency}")
        print(f"Stripe: Payment successful!")
        return {
            "status": "success",
            "processor": "stripe",
            "transaction_id": "stripe_txn_abc123",
            "amount": amount,
            "currency": currency,
        }

    def get_name(self) -> str:
        return "Stripe"


class PayPalProcessor(PaymentProcessor):
    """Concrete product: PayPal payment processing."""

    def validate_payment(self, amount: float) -> bool:
        if amount <= 0:
            print(f"PayPal: Invalid amount ${amount:.2f}")
            return False
        if amount > 10000.00:
            print("PayPal: Amount exceeds single transaction limit")
            return False
        return True

    def process(self, amount: float, currency: str) -> dict:
        print(f"PayPal: Connecting to api.paypal.com...")
        print(f"PayPal: Creating payment for ${amount:.2f} {currency}")
        print(f"PayPal: Payment authorized!")
        return {
            "status": "success",
            "processor": "paypal",
            "transaction_id": "paypal_txn_xyz789",
            "amount": amount,
            "currency": currency,
        }

    def get_name(self) -> str:
        return "PayPal"


class SquareProcessor(PaymentProcessor):
    """Concrete product: Square payment processing."""

    def validate_payment(self, amount: float) -> bool:
        if amount <= 0:
            print(f"Square: Invalid amount ${amount:.2f}")
            return False
        return True

    def process(self, amount: float, currency: str) -> dict:
        print(f"Square: Connecting to connect.squareup.com...")
        print(f"Square: Charging ${amount:.2f} {currency}")
        print(f"Square: Charge completed!")
        return {
            "status": "success",
            "processor": "square",
            "transaction_id": "square_txn_def456",
            "amount": amount,
            "currency": currency,
        }

    def get_name(self) -> str:
        return "Square"


# ---- Creator (Factory Method) ----

class PaymentService(ABC):
    """
    Creator class with the factory method.

    The key insight: PaymentService contains business logic
    (validate, process, log) but does NOT know which specific
    PaymentProcessor it will use.
    """

    @abstractmethod
    def create_processor(self) -> PaymentProcessor:
        """Factory method - subclasses decide which processor to create."""
        pass

    def charge(self, amount: float, currency: str = "USD") -> dict:
        """
        Business logic that uses the factory method.
        This method NEVER changes when new processors are added.
        """
        processor = self.create_processor()
        print(f"\n--- Processing payment via {processor.get_name()} ---")

        # Validate
        if not processor.validate_payment(amount):
            return {"status": "failed", "reason": "validation_error"}

        # Process
        result = processor.process(amount, currency)

        # Log (common to all processors)
        print(f"Payment logged: {result['transaction_id']}")

        return result


# ---- Concrete Creators ----

class StripePaymentService(PaymentService):
    def create_processor(self) -> PaymentProcessor:
        return StripeProcessor()


class PayPalPaymentService(PaymentService):
    def create_processor(self) -> PaymentProcessor:
        return PayPalProcessor()


class SquarePaymentService(PaymentService):
    def create_processor(self) -> PaymentProcessor:
        return SquareProcessor()
```

**Usage and output:**

```python
def main():
    # Client code works with the base PaymentService class
    services = [
        StripePaymentService(),
        PayPalPaymentService(),
        SquarePaymentService(),
    ]

    for service in services:
        result = service.charge(49.99)
        print(f"Result: {result['status']}\n")


if __name__ == "__main__":
    main()
```

```
Output:

--- Processing payment via Stripe ---
Stripe: Connecting to api.stripe.com...
Stripe: Processing $49.99 USD
Stripe: Payment successful!
Payment logged: stripe_txn_abc123
Result: success

--- Processing payment via PayPal ---
PayPal: Connecting to api.paypal.com...
PayPal: Creating payment for $49.99 USD
PayPal: Payment authorized!
Payment logged: paypal_txn_xyz789
Result: success

--- Processing payment via Square ---
Square: Connecting to connect.squareup.com...
Square: Charging $49.99 USD
Square: Charge completed!
Payment logged: square_txn_def456
Result: success
```

---

## Factory Method vs. Simple Factory

Many developers confuse Factory Method with Simple Factory. They are different.

### Simple Factory (Not a GoF Pattern)

A Simple Factory is a single class with a method that creates objects based on a parameter. It is useful but does not follow the Open/Closed Principle.

```java
// Simple Factory - a single class with creation logic
public class NotificationFactory {

    public static Notification create(String type) {
        switch (type) {
            case "email": return new EmailNotification();
            case "sms":   return new SMSNotification();
            case "push":  return new PushNotification();
            default:
                throw new IllegalArgumentException(
                    "Unknown notification type: " + type
                );
        }
    }
}

// Usage:
Notification n = NotificationFactory.create("email");
n.send("user@example.com", "Hello!");
```

```python
# Simple Factory in Python
class NotificationFactory:

    @staticmethod
    def create(notification_type: str) -> Notification:
        factories = {
            "email": EmailNotification,
            "sms": SMSNotification,
            "push": PushNotification,
        }
        creator = factories.get(notification_type)
        if creator is None:
            raise ValueError(f"Unknown type: {notification_type}")
        return creator()

# Usage:
n = NotificationFactory.create("email")
n.send("user@example.com", "Hello!")
```

### Side-by-Side Comparison

```
+-------------------------------+-------------------------------+
|       SIMPLE FACTORY          |       FACTORY METHOD          |
+-------------------------------+-------------------------------+
|                               |                               |
| One class creates all types   | Each type has its own creator |
|                               |                               |
| Uses if/else or switch        | Uses inheritance/polymorphism |
|                               |                               |
| Adding a type = modify the    | Adding a type = add new class |
| factory (violates OCP)        | (follows OCP)                 |
|                               |                               |
| Simpler to understand         | More classes, more flexible   |
|                               |                               |
| Good for: few types that      | Good for: many types, types   |
| rarely change                 | added frequently, frameworks  |
|                               |                               |
+-------------------------------+-------------------------------+

SIMPLE FACTORY:

  +-----------------------+
  | NotificationFactory   |
  +-----------------------+         +------------------+
  | + create(type): Notif |-------->| Notification     |
  +-----------------------+         +------------------+
  | if "email" -> Email   |              ^    ^    ^
  | if "sms"   -> SMS     |              |    |    |
  | if "push"  -> Push    |         Email SMS Push
  +-----------------------+

FACTORY METHOD:

  +---------------------+         +------------------+
  | NotificationCreator |         | Notification     |
  | {abstract}          |-------->| {interface}      |
  +---------------------+         +------------------+
  | + create(): Notif   |              ^    ^    ^
  +---------------------+              |    |    |
       ^      ^      ^            Email SMS Push
       |      |      |
  Email   SMS    Push
  Creator Creator Creator
```

**When to use Simple Factory:** You have a small, stable set of types (fewer than 5) that rarely changes. The simplicity is worth the OCP violation.

**When to use Factory Method:** You expect new types to be added over time, you want to follow the Open/Closed Principle, or you are building a framework/library.

---

## Spring: @Bean as Factory Method

In Spring, the `@Bean` annotation on a method is essentially a factory method. Spring calls that method to create the bean.

```java
@Configuration
public class AppConfig {

    // This is a factory method - Spring calls it to create the bean
    @Bean
    public PaymentProcessor paymentProcessor() {
        String provider = System.getenv("PAYMENT_PROVIDER");

        switch (provider) {
            case "stripe":
                return new StripeProcessor("sk_live_xxx");
            case "paypal":
                return new PayPalProcessor("client_id", "secret");
            default:
                return new StripeProcessor("sk_test_xxx");
        }
    }

    // Another factory method
    @Bean
    public NotificationSender notificationSender() {
        return new EmailNotificationSender(
            smtpHost(),
            smtpPort()
        );
    }

    @Bean
    public String smtpHost() {
        return System.getenv("SMTP_HOST");
    }

    @Bean
    public int smtpPort() {
        return Integer.parseInt(
            System.getenv().getOrDefault("SMTP_PORT", "587")
        );
    }
}
```

```java
@Service
public class CheckoutService {

    private final PaymentProcessor processor;

    // Spring injects the object created by the @Bean factory method
    public CheckoutService(PaymentProcessor processor) {
        this.processor = processor;
    }

    public void checkout(Order order) {
        processor.process(order.getTotal(), "USD");
    }
}
```

```
Spring's Factory Method flow:

  @Configuration class
  +---------------------------+
  | @Bean                     |
  | paymentProcessor()  ------+---> creates StripeProcessor
  +---------------------------+            |
                                           v
  @Service class                    +--------------+
  +---------------------------+    | Spring       |
  | CheckoutService           |<---| Container    |
  | (PaymentProcessor proc)   |    | (injects)    |
  +---------------------------+    +--------------+

  The CheckoutService never knows whether it gets
  Stripe, PayPal, or Square. It depends on the
  PaymentProcessor abstraction.
```

---

## Real-World Backend Use Case: Log Exporter

Different environments need different log export formats. Development uses console output. Staging uses JSON files. Production uses a centralized logging service.

```java
// Product interface
public interface LogExporter {
    void export(List<LogEntry> entries);
    String getFormat();
}

// Concrete products
public class ConsoleLogExporter implements LogExporter {
    public void export(List<LogEntry> entries) {
        entries.forEach(e -> System.out.println(
            e.getTimestamp() + " | " + e.getLevel()
            + " | " + e.getMessage()
        ));
    }
    public String getFormat() { return "CONSOLE"; }
}

public class JsonFileLogExporter implements LogExporter {
    public void export(List<LogEntry> entries) {
        // Write entries as JSON to a file
        String json = new ObjectMapper()
            .writeValueAsString(entries);
        Files.writeString(Path.of("logs/app.json"), json);
    }
    public String getFormat() { return "JSON_FILE"; }
}

public class CloudLogExporter implements LogExporter {
    public void export(List<LogEntry> entries) {
        // Send entries to centralized logging (e.g., Datadog)
        httpClient.post("https://api.datadog.com/v1/logs", entries);
    }
    public String getFormat() { return "CLOUD"; }
}

// Creator
public abstract class LogManager {

    public abstract LogExporter createExporter();

    public void flush(List<LogEntry> entries) {
        LogExporter exporter = createExporter();
        System.out.println("Exporting " + entries.size()
            + " entries via " + exporter.getFormat());
        exporter.export(entries);
    }
}

// Concrete creators - one per environment
public class DevLogManager extends LogManager {
    public LogExporter createExporter() {
        return new ConsoleLogExporter();
    }
}

public class StagingLogManager extends LogManager {
    public LogExporter createExporter() {
        return new JsonFileLogExporter();
    }
}

public class ProductionLogManager extends LogManager {
    public LogExporter createExporter() {
        return new CloudLogExporter();
    }
}
```

```python
# Python equivalent with environment-based selection

from abc import ABC, abstractmethod
from typing import List
import json
import os


class LogEntry:
    def __init__(self, timestamp: str, level: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.message = message


class LogExporter(ABC):
    @abstractmethod
    def export(self, entries: List[LogEntry]):
        pass

    @abstractmethod
    def get_format(self) -> str:
        pass


class ConsoleLogExporter(LogExporter):
    def export(self, entries: List[LogEntry]):
        for e in entries:
            print(f"{e.timestamp} | {e.level} | {e.message}")

    def get_format(self) -> str:
        return "CONSOLE"


class JsonFileLogExporter(LogExporter):
    def export(self, entries: List[LogEntry]):
        data = [vars(e) for e in entries]
        with open("logs/app.json", "w") as f:
            json.dump(data, f, indent=2)

    def get_format(self) -> str:
        return "JSON_FILE"


class LogManager(ABC):
    @abstractmethod
    def create_exporter(self) -> LogExporter:
        pass

    def flush(self, entries: List[LogEntry]):
        exporter = self.create_exporter()
        print(f"Exporting {len(entries)} entries "
              f"via {exporter.get_format()}")
        exporter.export(entries)


class DevLogManager(LogManager):
    def create_exporter(self) -> LogExporter:
        return ConsoleLogExporter()


class StagingLogManager(LogManager):
    def create_exporter(self) -> LogExporter:
        return JsonFileLogExporter()


# Select manager based on environment
def get_log_manager() -> LogManager:
    env = os.getenv("APP_ENV", "development")
    managers = {
        "development": DevLogManager,
        "staging": StagingLogManager,
    }
    manager_class = managers.get(env, DevLogManager)
    return manager_class()
```

---

## When to Use / When NOT to Use

```
+----------------------------------+----------------------------------+
|  USE FACTORY METHOD WHEN         |  DO NOT USE WHEN                 |
+----------------------------------+----------------------------------+
|                                  |                                  |
| - You do not know ahead of time  | - You have only one concrete     |
|   which exact class to create    |   class and no plans for more    |
|                                  |                                  |
| - You want subclasses to specify | - The creation logic is trivial  |
|   which objects to create        |   (just `new SomeClass()`)       |
|                                  |                                  |
| - You need to follow the         | - Adding the pattern makes the   |
|   Open/Closed Principle          |   code harder to understand      |
|                                  |                                  |
| - You are building a framework   | - You have fewer than 3 types    |
|   or library where users add     |   and they rarely change         |
|   their own types                |   (Simple Factory is enough)     |
|                                  |                                  |
| - Different environments need    | - You are over-engineering a     |
|   different implementations      |   simple creation scenario       |
|   (dev/staging/prod)             |                                  |
|                                  |                                  |
+----------------------------------+----------------------------------+
```

---

## Common Mistakes

1. **Using Factory Method when Simple Factory is enough.** If you have three notification types and they have not changed in two years, a Simple Factory is simpler and perfectly fine.

2. **Creating a factory for every class.** Not every object needs a factory. If there is only one implementation and no reason to expect others, use `new` directly.

3. **Putting too much logic in the factory method.** The factory method should create an object and return it. Business logic belongs in the Creator's other methods or in the Product itself.

4. **Forgetting to program to the interface.** If your client code references `EmailNotification` directly instead of `Notification`, the factory provides no benefit.

5. **Confusing Factory Method with Abstract Factory.** Factory Method creates ONE product. Abstract Factory creates FAMILIES of related products. We cover Abstract Factory in the next chapter.

---

## Best Practices

1. **Start with Simple Factory, evolve to Factory Method.** Begin with the simplest approach. When you add the third or fourth type, refactor to Factory Method.

2. **Name your factories clearly.** `NotificationCreator` is better than `NotificationFactory` for the Factory Method pattern, because it emphasizes the creator/product relationship.

3. **Use the Product interface everywhere.** Client code should never reference concrete product classes. Always work with the `Notification` or `PaymentProcessor` interface.

4. **Combine with Dependency Injection.** In Spring or similar frameworks, let the DI container choose the concrete creator based on configuration. This moves the decision out of code entirely.

5. **Keep the factory method simple.** It should do one thing: create and return a product. If it needs complex setup, move that to the product's constructor or an initialization method.

---

## Quick Summary

| Aspect | Details |
|--------|---------|
| Pattern name | Factory Method |
| Category | Creational |
| Intent | Let subclasses decide which class to instantiate |
| Problem it solves | Tight coupling to concrete classes; if/else chains for object creation |
| Key principle | Open/Closed: add new types without modifying existing code |
| Participants | Creator (abstract), ConcreteCreator, Product (interface), ConcreteProduct |
| vs. Simple Factory | Simple Factory uses one class with if/else; Factory Method uses inheritance |
| Spring equivalent | `@Bean` methods in `@Configuration` classes |

---

## Key Points

1. Factory Method lets subclasses decide which class to instantiate. The Creator defines the factory method signature; ConcreteCreators provide the implementation.

2. The main benefit is the Open/Closed Principle. Adding a new product type requires only new classes, never modifying existing ones.

3. Simple Factory is not a GoF pattern but is useful for simple cases. Upgrade to Factory Method when you need extensibility.

4. In Spring, `@Bean` methods are factory methods. The framework calls them to create beans, and the rest of your code depends on abstractions.

5. Always program to the Product interface. If client code references concrete classes, the factory adds complexity without benefit.

---

## Practice Questions

1. Explain the difference between Simple Factory and Factory Method. When would you choose one over the other?

2. How does the Factory Method pattern support the Open/Closed Principle? Walk through a specific example of adding a new type.

3. A developer writes a `NotificationFactory` with a 500-line `create()` method containing 20 if/else branches. What problems does this cause, and how would you refactor it?

4. Why is it important for client code to depend on the Product interface rather than concrete product classes? What breaks if it does not?

5. How does Spring's `@Bean` annotation relate to the Factory Method pattern?

---

## Exercises

### Exercise 1: Serialization Factory

Create a Factory Method implementation for data serialization. Support JSON, XML, and CSV formats. Each serializer should implement a `Serializer` interface with `serialize(data)` and `deserialize(text)` methods. Implement in both Java and Python.

### Exercise 2: Simple Factory to Factory Method Refactoring

Start with this Simple Factory and refactor it to use the Factory Method pattern:

```python
class CacheFactory:
    @staticmethod
    def create(cache_type: str):
        if cache_type == "memory":
            return InMemoryCache()
        elif cache_type == "redis":
            return RedisCache("localhost", 6379)
        elif cache_type == "memcached":
            return MemcachedCache("localhost", 11211)
        else:
            raise ValueError(f"Unknown cache type: {cache_type}")
```

### Exercise 3: Environment-Aware Factory

Build a Factory Method system that creates different database connection objects based on the environment (development, testing, production). Development should use SQLite, testing should use an in-memory H2/SQLite database, and production should use PostgreSQL. The factory should read the environment from a configuration source.

---

## What Is Next?

In the next chapter, we level up from Factory Method to Abstract Factory. While Factory Method creates a single product, Abstract Factory creates entire families of related products. You will see how to build a database abstraction layer that creates matched sets of connections, queries, and migrations for PostgreSQL and MySQL, and a cloud provider factory for AWS and GCP that creates consistent sets of storage, compute, and queue services.
