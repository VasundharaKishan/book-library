# Chapter 31: Project Refactoring -- From God Class to Clean Architecture

## What You Will Learn

- How to recognize and dismantle a "god class" -- a single class that does everything
- A step-by-step refactoring process that applies every principle from this book
- How to go from one messy 300-line file to six clean, focused files
- How to maintain working code at every step (no big-bang rewrites)
- Practical application of SRP, DIP, DI, strategy pattern, and clean architecture

## Why This Chapter Matters

Throughout this book, you have learned principles: Single Responsibility, Open/Closed, Dependency Inversion, clean naming, small functions, testability. But learning principles and applying them are two different things.

This chapter is where everything comes together. We take a realistic, messy `OrderProcessor` god class -- the kind you would find in any production codebase -- and refactor it step by step into clean, well-structured code. Every step applies a principle you have already learned. Every step keeps the code working.

This is not a toy example. The original code is 300 lines of tangled logic: validation mixed with pricing, payment processing mixed with notification, database calls mixed with business rules. By the end, you will have six clean files, each with a single responsibility, fully testable, and easy to modify.

---

## The Starting Point: The God Class

Here is the `OrderProcessor` in its original form. This is one file, one class, one massive method. Read through it and notice how many different responsibilities are tangled together.

### BEFORE: OrderProcessor.java (One File, ~300 Lines)

```java
import java.sql.*;
import java.util.*;
import java.time.LocalDateTime;

public class OrderProcessor {

    private static final String DB_URL = "jdbc:mysql://localhost:3306/shop";
    private static final String DB_USER = "root";
    private static final String DB_PASS = "password123";
    private static final double TAX_RATE = 0.08;
    private static final double FREE_SHIPPING_THRESHOLD = 50.0;
    private static final double STANDARD_SHIPPING = 5.99;
    private static final String SMTP_HOST = "smtp.company.com";

    public Map<String, Object> processOrder(Map<String, Object> orderData) {
        Map<String, Object> result = new HashMap<>();

        // ---- VALIDATION ----
        String customerEmail = (String) orderData.get("email");
        if (customerEmail == null || customerEmail.isEmpty()) {
            result.put("success", false);
            result.put("error", "Email is required");
            return result;
        }
        if (!customerEmail.contains("@")) {
            result.put("success", false);
            result.put("error", "Invalid email format");
            return result;
        }

        List<Map<String, Object>> items = (List<Map<String, Object>>) orderData.get("items");
        if (items == null || items.isEmpty()) {
            result.put("success", false);
            result.put("error", "Order must have at least one item");
            return result;
        }

        for (Map<String, Object> item : items) {
            int qty = (int) item.get("quantity");
            if (qty <= 0) {
                result.put("success", false);
                result.put("error", "Quantity must be positive for item: " + item.get("name"));
                return result;
            }
            double price = (double) item.get("price");
            if (price < 0) {
                result.put("success", false);
                result.put("error", "Price cannot be negative for item: " + item.get("name"));
                return result;
            }
        }

        // ---- PRICING ----
        double subtotal = 0;
        for (Map<String, Object> item : items) {
            subtotal += (double) item.get("price") * (int) item.get("quantity");
        }

        // Apply discount
        String discountCode = (String) orderData.get("discountCode");
        double discount = 0;
        if (discountCode != null) {
            if (discountCode.equals("SAVE10")) {
                discount = subtotal * 0.10;
            } else if (discountCode.equals("SAVE20")) {
                discount = subtotal * 0.20;
            } else if (discountCode.equals("FLAT5")) {
                discount = 5.0;
            } else {
                // Check database for custom discount codes
                try {
                    Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
                    PreparedStatement ps = conn.prepareStatement(
                        "SELECT discount_percent FROM discount_codes WHERE code = ? AND expiry > NOW()");
                    ps.setString(1, discountCode);
                    ResultSet rs = ps.executeQuery();
                    if (rs.next()) {
                        discount = subtotal * (rs.getDouble("discount_percent") / 100);
                    }
                    conn.close();
                } catch (SQLException e) {
                    System.out.println("DB error checking discount: " + e.getMessage());
                }
            }
        }

        double afterDiscount = subtotal - discount;
        double tax = afterDiscount * TAX_RATE;
        double shipping = afterDiscount >= FREE_SHIPPING_THRESHOLD ? 0 : STANDARD_SHIPPING;
        double total = afterDiscount + tax + shipping;

        // ---- CHECK INVENTORY ----
        try {
            Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
            for (Map<String, Object> item : items) {
                PreparedStatement ps = conn.prepareStatement(
                    "SELECT stock FROM inventory WHERE product_id = ?");
                ps.setString(1, (String) item.get("productId"));
                ResultSet rs = ps.executeQuery();
                if (rs.next()) {
                    int stock = rs.getInt("stock");
                    int qty = (int) item.get("quantity");
                    if (stock < qty) {
                        result.put("success", false);
                        result.put("error", "Insufficient stock for: " + item.get("name"));
                        conn.close();
                        return result;
                    }
                } else {
                    result.put("success", false);
                    result.put("error", "Product not found: " + item.get("productId"));
                    conn.close();
                    return result;
                }
            }
            conn.close();
        } catch (SQLException e) {
            result.put("success", false);
            result.put("error", "Database error: " + e.getMessage());
            return result;
        }

        // ---- PROCESS PAYMENT ----
        boolean paymentSuccess = false;
        String paymentMethod = (String) orderData.get("paymentMethod");
        String paymentId = null;
        try {
            if ("credit_card".equals(paymentMethod)) {
                // Simulate credit card processing
                String cardNumber = (String) orderData.get("cardNumber");
                if (cardNumber == null || cardNumber.length() < 13) {
                    result.put("success", false);
                    result.put("error", "Invalid card number");
                    return result;
                }
                paymentId = "CC-" + System.currentTimeMillis();
                paymentSuccess = true;
            } else if ("paypal".equals(paymentMethod)) {
                String paypalEmail = (String) orderData.get("paypalEmail");
                paymentId = "PP-" + System.currentTimeMillis();
                paymentSuccess = true;
            } else {
                result.put("success", false);
                result.put("error", "Unknown payment method: " + paymentMethod);
                return result;
            }
        } catch (Exception e) {
            result.put("success", false);
            result.put("error", "Payment processing failed: " + e.getMessage());
            return result;
        }

        // ---- SAVE ORDER TO DATABASE ----
        String orderId = "ORD-" + System.currentTimeMillis();
        try {
            Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
            PreparedStatement ps = conn.prepareStatement(
                "INSERT INTO orders (id, customer_email, subtotal, discount, tax, " +
                "shipping, total, payment_id, status, created_at) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
            ps.setString(1, orderId);
            ps.setString(2, customerEmail);
            ps.setDouble(3, subtotal);
            ps.setDouble(4, discount);
            ps.setDouble(5, tax);
            ps.setDouble(6, shipping);
            ps.setDouble(7, total);
            ps.setString(8, paymentId);
            ps.setString(9, "CONFIRMED");
            ps.setString(10, LocalDateTime.now().toString());
            ps.executeUpdate();

            // Update inventory
            for (Map<String, Object> item : items) {
                PreparedStatement updatePs = conn.prepareStatement(
                    "UPDATE inventory SET stock = stock - ? WHERE product_id = ?");
                updatePs.setInt(1, (int) item.get("quantity"));
                updatePs.setString(2, (String) item.get("productId"));
                updatePs.executeUpdate();
            }

            conn.close();
        } catch (SQLException e) {
            result.put("success", false);
            result.put("error", "Failed to save order: " + e.getMessage());
            return result;
        }

        // ---- SEND CONFIRMATION EMAIL ----
        try {
            Properties props = new Properties();
            props.put("mail.smtp.host", SMTP_HOST);
            // ... email sending code ...
            System.out.println("Email sent to " + customerEmail + " for order " + orderId);
        } catch (Exception e) {
            // Log but don't fail the order
            System.out.println("Failed to send email: " + e.getMessage());
        }

        // ---- BUILD RESPONSE ----
        result.put("success", true);
        result.put("orderId", orderId);
        result.put("subtotal", subtotal);
        result.put("discount", discount);
        result.put("tax", tax);
        result.put("shipping", shipping);
        result.put("total", total);
        result.put("paymentId", paymentId);

        return result;
    }
}
```

### What Is Wrong With This Code?

```
PROBLEMS IN THE GOD CLASS:

  +-----------------------------------------------------+
  | 1. SINGLE RESPONSIBILITY VIOLATION                   |
  |    One class does: validation, pricing, inventory,   |
  |    payment, persistence, notifications               |
  |                                                      |
  | 2. NO ABSTRACTION                                   |
  |    Raw Maps instead of domain objects                |
  |    Raw JDBC instead of repositories                  |
  |    Hard-coded SMTP instead of notification interface |
  |                                                      |
  | 3. UNTESTABLE                                       |
  |    Cannot test pricing without a database            |
  |    Cannot test validation without payment processing |
  |    Cannot test anything in isolation                 |
  |                                                      |
  | 4. HARD-CODED CONFIGURATION                         |
  |    Database credentials in source code               |
  |    SMTP host hard-coded                              |
  |    Tax rate hard-coded                               |
  |                                                      |
  | 5. POOR ERROR HANDLING                               |
  |    Some exceptions caught, some ignored              |
  |    Database connections not properly closed           |
  |    No transaction management                         |
  |                                                      |
  | 6. NO DOMAIN MODEL                                  |
  |    Map<String, Object> everywhere                    |
  |    No type safety                                    |
  |    Business rules hidden in procedural code          |
  +-----------------------------------------------------+
```

---

## The Refactoring Plan

We will refactor in six steps. Each step produces working code. Each step applies specific principles from this book.

```
REFACTORING PLAN:

  Step 1: Create Domain Objects       (Ch 2: Meaningful Names)
          Replace Map<String, Object>   (Ch 7: Classes)
          with typed classes

  Step 2: Extract OrderValidator       (Ch 8: Single Responsibility)
          All validation in one place

  Step 3: Extract PricingService       (Ch 8: Single Responsibility)
          Subtotal, discount, tax,      (Ch 25: Strategy Pattern)
          shipping calculations

  Step 4: Extract OrderRepository      (Ch 12: Dependency Inversion)
          Database access behind        (Ch 24: Dependency Injection)
          an interface

  Step 5: Extract PaymentProcessor     (Ch 12: Dependency Inversion)
          Payment logic behind          (Ch 24: Dependency Injection)
          an interface

  Step 6: Extract NotificationService  (Ch 12: Dependency Inversion)
          Email behind an interface     (Ch 24: Dependency Injection)

  Final: Wire everything in            (Ch 24: Composition Root)
         OrderService
```

---

## Step 1: Create Domain Objects

Replace the raw `Map<String, Object>` with proper domain objects.

**Principles applied:** Meaningful Names (Ch 2), Classes (Ch 7)

### File 1: Domain Objects

```java
// domain/OrderItem.java
public record OrderItem(
    String productId,
    String name,
    double price,
    int quantity
) {
    public OrderItem {
        if (productId == null || productId.isBlank())
            throw new IllegalArgumentException("Product ID is required");
        if (price < 0)
            throw new IllegalArgumentException("Price cannot be negative");
        if (quantity <= 0)
            throw new IllegalArgumentException("Quantity must be positive");
    }

    public double lineTotal() {
        return price * quantity;
    }
}

// domain/Order.java
public class Order {
    private final String id;
    private final String customerEmail;
    private final List<OrderItem> items;
    private final String discountCode;
    private final String paymentMethod;
    private final Map<String, String> paymentDetails;
    private OrderStatus status;
    private OrderPricing pricing;
    private String paymentId;

    public Order(String customerEmail, List<OrderItem> items,
                 String discountCode, String paymentMethod,
                 Map<String, String> paymentDetails) {
        this.id = "ORD-" + System.currentTimeMillis();
        this.customerEmail = customerEmail;
        this.items = List.copyOf(items);
        this.discountCode = discountCode;
        this.paymentMethod = paymentMethod;
        this.paymentDetails = paymentDetails != null
            ? Map.copyOf(paymentDetails) : Map.of();
        this.status = OrderStatus.PENDING;
    }

    public String getId() { return id; }
    public String getCustomerEmail() { return customerEmail; }
    public List<OrderItem> getItems() { return items; }
    public String getDiscountCode() { return discountCode; }
    public String getPaymentMethod() { return paymentMethod; }
    public Map<String, String> getPaymentDetails() { return paymentDetails; }
    public OrderStatus getStatus() { return status; }
    public OrderPricing getPricing() { return pricing; }
    public String getPaymentId() { return paymentId; }

    public void confirm(OrderPricing pricing, String paymentId) {
        this.pricing = pricing;
        this.paymentId = paymentId;
        this.status = OrderStatus.CONFIRMED;
    }
}

// domain/OrderPricing.java
public record OrderPricing(
    double subtotal,
    double discount,
    double tax,
    double shipping,
    double total
) {}

// domain/OrderStatus.java
public enum OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

// domain/OrderResult.java
public record OrderResult(
    boolean success,
    String orderId,
    OrderPricing pricing,
    String paymentId,
    String error
) {
    public static OrderResult success(Order order) {
        return new OrderResult(true, order.getId(), order.getPricing(),
                               order.getPaymentId(), null);
    }

    public static OrderResult failure(String error) {
        return new OrderResult(false, null, null, null, error);
    }
}
```

---

## Step 2: Extract OrderValidator

Move all validation logic into its own class.

**Principles applied:** Single Responsibility (Ch 8), Clean Functions (Ch 3)

### File 2: OrderValidator.java

```java
// validation/OrderValidator.java
public class OrderValidator {

    public List<String> validate(Order order) {
        List<String> errors = new ArrayList<>();

        validateEmail(order.getCustomerEmail(), errors);
        validateItems(order.getItems(), errors);
        validatePaymentMethod(order.getPaymentMethod(), errors);

        return errors;
    }

    private void validateEmail(String email, List<String> errors) {
        if (email == null || email.isBlank()) {
            errors.add("Email is required");
        } else if (!email.contains("@")) {
            errors.add("Invalid email format");
        }
    }

    private void validateItems(List<OrderItem> items, List<String> errors) {
        if (items == null || items.isEmpty()) {
            errors.add("Order must have at least one item");
        }
        // Note: Individual item validation is now in the OrderItem constructor
    }

    private void validatePaymentMethod(String method, List<String> errors) {
        if (method == null || method.isBlank()) {
            errors.add("Payment method is required");
        }
    }
}
```

---

## Step 3: Extract PricingService

Move all pricing logic (subtotal, discounts, tax, shipping) into its own service.

**Principles applied:** Single Responsibility (Ch 8), Strategy Pattern (Ch 25), Open/Closed (Ch 9)

### File 3: PricingService.java

```java
// pricing/PricingService.java
public class PricingService {

    private final DiscountStrategy discountStrategy;
    private final double taxRate;
    private final double freeShippingThreshold;
    private final double standardShipping;

    public PricingService(DiscountStrategy discountStrategy,
                          double taxRate,
                          double freeShippingThreshold,
                          double standardShipping) {
        this.discountStrategy = discountStrategy;
        this.taxRate = taxRate;
        this.freeShippingThreshold = freeShippingThreshold;
        this.standardShipping = standardShipping;
    }

    public OrderPricing calculatePricing(List<OrderItem> items, String discountCode) {
        double subtotal = calculateSubtotal(items);
        double discount = discountStrategy.calculateDiscount(subtotal, discountCode);
        double afterDiscount = subtotal - discount;
        double tax = afterDiscount * taxRate;
        double shipping = calculateShipping(afterDiscount);
        double total = afterDiscount + tax + shipping;

        return new OrderPricing(subtotal, discount, tax, shipping, total);
    }

    private double calculateSubtotal(List<OrderItem> items) {
        return items.stream()
            .mapToDouble(OrderItem::lineTotal)
            .sum();
    }

    private double calculateShipping(double afterDiscount) {
        return afterDiscount >= freeShippingThreshold ? 0 : standardShipping;
    }
}

// pricing/DiscountStrategy.java
public interface DiscountStrategy {
    double calculateDiscount(double subtotal, String discountCode);
}

// pricing/StandardDiscountStrategy.java
public class StandardDiscountStrategy implements DiscountStrategy {

    private final DiscountCodeRepository discountCodeRepo;

    public StandardDiscountStrategy(DiscountCodeRepository discountCodeRepo) {
        this.discountCodeRepo = discountCodeRepo;
    }

    @Override
    public double calculateDiscount(double subtotal, String discountCode) {
        if (discountCode == null || discountCode.isBlank()) {
            return 0;
        }

        return switch (discountCode) {
            case "SAVE10" -> subtotal * 0.10;
            case "SAVE20" -> subtotal * 0.20;
            case "FLAT5"  -> 5.0;
            default       -> lookupCustomDiscount(subtotal, discountCode);
        };
    }

    private double lookupCustomDiscount(double subtotal, String code) {
        return discountCodeRepo.findActiveByCode(code)
            .map(discount -> subtotal * (discount.percent() / 100))
            .orElse(0.0);
    }
}
```

---

## Step 4: Extract OrderRepository

Move all database access behind an interface.

**Principles applied:** Dependency Inversion (Ch 12), Dependency Injection (Ch 24)

### File 4: OrderRepository.java

```java
// repository/OrderRepository.java
public interface OrderRepository {
    void save(Order order);
    Optional<Order> findById(String orderId);
}

// repository/InventoryRepository.java
public interface InventoryRepository {
    int getStock(String productId);
    void reduceStock(String productId, int quantity);
}

// repository/DiscountCodeRepository.java
public interface DiscountCodeRepository {
    Optional<DiscountCode> findActiveByCode(String code);
}

// repository/mysql/MySqlOrderRepository.java
public class MySqlOrderRepository implements OrderRepository {

    private final DataSource dataSource;

    public MySqlOrderRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public void save(Order order) {
        try (Connection conn = dataSource.getConnection()) {
            PreparedStatement ps = conn.prepareStatement(
                "INSERT INTO orders (id, customer_email, subtotal, discount, " +
                "tax, shipping, total, payment_id, status, created_at) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
            ps.setString(1, order.getId());
            ps.setString(2, order.getCustomerEmail());
            ps.setDouble(3, order.getPricing().subtotal());
            ps.setDouble(4, order.getPricing().discount());
            ps.setDouble(5, order.getPricing().tax());
            ps.setDouble(6, order.getPricing().shipping());
            ps.setDouble(7, order.getPricing().total());
            ps.setString(8, order.getPaymentId());
            ps.setString(9, order.getStatus().name());
            ps.setString(10, LocalDateTime.now().toString());
            ps.executeUpdate();
        } catch (SQLException e) {
            throw new PersistenceException("Failed to save order: " + e.getMessage(), e);
        }
    }

    @Override
    public Optional<Order> findById(String orderId) {
        // Implementation omitted for brevity
        return Optional.empty();
    }
}

// repository/mysql/MySqlInventoryRepository.java
public class MySqlInventoryRepository implements InventoryRepository {

    private final DataSource dataSource;

    public MySqlInventoryRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public int getStock(String productId) {
        try (Connection conn = dataSource.getConnection()) {
            PreparedStatement ps = conn.prepareStatement(
                "SELECT stock FROM inventory WHERE product_id = ?");
            ps.setString(1, productId);
            ResultSet rs = ps.executeQuery();
            if (rs.next()) return rs.getInt("stock");
            throw new ProductNotFoundException(productId);
        } catch (SQLException e) {
            throw new PersistenceException("Failed to check stock: " + e.getMessage(), e);
        }
    }

    @Override
    public void reduceStock(String productId, int quantity) {
        try (Connection conn = dataSource.getConnection()) {
            PreparedStatement ps = conn.prepareStatement(
                "UPDATE inventory SET stock = stock - ? WHERE product_id = ?");
            ps.setInt(1, quantity);
            ps.setString(2, productId);
            ps.executeUpdate();
        } catch (SQLException e) {
            throw new PersistenceException("Failed to update stock: " + e.getMessage(), e);
        }
    }
}
```

---

## Step 5: Extract PaymentProcessor

Move payment logic behind an interface.

**Principles applied:** Dependency Inversion (Ch 12), Strategy Pattern (Ch 25)

### File 5: PaymentProcessor.java

```java
// payment/PaymentProcessor.java
public interface PaymentProcessor {
    PaymentResult processPayment(double amount, String method,
                                 Map<String, String> details);
}

// payment/PaymentResult.java
public record PaymentResult(String paymentId, boolean success, String error) {
    public static PaymentResult success(String paymentId) {
        return new PaymentResult(paymentId, true, null);
    }
    public static PaymentResult failure(String error) {
        return new PaymentResult(null, false, error);
    }
}

// payment/DefaultPaymentProcessor.java
public class DefaultPaymentProcessor implements PaymentProcessor {

    @Override
    public PaymentResult processPayment(double amount, String method,
                                        Map<String, String> details) {
        return switch (method) {
            case "credit_card" -> processCreditCard(amount, details);
            case "paypal"      -> processPayPal(amount, details);
            default            -> PaymentResult.failure(
                                     "Unknown payment method: " + method);
        };
    }

    private PaymentResult processCreditCard(double amount,
                                            Map<String, String> details) {
        String cardNumber = details.get("cardNumber");
        if (cardNumber == null || cardNumber.length() < 13) {
            return PaymentResult.failure("Invalid card number");
        }
        String paymentId = "CC-" + System.currentTimeMillis();
        return PaymentResult.success(paymentId);
    }

    private PaymentResult processPayPal(double amount,
                                        Map<String, String> details) {
        String paymentId = "PP-" + System.currentTimeMillis();
        return PaymentResult.success(paymentId);
    }
}
```

---

## Step 6: Extract NotificationService

Move email notification behind an interface.

**Principles applied:** Dependency Inversion (Ch 12)

### File 6: NotificationService.java

```java
// notification/NotificationService.java
public interface NotificationService {
    void sendOrderConfirmation(String email, String orderId, OrderPricing pricing);
}

// notification/EmailNotificationService.java
public class EmailNotificationService implements NotificationService {

    private final String smtpHost;

    public EmailNotificationService(String smtpHost) {
        this.smtpHost = smtpHost;
    }

    @Override
    public void sendOrderConfirmation(String email, String orderId,
                                       OrderPricing pricing) {
        try {
            // Email sending implementation
            System.out.println("Confirmation email sent to " + email
                             + " for order " + orderId);
        } catch (Exception e) {
            // Log but don't fail the order
            System.err.println("Failed to send email: " + e.getMessage());
        }
    }
}
```

---

## The Final Result: OrderService

Now the `OrderService` orchestrates clean, focused components. Compare this to the original 300-line god class.

### AFTER: OrderService.java (The Orchestrator)

```java
// service/OrderService.java
public class OrderService {

    private final OrderValidator validator;
    private final PricingService pricingService;
    private final InventoryRepository inventoryRepo;
    private final PaymentProcessor paymentProcessor;
    private final OrderRepository orderRepo;
    private final NotificationService notifications;

    public OrderService(OrderValidator validator,
                        PricingService pricingService,
                        InventoryRepository inventoryRepo,
                        PaymentProcessor paymentProcessor,
                        OrderRepository orderRepo,
                        NotificationService notifications) {
        this.validator = validator;
        this.pricingService = pricingService;
        this.inventoryRepo = inventoryRepo;
        this.paymentProcessor = paymentProcessor;
        this.orderRepo = orderRepo;
        this.notifications = notifications;
    }

    public OrderResult processOrder(Order order) {
        // Step 1: Validate
        List<String> errors = validator.validate(order);
        if (!errors.isEmpty()) {
            return OrderResult.failure(String.join("; ", errors));
        }

        // Step 2: Check inventory
        for (OrderItem item : order.getItems()) {
            int stock = inventoryRepo.getStock(item.productId());
            if (stock < item.quantity()) {
                return OrderResult.failure(
                    "Insufficient stock for: " + item.name());
            }
        }

        // Step 3: Calculate pricing
        OrderPricing pricing = pricingService.calculatePricing(
            order.getItems(), order.getDiscountCode());

        // Step 4: Process payment
        PaymentResult payment = paymentProcessor.processPayment(
            pricing.total(), order.getPaymentMethod(),
            order.getPaymentDetails());
        if (!payment.success()) {
            return OrderResult.failure("Payment failed: " + payment.error());
        }

        // Step 5: Confirm and save
        order.confirm(pricing, payment.paymentId());
        orderRepo.save(order);

        // Step 6: Reduce inventory
        for (OrderItem item : order.getItems()) {
            inventoryRepo.reduceStock(item.productId(), item.quantity());
        }

        // Step 7: Notify customer
        notifications.sendOrderConfirmation(
            order.getCustomerEmail(), order.getId(), pricing);

        return OrderResult.success(order);
    }
}
```

---

## Before vs After: Side by Side

```
BEFORE (1 file, ~300 lines):          AFTER (6+ files, each focused):

+----------------------------------+  +-----------------------------+
| OrderProcessor.java              |  | domain/                     |
|                                  |  |   Order.java          (45)  |
|  - Validation        (30 lines) |  |   OrderItem.java      (20)  |
|  - Pricing            (40 lines) |  |   OrderPricing.java   (10)  |
|  - Discount lookup    (20 lines) |  |   OrderResult.java    (15)  |
|  - Inventory check    (30 lines) |  |   OrderStatus.java     (5)  |
|  - Payment processing (35 lines) |  |                             |
|  - Order persistence  (35 lines) |  | validation/                 |
|  - Inventory update   (15 lines) |  |   OrderValidator.java (30)  |
|  - Email notification (15 lines) |  |                             |
|  - Response building  (15 lines) |  | pricing/                    |
|  - Error handling     (scattered)|  |   PricingService.java (35)  |
|  - DB connection      (repeated) |  |   DiscountStrategy.java (5) |
|  - Configuration      (hard-coded) |   StandardDiscount.java(25)|
|                                  |  |                             |
|  Total: ~300 lines               |  | repository/                 |
|  Responsibilities: 8+            |  |   OrderRepository.java  (5) |
|  Testable: NO                    |  |   InventoryRepository   (5) |
|                                  |  |   MySqlOrderRepo.java  (35) |
+----------------------------------+  |   MySqlInventoryRepo   (30) |
                                      |                             |
                                      | payment/                    |
                                      |   PaymentProcessor.java  (5)|
                                      |   PaymentResult.java   (10) |
                                      |   DefaultPaymentProc   (30) |
                                      |                             |
                                      | notification/               |
                                      |   NotificationService    (5)|
                                      |   EmailNotification     (20)|
                                      |                             |
                                      | service/                    |
                                      |   OrderService.java    (50) |
                                      |                             |
                                      | Each file: 5-50 lines       |
                                      | Each: ONE responsibility    |
                                      | Testable: YES               |
                                      +-----------------------------+
```

---

## Testing the Refactored Code

The refactored code is trivially testable because every dependency is injected.

```java
class OrderServiceTest {

    private OrderValidator validator = new OrderValidator();
    private FakeInventoryRepository inventoryRepo = new FakeInventoryRepository();
    private FakePaymentProcessor paymentProcessor = new FakePaymentProcessor();
    private FakeOrderRepository orderRepo = new FakeOrderRepository();
    private FakeNotificationService notifications = new FakeNotificationService();
    private PricingService pricingService = new PricingService(
        new StandardDiscountStrategy(new FakeDiscountCodeRepository()),
        0.08, 50.0, 5.99
    );

    private OrderService service = new OrderService(
        validator, pricingService, inventoryRepo,
        paymentProcessor, orderRepo, notifications
    );

    @Test
    void successful_order_flow() {
        inventoryRepo.setStock("WIDGET-1", 100);
        paymentProcessor.willSucceed();

        Order order = new Order(
            "jane@example.com",
            List.of(new OrderItem("WIDGET-1", "Widget", 25.0, 2)),
            null, "credit_card",
            Map.of("cardNumber", "4111111111111111")
        );

        OrderResult result = service.processOrder(order);

        assertTrue(result.success());
        assertNotNull(result.orderId());
        assertEquals(50.0, result.pricing().subtotal());
        assertTrue(orderRepo.wasSaved(result.orderId()));
        assertTrue(notifications.wasSentTo("jane@example.com"));
    }

    @Test
    void rejects_order_with_invalid_email() {
        Order order = new Order(
            "not-an-email",
            List.of(new OrderItem("WIDGET-1", "Widget", 25.0, 1)),
            null, "credit_card", Map.of()
        );

        OrderResult result = service.processOrder(order);

        assertFalse(result.success());
        assertTrue(result.error().contains("Invalid email"));
    }

    @Test
    void rejects_order_when_insufficient_stock() {
        inventoryRepo.setStock("WIDGET-1", 0);  // Out of stock

        Order order = new Order(
            "jane@example.com",
            List.of(new OrderItem("WIDGET-1", "Widget", 25.0, 5)),
            null, "credit_card",
            Map.of("cardNumber", "4111111111111111")
        );

        OrderResult result = service.processOrder(order);

        assertFalse(result.success());
        assertTrue(result.error().contains("Insufficient stock"));
    }

    @Test
    void applies_discount_correctly() {
        inventoryRepo.setStock("WIDGET-1", 100);
        paymentProcessor.willSucceed();

        Order order = new Order(
            "jane@example.com",
            List.of(new OrderItem("WIDGET-1", "Widget", 100.0, 1)),
            "SAVE10", "credit_card",
            Map.of("cardNumber", "4111111111111111")
        );

        OrderResult result = service.processOrder(order);

        assertTrue(result.success());
        assertEquals(10.0, result.pricing().discount());
    }
}
```

---

## The Python Version (After)

Here is the same refactored structure in Python:

```python
# domain.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"

@dataclass(frozen=True)
class OrderItem:
    product_id: str
    name: str
    price: float
    quantity: int

    def line_total(self) -> float:
        return self.price * self.quantity

@dataclass
class OrderPricing:
    subtotal: float
    discount: float
    tax: float
    shipping: float
    total: float

@dataclass
class Order:
    customer_email: str
    items: list[OrderItem]
    discount_code: Optional[str]
    payment_method: str
    payment_details: dict
    id: str = ""
    status: OrderStatus = OrderStatus.PENDING
    pricing: Optional[OrderPricing] = None
    payment_id: Optional[str] = None

    def confirm(self, pricing: OrderPricing, payment_id: str):
        self.pricing = pricing
        self.payment_id = payment_id
        self.status = OrderStatus.CONFIRMED

# validation.py
class OrderValidator:
    def validate(self, order: Order) -> list[str]:
        errors = []
        if not order.customer_email or "@" not in order.customer_email:
            errors.append("Valid email is required")
        if not order.items:
            errors.append("Order must have at least one item")
        return errors

# pricing.py
from typing import Protocol

class DiscountStrategy(Protocol):
    def calculate_discount(self, subtotal: float, code: str) -> float: ...

class PricingService:
    def __init__(self, discount_strategy, tax_rate=0.08,
                 free_shipping_threshold=50.0, standard_shipping=5.99):
        self.discount_strategy = discount_strategy
        self.tax_rate = tax_rate
        self.free_shipping_threshold = free_shipping_threshold
        self.standard_shipping = standard_shipping

    def calculate_pricing(self, items, discount_code) -> OrderPricing:
        subtotal = sum(item.line_total() for item in items)
        discount = self.discount_strategy.calculate_discount(subtotal, discount_code)
        after_discount = subtotal - discount
        tax = after_discount * self.tax_rate
        shipping = 0 if after_discount >= self.free_shipping_threshold \
                     else self.standard_shipping
        total = after_discount + tax + shipping
        return OrderPricing(subtotal, discount, tax, shipping, total)

# service.py
class OrderService:
    def __init__(self, validator, pricing_service, inventory_repo,
                 payment_processor, order_repo, notifications):
        self.validator = validator
        self.pricing_service = pricing_service
        self.inventory_repo = inventory_repo
        self.payment_processor = payment_processor
        self.order_repo = order_repo
        self.notifications = notifications

    def process_order(self, order: Order) -> dict:
        errors = self.validator.validate(order)
        if errors:
            return {"success": False, "error": "; ".join(errors)}

        for item in order.items:
            stock = self.inventory_repo.get_stock(item.product_id)
            if stock < item.quantity:
                return {"success": False,
                        "error": f"Insufficient stock for: {item.name}"}

        pricing = self.pricing_service.calculate_pricing(
            order.items, order.discount_code)

        payment = self.payment_processor.process_payment(
            pricing.total, order.payment_method, order.payment_details)
        if not payment["success"]:
            return {"success": False,
                    "error": f"Payment failed: {payment['error']}"}

        order.confirm(pricing, payment["payment_id"])
        self.order_repo.save(order)

        for item in order.items:
            self.inventory_repo.reduce_stock(item.product_id, item.quantity)

        self.notifications.send_order_confirmation(
            order.customer_email, order.id, pricing)

        return {"success": True, "order_id": order.id,
                "pricing": pricing, "payment_id": order.payment_id}
```

---

## Principles Applied: Summary

```
PRINCIPLES APPLIED IN THIS REFACTORING:

  +------------------------------+-------------------------------+
  | Principle                    | Where it was applied          |
  +------------------------------+-------------------------------+
  | Single Responsibility (Ch 8) | Each class has ONE job:       |
  |                              | validate, price, pay, save,   |
  |                              | notify, orchestrate.          |
  +------------------------------+-------------------------------+
  | Open/Closed (Ch 9)          | DiscountStrategy interface:   |
  |                              | add new discounts without     |
  |                              | modifying PricingService.     |
  +------------------------------+-------------------------------+
  | Dependency Inversion (Ch 12)| OrderService depends on       |
  |                              | interfaces, not MySQL or SMTP.|
  +------------------------------+-------------------------------+
  | Dependency Injection (Ch 24)| All dependencies injected     |
  |                              | via constructor.              |
  +------------------------------+-------------------------------+
  | Strategy Pattern (Ch 25)    | DiscountStrategy and          |
  |                              | PaymentProcessor are swappable|
  +------------------------------+-------------------------------+
  | Meaningful Names (Ch 2)     | OrderItem, PricingService,    |
  |                              | InventoryRepository -- clear. |
  +------------------------------+-------------------------------+
  | Clean Functions (Ch 3)      | Each method does one thing.   |
  |                              | No method exceeds 20 lines.   |
  +------------------------------+-------------------------------+
  | Error Handling (Ch 6)       | Exceptions with context.      |
  |                              | Resources properly closed.    |
  +------------------------------+-------------------------------+
  | Testability                  | Every component testable in   |
  |                              | isolation with fake deps.     |
  +------------------------------+-------------------------------+
```

---

## Common Mistakes

### Mistake 1: Refactoring Everything at Once

Trying to do all six steps in one commit. If anything breaks, you cannot tell which step caused it.

**Fix:** One step per commit. Run tests after each step. Keep the code working at every point.

### Mistake 2: Refactoring Without Tests

Starting to refactor the god class without characterization tests. You will not know if you changed behavior.

**Fix:** Write characterization tests for the god class first (Chapter 30). Then refactor with confidence.

### Mistake 3: Creating Too Many Tiny Classes

Splitting so aggressively that each class has only one method and you need to trace through fifteen files to understand a flow.

**Fix:** Aim for cohesive classes with 3-10 methods, not one-method classes. Group related behavior.

---

## Best Practices

1. **Refactor in small, verifiable steps.** Each step should produce working, tested code.
2. **Write characterization tests first.** Know what the code does before changing it.
3. **Extract the easiest piece first.** Build momentum with a simple extraction (validation is often easiest).
4. **Keep the orchestrator thin.** The final service should only coordinate, not contain business logic.
5. **Use interfaces for external boundaries.** Databases, APIs, email -- these should be behind interfaces.
6. **Commit after each step.** If something goes wrong, you can revert to the last working state.

---

## Quick Summary

```
PROJECT REFACTORING AT A GLANCE:

  BEFORE: 1 file, 300 lines, 8+ responsibilities, untestable

  AFTER:  6+ files, each < 50 lines, 1 responsibility each, testable

  Steps:
  1. Create domain objects (replace Maps with types)
  2. Extract validation
  3. Extract pricing (with strategy for discounts)
  4. Extract repositories (database behind interfaces)
  5. Extract payment processing (behind interface)
  6. Extract notifications (behind interface)

  Result: OrderService orchestrates clean components.
          Every component is independently testable.
          Every dependency is injected.
```

---

## Key Points

- A god class is a single class with too many responsibilities. It is rigid, untestable, and painful to modify.
- Refactoring a god class is done in small, safe steps -- never as a big-bang rewrite.
- Create domain objects first to replace untyped data structures like Maps.
- Extract each responsibility into its own class: validation, pricing, persistence, payment, notification.
- Use interfaces for external dependencies (database, payment, email) to enable testing and flexibility.
- Use the Strategy pattern for behavior that varies (discounts, payment methods).
- The final service class should only orchestrate -- it should contain no business logic of its own.
- Write characterization tests before refactoring and run tests after every step.

---

## Practice Questions

1. Why is it important to refactor in small steps rather than rewriting the entire god class at once?

2. The original `OrderProcessor` uses `Map<String, Object>` for order data. What specific problems does this cause, and how do domain objects solve them?

3. Why did we extract `DiscountStrategy` as an interface instead of putting all discount logic directly in `PricingService`?

4. After the refactoring, the `OrderService` has six constructor parameters. Is this a problem? Why or why not?

5. How would you add a new payment method (e.g., Bitcoin) to the refactored code? How many files would you need to change compared to the original god class?

---

## Exercises

### Exercise 1: Add a New Feature

Using the refactored code, add support for a "loyalty points" discount. Loyal customers earn points on each purchase, and those points can be redeemed as a discount on future orders. Implement this as a new `DiscountStrategy` without modifying any existing discount code.

### Exercise 2: Refactor a Python God Class

Take this Python god class and refactor it following the same six-step process:

```python
class ReportGenerator:
    def generate(self, report_type, date_range, format_type, recipients):
        # 1. Validate inputs (30 lines)
        # 2. Query database for raw data (40 lines)
        # 3. Transform and aggregate data (50 lines)
        # 4. Format as PDF/CSV/Excel (60 lines)
        # 5. Save to file system (20 lines)
        # 6. Email to recipients (30 lines)
        # Total: ~230 lines, all in one method
        pass
```

### Exercise 3: Write Tests for the Orchestrator

Write a complete test suite for the `OrderService` orchestrator using fake implementations. Test: successful order, validation failure, insufficient stock, payment failure, and discount application.

---

## What Is Next?

Congratulations -- you have just completed the most comprehensive refactoring in this book. The final chapter provides a Glossary of all the terms, patterns, and principles you have learned, along with recommended reading to continue your journey into clean code and software architecture.
