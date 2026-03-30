# Chapter 6: Dependency Injection -- Wiring Your Application Together

## What You Will Learn

- What a dependency is in programming
- Why manually creating objects causes problems (the old way)
- How Spring creates and manages objects for you (the Spring way)
- What the IoC container is (and a hiring agency analogy)
- How constructor injection works
- What `@Autowired` does and when you need it
- Why dependency injection matters for testing and maintainability
- A real example with `OrderService` and `EmailService`

## Why This Chapter Matters

Every real application has multiple parts that work together. A controller calls a service. A service calls a repository. A repository talks to a database.

These parts depend on each other. How you connect them determines whether your code is easy to change, easy to test, and easy to understand -- or a tangled mess.

Dependency injection is the single most important concept in Spring. Every Spring application uses it. Every Spring annotation relates to it in some way. If you understand this chapter, the rest of the framework clicks into place.

---

## 6.1 What Is a Dependency?

In programming, a **dependency** is an object that another object needs to do its job.

Think of a chef in a restaurant. The chef **depends on** a knife to chop vegetables. The knife is a dependency of the chef. Without it, the chef cannot do their work.

In code, if class A uses class B, then B is a dependency of A.

```java
public class OrderService {
    private EmailService emailService;  // EmailService is a dependency
}
```

`OrderService` needs `EmailService` to send order confirmations. Without it, `OrderService` cannot complete its job.

```
+--------------------------------------------------+
|           What Is a Dependency?                  |
+--------------------------------------------------+
|                                                   |
|   OrderService depends on EmailService            |
|                                                   |
|   OrderService ----needs----> EmailService        |
|                                                   |
|   "I need you to send emails for me."             |
|                                                   |
|   The chef      ----needs----> the knife          |
|   "I need you to chop vegetables for me."         |
|                                                   |
+--------------------------------------------------+
```

---

## 6.2 The Old Way: Creating Objects Yourself

Before Spring, developers created dependencies manually. Here is what that looked like:

```java
public class OrderService {

    private EmailService emailService;

    public OrderService() {
        this.emailService = new EmailService();     // 1
    }

    public void placeOrder(String item) {
        System.out.println("Order placed: " + item);
        emailService.sendConfirmation(item);        // 2
    }
}
```

- **Line 1:** `OrderService` creates its own `EmailService` using `new`. This is the problem.
- **Line 2:** `OrderService` uses the `EmailService` to send a confirmation email.

This looks simple. What is wrong with it?

### Problem 1: Tight Coupling

`OrderService` is **tightly coupled** to `EmailService`. The word "coupled" means "connected." Tight coupling means the connection is rigid and hard to change.

If you want to replace `EmailService` with `SmsService`, you must change the code inside `OrderService`. In a big application, `EmailService` might be used in 50 classes. You would need to change all 50.

### Problem 2: Hard to Test

When you write tests for `OrderService`, you do not want to send real emails. You want a fake `EmailService` that pretends to send emails. But `OrderService` creates its own `EmailService` with `new`. You cannot swap it for a fake one.

### Problem 3: Hidden Dependencies

Looking at `OrderService` from the outside, you cannot see what it needs. The dependency is hidden inside the constructor. If `OrderService` needs five other objects, they are all buried in the code.

```
+----------------------------------------------------------+
|     Problems with "new" (Creating Objects Yourself)      |
+----------------------------------------------------------+
|                                                           |
|   Problem 1: Tight Coupling                               |
|     OrderService is glued to EmailService.                 |
|     You cannot swap it without changing the code.          |
|                                                           |
|   Problem 2: Hard to Test                                 |
|     You cannot replace EmailService with a fake            |
|     version during testing.                                |
|                                                           |
|   Problem 3: Hidden Dependencies                          |
|     You cannot see what OrderService needs                 |
|     without reading its internal code.                     |
|                                                           |
+----------------------------------------------------------+
```

---

## 6.3 The Spring Way: Let Someone Else Create Objects

Spring takes a different approach. Instead of each class creating its own dependencies, Spring creates all the objects and **injects** them where they are needed.

Here is the same example, the Spring way:

```java
@Service                                                 // 1
public class EmailService {

    public void sendConfirmation(String item) {
        System.out.println("Email sent for: " + item);
    }
}
```

```java
@Service                                                 // 2
public class OrderService {

    private final EmailService emailService;             // 3

    public OrderService(EmailService emailService) {     // 4
        this.emailService = emailService;
    }

    public void placeOrder(String item) {
        System.out.println("Order placed: " + item);
        emailService.sendConfirmation(item);
    }
}
```

**Line-by-line explanation:**

- **Line 1:** `@Service` on `EmailService` tells Spring: "Create an instance of this class and manage it." Spring creates one `EmailService` object and keeps it ready.

- **Line 2:** `@Service` on `OrderService` tells Spring the same thing.

- **Line 3:** `private final EmailService emailService;` -- The dependency is declared as a field. The `final` keyword means it must be set once and cannot change.

- **Line 4:** The constructor takes `EmailService` as a parameter. Spring sees this and says: "OrderService needs an EmailService. I already created one. Let me pass it in."

Notice what is different:

- No `new EmailService()` anywhere.
- `OrderService` does not create its own dependency.
- Spring creates both objects and connects them.

This is **dependency injection**. The dependency (`EmailService`) is **injected** into `OrderService` through the constructor.

---

## 6.4 The IoC Container: The Hiring Agency Analogy

Spring uses something called an **IoC Container**. IoC stands for **Inversion of Control**.

**What does "Inversion of Control" mean?**

Normally, your code controls everything. It creates objects, connects them, and manages their lifecycle. With IoC, this control is **inverted** (flipped). The framework (Spring) takes control. Your code just declares what it needs.

Think of it like hiring employees at a company:

**Without IoC (You do everything yourself):**
1. You write a job posting
2. You review resumes
3. You interview candidates
4. You hire the person
5. You train them
6. You assign them to a team

**With IoC (Hiring agency does it for you):**
1. You tell the agency: "I need a Java developer"
2. The agency finds one, hires them, and sends them to your office

The hiring agency is the IoC container. You declare what you need. The agency provides it.

```
+----------------------------------------------------------+
|     The Hiring Agency Analogy                            |
+----------------------------------------------------------+
|                                                           |
|   Spring IoC Container = Hiring Agency                    |
|                                                           |
|   You (OrderService):                                     |
|     "I need an EmailService employee."                    |
|                                                           |
|   Hiring Agency (Spring):                                 |
|     "I have one. Here you go."                            |
|     [passes EmailService to OrderService]                 |
|                                                           |
|   You (OrderController):                                  |
|     "I need an OrderService employee."                    |
|                                                           |
|   Hiring Agency (Spring):                                 |
|     "I have one (with EmailService already assigned).     |
|      Here you go."                                        |
|     [passes OrderService to OrderController]              |
|                                                           |
+----------------------------------------------------------+
```

The IoC container holds all the objects (called **beans**) and knows how to wire them together. When a bean needs another bean, the container provides it.

```
+----------------------------------------------------------+
|     Inside the IoC Container                             |
+----------------------------------------------------------+
|                                                           |
|   +------------------+                                    |
|   |  IoC Container   |                                    |
|   |                  |                                    |
|   |  Beans:          |                                    |
|   |   - EmailService |-----+                              |
|   |   - OrderService |--+  |                              |
|   |   - OrderController |  |                              |
|   |                  |  |  |                              |
|   +------------------+  |  |                              |
|                         |  |                              |
|   OrderService needs    |  |                              |
|   EmailService -------->+--+                              |
|                                                           |
|   OrderController needs                                   |
|   OrderService -------->+                                 |
|                                                           |
+----------------------------------------------------------+
```

---

## 6.5 Constructor Injection (The Recommended Way)

There are three ways to inject dependencies in Spring:

1. **Constructor injection** (recommended)
2. Field injection
3. Setter injection

We will focus on constructor injection because it is the best practice recommended by the Spring team.

### How Constructor Injection Works

```java
@Service
public class OrderService {

    private final EmailService emailService;
    private final PaymentService paymentService;

    // Constructor injection: Spring passes both dependencies
    public OrderService(EmailService emailService,
                        PaymentService paymentService) {
        this.emailService = emailService;
        this.paymentService = paymentService;
    }

    public void placeOrder(String item, double amount) {
        paymentService.charge(amount);
        System.out.println("Order placed: " + item);
        emailService.sendConfirmation(item);
    }
}
```

Spring sees the constructor and says: "This class needs `EmailService` and `PaymentService`. I have both in my container. Let me pass them in."

### Why Constructor Injection Is Best

| Benefit                  | Explanation                                                    |
|-------------------------|----------------------------------------------------------------|
| **Immutability**        | Fields are `final`. Once set, they cannot change.              |
| **Required dependencies** | If a dependency is missing, the app fails at startup, not at runtime. |
| **Easy to test**        | In tests, just call `new OrderService(mockEmail, mockPayment)`. |
| **Clear dependencies**  | The constructor lists everything the class needs.              |

```
+----------------------------------------------------------+
|     Why Constructor Injection Wins                       |
+----------------------------------------------------------+
|                                                           |
|   Constructor injection:                                  |
|     - All dependencies are visible in the constructor.    |
|     - Fields are final (immutable).                       |
|     - Missing dependency? App won't start. Fail fast.     |
|     - Easy to test: just pass mocks to the constructor.   |
|                                                           |
|   Field injection (@Autowired on fields):                 |
|     - Dependencies are hidden.                            |
|     - Fields are not final (can be null).                 |
|     - Missing dependency? Null pointer at runtime.        |
|     - Hard to test without Spring's help.                 |
|                                                           |
+----------------------------------------------------------+
```

---

## 6.6 Understanding @Autowired

You might see `@Autowired` in tutorials and older code:

```java
@Service
public class OrderService {

    @Autowired                              // Field injection
    private EmailService emailService;
}
```

`@Autowired` tells Spring: "Inject a bean here." It can be used on fields, constructors, and setter methods.

**Important rule:** If a class has **only one constructor**, Spring automatically injects dependencies through it. You do not need `@Autowired`.

```java
@Service
public class OrderService {

    private final EmailService emailService;

    // @Autowired is optional here (only one constructor)
    public OrderService(EmailService emailService) {
        this.emailService = emailService;
    }
}
```

This is why most modern Spring Boot code does not use `@Autowired` at all. One constructor + Spring = automatic injection.

**When do you need `@Autowired`?**

Only when a class has **multiple constructors** and you want to tell Spring which one to use:

```java
@Service
public class OrderService {

    private final EmailService emailService;
    private final int maxRetries;

    @Autowired                              // Tell Spring: use this constructor
    public OrderService(EmailService emailService) {
        this(emailService, 3);
    }

    public OrderService(EmailService emailService, int maxRetries) {
        this.emailService = emailService;
        this.maxRetries = maxRetries;
    }
}
```

In practice, most classes have one constructor. So you rarely need `@Autowired`.

---

## 6.7 A Complete Example: OrderService + EmailService

Let us build a complete, working example. We will create an order system where `OrderController` calls `OrderService`, and `OrderService` calls `EmailService`.

### The Wiring Diagram

```
+----------------------------------------------------------+
|     Dependency Wiring Diagram                            |
+----------------------------------------------------------+
|                                                           |
|   Browser                                                 |
|     |                                                     |
|     | GET /orders/place?item=Laptop                       |
|     v                                                     |
|   +------------------+                                    |
|   | OrderController  |                                    |
|   |                  |                                    |
|   |  needs:          |                                    |
|   |  - OrderService  |---------+                          |
|   +------------------+         |                          |
|                                |                          |
|                                v                          |
|                    +------------------+                    |
|                    | OrderService     |                    |
|                    |                  |                    |
|                    |  needs:          |                    |
|                    |  - EmailService  |------+             |
|                    +------------------+      |             |
|                                              |             |
|                                              v             |
|                                  +------------------+      |
|                                  | EmailService     |      |
|                                  |                  |      |
|                                  |  no dependencies |      |
|                                  +------------------+      |
|                                                           |
|   Spring creates all three objects and wires them.        |
|                                                           |
+----------------------------------------------------------+
```

### Step 1: Create EmailService

Create `src/main/java/com/example/hellospringboot/service/EmailService.java`:

```java
package com.example.hellospringboot.service;             // 1

import org.springframework.stereotype.Service;            // 2

@Service                                                  // 3
public class EmailService {

    public void sendConfirmation(String item) {           // 4
        // In a real app, this would send an actual email
        System.out.println(                               // 5
            "[EMAIL] Confirmation sent for item: " + item
        );
    }
}
```

**Line-by-line explanation:**

- **Line 1:** The class is in the `service` sub-package. Spring Boot will find it because it is under the base package.
- **Line 2:** Import the `@Service` annotation.
- **Line 3:** `@Service` tells Spring: "This class is a service. Create a bean for it and manage it." Spring will create exactly one instance of `EmailService`.
- **Line 4:** A simple method that "sends" a confirmation.
- **Line 5:** We use `System.out.println` to simulate sending an email. In a real application, this would use an email library.

### Step 2: Create OrderService

Create `src/main/java/com/example/hellospringboot/service/OrderService.java`:

```java
package com.example.hellospringboot.service;             // 1

import org.springframework.stereotype.Service;            // 2

@Service                                                  // 3
public class OrderService {

    private final EmailService emailService;              // 4

    public OrderService(EmailService emailService) {      // 5
        this.emailService = emailService;
    }

    public String placeOrder(String item) {               // 6
        // Process the order
        String message = "Order placed successfully: "
                         + item;
        System.out.println("[ORDER] " + message);         // 7

        // Send confirmation email
        emailService.sendConfirmation(item);              // 8

        return message;                                   // 9
    }
}
```

**Line-by-line explanation:**

- **Line 3:** `@Service` registers this class with Spring.
- **Line 4:** `private final EmailService emailService;` -- Declares the dependency. `final` ensures it is set once.
- **Line 5:** Constructor injection. Spring will pass an `EmailService` instance here.
- **Line 6:** The `placeOrder` method takes an item name and returns a confirmation message.
- **Line 7:** Logs the order to the console.
- **Line 8:** Uses the injected `EmailService` to send a confirmation.
- **Line 9:** Returns the confirmation message (which the controller will send to the browser).

### Step 3: Create OrderController

Create `src/main/java/com/example/hellospringboot/controller/OrderController.java`:

```java
package com.example.hellospringboot.controller;          // 1

import com.example.hellospringboot.service.OrderService; // 2
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController                                          // 3
public class OrderController {

    private final OrderService orderService;             // 4

    public OrderController(OrderService orderService) {  // 5
        this.orderService = orderService;
    }

    @GetMapping("/orders/place")                         // 6
    public String placeOrder(
            @RequestParam String item) {                 // 7
        return orderService.placeOrder(item);            // 8
    }
}
```

**Line-by-line explanation:**

- **Line 3:** `@RestController` marks this class as a web controller.
- **Line 4:** Declares the dependency on `OrderService`.
- **Line 5:** Constructor injection. Spring passes `OrderService` (which already has `EmailService` injected).
- **Line 6:** `@GetMapping("/orders/place")` maps the URL `/orders/place` to this method.
- **Line 7:** `@RequestParam String item` tells Spring to read a query parameter named `item` from the URL. If the URL is `/orders/place?item=Laptop`, then `item` will be `"Laptop"`.
- **Line 8:** Calls the service and returns its result to the browser.

### Step 4: Run and Test

Start the application:

```bash
./mvnw spring-boot:run
```

Open your browser and visit:

```
http://localhost:8080/orders/place?item=Laptop
```

**Browser shows:**

```
Order placed successfully: Laptop
```

**Console shows:**

```
[ORDER] Order placed successfully: Laptop
[EMAIL] Confirmation sent for item: Laptop
```

The request flowed through three layers:

```
Browser --> OrderController --> OrderService --> EmailService
```

Spring created all three objects and wired them together. You never called `new` on any of them.

---

## 6.8 Why Dependency Injection Matters

### Reason 1: Easy to Test

With dependency injection, testing is straightforward:

```java
// In a test, create a mock EmailService
EmailService mockEmail = new EmailService() {
    @Override
    public void sendConfirmation(String item) {
        // Do nothing (fake email)
    }
};

// Pass the mock to OrderService
OrderService orderService = new OrderService(mockEmail);

// Test the order logic without sending real emails
String result = orderService.placeOrder("Laptop");
```

No Spring needed. No configuration. Just plain Java. You inject a fake dependency and test the logic.

### Reason 2: Easy to Change

Want to switch from email to SMS notifications? Create a new service and swap it:

```java
@Service
public class SmsService {
    public void sendConfirmation(String item) {
        System.out.println("[SMS] Confirmation for: " + item);
    }
}
```

If you program to an interface (which we will cover in later chapters), you can swap `EmailService` for `SmsService` without changing `OrderService` at all.

### Reason 3: Clear Dependencies

The constructor tells you exactly what a class needs:

```java
public OrderService(EmailService emailService,
                    PaymentService paymentService,
                    InventoryService inventoryService) {
```

One look at the constructor and you know: `OrderService` needs three things. No surprises. No hidden connections.

---

## 6.9 Annotations That Create Beans

You have seen `@Service` and `@RestController`. Here is the full list of annotations that tell Spring to create a bean:

| Annotation        | Purpose                                    |
|-------------------|--------------------------------------------|
| `@Component`      | General-purpose bean. The base annotation. |
| `@Service`        | A service class (business logic).          |
| `@Repository`     | A data access class (database).            |
| `@Controller`     | A web controller (returns views).          |
| `@RestController` | A REST controller (returns data).          |
| `@Configuration`  | A class that defines beans.                |

They all do the same basic thing: tell Spring to create and manage an instance. The different names (`@Service`, `@Repository`, etc.) are for clarity. They tell other developers the purpose of the class.

```
+----------------------------------------------------------+
|     Bean Stereotype Annotations                          |
+----------------------------------------------------------+
|                                                           |
|                   @Component                              |
|                   (base annotation)                       |
|                       |                                   |
|          +------------+------------+                      |
|          |            |            |                      |
|      @Service    @Repository  @Controller                 |
|    (business     (database    (web layer)                 |
|     logic)       access)          |                       |
|                               @RestController             |
|                              (REST API)                   |
|                                                           |
|   All of these tell Spring:                               |
|   "Create a bean from this class."                        |
|                                                           |
+----------------------------------------------------------+
```

---

## Common Mistakes

1. **Using `new` to create Spring beans.** If you write `new OrderService()`, Spring does not know about that instance. Dependencies will not be injected. Always let Spring create the objects.

2. **Forgetting `@Service` or `@Component`.** If a class does not have a stereotype annotation, Spring will not create a bean for it. You will get an error: "No qualifying bean of type 'X' found."

3. **Using field injection in production code.** `@Autowired` on fields works, but hides dependencies and makes testing harder. Use constructor injection instead.

4. **Circular dependencies.** If A depends on B and B depends on A, Spring cannot create either one. Redesign your classes to break the circle.

5. **Putting classes outside the component scan range.** If your class is not in the base package or a sub-package, Spring will not find it. Always check your package structure.

---

## Best Practices

1. **Always use constructor injection.** Make dependencies `final` and pass them through the constructor.
2. **Omit `@Autowired` when there is only one constructor.** Spring auto-detects it. Less code, same result.
3. **Use the right stereotype annotation.** Use `@Service` for services, `@Repository` for data access, `@RestController` for REST endpoints. This makes your code self-documenting.
4. **Keep beans focused.** Each bean should do one thing well. `EmailService` sends emails. `OrderService` manages orders. Do not mix responsibilities.
5. **Program to interfaces.** Define an interface (e.g., `NotificationService`) and implement it (e.g., `EmailService`). This makes swapping implementations easy. We will cover this in a later chapter.

---

## Quick Summary

Dependency injection is how Spring connects your classes together:

1. You annotate classes with `@Service`, `@Repository`, or `@RestController`.
2. Spring creates instances (beans) of those classes.
3. Spring looks at constructors to see what each bean needs.
4. Spring passes the required beans through constructors (injection).

The IoC container manages the entire lifecycle. You declare what you need. Spring provides it. This makes your code loosely coupled, easy to test, and easy to change.

---

## Key Points

- A **dependency** is an object that another object needs to do its job.
- The **old way** (`new EmailService()`) creates tight coupling. The code is hard to test and hard to change.
- **Dependency injection** means the framework creates objects and passes them where needed.
- The **IoC container** is Spring's object manager. It creates beans and wires them together.
- **Constructor injection** is the recommended way. Declare dependencies as `final` fields. Pass them through the constructor.
- `@Autowired` is optional when a class has only one constructor.
- `@Service`, `@Repository`, `@Controller`, and `@RestController` all tell Spring to create a bean.
- Dependency injection makes code **testable** (inject mocks), **flexible** (swap implementations), and **clear** (dependencies are visible in the constructor).

---

## Practice Questions

1. What is a dependency? Give a real-life analogy and a code example.

2. Why is using `new` to create dependencies considered a bad practice in Spring applications?

3. Explain the Inversion of Control (IoC) concept using the hiring agency analogy.

4. What is the difference between constructor injection and field injection? Why is constructor injection preferred?

5. You see this error: `"No qualifying bean of type 'EmailService' found."` What is the most likely cause? How do you fix it?

---

## Exercises

### Exercise 1: Add a PaymentService

Create a `PaymentService` class with a method `processPayment(double amount)` that prints "Payment processed: $" followed by the amount. Inject it into `OrderService`. Update the `placeOrder` method to call `processPayment` before sending the confirmation email.

Test it by visiting:

```
http://localhost:8080/orders/place?item=Laptop
```

The console should show:

```
[PAYMENT] Payment processed: $999.99
[ORDER] Order placed successfully: Laptop
[EMAIL] Confirmation sent for item: Laptop
```

### Exercise 2: Count Orders

Add an `OrderCountService` that keeps track of how many orders have been placed. It should have two methods:
- `increment()` -- adds 1 to the count
- `getCount()` -- returns the current count

Inject it into `OrderService`. Call `increment()` every time an order is placed. Add a new endpoint `/orders/count` in the controller that returns the current count.

### Exercise 3: Trace the Wiring

Draw a diagram (on paper or in a text file) that shows:
1. All the beans in your application
2. Which bean depends on which other bean
3. The arrows showing the direction of dependency

Compare your diagram with the ASCII wiring diagram in this chapter.

---

## What Is Next?

You now understand how Spring connects your classes together using dependency injection. In the next chapters, we will build on this foundation. You will learn how to work with databases, validate user input, and handle errors -- all using the patterns you learned here.
