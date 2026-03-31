# Chapter 28: Technical Debt

## What You Will Learn

- What technical debt is and why the metaphor matters
- The difference between intentional and unintentional debt
- The four types of debt: code, architecture, test, and documentation
- Martin Fowler's Technical Debt Quadrant (reckless/prudent x
  deliberate/inadvertent)
- How to measure and track technical debt
- Strategies for paying it down: refactoring sprints, the boy scout rule, and
  the strangler fig pattern
- How to communicate debt to non-technical stakeholders
- When taking on debt is the right decision

## Why This Chapter Matters

Every software project accumulates shortcuts. A quick hack to meet a deadline.
A copy-paste instead of a proper abstraction. A test that was "going to be
written later." These shortcuts are not free. Like financial debt, they accrue
interest: every future change takes longer, bugs appear more frequently, and
new developers take longer to become productive.

The term "technical debt" was coined by Ward Cunningham specifically so that
developers could explain this phenomenon to business stakeholders in terms they
understand. If you cannot articulate why your team is slowing down, you will
never get the time to fix the underlying problems.

This chapter teaches you to recognize debt, measure it, communicate it, and
pay it down systematically -- without stopping feature development.

---

## Section 1: What Is Technical Debt?

Technical debt is the implied cost of future rework caused by choosing a quick
or easy solution now instead of a better approach that would take longer.

### The Financial Metaphor

```
+---------------------------------------------------------------+
|  Financial Debt vs Technical Debt                             |
+---------------------------------------------------------------+
|                                                               |
|  FINANCIAL DEBT              TECHNICAL DEBT                   |
|  --------------              ---------------                  |
|  Borrow money                Take a shortcut                  |
|  Get something now           Ship a feature faster            |
|  Pay interest over time      Spend extra time on every        |
|                              future change                    |
|  Pay down principal          Refactor the shortcut properly   |
|  Go bankrupt                 Project becomes unmaintainable   |
|                                                               |
|  KEY INSIGHT: Just like financial debt, technical debt         |
|  is not inherently bad. A mortgage lets you live in a         |
|  house while paying for it. A startup shipping an MVP         |
|  with shortcuts lets them validate the market before          |
|  investing in perfect code.                                   |
|                                                               |
|  The problem is UNMANAGED debt.                               |
+---------------------------------------------------------------+
```

### A Concrete Example

```java
// The "quick" solution (taking on debt)
public class OrderService {
    public void processOrder(Order order) {
        // TODO: Extract to separate validator class
        // TODO: Add proper validation rules
        if (order.getTotal() > 0 && order.getItems() != null) {
            // TODO: Handle multiple payment methods
            // Hardcoded to credit card for now
            chargeCreditCard(order);

            // TODO: Make this async
            // TODO: Support SMS notifications
            sendEmail(order.getCustomerEmail(), "Order confirmed");

            // Direct database call, no repository pattern
            // TODO: Add caching
            database.execute(
                "INSERT INTO orders VALUES ('" + order.getId() + "', " +
                "'" + order.getCustomerName() + "', " +
                order.getTotal() + ")"
            );
        }
    }
}
```

Every one of those TODO comments represents debt. Each one means that the
next developer who touches this code will have to work around limitations,
and each future feature (like adding PayPal support or SMS notifications)
will require untangling this mess first.

### The Interest Compounds

```
+---------------------------------------------------------------+
|  How Technical Debt Compounds Over Time                       |
+---------------------------------------------------------------+
|                                                               |
|  Velocity                                                     |
|  ^                                                            |
|  |  * * *                                                     |
|  |        * * *            <-- Without debt                   |
|  |              * * * * *                                     |
|  |                                                            |
|  |  * * *                                                     |
|  |        * *                                                 |
|  |           *  *          <-- With accumulating debt         |
|  |               *  *                                         |
|  |                   *                                        |
|  |                    * *                                     |
|  +---------------------------------------------> Time        |
|                                                               |
|  At first, shortcuts make you FASTER.                         |
|  Over time, they make you MUCH SLOWER.                        |
+---------------------------------------------------------------+
```

---

## Section 2: Intentional vs Unintentional Debt

Not all technical debt is created equal. Understanding the difference helps
you manage it.

### Intentional Debt (Deliberate)

You know you are taking a shortcut. You make a conscious decision to do so.

```python
# Intentional debt: hardcoded for launch, refactor in sprint 3
# TECH-DEBT: Ticket JIRA-1234 - Replace with configurable tax rates
TAX_RATE = 0.08  # Only works for California

class PriceCalculator:
    def calculate_total(self, subtotal: float) -> float:
        # TECH-DEBT: JIRA-1234 - Need tax lookup by state
        tax = subtotal * TAX_RATE
        return subtotal + tax
```

This is managed debt. You know it exists, you have a ticket for it, and you
plan to fix it.

### Unintentional Debt (Accidental)

You did not realize you were creating a problem. This happens when:
- You did not know a better approach existed
- Requirements changed and the design no longer fits
- The codebase grew beyond the original architecture's capacity

```java
// Unintentional debt: seemed fine for 10 products,
// breaks down at 10,000 products
public List<Product> searchProducts(String query) {
    List<Product> allProducts = productRepository.findAll();
    List<Product> results = new ArrayList<>();

    for (Product product : allProducts) {
        if (product.getName().toLowerCase()
                   .contains(query.toLowerCase())) {
            results.add(product);
        }
    }
    return results;
}
// Nobody realized this loads ALL products into memory.
// It worked fine with 50 products. Now there are 50,000.
```

---

## Section 3: The Technical Debt Quadrant

Martin Fowler's Technical Debt Quadrant classifies debt along two dimensions:
reckless vs prudent, and deliberate vs inadvertent.

```
+---------------------------------------------------------------+
|  Martin Fowler's Technical Debt Quadrant                      |
+---------------------------------------------------------------+
|                                                               |
|              DELIBERATE              INADVERTENT               |
|          (We know it's debt)    (We didn't realize)            |
|                                                               |
|  RECKLESS  "We don't have       "What's layered               |
|            time for design."     architecture?"                |
|                                                               |
|            - Skipping tests      - Junior dev doesn't          |
|              because deadline      know patterns               |
|            - Copy-pasting        - No code review              |
|              everywhere            caught it                   |
|            - No error handling   - Accidental coupling         |
|                                                               |
|  --------+----------------------+-------------------------    |
|                                                               |
|  PRUDENT   "We must ship now     "Now we know how we           |
|            and deal with the      should have done it."        |
|            consequences."                                      |
|                                                               |
|            - Hardcoded config    - Outgrew the original        |
|              for MVP launch        architecture                |
|            - Monolith before     - Learned better patterns     |
|              microservices         after shipping               |
|            - Manual deployment   - Requirements changed        |
|              for first release     the ideal design            |
|                                                               |
+---------------------------------------------------------------+
```

**Reckless-Deliberate** is the most dangerous: you know you are making a mess
and do not care. This leads to projects that become unmaintainable.

**Prudent-Deliberate** is often the best strategy: you make a conscious
trade-off, document it, and plan to fix it.

**Prudent-Inadvertent** is unavoidable: you only learn the right design after
you have built the wrong one. This is normal and expected.

**Reckless-Inadvertent** is prevented through learning, mentorship, and code
reviews.

---

## Section 4: Types of Technical Debt

### Code Debt

The most visible kind. Messy code, poor naming, duplicated logic, long methods,
god classes.

```java
// BEFORE: Code debt - duplicated validation logic
public class UserController {
    public Response createUser(UserRequest req) {
        if (req.getEmail() == null || req.getEmail().isEmpty()) {
            return Response.error("Email required");
        }
        if (!req.getEmail().contains("@")) {
            return Response.error("Invalid email");
        }
        if (req.getName() == null || req.getName().length() < 2) {
            return Response.error("Name must be at least 2 characters");
        }
        // ... create user
    }

    public Response updateUser(UserRequest req) {
        // SAME validation copied here
        if (req.getEmail() == null || req.getEmail().isEmpty()) {
            return Response.error("Email required");
        }
        if (!req.getEmail().contains("@")) {
            return Response.error("Invalid email");
        }
        if (req.getName() == null || req.getName().length() < 2) {
            return Response.error("Name must be at least 2 characters");
        }
        // ... update user
    }
}
```

```java
// AFTER: Debt paid off - extracted validation
public class UserValidator {
    public ValidationResult validate(UserRequest req) {
        List<String> errors = new ArrayList<>();

        if (req.getEmail() == null || req.getEmail().isEmpty()) {
            errors.add("Email is required");
        } else if (!req.getEmail().contains("@")) {
            errors.add("Email format is invalid");
        }

        if (req.getName() == null || req.getName().length() < 2) {
            errors.add("Name must be at least 2 characters");
        }

        return errors.isEmpty()
            ? ValidationResult.valid()
            : ValidationResult.invalid(errors);
    }
}
```

### Architecture Debt

The system's structure no longer fits its needs.

```
+---------------------------------------------------------------+
|  Architecture Debt Example                                    |
+---------------------------------------------------------------+
|                                                               |
|  What we built (Year 1):           What we need (Year 3):     |
|                                                               |
|  +------------------+              +--------+  +--------+     |
|  |   Monolith       |              | Orders |  | Users  |     |
|  |   - Orders       |              +--------+  +--------+     |
|  |   - Users        |              +--------+  +--------+     |
|  |   - Products     |     ==>      |Products|  |Payments|     |
|  |   - Payments     |              +--------+  +--------+     |
|  |   - Notifications|              +--------+                 |
|  +------------------+              | Notify |                 |
|                                    +--------+                 |
|  Works fine at 100 req/s           Need 10,000 req/s for      |
|                                    products, only 10 req/s    |
|                                    for user registration      |
+---------------------------------------------------------------+
```

### Test Debt

Missing tests, brittle tests, slow tests, or no tests at all.

```python
# Test debt: no tests for critical business logic
class DiscountCalculator:
    def calculate(self, order, customer):
        # 15 complex discount rules
        # No tests for any of them
        # Nobody dares change this code
        # Last person who tried broke checkout for 4 hours
        if customer.is_premium and order.total > 100:
            discount = order.total * 0.15
        elif customer.order_count > 10:
            discount = order.total * 0.10
        # ... 13 more rules ...
        return discount
```

### Documentation Debt

No README, no architecture decision records, no API documentation, tribal
knowledge that exists only in people's heads.

```
+---------------------------------------------------------------+
|  Documentation Debt Symptoms                                  |
+---------------------------------------------------------------+
|                                                               |
|  "Ask Sarah, she wrote that part."                            |
|  "I think this config does something important, don't touch." |
|  "The onboarding process takes 3 months."                     |
|  "Nobody knows why we have two user tables."                  |
|  "The deployment process is in a Slack thread from 2022."     |
|                                                               |
+---------------------------------------------------------------+
```

---

## Section 5: Measuring Technical Debt

You cannot manage what you cannot measure. Here are practical ways to quantify
debt.

### Code-Level Metrics

```python
# Python - Simple cyclomatic complexity checker concept
# Real tools: radon (Python), SonarQube (Java), CodeClimate

# These metrics indicate potential debt:
#
# 1. Cyclomatic Complexity
#    Low debt:  1-10 per method
#    Moderate:  11-20 per method
#    High debt: 21+ per method
#
# 2. Code Duplication
#    Low debt:  < 3% duplicate blocks
#    Moderate:  3-5%
#    High debt: > 5%
#
# 3. Method Length
#    Low debt:  < 20 lines
#    Moderate:  20-50 lines
#    High debt: > 50 lines
#
# 4. Test Coverage (for critical paths)
#    Low debt:  > 80%
#    Moderate:  50-80%
#    High debt: < 50%
```

### Team-Level Indicators

```
+---------------------------------------------------------------+
|  Signs Your Team Is Drowning in Debt                          |
+---------------------------------------------------------------+
|                                                               |
|  METRIC                          HEALTHY       DEBT-LADEN     |
|  ------                          -------       ----------     |
|  Time to onboard new dev         1-2 weeks     2-3 months     |
|  Bug fix time (average)          Hours         Days/weeks     |
|  Feature delivery estimate       Predictable   "It depends"   |
|  Ratio of bug fixes to features  20/80         60/40          |
|  Deployment frequency            Daily/weekly  Monthly+       |
|  Fear of changing code           Low           High           |
|  "Just don't touch that file"    Never said    Said weekly     |
|                                                               |
+---------------------------------------------------------------+
```

### Tracking Debt Formally

```java
// Java - Tag debt in code with annotations
@TechnicalDebt(
    description = "Tax calculation is hardcoded to US rates",
    type = DebtType.CODE,
    severity = Severity.MEDIUM,
    ticket = "JIRA-4567",
    createdDate = "2024-01-15",
    estimatedEffort = "3 days"
)
public BigDecimal calculateTax(BigDecimal amount, String country) {
    // Only handles US tax rates
    return amount.multiply(new BigDecimal("0.08"));
}
```

```python
# Python - Track debt with structured comments and a registry
# TECH-DEBT: [MEDIUM] [JIRA-4567] [3 days]
# Tax calculation is hardcoded to US rates.
# Need to support EU VAT and other tax jurisdictions.
def calculate_tax(amount: float, country: str) -> float:
    return amount * 0.08  # Only US rates
```

Keep a tech debt register (a spreadsheet or board is fine):

```
+---------------------------------------------------------------+
|  Technical Debt Register                                      |
+---------------------------------------------------------------+
|                                                               |
|  ID    | Area        | Severity | Effort | Impact  | Status   |
|  ------+-------------+----------+--------+---------+--------  |
|  TD-01 | Tax calc    | Medium   | 3 days | Orders  | Open     |
|  TD-02 | Search      | High     | 5 days | Perf    | Planned  |
|  TD-03 | Auth module | Critical | 2 wks  | Securty | In prog  |
|  TD-04 | No CI/CD    | High     | 1 week | Deploy  | Open     |
|  TD-05 | Tests: Cart | Medium   | 3 days | Quality | Open     |
|                                                               |
+---------------------------------------------------------------+
```

---

## Section 6: Paying Down Debt

### Strategy 1: The Boy Scout Rule

"Leave the code cleaner than you found it." -- Robert C. Martin

Every time you touch a file, make one small improvement. Rename a variable.
Extract a method. Add a missing test. Over time, the most-touched files get
steadily cleaner.

```python
# BEFORE: You are adding a new feature to this file
# and notice the poor naming
def proc(d):
    t = 0
    for i in d:
        if i['s'] == 'A':
            t += i['p'] * i['q']
    return t

# AFTER: You clean it up while you are here anyway
def calculate_active_order_total(orders):
    total = 0
    for order in orders:
        if order['status'] == 'ACTIVE':
            total += order['price'] * order['quantity']
    return total
```

This works because the files you touch most are the files that matter most.

### Strategy 2: Refactoring Sprints

Dedicate a percentage of each sprint to debt reduction. Common ratios:

```
+---------------------------------------------------------------+
|  Sprint Allocation Models                                     |
+---------------------------------------------------------------+
|                                                               |
|  80/20 Rule:  80% features, 20% debt reduction               |
|  (Most common, sustainable, easy to justify)                  |
|                                                               |
|  Debt Sprint: Every 4th sprint is 100% debt reduction         |
|  (Good for catching up, harder to justify to business)        |
|                                                               |
|  Continuous: Each ticket includes time for related cleanup    |
|  (Best long-term, but requires discipline)                    |
|                                                               |
+---------------------------------------------------------------+
```

### Strategy 3: Strangler Fig Pattern

Gradually replace the old system with new code instead of a risky "big bang"
rewrite.

```
+---------------------------------------------------------------+
|  Strangler Fig Pattern                                        |
+---------------------------------------------------------------+
|                                                               |
|  Phase 1: All traffic goes to old system                      |
|                                                               |
|  Request --> [Old Monolith]                                   |
|                                                               |
|  Phase 2: New feature routes to new service                   |
|                                                               |
|  Request --> [Router] --orders--> [Old Monolith]              |
|                      --search--> [New Search Service]         |
|                                                               |
|  Phase 3: More routes migrated                                |
|                                                               |
|  Request --> [Router] --orders--> [New Order Service]         |
|                      --search--> [New Search Service]         |
|                      --users---> [Old Monolith]               |
|                                                               |
|  Phase 4: Old system fully replaced                           |
|                                                               |
|  Request --> [Router] --orders--> [New Order Service]         |
|                      --search--> [New Search Service]         |
|                      --users---> [New User Service]           |
|                                                               |
|  Old monolith decommissioned.                                 |
+---------------------------------------------------------------+
```

```java
// Java - Strangler fig with a routing facade
public class OrderFacade {
    private final LegacyOrderService legacyService;
    private final NewOrderService newService;
    private final FeatureFlags featureFlags;

    public OrderResult processOrder(Order order) {
        if (featureFlags.isEnabled("new-order-processing")) {
            // New path: gradually migrate traffic
            return newService.processOrder(order);
        } else {
            // Old path: legacy system
            return legacyService.processOrder(order);
        }
    }
}
```

```python
# Python - Strangler fig with gradual migration
class OrderFacade:
    def __init__(self, legacy_service, new_service, feature_flags):
        self.legacy_service = legacy_service
        self.new_service = new_service
        self.feature_flags = feature_flags

    def process_order(self, order):
        if self.feature_flags.is_enabled("new-order-processing"):
            return self.new_service.process_order(order)
        else:
            return self.legacy_service.process_order(order)
```

---

## Section 7: Communicating Debt to Non-Technical Stakeholders

This is one of the most important skills a developer can have. Business people
do not understand (and should not need to understand) code quality. But they
understand money, risk, and speed.

### Language That Works

```
+---------------------------------------------------------------+
|  How to Translate Technical Debt for Business People           |
+---------------------------------------------------------------+
|                                                               |
|  DON'T SAY                    DO SAY                          |
|  ---------                    ------                          |
|  "The code is messy"          "New features take 3x longer    |
|                                than they should"              |
|                                                               |
|  "We need to refactor"        "We can cut development time    |
|                                by 40% with a 2-week           |
|                                investment"                     |
|                                                               |
|  "We have technical debt"     "We have a $200K/year hidden    |
|                                cost that's growing"           |
|                                                               |
|  "The architecture is wrong"  "We cannot scale past 1000      |
|                                users without changes"         |
|                                                               |
|  "We skipped tests"           "Each release has a 30% chance  |
|                                of a customer-facing bug"      |
|                                                               |
|  "We need to rewrite this"    "We're spending 60% of our time |
|                                working around limitations"    |
|                                                               |
+---------------------------------------------------------------+
```

### Quantify the Cost

Instead of saying "we have technical debt," calculate what it actually costs:

```
+---------------------------------------------------------------+
|  Debt Cost Calculation Example                                |
+---------------------------------------------------------------+
|                                                               |
|  Feature that should take:        3 developer-days            |
|  Feature actually takes:          9 developer-days            |
|  Overhead per feature:            6 developer-days            |
|                                                               |
|  Features delivered per quarter:  12                          |
|  Total overhead per quarter:      72 developer-days           |
|                                                               |
|  Average developer daily cost:    $600                        |
|  Quarterly cost of debt:          $43,200                     |
|  Annual cost of debt:             $172,800                    |
|                                                               |
|  Cost to fix (one-time):          $30,000 (2 devs, 5 weeks)  |
|  ROI payback period:              ~2 months                   |
|                                                               |
|  NOW the business understands.                                |
+---------------------------------------------------------------+
```

---

## Section 8: When Debt Is Acceptable

Technical debt is not always bad. Sometimes it is the right strategic choice.

### Good Reasons to Take On Debt

```
+---------------------------------------------------------------+
|  When Technical Debt Makes Sense                              |
+---------------------------------------------------------------+
|                                                               |
|  SCENARIO                    RATIONALE                        |
|  --------                    ---------                        |
|  MVP / prototype             Validate idea before investing   |
|                              in quality code                  |
|                                                               |
|  Competitive deadline        Missing a market window costs    |
|                              more than the debt interest      |
|                                                               |
|  Throwaway code              Proof of concept that will be    |
|                              rewritten regardless             |
|                                                               |
|  Learning / exploration      First version teaches you what   |
|                              the right design should be       |
|                                                               |
|  Emergency hotfix            Stop the bleeding first,         |
|                              proper fix in next sprint        |
|                                                               |
+---------------------------------------------------------------+
```

### Bad Reasons to Take On Debt

```
+---------------------------------------------------------------+
|  When Technical Debt Is Just Laziness                          |
+---------------------------------------------------------------+
|                                                               |
|  "We don't have time for tests"                               |
|  --> You don't have time NOT to write tests. Bugs cost more.  |
|                                                               |
|  "Nobody will ever change this code"                          |
|  --> They will. They always will.                             |
|                                                               |
|  "It works, so why clean it up?"                              |
|  --> It works TODAY. The next person who touches it will       |
|      spend hours understanding it.                            |
|                                                               |
|  "We'll fix it later"                                         |
|  --> Later never comes unless you put it on the backlog       |
|      with a priority and a date.                              |
|                                                               |
+---------------------------------------------------------------+
```

### The Golden Rule

If you take on debt deliberately, you must:
1. **Document it** (code comment + ticket in your tracker)
2. **Estimate the interest** (how much will it slow us down?)
3. **Set a pay-down date** (when will we fix it?)
4. **Get agreement** (the team agrees to the trade-off)

---

## Common Mistakes

1. **Ignoring debt until it is too late.** By the time the team can barely ship
   features, the cost to fix everything is enormous.

2. **Treating all debt as equal.** A hardcoded config value is not the same as a
   fundamental architecture problem. Prioritize by impact and cost.

3. **Trying to fix everything at once.** A "stop the world and rewrite"
   approach almost always fails. Pay debt incrementally.

4. **Not tracking debt.** If debt is not in your issue tracker, it does not
   exist in the eyes of planning. "I'll remember" is not a strategy.

5. **Using "technical debt" to mean "code I don't like."** Debt is about
   trade-offs that cost you in the future, not stylistic preferences.

6. **Never communicating debt to stakeholders.** If the business does not
   understand why things are slowing down, they will not allocate time to fix
   the root causes.

7. **Taking on reckless debt habitually.** Prudent, deliberate debt with a
   paydown plan is fine. "We don't have time for design" is not.

---

## Best Practices

1. **Make debt visible.** Track it in your issue tracker with clear labels,
   estimated effort, and business impact.

2. **Pay continuously.** Use the boy scout rule and allocate 15-20% of each
   sprint to debt reduction.

3. **Prioritize by interest rate.** Fix the debt that slows you down the most
   first, not the debt that annoys you the most.

4. **Communicate in business terms.** Translate technical problems into cost,
   risk, and speed.

5. **Use the strangler fig pattern for large debts.** Replace systems
   incrementally rather than attempting big-bang rewrites.

6. **Document deliberate debt.** Every intentional shortcut needs a comment, a
   ticket, and a planned resolution date.

7. **Prevent reckless debt through code reviews.** A good review process catches
   shortcuts before they become permanent.

8. **Celebrate debt reduction.** Make paying down debt as valued as shipping
   features.

---

## Quick Summary

Technical debt is the future cost of shortcuts taken today. Like financial
debt, it can be strategic (an MVP that validates a market) or reckless
(skipping tests because you cannot be bothered). The key is to make it
visible, track it, communicate it in business terms, and pay it down
continuously. Use the boy scout rule for small improvements, dedicated sprints
for medium debts, and the strangler fig pattern for large architectural debts.
Never let debt accumulate silently.

---

## Key Points

- **Technical debt = shortcuts now, interest payments later.** The longer debt
  remains unpaid, the more it costs.
- **Intentional debt is manageable.** Track it, estimate it, plan to fix it.
- **Unintentional debt is prevented** through learning, code reviews, and
  experience.
- **The debt quadrant** helps classify debt: reckless/prudent x
  deliberate/inadvertent.
- **Four types of debt:** code, architecture, test, and documentation.
- **Measure debt** using code metrics, team velocity trends, and cost
  calculations.
- **Communicate in business language:** cost, risk, speed -- not "the code is
  messy."
- **Pay debt continuously:** boy scout rule, 20% sprint allocation, strangler
  fig for large changes.

---

## Practice Questions

1. A product manager asks, "Why can't we just add the new payment method? It
   should only take a day." The real answer is that the payment module was
   hardcoded for credit cards three years ago and has accumulated significant
   debt. How do you explain this in business terms?

2. Your team inherits a codebase with no tests, inconsistent naming, and no
   documentation. Classify this debt using the Technical Debt Quadrant. What
   paydown strategy would you recommend?

3. A startup founder says, "We don't have time for clean code; we need to ship
   the MVP by next month." Is this a valid position? Under what conditions?
   What should they do after the MVP ships?

4. You calculate that technical debt is costing your team 60 developer-days per
   quarter. A complete refactoring would take 40 developer-days but would
   eliminate 80% of the overhead. Build the business case.

5. Compare the boy scout rule, refactoring sprints, and the strangler fig
   pattern. When is each strategy most appropriate?

---

## Exercises

### Exercise 1: Debt Audit

Take a project you are working on (or an open-source project you know) and
perform a technical debt audit:
1. Identify at least 5 instances of technical debt
2. Classify each one on the debt quadrant
3. Estimate the "interest rate" (how much time does it cost per month?)
4. Prioritize them by business impact
5. Propose a paydown plan

### Exercise 2: Communicate Debt to Stakeholders

Write a one-page summary for a non-technical product manager explaining:
- What technical debt the team has accumulated
- How much it is costing in developer time and quality
- What the proposed solution is
- What the ROI of fixing it would be

Use only business language. No code, no jargon.

### Exercise 3: Strangler Fig Implementation

Given this legacy function, implement a strangler fig migration:

```python
# Legacy function: does too much, hard to test, no error handling
def process_order(order_data):
    # Validates, calculates price, charges payment, sends email,
    # saves to database -- all in one giant function (200 lines)
    ...
```

1. Create an interface/facade that can route to old or new code
2. Extract the validation logic into a new, well-tested module
3. Keep the rest routing to the legacy code
4. Write tests that prove the new validation matches the old behavior

---

## What Is Next?

You now understand how to recognize, measure, and manage technical debt. In the
next chapter, we tackle one of the most powerful tools for preventing debt from
accumulating in the first place: **Code Review Culture**. You will learn how to
give and receive feedback effectively, what to look for in a review, and how to
build a team culture where reviews are valued, not dreaded.
