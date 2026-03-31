# Chapter 23: Bounded Contexts

## What You Will Learn

- What Bounded Contexts are and why they are the most important pattern in Domain-Driven Design
- How to identify boundaries where the same word means different things
- Context Mapping: how bounded contexts relate to each other
- The Anti-Corruption Layer pattern for protecting your model from external systems
- How bounded contexts naturally align with microservices
- Practical strategies for defining and enforcing context boundaries

## Why This Chapter Matters

In the previous chapter on Domain-Driven Design, we learned about Ubiquitous Language -- the shared vocabulary between developers and domain experts. But here is a critical insight that many teams miss: **Ubiquitous Language only works within a boundary.**

In a real business, the word "product" means one thing to the catalog team, another to the warehouse team, and something entirely different to the accounting team. Trying to create a single `Product` class that satisfies all three teams creates a monster -- a class with dozens of fields, half of which are irrelevant to any given use case.

Bounded Contexts solve this problem. They say: **each part of your system gets its own model, its own language, and its own boundary.** Inside that boundary, the model is consistent and clear. Between boundaries, you translate explicitly.

If you have ever seen a codebase where one "god object" is passed everywhere and every team adds their own fields to it, you have seen what happens without Bounded Contexts. This chapter shows you a better way.

---

## The Problem: One Word, Many Meanings

Consider an e-commerce company. The word "Customer" appears everywhere, but it means different things to different teams:

```
THE SAME WORD, DIFFERENT MEANINGS:

  Sales Team:                Shipping Team:             Billing Team:
  +------------------+      +------------------+       +------------------+
  | Customer         |      | Customer         |       | Customer         |
  |------------------|      |------------------|       |------------------|
  | - name           |      | - name           |       | - name           |
  | - email          |      | - shippingAddr   |       | - billingAddr    |
  | - preferences    |      | - deliveryNotes  |       | - paymentMethod  |
  | - leadSource     |      | - accessCode     |       | - creditLimit    |
  | - purchaseHist   |      | - preferredTime  |       | - taxId          |
  | - loyaltyTier    |      | - signatureReq   |       | - invoiceHistory |
  +------------------+      +------------------+       +------------------+

  If you merge all of these into ONE Customer class:

  +----------------------------------+
  | Customer (God Object)            |
  |----------------------------------|
  | - name, email, preferences       |
  | - leadSource, purchaseHistory    |
  | - loyaltyTier                    |
  | - shippingAddress                |
  | - deliveryNotes, accessCode      |
  | - preferredDeliveryTime          |
  | - signatureRequired              |
  | - billingAddress                 |
  | - paymentMethod, creditLimit     |
  | - taxId, invoiceHistory          |
  |----------------------------------|
  | 12+ fields, most irrelevant to   |
  | any single use case              |
  +----------------------------------+
```

This merged class is a maintenance nightmare. Every change risks breaking unrelated features. Every developer must understand fields they do not use. Testing requires setting up irrelevant data.

---

## What Is a Bounded Context?

A Bounded Context is an explicit boundary within which a particular domain model applies. Inside the boundary, every term has exactly one meaning, and the model is internally consistent.

```
BOUNDED CONTEXTS: Each context owns its own model.

  +----------------------+    +----------------------+    +----------------------+
  |   SALES CONTEXT      |    |  SHIPPING CONTEXT    |    |  BILLING CONTEXT     |
  |                      |    |                      |    |                      |
  | Customer:            |    | Recipient:           |    | Account:             |
  |  - name              |    |  - name              |    |  - name              |
  |  - email             |    |  - address           |    |  - billingAddress    |
  |  - preferences       |    |  - deliveryNotes     |    |  - paymentMethod     |
  |  - leadSource        |    |  - accessCode        |    |  - creditLimit       |
  |  - loyaltyTier       |    |  - preferredTime     |    |  - taxId             |
  |                      |    |                      |    |                      |
  | Order:               |    | Shipment:            |    | Invoice:             |
  |  - items             |    |  - packages          |    |  - lineItems         |
  |  - total             |    |  - carrier           |    |  - taxes             |
  |  - status            |    |  - trackingNumber    |    |  - amountDue         |
  +----------------------+    +----------------------+    +----------------------+

  Key insight: "Customer" in Sales, "Recipient" in Shipping, and
  "Account" in Billing are DIFFERENT models of the same real person.
  Each model contains only what that context needs.
```

### Key Properties of a Bounded Context

1. **Own language.** Terms inside the context have precise, unambiguous meanings.
2. **Own model.** Classes, entities, and value objects are defined for this context only.
3. **Explicit boundary.** You know exactly what is inside and outside the context.
4. **Independence.** Changes inside one context should not force changes in another.

---

## Identifying Bounded Contexts

How do you find the boundaries? Here are practical techniques:

### 1. Listen for Language Conflicts

When the same word means different things to different people, you have found a boundary.

```
LANGUAGE CONFLICT SIGNALS:

  "When you say 'order,' do you mean..."
    Sales:    "The customer's purchase request"
    Shipping: "The instruction to ship specific packages"
    Billing:  "The financial transaction to invoice"

  Each of these is a different concept that happens to share a name.
  Each belongs in its own Bounded Context.
```

### 2. Look for Different Lifecycles

If two concepts change at different rates or for different reasons, they probably belong in different contexts.

```
LIFECYCLE DIFFERENCES:

  Product Catalog Context:         Inventory Context:
  +---------------------+         +---------------------+
  | Product              |         | StockItem            |
  | - Changes when       |         | - Changes when       |
  |   marketing updates  |         |   warehouse receives |
  |   descriptions       |         |   or ships items     |
  | - Updated by: Content|         | - Updated by:        |
  |   team, monthly      |         |   Warehouse, hourly  |
  +---------------------+         +---------------------+

  Same physical product, different models, different change rates.
```

### 3. Look for Different Stakeholders

Different teams or departments often indicate different bounded contexts.

---

## Context Mapping: How Contexts Relate

Bounded Contexts do not exist in isolation. They must communicate. A Context Map shows how contexts relate to each other and who has power in the relationship.

```
E-COMMERCE CONTEXT MAP:

  +------------------+          +-------------------+
  |                  |  Order   |                   |
  |  SALES           |  Placed  |  ORDER            |
  |  CONTEXT         |--------->|  FULFILLMENT      |
  |                  |          |  CONTEXT           |
  | (Upstream)       |          |  (Downstream)     |
  +------------------+          +-------------------+
         |                              |
         |                              |
         | Customer                     | Shipment
         | Created                      | Ready
         v                              v
  +------------------+          +-------------------+
  |                  |          |                   |
  |  CUSTOMER        |          |  SHIPPING         |
  |  MANAGEMENT      |          |  CONTEXT          |
  |  CONTEXT         |          |                   |
  +------------------+          +-------------------+
         |                              |
         |                              |
         | Account                      | Delivery
         | Info                         | Confirmed
         v                              v
  +------------------+          +-------------------+
  |                  |  Invoice |                   |
  |  BILLING         |<--------|  NOTIFICATION     |
  |  CONTEXT         |  Request |  CONTEXT          |
  |                  |          |                   |
  +------------------+          +-------------------+

  Arrows show the direction of data flow and events.
  Upstream contexts produce data. Downstream contexts consume it.
```

### Common Relationship Patterns

#### 1. Customer-Supplier (Upstream-Downstream)

The upstream context provides data that the downstream context needs. The upstream team should accommodate reasonable requests from the downstream team.

```java
// UPSTREAM: Sales Context publishes an event when an order is placed
public class OrderPlacedEvent {
    private final String orderId;
    private final String customerId;
    private final List<OrderLineItem> items;
    private final Money totalAmount;
    private final Instant occurredAt;

    public OrderPlacedEvent(String orderId, String customerId,
                            List<OrderLineItem> items, Money totalAmount) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.items = List.copyOf(items);
        this.totalAmount = totalAmount;
        this.occurredAt = Instant.now();
    }

    // Getters omitted for brevity
}

// DOWNSTREAM: Fulfillment Context consumes the event
// and translates it into its own model
public class FulfillmentOrderCreator {

    public FulfillmentOrder createFrom(OrderPlacedEvent event) {
        // Translate from Sales language to Fulfillment language
        List<PickItem> pickList = event.getItems().stream()
            .map(item -> new PickItem(
                item.getSku(),           // Sales calls it "productId"
                item.getQuantity(),      // Fulfillment calls it "pickQuantity"
                lookupWarehouseLocation(item.getSku())
            ))
            .collect(Collectors.toList());

        return new FulfillmentOrder(
            event.getOrderId(),
            pickList,
            FulfillmentPriority.fromAmount(event.getTotalAmount())
        );
    }
}
```

```python
# UPSTREAM: Sales Context publishes an event
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: str
    customer_id: str
    items: List[dict]
    total_amount: float
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# DOWNSTREAM: Fulfillment Context translates it
class FulfillmentOrderCreator:

    def create_from(self, event: OrderPlacedEvent) -> "FulfillmentOrder":
        """Translate from Sales language to Fulfillment language."""
        pick_list = [
            PickItem(
                sku=item["product_id"],
                pick_quantity=item["quantity"],
                location=self._lookup_warehouse_location(item["product_id"])
            )
            for item in event.items
        ]

        return FulfillmentOrder(
            order_id=event.order_id,
            pick_list=pick_list,
            priority=FulfillmentPriority.from_amount(event.total_amount)
        )

    def _lookup_warehouse_location(self, sku: str) -> str:
        # Look up where this item is stored
        ...
```

#### 2. Shared Kernel

Two contexts share a small, common model that both teams agree on and maintain together.

```
SHARED KERNEL:

  +------------------+     +------------------+
  |                  |     |                  |
  |  SALES           |     |  BILLING         |
  |  CONTEXT         |     |  CONTEXT         |
  |                  |     |                  |
  |       +----------+-----+----------+       |
  |       |    SHARED KERNEL          |       |
  |       |  - Money value object     |       |
  |       |  - Currency enum          |       |
  |       |  - Address value object   |       |
  |       +---------------------------+       |
  |                  |     |                  |
  +------------------+     +------------------+

  WARNING: Keep the shared kernel SMALL.
  The larger it grows, the more coupling you create.
```

#### 3. Conformist

The downstream context conforms to the upstream context's model without any translation. This is common when integrating with external APIs you cannot change.

#### 4. Anti-Corruption Layer (ACL)

The downstream context creates a translation layer to protect its model from the upstream context's model.

---

## The Anti-Corruption Layer Pattern

The Anti-Corruption Layer is one of the most important patterns for maintaining clean boundaries. It acts as a translator between two contexts, ensuring that one context's model does not leak into another.

```
ANTI-CORRUPTION LAYER:

  +------------------+     +---+     +------------------+
  |                  |     |   |     |                  |
  |  EXTERNAL        |     | A |     |  YOUR            |
  |  PAYMENT         |---->| C |---->|  BILLING         |
  |  GATEWAY         |     | L |     |  CONTEXT         |
  |                  |     |   |     |                  |
  |  Their model:    |     |   |     |  Your model:     |
  |  - txn_id        |     | T |     |  - paymentId     |
  |  - amt_cents     |     | R |     |  - amount (Money)|
  |  - ccy_code      |     | A |     |  - currency      |
  |  - stat          |     | N |     |  - status        |
  |  - cust_ref      |     | S |     |  - customerId    |
  |  - err_cd        |     | L |     |  - failureReason |
  |                  |     | A |     |                  |
  |  Ugly, cryptic   |     | T |     |  Clean, clear    |
  |  abbreviations   |     | E |     |  domain language |
  +------------------+     +---+     +------------------+
```

### Java Example

```java
// EXTERNAL SYSTEM: Payment gateway response (their model, their language)
// You cannot change this -- it comes from a third-party API
public class PayGatewayResponse {
    public String txn_id;
    public int amt_cents;
    public String ccy_code;
    public String stat;       // "OK", "FAIL", "PEND"
    public String cust_ref;
    public String err_cd;     // "E001", "E002", etc.
}

// ANTI-CORRUPTION LAYER: Translates external model to your domain model
public class PaymentGatewayAdapter {

    public PaymentResult translate(PayGatewayResponse response) {
        return new PaymentResult(
            new PaymentId(response.txn_id),
            Money.ofMinorUnits(response.amt_cents,
                              Currency.fromCode(response.ccy_code)),
            translateStatus(response.stat),
            new CustomerId(response.cust_ref),
            translateError(response.err_cd)
        );
    }

    private PaymentStatus translateStatus(String stat) {
        return switch (stat) {
            case "OK"   -> PaymentStatus.COMPLETED;
            case "FAIL" -> PaymentStatus.FAILED;
            case "PEND" -> PaymentStatus.PENDING;
            default     -> throw new UnknownPaymentStatusException(stat);
        };
    }

    private FailureReason translateError(String errorCode) {
        if (errorCode == null) return null;
        return switch (errorCode) {
            case "E001" -> FailureReason.INSUFFICIENT_FUNDS;
            case "E002" -> FailureReason.CARD_EXPIRED;
            case "E003" -> FailureReason.FRAUD_SUSPECTED;
            default     -> FailureReason.UNKNOWN;
        };
    }
}

// YOUR DOMAIN MODEL: Clean, expressive, uses your Ubiquitous Language
public record PaymentResult(
    PaymentId paymentId,
    Money amount,
    PaymentStatus status,
    CustomerId customerId,
    FailureReason failureReason
) {
    public boolean isSuccessful() {
        return status == PaymentStatus.COMPLETED;
    }

    public boolean requiresRetry() {
        return status == PaymentStatus.FAILED
            && failureReason != FailureReason.FRAUD_SUSPECTED;
    }
}
```

```python
# EXTERNAL SYSTEM: Payment gateway response (their ugly model)
# You cannot change this -- it comes from a third-party API

# ANTI-CORRUPTION LAYER: Translates external to your domain
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class PaymentStatus(Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"

class FailureReason(Enum):
    INSUFFICIENT_FUNDS = "insufficient_funds"
    CARD_EXPIRED = "card_expired"
    FRAUD_SUSPECTED = "fraud_suspected"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class PaymentResult:
    """Your clean domain model."""
    payment_id: str
    amount_cents: int
    currency: str
    status: PaymentStatus
    customer_id: str
    failure_reason: Optional[FailureReason] = None

    @property
    def is_successful(self) -> bool:
        return self.status == PaymentStatus.COMPLETED

    @property
    def requires_retry(self) -> bool:
        return (self.status == PaymentStatus.FAILED
                and self.failure_reason != FailureReason.FRAUD_SUSPECTED)


class PaymentGatewayAdapter:
    """Anti-Corruption Layer: translates external model to domain model."""

    STATUS_MAP = {
        "OK": PaymentStatus.COMPLETED,
        "FAIL": PaymentStatus.FAILED,
        "PEND": PaymentStatus.PENDING,
    }

    ERROR_MAP = {
        "E001": FailureReason.INSUFFICIENT_FUNDS,
        "E002": FailureReason.CARD_EXPIRED,
        "E003": FailureReason.FRAUD_SUSPECTED,
    }

    def translate(self, response: dict) -> PaymentResult:
        status = self.STATUS_MAP.get(response["stat"])
        if status is None:
            raise ValueError(f"Unknown payment status: {response['stat']}")

        failure_reason = None
        if response.get("err_cd"):
            failure_reason = self.ERROR_MAP.get(
                response["err_cd"], FailureReason.UNKNOWN
            )

        return PaymentResult(
            payment_id=response["txn_id"],
            amount_cents=response["amt_cents"],
            currency=response["ccy_code"],
            status=status,
            customer_id=response["cust_ref"],
            failure_reason=failure_reason,
        )
```

### Why the Anti-Corruption Layer Matters

Without an ACL, the external system's model leaks into your code:

```
WITHOUT ACL (Bad):

  Your service methods use external types directly:

  def process_payment(self, gateway_response):
      if gateway_response["stat"] == "OK":        # External language
          amount = gateway_response["amt_cents"]    # External naming
          # Your code is now coupled to their abbreviations

WITH ACL (Good):

  Your service methods use your own domain types:

  def process_payment(self, result: PaymentResult):
      if result.is_successful:                      # Your language
          amount = result.amount_cents               # Your naming
          # Your code is clean and independent
```

---

## Bounded Contexts and Microservices

There is a natural alignment between bounded contexts and microservices, but they are not the same thing.

```
BOUNDED CONTEXTS vs MICROSERVICES:

  +-----------------------------------------------------+
  |  Bounded Context = LOGICAL boundary                  |
  |  (A model boundary in your domain)                   |
  |                                                      |
  |  Microservice = DEPLOYMENT boundary                  |
  |  (A separately deployable unit)                      |
  +-----------------------------------------------------+

  IDEAL ALIGNMENT:

  +------------------+    +------------------+    +------------------+
  |  Sales Context   |    |  Shipping Context|    |  Billing Context |
  |  = Sales Service |    |  = Ship Service  |    |  = Bill Service  |
  +------------------+    +------------------+    +------------------+
       One bounded context per microservice

  COMMON MISTAKE:

  +------------------------------------------+
  |  One Big Monolith Service                 |
  |  +----------+  +----------+  +----------+|
  |  | Sales    |  | Shipping |  | Billing  ||
  |  | Context  |  | Context  |  | Context  ||
  |  +----------+  +----------+  +----------+|
  +------------------------------------------+
       Multiple contexts in one service (OK for starting)

  WORSE MISTAKE:

  +----------+  +----------+  +----------+
  | Service1 |  | Service2 |  | Service3 |
  | Part of  |  | Part of  |  | Part of  |
  | Sales    |  | Sales    |  | Sales    |
  +----------+  +----------+  +----------+
       One context split across multiple services (BAD)
```

### Guidelines for Alignment

1. **Start with a monolith and identify bounded contexts first.** Do not jump to microservices.
2. **One bounded context per microservice** is the ideal target.
3. **Never split one bounded context across multiple microservices.** This creates distributed coupling -- the worst kind.
4. **Multiple bounded contexts in one deployment** is acceptable when starting out (modular monolith).

---

## Practical Example: E-Commerce System

Let us design the bounded contexts for an e-commerce system step by step.

### Step 1: Identify the Sub-Domains

```
E-COMMERCE SUB-DOMAINS:

  +---------------+  +---------------+  +---------------+
  |   Product     |  |   Ordering    |  |   Shipping    |
  |   Catalog     |  |               |  |               |
  +---------------+  +---------------+  +---------------+

  +---------------+  +---------------+  +---------------+
  |   Payment     |  |   Customer    |  |   Inventory   |
  |   Processing  |  |   Management  |  |               |
  +---------------+  +---------------+  +---------------+
```

### Step 2: Define the Models in Each Context

```java
// PRODUCT CATALOG CONTEXT
// Here, a "Product" is rich with marketing information
public class Product {
    private final ProductId id;
    private String name;
    private String description;
    private List<String> images;
    private List<Category> categories;
    private List<ProductAttribute> attributes;  // color, size, material
    private Money listPrice;

    public void updateDescription(String description) {
        // Marketing team updates this
        this.description = description;
    }
}

// INVENTORY CONTEXT
// Here, the same physical product is a "StockItem" -- only quantity matters
public class StockItem {
    private final String sku;
    private int quantityOnHand;
    private int quantityReserved;
    private WarehouseLocation location;

    public int availableQuantity() {
        return quantityOnHand - quantityReserved;
    }

    public void reserve(int quantity) {
        if (quantity > availableQuantity()) {
            throw new InsufficientStockException(sku, quantity, availableQuantity());
        }
        this.quantityReserved += quantity;
    }

    public void confirmPickup(int quantity) {
        this.quantityOnHand -= quantity;
        this.quantityReserved -= quantity;
    }
}

// ORDERING CONTEXT
// Here, it is an "OrderItem" -- just a line in an order
public class OrderItem {
    private final String productId;
    private final String productName;   // Snapshot at time of order
    private final Money unitPrice;      // Snapshot at time of order
    private final int quantity;

    public Money lineTotal() {
        return unitPrice.multiply(quantity);
    }
}
```

```python
# PRODUCT CATALOG CONTEXT
@dataclass
class Product:
    """In the catalog context, a product has rich marketing data."""
    id: str
    name: str
    description: str
    images: list[str]
    categories: list[str]
    attributes: dict[str, str]  # color, size, material
    list_price: float


# INVENTORY CONTEXT
@dataclass
class StockItem:
    """In inventory context, same physical product is just quantity."""
    sku: str
    quantity_on_hand: int
    quantity_reserved: int
    warehouse_location: str

    @property
    def available_quantity(self) -> int:
        return self.quantity_on_hand - self.quantity_reserved

    def reserve(self, quantity: int) -> None:
        if quantity > self.available_quantity:
            raise InsufficientStockError(
                f"Cannot reserve {quantity} of {self.sku}. "
                f"Only {self.available_quantity} available."
            )
        self.quantity_reserved += quantity


# ORDERING CONTEXT
@dataclass(frozen=True)
class OrderItem:
    """In ordering context, it is a line item with a price snapshot."""
    product_id: str
    product_name: str   # Snapshot at time of order
    unit_price: float   # Snapshot at time of order
    quantity: int

    @property
    def line_total(self) -> float:
        return self.unit_price * self.quantity
```

### Step 3: Define How Contexts Communicate

```java
// When an order is placed in the ORDERING CONTEXT,
// it publishes an event for other contexts to react to.

// ORDERING CONTEXT publishes:
public record OrderPlacedEvent(
    String orderId,
    String customerId,
    List<OrderItemSnapshot> items,
    Money totalAmount,
    Instant occurredAt
) {}

// INVENTORY CONTEXT listens and reserves stock:
public class InventoryEventHandler {
    private final StockItemRepository stockItems;

    public void onOrderPlaced(OrderPlacedEvent event) {
        for (OrderItemSnapshot item : event.items()) {
            StockItem stock = stockItems.findBySku(item.sku());
            stock.reserve(item.quantity());
            stockItems.save(stock);
        }
    }
}

// PAYMENT CONTEXT listens and initiates payment:
public class PaymentEventHandler {
    private final PaymentService payments;

    public void onOrderPlaced(OrderPlacedEvent event) {
        payments.initiatePayment(
            new PaymentRequest(
                event.orderId(),
                event.customerId(),
                event.totalAmount()
            )
        );
    }
}
```

```python
# INVENTORY CONTEXT listens and reserves stock
class InventoryEventHandler:
    def __init__(self, stock_repository):
        self.stock_repository = stock_repository

    def on_order_placed(self, event: dict) -> None:
        for item in event["items"]:
            stock = self.stock_repository.find_by_sku(item["sku"])
            stock.reserve(item["quantity"])
            self.stock_repository.save(stock)


# PAYMENT CONTEXT listens and initiates payment
class PaymentEventHandler:
    def __init__(self, payment_service):
        self.payment_service = payment_service

    def on_order_placed(self, event: dict) -> None:
        self.payment_service.initiate_payment(
            order_id=event["order_id"],
            customer_id=event["customer_id"],
            amount=event["total_amount"],
        )
```

---

## Enforcing Boundaries in Code

Bounded contexts are only useful if you enforce their boundaries in your code. Here are practical techniques:

### Package/Module Structure

```
JAVA PROJECT STRUCTURE:

  com.shop/
  +-- catalog/                    # Product Catalog Context
  |   +-- domain/
  |   |   +-- Product.java
  |   |   +-- Category.java
  |   +-- application/
  |   |   +-- ProductService.java
  |   +-- infrastructure/
  |       +-- ProductRepository.java
  |
  +-- ordering/                   # Ordering Context
  |   +-- domain/
  |   |   +-- Order.java
  |   |   +-- OrderItem.java
  |   +-- application/
  |   |   +-- OrderService.java
  |   +-- infrastructure/
  |       +-- OrderRepository.java
  |
  +-- inventory/                  # Inventory Context
  |   +-- domain/
  |   |   +-- StockItem.java
  |   +-- application/
  |   |   +-- StockService.java
  |   +-- infrastructure/
  |       +-- StockRepository.java
  |
  +-- shared/                     # Shared Kernel (keep small!)
      +-- Money.java
      +-- Currency.java


PYTHON PROJECT STRUCTURE:

  shop/
  +-- catalog/                    # Product Catalog Context
  |   +-- __init__.py
  |   +-- domain.py
  |   +-- services.py
  |   +-- repository.py
  |
  +-- ordering/                   # Ordering Context
  |   +-- __init__.py
  |   +-- domain.py
  |   +-- services.py
  |   +-- repository.py
  |
  +-- inventory/                  # Inventory Context
  |   +-- __init__.py
  |   +-- domain.py
  |   +-- services.py
  |   +-- repository.py
  |
  +-- shared/                     # Shared Kernel (keep small!)
      +-- __init__.py
      +-- money.py
```

### Rules for Boundary Enforcement

1. **No direct imports across contexts.** The ordering context should never import from the inventory context's domain.
2. **Communicate through events or defined interfaces.** Use published events, APIs, or shared contracts.
3. **Each context has its own database schema (ideally).** No shared tables between contexts.
4. **Use architecture fitness functions** to automatically check for boundary violations in CI.

```java
// BAD: Direct dependency across context boundaries
// ordering/application/OrderService.java
import com.shop.inventory.domain.StockItem;  // VIOLATION!

public class OrderService {
    public void placeOrder(Order order) {
        // Directly reaching into another context
        StockItem stock = stockRepo.findBySku(order.getSku());  // WRONG
        stock.reserve(order.getQuantity());
    }
}

// GOOD: Communicate through an event or interface
// ordering/application/OrderService.java
public class OrderService {
    private final EventPublisher events;

    public void placeOrder(Order order) {
        order.place();
        orderRepo.save(order);
        // Publish event -- inventory context will handle reservation
        events.publish(new OrderPlacedEvent(
            order.getId(), order.getItems()
        ));
    }
}
```

---

## Common Mistakes

### Mistake 1: Making Bounded Contexts Too Small

Creating a bounded context for every entity leads to excessive complexity and constant inter-context communication.

**Fix:** A bounded context should encompass a cohesive set of related concepts, not a single class. If two concepts always change together, they belong in the same context.

### Mistake 2: Sharing a Database Between Contexts

When two contexts read and write the same tables, changes in one context can break the other.

**Fix:** Each context should own its data. Use events to synchronize data between contexts.

### Mistake 3: No Anti-Corruption Layer for External Systems

Directly using an external API's response types in your domain model couples your code to their design decisions.

**Fix:** Always create an ACL when integrating with external systems. Translate their model into your domain language.

### Mistake 4: Letting the Shared Kernel Grow

Starting with a small shared kernel is fine. But over time, teams add more and more to it, creating tight coupling between contexts.

**Fix:** Regularly review the shared kernel. If it grows beyond a few value objects, split it or move things into individual contexts.

### Mistake 5: Ignoring Organizational Boundaries

Bounded contexts should align with team boundaries (Conway's Law). A single team should own a single bounded context.

**Fix:** Map your contexts to your team structure. If two teams are working on one context, either split the context or merge the teams.

---

## Best Practices

1. **Start with the domain, not the technology.** Identify bounded contexts through domain analysis, not by choosing microservices first.
2. **Use events for inter-context communication.** Events decouple contexts better than direct calls.
3. **Keep the shared kernel minimal.** Only share what is truly common (Money, Currency, basic value objects).
4. **Build an Anti-Corruption Layer for every external integration.** Never let external models leak into your domain.
5. **Enforce boundaries with package structure and build rules.** Make violations visible and hard to introduce.
6. **Align contexts with team ownership.** One team, one context. This follows Conway's Law.
7. **Document your context map.** Keep it visible and up-to-date as a team reference.
8. **Evolve boundaries as understanding deepens.** Your first context map will be wrong. Refine it as you learn.

---

## Quick Summary

```
BOUNDED CONTEXTS AT A GLANCE:

  What:    An explicit boundary within which a domain model applies
  Why:     The same word means different things in different parts
           of a business. One model cannot serve all needs.
  How:     Define separate models per context. Communicate through
           events and translation layers.

  Key patterns:
  +---------------------------+----------------------------------+
  | Pattern                   | When to use                      |
  +---------------------------+----------------------------------+
  | Customer-Supplier         | Upstream provides, downstream    |
  |                           | consumes. Teams can negotiate.   |
  | Shared Kernel             | Two contexts share a small,      |
  |                           | jointly maintained model.         |
  | Anti-Corruption Layer     | Protect your model from an       |
  |                           | external or legacy system.        |
  | Conformist                | You cannot change the upstream.   |
  |                           | You just conform to their model. |
  | Separate Ways             | No integration needed. Contexts  |
  |                           | are completely independent.       |
  +---------------------------+----------------------------------+
```

---

## Key Points

- A Bounded Context is an explicit boundary where a particular domain model applies and every term has one clear meaning.
- The same real-world concept (like "Customer") can and should have different representations in different contexts.
- Context Mapping shows how bounded contexts relate: Customer-Supplier, Shared Kernel, Anti-Corruption Layer, Conformist.
- The Anti-Corruption Layer translates between an external model and your domain model, protecting your code from external design decisions.
- Bounded contexts align naturally with microservices, but start with a modular monolith and extract services later.
- Enforce boundaries through package structure, build rules, and architectural fitness functions.
- Communicate between contexts using events, not direct calls or shared databases.

---

## Practice Questions

1. You are building a hospital system. The word "Patient" is used by the admissions desk, the medical staff, and the billing department. Each group needs different information about the patient. How would you model this using bounded contexts?

2. Your team integrates with a third-party shipping API that returns responses with cryptic field names like `shp_stat`, `dlv_dt`, and `rcpt_nm`. How would you protect your domain model from this external API's design?

3. Two bounded contexts both need to work with monetary values (amounts with currency). Should you duplicate the `Money` class in each context, or share it? What are the trade-offs?

4. Your e-commerce system has a Product Catalog context and an Inventory context. A developer proposes that both contexts should read from the same `products` database table. What problems could this cause, and what would you suggest instead?

5. A team has split their Order Management bounded context into three microservices: one for creating orders, one for processing payments, and one for shipping. Each service needs to access the Order entity. What is wrong with this design?

---

## Exercises

### Exercise 1: Context Map for a University System

Draw a context map for a university system with these sub-domains: Student Enrollment, Course Management, Grading, Financial Aid, and Library. For each pair of related contexts, identify the relationship type (Customer-Supplier, Shared Kernel, ACL, etc.) and explain why.

### Exercise 2: Build an Anti-Corruption Layer

You integrate with a legacy HR system that returns employee data in this format:

```json
{
  "emp_no": "E12345",
  "f_nm": "Jane",
  "l_nm": "Smith",
  "dept_cd": "ENG",
  "sal_grade": 7,
  "mgr_emp_no": "E00042",
  "hire_dt": "20190315"
}
```

Write an Anti-Corruption Layer (in Java or Python) that translates this into a clean `Employee` domain object with proper field names, parsed dates, and meaningful types.

### Exercise 3: Identify Bounded Contexts

You are building a food delivery platform. Stakeholder interviews reveal these concepts: Restaurant Menu, Customer Orders, Delivery Tracking, Payment Processing, Restaurant Ratings, Driver Management, and Promotions. Group these into bounded contexts, define the key entity in each context, and explain how the contexts communicate.

---

## What Is Next?

Now that you understand how to define clear boundaries between different parts of your domain, the next chapter explores Dependency Injection -- a technique for managing dependencies within a bounded context. You will learn how constructor injection, DI containers, and the dependency inversion principle work together to make your code testable, flexible, and loosely coupled.
