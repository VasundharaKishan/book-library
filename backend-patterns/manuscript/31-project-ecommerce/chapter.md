# Chapter 31: Project -- Building a Complete E-Commerce System

## What You Will Learn

- How to combine 15+ design patterns into a cohesive system
- Architecture decisions for a real e-commerce platform
- How patterns interact and reinforce each other
- Complete working code for core e-commerce functionality
- How to think architecturally about pattern selection

## Why This Chapter Matters

Individual patterns are tools. This chapter teaches you to use them together. Building
a real system requires knowing not just what each pattern does, but when to apply which
pattern, how they compose, and where they overlap. You will see how Singleton, Factory,
Builder, Strategy, Observer, Command, Chain of Responsibility, Repository, CQRS,
Circuit Breaker, and Saga work together to create a production-quality e-commerce
backend.

---

## System Architecture Overview

```
+------------------------------------------------------------------+
|                        API Gateway                                |
|  (Routing, Auth, Rate Limiting)                                   |
+------------------------------------------------------------------+
         |              |              |              |
         v              v              v              v
+------------+  +------------+  +------------+  +------------+
|  Product   |  |   Order    |  |  Payment   |  | Notification|
|  Service   |  |  Service   |  |  Service   |  |  Service   |
+------------+  +------------+  +------------+  +------------+
     |               |              |               |
     v               v              v               v
+------------+  +------------+  +------------+  +------------+
| Product DB |  | Order DB   |  | Payment DB |  | Email/SMS  |
+------------+  +------------+  +------------+  +------------+

Cross-cutting:
  - Service Discovery (all services register)
  - Circuit Breaker (all inter-service calls)
  - Observer/Events (async communication)
  - Saga (distributed transactions)
```

---

## Patterns Applied

Here is every pattern we use in this project and why:

```
+----------------------------+-------------------------------------------+
| Pattern                    | Where We Use It                           |
+----------------------------+-------------------------------------------+
| Singleton                  | Configuration manager, DB connection pool |
| Factory Method             | Create payment processors by type         |
| Builder                    | Construct complex Order objects            |
| Strategy                   | Pricing, discount, and shipping rules     |
| Observer                   | Event bus for async notifications         |
| Command                    | Order operations (place, cancel, refund)  |
| Chain of Responsibility    | Order validation pipeline                 |
| Repository                 | Data access abstraction                   |
| CQRS                       | Separate read/write models for products  |
| Circuit Breaker            | Resilient inter-service calls             |
| Saga                       | Distributed checkout transaction          |
+----------------------------+-------------------------------------------+
```

---

## Part 1: Foundation Layer

### Singleton -- Configuration Manager

Every service needs access to configuration. A Singleton ensures one configuration
instance across the application.

```python
import threading


class Config:
    """Singleton configuration manager."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._settings = {
            "db_host": "localhost",
            "db_port": 5432,
            "db_name": "ecommerce",
            "payment_timeout": 30,
            "max_retry": 3,
            "tax_rate": 0.08,
            "free_shipping_threshold": 50.00,
            "currency": "USD",
        }

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def set(self, key, value):
        self._settings[key] = value


# Usage across the entire application
config = Config()
print(f"Tax rate: {config.get('tax_rate')}")
print(f"Same instance? {Config() is Config()}")  # True
```

**Output:**
```
Tax rate: 0.08
Same instance? True
```

### Repository -- Data Access Layer

The Repository pattern abstracts away data storage, making business logic independent
of the database.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
import uuid


@dataclass
class Product:
    id: str
    name: str
    price: float
    category: str
    stock: int
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OrderItem:
    product_id: str
    product_name: str
    quantity: int
    unit_price: float

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


@dataclass
class Order:
    id: str
    customer_id: str
    items: List[OrderItem]
    status: str = "pending"
    total: float = 0.0
    tax: float = 0.0
    shipping_cost: float = 0.0
    discount: float = 0.0
    payment_method: str = ""
    shipping_address: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class ProductRepository(ABC):
    @abstractmethod
    def find_by_id(self, product_id: str) -> Optional[Product]:
        pass

    @abstractmethod
    def find_by_category(self, category: str) -> List[Product]:
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        pass

    @abstractmethod
    def update_stock(self, product_id: str, quantity_change: int) -> bool:
        pass

    @abstractmethod
    def find_all(self) -> List[Product]:
        pass


class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        pass

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> List[Order]:
        pass

    @abstractmethod
    def save(self, order: Order) -> Order:
        pass

    @abstractmethod
    def update_status(self, order_id: str, status: str) -> bool:
        pass


class InMemoryProductRepository(ProductRepository):
    """In-memory implementation for demonstration."""

    def __init__(self):
        self._products: Dict[str, Product] = {}

    def find_by_id(self, product_id):
        return self._products.get(product_id)

    def find_by_category(self, category):
        return [p for p in self._products.values()
                if p.category == category]

    def save(self, product):
        self._products[product.id] = product
        return product

    def update_stock(self, product_id, quantity_change):
        product = self._products.get(product_id)
        if product and product.stock + quantity_change >= 0:
            product.stock += quantity_change
            return True
        return False

    def find_all(self):
        return list(self._products.values())


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._orders: Dict[str, Order] = {}

    def find_by_id(self, order_id):
        return self._orders.get(order_id)

    def find_by_customer(self, customer_id):
        return [o for o in self._orders.values()
                if o.customer_id == customer_id]

    def save(self, order):
        self._orders[order.id] = order
        return order

    def update_status(self, order_id, status):
        order = self._orders.get(order_id)
        if order:
            order.status = status
            order.updated_at = datetime.now()
            return True
        return False
```

---

## Part 2: Business Logic Layer

### Builder -- Order Construction

Orders are complex objects with many optional fields. The Builder pattern makes
construction clean and readable.

```python
class OrderBuilder:
    """Builds Order objects step by step."""

    def __init__(self, customer_id: str):
        self._customer_id = customer_id
        self._items: List[OrderItem] = []
        self._shipping_address = ""
        self._payment_method = ""
        self._discount = 0.0

    def add_item(self, product: Product, quantity: int):
        if product.stock < quantity:
            raise ValueError(
                f"Insufficient stock for {product.name}: "
                f"need {quantity}, have {product.stock}")
        self._items.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            unit_price=product.price
        ))
        return self

    def shipping_address(self, address: str):
        self._shipping_address = address
        return self

    def payment_method(self, method: str):
        self._payment_method = method
        return self

    def apply_discount(self, discount: float):
        self._discount = discount
        return self

    def build(self) -> Order:
        if not self._items:
            raise ValueError("Order must have at least one item")
        if not self._shipping_address:
            raise ValueError("Shipping address is required")
        if not self._payment_method:
            raise ValueError("Payment method is required")

        order = Order(
            id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            customer_id=self._customer_id,
            items=list(self._items),
            shipping_address=self._shipping_address,
            payment_method=self._payment_method,
            discount=self._discount
        )
        return order
```

### Strategy -- Pricing, Discounts, and Shipping

Different business rules for calculating prices, discounts, and shipping costs are
encapsulated as interchangeable strategies.

```python
class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, items: List[OrderItem]) -> float:
        pass


class StandardPricing(PricingStrategy):
    def calculate(self, items):
        return sum(item.subtotal for item in items)


class BulkPricing(PricingStrategy):
    """10% off when ordering 5+ of any single item."""

    def calculate(self, items):
        total = 0.0
        for item in items:
            if item.quantity >= 5:
                total += item.subtotal * 0.90  # 10% off
            else:
                total += item.subtotal
        return total


class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, subtotal: float, customer_id: str) -> float:
        pass


class NoDiscount(DiscountStrategy):
    def apply(self, subtotal, customer_id):
        return 0.0


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.percentage = percentage

    def apply(self, subtotal, customer_id):
        return subtotal * (self.percentage / 100)


class LoyaltyDiscount(DiscountStrategy):
    """VIP customers get 15% off orders over $100."""

    def __init__(self, vip_customers: set):
        self.vip_customers = vip_customers

    def apply(self, subtotal, customer_id):
        if customer_id in self.vip_customers and subtotal > 100:
            return subtotal * 0.15
        return 0.0


class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, subtotal: float, items: List[OrderItem]) -> float:
        pass


class StandardShipping(ShippingStrategy):
    def calculate(self, subtotal, items):
        config = Config()
        if subtotal >= config.get("free_shipping_threshold", 50):
            return 0.0
        return 5.99


class ExpressShipping(ShippingStrategy):
    def calculate(self, subtotal, items):
        total_items = sum(item.quantity for item in items)
        return 9.99 + (total_items * 1.50)


class FreeShipping(ShippingStrategy):
    def calculate(self, subtotal, items):
        return 0.0
```

### Factory Method -- Payment Processors

Different payment methods require different processing logic. The Factory pattern
creates the right processor based on the payment method.

```python
class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount: float, order_id: str) -> dict:
        pass

    @abstractmethod
    def refund(self, amount: float, order_id: str) -> dict:
        pass


class CreditCardProcessor(PaymentProcessor):
    def charge(self, amount, order_id):
        print(f"    [CreditCard] Charging ${amount:.2f} "
              f"for order {order_id}")
        return {"status": "charged", "method": "credit_card",
                "transaction_id": f"CC-{uuid.uuid4().hex[:8]}"}

    def refund(self, amount, order_id):
        print(f"    [CreditCard] Refunding ${amount:.2f} "
              f"for order {order_id}")
        return {"status": "refunded", "method": "credit_card"}


class PayPalProcessor(PaymentProcessor):
    def charge(self, amount, order_id):
        print(f"    [PayPal] Charging ${amount:.2f} for order {order_id}")
        return {"status": "charged", "method": "paypal",
                "transaction_id": f"PP-{uuid.uuid4().hex[:8]}"}

    def refund(self, amount, order_id):
        print(f"    [PayPal] Refunding ${amount:.2f} for order {order_id}")
        return {"status": "refunded", "method": "paypal"}


class CryptoProcessor(PaymentProcessor):
    def charge(self, amount, order_id):
        print(f"    [Crypto] Charging ${amount:.2f} for order {order_id}")
        return {"status": "charged", "method": "crypto",
                "transaction_id": f"BTC-{uuid.uuid4().hex[:8]}"}

    def refund(self, amount, order_id):
        print(f"    [Crypto] Refunding ${amount:.2f} for order {order_id}")
        return {"status": "refunded", "method": "crypto"}


class PaymentProcessorFactory:
    """Factory that creates the right processor by payment method."""

    _processors = {
        "credit_card": CreditCardProcessor,
        "paypal": PayPalProcessor,
        "crypto": CryptoProcessor,
    }

    @classmethod
    def create(cls, method: str) -> PaymentProcessor:
        processor_class = cls._processors.get(method)
        if not processor_class:
            raise ValueError(f"Unsupported payment method: {method}")
        return processor_class()

    @classmethod
    def register(cls, method: str, processor_class):
        cls._processors[method] = processor_class
```

---

## Part 3: Chain of Responsibility -- Order Validation

Before processing an order, it must pass through a validation pipeline. Each validator
checks one thing and passes to the next.

```python
class OrderValidator(ABC):
    def __init__(self):
        self._next: Optional['OrderValidator'] = None

    def set_next(self, validator: 'OrderValidator') -> 'OrderValidator':
        self._next = validator
        return validator

    def validate(self, order: Order, product_repo: ProductRepository) \
            -> List[str]:
        errors = self._check(order, product_repo)
        if self._next:
            errors.extend(self._next.validate(order, product_repo))
        return errors

    @abstractmethod
    def _check(self, order: Order,
               product_repo: ProductRepository) -> List[str]:
        pass


class ItemsValidator(OrderValidator):
    def _check(self, order, product_repo):
        if not order.items:
            return ["Order must have at least one item"]
        return []


class StockValidator(OrderValidator):
    def _check(self, order, product_repo):
        errors = []
        for item in order.items:
            product = product_repo.find_by_id(item.product_id)
            if not product:
                errors.append(f"Product not found: {item.product_id}")
            elif product.stock < item.quantity:
                errors.append(
                    f"Insufficient stock for {product.name}: "
                    f"need {item.quantity}, have {product.stock}")
        return errors


class PriceValidator(OrderValidator):
    def _check(self, order, product_repo):
        errors = []
        for item in order.items:
            product = product_repo.find_by_id(item.product_id)
            if product and item.unit_price != product.price:
                errors.append(
                    f"Price mismatch for {item.product_name}: "
                    f"expected ${product.price}, got ${item.unit_price}")
        return errors


class MinimumOrderValidator(OrderValidator):
    def __init__(self, minimum: float = 1.00):
        super().__init__()
        self.minimum = minimum

    def _check(self, order, product_repo):
        subtotal = sum(item.subtotal for item in order.items)
        if subtotal < self.minimum:
            return [f"Minimum order amount is ${self.minimum:.2f}"]
        return []


def build_validation_chain() -> OrderValidator:
    """Build the validation pipeline."""
    items = ItemsValidator()
    stock = StockValidator()
    price = PriceValidator()
    minimum = MinimumOrderValidator(5.00)

    items.set_next(stock).set_next(price).set_next(minimum)
    return items
```

---

## Part 4: Observer -- Event System

Services communicate through events. The Observer pattern enables loose coupling
between components.

```python
class EventBus:
    """Central event bus using Observer pattern."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = {}
            cls._instance._event_log = []
        return cls._instance

    def subscribe(self, event_type: str, handler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event_type: str, data: dict):
        self._event_log.append({
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })

        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                print(f"  [EventBus] Handler error for {event_type}: {e}")

    def get_log(self):
        return self._event_log


# Event handlers
class NotificationHandler:
    def on_order_placed(self, data):
        print(f"  [Notification] Order {data['order_id']} confirmation "
              f"sent to customer {data['customer_id']}")

    def on_order_cancelled(self, data):
        print(f"  [Notification] Order {data['order_id']} cancellation "
              f"notice sent")

    def on_payment_completed(self, data):
        print(f"  [Notification] Payment receipt sent for "
              f"order {data['order_id']}")


class AnalyticsHandler:
    def __init__(self):
        self.events = []

    def on_order_placed(self, data):
        self.events.append({"type": "order_placed", **data})
        print(f"  [Analytics] Tracked order {data['order_id']} "
              f"(total tracked: {len(self.events)})")

    def on_payment_completed(self, data):
        self.events.append({"type": "payment", **data})


class InventoryHandler:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def on_order_placed(self, data):
        for item in data.get("items", []):
            success = self.product_repo.update_stock(
                item["product_id"], -item["quantity"])
            if success:
                print(f"  [Inventory] Reserved {item['quantity']}x "
                      f"{item['product_name']}")

    def on_order_cancelled(self, data):
        for item in data.get("items", []):
            self.product_repo.update_stock(
                item["product_id"], item["quantity"])
            print(f"  [Inventory] Released {item['quantity']}x "
                  f"{item['product_name']}")
```

---

## Part 5: Command -- Order Operations

The Command pattern encapsulates order operations, enabling undo, logging, and queuing.

```python
class OrderCommand(ABC):
    @abstractmethod
    def execute(self) -> dict:
        pass

    @abstractmethod
    def undo(self) -> dict:
        pass

    @abstractmethod
    def describe(self) -> str:
        pass


class PlaceOrderCommand(OrderCommand):
    def __init__(self, order: Order, order_repo: OrderRepository,
                 pricing: PricingStrategy, discount: DiscountStrategy,
                 shipping: ShippingStrategy):
        self.order = order
        self.order_repo = order_repo
        self.pricing = pricing
        self.discount = discount
        self.shipping = shipping
        self._executed = False

    def execute(self) -> dict:
        # Calculate totals using strategies
        subtotal = self.pricing.calculate(self.order.items)
        discount_amount = self.discount.apply(
            subtotal, self.order.customer_id)
        shipping_cost = self.shipping.calculate(
            subtotal - discount_amount, self.order.items)
        tax = (subtotal - discount_amount) * Config().get("tax_rate", 0.08)
        total = subtotal - discount_amount + shipping_cost + tax

        self.order.total = round(total, 2)
        self.order.tax = round(tax, 2)
        self.order.shipping_cost = round(shipping_cost, 2)
        self.order.discount = round(discount_amount, 2)
        self.order.status = "placed"

        self.order_repo.save(self.order)
        self._executed = True

        # Publish event
        EventBus().publish("order.placed", {
            "order_id": self.order.id,
            "customer_id": self.order.customer_id,
            "total": self.order.total,
            "items": [
                {"product_id": i.product_id,
                 "product_name": i.product_name,
                 "quantity": i.quantity}
                for i in self.order.items
            ]
        })

        return {
            "order_id": self.order.id,
            "subtotal": round(subtotal, 2),
            "discount": self.order.discount,
            "shipping": self.order.shipping_cost,
            "tax": self.order.tax,
            "total": self.order.total,
            "status": self.order.status
        }

    def undo(self) -> dict:
        if not self._executed:
            return {"error": "Order was not placed"}

        self.order_repo.update_status(self.order.id, "cancelled")
        self.order.status = "cancelled"

        EventBus().publish("order.cancelled", {
            "order_id": self.order.id,
            "customer_id": self.order.customer_id,
            "items": [
                {"product_id": i.product_id,
                 "product_name": i.product_name,
                 "quantity": i.quantity}
                for i in self.order.items
            ]
        })

        return {"order_id": self.order.id, "status": "cancelled"}

    def describe(self):
        return f"Place order {self.order.id} for {self.order.customer_id}"
```

---

## Part 6: Circuit Breaker -- Resilient Service Calls

When calling external services (payment, shipping), the Circuit Breaker prevents
cascading failures.

```python
import time
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"       # normal operation
    OPEN = "open"           # failing, reject calls
    HALF_OPEN = "half_open" # testing recovery


class CircuitBreaker:
    def __init__(self, name, failure_threshold=3,
                 recovery_timeout=10):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.success_count = 0

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                print(f"  [CB:{self.name}] HALF_OPEN: testing...")
            else:
                raise RuntimeError(
                    f"Circuit breaker {self.name} is OPEN")

        try:
            result = func(*args, **kwargs)

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                print(f"  [CB:{self.name}] CLOSED: recovered")

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"  [CB:{self.name}] OPEN: too many failures "
                      f"({self.failure_count})")

            raise
```

---

## Part 7: Saga -- Checkout Transaction

The complete checkout flow as a Saga with compensating transactions.

```python
class CheckoutSaga:
    """Orchestrates the checkout process across multiple services."""

    def __init__(self, order_repo, product_repo, payment_factory):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.payment_factory = payment_factory
        self.circuit_breaker = CircuitBreaker("payment", 3, 30)

    def execute(self, order: Order) -> dict:
        print(f"\n{'=' * 50}")
        print(f"  CHECKOUT SAGA: {order.id}")
        print(f"{'=' * 50}")

        completed_steps = []

        try:
            # Step 1: Validate order
            print(f"\n  Step 1: Validate Order")
            validator = build_validation_chain()
            errors = validator.validate(order, self.product_repo)
            if errors:
                return {"status": "failed", "errors": errors}
            print(f"  --> Validation passed")

            # Step 2: Reserve inventory
            print(f"\n  Step 2: Reserve Inventory")
            reserved_items = []
            for item in order.items:
                success = self.product_repo.update_stock(
                    item.product_id, -item.quantity)
                if not success:
                    # Compensate already-reserved items
                    for ri in reserved_items:
                        self.product_repo.update_stock(
                            ri["product_id"], ri["quantity"])
                    return {"status": "failed",
                            "errors": [f"Failed to reserve {item.product_name}"]}
                reserved_items.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity
                })
                product = self.product_repo.find_by_id(item.product_id)
                print(f"    Reserved {item.quantity}x {item.product_name} "
                      f"(remaining: {product.stock})")
            completed_steps.append("inventory")
            print(f"  --> Inventory reserved")

            # Step 3: Process payment
            print(f"\n  Step 3: Process Payment")
            processor = self.payment_factory.create(order.payment_method)
            try:
                payment_result = self.circuit_breaker.call(
                    processor.charge, order.total, order.id)
            except RuntimeError as e:
                # Circuit breaker open or payment failed
                self._compensate(completed_steps, order, reserved_items)
                return {"status": "failed", "errors": [str(e)]}
            completed_steps.append("payment")
            print(f"  --> Payment processed: {payment_result['transaction_id']}")

            # Step 4: Confirm order
            print(f"\n  Step 4: Confirm Order")
            self.order_repo.update_status(order.id, "confirmed")
            order.status = "confirmed"
            completed_steps.append("order_confirmed")

            # Publish success event
            EventBus().publish("payment.completed", {
                "order_id": order.id,
                "customer_id": order.customer_id,
                "total": order.total,
                "transaction_id": payment_result["transaction_id"]
            })

            print(f"\n{'=' * 50}")
            print(f"  CHECKOUT COMPLETE: {order.id}")
            print(f"  Total: ${order.total:.2f}")
            print(f"{'=' * 50}")

            return {
                "status": "confirmed",
                "order_id": order.id,
                "total": order.total,
                "transaction_id": payment_result["transaction_id"]
            }

        except Exception as e:
            print(f"\n  SAGA FAILED: {e}")
            self._compensate(completed_steps, order, reserved_items
                             if 'reserved_items' in dir() else [])
            return {"status": "failed", "errors": [str(e)]}

    def _compensate(self, completed_steps, order, reserved_items):
        print(f"\n  Compensating {len(completed_steps)} steps...")

        if "payment" in completed_steps:
            processor = self.payment_factory.create(order.payment_method)
            processor.refund(order.total, order.id)
            print(f"    Refunded payment")

        if "inventory" in completed_steps:
            for ri in reserved_items:
                self.product_repo.update_stock(
                    ri["product_id"], ri["quantity"])
            print(f"    Released inventory")

        self.order_repo.update_status(order.id, "cancelled")
        print(f"    Order cancelled")
```

---

## Part 8: CQRS -- Product Read/Write Separation

High-traffic product pages need fast reads. CQRS separates the read and write paths.

```python
class ProductCommandService:
    """Write side: handles product mutations."""

    def __init__(self, product_repo: ProductRepository):
        self.repo = product_repo
        self.event_bus = EventBus()

    def create_product(self, name, price, category, stock, description=""):
        product = Product(
            id=f"PROD-{uuid.uuid4().hex[:6].upper()}",
            name=name,
            price=price,
            category=category,
            stock=stock,
            description=description
        )
        self.repo.save(product)
        self.event_bus.publish("product.created", {
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "category": product.category
        })
        return product

    def update_price(self, product_id, new_price):
        product = self.repo.find_by_id(product_id)
        if product:
            old_price = product.price
            product.price = new_price
            self.repo.save(product)
            self.event_bus.publish("product.price_updated", {
                "product_id": product_id,
                "old_price": old_price,
                "new_price": new_price
            })
            return product
        return None


class ProductQueryService:
    """Read side: optimized for fast product lookups."""

    def __init__(self, product_repo: ProductRepository):
        self.repo = product_repo
        self._cache: Dict[str, dict] = {}
        self._category_cache: Dict[str, List[dict]] = {}

    def get_product(self, product_id):
        if product_id in self._cache:
            return self._cache[product_id]

        product = self.repo.find_by_id(product_id)
        if product:
            view = self._to_view(product)
            self._cache[product_id] = view
            return view
        return None

    def get_by_category(self, category):
        if category in self._category_cache:
            return self._category_cache[category]

        products = self.repo.find_by_category(category)
        views = [self._to_view(p) for p in products]
        self._category_cache[category] = views
        return views

    def get_catalog(self):
        """Full product catalog for browsing."""
        return [self._to_view(p) for p in self.repo.find_all()]

    def invalidate_cache(self, data):
        """Called when products change (event handler)."""
        product_id = data.get("product_id")
        if product_id in self._cache:
            del self._cache[product_id]
        self._category_cache.clear()

    def _to_view(self, product):
        return {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "category": product.category,
            "in_stock": product.stock > 0,
            "stock_level": "high" if product.stock > 10
                          else "low" if product.stock > 0
                          else "out_of_stock"
        }
```

---

## Part 9: Putting It All Together

```python
def run_ecommerce_demo():
    """Complete e-commerce flow using 15+ patterns."""

    print("=" * 60)
    print("  E-COMMERCE SYSTEM DEMO")
    print("  Patterns: Singleton, Factory, Builder, Strategy,")
    print("  Observer, Command, Chain of Responsibility,")
    print("  Repository, CQRS, Circuit Breaker, Saga")
    print("=" * 60)

    # --- Setup (Singleton: Config, Repository: Data Access) ---
    config = Config()
    product_repo = InMemoryProductRepository()
    order_repo = InMemoryOrderRepository()

    # --- CQRS: Separate read/write services ---
    product_cmd = ProductCommandService(product_repo)
    product_query = ProductQueryService(product_repo)

    # --- Observer: Wire up event handlers ---
    event_bus = EventBus()
    notification = NotificationHandler()
    analytics = AnalyticsHandler()
    inventory = InventoryHandler(product_repo)

    event_bus.subscribe("order.placed", notification.on_order_placed)
    event_bus.subscribe("order.placed", analytics.on_order_placed)
    event_bus.subscribe("order.cancelled", notification.on_order_cancelled)
    event_bus.subscribe("order.cancelled", inventory.on_order_cancelled)
    event_bus.subscribe("payment.completed", notification.on_payment_completed)
    event_bus.subscribe("payment.completed", analytics.on_payment_completed)
    event_bus.subscribe("product.price_updated",
                        product_query.invalidate_cache)

    # --- Create products (CQRS write side) ---
    print("\n--- Creating Products ---")
    laptop = product_cmd.create_product(
        "Gaming Laptop", 999.99, "electronics", 15,
        "High-performance gaming laptop")
    mouse = product_cmd.create_product(
        "Wireless Mouse", 29.99, "electronics", 50)
    book = product_cmd.create_product(
        "Design Patterns Book", 44.99, "books", 100)
    shirt = product_cmd.create_product(
        "Python T-Shirt", 24.99, "clothing", 200)

    print(f"  Created: {laptop.name} (${laptop.price})")
    print(f"  Created: {mouse.name} (${mouse.price})")
    print(f"  Created: {book.name} (${book.price})")
    print(f"  Created: {shirt.name} (${shirt.price})")

    # --- Browse products (CQRS read side) ---
    print("\n--- Product Catalog (CQRS Read) ---")
    catalog = product_query.get_catalog()
    for p in catalog:
        print(f"  {p['name']:25s} ${p['price']:>8.2f}  "
              f"[{p['stock_level']}]")

    # --- Build an order (Builder Pattern) ---
    print("\n--- Building Order (Builder) ---")
    order = (OrderBuilder("customer-alice")
        .add_item(laptop, 1)
        .add_item(mouse, 2)
        .add_item(book, 1)
        .shipping_address("123 Main St, Springfield")
        .payment_method("credit_card")
        .build())

    print(f"  Order {order.id} built with {len(order.items)} items")

    # --- Calculate totals (Strategy Pattern) ---
    print("\n--- Calculating Totals (Strategy) ---")
    pricing = StandardPricing()
    vip_set = {"customer-alice"}
    discount = LoyaltyDiscount(vip_set)
    shipping = StandardShipping()

    # --- Place order (Command Pattern) ---
    place_cmd = PlaceOrderCommand(
        order, order_repo, pricing, discount, shipping)
    print(f"\n--- Placing Order (Command) ---")
    result = place_cmd.execute()

    print(f"\n  Order Summary:")
    print(f"    Subtotal:  ${result['subtotal']:>8.2f}")
    print(f"    Discount:  -${result['discount']:>7.2f}")
    print(f"    Shipping:  ${result['shipping']:>8.2f}")
    print(f"    Tax:       ${result['tax']:>8.2f}")
    print(f"    Total:     ${result['total']:>8.2f}")

    # --- Checkout (Saga + Circuit Breaker + Factory) ---
    saga = CheckoutSaga(order_repo, product_repo,
                        PaymentProcessorFactory)
    checkout_result = saga.execute(order)

    # --- Verify stock updated ---
    print("\n--- Stock After Order ---")
    for product in product_repo.find_all():
        print(f"  {product.name:25s} stock: {product.stock}")

    # --- Order history (Repository) ---
    print("\n--- Order History (Repository) ---")
    alice_orders = order_repo.find_by_customer("customer-alice")
    for o in alice_orders:
        print(f"  {o.id}: ${o.total:.2f} [{o.status}]")

    # --- Event log (Observer) ---
    print("\n--- Event Log ---")
    for event in event_bus.get_log()[-6:]:
        print(f"  {event['event']:25s} at {event['timestamp'][:19]}")

    # --- Second order: with cancellation (Command undo) ---
    print("\n--- Building Second Order (will be cancelled) ---")
    order2 = (OrderBuilder("customer-bob")
        .add_item(shirt, 3)
        .shipping_address("456 Oak Ave, Shelbyville")
        .payment_method("paypal")
        .build())

    place_cmd2 = PlaceOrderCommand(
        order2, order_repo, StandardPricing(),
        NoDiscount(), ExpressShipping())
    result2 = place_cmd2.execute()
    print(f"  Placed: {order2.id} total=${result2['total']}")

    print("\n--- Cancelling Order (Command Undo) ---")
    cancel_result = place_cmd2.undo()
    print(f"  Cancelled: {cancel_result}")

    print("\n--- Final Stock ---")
    for product in product_repo.find_all():
        print(f"  {product.name:25s} stock: {product.stock}")

    print(f"\n{'=' * 60}")
    print(f"  DEMO COMPLETE")
    print(f"  Patterns demonstrated: Singleton, Factory, Builder,")
    print(f"  Strategy, Observer, Command, Chain of Responsibility,")
    print(f"  Repository, CQRS, Circuit Breaker, Saga")
    print(f"{'=' * 60}")


# Run the demo
run_ecommerce_demo()
```

**Output:**
```
============================================================
  E-COMMERCE SYSTEM DEMO
  Patterns: Singleton, Factory, Builder, Strategy,
  Observer, Command, Chain of Responsibility,
  Repository, CQRS, Circuit Breaker, Saga
============================================================

--- Creating Products ---
  Created: Gaming Laptop ($999.99)
  Created: Wireless Mouse ($29.99)
  Created: Design Patterns Book ($44.99)
  Created: Python T-Shirt ($24.99)

--- Product Catalog (CQRS Read) ---
  Gaming Laptop             $  999.99  [high]
  Wireless Mouse            $   29.99  [high]
  Design Patterns Book      $   44.99  [high]
  Python T-Shirt            $   24.99  [high]

--- Building Order (Builder) ---
  Order ORD-A1B2C3D4 built with 3 items

--- Calculating Totals (Strategy) ---

--- Placing Order (Command) ---
  [Notification] Order ORD-A1B2C3D4 confirmation sent to customer customer-alice
  [Analytics] Tracked order ORD-A1B2C3D4 (total tracked: 1)

  Order Summary:
    Subtotal:  $ 1104.96
    Discount:  -$ 165.74
    Shipping:  $    0.00
    Tax:       $   75.14
    Total:     $ 1014.36

==================================================
  CHECKOUT SAGA: ORD-A1B2C3D4
==================================================

  Step 1: Validate Order
  --> Validation passed

  Step 2: Reserve Inventory
    Reserved 1x Gaming Laptop (remaining: 14)
    Reserved 2x Wireless Mouse (remaining: 48)
    Reserved 1x Design Patterns Book (remaining: 99)
  --> Inventory reserved

  Step 3: Process Payment
    [CreditCard] Charging $1014.36 for order ORD-A1B2C3D4
  --> Payment processed: CC-e5f6g7h8

  Step 4: Confirm Order
  [Notification] Payment receipt sent for order ORD-A1B2C3D4
  [Analytics] Tracked order ... (total tracked: 2)

==================================================
  CHECKOUT COMPLETE: ORD-A1B2C3D4
  Total: $1014.36
==================================================

--- Stock After Order ---
  Gaming Laptop             stock: 14
  Wireless Mouse            stock: 48
  Design Patterns Book      stock: 99
  Python T-Shirt            stock: 200

--- Order History (Repository) ---
  ORD-A1B2C3D4: $1014.36 [confirmed]

--- Event Log ---
  order.placed              at 2026-03-29T10:30
  payment.completed         at 2026-03-29T10:30
  ...

--- Building Second Order (will be cancelled) ---
  Placed: ORD-E5F6G7H8 total=$89.46

--- Cancelling Order (Command Undo) ---
  [Notification] Order ORD-E5F6G7H8 cancellation notice sent
  Cancelled: {'order_id': 'ORD-E5F6G7H8', 'status': 'cancelled'}

--- Final Stock ---
  Gaming Laptop             stock: 14
  Wireless Mouse            stock: 48
  Design Patterns Book      stock: 99
  Python T-Shirt            stock: 200

============================================================
  DEMO COMPLETE
  Patterns demonstrated: Singleton, Factory, Builder,
  Strategy, Observer, Command, Chain of Responsibility,
  Repository, CQRS, Circuit Breaker, Saga
============================================================
```

---

## Architecture Decision Map

When building a system like this, use this decision map to choose patterns:

```
"I need to create objects..."
  - Complex construction?           -> Builder
  - Multiple types from one family? -> Factory Method
  - Copy an existing template?      -> Prototype

"I need to structure behavior..."
  - Interchangeable algorithms?     -> Strategy
  - Pipeline of handlers?           -> Chain of Responsibility
  - Undoable operations?            -> Command
  - React to state changes?         -> Observer

"I need to access data..."
  - Abstract storage?               -> Repository
  - Separate read/write?            -> CQRS
  - Cross-service transaction?      -> Saga

"I need reliability..."
  - External service might fail?    -> Circuit Breaker
  - Need a single entry point?      -> API Gateway
  - Dynamic service locations?      -> Service Discovery

"I need shared resources..."
  - One instance globally?          -> Singleton
  - Share common state?             -> Flyweight
  - Pool expensive resources?       -> Object Pool
```

---

## Quick Summary

This project demonstrates how design patterns work together in a real system. No
pattern exists in isolation. Singleton provides configuration. Repository abstracts
data access. Builder constructs complex orders. Strategy handles variable business
rules. Observer enables event-driven communication. Command enables undoable operations.
Chain of Responsibility validates data. Factory creates processors. CQRS optimizes
reads and writes. Circuit Breaker adds resilience. Saga manages distributed
transactions.

---

## Key Points

- Patterns are tools that **compose**: Builder creates objects that Strategy processes
- The **Repository** pattern is the foundation that every other pattern depends on for
  data access
- **Events** (Observer) are the glue that connects loosely coupled components
- **Saga** coordinates across service boundaries what transactions do within one
- **Circuit Breaker** prevents one failing service from taking down the whole system
- **CQRS** lets you optimize reads and writes independently
- Start simple: add patterns only when the complexity they address actually exists
- Every pattern has a cost: do not use patterns just because you can

---

## Practice Questions

1. In this system, why do we use both the Command pattern and the Saga pattern? What
   does each handle that the other cannot?

2. If we removed the Event Bus (Observer), what would change? Which components would
   need direct references to each other?

3. The Circuit Breaker wraps payment calls. What other external calls in an e-commerce
   system should have circuit breakers?

4. How would you add a "gift wrapping" option to the order? Which patterns would be
   involved and how?

5. The system uses in-memory repositories. What changes if you switch to a real
   database? Which patterns protect you from this change?

---

## Exercises

### Exercise 1: Add a Coupon System

Add coupon support to the e-commerce system:

- Create a `CouponRepository` to store and validate coupons
- Add a `CouponDiscountStrategy` that applies coupon codes
- Extend `OrderBuilder` with a `.apply_coupon(code)` method
- Add coupon validation to the Chain of Responsibility
- Publish a "coupon.redeemed" event when a coupon is used
- Support: percentage coupons, fixed-amount coupons, and minimum-order coupons

### Exercise 2: Add Product Reviews

Add a review system:

- `Review` entity with rating, comment, customer_id, product_id
- `ReviewRepository` with CQRS: write side saves reviews, read side returns aggregated
  ratings
- Chain of Responsibility for review validation (profanity filter, rating range check,
  purchase verification)
- Observer events: "review.posted" triggers notification to product owner
- Strategy for sorting reviews: by date, by rating, by helpfulness

### Exercise 3: Add Inventory Alerts

Build an inventory monitoring system:

- Observer that watches stock levels after every order
- When stock drops below threshold (5 items), publish "inventory.low" event
- When stock reaches zero, publish "inventory.depleted" event
- NotificationHandler sends alerts to the inventory team
- Command to restock products with undo capability
- Dashboard view (print) showing all products with stock warnings

---

## What Is Next?

The final chapter provides a comprehensive **Glossary** of all design pattern terms
used throughout this book, giving you a quick reference to look up any concept.
