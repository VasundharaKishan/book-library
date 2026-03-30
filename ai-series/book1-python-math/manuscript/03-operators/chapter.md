# Chapter 3: Operators

## What You Will Learn

- How to do math with arithmetic operators (+, -, *, /, //, %, **)
- How to compare values with comparison operators (==, !=, >, <, >=, <=)
- How to combine conditions with logical operators (and, or, not)
- How to use assignment operators (=, +=, -=, *=)
- The order Python follows when evaluating expressions (operator precedence)
- How to use + and * with strings

## Why This Chapter Matters

Operators are the verbs of programming. Variables store data (nouns). Operators act on that data (verbs). Without operators, your data just sits there. With operators, you can calculate totals, compare scores, check conditions, and make decisions. Every AI algorithm uses operators constantly -- from simple addition to complex mathematical formulas.

---

## Arithmetic Operators

Arithmetic operators do math. You already know most of them from school.

### The Seven Arithmetic Operators

| Operator | Name | Example | Result |
|----------|------|---------|--------|
| `+` | Addition | `5 + 3` | `8` |
| `-` | Subtraction | `10 - 4` | `6` |
| `*` | Multiplication | `6 * 7` | `42` |
| `/` | Division | `15 / 4` | `3.75` |
| `//` | Floor Division | `15 // 4` | `3` |
| `%` | Modulo (Remainder) | `15 % 4` | `3` |
| `**` | Exponentiation (Power) | `2 ** 3` | `8` |

Let us explore each one.

### Addition (+) and Subtraction (-)

These work exactly like in math class.

```python
a = 10
b = 3

print(a + b)    # Output: 13
print(a - b)    # Output: 7
print(a + b - 2) # Output: 11
```

**Line-by-Line Explanation:**

- `a + b` adds 10 and 3, giving 13.
- `a - b` subtracts 3 from 10, giving 7.
- `a + b - 2` adds 10 and 3 first (13), then subtracts 2 (11). Python reads left to right for operators of the same level.

### Multiplication (*)

```python
price = 9.99
quantity = 3

total = price * quantity
print(f"Total: ${total:.2f}")    # Output: Total: $29.97
```

### Division (/)

Division always returns a float, even when dividing evenly.

```python
print(10 / 2)     # Output: 5.0  (not 5!)
print(15 / 4)     # Output: 3.75
print(7 / 3)      # Output: 2.3333333333333335
```

**Line-by-Line Explanation:**

- `10 / 2` gives `5.0`, not `5`. Regular division always produces a float in Python.
- `15 / 4` gives `3.75`. This is the exact decimal result.
- `7 / 3` gives a long decimal. Some divisions never end perfectly.

### Floor Division (//)

Floor division divides and then rounds DOWN to the nearest whole number.

```python
print(15 // 4)     # Output: 3
print(7 // 2)      # Output: 3
print(-7 // 2)     # Output: -4  (rounds DOWN, not toward zero!)
```

```
+----------------------------------------------+
|        DIVISION vs FLOOR DIVISION            |
+----------------------------------------------+
|                                              |
|   15 / 4  = 3.75   (regular division)        |
|   15 // 4 = 3      (floor: round DOWN)       |
|                                              |
|   Think of it like sharing cookies:          |
|                                              |
|   15 cookies shared among 4 friends          |
|   Each friend gets: 15 // 4 = 3 cookies      |
|   Cookies left over: 15 % 4 = 3 cookies      |
|                                              |
|   3 * 4 + 3 = 15   (it all adds up!)        |
|                                              |
+----------------------------------------------+
```

### Modulo / Remainder (%)

The modulo operator gives you the remainder after division.

```python
print(15 % 4)     # Output: 3  (15 / 4 = 3 remainder 3)
print(10 % 3)     # Output: 1  (10 / 3 = 3 remainder 1)
print(8 % 2)      # Output: 0  (8 / 2 = 4 remainder 0)
```

**When is modulo useful?**

**Checking if a number is even or odd:**

```python
number = 7

if number % 2 == 0:
    print(f"{number} is even")
else:
    print(f"{number} is odd")
```

**Expected Output:**

```
7 is odd
```

If a number divided by 2 has a remainder of 0, it is even. Otherwise, it is odd.

```
+----------------------------------------------+
|         MODULO: COMMON USES                  |
+----------------------------------------------+
|                                              |
|   Even/Odd:    number % 2 == 0  -> even      |
|   Divisible:   number % 5 == 0  -> by 5      |
|   Last digit:  1234 % 10 == 4                |
|   Clock math:  14 % 12 == 2  (2 PM)         |
|   Wrapping:    index % length                |
|                                              |
+----------------------------------------------+
```

### Exponentiation / Power (**)

The `**` operator raises a number to a power.

```python
print(2 ** 3)     # Output: 8    (2 * 2 * 2)
print(5 ** 2)     # Output: 25   (5 * 5)
print(10 ** 0)    # Output: 1    (anything to the power of 0 is 1)
print(9 ** 0.5)   # Output: 3.0  (square root!)
```

**Line-by-Line Explanation:**

- `2 ** 3` means 2 to the power of 3: 2 x 2 x 2 = 8.
- `5 ** 2` means 5 squared: 5 x 5 = 25.
- `10 ** 0` is 1. Any number to the power of 0 equals 1.
- `9 ** 0.5` is the square root of 9. Raising to the power of 0.5 gives the square root.

```
+----------------------------------------------+
|         EXPONENTIATION (**)                  |
+----------------------------------------------+
|                                              |
|   2 ** 3 = 2 x 2 x 2 = 8                    |
|                                              |
|   base ** exponent                           |
|                                              |
|   Think of it as repeated multiplication:    |
|                                              |
|   2 ** 1 = 2                                 |
|   2 ** 2 = 2 * 2 = 4                        |
|   2 ** 3 = 2 * 2 * 2 = 8                    |
|   2 ** 4 = 2 * 2 * 2 * 2 = 16               |
|                                              |
|   Special: 9 ** 0.5 = 3.0 (square root)     |
|                                              |
+----------------------------------------------+
```

---

## Comparison Operators

Comparison operators compare two values. They always return a boolean: `True` or `False`.

| Operator | Meaning | Example | Result |
|----------|---------|---------|--------|
| `==` | Equal to | `5 == 5` | `True` |
| `!=` | Not equal to | `5 != 3` | `True` |
| `>` | Greater than | `5 > 3` | `True` |
| `<` | Less than | `5 < 3` | `False` |
| `>=` | Greater than or equal | `5 >= 5` | `True` |
| `<=` | Less than or equal | `5 <= 3` | `False` |

```python
age = 20

print(age == 20)    # Output: True   (Is age equal to 20?)
print(age != 18)    # Output: True   (Is age NOT equal to 18?)
print(age > 18)     # Output: True   (Is age greater than 18?)
print(age < 21)     # Output: True   (Is age less than 21?)
print(age >= 20)    # Output: True   (Is age greater than or equal to 20?)
print(age <= 19)    # Output: False  (Is age less than or equal to 19?)
```

**Line-by-Line Explanation:**

- `age == 20` asks "Is age equal to 20?" Yes, so `True`.
- `age != 18` asks "Is age NOT equal to 18?" Yes (it is 20), so `True`.
- `age > 18` asks "Is age greater than 18?" Yes (20 > 18), so `True`.
- `age < 21` asks "Is age less than 21?" Yes (20 < 21), so `True`.
- `age >= 20` asks "Is age greater than or equal to 20?" Yes (20 equals 20), so `True`.
- `age <= 19` asks "Is age less than or equal to 19?" No (20 > 19), so `False`.

```
+----------------------------------------------+
|     == (EQUAL) vs = (ASSIGNMENT)             |
+----------------------------------------------+
|                                              |
|   =   means "put this value in the box"      |
|       age = 20  (assignment)                 |
|                                              |
|   ==  means "are these two things equal?"    |
|       age == 20  (comparison, returns bool)  |
|                                              |
|   This is the #1 beginner confusion!         |
|   One = assigns. Two == compares.            |
|                                              |
+----------------------------------------------+
```

### Comparing Strings

You can compare strings too. Python compares them alphabetically.

```python
print("apple" == "apple")     # Output: True
print("apple" == "Apple")     # Output: False  (case matters!)
print("apple" < "banana")     # Output: True   (a comes before b)
print("cat" > "car")          # Output: True   (t comes after r)
```

---

## Logical Operators

Logical operators combine multiple conditions. They work with boolean values.

| Operator | Meaning | Example | Result |
|----------|---------|---------|--------|
| `and` | Both must be True | `True and True` | `True` |
| `or` | At least one must be True | `True or False` | `True` |
| `not` | Reverses the value | `not True` | `False` |

### The `and` Operator

Both conditions must be `True` for the result to be `True`.

```python
age = 25
has_license = True

can_drive = age >= 16 and has_license
print(can_drive)    # Output: True
```

Think of `and` like two locks on a door. You need BOTH keys to open it.

```
+----------------------------------------------+
|           AND TRUTH TABLE                    |
+----------------------------------------------+
|                                              |
|   A       and    B      =  Result            |
|   -----   ---   -----      ------            |
|   True    and   True    =  True              |
|   True    and   False   =  False             |
|   False   and   True    =  False             |
|   False   and   False   =  False             |
|                                              |
|   Both must be True!                         |
|                                              |
+----------------------------------------------+
```

### The `or` Operator

At least one condition must be `True` for the result to be `True`.

```python
is_weekend = True
is_holiday = False

day_off = is_weekend or is_holiday
print(day_off)    # Output: True
```

Think of `or` like two doors into a room. You can enter through EITHER one.

```
+----------------------------------------------+
|            OR TRUTH TABLE                    |
+----------------------------------------------+
|                                              |
|   A       or     B      =  Result            |
|   -----   ---   -----      ------            |
|   True    or    True    =  True              |
|   True    or    False   =  True              |
|   False   or    True    =  True              |
|   False   or    False   =  False             |
|                                              |
|   At least one must be True!                 |
|                                              |
+----------------------------------------------+
```

### The `not` Operator

`not` flips the value. True becomes False. False becomes True.

```python
is_raining = False
go_outside = not is_raining
print(go_outside)    # Output: True
```

Think of `not` as the opposite switch. It reverses whatever it gets.

```
+----------------------------------------------+
|           NOT TRUTH TABLE                    |
+----------------------------------------------+
|                                              |
|   not True   =  False                        |
|   not False  =  True                         |
|                                              |
|   It flips the value!                        |
|                                              |
+----------------------------------------------+
```

### Combining Logical Operators

You can combine `and`, `or`, and `not` in a single expression.

```python
age = 25
income = 50000
has_good_credit = True

# Can get a loan if: age >= 21 AND (income > 40000 OR good credit)
can_get_loan = age >= 21 and (income > 40000 or has_good_credit)
print(can_get_loan)    # Output: True
```

**Line-by-Line Explanation:**

- `age >= 21` is `True` (25 >= 21).
- `income > 40000` is `True` (50000 > 40000).
- `income > 40000 or has_good_credit` is `True` (at least one is True).
- `True and True` is `True`.
- The parentheses control the order, just like in math.

---

## Assignment Operators

Assignment operators are shortcuts for updating a variable's value.

| Operator | Example | Equivalent To |
|----------|---------|---------------|
| `=` | `x = 5` | `x = 5` |
| `+=` | `x += 3` | `x = x + 3` |
| `-=` | `x -= 2` | `x = x - 2` |
| `*=` | `x *= 4` | `x = x * 4` |
| `/=` | `x /= 2` | `x = x / 2` |
| `//=` | `x //= 3` | `x = x // 3` |
| `%=` | `x %= 2` | `x = x % 2` |
| `**=` | `x **= 2` | `x = x ** 2` |

```python
score = 100
print(f"Start: {score}")      # Output: Start: 100

score += 10
print(f"After +10: {score}")   # Output: After +10: 110

score -= 5
print(f"After -5: {score}")    # Output: After -5: 105

score *= 2
print(f"After *2: {score}")    # Output: After *2: 210

score //= 3
print(f"After //3: {score}")   # Output: After //3: 70
```

**Line-by-Line Explanation:**

- `score += 10` means "take score (100), add 10, put the result back in score (110)."
- `score -= 5` means "take score (110), subtract 5, put the result back (105)."
- `score *= 2` means "take score (105), multiply by 2, put the result back (210)."
- `score //= 3` means "take score (210), floor divide by 3, put the result back (70)."

```
+----------------------------------------------+
|      ASSIGNMENT OPERATOR SHORTCUT            |
+----------------------------------------------+
|                                              |
|   score = 100                                |
|                                              |
|   Long way:       Short way:                 |
|   score = score + 10    score += 10          |
|   score = score - 5     score -= 5           |
|   score = score * 2     score *= 2           |
|                                              |
|   Both do the same thing.                    |
|   The short way is just easier to write.     |
|                                              |
+----------------------------------------------+
```

---

## Operator Precedence

When you write `2 + 3 * 4`, does Python calculate `(2 + 3) * 4 = 20` or `2 + (3 * 4) = 14`?

Python follows an order of operations, just like math class.

### The Order (Highest to Lowest Priority)

```
+----------------------------------------------+
|        OPERATOR PRECEDENCE                   |
|        (highest to lowest)                   |
+----------------------------------------------+
|                                              |
|   1. **          (exponentiation)            |
|   2. -, +        (unary: -x, +x)            |
|   3. *, /, //, % (multiply, divide)          |
|   4. +, -        (add, subtract)             |
|   5. ==, !=, >, <, >=, <=  (comparison)      |
|   6. not         (logical NOT)               |
|   7. and         (logical AND)               |
|   8. or          (logical OR)                |
|                                              |
|   Higher number = evaluated later            |
|   Use () to override the order               |
|                                              |
+----------------------------------------------+
```

### Examples

```python
# Multiplication before addition
result = 2 + 3 * 4
print(result)    # Output: 14  (not 20!)

# Exponentiation before multiplication
result = 2 * 3 ** 2
print(result)    # Output: 18  (3**2=9, then 2*9=18)

# Parentheses override everything
result = (2 + 3) * 4
print(result)    # Output: 20  (parentheses first!)
```

**Line-by-Line Explanation:**

- `2 + 3 * 4`: Multiplication has higher precedence than addition. Python calculates `3 * 4 = 12` first, then `2 + 12 = 14`.
- `2 * 3 ** 2`: Exponentiation has higher precedence than multiplication. Python calculates `3 ** 2 = 9` first, then `2 * 9 = 18`.
- `(2 + 3) * 4`: Parentheses override all precedence rules. Python calculates `2 + 3 = 5` first, then `5 * 4 = 20`.

> **Rule of thumb:** When in doubt, use parentheses. They make your code clearer and prevent surprises.

### A Realistic Example

```python
# Calculate the final price after tax and discount
price = 100
tax_rate = 0.08
discount = 15

# Without parentheses (WRONG result)
wrong = price + price * tax_rate - discount
print(f"Wrong: ${wrong}")    # Output: Wrong: $93.0

# With parentheses (CLEAR intent)
correct = (price * (1 + tax_rate)) - discount
print(f"Correct: ${correct}")  # Output: Correct: $93.0
```

In this case, the results happen to be the same. But parentheses make your intent obvious. Other programmers (and future-you) will thank you.

---

## String Concatenation and Repetition

The `+` and `*` operators work with strings too, but they do different things than with numbers.

### String Concatenation (+)

The `+` operator joins strings together.

```python
first_name = "Alice"
last_name = "Smith"

full_name = first_name + " " + last_name
print(full_name)    # Output: Alice Smith
```

**Line-by-Line Explanation:**

- `first_name + " " + last_name` joins three strings: "Alice", a space, and "Smith".
- The result is "Alice Smith".

### String Repetition (*)

The `*` operator repeats a string.

```python
line = "-" * 40
print(line)    # Output: ----------------------------------------

cheer = "Hip! " * 3
print(cheer)   # Output: Hip! Hip! Hip!
```

**Line-by-Line Explanation:**

- `"-" * 40` creates a string of 40 dashes.
- `"Hip! " * 3` repeats "Hip! " three times.

```
+----------------------------------------------+
|   + AND * WITH DIFFERENT TYPES               |
+----------------------------------------------+
|                                              |
|   With numbers:                              |
|   5 + 3   = 8        (addition)              |
|   5 * 3   = 15       (multiplication)        |
|                                              |
|   With strings:                              |
|   "Hi" + "!"  = "Hi!" (concatenation)        |
|   "Ha" * 3    = "HaHaHa" (repetition)        |
|                                              |
|   Cannot mix:                                |
|   "Hi" + 5    = ERROR!                       |
|   "Hi" + "5"  = "Hi5"  (both are strings)    |
|                                              |
+----------------------------------------------+
```

### You Cannot Mix Types with +

```python
# This causes an error
age = 25
message = "I am " + age + " years old"    # TypeError!

# Fix option 1: Convert to string
message = "I am " + str(age) + " years old"

# Fix option 2: Use f-string (recommended)
message = f"I am {age} years old"
```

---

## Putting It All Together

Here is a practical program that uses many operators:

```python
# grade_calculator.py - Calculate a student's final grade

# Input scores
homework = float(input("Homework average (0-100): "))
midterm = float(input("Midterm exam score (0-100): "))
final_exam = float(input("Final exam score (0-100): "))

# Calculate weighted grade
# Homework = 30%, Midterm = 30%, Final = 40%
weighted_grade = homework * 0.30 + midterm * 0.30 + final_exam * 0.40

# Determine if passing (>= 60)
is_passing = weighted_grade >= 60

# Display results
print()
print("=" * 40)
print("        GRADE REPORT")
print("=" * 40)
print(f"  Homework:    {homework}")
print(f"  Midterm:     {midterm}")
print(f"  Final Exam:  {final_exam}")
print("-" * 40)
print(f"  Final Grade: {weighted_grade:.1f}")
print(f"  Passing:     {is_passing}")
print("=" * 40)
```

**Expected Output:**

```
Homework average (0-100): 85
Midterm exam score (0-100): 78
Final exam score (0-100): 92

========================================
        GRADE REPORT
========================================
  Homework:    85.0
  Midterm:     78.0
  Final Exam:  92.0
----------------------------------------
  Final Grade: 85.7
  Passing:     True
========================================
```

**Line-by-Line Explanation:**

- `homework * 0.30` calculates 30% of the homework score.
- `midterm * 0.30` calculates 30% of the midterm.
- `final_exam * 0.40` calculates 40% of the final.
- Adding them gives the weighted grade: `85 * 0.30 + 78 * 0.30 + 92 * 0.40 = 25.5 + 23.4 + 36.8 = 85.7`.
- `weighted_grade >= 60` evaluates to `True` (85.7 >= 60).
- `"=" * 40` creates a visual separator line.
- `{weighted_grade:.1f}` formats to one decimal place.

---

## Common Mistakes

**Mistake 1: Confusing = and ==**

```python
# Wrong - this assigns, not compares
if x = 5:     # SyntaxError!
    print("yes")

# Right - use == to compare
if x == 5:
    print("yes")
```

**Mistake 2: Integer division surprise**

```python
# Might expect an integer, but / always returns float
result = 10 / 2
print(result)       # Output: 5.0 (float, not int!)
print(type(result)) # Output: <class 'float'>

# Use // if you want an integer result
result = 10 // 2
print(result)       # Output: 5 (integer)
```

**Mistake 3: Dividing by zero**

```python
# This crashes your program!
result = 10 / 0    # ZeroDivisionError!

# Always check first
denominator = 0
if denominator != 0:
    result = 10 / denominator
else:
    print("Cannot divide by zero!")
```

**Mistake 4: Forgetting operator precedence**

```python
# This does NOT calculate 20% of 150
discount = 150 + 150 * 0.20    # = 150 + 30 = 180 (wrong intent?)

# Use parentheses to be clear
total_with_extra = 150 * (1 + 0.20)    # = 150 * 1.20 = 180
discount_price = 150 * (1 - 0.20)      # = 150 * 0.80 = 120
```

**Mistake 5: Using + to combine a string and a number**

```python
# Wrong
print("Score: " + 95)     # TypeError!

# Right
print("Score: " + str(95))    # Convert to string
print(f"Score: {95}")          # Or use f-string
```

---

## Best Practices

1. **Use parentheses for clarity.** Even when not strictly needed, parentheses make your intent clear: `result = (a * b) + c`.

2. **Use meaningful variable names for intermediate results.** Instead of one giant expression, break it into steps:
   ```python
   # Hard to read
   final = (a * 0.3 + b * 0.3 + c * 0.4) * (1 - d / 100)

   # Easy to read
   weighted_score = a * 0.3 + b * 0.3 + c * 0.4
   penalty = d / 100
   final = weighted_score * (1 - penalty)
   ```

3. **Use augmented assignment operators.** Write `count += 1` instead of `count = count + 1`. It is shorter and clearer.

4. **Check for zero before dividing.** Division by zero crashes your program. Always verify the denominator is not zero.

5. **Use f-strings instead of string concatenation.** They are more readable and handle type conversion automatically.

---

## Quick Summary

Operators are the tools you use to work with data. Arithmetic operators do math (+, -, *, /, //, %, **). Comparison operators compare values and return True or False (==, !=, >, <, >=, <=). Logical operators combine conditions (and, or, not). Assignment operators update variables (=, +=, -=, *=). Python follows precedence rules (like PEMDAS in math), but you should use parentheses for clarity. The + operator concatenates strings, and * repeats them.

---

## Key Points to Remember

- `/` always returns a float. `//` returns an integer (floor division).
- `%` gives the remainder. Great for even/odd checks: `n % 2 == 0`.
- `**` raises to a power. `9 ** 0.5` gives the square root.
- `=` assigns a value. `==` compares values. Do not confuse them.
- `and` needs both sides True. `or` needs at least one True. `not` flips the value.
- `+=` is a shortcut for `x = x + value`. Same pattern for `-=`, `*=`, etc.
- Operator precedence: ** first, then * / // %, then + -, then comparisons, then not, then and, then or.
- Use parentheses when in doubt about precedence.
- `+` with strings concatenates them. `*` with a string repeats it.
- You cannot use `+` to combine a string and a number. Convert first or use f-strings.

---

## Practice Questions

**Question 1:** What is the output of this code?

```python
print(17 // 5)
print(17 % 5)
```

<details>
<summary>Answer</summary>

```
3
2
```

`17 // 5` is 3 (floor division: 17 divided by 5 is 3.4, rounded down to 3).
`17 % 5` is 2 (remainder: 17 = 5 * 3 + 2).

</details>

**Question 2:** What is the output?

```python
x = 5
x += 3
x *= 2
x -= 4
print(x)
```

<details>
<summary>Answer</summary>

`12`. Step by step: x starts at 5, becomes 8 (5+3), becomes 16 (8*2), becomes 12 (16-4).

</details>

**Question 3:** What does this expression evaluate to?

```python
result = 2 + 3 * 4 ** 2
```

<details>
<summary>Answer</summary>

`50`. Precedence: `4 ** 2 = 16` first, then `3 * 16 = 48`, then `2 + 48 = 50`.

</details>

**Question 4:** What is the output?

```python
print(True and False or True)
```

<details>
<summary>Answer</summary>

`True`. `and` is evaluated before `or`. So: `True and False` = `False`, then `False or True` = `True`.

</details>

**Question 5:** Why does this code produce an error?

```python
result = "The answer is " + 42
```

<details>
<summary>Answer</summary>

TypeError. You cannot concatenate a string and an integer with `+`. Fix it with: `"The answer is " + str(42)` or `f"The answer is {42}"`.

</details>

---

## Exercises

### Exercise 1: Bill Splitter

Write a program that takes a restaurant bill total and number of people, then calculates how much each person pays (including a 15% tip).

**Example:**

```
Enter the bill total: 85.50
How many people? 4
Each person pays: $24.58
```

**Solution:**

```python
# bill_splitter.py
bill = float(input("Enter the bill total: "))
people = int(input("How many people? "))

tip = bill * 0.15
total_with_tip = bill + tip
per_person = total_with_tip / people

print(f"Each person pays: ${per_person:.2f}")
```

### Exercise 2: Time Converter

Write a program that takes a number of seconds and converts it to hours, minutes, and remaining seconds. Use `//` and `%`.

**Example:**

```
Enter seconds: 3725
That is 1 hour(s), 2 minute(s), and 5 second(s)
```

**Hint:** There are 3600 seconds in an hour and 60 seconds in a minute.

**Solution:**

```python
# time_converter.py
total_seconds = int(input("Enter seconds: "))

hours = total_seconds // 3600
remaining = total_seconds % 3600
minutes = remaining // 60
seconds = remaining % 60

print(f"That is {hours} hour(s), {minutes} minute(s), and {seconds} second(s)")
```

### Exercise 3: BMI Calculator

Write a program that calculates Body Mass Index. The formula is: `BMI = weight_kg / (height_m ** 2)`. Print the BMI and whether it is in the "normal" range (18.5 to 24.9).

**Example:**

```
Enter weight in kg: 70
Enter height in meters: 1.75
Your BMI is 22.9
Normal range: True
```

**Solution:**

```python
# bmi_calculator.py
weight = float(input("Enter weight in kg: "))
height = float(input("Enter height in meters: "))

bmi = weight / (height ** 2)
is_normal = bmi >= 18.5 and bmi <= 24.9

print(f"Your BMI is {bmi:.1f}")
print(f"Normal range: {is_normal}")
```

---

## What Is Next?

You can now do math, compare values, and combine conditions. But your programs still run every line from top to bottom without making choices. In the next chapter, you will learn about **conditionals** -- the `if`, `elif`, and `else` statements that let your program make decisions. This is where your programs start to get truly smart.
