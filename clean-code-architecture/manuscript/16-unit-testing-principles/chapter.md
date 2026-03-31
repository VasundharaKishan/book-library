# Chapter 16: Unit Testing Principles -- Building Your Safety Net

## What You Will Learn

- What a unit test is and what makes it different from other kinds of tests
- How to structure every test using the Arrange-Act-Assert (AAA) pattern
- The FIRST properties that separate great tests from fragile ones
- When and how to use test doubles: mocks, stubs, spies, and fakes
- What code coverage really tells you (and what it does not)
- How the testing pyramid guides your testing strategy

## Why This Chapter Matters

Code without tests is code you cannot confidently change. Every refactoring technique from Chapter 15 assumes you have a safety net that catches regressions instantly. Unit tests are the foundation of that safety net. They run in milliseconds, pinpoint exactly what broke, and serve as living documentation of how your code is supposed to behave. Writing good tests is a skill as important as writing good production code. Bad tests are worse than no tests -- they give false confidence and break every time you refactor.

---

## 16.1 What Is a Unit Test?

A unit test verifies the behavior of a small, isolated piece of code -- typically a single method or function -- in a controlled environment.

```
  +-------------------------------------------------------+
  |                  UNIT TEST PROPERTIES                  |
  +-------------------------------------------------------+
  |                                                        |
  |  Fast         Runs in milliseconds, not seconds        |
  |  Isolated     Tests one thing, no external deps        |
  |  Repeatable   Same result every time, any machine      |
  |  Self-checking  Pass/fail without human inspection     |
  |  Timely       Written close to the code it tests       |
  |                                                        |
  +-------------------------------------------------------+
```

### What a "Unit" Means

In Java, a unit is typically a single method of a class. In Python, it is typically a single function or method. The exact boundary is less important than the principle: **test one behavior at a time.**

---

## 16.2 The AAA Pattern (Arrange-Act-Assert)

Every well-structured test follows three phases:

```
  +-----------+     +-------+     +----------+
  |  ARRANGE  | --> |  ACT  | --> |  ASSERT  |
  +-----------+     +-------+     +----------+
  |  Set up    |    | Call   |    | Verify   |
  |  test data |    | the    |    | the      |
  |  and deps  |    | method |    | result   |
  +-----------+     +-------+     +----------+
```

### AAA in Java (JUnit 5)

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ShoppingCartTest {

    @Test
    void addItem_increasesTotalByItemPrice() {
        // Arrange
        ShoppingCart cart = new ShoppingCart();
        Product apple = new Product("Apple", 1.50);

        // Act
        cart.addItem(apple, 3);

        // Assert
        assertEquals(4.50, cart.getTotal(), 0.001);
    }

    @Test
    void addItem_incrementsItemCount() {
        // Arrange
        ShoppingCart cart = new ShoppingCart();
        Product apple = new Product("Apple", 1.50);

        // Act
        cart.addItem(apple, 3);

        // Assert
        assertEquals(3, cart.getItemCount());
    }

    @Test
    void removeItem_decreasesTotal() {
        // Arrange
        ShoppingCart cart = new ShoppingCart();
        Product apple = new Product("Apple", 1.50);
        cart.addItem(apple, 3);

        // Act
        cart.removeItem(apple, 1);

        // Assert
        assertEquals(3.00, cart.getTotal(), 0.001);
        assertEquals(2, cart.getItemCount());
    }
}
```

### AAA in Python (pytest)

```python
import pytest
from shopping_cart import ShoppingCart, Product


class TestShoppingCart:

    def test_add_item_increases_total(self):
        # Arrange
        cart = ShoppingCart()
        apple = Product("Apple", 1.50)

        # Act
        cart.add_item(apple, quantity=3)

        # Assert
        assert cart.total == pytest.approx(4.50)

    def test_add_item_increments_count(self):
        # Arrange
        cart = ShoppingCart()
        apple = Product("Apple", 1.50)

        # Act
        cart.add_item(apple, quantity=3)

        # Assert
        assert cart.item_count == 3

    def test_remove_item_decreases_total(self):
        # Arrange
        cart = ShoppingCart()
        apple = Product("Apple", 1.50)
        cart.add_item(apple, quantity=3)

        # Act
        cart.remove_item(apple, quantity=1)

        # Assert
        assert cart.total == pytest.approx(3.00)
        assert cart.item_count == 2
```

### Why AAA Works

- **Readability:** Anyone can see what is being tested at a glance
- **Consistency:** Every test has the same structure, reducing cognitive load
- **Debugging:** When a test fails, you immediately know whether the problem is in the setup, the action, or the expectation

---

## 16.3 Test One Thing

Each test should verify exactly one behavior. This does not mean one assertion -- it means one logical concept.

### BEFORE: Testing Too Many Things

```java
@Test
void testEverything() {
    Calculator calc = new Calculator();

    // Test addition
    assertEquals(5, calc.add(2, 3));

    // Test subtraction
    assertEquals(1, calc.subtract(3, 2));

    // Test division
    assertEquals(2.5, calc.divide(5, 2), 0.001);

    // Test division by zero
    assertThrows(ArithmeticException.class, () -> calc.divide(5, 0));
}
```

If `subtract` fails, you do not know whether `divide` also fails because the test stops at the first failure.

### AFTER: One Behavior Per Test

```java
@Test
void add_returnsSumOfTwoNumbers() {
    Calculator calc = new Calculator();
    assertEquals(5, calc.add(2, 3));
}

@Test
void subtract_returnsDifference() {
    Calculator calc = new Calculator();
    assertEquals(1, calc.subtract(3, 2));
}

@Test
void divide_returnsQuotient() {
    Calculator calc = new Calculator();
    assertEquals(2.5, calc.divide(5, 2), 0.001);
}

@Test
void divide_byZeroThrowsException() {
    Calculator calc = new Calculator();
    assertThrows(ArithmeticException.class, () -> calc.divide(5, 0));
}
```

### BEFORE: Testing Too Many Things (Python)

```python
def test_user_service():
    service = UserService()

    user = service.create("Alice", "alice@example.com")
    assert user.name == "Alice"

    found = service.find_by_email("alice@example.com")
    assert found.name == "Alice"

    service.deactivate(user.id)
    assert not service.is_active(user.id)
```

### AFTER: One Behavior Per Test (Python)

```python
def test_create_user_sets_name():
    service = UserService()
    user = service.create("Alice", "alice@example.com")
    assert user.name == "Alice"


def test_find_by_email_returns_matching_user():
    service = UserService()
    service.create("Alice", "alice@example.com")
    found = service.find_by_email("alice@example.com")
    assert found.name == "Alice"


def test_deactivate_makes_user_inactive():
    service = UserService()
    user = service.create("Alice", "alice@example.com")
    service.deactivate(user.id)
    assert not service.is_active(user.id)
```

### Test Naming Convention

Good test names describe the scenario and expected outcome:

```
  Method Under Test     Scenario              Expected Result
  +--------------+  +------------------+  +-------------------+
  | add          |  | twoPositiveNums  |  | returnsSum        |
  | divide       |  | byZero           |  | throwsException   |
  | applyDiscount|  | expiredCoupon    |  | returnsFullPrice  |
  +--------------+  +------------------+  +-------------------+
```

---

## 16.4 FIRST Properties of Good Tests

The FIRST acronym captures the essential properties of well-designed unit tests:

### F -- Fast

Tests must run in milliseconds. If your test suite takes minutes, developers stop running it. Fast tests enable the rapid feedback loop that makes TDD and refactoring possible.

```java
// SLOW: Hits a real database
@Test
void findUser_slow() {
    Database db = new Database("jdbc:mysql://localhost:3306/test");
    UserRepository repo = new UserRepository(db);
    User user = repo.findById(1);
    assertNotNull(user);
}

// FAST: Uses an in-memory substitute
@Test
void findUser_fast() {
    UserRepository repo = new UserRepository(new InMemoryDatabase());
    repo.save(new User(1, "Alice"));
    User user = repo.findById(1);
    assertEquals("Alice", user.getName());
}
```

### I -- Isolated (Independent)

Tests must not depend on each other. Each test sets up its own state, runs, and cleans up after itself. Running tests in any order must produce the same result.

```python
# BAD: Tests depend on shared state
shared_list = []

def test_add():
    shared_list.append("item")
    assert len(shared_list) == 1  # Fails if test_add runs twice

def test_remove():
    shared_list.pop()             # Fails if test_add did not run first
    assert len(shared_list) == 0


# GOOD: Each test creates its own state
def test_add():
    items = []
    items.append("item")
    assert len(items) == 1

def test_remove():
    items = ["item"]
    items.pop()
    assert len(items) == 0
```

### R -- Repeatable

Tests must produce the same result regardless of environment, time, or network state. Avoid dependencies on the current date, random numbers, or external services.

```java
// BAD: Depends on current time
@Test
void isExpired_today() {
    Coupon coupon = new Coupon("SAVE10", LocalDate.now().minusDays(1));
    assertTrue(coupon.isExpired());  // What if the clock changes?
}

// GOOD: Uses a fixed date
@Test
void isExpired_whenPastExpirationDate() {
    LocalDate fixedToday = LocalDate.of(2024, 6, 15);
    Coupon coupon = new Coupon("SAVE10", LocalDate.of(2024, 6, 14));
    assertTrue(coupon.isExpired(fixedToday));
}
```

### S -- Self-Validating

Tests must produce a clear pass or fail result. No manual inspection of log files or console output.

```python
# BAD: Requires manual inspection
def test_format_report():
    report = format_report(sample_data)
    print(report)  # Developer must read this and decide if it looks right

# GOOD: Automated assertion
def test_format_report_includes_header():
    report = format_report(sample_data)
    assert "Monthly Sales Report" in report

def test_format_report_includes_total():
    report = format_report(sample_data)
    assert "$1,234.56" in report
```

### T -- Timely

Write tests close in time to the production code they test. Ideally, write them before (TDD, Chapter 17) or immediately after.

---

## 16.5 Test Doubles: Mock, Stub, Spy, and Fake

When your code depends on external systems (databases, APIs, file systems), you replace those dependencies with test doubles to keep tests fast and isolated.

```
  +-------------------------------------------------------+
  |                  TEST DOUBLE TYPES                     |
  +-------------------------------------------------------+
  |                                                        |
  |  Stub    Returns canned answers to calls               |
  |  Mock    Verifies that specific calls were made        |
  |  Spy     Records calls for later verification          |
  |  Fake    Working implementation (simplified)           |
  |                                                        |
  +-------------------------------------------------------+
  |                                                        |
  |  Dummy   Passed around but never used                  |
  |                                                        |
  +-------------------------------------------------------+
```

### Stub: Providing Canned Answers

A stub returns predefined answers. It does not verify how it was called.

**Java (Mockito):**

```java
@Test
void getWeatherSummary_returnsFormattedString() {
    // Arrange: Create a stub that returns a fixed temperature
    WeatherService weatherStub = mock(WeatherService.class);
    when(weatherStub.getTemperature("NYC")).thenReturn(72.0);

    WeatherReporter reporter = new WeatherReporter(weatherStub);

    // Act
    String summary = reporter.getSummary("NYC");

    // Assert
    assertEquals("NYC: 72.0 F", summary);
}
```

**Python (unittest.mock):**

```python
from unittest.mock import Mock

def test_get_weather_summary():
    # Arrange: Create a stub
    weather_service = Mock()
    weather_service.get_temperature.return_value = 72.0

    reporter = WeatherReporter(weather_service)

    # Act
    summary = reporter.get_summary("NYC")

    # Assert
    assert summary == "NYC: 72.0 F"
```

### Mock: Verifying Interactions

A mock checks that specific methods were called with specific arguments.

**Java (Mockito):**

```java
@Test
void placeOrder_sendsConfirmationEmail() {
    // Arrange
    EmailService emailMock = mock(EmailService.class);
    OrderService orderService = new OrderService(emailMock);
    Order order = new Order("Alice", "alice@example.com", 99.99);

    // Act
    orderService.placeOrder(order);

    // Assert: Verify the email was sent
    verify(emailMock).sendEmail(
        eq("alice@example.com"),
        eq("Order Confirmation"),
        contains("99.99")
    );
}
```

**Python (unittest.mock):**

```python
from unittest.mock import Mock, call

def test_place_order_sends_confirmation_email():
    # Arrange
    email_service = Mock()
    order_service = OrderService(email_service)
    order = Order("Alice", "alice@example.com", 99.99)

    # Act
    order_service.place_order(order)

    # Assert
    email_service.send_email.assert_called_once_with(
        "alice@example.com",
        "Order Confirmation",
        "Your order total: $99.99"
    )
```

### Spy: Recording Calls

A spy wraps a real object and records calls to it, letting you verify interactions while using real behavior.

**Java (Mockito):**

```java
@Test
void addToCart_logsTheAction() {
    // Arrange
    Logger loggerSpy = spy(new ConsoleLogger());
    ShoppingCart cart = new ShoppingCart(loggerSpy);
    Product apple = new Product("Apple", 1.50);

    // Act
    cart.addItem(apple, 2);

    // Assert: Real logging happened, AND we can verify it
    verify(loggerSpy).log("Added 2x Apple to cart");
}
```

**Python:**

```python
from unittest.mock import patch

def test_add_to_cart_logs_action():
    cart = ShoppingCart()
    apple = Product("Apple", 1.50)

    with patch.object(cart, 'logger', wraps=cart.logger) as spy_logger:
        cart.add_item(apple, 2)
        spy_logger.log.assert_called_with("Added 2x Apple to cart")
```

### Fake: Simplified Implementation

A fake is a working implementation that takes shortcuts. An in-memory database is a common fake.

**Java:**

```java
public class InMemoryUserRepository implements UserRepository {
    private final Map<Integer, User> store = new HashMap<>();
    private int nextId = 1;

    @Override
    public User save(User user) {
        user.setId(nextId++);
        store.put(user.getId(), user);
        return user;
    }

    @Override
    public User findById(int id) {
        return store.get(id);
    }

    @Override
    public List<User> findAll() {
        return new ArrayList<>(store.values());
    }
}

// Usage in tests:
@Test
void saveAndRetrieveUser() {
    UserRepository repo = new InMemoryUserRepository();
    User saved = repo.save(new User("Alice"));
    User found = repo.findById(saved.getId());
    assertEquals("Alice", found.getName());
}
```

**Python:**

```python
class InMemoryUserRepository:
    def __init__(self):
        self._store = {}
        self._next_id = 1

    def save(self, user):
        user.id = self._next_id
        self._next_id += 1
        self._store[user.id] = user
        return user

    def find_by_id(self, user_id):
        return self._store.get(user_id)

    def find_all(self):
        return list(self._store.values())


# Usage in tests:
def test_save_and_retrieve_user():
    repo = InMemoryUserRepository()
    saved = repo.save(User("Alice"))
    found = repo.find_by_id(saved.id)
    assert found.name == "Alice"
```

### Choosing the Right Double

```
  +-----------------------------------------------------------+
  |  QUESTION                          | USE THIS              |
  +-----------------------------------------------------------+
  |  Need fixed return values?         | Stub                  |
  |  Need to verify a call was made?   | Mock                  |
  |  Need real behavior + recording?   | Spy                   |
  |  Need a working in-memory system?  | Fake                  |
  |  Need to fill a parameter?         | Dummy (null/empty)    |
  +-----------------------------------------------------------+
```

---

## 16.6 Code Coverage

Code coverage measures how much of your production code is executed by your tests. It is reported as a percentage.

### Types of Coverage

```
  +-----------------------------------------------------------+
  |  TYPE               | WHAT IT MEASURES                    |
  +-----------------------------------------------------------+
  |  Line coverage      | Lines executed / total lines         |
  |  Branch coverage    | Branches taken / total branches      |
  |  Method coverage    | Methods called / total methods       |
  |  Condition coverage | Boolean conditions evaluated         |
  +-----------------------------------------------------------+
```

### What Coverage Tells You

Coverage tells you what code your tests **execute**. It does NOT tell you:

- Whether the tests actually **verify** correct behavior
- Whether edge cases are covered
- Whether the design is good

### The Coverage Trap

```java
// This test achieves 100% line coverage of calculateDiscount():
@Test
void calculateDiscount_runsWithoutError() {
    Calculator calc = new Calculator();
    calc.calculateDiscount(100, "SAVE10");
    // No assertion! The test passes even if the result is wrong.
}
```

This test is worthless despite achieving 100% coverage. Always assert meaningful outcomes.

### Practical Coverage Guidelines

```
  +----------------------------------------------+
  |          COVERAGE SWEET SPOT                  |
  +----------------------------------------------+
  |                                               |
  |  0-30%    Dangerously low                     |
  |  30-60%   Many gaps, high risk                |
  |  60-80%   Reasonable for most projects        |
  |  80-90%   Strong coverage, good confidence    |
  |  90-100%  Diminishing returns past 90%        |
  |                                               |
  |  Target: 70-85% with meaningful assertions    |
  +----------------------------------------------+
```

### Coverage in Practice (Python with pytest-cov)

```bash
# Run tests with coverage report
pytest --cov=src --cov-report=term-missing

# Output example:
# Name                    Stmts   Miss  Cover   Missing
# -------------------------------------------------
# src/calculator.py          24      3    88%   42-44
# src/cart.py                 31      0   100%
# src/order.py               45     12    73%   23-34
# -------------------------------------------------
# TOTAL                     100     15    85%
```

### Coverage in Practice (Java with JaCoCo)

```xml
<!-- Maven pom.xml -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

---

## 16.7 The Testing Pyramid

The testing pyramid describes the ideal distribution of test types in a project:

```
           /\
          /  \
         / E2E\         Few, slow, expensive
        /------\
       /        \
      /Integration\     Some, moderate speed
     /--------------\
    /                \
   /    Unit Tests    \  Many, fast, cheap
  /____________________\
```

### Layer Breakdown

| Layer | Count | Speed | Cost to Write | What It Tests |
|-------|-------|-------|---------------|--------------|
| Unit | Many (hundreds) | Milliseconds | Low | Individual functions and methods |
| Integration | Some (dozens) | Seconds | Medium | Components working together |
| End-to-End | Few (handful) | Minutes | High | Full user workflows |

### Why the Pyramid Shape?

- **Unit tests** are fast and cheap. Write many of them. They catch most bugs.
- **Integration tests** verify that components work together (e.g., your code + the database). Write enough to cover critical paths.
- **End-to-end tests** verify the complete system from the user's perspective. Write few because they are slow, brittle, and expensive to maintain.

### Anti-Pattern: The Ice Cream Cone

```
  ____________________
  \                  /
   \    E2E Tests   /     Many slow E2E tests
    \--------------/
     \            /
      \Integration\       Some integration
       \----------/
        \        /
         \ Unit /           Few unit tests
          \    /
           \  /
            \/

  This is the ICE CREAM CONE anti-pattern.
  Tests are slow, brittle, and expensive.
```

Teams that rely mostly on E2E tests have slow feedback loops, flaky test suites, and developers who stop trusting their tests.

### Practical Example: Testing a User Registration Feature

```
  +---------------------------------------------------+
  |  E2E (1-2 tests)                                  |
  |    User fills form, clicks submit, sees success    |
  +---------------------------------------------------+
  |  Integration (3-5 tests)                           |
  |    UserService + Database: save and retrieve user   |
  |    UserService + EmailService: sends welcome email  |
  +---------------------------------------------------+
  |  Unit (10-20 tests)                                |
  |    Email validation logic                          |
  |    Password strength checker                       |
  |    Username uniqueness check (with fake repo)      |
  |    Welcome email template generation               |
  |    Input sanitization                              |
  +---------------------------------------------------+
```

---

## 16.8 Writing Your First Test Suite

Here is a complete example of a well-tested class in both Java and Python.

### The Production Code (Java)

```java
public class StringCalculator {

    public int add(String numbers) {
        if (numbers.isEmpty()) {
            return 0;
        }
        String delimiter = ",";
        String body = numbers;

        if (numbers.startsWith("//")) {
            int newlineIndex = numbers.indexOf("\n");
            delimiter = numbers.substring(2, newlineIndex);
            body = numbers.substring(newlineIndex + 1);
        }

        String[] parts = body.split(delimiter + "|\n");
        int sum = 0;
        for (String part : parts) {
            int value = Integer.parseInt(part.trim());
            if (value < 0) {
                throw new IllegalArgumentException("Negatives not allowed: " + value);
            }
            if (value <= 1000) {
                sum += value;
            }
        }
        return sum;
    }
}
```

### The Test Suite (Java)

```java
class StringCalculatorTest {

    private StringCalculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new StringCalculator();
    }

    @Test
    void add_emptyString_returnsZero() {
        assertEquals(0, calculator.add(""));
    }

    @Test
    void add_singleNumber_returnsThatNumber() {
        assertEquals(5, calculator.add("5"));
    }

    @Test
    void add_twoNumbers_returnsSum() {
        assertEquals(8, calculator.add("3,5"));
    }

    @Test
    void add_multipleNumbers_returnsSum() {
        assertEquals(15, calculator.add("1,2,3,4,5"));
    }

    @Test
    void add_newlineDelimiter_works() {
        assertEquals(6, calculator.add("1\n2,3"));
    }

    @Test
    void add_customDelimiter_works() {
        assertEquals(7, calculator.add("//;\n3;4"));
    }

    @Test
    void add_negativeNumber_throwsException() {
        IllegalArgumentException ex = assertThrows(
            IllegalArgumentException.class,
            () -> calculator.add("1,-2,3")
        );
        assertTrue(ex.getMessage().contains("-2"));
    }

    @Test
    void add_numbersAbove1000_ignored() {
        assertEquals(2, calculator.add("2,1001"));
    }
}
```

### The Production Code (Python)

```python
class StringCalculator:

    def add(self, numbers: str) -> int:
        if not numbers:
            return 0

        delimiter = ","
        body = numbers

        if numbers.startswith("//"):
            newline_index = numbers.index("\n")
            delimiter = numbers[2:newline_index]
            body = numbers[newline_index + 1:]

        import re
        parts = re.split(f"{re.escape(delimiter)}|\n", body)
        total = 0
        for part in parts:
            value = int(part.strip())
            if value < 0:
                raise ValueError(f"Negatives not allowed: {value}")
            if value <= 1000:
                total += value
        return total
```

### The Test Suite (Python)

```python
import pytest
from string_calculator import StringCalculator


@pytest.fixture
def calc():
    return StringCalculator()


def test_add_empty_string_returns_zero(calc):
    assert calc.add("") == 0


def test_add_single_number(calc):
    assert calc.add("5") == 5


def test_add_two_numbers(calc):
    assert calc.add("3,5") == 8


def test_add_multiple_numbers(calc):
    assert calc.add("1,2,3,4,5") == 15


def test_add_newline_delimiter(calc):
    assert calc.add("1\n2,3") == 6


def test_add_custom_delimiter(calc):
    assert calc.add("//;\n3;4") == 7


def test_add_negative_raises_error(calc):
    with pytest.raises(ValueError, match="-2"):
        calc.add("1,-2,3")


def test_add_ignores_numbers_above_1000(calc):
    assert calc.add("2,1001") == 2
```

---

## Common Mistakes

1. **Testing implementation, not behavior.** Do not test that a method calls a private helper. Test the observable outcome.
2. **Overusing mocks.** If every test is full of mocks, your design might have too many dependencies. Consider simplifying the design first.
3. **Fragile tests that break on refactoring.** If renaming a private method breaks tests, the tests are coupled to implementation details.
4. **Chasing 100% coverage.** The last 10% often tests getters, setters, and trivial code. The effort is better spent writing integration tests for critical paths.
5. **Ignoring test readability.** Tests are documentation. If a test is hard to read, it is hard to trust and hard to maintain.

---

## Best Practices

1. **Follow AAA consistently.** Arrange, Act, Assert -- with blank lines separating each section in longer tests.
2. **Use descriptive test names.** `test_divide_by_zero_raises_error` is infinitely better than `test3`.
3. **Keep tests independent.** Each test must create its own state. Never rely on test execution order.
4. **Prefer stubs over mocks when possible.** Stubs test outcomes. Mocks test interactions. Outcome-based tests are more resilient to refactoring.
5. **Run tests frequently.** After every change. Make it a habit, not a chore.

---

## Quick Summary

| Concept | Purpose |
|---------|---------|
| AAA Pattern | Structure every test into Arrange, Act, Assert |
| Test One Thing | Each test verifies a single behavior |
| FIRST Properties | Fast, Isolated, Repeatable, Self-validating, Timely |
| Stub | Returns canned answers |
| Mock | Verifies interactions |
| Spy | Records calls on a real object |
| Fake | Simplified working implementation |
| Code Coverage | Measures executed code, not correctness |
| Testing Pyramid | Many unit, some integration, few E2E |

---

## Key Points

- Unit tests are the foundation of your testing strategy. They are fast, focused, and cheap.
- The AAA pattern gives every test a consistent, readable structure.
- Test doubles let you isolate the code under test from external dependencies.
- Code coverage is a useful metric but a terrible goal. High coverage with no assertions is useless.
- The testing pyramid guides you toward a balanced, maintainable test suite.

---

## Practice Questions

1. What is the difference between a mock and a stub? In what situation would you choose one over the other?

2. A test suite achieves 95% code coverage but has no assertions -- every test just calls methods and discards the result. What is wrong with this suite? What does its coverage number actually mean?

3. Your test for a `sendEmail` method calls a real SMTP server. Which FIRST property does this violate? How would you fix it?

4. You have a method that generates a report with today's date in the header. How would you make this testable and repeatable?

5. Explain why the "ice cream cone" anti-pattern leads to slow development cycles. What happens when most tests are E2E tests?

---

## Exercises

### Exercise 1: Write a Test Suite

Write a complete test suite for this Python class using the AAA pattern and pytest:

```python
class PasswordValidator:
    def validate(self, password: str) -> list[str]:
        errors = []
        if len(password) < 8:
            errors.append("Must be at least 8 characters")
        if not any(c.isupper() for c in password):
            errors.append("Must contain an uppercase letter")
        if not any(c.isdigit() for c in password):
            errors.append("Must contain a digit")
        return errors
```

Write at least five tests covering valid passwords, each individual rule, and the combination of multiple failures.

### Exercise 2: Introduce a Test Double

Given this class, write tests using a stub for the `WeatherApi`:

```java
public class FarmingAdvisor {
    private WeatherApi weatherApi;

    public FarmingAdvisor(WeatherApi weatherApi) {
        this.weatherApi = weatherApi;
    }

    public String advise(String location) {
        double temp = weatherApi.getTemperature(location);
        double rain = weatherApi.getRainProbability(location);

        if (temp > 35) return "Too hot to plant.";
        if (temp < 5) return "Too cold to plant.";
        if (rain > 0.7) return "Delay planting, heavy rain expected.";
        return "Good conditions for planting.";
    }
}
```

### Exercise 3: Coverage Analysis

Run your tests from Exercise 1 with coverage enabled. Identify any uncovered lines. Add tests until you reach at least 90% branch coverage. Then explain: does 90% coverage mean the code is bug-free?

---

## What Is Next?

You now know how to write tests that verify your code works. But what if you wrote the tests first -- before writing any production code? That is the idea behind Test-Driven Development (TDD). Chapter 17 walks you through the Red-Green-Refactor cycle and shows you how writing tests first leads to cleaner, simpler designs.
