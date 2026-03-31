# Chapter 13: DRY, KISS, and YAGNI -- The Three Pillars of Pragmatic Code

## What You Will Learn

- What the DRY principle really means and when duplication is actually acceptable
- How to apply KISS to write the simplest solution that genuinely works
- Why YAGNI saves you from building features nobody asked for
- How to recognize over-engineering and premature abstraction
- The Rule of Three for deciding when to eliminate duplication
- Practical before-and-after transformations for each principle

## Why This Chapter Matters

Every developer eventually writes code that is too clever, too abstract, or too duplicated. These three principles -- DRY, KISS, and YAGNI -- act as guardrails that keep your code practical and maintainable. They sound simple, but applying them well requires judgment. Misapplying them causes just as many problems as ignoring them. This chapter gives you that judgment.

---

## 13.1 DRY -- Don't Repeat Yourself

### The Core Idea

DRY was coined by Andy Hunt and Dave Thomas in "The Pragmatic Programmer." It states:

> Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.

Notice: DRY is about **knowledge**, not just code. Two identical lines of code are not necessarily a DRY violation if they represent different pieces of knowledge.

### What DRY Actually Means

```
  +--------------------------------------------------+
  |              DRY IS ABOUT KNOWLEDGE               |
  +--------------------------------------------------+
  |                                                    |
  |  Same code, same reason to change  -->  Violation  |
  |  Same code, different reasons      -->  Acceptable |
  |  Different code, same knowledge    -->  Violation   |
  |                                                    |
  +--------------------------------------------------+
```

### BEFORE: DRY Violation (Java)

```java
public class OrderService {

    public double calculateOrderTotal(Order order) {
        double total = 0;
        for (OrderItem item : order.getItems()) {
            total += item.getPrice() * item.getQuantity();
        }
        // Apply 10% tax
        total = total * 1.10;
        return total;
    }

    public double calculateInvoiceTotal(Invoice invoice) {
        double total = 0;
        for (InvoiceItem item : invoice.getItems()) {
            total += item.getPrice() * item.getQuantity();
        }
        // Apply 10% tax
        total = total * 1.10;
        return total;
    }

    public String generateOrderSummary(Order order) {
        double total = 0;
        for (OrderItem item : order.getItems()) {
            total += item.getPrice() * item.getQuantity();
        }
        // Apply 10% tax
        total = total * 1.10;
        return "Order total: $" + String.format("%.2f", total);
    }
}
```

The tax rate (10%) and the line-item calculation logic appear three times. If the tax rate changes, you must find and update all three locations.

### AFTER: DRY Applied (Java)

```java
public class OrderService {

    private static final double TAX_RATE = 0.10;

    private double calculateLineItemTotal(List<? extends LineItem> items) {
        double subtotal = 0;
        for (LineItem item : items) {
            subtotal += item.getPrice() * item.getQuantity();
        }
        return subtotal;
    }

    private double applyTax(double subtotal) {
        return subtotal * (1 + TAX_RATE);
    }

    public double calculateOrderTotal(Order order) {
        return applyTax(calculateLineItemTotal(order.getItems()));
    }

    public double calculateInvoiceTotal(Invoice invoice) {
        return applyTax(calculateLineItemTotal(invoice.getItems()));
    }

    public String generateOrderSummary(Order order) {
        double total = calculateOrderTotal(order);
        return "Order total: $" + String.format("%.2f", total);
    }
}
```

Now the tax rate lives in one place, and the line-item calculation is shared through a common interface.

### BEFORE: DRY Violation (Python)

```python
def send_welcome_email(user):
    subject = f"Welcome, {user.name}!"
    body = f"Hi {user.name},\n\nWelcome to our platform."
    smtp = smtplib.SMTP("mail.example.com", 587)
    smtp.starttls()
    smtp.login("noreply@example.com", "secret123")
    smtp.sendmail("noreply@example.com", user.email,
                  f"Subject: {subject}\n\n{body}")
    smtp.quit()

def send_password_reset_email(user, reset_link):
    subject = "Password Reset"
    body = f"Hi {user.name},\n\nClick here to reset: {reset_link}"
    smtp = smtplib.SMTP("mail.example.com", 587)
    smtp.starttls()
    smtp.login("noreply@example.com", "secret123")
    smtp.sendmail("noreply@example.com", user.email,
                  f"Subject: {subject}\n\n{body}")
    smtp.quit()

def send_order_confirmation(user, order_id):
    subject = "Order Confirmed"
    body = f"Hi {user.name},\n\nYour order #{order_id} is confirmed."
    smtp = smtplib.SMTP("mail.example.com", 587)
    smtp.starttls()
    smtp.login("noreply@example.com", "secret123")
    smtp.sendmail("noreply@example.com", user.email,
                  f"Subject: {subject}\n\n{body}")
    smtp.quit()
```

The SMTP connection logic is repeated three times. If you change the mail server, you update three places.

### AFTER: DRY Applied (Python)

```python
class EmailService:
    def __init__(self, host="mail.example.com", port=587,
                 sender="noreply@example.com", password="secret123"):
        self.host = host
        self.port = port
        self.sender = sender
        self.password = password

    def send(self, recipient, subject, body):
        smtp = smtplib.SMTP(self.host, self.port)
        smtp.starttls()
        smtp.login(self.sender, self.password)
        smtp.sendmail(self.sender, recipient,
                      f"Subject: {subject}\n\n{body}")
        smtp.quit()


email_service = EmailService()

def send_welcome_email(user):
    email_service.send(user.email, f"Welcome, {user.name}!",
                       f"Hi {user.name},\n\nWelcome to our platform.")

def send_password_reset_email(user, reset_link):
    email_service.send(user.email, "Password Reset",
                       f"Hi {user.name},\n\nClick here to reset: {reset_link}")

def send_order_confirmation(user, order_id):
    email_service.send(user.email, "Order Confirmed",
                       f"Hi {user.name},\n\nYour order #{order_id} is confirmed.")
```

### When Duplication Is Acceptable

Not all duplication is bad. Here are cases where keeping duplicated code is the right call:

**1. Coincidental duplication.** Two pieces of code look the same today but represent different business concepts that will evolve independently.

```python
# These look similar but serve DIFFERENT business rules
def calculate_employee_bonus(salary):
    return salary * 0.10  # HR policy: 10% bonus

def calculate_sales_tax(price):
    return price * 0.10  # Tax law: 10% tax rate
```

Merging these into a single `apply_ten_percent()` function would be wrong. When the tax rate changes to 12%, you do not want to accidentally change bonuses too.

**2. Across bounded contexts.** In microservices or modular systems, some duplication between services is healthier than coupling them through shared libraries.

**3. Test code.** Tests should be readable and self-contained. A little duplication in tests is far better than fragile shared test helpers.

### The Rule of Three

> The first time you write something, just write it. The second time, wince but duplicate it. The third time, refactor.

This rule prevents premature abstraction. You need at least three examples of duplication to understand the true pattern before you extract it.

```
  Occurrence 1:  Write it.
                    |
  Occurrence 2:  Duplicate it. Note the similarity.
                    |
  Occurrence 3:  NOW refactor. You understand the pattern.
```

---

## 13.2 KISS -- Keep It Simple, Stupid

### The Core Idea

KISS says: choose the simplest solution that correctly solves the problem. Complexity is a cost. Every line of clever code is a line that a future developer (including future you) must understand.

### The Simplicity Spectrum

```
  Too Simple          Just Right           Over-Engineered
  (doesn't work)     (KISS sweet spot)    (works but nobody
                                           can maintain it)
      |                    |                     |
      +--------------------+---------------------+

  Example:            Example:              Example:
  No validation       If/else check         Custom validation
  at all              with clear message    framework with
                                            plugin system and
                                            XML configuration
```

### BEFORE: Over-Complicated (Java)

```java
// Someone wanted a "flexible" way to check if a number is even
public class NumberClassifierFactory {

    public interface NumberClassificationStrategy {
        boolean classify(int number);
    }

    public static class EvenClassificationStrategy
            implements NumberClassificationStrategy {
        @Override
        public boolean classify(int number) {
            return number % 2 == 0;
        }
    }

    public static NumberClassificationStrategy createStrategy(String type) {
        switch (type) {
            case "even": return new EvenClassificationStrategy();
            default: throw new IllegalArgumentException("Unknown type: " + type);
        }
    }
}

// Usage
NumberClassificationStrategy strategy =
    NumberClassifierFactory.createStrategy("even");
boolean result = strategy.classify(42);
```

### AFTER: KISS Applied (Java)

```java
public class NumberUtils {
    public static boolean isEven(int number) {
        return number % 2 == 0;
    }
}

// Usage
boolean result = NumberUtils.isEven(42);
```

Same functionality. One method instead of an entire factory-strategy hierarchy.

### BEFORE: Over-Complicated (Python)

```python
from abc import ABC, abstractmethod

class DataTransformerBase(ABC):
    @abstractmethod
    def transform(self, data):
        pass

class UpperCaseTransformer(DataTransformerBase):
    def transform(self, data):
        return data.upper()

class LowerCaseTransformer(DataTransformerBase):
    def transform(self, data):
        return data.lower()

class TransformerPipeline:
    def __init__(self):
        self.transformers = []

    def add_transformer(self, transformer):
        self.transformers.append(transformer)

    def execute(self, data):
        result = data
        for t in self.transformers:
            result = t.transform(result)
        return result

# Usage: just to convert a string to uppercase
pipeline = TransformerPipeline()
pipeline.add_transformer(UpperCaseTransformer())
result = pipeline.execute("hello world")
```

### AFTER: KISS Applied (Python)

```python
result = "hello world".upper()
```

One line. No classes. No pipeline. The built-in method does exactly what we need.

### Real-World Scenario: Configuration Loading

A team needs to load application configuration from a file.

**Over-engineered approach:**
```
  +-------------------+     +-----------------+     +------------------+
  | ConfigLoaderFactory| --> | ConfigParser    | --> | ConfigValidator  |
  +-------------------+     | Interface       |     | Interface        |
           |                +-----------------+     +------------------+
           |                   |          |              |
           v                   v          v              v
  +------------------+  +----------+ +----------+ +------------+
  | ConfigBuilder    |  | YAMLImpl | | JSONImpl | | SchemaValid|
  +------------------+  +----------+ +----------+ +------------+
```

**KISS approach:**

```python
import json

def load_config(filepath="config.json"):
    with open(filepath) as f:
        return json.load(f)

config = load_config()
```

Start simple. Add YAML support only when someone actually needs it. Add validation only when bad configs cause real problems.

---

## 13.3 YAGNI -- You Aren't Gonna Need It

### The Core Idea

YAGNI comes from Extreme Programming. It states: do not add functionality until it is necessary. The cost of building unused features is enormous:

```
  Cost of a Feature You Don't Need:
  +------------------------------------------+
  |  Time to build it              (wasted)   |
  |  Time to test it               (wasted)   |
  |  Time to maintain it           (ongoing)  |
  |  Complexity it adds            (ongoing)  |
  |  Bugs it might introduce       (ongoing)  |
  |  Time to understand it later   (ongoing)  |
  +------------------------------------------+
```

Studies show that roughly 65% of features in software products are rarely or never used.

### BEFORE: YAGNI Violation (Java)

A team needs a simple user registration system. One developer anticipates "future needs."

```java
public class UserService {

    // Current requirement: register users with email and password
    // "Future-proofed" with things nobody asked for

    private final UserRepository userRepository;
    private final EventBus eventBus;
    private final AuditLogService auditLogService;
    private final NotificationPreferenceService notifPrefService;
    private final UserProfileImageService imageService;
    private final SocialMediaLinkingService socialService;
    private final TwoFactorAuthService twoFactorService;
    private final GamificationService gamificationService;

    public User registerUser(RegistrationRequest request) {
        // Validate (required)
        validateEmail(request.getEmail());
        validatePassword(request.getPassword());

        // Create user (required)
        User user = new User(request.getEmail(),
                            hashPassword(request.getPassword()));
        userRepository.save(user);

        // --- Everything below is YAGNI ---

        // Set up default notification preferences
        notifPrefService.createDefaults(user);

        // Generate default avatar
        imageService.generateDefaultAvatar(user);

        // Set up gamification profile
        gamificationService.initializeProfile(user);

        // Prepare 2FA enrollment (not required yet)
        twoFactorService.prepareEnrollment(user);

        // Link social accounts (nobody asked for this)
        socialService.checkAndLink(user);

        // Publish event (no consumers exist yet)
        eventBus.publish(new UserRegisteredEvent(user));

        // Audit log (no compliance requirement yet)
        auditLogService.log("USER_REGISTERED", user.getId());

        return user;
    }
}
```

### AFTER: YAGNI Applied (Java)

```java
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User registerUser(String email, String password) {
        validateEmail(email);
        validatePassword(password);

        User user = new User(email, hashPassword(password));
        userRepository.save(user);
        return user;
    }

    private void validateEmail(String email) {
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("Invalid email address");
        }
    }

    private void validatePassword(String password) {
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException(
                "Password must be at least 8 characters");
        }
    }

    private String hashPassword(String password) {
        return BCrypt.hashpw(password, BCrypt.gensalt());
    }
}
```

Clean. Does exactly what the requirements say. When someone actually needs 2FA, gamification, or social linking, you add it then -- with the benefit of understanding the real requirements.

### BEFORE: YAGNI Violation (Python)

```python
class DataProcessor:
    """Processes data from CSV files."""

    def __init__(self, source_type="csv"):
        self.source_type = source_type
        # "Supporting" formats nobody uses yet
        self.parsers = {
            "csv": self._parse_csv,
            "json": self._parse_json,       # Not needed yet
            "xml": self._parse_xml,         # Not needed yet
            "yaml": self._parse_yaml,       # Not needed yet
            "excel": self._parse_excel,     # Not needed yet
            "parquet": self._parse_parquet,  # Not needed yet
        }
        self.output_formats = ["csv", "json", "xml", "html", "pdf"]
        self.compression_types = ["gzip", "bzip2", "lzma", "zip"]

    def process(self, filepath):
        parser = self.parsers.get(self.source_type)
        if not parser:
            raise ValueError(f"Unsupported format: {self.source_type}")
        return parser(filepath)

    def _parse_csv(self, filepath):
        # Actual implementation
        import csv
        with open(filepath) as f:
            return list(csv.DictReader(f))

    def _parse_json(self, filepath):
        raise NotImplementedError("Coming soon!")

    def _parse_xml(self, filepath):
        raise NotImplementedError("Coming soon!")

    def _parse_yaml(self, filepath):
        raise NotImplementedError("Coming soon!")

    def _parse_excel(self, filepath):
        raise NotImplementedError("Coming soon!")

    def _parse_parquet(self, filepath):
        raise NotImplementedError("Coming soon!")
```

Half of these methods are stubs that throw `NotImplementedError`. They add noise, give a false impression of capability, and clutter the interface.

### AFTER: YAGNI Applied (Python)

```python
import csv

class CsvProcessor:
    """Processes data from CSV files."""

    def process(self, filepath):
        with open(filepath) as f:
            return list(csv.DictReader(f))
```

When someone needs JSON support, add a `JsonProcessor`. When multiple formats are in use, then consider a common interface. Not before.

### Over-Engineering: A Real-World Story

Imagine a team building an internal tool for 20 users. They spend three months building:

- A plugin architecture for custom data sources
- A role-based access control system with eight permission levels
- A caching layer with configurable eviction strategies
- An internationalization system supporting 12 languages
- A theming engine with custom CSS compilation

The actual need was a form that reads from one database and displays results in a table for 20 English-speaking employees in the same department.

```
  What was needed:          What was built:

  +--------+  +-------+    +--------+  +--------+  +--------+
  | Form   |->| Table |    | Plugin |  | RBAC   |  | Cache  |
  +--------+  +-------+    | System |  | System |  | Layer  |
                            +--------+  +--------+  +--------+
                            +--------+  +--------+  +--------+
                            | i18n   |  | Theme  |  | API    |
                            | Engine |  | Engine |  | Gateway|
                            +--------+  +--------+  +--------+

  1 week of work             3 months of work
  Maintained by anyone       Maintained by specialists
```

### Premature Abstraction

Premature abstraction is one of the most common YAGNI violations. It happens when you create interfaces, abstract classes, or generic solutions before you have enough concrete examples.

```java
// Premature: only one payment method exists
public interface PaymentProcessor {
    PaymentResult process(Payment payment);
}

public class CreditCardProcessor implements PaymentProcessor {
    public PaymentResult process(Payment payment) {
        // ... credit card logic
    }
}

// When you only have one implementation, the interface
// adds complexity without benefit. Just use the class directly.
```

**Better approach:** Write the concrete class first. When a second payment method is needed, then extract the interface.

---

## 13.4 How the Three Principles Work Together

```
  +----------------------------------------------------------+
  |               The Pragmatic Code Triangle                 |
  |                                                           |
  |              DRY                                          |
  |             /   \          "Is this knowledge             |
  |            /     \          duplicated?"                   |
  |           /       \                                       |
  |          /  GOOD   \                                      |
  |         /   CODE    \                                     |
  |        /             \                                    |
  |     KISS ----------- YAGNI                                |
  |  "Is this the       "Do I actually                        |
  |   simplest way?"     need this?"                          |
  +----------------------------------------------------------+
```

**Decision flow when writing code:**

```
  Need to implement something?
         |
         v
  Do I actually need this now? ----NO----> Don't build it (YAGNI)
         |
        YES
         |
         v
  Is there a simpler way? --------YES----> Use the simpler way (KISS)
         |
        NO (this is the simplest)
         |
         v
  Does this duplicate existing
  knowledge? ---------------------YES----> Reuse existing code (DRY)
         |                                  (if Rule of Three is met)
        NO
         |
         v
  Write the code.
```

### Balancing the Principles

Sometimes the principles conflict:

| Situation | DRY Says | KISS Says | YAGNI Says | Best Choice |
|-----------|----------|-----------|------------|-------------|
| Two similar functions | Merge them | Keep them separate if simpler | Only merge if both are needed | Depends on Rule of Three |
| Adding an interface | Extract common behavior | Skip the interface | Don't add until second implementation | Wait for second use case |
| Shared utility library | Centralize common code | Keep it local if simpler | Don't build a library for one use | Start local, extract later |

---

## Common Mistakes

1. **Treating DRY as "never duplicate any code."** DRY is about knowledge duplication, not textual duplication. Two functions that look the same but represent different business rules should stay separate.

2. **Applying KISS to mean "no abstractions ever."** KISS does not mean dumb code. It means the right level of abstraction for the current problem. A well-named function is simpler than inline code, even though it adds an abstraction.

3. **Using YAGNI as an excuse for no planning.** YAGNI means don't build features you don't need. It does not mean don't think about architecture or design. You should still write extensible code -- just don't implement the extensions.

4. **Refactoring too early.** Extracting a shared function after seeing duplication only twice often leads to the wrong abstraction. Wait for three occurrences.

5. **Confusing "simple" with "easy."** Simple means fewer concepts and moving parts. Easy means familiar. A regex might be easy for you but it is not simple. A well-named function with clear logic is simple even if you have to write more lines.

---

## Best Practices

1. **Apply the Rule of Three before extracting shared code.** Tolerate duplication until you see the pattern clearly in three places.

2. **Start with the simplest implementation that works.** You can always add complexity later. You rarely remove it.

3. **Ask "who asked for this?" before building any feature.** If the answer is "nobody yet," stop.

4. **Prefer boring technology.** A simple database query is better than an in-memory cache you need to invalidate. A flat file is better than a message queue for batch processing 10 records.

5. **Delete code you do not need.** Commented-out code, unused functions, dead feature flags -- remove them. Version control remembers everything.

6. **Review for over-engineering during code reviews.** Ask teammates: "Is there a simpler way to do this?"

7. **Write code for the current requirements.** Design for extensibility, but implement only what is needed now.

---

## Quick Summary

| Principle | Meaning | Misuse |
|-----------|---------|--------|
| DRY | One source of truth for each piece of knowledge | Merging unrelated code that happens to look similar |
| KISS | Choose the simplest correct solution | Avoiding all abstractions; writing spaghetti code |
| YAGNI | Don't build features until they are needed | Skipping all design and planning |

---

## Key Points

- DRY is about knowledge duplication, not code duplication. Two identical lines can be acceptable if they represent independent concepts.
- KISS means choosing the right level of complexity -- not the lowest level of complexity.
- YAGNI protects you from building features that may never be used, saving time and reducing maintenance burden.
- The Rule of Three is your guide for when to eliminate duplication: tolerate it until the third occurrence.
- Over-engineering and premature abstraction cause more damage than the problems they try to prevent.
- These three principles work together as a decision framework for every line of code you write.

---

## Practice Questions

1. A colleague duplicates a 15-line validation function in two microservices. They argue that DRY requires creating a shared library. What factors would you consider before agreeing or disagreeing?

2. You are asked to build a reporting feature. The product manager says, "Make it support PDF, CSV, and Excel export." Your analytics show 95% of users only download CSV. How would you apply YAGNI here?

3. A junior developer writes a `GenericRepositoryFactoryProvider<T, ID>` class to wrap a simple database query. The application has exactly one entity type. What would you say in a code review?

4. You find three functions in different modules that each parse a date string in the format "YYYY-MM-DD". Should you extract a shared utility? What questions would you ask first?

5. How does the Rule of Three help prevent premature abstraction? Give an example where extracting after two occurrences would lead to the wrong abstraction.

---

## Exercises

### Exercise 1: Identify the Violations

Look at the following code and identify which principles (DRY, KISS, YAGNI) are violated:

```python
class UserManager:
    def create_user(self, name, email):
        # Validate email
        if "@" not in email:
            raise ValueError("Invalid email")
        user = {"name": name, "email": email}
        self.save_to_db(user)
        self.save_to_cache(user)        # No cache exists yet
        self.save_to_search_index(user)  # No search feature yet
        self.send_to_analytics(user)     # No analytics yet
        self.sync_to_backup_db(user)     # No backup DB yet
        return user

    def update_user(self, user_id, name, email):
        # Validate email (same code as above)
        if "@" not in email:
            raise ValueError("Invalid email")
        user = {"id": user_id, "name": name, "email": email}
        self.save_to_db(user)
        self.save_to_cache(user)
        self.save_to_search_index(user)
        self.send_to_analytics(user)
        self.sync_to_backup_db(user)
        return user
```

Rewrite this code applying all three principles correctly.

### Exercise 2: Simplify the Over-Engineered Solution

Refactor this Java code to follow KISS:

```java
public class StringReverserStrategyExecutorService {
    public interface ReverseStrategy {
        String reverse(String input);
    }

    public static class RecursiveReverseStrategy implements ReverseStrategy {
        public String reverse(String input) {
            if (input.isEmpty()) return input;
            return reverse(input.substring(1)) + input.charAt(0);
        }
    }

    public String executeReverse(String input, ReverseStrategy strategy) {
        return strategy.reverse(input);
    }
}
```

### Exercise 3: Apply the Rule of Three

You discover the following date formatting code in three different files of your project:

```python
# In order_service.py
order_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")

# In report_generator.py
report_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")

# In notification_service.py
notify_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
```

This is the third occurrence. Extract an appropriate shared utility. Consider: where should it live? What should it be named? How would you ensure the original callers are updated?

---

## What Is Next?

Now that you understand the principles that guide clean code decisions, the next chapter dives into **Code Smells** -- the warning signs that tell you something is wrong with your code. You will learn to recognize 13 common code smells, understand why they matter, and know exactly how to fix each one.
