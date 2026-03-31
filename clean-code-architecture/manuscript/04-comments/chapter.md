# Chapter 4: Comments -- When They Help and When They Hurt

---

## What You Will Learn

- Why the best comment is the one you did not need to write
- The difference between good comments and bad comments with concrete examples
- Which types of comments actively improve a codebase
- Which types of comments are code smells in disguise
- How to write self-documenting code that eliminates the need for most comments
- Why commented-out code is one of the worst things you can leave in a codebase
- Before/after transformations showing comments replaced by clearer code

---

## Why This Chapter Matters

Comments are a double-edged sword. A good comment can save a developer hours of confusion. A bad comment can waste hours or, worse, actively mislead. The problem is that most comments in most codebases fall into the "bad" category.

Here is the uncomfortable truth: comments are, at best, a necessary evil. If our programming languages were expressive enough, if we were skilled enough to write code that expresses our intent clearly, we would not need comments at all.

Every time you write a comment, you should feel a twinge of failure. Not because commenting is wrong, but because it means you failed to express yourself in code. Before you write a comment, ask yourself: "Can I rename this variable, extract this function, or restructure this logic so the comment becomes unnecessary?"

Sometimes the answer is no, and a comment is genuinely the best tool. This chapter teaches you to tell the difference.

---

## The Problem with Comments

Comments do not make up for bad code. If you write confusing code and then add a comment to explain it, you have two problems: confusing code and a comment that will eventually become outdated and lie to the next developer.

```
+-----------------------------------------------------------+
|              The Comment Lifecycle                        |
+-----------------------------------------------------------+
|                                                           |
|  1. Developer writes code and a comment explaining it     |
|  2. Code works correctly. Comment is accurate.            |
|  3. Months pass. Requirements change.                     |
|  4. Developer modifies the code.                          |
|  5. Developer forgets to update the comment.              |
|  6. Comment now lies about what the code does.            |
|  7. Next developer reads the comment, trusts it.          |
|  8. Next developer wastes hours debugging based on the    |
|     comment's outdated information.                       |
|                                                           |
|  The older a comment gets, the more likely it is wrong.   |
|                                                           |
+-----------------------------------------------------------+
```

### Code Is the Only Source of Truth

Code gets compiled or interpreted. Code gets tested. Code gets executed. Comments do none of these things. When the code and the comment disagree, the comment is always wrong.

**BEFORE: Comment explains unclear code**

Java:
```java
// Check to see if the employee is eligible for full benefits
if ((employee.flags & HOURLY_FLAG) && (employee.age > 65)) {
    // ...
}
```

**AFTER: Code explains itself**

Java:
```java
if (employee.isEligibleForFullBenefits()) {
    // ...
}
```

The comment vanished because the code now says exactly what the comment used to say. The extracted method `isEligibleForFullBenefits()` carries all the meaning, and unlike a comment, it will cause a compile error if the class changes in incompatible ways.

---

## Good Comments

Some comments are necessary and valuable. Here are the types worth keeping.

### Legal Comments

Copyright and license headers are sometimes required by corporate or legal standards. These belong at the top of files.

Java:
```java
/*
 * Copyright (c) 2024 Acme Corporation
 * Licensed under the Apache License, Version 2.0
 * See LICENSE file for details.
 */
```

Python:
```python
# Copyright (c) 2024 Acme Corporation
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.
```

Keep them short. Reference an external license file rather than including the full license text.

### Informative Comments

Sometimes a comment provides useful information that cannot be easily expressed in code.

Java:
```java
// Format: kk:mm:ss EEE, MMM dd, yyyy
Pattern timeMatcher = Pattern.compile(
    "\\d*:\\d*:\\d* \\w*, \\w* \\d*, \\d*");
```

The regex is inherently hard to read. The comment clarifying the format is genuinely helpful.

### Explanation of Intent

Sometimes a comment explains *why* a decision was made, not *what* the code does.

Java:
```java
// We sort by priority descending because the payment processor
// applies the first matching discount rule, and we want the
// highest-value discount to be checked first.
Collections.sort(discountRules, Collections.reverseOrder());
```

Python:
```python
# Using insertion sort here instead of the built-in sort because
# the list is nearly sorted (only 1-2 elements move per update)
# and insertion sort is O(n) for nearly-sorted data.
insertion_sort(almost_sorted_data)
```

These comments explain *why*, not *what*. The code already shows what happens. The comment explains the reasoning behind the choice.

### Clarification

When dealing with code you cannot alter (library calls, legacy APIs), clarification comments help translate obscure operations.

Java:
```java
assertTrue(a.compareTo(b) != 0);    // a != b
assertTrue(a.compareTo(b) == -1);   // a < b
assertTrue(b.compareTo(a) == 1);    // b > a
```

### Warning of Consequences

Comments that warn other developers about consequences are valuable.

Java:
```java
// WARNING: This test takes approximately 30 minutes to run.
// It performs a full integration test against the payment provider's
// staging environment. Only run manually before releases.
@Test
public void testPaymentProviderIntegration() {
    // ...
}
```

Python:
```python
# WARNING: This function is NOT thread-safe. It modifies
# shared state without locking. Use ThreadSafeCounter instead
# if calling from multiple threads.
def increment_counter():
    global _counter
    _counter += 1
```

### TODO Comments

`TODO` comments are acceptable as temporary markers for work that needs to be done but cannot be completed right now.

Java:
```java
// TODO: Extract discount calculation into a strategy pattern
//       when we add the third discount type. -- Jane, 2024-03-15
public double calculateDiscount(Order order) {
    // current simple implementation
}
```

Python:
```python
# TODO: Replace with async HTTP calls when we upgrade to Python 3.12
#       Tracking issue: PROJ-1234
def fetch_all_prices(product_ids):
    return [fetch_price(pid) for pid in product_ids]
```

Good TODO comments include who left them, when, and ideally a ticket reference. They should be reviewed and cleaned up regularly.

### Javadoc for Public APIs

Documentation comments on public APIs are essential. They form the contract between the code and its users.

Java:
```java
/**
 * Calculates the shipping cost for the given order.
 *
 * The cost is determined by the total weight of all items,
 * the shipping destination zone, and the selected speed.
 *
 * @param order  the order containing items with weights
 * @param zone   the destination shipping zone (1-5)
 * @param speed  the shipping speed (STANDARD, EXPRESS, OVERNIGHT)
 * @return the shipping cost in dollars, always non-negative
 * @throws InvalidZoneException if zone is outside range 1-5
 */
public BigDecimal calculateShippingCost(Order order, int zone,
                                         ShippingSpeed speed) {
    // ...
}
```

Python:
```python
def calculate_shipping_cost(order, zone, speed):
    """Calculate the shipping cost for the given order.

    The cost is determined by the total weight of all items,
    the shipping destination zone, and the selected speed.

    Args:
        order: The order containing items with weights.
        zone: The destination shipping zone (1-5).
        speed: The shipping speed (STANDARD, EXPRESS, OVERNIGHT).

    Returns:
        The shipping cost in dollars as a Decimal, always non-negative.

    Raises:
        InvalidZoneError: If zone is outside range 1-5.
    """
    pass
```

```
+-----------------------------------------------------------+
|                  Good Comments Summary                    |
+-----------------------------------------------------------+
|                                                           |
|  Type                |  Purpose                           |
|  --------------------|----------------------------------- |
|  Legal               |  Copyright, license headers        |
|  Informative         |  Clarify obscure constructs        |
|  Intent              |  Explain WHY, not WHAT             |
|  Clarification       |  Translate library/API calls       |
|  Warning             |  Consequences of changes           |
|  TODO                |  Temporary work markers            |
|  Javadoc / Docstring |  Public API documentation          |
|                                                           |
+-----------------------------------------------------------+
```

---

## Bad Comments

Far more common than good comments are bad comments. These clutter the code, mislead developers, and create maintenance burden. Here are the types to eliminate.

### Redundant Comments

A comment that says exactly what the code says is pure noise.

**BEFORE: Redundant comments**

Java:
```java
// The day of the month
private int dayOfMonth;

// Returns the day of the month
public int getDayOfMonth() {
    return dayOfMonth;
}

// Sets the day of the month
public void setDayOfMonth(int dayOfMonth) {
    this.dayOfMonth = dayOfMonth;
}

// The name
private String name;

// Default constructor
public Employee() {
}
```

**AFTER: No comments needed**

Java:
```java
private int dayOfMonth;
private String name;

public int getDayOfMonth() {
    return dayOfMonth;
}

public void setDayOfMonth(int dayOfMonth) {
    this.dayOfMonth = dayOfMonth;
}

public Employee() {
}
```

Every comment in the "before" version was pure noise. The code already communicated everything the comments said. Removing them makes the code cleaner and shorter.

Python:
```python
# BAD: Redundant
class Employee:
    def __init__(self):
        self.name = ""  # the name of the employee
        self.age = 0    # the age of the employee

# GOOD: Self-evident
class Employee:
    def __init__(self):
        self.name = ""
        self.age = 0
```

### Misleading Comments

Worse than redundant comments are comments that lie. They were accurate once but the code changed and nobody updated the comment.

Java:
```java
// Returns true if the user is active
public boolean isActive(User user) {
    // Code was later modified to also check subscription status
    return user.getStatus() == Status.ACTIVE
        && user.getSubscription() != null
        && !user.getSubscription().isExpired();
}
```

The comment says this checks if the user is active. But the code also checks subscription status. A developer reading only the comment would miss the subscription requirement.

### Journal Comments

Some developers maintain a changelog at the top of every file. This was useful before version control existed. Today it is pointless clutter -- that is what `git log` is for.

**BEFORE: Journal comments**

Java:
```java
/*
 * Changes (from 01-Oct-2023)
 * --------------------------
 * 01-Oct-2023 : Added calculateTotal method (Mike)
 * 15-Oct-2023 : Fixed tax calculation bug (Sarah)
 * 02-Nov-2023 : Added discount support (Mike)
 * 14-Nov-2023 : Refactored to use streams (Jane)
 * 03-Dec-2023 : Fixed null pointer in discount (Sarah)
 * 18-Dec-2023 : Added support for bulk pricing (Mike)
 * 05-Jan-2024 : Performance optimization (Jane)
 */
```

**AFTER: Use version control**

Delete the entire journal. Every single entry is already captured in your Git history with more detail (diffs, timestamps, branches, associated pull requests).

### Noise Comments

Comments that restate the obvious add nothing but visual noise.

Java:
```java
/** The name. */
private String name;

/** The version. */
private String version;

/** The info. */
private String info;

/** Default constructor. */
public MyClass() {
}

/** Returns the name. */
public String getName() {
    return name;
}
```

Python:
```python
def get_name(self):
    """Returns the name."""  # Adds nothing
    return self.name
```

These comments train developers to ignore comments entirely, which means they will also ignore the rare genuinely useful comment.

### Mandated Comments

Some organizations require Javadoc on every function and every variable. This creates a tsunami of useless comments.

Java:
```java
/**
 * @param title The title of the CD
 * @param author The author of the CD
 * @param tracks The number of tracks on the CD
 * @param duration The duration of the CD in minutes
 */
public void addCD(String title, String author,
                  int tracks, int duration) {
    // ...
}
```

Every `@param` tag merely restates the parameter name. This adds no value and creates a maintenance burden -- if you rename a parameter, you must also update the comment. Require documentation for public APIs, not for every function.

### Commented-Out Code

This is one of the worst offenses in any codebase.

**BEFORE: Commented-out code**

Java:
```java
public double calculateTotal(List<Item> items) {
    double total = 0;
    for (Item item : items) {
        total += item.getPrice();
        // total += item.getPrice() * item.getQuantity();
        // if (item.isOnSale()) {
        //     total -= item.getDiscount();
        // }
    }
    // applyBulkDiscount(total, items.size());
    // logCalculation(total);
    return total;
}
```

Python:
```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
        # total += item.price * item.quantity
        # if item.is_on_sale:
        #     total -= item.discount
    # apply_bulk_discount(total, len(items))
    # log_calculation(total)
    return total
```

Why is this so bad?

1. **Nobody will delete it.** Other developers see commented-out code and think "someone left this for a reason" and are afraid to remove it.
2. **It accumulates.** Over months, more and more commented-out code piles up.
3. **It is confusing.** Is the commented code the old way? A feature in progress? A debugging artifact?
4. **Version control already has it.** If you need the old code, use `git log` or `git show`.

**AFTER: Delete it**

Java:
```java
public double calculateTotal(List<Item> items) {
    double total = 0;
    for (Item item : items) {
        total += item.getPrice();
    }
    return total;
}
```

If you genuinely need the old code someday, Git has it. Delete the commented-out code without hesitation.

### Position Markers and Banners

Java:
```java
// ==================== GETTERS ====================

public String getName() { return name; }
public int getAge() { return age; }

// ==================== SETTERS ====================

public void setName(String name) { this.name = name; }
public void setAge(int age) { this.age = age; }

// ==================== BUSINESS LOGIC ==============
```

If you feel the need for section markers, your class is too large. Extract separate classes instead of organizing a monolith with banners.

### Closing Brace Comments

Java:
```java
if (condition) {
    while (running) {
        for (Item item : items) {
            if (item.isValid()) {
                // ... lots of code ...
            } // if item is valid
        } // for each item
    } // while running
} // if condition
```

If your nesting is so deep that you need comments on closing braces to keep track, your function is too long. Extract smaller functions instead.

### Attribution Comments

```java
// Added by Mike, March 2024
public void calculateDiscount() { ... }
```

This is what `git blame` is for. Attribution comments get outdated as code gets modified by other developers.

```
+-----------------------------------------------------------+
|                  Bad Comments Summary                     |
+-----------------------------------------------------------+
|                                                           |
|  Type              |  Why It Is Bad                       |
|  ------------------|--------------------------------------|
|  Redundant         |  Says what code already says         |
|  Misleading        |  Lies about what code does           |
|  Journal           |  Duplicates version control          |
|  Noise             |  States the obvious, trains ignoring |
|  Mandated          |  Creates maintenance burden          |
|  Commented-out     |  Clutters, confuses, never deleted   |
|  Position markers  |  Masks classes that are too large    |
|  Closing brace     |  Masks functions that are too long   |
|  Attribution       |  Duplicates git blame                |
|                                                           |
+-----------------------------------------------------------+
```

---

## Self-Documenting Code

The ultimate goal is code that documents itself. Every time you are tempted to write a comment, try these alternatives first.

### Replace Comments with Better Names

**BEFORE:**

Python:
```python
# Check if the user can access premium features
if user.plan == "premium" and user.is_active and not user.is_suspended:
    show_premium_features()
```

**AFTER:**

Python:
```python
if user.can_access_premium_features():
    show_premium_features()
```

### Replace Comments with Extracted Functions

**BEFORE:**

Java:
```java
// Calculate the price after applying the seasonal discount
// and the loyalty bonus, but cap the total discount at 30%
double discount = seasonalRate + loyaltyBonus;
if (discount > 0.30) {
    discount = 0.30;
}
double finalPrice = basePrice * (1 - discount);
```

**AFTER:**

Java:
```java
double finalPrice = calculateDiscountedPrice(basePrice,
    seasonalRate, loyaltyBonus);

private double calculateDiscountedPrice(double basePrice,
        double seasonalRate, double loyaltyBonus) {
    double totalDiscount = Math.min(
        seasonalRate + loyaltyBonus, MAX_DISCOUNT_RATE);
    return basePrice * (1 - totalDiscount);
}
```

### Replace Comments with Constants

**BEFORE:**

Python:
```python
# Timeout after 30 seconds
time.sleep(30)

# Maximum retry attempts
for i in range(3):
    pass
```

**AFTER:**

Python:
```python
CONNECTION_TIMEOUT_SECONDS = 30
MAX_RETRY_ATTEMPTS = 3

time.sleep(CONNECTION_TIMEOUT_SECONDS)

for attempt in range(MAX_RETRY_ATTEMPTS):
    pass
```

### Replace Comments with Better Structure

**BEFORE:**

Java:
```java
public void processApplication(Application app) {
    // Step 1: Validate
    if (app.getName() == null) { throw new Exception("Name required"); }
    if (app.getAge() < 18) { throw new Exception("Must be 18+"); }

    // Step 2: Calculate score
    int score = app.getGpa() * 10 + app.getTestScore();

    // Step 3: Determine result
    String result;
    if (score > 90) {
        result = "ACCEPTED";
    } else if (score > 70) {
        result = "WAITLISTED";
    } else {
        result = "REJECTED";
    }

    // Step 4: Save
    repository.save(app, result);

    // Step 5: Notify
    emailService.send(app.getEmail(), result);
}
```

**AFTER:**

Java:
```java
public void processApplication(Application app) {
    validateApplication(app);
    int score = calculateScore(app);
    AdmissionResult result = determineResult(score);
    repository.save(app, result);
    notifyApplicant(app, result);
}
```

The "step" comments disappeared because the extracted functions tell the same story.

```
+-----------------------------------------------------------+
|           Self-Documenting Code Strategies                |
+-----------------------------------------------------------+
|                                                           |
|  Instead of...         |  Try...                          |
|  ----------------------|--------------------------------- |
|  // Check if valid     |  if (isValid())                  |
|  // Max retries = 3    |  MAX_RETRIES = 3                 |
|  // Calculate discount |  calculateDiscount()             |
|  // User is admin      |  user.isAdmin()                  |
|  // Step 1, Step 2...  |  Extract methods                 |
|  // Complex condition  |  Extract to named boolean        |
|                                                           |
+-----------------------------------------------------------+
```

---

## A Complete Before/After Example

### BEFORE: Comment-Heavy Code

Python:
```python
class OrderProcessor:
    def process(self, order_data):
        # Validate the order data
        # Check that we have all required fields
        if "customer_id" not in order_data:
            raise ValueError("Missing customer ID")  # customer ID is required
        if "items" not in order_data or len(order_data["items"]) == 0:
            raise ValueError("No items")  # must have at least one item

        # Get customer from database
        # We use the customer repository to look up by ID
        customer = self.customer_repo.find(order_data["customer_id"])
        if customer is None:
            raise ValueError("Customer not found")  # invalid customer

        # Calculate the total
        total = 0  # running total
        for item in order_data["items"]:
            # Get the product price
            product = self.product_repo.find(item["product_id"])
            # Multiply price by quantity
            total += product.price * item["quantity"]

        # Apply discount if customer is preferred
        # Preferred customers get 10% off
        if customer.is_preferred:
            total = total * 0.9  # 10% discount

        # Add tax (8%)
        total = total * 1.08  # 8% tax rate

        # Save the order
        # order = Order(customer, total)
        # self.order_repo.save(order)
        order = Order(customer_id=customer.id, total=total,
                      items=order_data["items"])
        self.order_repo.save(order)

        # Send confirmation email
        # self.email_service.send_simple(customer.email, total)
        self.email_service.send_confirmation(customer.email, order)

        return order  # return the saved order
```

This code has redundant comments, commented-out code, and comments that simply restate what the code does.

### AFTER: Self-Documenting Code

Python:
```python
TAX_RATE = 0.08
PREFERRED_CUSTOMER_DISCOUNT = 0.10


class OrderProcessor:
    def process(self, order_data):
        self._validate(order_data)
        customer = self._find_customer(order_data["customer_id"])
        total = self._calculate_total(order_data["items"])
        total = self._apply_preferred_discount(total, customer)
        total = self._apply_tax(total)
        order = self._create_and_save_order(customer, total, order_data["items"])
        self.email_service.send_confirmation(customer.email, order)
        return order

    def _validate(self, order_data):
        if "customer_id" not in order_data:
            raise ValueError("Missing customer ID")
        if not order_data.get("items"):
            raise ValueError("Order must contain at least one item")

    def _find_customer(self, customer_id):
        customer = self.customer_repo.find(customer_id)
        if customer is None:
            raise CustomerNotFoundError(customer_id)
        return customer

    def _calculate_total(self, items):
        return sum(
            self.product_repo.find(item["product_id"]).price * item["quantity"]
            for item in items
        )

    def _apply_preferred_discount(self, total, customer):
        if customer.is_preferred:
            return total * (1 - PREFERRED_CUSTOMER_DISCOUNT)
        return total

    def _apply_tax(self, total):
        return total * (1 + TAX_RATE)

    def _create_and_save_order(self, customer, total, items):
        order = Order(customer_id=customer.id, total=total, items=items)
        self.order_repo.save(order)
        return order
```

The refactored version has zero comments but is far more readable. Every function name explains what happens. Constants replace magic numbers. Commented-out code is gone. The main `process()` method reads like a recipe.

---

## Common Mistakes

1. **Writing comments instead of improving the code** -- If you need a comment to explain code, the code should probably be rewritten to be clearer.

2. **Keeping commented-out code** -- Delete it. Git remembers everything. Other developers will be afraid to remove it, so it will live forever if you leave it.

3. **Writing journal comments at the top of files** -- Use version control. That is literally what it is for.

4. **Adding redundant Javadoc that restates parameter names** -- Only document public APIs, and add information beyond what the signature already tells you.

5. **Explaining "what" instead of "why"** -- Good comments explain why a decision was made, not what the code does. The code already shows what it does.

6. **Leaving TODO comments forever** -- TODOs are temporary. Set a deadline, tie them to a ticket, and review them regularly.

7. **Using comments to organize a function into sections** -- If a function needs section headers, it is too long. Extract functions instead.

---

## Best Practices

1. **Try to express yourself in code first** -- Before writing a comment, ask if you can rename a variable, extract a function, or introduce a constant to make the comment unnecessary.

2. **When you must comment, explain why, not what** -- The code shows what happens. A good comment explains the reasoning behind a non-obvious decision.

3. **Keep comments close to the code they describe** -- A comment that is five lines away from the code it explains might as well not exist.

4. **Delete commented-out code immediately** -- No exceptions. If it is important, it is in version control.

5. **Review and clean up TODOs regularly** -- Make TODO review part of your sprint process.

6. **Document public APIs thoroughly** -- This is the one place where more documentation is almost always better.

7. **Treat misleading comments as bugs** -- A comment that lies about the code is worse than no comment at all. When you find one, fix or delete it.

8. **Use constants instead of magic number comments** -- Replace `sleep(86400)  // seconds in a day` with `sleep(SECONDS_PER_DAY)`.

---

## Quick Summary

The best comment is the one you did not need to write because your code was clear enough on its own. Good comments explain *why* (not *what*), provide legal notices, warn about consequences, mark TODOs with accountability, and document public APIs. Bad comments restate the obvious, lie about the code, maintain change journals, add noise, and worst of all, leave commented-out code rotting in the codebase. Before writing a comment, always try to make the code itself more expressive through better names, extracted functions, and meaningful constants.

---

## Key Points

- Comments are a sign that the code failed to express itself. Always try code-level solutions first.
- Good comments explain why decisions were made, not what the code does.
- Legal comments, intent explanations, warnings, TODOs, and public API docs are the main categories of useful comments.
- Redundant comments that restate the code are pure noise and train developers to ignore all comments.
- Misleading comments are worse than no comments because they actively deceive.
- Journal comments belong in version control, not in source files.
- Commented-out code must be deleted immediately. Git remembers everything.
- Self-documenting code uses descriptive names, extracted functions, and named constants to eliminate the need for comments.
- Mandated comments on every function create a maintenance burden with no value.
- If your code needs section-header comments, your function is too long.

---

## Practice Questions

1. You find a function with 15 lines of code and 12 lines of comments. What does this ratio suggest, and what would you do about it?

2. A colleague argues that commenting every function is "good practice for documentation." How would you respond? What is the difference between documentation and noise?

3. You encounter this comment in a codebase: `// IMPORTANT: Do not remove this sleep(500) -- it prevents a race condition with the payment processor`. Is this a good or bad comment? Explain your reasoning.

4. Explain three strategies for making code self-documenting. For each strategy, give a before/after example.

5. Why are closing brace comments (like `} // end if` or `} // end for`) a code smell? What do they indicate about the function?

---

## Exercises

### Exercise 1: Comment Cleanup

Take this code and remove all bad comments while preserving any good ones. Refactor the code to be self-documenting where possible.

```python
# User class
class User:
    # Constructor
    def __init__(self, name, email, age):
        self.name = name      # the user's name
        self.email = email    # the user's email
        self.age = age        # the user's age
        self.active = True    # whether user is active

    # Check if the user is an adult (18 or older)
    def check(self):
        # Return true if age >= 18
        return self.age >= 18

    # Deactivate the user
    # Added by Mike on 2023-10-15
    # Modified by Sarah on 2023-11-02
    def deactivate(self):
        self.active = False   # set active to false
        # self.send_notification()
        # self.log_deactivation()
```

### Exercise 2: Self-Documenting Transformation

Rewrite this code so that all comments become unnecessary:

```java
public boolean validate(String input) {
    // Check if null or empty
    if (input == null || input.trim().isEmpty()) {
        return false;
    }
    // Must be between 3 and 50 characters
    if (input.length() < 3 || input.length() > 50) {
        return false;
    }
    // Must start with a letter
    if (!Character.isLetter(input.charAt(0))) {
        return false;
    }
    // Can only contain letters, numbers, and underscores
    if (!input.matches("[a-zA-Z0-9_]+")) {
        return false;
    }
    return true;
}
```

### Exercise 3: Comment Audit

Review one of your own source files. Categorize each comment as one of: legal, informative, intent, warning, TODO, redundant, misleading, noise, journal, or commented-out code. Delete the bad ones and refactor the code to make the redundant ones unnecessary.

---

## What Is Next?

You now know when comments help and when they hurt, and how to write code that speaks for itself. In Chapter 5, we turn to another aspect of code communication: formatting. Just as punctuation and paragraphs make prose readable, consistent formatting makes code scannable and maintainable. You will learn the newspaper metaphor, vertical and horizontal formatting rules, and how to use tools like Prettier, Black, and Checkstyle to enforce consistency automatically.
