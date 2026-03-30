# Chapter 9: The Facade Pattern

---

## What You Will Learn

By the end of this chapter, you will be able to:

- Understand the Facade pattern and why it simplifies complex systems
- Recognize when a subsystem has too many moving parts for clients to manage
- Build an `OrderFacade` in Java that coordinates inventory, payment, shipping, and notification subsystems
- Create a `DataPipelineFacade` in Python that hides ETL complexity
- Distinguish between the Facade pattern and the Adapter pattern
- Apply the Facade pattern to SDK client design and complex business workflows
- Know when a facade helps and when it hides too much

---

## Why This Chapter Matters

Backend systems grow. What starts as a simple "place an order" operation eventually involves checking inventory, validating the customer's payment, calculating shipping costs, reserving stock, charging the credit card, creating a shipment, sending a confirmation email, updating analytics, and notifying the warehouse. That is ten subsystems for one user action.

Without a facade, every controller, service, or API endpoint that needs to place an order must coordinate all ten subsystems in the correct sequence, handle errors at each step, and manage rollbacks if something fails halfway through.

Think of a **hotel front desk**. When you check in, you do not call housekeeping to prepare your room, contact the restaurant to reserve your dinner table, ask the valet to park your car, and notify the concierge about your preferences. You talk to **one person at the front desk**, and they coordinate everything behind the scenes.

```
   Without Facade                          With Facade
   (Guest does everything)                (Front desk handles it)

   ┌───────┐                              ┌───────┐
   │ Guest │                              │ Guest │
   └───┬───┘                              └───┬───┘
       │                                      │
       ├──> Housekeeping                      ▼
       ├──> Restaurant                  ┌───────────┐
       ├──> Valet                       │ Front Desk│
       ├──> Concierge                   │ (Facade)  │
       ├──> Billing                     └─────┬─────┘
       └──> Security                          │
                                              ├──> Housekeeping
       6 interactions                         ├──> Restaurant
       Guest must know                        ├──> Valet
       every department                       ├──> Concierge
                                              ├──> Billing
                                              └──> Security

                                         1 interaction
                                         Guest only knows
                                         the front desk
```

The Facade pattern provides a simplified interface to a complex subsystem. The subsystem still exists in all its complexity, but clients do not need to know about it.

---

## The Problem

You are building an e-commerce backend. Placing an order involves four subsystems:

```java
// Subsystem 1: Inventory Management
public class InventoryService {
    public boolean checkStock(String productId, int quantity) { /* ... */ }
    public void reserveStock(String productId, int quantity) { /* ... */ }
    public void releaseStock(String productId, int quantity) { /* ... */ }
}

// Subsystem 2: Payment Processing
public class PaymentService {
    public boolean validatePaymentMethod(String customerId) { /* ... */ }
    public String chargeCustomer(String customerId, double amount) { /* ... */ }
    public void refundCharge(String chargeId) { /* ... */ }
}

// Subsystem 3: Shipping
public class ShippingService {
    public double calculateShippingCost(String address, double weight) { /* ... */ }
    public String createShipment(String orderId, String address) { /* ... */ }
    public String getTrackingNumber(String shipmentId) { /* ... */ }
}

// Subsystem 4: Notifications
public class NotificationService {
    public void sendOrderConfirmation(String email, String orderId) { /* ... */ }
    public void sendShippingNotification(String email, String trackingNumber) { /* ... */ }
    public void sendFailureNotification(String email, String reason) { /* ... */ }
}
```

Without a facade, the controller looks like this:

```java
// BAD: Controller knows too much about every subsystem
@PostMapping("/orders")
public ResponseEntity<?> placeOrder(@RequestBody OrderRequest request) {
    // Step 1: Check inventory
    if (!inventoryService.checkStock(request.getProductId(), request.getQuantity())) {
        notificationService.sendFailureNotification(request.getEmail(), "Out of stock");
        return ResponseEntity.badRequest().body("Out of stock");
    }

    // Step 2: Reserve stock
    inventoryService.reserveStock(request.getProductId(), request.getQuantity());

    // Step 3: Validate payment
    if (!paymentService.validatePaymentMethod(request.getCustomerId())) {
        inventoryService.releaseStock(request.getProductId(), request.getQuantity());
        notificationService.sendFailureNotification(request.getEmail(), "Invalid payment");
        return ResponseEntity.badRequest().body("Invalid payment method");
    }

    // Step 4: Calculate shipping
    double shippingCost = shippingService.calculateShippingCost(
        request.getAddress(), request.getWeight());
    double total = request.getAmount() + shippingCost;

    // Step 5: Charge customer
    String chargeId = paymentService.chargeCustomer(request.getCustomerId(), total);
    if (chargeId == null) {
        inventoryService.releaseStock(request.getProductId(), request.getQuantity());
        notificationService.sendFailureNotification(request.getEmail(), "Payment failed");
        return ResponseEntity.badRequest().body("Payment failed");
    }

    // Step 6: Create shipment
    String shipmentId = shippingService.createShipment(orderId, request.getAddress());
    String trackingNumber = shippingService.getTrackingNumber(shipmentId);

    // Step 7: Send notifications
    notificationService.sendOrderConfirmation(request.getEmail(), orderId);
    notificationService.sendShippingNotification(request.getEmail(), trackingNumber);

    return ResponseEntity.ok(new OrderResponse(orderId, trackingNumber));
}
```

This controller is doing too much. It knows the exact sequence of operations. It handles rollbacks. It coordinates four services. And if any other endpoint needs to place an order (an admin tool, a batch processor, a webhook handler), all this logic must be duplicated.

---

## The Solution: Facade Pattern

Create a single class that exposes a simple interface and handles the coordination internally.

```
┌─────────────────────────────────────────────────────────────┐
│                     Facade Pattern Structure                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────┐        ┌──────────────────────────┐          │
│   │  Client   │───────>│      OrderFacade         │          │
│   │(Controller│        │                          │          │
│   │  or API)  │        │  placeOrder(request)     │          │
│   └──────────┘        │  cancelOrder(orderId)    │          │
│                        │  getOrderStatus(orderId) │          │
│   Only calls           └────────────┬─────────────┘          │
│   the facade                        │                        │
│                          ┌──────────┼──────────┐             │
│                          │          │          │             │
│                     ┌────┴───┐ ┌────┴───┐ ┌───┴────┐       │
│                     │Inventory│ │Payment │ │Shipping│       │
│                     │Service  │ │Service │ │Service │       │
│                     └────────┘ └────────┘ └────────┘       │
│                                                    │         │
│                                              ┌─────┴──────┐ │
│                                              │Notification│ │
│                                              │Service     │ │
│                                              └────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Java Example: OrderFacade

### The Subsystems

```java
public class InventoryService {

    public boolean checkStock(String productId, int quantity) {
        System.out.println("  [Inventory] Checking stock for " + productId
            + " (qty: " + quantity + ")");
        // Simulate: product "PROD-999" is out of stock
        return !productId.equals("PROD-999");
    }

    public void reserveStock(String productId, int quantity) {
        System.out.println("  [Inventory] Reserved " + quantity
            + " units of " + productId);
    }

    public void releaseStock(String productId, int quantity) {
        System.out.println("  [Inventory] Released " + quantity
            + " units of " + productId);
    }
}

public class PaymentService {

    public boolean validatePaymentMethod(String customerId) {
        System.out.println("  [Payment] Validating payment for customer: " + customerId);
        return true; // assume valid
    }

    public String chargeCustomer(String customerId, double amount) {
        System.out.println("  [Payment] Charging customer " + customerId
            + " amount: $" + String.format("%.2f", amount));
        return "CHG-" + System.currentTimeMillis();
    }

    public void refundCharge(String chargeId) {
        System.out.println("  [Payment] Refunding charge: " + chargeId);
    }
}

public class ShippingService {

    public double calculateShippingCost(String address, double weightKg) {
        System.out.println("  [Shipping] Calculating cost to: " + address);
        return weightKg * 2.50; // $2.50 per kg
    }

    public String createShipment(String orderId, String address) {
        System.out.println("  [Shipping] Creating shipment for order: " + orderId);
        return "SHIP-" + orderId;
    }

    public String getTrackingNumber(String shipmentId) {
        return "TRACK-" + shipmentId.hashCode();
    }
}

public class NotificationService {

    public void sendOrderConfirmation(String email, String orderId) {
        System.out.println("  [Notify] Order confirmation sent to " + email
            + " for order: " + orderId);
    }

    public void sendShippingNotification(String email, String trackingNumber) {
        System.out.println("  [Notify] Shipping notification sent to " + email
            + " tracking: " + trackingNumber);
    }

    public void sendFailureNotification(String email, String reason) {
        System.out.println("  [Notify] Failure notification sent to " + email
            + " reason: " + reason);
    }
}
```

### The Order Request and Result

```java
public class OrderRequest {
    private final String customerId;
    private final String productId;
    private final int quantity;
    private final double unitPrice;
    private final String shippingAddress;
    private final double weightKg;
    private final String email;

    public OrderRequest(String customerId, String productId, int quantity,
                        double unitPrice, String shippingAddress,
                        double weightKg, String email) {
        this.customerId = customerId;
        this.productId = productId;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
        this.shippingAddress = shippingAddress;
        this.weightKg = weightKg;
        this.email = email;
    }

    // Getters omitted for brevity
    public String getCustomerId() { return customerId; }
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
    public double getUnitPrice() { return unitPrice; }
    public String getShippingAddress() { return shippingAddress; }
    public double getWeightKg() { return weightKg; }
    public String getEmail() { return email; }
}

public class OrderResult {
    private final boolean success;
    private final String orderId;
    private final String trackingNumber;
    private final String message;
    private final double totalCharged;

    public OrderResult(boolean success, String orderId, String trackingNumber,
                       String message, double totalCharged) {
        this.success = success;
        this.orderId = orderId;
        this.trackingNumber = trackingNumber;
        this.message = message;
        this.totalCharged = totalCharged;
    }

    public boolean isSuccess() { return success; }
    public String getOrderId() { return orderId; }

    @Override
    public String toString() {
        if (success) {
            return "OrderResult{SUCCESS, orderId='" + orderId
                + "', tracking='" + trackingNumber
                + "', total=$" + String.format("%.2f", totalCharged) + "}";
        }
        return "OrderResult{FAILED, message='" + message + "'}";
    }
}
```

### The Facade

```java
public class OrderFacade {

    private final InventoryService inventory;
    private final PaymentService payment;
    private final ShippingService shipping;
    private final NotificationService notification;

    public OrderFacade(InventoryService inventory, PaymentService payment,
                       ShippingService shipping, NotificationService notification) {
        this.inventory = inventory;
        this.payment = payment;
        this.shipping = shipping;
        this.notification = notification;
    }

    /**
     * Places an order. This single method coordinates four subsystems:
     * inventory check, payment processing, shipment creation, and notifications.
     */
    public OrderResult placeOrder(OrderRequest request) {
        String orderId = "ORD-" + System.currentTimeMillis();
        System.out.println("=== Processing Order: " + orderId + " ===");

        // Step 1: Check and reserve inventory
        if (!inventory.checkStock(request.getProductId(), request.getQuantity())) {
            notification.sendFailureNotification(request.getEmail(), "Out of stock");
            return new OrderResult(false, null, null, "Product out of stock", 0);
        }
        inventory.reserveStock(request.getProductId(), request.getQuantity());

        // Step 2: Validate and process payment
        if (!payment.validatePaymentMethod(request.getCustomerId())) {
            inventory.releaseStock(request.getProductId(), request.getQuantity());
            notification.sendFailureNotification(request.getEmail(), "Invalid payment");
            return new OrderResult(false, null, null, "Invalid payment method", 0);
        }

        double subtotal = request.getUnitPrice() * request.getQuantity();
        double shippingCost = shipping.calculateShippingCost(
            request.getShippingAddress(), request.getWeightKg());
        double total = subtotal + shippingCost;

        String chargeId = payment.chargeCustomer(request.getCustomerId(), total);
        if (chargeId == null) {
            inventory.releaseStock(request.getProductId(), request.getQuantity());
            notification.sendFailureNotification(request.getEmail(), "Payment failed");
            return new OrderResult(false, null, null, "Payment processing failed", 0);
        }

        // Step 3: Create shipment
        String shipmentId = shipping.createShipment(orderId, request.getShippingAddress());
        String trackingNumber = shipping.getTrackingNumber(shipmentId);

        // Step 4: Send notifications
        notification.sendOrderConfirmation(request.getEmail(), orderId);
        notification.sendShippingNotification(request.getEmail(), trackingNumber);

        System.out.println("=== Order Complete ===\n");
        return new OrderResult(true, orderId, trackingNumber, "Order placed", total);
    }

    /**
     * Cancels an order. Another complex operation simplified to one call.
     */
    public boolean cancelOrder(String orderId, String customerId, String email) {
        System.out.println("=== Cancelling Order: " + orderId + " ===");
        // In a real system: look up order, refund payment, release stock, cancel shipment
        payment.refundCharge("CHG-" + orderId);
        notification.sendFailureNotification(email, "Order " + orderId + " cancelled");
        System.out.println("=== Cancellation Complete ===\n");
        return true;
    }
}
```

### Using the Facade

```java
public class Main {
    public static void main(String[] args) {
        // Create subsystems
        InventoryService inventory = new InventoryService();
        PaymentService payment = new PaymentService();
        ShippingService shipping = new ShippingService();
        NotificationService notification = new NotificationService();

        // Create the facade -- this is the only thing the client knows about
        OrderFacade orderFacade = new OrderFacade(
            inventory, payment, shipping, notification
        );

        // Place an order -- one simple call
        OrderRequest request = new OrderRequest(
            "CUST-42",           // customerId
            "PROD-100",          // productId
            2,                   // quantity
            29.99,               // unitPrice
            "123 Main St, NYC",  // shippingAddress
            1.5,                 // weightKg
            "alice@example.com"  // email
        );

        OrderResult result = orderFacade.placeOrder(request);
        System.out.println("Result: " + result);
    }
}
```

**Output:**

```
=== Processing Order: ORD-1703001234567 ===
  [Inventory] Checking stock for PROD-100 (qty: 2)
  [Inventory] Reserved 2 units of PROD-100
  [Payment] Validating payment for customer: CUST-42
  [Shipping] Calculating cost to: 123 Main St, NYC
  [Payment] Charging customer CUST-42 amount: $63.73
  [Shipping] Creating shipment for order: ORD-1703001234567
  [Notify] Order confirmation sent to alice@example.com for order: ORD-1703001234567
  [Notify] Shipping notification sent to alice@example.com tracking: TRACK-987654321
=== Order Complete ===

Result: OrderResult{SUCCESS, orderId='ORD-1703001234567', tracking='TRACK-987654321', total=$63.73}
```

### Before vs After

**Before (controller coordinates everything):**

```java
@PostMapping("/orders")
public ResponseEntity<?> placeOrder(@RequestBody OrderRequest request) {
    // 40+ lines of coordination logic
    // Error handling at each step
    // Rollback logic scattered throughout
    // Duplicated in every endpoint that creates orders
}
```

**After (controller uses facade):**

```java
@PostMapping("/orders")
public ResponseEntity<?> placeOrder(@RequestBody OrderRequest request) {
    OrderResult result = orderFacade.placeOrder(request);
    if (result.isSuccess()) {
        return ResponseEntity.ok(result);
    }
    return ResponseEntity.badRequest().body(result);
}
```

The controller went from 40+ lines to 5 lines. The coordination logic lives in one place and is reusable.

---

## Python Example: DataPipelineFacade

Data pipelines involve many steps: extracting data from sources, transforming it, validating it, loading it into a destination, and sending reports. A facade simplifies this.

### The Subsystems

```python
import csv
import json
import io
from datetime import datetime


class DataExtractor:
    """Extracts data from various sources."""

    def extract_from_csv(self, file_path: str) -> list[dict]:
        print(f"  [Extractor] Reading CSV: {file_path}")
        # Simulated CSV data
        return [
            {"id": "1", "name": "Widget A", "price": "19.99", "quantity": "150"},
            {"id": "2", "name": "Widget B", "price": "29.99", "quantity": "75"},
            {"id": "3", "name": "Widget C", "price": "9.99", "quantity": "300"},
        ]

    def extract_from_api(self, endpoint: str) -> list[dict]:
        print(f"  [Extractor] Fetching API: {endpoint}")
        return [{"id": "4", "name": "Widget D", "price": "49.99", "quantity": "20"}]

    def extract_from_database(self, query: str) -> list[dict]:
        print(f"  [Extractor] Running query: {query}")
        return [{"id": "5", "name": "Widget E", "price": "14.99", "quantity": "200"}]


class DataTransformer:
    """Transforms and cleans data."""

    def normalize_fields(self, records: list[dict]) -> list[dict]:
        """Convert string numbers to proper types."""
        print(f"  [Transformer] Normalizing {len(records)} records")
        normalized = []
        for record in records:
            normalized.append({
                "id": int(record["id"]),
                "name": record["name"].strip().upper(),
                "price": float(record["price"]),
                "quantity": int(record["quantity"]),
            })
        return normalized

    def enrich_data(self, records: list[dict]) -> list[dict]:
        """Add computed fields."""
        print(f"  [Transformer] Enriching {len(records)} records")
        for record in records:
            record["total_value"] = record["price"] * record["quantity"]
            record["processed_at"] = datetime.now().isoformat()
        return records

    def filter_records(self, records: list[dict], min_quantity: int) -> list[dict]:
        """Remove records below a threshold."""
        filtered = [r for r in records if r["quantity"] >= min_quantity]
        print(f"  [Transformer] Filtered: {len(records)} -> {len(filtered)} records"
              f" (min_quantity={min_quantity})")
        return filtered


class DataValidator:
    """Validates data before loading."""

    def validate(self, records: list[dict]) -> tuple[list[dict], list[str]]:
        """Returns (valid_records, error_messages)."""
        print(f"  [Validator] Validating {len(records)} records")
        valid = []
        errors = []
        for record in records:
            if record["price"] <= 0:
                errors.append(f"Invalid price for {record['name']}: {record['price']}")
            elif record["quantity"] < 0:
                errors.append(f"Negative quantity for {record['name']}")
            else:
                valid.append(record)
        print(f"  [Validator] {len(valid)} valid, {len(errors)} errors")
        return valid, errors


class DataLoader:
    """Loads data into a destination."""

    def load_to_database(self, records: list[dict], table_name: str) -> int:
        print(f"  [Loader] Loading {len(records)} records into table: {table_name}")
        return len(records)

    def load_to_file(self, records: list[dict], file_path: str) -> int:
        print(f"  [Loader] Writing {len(records)} records to: {file_path}")
        return len(records)


class ReportGenerator:
    """Generates pipeline execution reports."""

    def generate_summary(self, stats: dict) -> str:
        print("  [Report] Generating pipeline summary")
        lines = ["Pipeline Execution Report", "=" * 40]
        for key, value in stats.items():
            lines.append(f"  {key}: {value}")
        report = "\n".join(lines)
        return report
```

### The Facade

```python
class DataPipelineFacade:
    """Simple interface for running complex data pipelines."""

    def __init__(self):
        self._extractor = DataExtractor()
        self._transformer = DataTransformer()
        self._validator = DataValidator()
        self._loader = DataLoader()
        self._reporter = ReportGenerator()

    def run_csv_pipeline(
        self,
        csv_path: str,
        destination_table: str,
        min_quantity: int = 0,
    ) -> dict:
        """
        Complete ETL pipeline from CSV to database.

        One method call replaces what would otherwise be 6+ manual steps
        with error handling at each stage.
        """
        print(f"\n{'=' * 50}")
        print(f"Pipeline: CSV -> Database")
        print(f"{'=' * 50}")

        # Extract
        raw_data = self._extractor.extract_from_csv(csv_path)

        # Transform
        normalized = self._transformer.normalize_fields(raw_data)
        enriched = self._transformer.enrich_data(normalized)
        filtered = self._transformer.filter_records(enriched, min_quantity)

        # Validate
        valid_records, errors = self._validator.validate(filtered)

        # Load
        loaded_count = self._loader.load_to_database(valid_records, destination_table)

        # Report
        stats = {
            "source": csv_path,
            "destination": destination_table,
            "records_extracted": len(raw_data),
            "records_after_filter": len(filtered),
            "records_valid": len(valid_records),
            "records_loaded": loaded_count,
            "validation_errors": len(errors),
        }
        report = self._reporter.generate_summary(stats)
        print(f"\n{report}")

        return stats

    def run_multi_source_pipeline(
        self,
        csv_path: str,
        api_endpoint: str,
        db_query: str,
        output_file: str,
    ) -> dict:
        """
        Combines data from CSV, API, and database into a single output file.
        """
        print(f"\n{'=' * 50}")
        print(f"Pipeline: Multi-Source -> File")
        print(f"{'=' * 50}")

        # Extract from all sources
        csv_data = self._extractor.extract_from_csv(csv_path)
        api_data = self._extractor.extract_from_api(api_endpoint)
        db_data = self._extractor.extract_from_database(db_query)

        # Merge all sources
        all_data = csv_data + api_data + db_data
        print(f"  [Pipeline] Merged {len(all_data)} total records from 3 sources")

        # Transform
        normalized = self._transformer.normalize_fields(all_data)
        enriched = self._transformer.enrich_data(normalized)

        # Validate
        valid_records, errors = self._validator.validate(enriched)

        # Load
        loaded_count = self._loader.load_to_file(valid_records, output_file)

        stats = {
            "sources": 3,
            "total_extracted": len(all_data),
            "records_loaded": loaded_count,
            "output": output_file,
        }
        report = self._reporter.generate_summary(stats)
        print(f"\n{report}")

        return stats
```

### Using the Facade

```python
def main():
    pipeline = DataPipelineFacade()

    # One call to run a complete ETL pipeline
    stats = pipeline.run_csv_pipeline(
        csv_path="sales_data.csv",
        destination_table="products",
        min_quantity=50,
    )
    print(f"\nLoaded {stats['records_loaded']} records successfully\n")

    # Another complex pipeline, still one call
    stats = pipeline.run_multi_source_pipeline(
        csv_path="inventory.csv",
        api_endpoint="https://api.supplier.com/products",
        db_query="SELECT * FROM legacy_products",
        output_file="merged_catalog.json",
    )


if __name__ == "__main__":
    main()
```

**Output:**

```
==================================================
Pipeline: CSV -> Database
==================================================
  [Extractor] Reading CSV: sales_data.csv
  [Transformer] Normalizing 3 records
  [Transformer] Enriching 3 records
  [Transformer] Filtered: 3 -> 3 records (min_quantity=50)
  [Validator] Validating 3 records
  [Validator] 3 valid, 0 errors
  [Loader] Loading 3 records into table: products
  [Report] Generating pipeline summary

Pipeline Execution Report
========================================
  source: sales_data.csv
  destination: products
  records_extracted: 3
  records_after_filter: 3
  records_valid: 3
  records_loaded: 3
  validation_errors: 0

Loaded 3 records successfully

==================================================
Pipeline: Multi-Source -> File
==================================================
  [Extractor] Reading CSV: inventory.csv
  [Extractor] Fetching API: https://api.supplier.com/products
  [Extractor] Running query: SELECT * FROM legacy_products
  [Pipeline] Merged 5 total records from 3 sources
  [Transformer] Normalizing 5 records
  [Transformer] Enriching 5 records
  [Validator] Validating 5 records
  [Validator] 5 valid, 0 errors
  [Loader] Writing 5 records to: merged_catalog.json
  [Report] Generating pipeline summary

Pipeline Execution Report
========================================
  sources: 3
  total_extracted: 5
  records_loaded: 5
  output: merged_catalog.json
```

---

## Real-World Backend Use Cases

### Use Case 1: SDK Client Libraries

Every cloud SDK is a facade. The AWS SDK for S3, for example, hides the complexity of HTTP requests, authentication, retries, region selection, and serialization behind simple methods:

```python
# Behind the scenes: HTTP client, auth signer, retry handler,
# region resolver, XML parser, multipart upload manager...
# The facade gives you this:
s3.upload_file("local.txt", "my-bucket", "remote.txt")
```

### Use Case 2: Complex Business Workflows

```
┌──────────────────────────────────────────────┐
│         UserRegistrationFacade               │
│                                              │
│  register(name, email, password)             │
│    1. Validate email format                  │
│    2. Check if email already exists          │
│    3. Hash password                          │
│    4. Create user record in database         │
│    5. Create default preferences             │
│    6. Assign default role                    │
│    7. Send welcome email                     │
│    8. Create audit log entry                 │
│    9. Sync with CRM system                   │
│   10. Update analytics                       │
│                                              │
│  Client just calls: facade.register(...)     │
└──────────────────────────────────────────────┘
```

### Use Case 3: Testing Complex Systems

Facades make testing easier because you can mock one facade instead of five subsystems:

```java
// Without facade: must mock 4 services
@Test
void testOrderPlacement() {
    InventoryService mockInventory = mock(InventoryService.class);
    PaymentService mockPayment = mock(PaymentService.class);
    ShippingService mockShipping = mock(ShippingService.class);
    NotificationService mockNotification = mock(NotificationService.class);
    // Set up all mocks... tedious
}

// With facade: mock one thing
@Test
void testCheckout() {
    OrderFacade mockFacade = mock(OrderFacade.class);
    when(mockFacade.placeOrder(any())).thenReturn(successResult);
    // Much simpler
}
```

---

## Facade vs Adapter

These two patterns are often confused. Here is how they differ:

| Aspect | Facade | Adapter |
|---|---|---|
| Purpose | Simplify a complex subsystem | Make incompatible interfaces work together |
| Direction | Provides a new, simpler interface | Converts one existing interface to another |
| Subsystems | Works with multiple classes | Usually wraps one class |
| Client knowledge | Client does not know about subsystems | Client knows the target interface |
| Analogy | Hotel front desk | Power plug adapter |

```
Facade:                              Adapter:
  Client ──> Facade ──> System A       Client ──> Adapter ──> Adaptee
                    ──> System B       (uses target       (has different
                    ──> System C        interface)          interface)
                    ──> System D

  Simplifies many into one             Translates one into another
```

---

## When to Use / When NOT to Use

### Use the Facade Pattern When:

- A subsystem has many classes and the client only needs a subset of functionality
- You want to layer your subsystem and provide an entry point to each layer
- You need to reduce coupling between clients and a complex subsystem
- You want to provide a simple default interface while still allowing advanced usage
- Multiple clients need to perform the same complex workflow

### Do NOT Use the Facade Pattern When:

- The subsystem is already simple -- adding a facade adds unnecessary indirection
- Every client needs different customization -- the facade cannot serve them all
- You need the facade to enforce access control (use a different pattern for that)
- You are using it to hide poor design -- fix the subsystem instead

---

## Common Mistakes

### Mistake 1: God Facade

```java
// BAD: Facade does everything for the entire application
public class ApplicationFacade {
    public OrderResult placeOrder(...) { }
    public UserResult registerUser(...) { }
    public ReportResult generateReport(...) { }
    public InventoryResult updateInventory(...) { }
    public void sendNotification(...) { }
    public void processRefund(...) { }
    // 50 more methods...
}
```

A facade should cover one cohesive area, not the entire application. Create multiple facades for different domains: `OrderFacade`, `UserFacade`, `ReportFacade`.

### Mistake 2: Facade Becomes the Only Access Point

```java
// BAD: Making subsystems package-private so only the facade can access them
// This turns the facade into a bottleneck

// GOOD: The facade provides a convenient interface, but advanced users
// can still access subsystems directly when they need fine-grained control
```

The facade should be an option, not a requirement. Clients that need more control should be able to bypass it.

### Mistake 3: Business Logic in the Facade

```java
// BAD: Facade calculates discounts, validates data, makes decisions
public OrderResult placeOrder(OrderRequest request) {
    double discount = request.getQuantity() > 10 ? 0.15 : 0.05; // business rule!
    // ...
}

// GOOD: Facade coordinates, subsystems contain the logic
public OrderResult placeOrder(OrderRequest request) {
    double discount = pricingService.calculateDiscount(request); // delegated
    // ...
}
```

The facade orchestrates. It should not contain business logic -- that belongs in the subsystems.

---

## Best Practices

1. **Keep facades thin.** A facade orchestrates calls to subsystems. It should not contain business logic, complex calculations, or data transformations.

2. **Create domain-specific facades.** One facade per bounded context or major feature area. `OrderFacade`, `UserFacade`, `ReportFacade` -- not one giant `ApplicationFacade`.

3. **Do not force clients to use the facade.** Make it convenient, not mandatory. Advanced clients might need direct subsystem access.

4. **Handle errors in the facade.** One of the facade's main jobs is coordinating error handling and rollbacks, so clients do not have to.

5. **Use dependency injection.** Pass subsystems into the facade's constructor. This makes testing easy and keeps the facade decoupled from specific implementations.

6. **Document what the facade coordinates.** A brief comment listing the subsystems and the sequence of operations helps the next developer.

---

## Quick Summary

The Facade pattern provides a simplified interface to a complex subsystem. Like a hotel front desk that coordinates housekeeping, valet, and room service, a facade lets clients accomplish complex operations with a single method call while hiding the coordination logic.

```
Without Facade:                    With Facade:

Client ──> Service A               Client ──> Facade ──> Service A
       ──> Service B                                ──> Service B
       ──> Service C                                ──> Service C
       ──> Service D                                ──> Service D

Client must coordinate             Facade coordinates
everything in the right order      everything internally
```

---

## Key Points

- The Facade pattern simplifies a complex subsystem by providing a higher-level interface
- It does not add new functionality -- it makes existing functionality easier to use
- Facades reduce coupling between clients and subsystem classes
- Unlike the Adapter (which translates one interface to another), the Facade simplifies multiple interfaces into one
- Keep facades thin -- they orchestrate, they do not contain business logic
- Create one facade per domain, not one facade for everything
- Facades are optional conveniences, not gatekeepers

---

## Practice Questions

1. You are building a user registration system that involves email validation, password hashing, database insertion, welcome email sending, and analytics tracking. Sketch the facade class. What methods would it expose?

2. A team has a `SystemFacade` class with 80 methods covering user management, order processing, reporting, and notifications. What is wrong with this design, and how would you fix it?

3. Your facade's `placeOrder()` method successfully charges the customer but fails when creating the shipment. How should the facade handle this situation? What about the notification to the customer?

4. When would you choose an Adapter over a Facade, and vice versa? Give a concrete example of each.

5. A junior developer suggests making all subsystem classes package-private so that only the facade can access them. What are the pros and cons of this approach?

---

## Exercises

### Exercise 1: Build a DeploymentFacade

Create a `DeploymentFacade` that coordinates these subsystems for deploying a web application:
- `BuildService`: compiles code and runs tests
- `ContainerService`: builds a Docker image and pushes it to a registry
- `KubernetesService`: updates the deployment with the new image
- `MonitoringService`: sets up health checks and alerts

The facade should expose a single `deploy(appName, version, environment)` method. Handle failures at each step with appropriate rollbacks.

### Exercise 2: Python EmailCampaignFacade

Build a facade for sending marketing email campaigns:
- `TemplateEngine`: renders email templates with variables
- `RecipientService`: fetches recipient lists, handles unsubscribes
- `EmailSender`: sends individual emails with rate limiting
- `AnalyticsTracker`: tracks opens, clicks, and bounces

Expose `send_campaign(template_name, recipient_list_name, variables)` and `get_campaign_stats(campaign_id)`.

### Exercise 3: Facade with Error Recovery

Extend the `OrderFacade` from this chapter to handle partial failures gracefully. If the payment succeeds but shipping fails, the facade should refund the payment and release the inventory. Write tests that verify the rollback behavior.

---

## What Is Next?

You have learned how to simplify complex subsystems with a single interface. But what if you need to control *access* to an object rather than simplify it? What if you want to add lazy loading, access control, or rate limiting without the client knowing?

In the next chapter, you will learn the **Proxy pattern**, which controls access to an object by standing in front of it like a bodyguard. Where the Facade simplifies, the Proxy controls.
