# Chapter 17: Test-Driven Development -- Writing Tests First

## What You Will Learn

- The Red-Green-Refactor cycle and why each step matters
- Why writing tests before production code leads to better design
- A complete TDD walkthrough building a calculator from scratch
- How to take the smallest possible steps in TDD
- When TDD helps the most and when it is overkill
- Common TDD mistakes and how to avoid them

## Why This Chapter Matters

Most developers learn to write code first and tests later -- if they write tests at all. Test-Driven Development flips this order. You write a failing test, then write just enough code to pass it, then clean up. This feels backward at first, but it produces code that is testable by design, contains no unnecessary complexity, and has complete test coverage from day one. TDD is not just a testing technique -- it is a design technique that happens to produce tests.

---

## 17.1 The Red-Green-Refactor Cycle

TDD follows a strict three-step cycle:

```
         +-------+
         |  RED  |  Write a test that FAILS
         +---+---+
             |
             v
        +--------+
        | GREEN  |  Write the SIMPLEST code to pass
        +---+----+
            |
            v
     +-----------+
     | REFACTOR  |  Clean up without changing behavior
     +-----+-----+
           |
           +-----------> Back to RED
```

### Step 1: RED -- Write a Failing Test

Write a test for the behavior you want. Run it. It must fail. If it passes, either your test is wrong or the behavior already exists.

**Why this matters:** A test that you never saw fail might be testing nothing. The red step proves the test can detect a problem.

### Step 2: GREEN -- Make It Pass

Write the absolute minimum production code to make the failing test pass. Do not worry about elegance. Do not handle edge cases you have not written tests for yet. Just make it green.

**Why this matters:** Writing only enough code to pass forces you to take small, safe steps and avoid speculative generality.

### Step 3: REFACTOR -- Clean Up

Now that the test passes, improve the code structure. Remove duplication, rename variables, extract methods. Run the tests after every change to make sure nothing breaks.

**Why this matters:** You now have a green safety net. Refactoring under green tests is safe and confident.

### The Discipline

```
  +------------------------------------------------------+
  |              TDD RULES OF THE GAME                    |
  +------------------------------------------------------+
  |                                                       |
  |  1. Do NOT write production code without a failing    |
  |     test that demands it.                             |
  |                                                       |
  |  2. Do NOT write more of a test than is sufficient    |
  |     to fail (including compile failures).             |
  |                                                       |
  |  3. Do NOT write more production code than is         |
  |     sufficient to pass the currently failing test.    |
  |                                                       |
  +------------------------------------------------------+
```

---

## 17.2 Why Test First?

### Tests First vs Tests After

```
  TESTS AFTER                        TESTS FIRST (TDD)
  +------------------+               +------------------+
  | Write all code   |               | Write ONE test   |
  +------------------+               +------------------+
  | "Now I should    |               | Write JUST ENOUGH|
  |  write tests..." |               | code to pass     |
  +------------------+               +------------------+
  | Tests feel like  |               | Refactor         |
  | a chore          |               +------------------+
  +------------------+               | Repeat           |
  | Skip edge cases  |               +------------------+
  +------------------+               | Tests feel like  |
  | Hard-to-test     |               | a design tool    |
  | design emerges   |               +------------------+
  +------------------+
```

### Benefits of TDD

1. **100% coverage by construction.** Every line of production code exists because a test demanded it.
2. **Simpler design.** You only write what is needed. YAGNI is built into the process.
3. **Immediate feedback.** You know within seconds if your change works.
4. **Confidence to refactor.** The test suite is always comprehensive because you never wrote code without a test.
5. **Living documentation.** The tests describe every behavior the system supports.

### The Design Benefit

When you write tests first, you are forced to think about how the code will be **used** before you think about how it will be **implemented**. This naturally leads to:

- Smaller, more focused methods
- Fewer dependencies (because dependencies make testing hard)
- Better interfaces (because you design the API from the caller's perspective)

---

## 17.3 TDD Walkthrough: Building a Calculator

Let us build a simple calculator using strict TDD. We will follow every Red-Green-Refactor cycle so you can see how the code evolves.

### Iteration 1: Addition of Two Numbers

**RED -- Write the failing test (Python):**

```python
# test_calculator.py
from calculator import Calculator


def test_add_two_numbers():
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5
```

Run: `pytest test_calculator.py` -- FAILS (no module named `calculator`).

**GREEN -- Write the minimum code:**

```python
# calculator.py
class Calculator:
    def add(self, a, b):
        return a + b
```

Run: `pytest test_calculator.py` -- PASSES.

**REFACTOR:** Nothing to clean up yet. Move on.

---

### Iteration 2: Subtraction

**RED:**

```python
def test_subtract_two_numbers():
    calc = Calculator()
    result = calc.subtract(10, 4)
    assert result == 6
```

Run: FAILS (`Calculator` has no method `subtract`).

**GREEN:**

```python
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
```

Run: PASSES.

**REFACTOR:** Still clean. Move on.

---

### Iteration 3: Multiplication

**RED:**

```python
def test_multiply_two_numbers():
    calc = Calculator()
    result = calc.multiply(3, 7)
    assert result == 21
```

**GREEN:**

```python
def multiply(self, a, b):
    return a * b
```

Run: PASSES. **REFACTOR:** Nothing needed.

---

### Iteration 4: Division

**RED:**

```python
def test_divide_two_numbers():
    calc = Calculator()
    result = calc.divide(10, 4)
    assert result == 2.5
```

**GREEN:**

```python
def divide(self, a, b):
    return a / b
```

Run: PASSES.

---

### Iteration 5: Division by Zero

**RED:**

```python
import pytest

def test_divide_by_zero_raises_error():
    calc = Calculator()
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(10, 0)
```

Run: FAILS (raises `ZeroDivisionError`, not `ValueError`).

**GREEN:**

```python
def divide(self, a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

Run: PASSES.

---

### Iteration 6: Chained Operations (Expression)

**RED:**

```python
def test_evaluate_simple_expression():
    calc = Calculator()
    # 2 + 3 * 4 should give 14 (multiply first, then add)
    result = calc.evaluate("2 + 3 * 4")
    assert result == 14
```

Run: FAILS (no `evaluate` method).

**GREEN -- Start simple:**

```python
def evaluate(self, expression):
    tokens = expression.split()
    # Handle single operations first
    if len(tokens) == 3:
        left = float(tokens[0])
        op = tokens[1]
        right = float(tokens[2])
        return self._apply_operator(op, left, right)

    # Handle operator precedence: find * or / first
    # Process multiplication and division first
    values = []
    operators = []
    i = 0
    while i < len(tokens):
        if i % 2 == 0:
            values.append(float(tokens[i]))
        else:
            operators.append(tokens[i])
        i += 1

    # First pass: handle * and /
    j = 0
    while j < len(operators):
        if operators[j] in ('*', '/'):
            result = self._apply_operator(operators[j], values[j], values[j + 1])
            values[j] = result
            values.pop(j + 1)
            operators.pop(j)
        else:
            j += 1

    # Second pass: handle + and -
    result = values[0]
    for j, op in enumerate(operators):
        result = self._apply_operator(op, result, values[j + 1])
    return result

def _apply_operator(self, op, left, right):
    if op == '+': return self.add(left, right)
    if op == '-': return self.subtract(left, right)
    if op == '*': return self.multiply(left, right)
    if op == '/': return self.divide(left, right)
    raise ValueError(f"Unknown operator: {op}")
```

Run: PASSES.

**REFACTOR:** The `evaluate` method is getting long. Extract methods:

```python
def evaluate(self, expression):
    values, operators = self._parse_expression(expression)
    values, operators = self._apply_high_precedence(values, operators)
    return self._apply_remaining(values, operators)

def _parse_expression(self, expression):
    tokens = expression.split()
    values = [float(tokens[i]) for i in range(0, len(tokens), 2)]
    operators = [tokens[i] for i in range(1, len(tokens), 2)]
    return values, operators

def _apply_high_precedence(self, values, operators):
    j = 0
    while j < len(operators):
        if operators[j] in ('*', '/'):
            result = self._apply_operator(operators[j], values[j], values[j + 1])
            values[j] = result
            values.pop(j + 1)
            operators.pop(j)
        else:
            j += 1
    return values, operators

def _apply_remaining(self, values, operators):
    result = values[0]
    for j, op in enumerate(operators):
        result = self._apply_operator(op, result, values[j + 1])
    return result
```

Run: All tests still PASS. The refactoring is safe.

---

### The Same Walkthrough in Java

Here is how the same TDD flow looks in Java with JUnit 5:

**RED:**

```java
class CalculatorTest {

    @Test
    void add_twoNumbers_returnsSum() {
        Calculator calc = new Calculator();
        assertEquals(5, calc.add(2, 3));
    }
}
```

**GREEN:**

```java
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
```

**Continue the cycle for each operation:**

```java
@Test
void subtract_twoNumbers_returnsDifference() {
    Calculator calc = new Calculator();
    assertEquals(6, calc.subtract(10, 4));
}

@Test
void multiply_twoNumbers_returnsProduct() {
    Calculator calc = new Calculator();
    assertEquals(21, calc.multiply(3, 7));
}

@Test
void divide_twoNumbers_returnsQuotient() {
    Calculator calc = new Calculator();
    assertEquals(2.5, calc.divide(10, 4), 0.001);
}

@Test
void divide_byZero_throwsException() {
    Calculator calc = new Calculator();
    assertThrows(IllegalArgumentException.class,
        () -> calc.divide(10, 0));
}
```

**Production code after all cycles:**

```java
public class Calculator {

    public int add(int a, int b) {
        return a + b;
    }

    public int subtract(int a, int b) {
        return a - b;
    }

    public int multiply(int a, int b) {
        return a * b;
    }

    public double divide(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("Cannot divide by zero");
        }
        return (double) a / b;
    }
}
```

---

## 17.4 The Transformation Priority Premise

Kent Beck and Robert C. Martin suggest taking the simplest possible transformations when going from Red to Green. The priority order (from simplest to most complex):

```
  +------------------------------------------------------+
  |         TRANSFORMATION PRIORITY (SIMPLEST FIRST)      |
  +------------------------------------------------------+
  |                                                       |
  |  1. {} -> nil           Return null/None              |
  |  2. nil -> constant     Return a hardcoded value      |
  |  3. constant -> variable  Use a parameter             |
  |  4. add computation    Add arithmetic                  |
  |  5. split flow         Add if/else                     |
  |  6. variable -> list   Use a collection               |
  |  7. list -> iteration  Add a loop                     |
  |  8. iteration -> recursion  Replace loop with recursion|
  |                                                       |
  +------------------------------------------------------+
```

### Example: FizzBuzz via Transformations

**Test 1: Returns "1" for 1**

```python
def test_fizzbuzz_1():
    assert fizzbuzz(1) == "1"
```

```python
def fizzbuzz(n):
    return "1"  # Transformation: nil -> constant
```

**Test 2: Returns "2" for 2**

```python
def test_fizzbuzz_2():
    assert fizzbuzz(2) == "2"
```

```python
def fizzbuzz(n):
    return str(n)  # Transformation: constant -> variable
```

**Test 3: Returns "Fizz" for 3**

```python
def test_fizzbuzz_3():
    assert fizzbuzz(3) == "Fizz"
```

```python
def fizzbuzz(n):
    if n % 3 == 0:  # Transformation: split flow
        return "Fizz"
    return str(n)
```

**Test 4: Returns "Buzz" for 5**

```python
def test_fizzbuzz_5():
    assert fizzbuzz(5) == "Buzz"
```

```python
def fizzbuzz(n):
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)
```

**Test 5: Returns "FizzBuzz" for 15**

```python
def test_fizzbuzz_15():
    assert fizzbuzz(15) == "FizzBuzz"
```

```python
def fizzbuzz(n):
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)
```

Each step added only the minimum code needed. The final solution emerged naturally.

---

## 17.5 When TDD Helps Most

TDD is most valuable when:

```
  +------------------------------------------------------+
  |           TDD SWEET SPOTS                            |
  +------------------------------------------------------+
  |                                                       |
  |  Business logic      Complex rules with many cases    |
  |  Algorithms          Clear inputs and outputs         |
  |  Data transformations Parse, convert, validate        |
  |  State machines       Well-defined transitions        |
  |  Bug fixes            Write a test that reproduces    |
  |                       the bug, then fix it            |
  |                                                       |
  +------------------------------------------------------+
```

### TDD for Bug Fixes

One of the most powerful uses of TDD: when you find a bug, write a test that fails because of the bug BEFORE you fix it. This guarantees:

1. You understand the bug (the test reproduces it)
2. Your fix actually works (the test passes)
3. The bug never comes back (the test stays in the suite)

```python
# Bug report: discount is applied twice for VIP customers

# Step 1: Write a test that exposes the bug
def test_vip_discount_applied_once():
    order = Order(customer_type="VIP", amount=100.00)
    total = order.calculate_total()
    # VIP discount is 10%, so total should be 90.00
    assert total == pytest.approx(90.00)  # FAILS: returns 81.00

# Step 2: Fix the bug
# Step 3: Test passes. Bug can never recur.
```

---

## 17.6 When TDD Is Overkill

TDD is not always the right approach:

```
  +------------------------------------------------------+
  |           WHEN TDD ADDS LITTLE VALUE                  |
  +------------------------------------------------------+
  |                                                       |
  |  Exploratory prototypes  You don't know what you're   |
  |                          building yet                 |
  |                                                       |
  |  UI layout code          Visual output is hard to     |
  |                          assert meaningfully          |
  |                                                       |
  |  Glue code               Simple delegation with no    |
  |                          logic                        |
  |                                                       |
  |  One-off scripts         Throwaway code not worth     |
  |                          investing in tests           |
  |                                                       |
  |  Framework boilerplate   Configuration, wiring, etc.  |
  |                                                       |
  +------------------------------------------------------+
```

### The Pragmatic Approach

You do not have to use TDD for everything. Many experienced developers use TDD for core business logic and algorithms, then write tests-after for simpler code. The important thing is that the code gets tested. TDD is a tool, not a religion.

```
  +------------------------------------------------------+
  |  Code Type              Recommended Approach          |
  +------------------------------------------------------+
  |  Business rules         TDD (test first)              |
  |  Algorithms             TDD (test first)              |
  |  Data access layer      Test after (integration)      |
  |  UI components          Test after (visual/snapshot)   |
  |  Configuration          Test after (smoke tests)       |
  |  Prototypes             No tests until design settles  |
  +------------------------------------------------------+
```

---

## 17.7 A Complete TDD Session: Building a Password Strength Checker

Let us walk through a realistic TDD session building a feature that a real application might need.

### Requirements

- Password must be at least 8 characters
- Must contain at least one uppercase letter
- Must contain at least one lowercase letter
- Must contain at least one digit
- Must contain at least one special character
- Return a strength rating: "weak", "fair", "strong"

### TDD Session (Java)

**Cycle 1: Empty password is weak**

```java
@Test
void emptyPassword_isWeak() {
    PasswordChecker checker = new PasswordChecker();
    assertEquals("weak", checker.checkStrength(""));
}
```

```java
public class PasswordChecker {
    public String checkStrength(String password) {
        return "weak";
    }
}
```

**Cycle 2: Short password is weak**

```java
@Test
void shortPassword_isWeak() {
    PasswordChecker checker = new PasswordChecker();
    assertEquals("weak", checker.checkStrength("Abc1!"));
}
```

Already passes (returns "weak" for everything). Move on.

**Cycle 3: Password meeting all criteria is strong**

```java
@Test
void passwordWithAllCriteria_isStrong() {
    PasswordChecker checker = new PasswordChecker();
    assertEquals("strong", checker.checkStrength("MyP@ss1word"));
}
```

FAILS. Now write the logic:

```java
public class PasswordChecker {
    public String checkStrength(String password) {
        int score = 0;
        if (password.length() >= 8) score++;
        if (password.matches(".*[A-Z].*")) score++;
        if (password.matches(".*[a-z].*")) score++;
        if (password.matches(".*[0-9].*")) score++;
        if (password.matches(".*[!@#$%^&*()_+\\-=].*")) score++;

        if (score >= 4) return "strong";
        return "weak";
    }
}
```

**Cycle 4: Password meeting some criteria is fair**

```java
@Test
void passwordMeetingSomeCriteria_isFair() {
    PasswordChecker checker = new PasswordChecker();
    assertEquals("fair", checker.checkStrength("Abcdefgh"));
}
```

FAILS (returns "weak" -- score is 3: length + upper + lower). Add "fair":

```java
if (score >= 4) return "strong";
if (score >= 3) return "fair";
return "weak";
```

**Cycle 5: Add more edge case tests**

```java
@Test
void onlyDigitsAndLength_isWeak() {
    PasswordChecker checker = new PasswordChecker();
    assertEquals("weak", checker.checkStrength("12345678"));
}

@Test
void allLowerWithDigit_isFair() {
    PasswordChecker checker = new PasswordChecker();
    assertEquals("fair", checker.checkStrength("password1"));
}
```

**REFACTOR: Extract criteria checks**

```java
public class PasswordChecker {

    public String checkStrength(String password) {
        int score = countPassingCriteria(password);
        if (score >= 4) return "strong";
        if (score >= 3) return "fair";
        return "weak";
    }

    private int countPassingCriteria(String password) {
        int score = 0;
        if (hasMinimumLength(password)) score++;
        if (hasUpperCase(password)) score++;
        if (hasLowerCase(password)) score++;
        if (hasDigit(password)) score++;
        if (hasSpecialChar(password)) score++;
        return score;
    }

    private boolean hasMinimumLength(String password) {
        return password.length() >= 8;
    }

    private boolean hasUpperCase(String password) {
        return password.matches(".*[A-Z].*");
    }

    private boolean hasLowerCase(String password) {
        return password.matches(".*[a-z].*");
    }

    private boolean hasDigit(String password) {
        return password.matches(".*[0-9].*");
    }

    private boolean hasSpecialChar(String password) {
        return password.matches(".*[!@#$%^&*()_+\\-=].*");
    }
}
```

All tests pass. The refactoring is complete. Notice how the final design emerged from the tests -- we did not plan the `countPassingCriteria` method up front.

---

## Common Mistakes

1. **Writing too many tests at once.** TDD works in single test increments. Writing five failing tests before any production code breaks the rhythm.
2. **Writing too much production code.** If your green step adds code not demanded by the failing test, you are guessing about future needs.
3. **Skipping the refactoring step.** Red-Green without Refactor leads to code that works but is messy. The refactoring step is not optional.
4. **Testing private methods directly.** Test behavior through public methods. Private methods are implementation details that should be free to change.
5. **Giving up too early.** TDD feels slow at first. The productivity gains come after you build the habit, typically after a few weeks of practice.

---

## Best Practices

1. **Start with the simplest possible test.** The first test should be almost trivially easy to pass.
2. **Take the smallest step that makes a test pass.** Resist the urge to write the full solution on the first green step.
3. **Run tests after every change.** After writing a test, after writing production code, after every refactoring step.
4. **Refactor both production code AND test code.** Tests deserve the same care as production code. Extract helpers, remove duplication.
5. **Use TDD for bug fixes.** Write a failing test that reproduces the bug, then fix it. This is one of TDD's highest-value applications.

---

## Quick Summary

| Concept | Description |
|---------|-------------|
| Red | Write a test that fails |
| Green | Write the minimum code to pass |
| Refactor | Clean up while tests stay green |
| Test First | Design the API before the implementation |
| Transformation Priority | Take the simplest possible step to go green |
| TDD Sweet Spots | Business logic, algorithms, bug fixes |
| TDD Overkill | Prototypes, UI layout, throwaway scripts |

---

## Key Points

- TDD is a design technique that produces tests, not a testing technique that produces design.
- The Red-Green-Refactor cycle ensures you never write untested code and never write unnecessary code.
- Writing the test first forces you to design the interface from the caller's perspective.
- Take the smallest possible steps. Each cycle should take minutes, not hours.
- TDD is most valuable for business logic and algorithms. Use judgment about when to apply it.

---

## Practice Questions

1. Explain why it is important to see the test FAIL before writing production code. What problem does this prevent?

2. You are writing a sorting algorithm using TDD. What would your first three tests be? (Hint: start with the simplest cases.)

3. A colleague writes a 50-line method in the GREEN step to pass a single test. What TDD principle did they violate, and what should they have done instead?

4. Your team argues that TDD is too slow because writing tests doubles the amount of code. How would you respond?

5. When is it appropriate to write tests AFTER the production code, even on a team that practices TDD?

---

## Exercises

### Exercise 1: TDD FizzBuzz in Java

Implement FizzBuzz using strict TDD in Java:
- `fizzbuzz(1)` returns `"1"`
- `fizzbuzz(3)` returns `"Fizz"`
- `fizzbuzz(5)` returns `"Buzz"`
- `fizzbuzz(15)` returns `"FizzBuzz"`

Write one test at a time. Commit after each Green phase. Show your commit history to prove you followed the cycle.

### Exercise 2: TDD Roman Numeral Converter

Using TDD in Python, build a function that converts integers to Roman numerals:
- `to_roman(1)` returns `"I"`
- `to_roman(4)` returns `"IV"`
- `to_roman(9)` returns `"IX"`
- `to_roman(2024)` returns `"MMXXIV"`

Start with the simplest case and work up. How many Red-Green-Refactor cycles did you need?

### Exercise 3: TDD Bug Fix

Given this buggy code:

```python
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)
```

There is a bug: it crashes on an empty list. Use TDD to fix it:
1. Write a test that fails because of the bug
2. Fix the bug (return 0 for an empty list)
3. Write additional tests for normal cases
4. Refactor if needed

---

## What Is Next?

You now understand TDD and unit testing. But tests and clean code exist within a larger structure -- the architecture of your application. Chapter 18: Clean Architecture Introduction explains how to organize your entire application so that business rules stay independent from frameworks, databases, and user interfaces.
