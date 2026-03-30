# Chapter 11: The Bridge Pattern

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand the Bridge pattern and the class explosion problem it solves
- Recognize when two independent dimensions of variation create a multiplication of classes
- Separate abstraction from implementation so they can vary independently
- Build a Notification system in Java with `Notification` (Email/SMS) x `Urgency` (Normal/Urgent)
- Create a DataExporter system in Python with `Format` (CSV/JSON) x `Destination` (File/S3/FTP)
- Know when the Bridge pattern helps most and when it is overkill
- Distinguish Bridge from Adapter, Strategy, and other structural patterns

---

## Why This Chapter Matters

Imagine you are building a notification system for a backend application. You need to support different channels (Email, SMS, Push Notification) and different urgency levels (Normal, Urgent). The naive approach using inheritance looks like this:

```
                    Notification
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    EmailNotification  SMSNotification  PushNotification
         │               │               │
    ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
    │         │     │         │     │         │
  Normal   Urgent  Normal  Urgent  Normal  Urgent
  Email    Email   SMS     SMS     Push    Push
```

That is 6 classes for 2 dimensions (3 channels x 2 urgency levels). Now add a third urgency level (Critical). You need 9 classes. Add a fourth channel (Slack). You need 12 classes. Add a priority dimension (High/Medium/Low). You need **36 classes**.

This is the **class explosion problem**: when two or more independent dimensions of variation are combined through inheritance, the number of classes grows multiplicatively.

The Bridge pattern solves this by separating the two dimensions into independent hierarchies connected by composition:

```
  Abstraction                   Implementation
  (Urgency)                     (Channel)

  ┌──────────────┐              ┌──────────────┐
  │ Notification  │─────has-a──>│ MessageSender │
  └──────┬───────┘              └──────┬───────┘
         │                             │
    ┌────┴────┐                 ┌──────┼──────┐
    │         │                 │      │      │
  Normal   Urgent            Email   SMS    Push

  2 classes + 3 classes = 5 total (instead of 6)
  Add Critical: 3 + 3 = 6 (instead of 9)
  Add Slack: 3 + 4 = 7 (instead of 12)
```

Instead of multiplication, you get addition.

---

## The Problem

You are building a notification service for an e-commerce platform. Notifications need to be sent through different channels, and the formatting and behavior changes based on urgency. Without the Bridge pattern:

```java
// Class explosion: one class per combination
public class NormalEmailNotification extends Notification { }
public class UrgentEmailNotification extends Notification { }
public class NormalSMSNotification extends Notification { }
public class UrgentSMSNotification extends Notification { }
public class NormalPushNotification extends Notification { }
public class UrgentPushNotification extends Notification { }
// Adding Slack channel: 2 more classes
// Adding Critical urgency: 3 more classes (now 4 channels)
// Adding scheduled delivery: doubles everything
```

Each class is nearly identical to its siblings, with only small differences. This violates the DRY principle and makes maintenance painful.

---

## The Solution: Bridge Pattern

Separate the two dimensions into independent hierarchies and connect them with a bridge (composition).

```
┌────────────────────────────────────────────────────────────────┐
│                      Bridge Pattern Structure                   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│    Abstraction                          Implementation          │
│    (What to do)                         (How to do it)          │
│                                                                 │
│   ┌──────────────────┐    bridge     ┌──────────────────┐      │
│   │   Notification    │─────────────>│  MessageSender    │      │
│   │                  │   (has-a)     │  <<interface>>    │      │
│   │ + send(msg)      │              │                  │      │
│   │ + formatMessage()│              │ + sendMessage()  │      │
│   └────────┬─────────┘              └────────┬─────────┘      │
│            │                                  │                 │
│     ┌──────┴──────┐              ┌────────────┼──────────┐     │
│     │             │              │            │          │     │
│  ┌──┴──────┐  ┌───┴─────┐   ┌───┴──────┐ ┌──┴─────┐ ┌──┴──┐ │
│  │ Normal  │  │ Urgent  │   │ Email    │ │ SMS    │ │Push │ │
│  │Notif.   │  │ Notif.  │   │ Sender   │ │Sender │ │Send.│ │
│  └─────────┘  └─────────┘   └──────────┘ └────────┘ └─────┘ │
│                                                                 │
│   2 abstractions  +  3 implementations  =  5 classes           │
│   (instead of 2 x 3 = 6 with inheritance)                      │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Java Example: Notification System

### Step 1: The Implementation Interface (Message Channel)

```java
/**
 * The "implementation" side of the bridge.
 * Defines HOW a message is actually delivered.
 */
public interface MessageSender {
    void sendMessage(String recipient, String subject, String body);
    String getChannelName();
}
```

### Step 2: Concrete Implementations (Channels)

```java
public class EmailSender implements MessageSender {

    @Override
    public void sendMessage(String recipient, String subject, String body) {
        System.out.println("  [Email] To: " + recipient);
        System.out.println("  [Email] Subject: " + subject);
        System.out.println("  [Email] Body: " + body);
        System.out.println("  [Email] Sent via SMTP server\n");
    }

    @Override
    public String getChannelName() {
        return "EMAIL";
    }
}

public class SMSSender implements MessageSender {

    private static final int SMS_MAX_LENGTH = 160;

    @Override
    public void sendMessage(String recipient, String subject, String body) {
        // SMS has no subject; combine into one message
        String smsText = subject + ": " + body;
        if (smsText.length() > SMS_MAX_LENGTH) {
            smsText = smsText.substring(0, SMS_MAX_LENGTH - 3) + "...";
        }
        System.out.println("  [SMS] To: " + recipient);
        System.out.println("  [SMS] Message: " + smsText);
        System.out.println("  [SMS] Sent via SMS gateway\n");
    }

    @Override
    public String getChannelName() {
        return "SMS";
    }
}

public class PushNotificationSender implements MessageSender {

    @Override
    public void sendMessage(String recipient, String subject, String body) {
        System.out.println("  [Push] Device: " + recipient);
        System.out.println("  [Push] Title: " + subject);
        System.out.println("  [Push] Body: " + body.substring(0, Math.min(body.length(), 100)));
        System.out.println("  [Push] Sent via Firebase Cloud Messaging\n");
    }

    @Override
    public String getChannelName() {
        return "PUSH";
    }
}
```

### Step 3: The Abstraction (Notification with Urgency)

```java
/**
 * The "abstraction" side of the bridge.
 * Defines WHAT the notification does (formatting, behavior).
 * Delegates the HOW to the MessageSender.
 */
public abstract class Notification {

    protected final MessageSender sender; // <-- the bridge

    public Notification(MessageSender sender) {
        this.sender = sender;
    }

    /**
     * Send a notification. Subclasses define the formatting
     * and behavior; the sender defines the delivery channel.
     */
    public abstract void send(String recipient, String message);

    /**
     * Each urgency level formats the message differently.
     */
    protected abstract String formatSubject(String message);
    protected abstract String formatBody(String message);
}
```

### Step 4: Refined Abstractions (Urgency Levels)

```java
public class NormalNotification extends Notification {

    public NormalNotification(MessageSender sender) {
        super(sender);
    }

    @Override
    public void send(String recipient, String message) {
        System.out.println("--- Normal Notification via " + sender.getChannelName() + " ---");
        String subject = formatSubject(message);
        String body = formatBody(message);
        sender.sendMessage(recipient, subject, body);
    }

    @Override
    protected String formatSubject(String message) {
        return "Notification: " + message;
    }

    @Override
    protected String formatBody(String message) {
        return message + "\n\nThis is a standard notification. No action required.";
    }
}

public class UrgentNotification extends Notification {

    public UrgentNotification(MessageSender sender) {
        super(sender);
    }

    @Override
    public void send(String recipient, String message) {
        System.out.println("--- URGENT Notification via " + sender.getChannelName() + " ---");
        String subject = formatSubject(message);
        String body = formatBody(message);

        // Urgent: send immediately, no batching
        sender.sendMessage(recipient, subject, body);

        // Also log urgent notifications for monitoring
        System.out.println("  [Monitor] URGENT notification logged for recipient: "
            + recipient + "\n");
    }

    @Override
    protected String formatSubject(String message) {
        return "[URGENT] " + message;
    }

    @Override
    protected String formatBody(String message) {
        return "*** URGENT ACTION REQUIRED ***\n\n"
            + message
            + "\n\nPlease respond immediately.";
    }
}

public class CriticalNotification extends Notification {

    public CriticalNotification(MessageSender sender) {
        super(sender);
    }

    @Override
    public void send(String recipient, String message) {
        System.out.println("--- CRITICAL Notification via " + sender.getChannelName() + " ---");
        String subject = formatSubject(message);
        String body = formatBody(message);

        // Critical: send multiple times to ensure delivery
        sender.sendMessage(recipient, subject, body);

        // Escalate: also notify the on-call team
        System.out.println("  [Escalation] Paging on-call team for: " + message);
        System.out.println("  [Escalation] Creating incident ticket\n");
    }

    @Override
    protected String formatSubject(String message) {
        return "[CRITICAL - IMMEDIATE ACTION] " + message;
    }

    @Override
    protected String formatBody(String message) {
        return "***** CRITICAL ALERT *****\n\n"
            + message
            + "\n\nThis requires immediate attention. "
            + "On-call team has been notified.";
    }
}
```

### Step 5: Using the Bridge

```java
public class Main {
    public static void main(String[] args) {
        // Create senders (implementation dimension)
        MessageSender emailSender = new EmailSender();
        MessageSender smsSender = new SMSSender();
        MessageSender pushSender = new PushNotificationSender();

        // Combine any urgency with any channel
        Notification normalEmail = new NormalNotification(emailSender);
        normalEmail.send("alice@example.com", "Your order has shipped");

        Notification urgentSms = new UrgentNotification(smsSender);
        urgentSms.send("+1-555-0123", "Payment declined on order #4521");

        Notification criticalPush = new CriticalNotification(pushSender);
        criticalPush.send("device-token-abc", "Server cluster is down");

        // Easy to add new combinations without new classes
        Notification urgentEmail = new UrgentNotification(emailSender);
        urgentEmail.send("admin@example.com", "Database failover activated");
    }
}
```

**Output:**

```
--- Normal Notification via EMAIL ---
  [Email] To: alice@example.com
  [Email] Subject: Notification: Your order has shipped
  [Email] Body: Your order has shipped

This is a standard notification. No action required.
  [Email] Sent via SMTP server

--- URGENT Notification via SMS ---
  [SMS] To: +1-555-0123
  [SMS] Message: [URGENT] Payment declined on order #4521: *** URGENT ACTION REQUI...
  [SMS] Sent via SMS gateway

  [Monitor] URGENT notification logged for recipient: +1-555-0123

--- CRITICAL Notification via PUSH ---
  [Push] Device: device-token-abc
  [Push] Title: [CRITICAL - IMMEDIATE ACTION] Server cluster is down
  [Push] Body: ***** CRITICAL ALERT *****

Server cluster is down

This requires immediate attention
  [Push] Sent via Firebase Cloud Messaging

  [Escalation] Paging on-call team for: Server cluster is down
  [Escalation] Creating incident ticket

--- URGENT Notification via EMAIL ---
  [Email] To: admin@example.com
  [Email] Subject: [URGENT] Database failover activated
  [Email] Body: *** URGENT ACTION REQUIRED ***

Database failover activated

Please respond immediately.
  [Email] Sent via SMTP server

  [Monitor] URGENT notification logged for recipient: admin@example.com
```

### Before vs After

**Before (without Bridge) -- class explosion:**

```
NormalEmailNotification
NormalSMSNotification
NormalPushNotification
UrgentEmailNotification
UrgentSMSNotification
UrgentPushNotification
CriticalEmailNotification
CriticalSMSNotification
CriticalPushNotification

Total: 9 classes (3 urgency x 3 channels)
Adding Slack: 12 classes
Adding WhatsApp: 15 classes
```

**After (with Bridge) -- linear growth:**

```
Abstractions: NormalNotification, UrgentNotification, CriticalNotification (3)
Implementations: EmailSender, SMSSender, PushSender (3)

Total: 6 classes (3 + 3)
Adding Slack: 7 classes (3 + 4)
Adding WhatsApp: 8 classes (3 + 5)
```

```
  Classes needed (Urgency levels x Channels)

  Without Bridge (multiplication):
  Channels:    3     4     5     6     7
  Urgency=3:   9    12    15    18    21
  Urgency=4:  12    16    20    24    28
  Urgency=5:  15    20    25    30    35

  With Bridge (addition):
  Channels:    3     4     5     6     7
  Urgency=3:   6     7     8     9    10
  Urgency=4:   7     8     9    10    11
  Urgency=5:   8     9    10    11    12
```

---

## Python Example: DataExporter System

Two dimensions: **Format** (CSV, JSON, XML) and **Destination** (File, S3, FTP).

### The Implementation Side (Destination)

```python
from abc import ABC, abstractmethod
import json
import os


class ExportDestination(ABC):
    """The implementation side: WHERE to export data."""

    @abstractmethod
    def write(self, data: str, filename: str) -> None:
        pass

    @abstractmethod
    def get_destination_name(self) -> str:
        pass


class FileDestination(ExportDestination):
    """Writes to the local filesystem."""

    def __init__(self, base_dir: str = "/tmp/exports"):
        self._base_dir = base_dir

    def write(self, data: str, filename: str) -> None:
        full_path = os.path.join(self._base_dir, filename)
        print(f"  [File] Writing {len(data)} bytes to: {full_path}")
        # In production: os.makedirs(self._base_dir, exist_ok=True)
        # with open(full_path, 'w') as f: f.write(data)

    def get_destination_name(self) -> str:
        return f"File({self._base_dir})"


class S3Destination(ExportDestination):
    """Uploads to AWS S3."""

    def __init__(self, bucket: str, prefix: str = "exports/"):
        self._bucket = bucket
        self._prefix = prefix

    def write(self, data: str, filename: str) -> None:
        s3_key = self._prefix + filename
        print(f"  [S3] Uploading {len(data)} bytes to s3://{self._bucket}/{s3_key}")
        # In production: boto3.client('s3').put_object(...)

    def get_destination_name(self) -> str:
        return f"S3({self._bucket})"


class FTPDestination(ExportDestination):
    """Uploads to an FTP server."""

    def __init__(self, host: str, port: int = 21, remote_dir: str = "/uploads"):
        self._host = host
        self._port = port
        self._remote_dir = remote_dir

    def write(self, data: str, filename: str) -> None:
        remote_path = f"{self._remote_dir}/{filename}"
        print(f"  [FTP] Uploading {len(data)} bytes to "
              f"ftp://{self._host}:{self._port}{remote_path}")
        # In production: ftplib.FTP(self._host).storbinary(...)

    def get_destination_name(self) -> str:
        return f"FTP({self._host})"
```

### The Abstraction Side (Format)

```python
class DataExporter(ABC):
    """
    The abstraction side: HOW to format data.
    Uses a destination (bridge) to determine WHERE to write.
    """

    def __init__(self, destination: ExportDestination):
        self._destination = destination  # <-- the bridge

    @abstractmethod
    def export(self, records: list[dict], filename: str) -> None:
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        pass

    def _write_output(self, formatted_data: str, filename: str) -> None:
        """Delegates writing to the destination (bridge)."""
        dest_name = self._destination.get_destination_name()
        fmt_name = self.get_format_name()
        print(f"Exporting {fmt_name} -> {dest_name}: {filename}")
        self._destination.write(formatted_data, filename)


class CSVExporter(DataExporter):
    """Exports data as CSV."""

    def __init__(self, destination: ExportDestination, delimiter: str = ","):
        super().__init__(destination)
        self._delimiter = delimiter

    def export(self, records: list[dict], filename: str) -> None:
        if not records:
            print("  [CSV] No records to export")
            return

        # Build CSV string
        headers = list(records[0].keys())
        lines = [self._delimiter.join(headers)]
        for record in records:
            values = [str(record.get(h, "")) for h in headers]
            lines.append(self._delimiter.join(values))

        csv_data = "\n".join(lines)
        print(f"  [CSV] Formatted {len(records)} records ({len(lines)} lines)")
        self._write_output(csv_data, filename)

    def get_format_name(self) -> str:
        return "CSV"


class JSONExporter(DataExporter):
    """Exports data as JSON."""

    def __init__(self, destination: ExportDestination, pretty: bool = True):
        super().__init__(destination)
        self._pretty = pretty

    def export(self, records: list[dict], filename: str) -> None:
        indent = 2 if self._pretty else None
        json_data = json.dumps(records, indent=indent, default=str)
        print(f"  [JSON] Formatted {len(records)} records "
              f"({'pretty' if self._pretty else 'compact'})")
        self._write_output(json_data, filename)

    def get_format_name(self) -> str:
        return "JSON"


class XMLExporter(DataExporter):
    """Exports data as XML."""

    def export(self, records: list[dict], filename: str) -> None:
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<records>"]
        for record in records:
            lines.append("  <record>")
            for key, value in record.items():
                lines.append(f"    <{key}>{value}</{key}>")
            lines.append("  </record>")
        lines.append("</records>")

        xml_data = "\n".join(lines)
        print(f"  [XML] Formatted {len(records)} records")
        self._write_output(xml_data, filename)

    def get_format_name(self) -> str:
        return "XML"
```

### Using the Bridge

```python
def main():
    # Sample data
    records = [
        {"id": 1, "name": "Widget A", "price": 19.99, "stock": 150},
        {"id": 2, "name": "Widget B", "price": 29.99, "stock": 75},
        {"id": 3, "name": "Widget C", "price": 9.99, "stock": 300},
    ]

    # Create destinations
    local_file = FileDestination("/tmp/reports")
    s3_bucket = S3Destination("my-data-bucket", "reports/2024/")
    ftp_server = FTPDestination("ftp.partner.com")

    # Mix and match any format with any destination
    print("=== CSV to Local File ===")
    csv_to_file = CSVExporter(local_file)
    csv_to_file.export(records, "products.csv")

    print("\n=== JSON to S3 ===")
    json_to_s3 = JSONExporter(s3_bucket)
    json_to_s3.export(records, "products.json")

    print("\n=== XML to FTP ===")
    xml_to_ftp = XMLExporter(ftp_server)
    xml_to_ftp.export(records, "products.xml")

    print("\n=== JSON to FTP (new combination, no new class) ===")
    json_to_ftp = JSONExporter(ftp_server, pretty=False)
    json_to_ftp.export(records, "products_compact.json")

    # Adding a new destination (e.g., Azure Blob Storage) requires
    # only ONE new class, not 3 (one per format)

    # Adding a new format (e.g., Parquet) requires
    # only ONE new class, not 3 (one per destination)


if __name__ == "__main__":
    main()
```

**Output:**

```
=== CSV to Local File ===
  [CSV] Formatted 3 records (4 lines)
Exporting CSV -> File(/tmp/reports): products.csv
  [File] Writing 97 bytes to: /tmp/reports/products.csv

=== JSON to S3 ===
  [JSON] Formatted 3 records (pretty)
Exporting JSON -> S3(my-data-bucket): products.json
  [S3] Uploading 234 bytes to s3://my-data-bucket/reports/2024/products.json

=== XML to FTP ===
  [XML] Formatted 3 records
Exporting XML -> FTP(ftp.partner.com): products.xml
  [FTP] Uploading 312 bytes to ftp://ftp.partner.com:21/uploads/products.xml

=== JSON to FTP (new combination, no new class) ===
  [JSON] Formatted 3 records (compact)
Exporting JSON -> FTP(ftp.partner.com): products_compact.json
  [FTP] Uploading 178 bytes to ftp://ftp.partner.com:21/uploads/products_compact.json
```

---

## When the Bridge Helps Most

The Bridge pattern provides the most value when:

1. **Two dimensions of variation exist.** If you only have one dimension (just formats, or just destinations), use simple polymorphism.

2. **The dimensions change independently.** Adding a new format should not require touching destination code, and vice versa.

3. **The number of combinations is large.** With 2 formats and 2 destinations, you have 4 combinations -- the Bridge saves little. With 5 formats and 5 destinations, you have 25 combinations vs 10 classes.

4. **You want to swap implementations at runtime.** The bridge (composition) lets you change the destination of an exporter without creating a new exporter.

```python
# Runtime swapping: same exporter, different destinations
exporter = JSONExporter(local_file)
exporter.export(records, "local_copy.json")

# Later, switch to S3 without creating a new class
exporter._destination = s3_bucket
exporter.export(records, "cloud_copy.json")
```

---

## When to Use / When NOT to Use

### Use the Bridge Pattern When:

- You have two or more independent dimensions of variation
- You want to avoid class explosion from combining dimensions via inheritance
- You need to switch implementations at runtime
- Both dimensions are likely to grow over time
- You want to change abstraction and implementation independently

### Do NOT Use the Bridge Pattern When:

- You have only one dimension of variation -- use simple polymorphism
- The dimensions are not truly independent (one depends on the other)
- The total number of combinations is small (fewer than 6)
- Adding the pattern would introduce unnecessary abstraction for a simple problem
- The implementation side has only one class and will not grow

---

## Common Mistakes

### Mistake 1: Using Bridge When Strategy Suffices

```java
// If you only have ONE dimension of variation, you do not need Bridge.
// This is just Strategy:
public class ReportGenerator {
    private ReportFormat format; // Strategy, not Bridge
    public void generate(Data data) { format.render(data); }
}

// Bridge is for TWO dimensions:
public class ReportGenerator { // abstraction dimension: summary vs detailed
    private ReportFormat format; // implementation dimension: PDF vs HTML vs CSV
}
```

### Mistake 2: Tight Coupling Between Abstraction and Implementation

```java
// BAD: The abstraction knows specific implementation details
public class UrgentNotification extends Notification {
    @Override
    public void send(String recipient, String message) {
        if (sender instanceof EmailSender) { // breaks the bridge!
            ((EmailSender) sender).setHighPriority(true);
        }
        sender.sendMessage(recipient, formatSubject(message), formatBody(message));
    }
}

// GOOD: The abstraction only uses the interface methods
public class UrgentNotification extends Notification {
    @Override
    public void send(String recipient, String message) {
        // No instanceof checks. Works with ANY sender.
        sender.sendMessage(recipient, formatSubject(message), formatBody(message));
    }
}
```

### Mistake 3: Making the Implementation Too Thin

```java
// BAD: Implementation interface is too generic
public interface MessageSender {
    void send(Object data); // Too vague, abstraction must know details
}

// GOOD: Implementation interface is specific enough to be useful
public interface MessageSender {
    void sendMessage(String recipient, String subject, String body);
    String getChannelName();
}
```

---

## Best Practices

1. **Identify the two dimensions first.** Before writing code, clearly name the two independent dimensions of variation. If you cannot find two, you probably do not need Bridge.

2. **Keep the bridge interface stable.** The implementation interface is the contract between the two dimensions. Changes to it ripple through both sides.

3. **Do not leak implementation details into the abstraction.** The abstraction should work with any implementation without type checks or casts.

4. **Use with dependency injection.** The implementation side is a natural fit for DI frameworks, making it easy to configure which implementation each abstraction uses.

5. **Start without Bridge.** If you start with only 2-3 combinations, simple classes are fine. Refactor to Bridge when you see class explosion happening.

---

## Quick Summary

The Bridge pattern separates an abstraction from its implementation so the two can vary independently. Instead of creating a class for every combination of two dimensions (NxM classes), you create N + M classes connected by composition. This is especially valuable when both dimensions will grow over time.

```
  Without Bridge:          With Bridge:

  Abstraction              Abstraction ────bridge────> Implementation
       │                        │                           │
  ┌────┼────┐              ┌────┼────┐              ┌──────┼──────┐
  │    │    │              │         │              │      │      │
  A1   A2   A3          Normal   Urgent         Email   SMS   Push
  │    │    │
  ├B1  ├B1  ├B1           2 classes + 3 classes = 5 total
  ├B2  ├B2  ├B2
  └B3  └B3  └B3           Instead of 2 x 3 = 6

  9 classes!
```

---

## Key Points

- The Bridge pattern decouples abstraction from implementation, letting them vary independently
- It solves the class explosion problem caused by combining two dimensions via inheritance
- The "bridge" is a composition relationship: the abstraction has-a reference to the implementation
- Growth is additive (N + M) instead of multiplicative (N x M)
- Bridge is most valuable when both dimensions are expected to grow
- Do not confuse Bridge with Strategy (Strategy has one dimension, Bridge has two)
- Do not confuse Bridge with Adapter (Adapter makes things work together after design; Bridge plans for separation from the start)

---

## Practice Questions

1. You are building a reporting system with report types (Summary, Detailed, Audit) and output formats (PDF, HTML, Excel). How many classes do you need with Bridge vs without? What are the two sides of the bridge?

2. How does the Bridge pattern differ from the Strategy pattern? Give a scenario where each would be appropriate.

3. Your team argues that the Bridge pattern is just "using interfaces." What would you say to explain why it is more specific than that?

4. You have a logging system with log levels (DEBUG, INFO, WARN, ERROR) and log destinations (Console, File, Remote). Should you use Bridge? Why or why not?

5. A colleague uses `instanceof` checks inside an abstraction class to handle specific implementation types. Why does this defeat the purpose of the Bridge pattern?

---

## Exercises

### Exercise 1: Shape Rendering Bridge

Create a Bridge pattern for drawing shapes:
- Abstraction dimension: Shape types (Circle, Rectangle, Triangle)
- Implementation dimension: Rendering engines (SVGRenderer, CanvasRenderer, ASCIIRenderer)

Each shape should delegate its rendering to the engine. Adding a new shape or renderer should require only one new class.

### Exercise 2: Python Payment Processing Bridge

Build a payment system with two dimensions:
- Payment type (OneTimePayment, RecurringPayment, InstallmentPayment) -- each formats the request differently
- Payment gateway (StripeGateway, PayPalGateway, SquareGateway) -- each uses a different API

Demonstrate creating all 9 combinations using only 6 classes (3 + 3).

### Exercise 3: Configurable Notification System

Extend the Java Notification example from this chapter:
- Add a `ScheduledNotification` abstraction that delays sending
- Add a `SlackSender` implementation
- Add a `WebhookSender` implementation
- Show how adding these 3 classes creates 5 new combinations (3 urgency levels x 2 new channels - but 5 new combinations, not 6 new classes)

---

## What Is Next?

You now know how to handle two dimensions of variation without class explosion. But what about tree structures? What if your objects form hierarchies -- files inside folders, menu items inside submenus, employees inside departments -- and you want to treat individual objects and groups of objects uniformly?

In the next chapter, you will learn the **Composite pattern**, which lets you build tree structures where leaves and branches share the same interface. Where Bridge separates two flat dimensions, Composite handles recursive, nested structures.
