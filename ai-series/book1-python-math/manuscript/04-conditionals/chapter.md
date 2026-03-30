# Chapter 4: Conditionals

## What You Will Learn

- How to make decisions with `if` statements
- How to handle two paths with `if-else`
- How to handle multiple paths with `if-elif-else`
- How to nest conditions inside each other
- What truthy and falsy values are
- How to write one-line conditionals (ternary operator)
- How to combine conditions with `and` and `or`
- Common patterns: checking ranges, validating input

## Why This Chapter Matters

Until now, your programs run every line from top to bottom. They cannot make choices. But real programs need to decide things. Should the user see a "Welcome back" or a "Please register" message? Is the password correct? Did the student pass or fail? Conditionals give your program the ability to choose different paths based on data. Every AI system uses conditionals -- from simple rule-based chatbots to deciding which branch of a neural network to activate.

---

## The if Statement

The `if` statement checks a condition. If the condition is `True`, it runs the indented code below it. If the condition is `False`, it skips that code.

```python
age = 20

if age >= 18:
    print("You are an adult")
```

**Expected Output:**

```
You are an adult
```

**Line-by-Line Explanation:**

- `age = 20` stores the value 20 in the variable `age`.
- `if age >= 18:` checks whether `age` is greater than or equal to 18. It is (20 >= 18 is True), so Python enters the indented block.
- `print("You are an adult")` runs because the condition was True.
- Notice the colon `:` at the end of the `if` line. This is required.
- Notice the indentation (4 spaces) before `print`. This tells Python which code belongs to the `if` block.

```
+----------------------------------------------+
|           HOW if WORKS                       |
+----------------------------------------------+
|                                              |
|   if condition:                              |
|       do this                                |
|                                              |
|          condition                           |
|            / \                               |
|          /     \                             |
|       True    False                          |
|        |        |                            |
|    run block   skip block                    |
|        |        |                            |
|        +--------+                            |
|             |                                |
|        continue program                      |
|                                              |
+----------------------------------------------+
```

### What If the Condition Is False?

```python
age = 15

if age >= 18:
    print("You are an adult")

print("Program continues")
```

**Expected Output:**

```
Program continues
```

The `print("You are an adult")` line is skipped because `15 >= 18` is `False`. The program jumps to the next unindented line.

### Multiple Lines in an if Block

You can put multiple lines inside an `if` block. They all must be indented the same amount.

```python
temperature = 35

if temperature > 30:
    print("It is hot outside!")
    print("Drink plenty of water.")
    print("Stay in the shade.")
```

**Expected Output:**

```
It is hot outside!
Drink plenty of water.
Stay in the shade.
```

All three `print` lines run because they are all inside the `if` block (all indented by 4 spaces).

---

## The if-else Statement

Sometimes you want to do one thing if a condition is True, and a different thing if it is False. That is what `else` is for.

```python
age = 15

if age >= 18:
    print("You can vote")
else:
    print("You cannot vote yet")
```

**Expected Output:**

```
You cannot vote yet
```

**Line-by-Line Explanation:**

- `if age >= 18:` checks the condition. 15 >= 18 is `False`.
- Since the condition is False, Python skips the `if` block.
- `else:` catches everything that did not match the `if` condition.
- `print("You cannot vote yet")` runs because we are in the `else` block.

```
+----------------------------------------------+
|          HOW if-else WORKS                   |
+----------------------------------------------+
|                                              |
|   if condition:                              |
|       path A                                 |
|   else:                                      |
|       path B                                 |
|                                              |
|          condition                           |
|            / \                               |
|          /     \                             |
|       True    False                          |
|        |        |                            |
|     path A   path B                          |
|        |        |                            |
|        +--------+                            |
|             |                                |
|        continue program                      |
|                                              |
|   ONE path always runs. Never both.          |
|                                              |
+----------------------------------------------+
```

Think of `if-else` like a fork in the road. You MUST take one path. You cannot take both. You cannot take neither.

---

## The if-elif-else Statement

What if you have more than two choices? Use `elif` (short for "else if") to add more conditions.

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Your grade is {grade}")
```

**Expected Output:**

```
Your grade is B
```

**Line-by-Line Explanation:**

- `if score >= 90:` checks if score is 90 or above. 85 >= 90 is `False`. Skip.
- `elif score >= 80:` checks if score is 80 or above. 85 >= 80 is `True`. Run this block.
- `grade = "B"` sets the grade.
- Python skips all remaining `elif` and `else` blocks. Once a match is found, the rest are ignored.

```
+----------------------------------------------+
|      HOW if-elif-else WORKS                  |
+----------------------------------------------+
|                                              |
|   score = 85                                 |
|                                              |
|   score >= 90?  --NO-->  score >= 80?        |
|       |                      |               |
|      YES                    YES              |
|       |                      |               |
|    grade = "A"           grade = "B" (DONE!) |
|                                              |
|   Python checks top to bottom.               |
|   First True match wins.                     |
|   Everything after is skipped.               |
|                                              |
+----------------------------------------------+
```

### Important: Order Matters

Python checks conditions from top to bottom. The first one that is `True` wins. This means you should put the most specific conditions first.

```python
score = 95

# WRONG ORDER - every score >= 60 matches the first condition!
if score >= 60:
    grade = "D"    # 95 >= 60 is True, so this runs!
elif score >= 70:
    grade = "C"    # Never reached for 95
elif score >= 80:
    grade = "B"    # Never reached
elif score >= 90:
    grade = "A"    # Never reached!

print(f"Grade: {grade}")    # Output: Grade: D  (WRONG!)
```

```python
# RIGHT ORDER - most restrictive first
if score >= 90:
    grade = "A"    # 95 >= 90 is True, correct!
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Grade: {grade}")    # Output: Grade: A  (CORRECT!)
```

---

## Nested if Statements

You can put an `if` statement inside another `if` statement. This is called nesting.

```python
age = 20
has_ticket = True

if age >= 18:
    if has_ticket:
        print("Welcome to the movie!")
    else:
        print("You need a ticket.")
else:
    print("You must be 18 or older.")
```

**Expected Output:**

```
Welcome to the movie!
```

**Line-by-Line Explanation:**

- First `if`: checks age. 20 >= 18 is True. Enter the block.
- Second `if` (nested): checks ticket. `has_ticket` is True. Enter this block.
- `print("Welcome to the movie!")` runs.

```
+----------------------------------------------+
|           NESTED if FLOW                     |
+----------------------------------------------+
|                                              |
|           age >= 18?                         |
|            /     \                           |
|          Yes      No                         |
|           |        |                         |
|     has_ticket?  "Must be 18+"               |
|       /    \                                 |
|     Yes    No                                |
|      |      |                                |
|  "Welcome" "Need ticket"                     |
|                                              |
+----------------------------------------------+
```

### When to Use Nesting vs Combined Conditions

You can often replace nested `if` statements with `and`:

```python
# Nested version
if age >= 18:
    if has_ticket:
        print("Welcome!")

# Combined version (same result, cleaner)
if age >= 18 and has_ticket:
    print("Welcome!")
```

Use nesting when different `else` blocks need different messages. Use `and` when you only care about the combined result.

---

## Truthy and Falsy Values

In Python, every value can be treated as `True` or `False` in a condition. This goes beyond just the boolean values `True` and `False`.

### Falsy Values (Treated as False)

These values are considered `False` in a condition:

```python
# All of these are "falsy"
if 0:           print("won't print")    # 0 is falsy
if 0.0:         print("won't print")    # 0.0 is falsy
if "":          print("won't print")    # empty string is falsy
if None:        print("won't print")    # None is falsy
if False:       print("won't print")    # False is falsy
if []:          print("won't print")    # empty list is falsy
```

### Truthy Values (Treated as True)

Everything else is considered `True`:

```python
# All of these are "truthy"
if 1:           print("prints!")    # non-zero number
if -5:          print("prints!")    # any non-zero number
if 3.14:        print("prints!")    # non-zero float
if "hello":     print("prints!")    # non-empty string
if True:        print("prints!")    # True itself
if [1, 2]:      print("prints!")    # non-empty list
```

```
+----------------------------------------------+
|       TRUTHY vs FALSY                        |
+----------------------------------------------+
|                                              |
|   FALSY (treated as False):                  |
|   - False                                    |
|   - 0 and 0.0                                |
|   - "" (empty string)                        |
|   - None                                     |
|   - [] (empty list)                          |
|                                              |
|   TRUTHY (treated as True):                  |
|   - Everything else!                         |
|   - Any non-zero number                      |
|   - Any non-empty string                     |
|   - True                                     |
|   - Any non-empty list                       |
|                                              |
|   Memory trick: "empty" or "zero" = False    |
|                                              |
+----------------------------------------------+
```

### Practical Use: Checking for Empty Strings

```python
name = input("Enter your name: ")

# Long way
if name != "":
    print(f"Hello, {name}!")

# Short way (using truthy/falsy)
if name:
    print(f"Hello, {name}!")
```

Both versions do the same thing. The short way works because an empty string `""` is falsy, and any non-empty string is truthy.

---

## The Ternary Operator (One-Line if-else)

Python lets you write a simple `if-else` in a single line.

**Regular way:**

```python
age = 20

if age >= 18:
    status = "adult"
else:
    status = "minor"
```

**Ternary way:**

```python
age = 20
status = "adult" if age >= 18 else "minor"
print(status)    # Output: adult
```

**Line-by-Line Explanation:**

- `"adult" if age >= 18 else "minor"` reads like English: "adult if age is 18 or more, otherwise minor."
- The value before `if` is used when the condition is True.
- The value after `else` is used when the condition is False.

```
+----------------------------------------------+
|        TERNARY OPERATOR                      |
+----------------------------------------------+
|                                              |
|   value_if_true  if  condition  else  value_if_false
|                                              |
|   Example:                                   |
|   "adult"  if  age >= 18  else  "minor"      |
|      |              |              |         |
|   result when    the test      result when   |
|   True                         False         |
|                                              |
+----------------------------------------------+
```

### When to Use the Ternary Operator

Use it for simple assignments. Do NOT use it for complex logic.

```python
# Good - simple and clear
label = "even" if x % 2 == 0 else "odd"
greeting = f"Good {'morning' if hour < 12 else 'afternoon'}"

# Bad - too complex, hard to read
result = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "F"
```

---

## Combining Conditions

You can combine multiple conditions in a single `if` statement using `and`, `or`, and `not`.

### Using `and`

Both conditions must be True.

```python
age = 25
income = 50000

if age >= 21 and income >= 30000:
    print("Loan approved")
else:
    print("Loan denied")
```

**Expected Output:**

```
Loan approved
```

### Using `or`

At least one condition must be True.

```python
day = "Saturday"

if day == "Saturday" or day == "Sunday":
    print("It is the weekend!")
else:
    print("It is a weekday.")
```

**Expected Output:**

```
It is the weekend!
```

### Using `not`

Reverses the condition.

```python
is_logged_in = False

if not is_logged_in:
    print("Please log in first")
```

**Expected Output:**

```
Please log in first
```

### Complex Combinations

```python
age = 30
is_member = True
has_coupon = False

# Member discount OR coupon discount, AND must be 18+
if age >= 18 and (is_member or has_coupon):
    print("You get a discount!")
else:
    print("No discount available")
```

**Expected Output:**

```
You get a discount!
```

**Line-by-Line Explanation:**

- `age >= 18` is `True` (30 >= 18).
- `is_member or has_coupon` is `True` (True or False = True).
- `True and True` is `True`.
- The parentheses ensure that `or` is evaluated before `and`.

---

## Common Patterns

### Pattern 1: Checking if a Value Is in a Range

```python
temperature = 72

# Long way
if temperature >= 60 and temperature <= 80:
    print("Nice weather!")

# Pythonic way (chained comparison)
if 60 <= temperature <= 80:
    print("Nice weather!")
```

Both produce the same result. Python allows chained comparisons, which read more naturally.

```
+----------------------------------------------+
|     CHAINED COMPARISONS                      |
+----------------------------------------------+
|                                              |
|   60 <= temperature <= 80                    |
|                                              |
|   This means:                                |
|   temperature >= 60 AND temperature <= 80    |
|                                              |
|   It is a Python shortcut.                   |
|   Other languages cannot do this!            |
|                                              |
|   0  10  20  30  40  50  60  70  80  90  100 |
|   |---|---|---|---|---|---|===|===|---|---|    |
|                           ^^^^^^^^^^^        |
|                           valid range        |
|                                              |
+----------------------------------------------+
```

### Pattern 2: Validating User Input

```python
age_input = input("Enter your age: ")

# Check if the input is a valid number
if age_input.isdigit():
    age = int(age_input)
    if 0 <= age <= 150:
        print(f"Your age is {age}")
    else:
        print("Age must be between 0 and 150")
else:
    print("Please enter a valid number")
```

**Line-by-Line Explanation:**

- `age_input.isdigit()` checks if the string contains only digits. This prevents errors when converting to int.
- If valid, we convert and then check the range.
- If not valid, we show an error message.

### Pattern 3: Menu Selection

```python
print("1. Start Game")
print("2. Load Game")
print("3. Quit")

choice = input("Enter your choice (1-3): ")

if choice == "1":
    print("Starting new game...")
elif choice == "2":
    print("Loading saved game...")
elif choice == "3":
    print("Goodbye!")
else:
    print("Invalid choice. Please enter 1, 2, or 3.")
```

### Pattern 4: Default Values

```python
user_name = input("Enter your name (or press Enter for default): ")

if not user_name:
    user_name = "Guest"

print(f"Welcome, {user_name}!")
```

If the user presses Enter without typing anything, `user_name` is an empty string (falsy). The `not` operator flips that to True, so we assign the default value "Guest".

---

## Putting It All Together

Here is a complete program using many conditional patterns:

```python
# ticket_price.py - Calculate movie ticket price

print("=== Movie Ticket Calculator ===")
print()

age = int(input("Enter your age: "))
is_student = input("Are you a student? (yes/no): ").lower() == "yes"
day = input("What day is it? (mon/tue/wed/thu/fri/sat/sun): ").lower()

# Determine base price by age
if age < 5:
    price = 0
    category = "Free (under 5)"
elif age < 13:
    price = 8
    category = "Child"
elif age >= 65:
    price = 9
    category = "Senior"
else:
    price = 14
    category = "Adult"

# Student discount (20% off, adults only)
discount = 0
if is_student and price == 14:
    discount = price * 0.20
    price -= discount

# Tuesday special (half price)
is_tuesday = day == "tue"
if is_tuesday and price > 0:
    price = price / 2

# Display result
print()
print("=" * 35)
print("       TICKET RECEIPT")
print("=" * 35)
print(f"  Category:  {category}")
print(f"  Student:   {'Yes' if is_student else 'No'}")
if discount > 0:
    print(f"  Discount:  -${discount:.2f}")
if is_tuesday:
    print(f"  Tuesday:   Half price!")
print(f"  Total:     ${price:.2f}")
print("=" * 35)
```

**Expected Output (example):**

```
=== Movie Ticket Calculator ===

Enter your age: 22
Are you a student? (yes/no): yes
What day is it? (mon/tue/wed/thu/fri/sat/sun): tue

===================================
       TICKET RECEIPT
===================================
  Category:  Adult
  Student:   Yes
  Discount:  -$2.80
  Tuesday:   Half price!
  Total:     $5.60
===================================
```

**Line-by-Line Explanation:**

- `input(...).lower()` gets input and converts to lowercase. So "Yes", "YES", "yes" all become "yes".
- The `if-elif-else` chain assigns a price based on age category.
- The student discount applies only to adults (price == 14). 20% of 14 is 2.80.
- After the student discount, price is 11.20. Tuesday halves it to 5.60.
- The ternary `'Yes' if is_student else 'No'` prints "Yes" or "No" inline.

---

## Common Mistakes

**Mistake 1: Forgetting the colon**

```python
# Wrong - missing colon
if age >= 18
    print("Adult")

# Right
if age >= 18:
    print("Adult")
```

**Mistake 2: Wrong indentation**

```python
# Wrong - inconsistent indentation
if age >= 18:
    print("You are an adult")
  print("You can vote")        # IndentationError!

# Right - consistent 4-space indent
if age >= 18:
    print("You are an adult")
    print("You can vote")
```

**Mistake 3: Using = instead of ==**

```python
# Wrong - this assigns, not compares
if age = 18:     # SyntaxError!
    print("You are 18")

# Right - use == to compare
if age == 18:
    print("You are 18")
```

**Mistake 4: Checking multiple values the wrong way**

```python
# Wrong - does not do what you think
if day == "Saturday" or "Sunday":    # Always True!
    print("Weekend")

# Right - compare each value explicitly
if day == "Saturday" or day == "Sunday":
    print("Weekend")

# Also right - use 'in' with a collection
if day in ("Saturday", "Sunday"):
    print("Weekend")
```

Why is the wrong version always True? Python reads `"Sunday"` as a standalone expression. A non-empty string is truthy. So it becomes `False or True`, which is `True`.

**Mistake 5: Overlapping conditions in elif**

```python
# Problem - what grade does 80 get?
if score >= 80:
    grade = "B"
elif score >= 80:    # This never runs! First condition catches 80.
    grade = "B+"
```

---

## Best Practices

1. **Keep conditions simple.** If a condition is complex, break it into variables:
   ```python
   # Hard to read
   if age >= 21 and income > 30000 and credit_score > 650 and not has_bankruptcy:
       approve_loan()

   # Easier to read
   is_old_enough = age >= 21
   has_income = income > 30000
   has_credit = credit_score > 650
   is_eligible = is_old_enough and has_income and has_credit and not has_bankruptcy
   if is_eligible:
       approve_loan()
   ```

2. **Avoid deep nesting.** More than 3 levels of nesting makes code hard to read. Use `and` to flatten conditions or use early returns.

3. **Put the most common case first.** If 90% of users are adults, check for adults first.

4. **Use `in` for multiple value checks.** `if x in (1, 2, 3):` is cleaner than `if x == 1 or x == 2 or x == 3:`.

5. **Use `.lower()` or `.upper()` for string comparisons.** This handles different capitalizations from user input.

6. **Always include an `else` in important decisions.** Even if you think the `if` and `elif` cover everything, an `else` catches unexpected cases.

---

## Quick Summary

The `if` statement runs code only when a condition is True. The `else` block runs when the condition is False. The `elif` block adds more conditions to check. Python checks conditions from top to bottom and runs the first matching block. You can nest conditions inside each other or combine them with `and`, `or`, and `not`. Every value in Python is either truthy or falsy. The ternary operator lets you write simple if-else on one line. Common patterns include range checking, input validation, menu selection, and default values.

---

## Key Points to Remember

- `if condition:` -- the colon is required.
- Indentation (4 spaces) defines the block. No curly braces.
- `elif` is short for "else if." You can have as many as you need.
- `else` catches everything that no `if` or `elif` caught.
- Python checks conditions top to bottom. First True match wins.
- Falsy values: `False`, `0`, `0.0`, `""`, `None`, `[]`.
- Everything else is truthy.
- Ternary: `value_if_true if condition else value_if_false`.
- Use `and` when both conditions must be True.
- Use `or` when at least one must be True.
- Use `not` to reverse a condition.
- Chained comparison: `10 <= x <= 20` works in Python.
- Use `in` to check membership: `if x in (1, 2, 3):`.

---

## Practice Questions

**Question 1:** What does this code print?

```python
x = 15
if x > 20:
    print("big")
elif x > 10:
    print("medium")
elif x > 5:
    print("small")
else:
    print("tiny")
```

<details>
<summary>Answer</summary>

`medium`. Python checks top to bottom. `x > 20` is False (15 > 20). `x > 10` is True (15 > 10). So "medium" prints. The remaining conditions are skipped.

</details>

**Question 2:** What is the value of `result`?

```python
result = "yes" if 0 else "no"
```

<details>
<summary>Answer</summary>

`"no"`. The condition is `0`, which is falsy. So the `else` value "no" is used.

</details>

**Question 3:** Why does this code always print "weekend"?

```python
day = "Monday"
if day == "Saturday" or "Sunday":
    print("weekend")
```

<details>
<summary>Answer</summary>

Python evaluates `"Sunday"` as a standalone expression. A non-empty string is truthy. So the condition becomes `False or True`, which is `True`. The fix is: `if day == "Saturday" or day == "Sunday":` or `if day in ("Saturday", "Sunday"):`.

</details>

**Question 4:** What does this code print?

```python
name = ""
if name:
    print(f"Hello, {name}")
else:
    print("Hello, stranger")
```

<details>
<summary>Answer</summary>

`Hello, stranger`. The empty string `""` is falsy, so the `if` block is skipped and the `else` block runs.

</details>

**Question 5:** What is wrong with this code?

```python
temperature = 75
if temperature > 90:
    print("Hot")
if temperature > 70:
    print("Warm")
if temperature > 50:
    print("Cool")
else:
    print("Cold")
```

<details>
<summary>Answer</summary>

The code uses separate `if` statements instead of `elif`. Each `if` is checked independently. For temperature = 75, it prints both "Warm" and "Cool" because both conditions are True. It should use `elif` to ensure only one block runs:
```python
if temperature > 90:
    print("Hot")
elif temperature > 70:
    print("Warm")
elif temperature > 50:
    print("Cool")
else:
    print("Cold")
```

</details>

---

## Exercises

### Exercise 1: Number Classifier

Write a program that takes a number from the user and tells them if it is positive, negative, or zero. Also tell them if it is even or odd (for non-zero numbers).

**Example:**

```
Enter a number: -7
-7 is negative
-7 is odd
```

**Solution:**

```python
# number_classifier.py
number = int(input("Enter a number: "))

if number > 0:
    print(f"{number} is positive")
elif number < 0:
    print(f"{number} is negative")
else:
    print(f"{number} is zero")

if number != 0:
    if number % 2 == 0:
        print(f"{number} is even")
    else:
        print(f"{number} is odd")
```

### Exercise 2: Simple Login System

Write a program that asks for a username and password. Check them against stored values. Give appropriate messages for wrong username, wrong password, or successful login.

**Example:**

```
Username: admin
Password: secret123
Login successful! Welcome, admin.
```

**Solution:**

```python
# login.py
stored_username = "admin"
stored_password = "secret123"

username = input("Username: ")
password = input("Password: ")

if username != stored_username:
    print("Username not found.")
elif password != stored_password:
    print("Incorrect password.")
else:
    print(f"Login successful! Welcome, {username}.")
```

### Exercise 3: Shipping Calculator

Write a program that calculates shipping cost based on weight and destination. Rules:
- Under 1 kg: $5 domestic, $15 international
- 1 to 5 kg: $10 domestic, $25 international
- Over 5 kg: $20 domestic, $45 international

**Example:**

```
Enter package weight (kg): 3.5
Destination (domestic/international): domestic
Shipping cost: $10.00
```

**Solution:**

```python
# shipping.py
weight = float(input("Enter package weight (kg): "))
destination = input("Destination (domestic/international): ").lower()

if destination not in ("domestic", "international"):
    print("Invalid destination. Choose domestic or international.")
else:
    is_domestic = destination == "domestic"

    if weight < 1:
        cost = 5 if is_domestic else 15
    elif weight <= 5:
        cost = 10 if is_domestic else 25
    else:
        cost = 20 if is_domestic else 45

    print(f"Shipping cost: ${cost:.2f}")
```

---

## What Is Next?

Your programs can now make decisions. But they still run each line at most once. What if you need to repeat something 100 times? Or process every item in a list? In the next chapter, you will learn about **loops** -- the structures that let your program repeat actions. Loops are the key to processing data at scale, and they are essential for everything in AI.
