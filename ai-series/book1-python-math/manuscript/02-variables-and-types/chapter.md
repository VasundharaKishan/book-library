# Chapter 2: Variables and Data Types

## What You Will Learn

- What variables are and why they matter
- How to create and name variables properly
- The four basic data types: int, float, string, and boolean
- How to check a value's type with `type()`
- How to convert between types with `int()`, `float()`, and `str()`
- How to get input from users with `input()`
- How to format text with f-strings
- What `None` means and when to use it

## Why This Chapter Matters

Every useful program needs to remember information. A game remembers your score. A weather app remembers the temperature. An AI model remembers its training data. Variables are how Python stores information in memory. Without variables, your programs cannot do anything meaningful. This chapter teaches you how to store, name, and work with different kinds of data.

---

## What Is a Variable?

A variable is a labeled box that holds a value.

Imagine you have a box. You write "age" on the outside. You put the number 25 inside. Now whenever you say "age", you get 25 back.

That is exactly what a variable does in Python.

```python
age = 25
```

```
+----------------------------------------------+
|          VARIABLE = LABELED BOX              |
+----------------------------------------------+
|                                              |
|    age = 25                                  |
|                                              |
|    +--------+                                |
|    |  age   |  <-- label (variable name)     |
|    +--------+                                |
|    |   25   |  <-- content (value)           |
|    +--------+                                |
|                                              |
|    name = "Alice"                            |
|                                              |
|    +--------+                                |
|    |  name  |  <-- label                     |
|    +--------+                                |
|    | Alice  |  <-- content                   |
|    +--------+                                |
|                                              |
+----------------------------------------------+
```

**Line-by-Line Explanation:**

```python
age = 25
```

- `age` is the variable name. It is the label on the box.
- `=` is the assignment operator. It means "put this value into this box." It does NOT mean "equals" in the math sense.
- `25` is the value. It is what goes inside the box.

Let us try a few more:

```python
name = "Alice"
temperature = 98.6
is_student = True
```

**Expected Output (when printed):**

```python
print(age)
print(name)
print(temperature)
print(is_student)
```

```
25
Alice
98.6
True
```

---

## Variable Naming Rules

Python has rules for naming variables. Break them and Python gives you an error.

### The Rules

| Rule | Valid | Invalid |
|------|-------|---------|
| Must start with a letter or underscore | `name`, `_count` | `2name`, `@data` |
| Can contain letters, numbers, underscores | `score1`, `my_age` | `my-age`, `my age` |
| Cannot be a Python keyword | `data`, `result` | `if`, `for`, `print` |
| Case sensitive | `Age` and `age` are different | -- |

### Good Naming Habits

```python
# Good - clear and descriptive
student_name = "Alice"
total_score = 95
is_active = True

# Bad - confusing
x = "Alice"
a = 95
b = True
```

```
+----------------------------------------------+
|        NAMING CONVENTION: snake_case         |
+----------------------------------------------+
|                                              |
|   Python uses snake_case for variables:      |
|                                              |
|   first_name     (good)                      |
|   firstName      (not Python style)          |
|   FirstName      (not Python style)          |
|   FIRST_NAME     (used for constants)        |
|                                              |
|   snake_case means:                          |
|   - all lowercase letters                    |
|   - words separated by underscores           |
|                                              |
+----------------------------------------------+
```

### Python Keywords You Cannot Use as Variable Names

These words are reserved. Python uses them for special purposes.

```
False    True     None     and      as
assert   async    await    break    class
continue def      del      elif     else
except   finally  for      from     global
if       import   in       is       lambda
nonlocal not      or       pass     raise
return   try      while    with     yield
```

---

## Data Type 1: Integers (int)

An integer is a whole number. No decimal point.

```python
age = 25
year = 2024
score = -10
zero = 0
```

**Expected Output:**

```python
print(age)
print(type(age))
```

```
25
<class 'int'>
```

**Line-by-Line Explanation:**

- `print(age)` displays the value stored in `age`, which is `25`.
- `print(type(age))` displays the data type of `age`. The `type()` function tells you what kind of data a variable holds. Here it says `<class 'int'>`, meaning integer.

Think of integers like counting on your fingers. You can count 1, 2, 3. You cannot count 1.5 on your fingers. That is the difference between integers and the next type.

```
+----------------------------------------------+
|              INTEGERS (int)                  |
+----------------------------------------------+
|                                              |
|   Whole numbers:                             |
|                                              |
|   ... -3  -2  -1   0   1   2   3 ...        |
|   <-------|---------|---------|------>        |
|        negative    zero    positive          |
|                                              |
|   No decimal points allowed.                 |
|   42 is an int. 42.0 is NOT an int.          |
|                                              |
+----------------------------------------------+
```

---

## Data Type 2: Floats (float)

A float is a number with a decimal point.

```python
temperature = 98.6
pi = 3.14159
price = 9.99
negative_float = -0.5
```

**Expected Output:**

```python
print(temperature)
print(type(temperature))
```

```
98.6
<class 'float'>
```

**Line-by-Line Explanation:**

- `print(temperature)` displays `98.6`.
- `type(temperature)` returns `<class 'float'>` because the value has a decimal point.

An important detail: even `10.0` is a float, not an integer. The decimal point makes it a float.

```python
>>> type(10)
<class 'int'>
>>> type(10.0)
<class 'float'>
```

Think of floats like measurements. Your height might be 5.9 feet. The temperature might be 72.3 degrees. These are not whole numbers. They need decimal points.

---

## Data Type 3: Strings (str)

A string is text. Letters, words, sentences, or any characters inside quotes.

```python
name = "Alice"
greeting = 'Hello, World!'
empty = ""
number_as_text = "42"
```

You can use double quotes `" "` or single quotes `' '`. Both work the same way. Pick one style and stick with it.

**Expected Output:**

```python
print(name)
print(type(name))
print(len(name))
```

```
Alice
<class 'str'>
5
```

**Line-by-Line Explanation:**

- `print(name)` displays `Alice`.
- `type(name)` returns `<class 'str'>`, confirming it is a string.
- `len(name)` returns `5` because "Alice" has 5 characters. The `len()` function counts the length of a string.

```
+----------------------------------------------+
|             STRINGS (str)                    |
+----------------------------------------------+
|                                              |
|   "Alice"                                    |
|    A  l  i  c  e                             |
|    0  1  2  3  4    <-- index positions       |
|                                              |
|   Length = 5 characters                      |
|                                              |
|   Strings can contain:                       |
|   - Letters: "Hello"                         |
|   - Numbers: "42" (still text, not a number) |
|   - Symbols: "hello@world.com"               |
|   - Spaces: "Hello World"                    |
|   - Nothing: "" (empty string)               |
|                                              |
+----------------------------------------------+
```

**Important:** `"42"` is a string, not a number. It is text that looks like a number. You cannot do math with it directly.

```python
>>> "42" + "8"
'428'         # String concatenation, not addition!

>>> 42 + 8
50            # This is actual math
```

---

## Data Type 4: Booleans (bool)

A boolean has only two possible values: `True` or `False`.

```python
is_raining = True
is_sunny = False
has_passed = True
```

**Expected Output:**

```python
print(is_raining)
print(type(is_raining))
```

```
True
<class 'bool'>
```

**Line-by-Line Explanation:**

- `print(is_raining)` displays `True`.
- `type(is_raining)` returns `<class 'bool'>`, confirming it is a boolean.

Think of booleans like light switches. A light is either on (True) or off (False). There is no in-between.

```
+----------------------------------------------+
|            BOOLEANS (bool)                   |
+----------------------------------------------+
|                                              |
|    True    or    False                        |
|                                              |
|    Like a light switch:                      |
|                                              |
|    ON  [/]     OFF [O]                       |
|    True        False                         |
|                                              |
|    Like yes/no questions:                    |
|    Is it raining?    True / False             |
|    Is the door open? True / False             |
|    Did the test pass? True / False            |
|                                              |
|    Note: Capital T and F required!            |
|    True  (correct)                           |
|    true  (error!)                            |
|                                              |
+----------------------------------------------+
```

> **Important:** `True` and `False` must be capitalized. Writing `true` or `false` (lowercase) will cause an error.

---

## The type() Function

The `type()` function is your data detective. It tells you what kind of data you are working with.

```python
print(type(42))
print(type(3.14))
print(type("hello"))
print(type(True))
```

**Expected Output:**

```
<class 'int'>
<class 'float'>
<class 'str'>
<class 'bool'>
```

This function is very useful when debugging. If your code is not working, checking the type often reveals the problem.

```
+----------------------------------------------+
|          DATA TYPE SUMMARY                   |
+----------------------------------------------+
|                                              |
|   Type      Example      type() returns     |
|   ----      -------      --------------     |
|   int       42           <class 'int'>      |
|   float     3.14         <class 'float'>    |
|   str       "hello"      <class 'str'>      |
|   bool      True         <class 'bool'>     |
|   NoneType  None         <class 'NoneType'> |
|                                              |
+----------------------------------------------+
```

---

## Type Conversion

Sometimes you need to change data from one type to another. Python gives you functions for this.

### int() - Convert to Integer

```python
# Float to integer (drops the decimal part)
x = int(3.9)
print(x)           # Output: 3

# String to integer
y = int("42")
print(y)           # Output: 42

# Boolean to integer
z = int(True)
print(z)           # Output: 1
```

**Line-by-Line Explanation:**

- `int(3.9)` converts the float `3.9` to the integer `3`. It does NOT round. It chops off the decimal part.
- `int("42")` converts the string `"42"` to the integer `42`. Now you can do math with it.
- `int(True)` converts `True` to `1`. In Python, `True` equals `1` and `False` equals `0`.

### float() - Convert to Float

```python
# Integer to float
a = float(42)
print(a)           # Output: 42.0

# String to float
b = float("3.14")
print(b)           # Output: 3.14
```

### str() - Convert to String

```python
# Integer to string
c = str(42)
print(c)           # Output: 42
print(type(c))     # Output: <class 'str'>

# Float to string
d = str(3.14)
print(d)           # Output: 3.14
print(type(d))     # Output: <class 'str'>
```

```
+----------------------------------------------+
|         TYPE CONVERSION FLOW                 |
+----------------------------------------------+
|                                              |
|           str("42")                          |
|              |                               |
|              v                               |
|   "42"  --int()--->  42  --float()--->  42.0 |
|    str               int                float|
|              ^                  |             |
|              |                  |             |
|           str()              int()           |
|              |                  |             |
|              +--<---  42  <-----+             |
|                                              |
+----------------------------------------------+
```

### Conversion Errors

Not all conversions work. Python will tell you when a conversion is impossible.

```python
>>> int("hello")
ValueError: invalid literal for int() with base 10: 'hello'
```

You cannot convert the word "hello" to a number. That makes no sense. Python tells you so.

```python
>>> int("3.14")
ValueError: invalid literal for int() with base 10: '3.14'
```

You cannot convert "3.14" directly to an integer. Convert to float first, then to int:

```python
>>> int(float("3.14"))
3
```

---

## Getting User Input

Programs that only display pre-written text are boring. Let us make programs that ask the user for information.

The `input()` function pauses the program and waits for the user to type something.

```python
name = input("What is your name? ")
print("Hello, " + name + "!")
```

**Expected Output (interactive):**

```
What is your name? Alice
Hello, Alice!
```

**Line-by-Line Explanation:**

- `input("What is your name? ")` displays the message and waits. Whatever the user types is stored in the variable `name`.
- `print("Hello, " + name + "!")` combines the greeting with the user's name and displays it.

### Important: input() Always Returns a String

Even if the user types a number, `input()` gives you a string.

```python
age = input("How old are you? ")
print(type(age))    # Output: <class 'str'>
```

If you need to do math with the input, convert it first:

```python
age = input("How old are you? ")
age = int(age)       # Convert string to integer
birth_year = 2024 - age
print("You were born around " + str(birth_year))
```

**Expected Output:**

```
How old are you? 25
You were born around 1999
```

**Line-by-Line Explanation:**

- `age = input("How old are you? ")` gets the user's age as a string.
- `age = int(age)` converts it from a string to an integer so we can do math.
- `2024 - age` subtracts the age from 2024 to estimate the birth year.
- `str(birth_year)` converts the result back to a string so we can combine it with text.

```
+----------------------------------------------+
|          input() ALWAYS RETURNS str          |
+----------------------------------------------+
|                                              |
|   User types: 25                             |
|                                              |
|   input() returns: "25"  <-- string!         |
|                                              |
|   You must convert:                          |
|   int("25")   -> 25     (now a number)       |
|   float("25") -> 25.0   (now a number)       |
|                                              |
|   Common pattern:                            |
|   age = int(input("Age? "))                  |
|   (input and convert in one line)            |
|                                              |
+----------------------------------------------+
```

---

## F-Strings: Easy Text Formatting

Combining text and variables with `+` works, but it gets messy. F-strings are a cleaner way to do it.

An f-string starts with the letter `f` before the opening quote. Inside the string, you put variables in curly braces `{}`.

```python
name = "Alice"
age = 25
score = 95.5

# Old way (using +)
print("Name: " + name + ", Age: " + str(age))

# New way (using f-strings)
print(f"Name: {name}, Age: {age}")
print(f"{name} scored {score} on the test")
print(f"In 5 years, {name} will be {age + 5}")
```

**Expected Output:**

```
Name: Alice, Age: 25
Name: Alice, Age: 25
Alice scored 95.5 on the test
In 5 years, Alice will be 30
```

**Line-by-Line Explanation:**

- `f"Name: {name}, Age: {age}"` puts the values of `name` and `age` directly into the string. No need for `+` or `str()`.
- `f"{name} scored {score} on the test"` mixes text and variables seamlessly.
- `f"In 5 years, {name} will be {age + 5}"` shows that you can even do math inside the curly braces.

```
+----------------------------------------------+
|          F-STRING ANATOMY                    |
+----------------------------------------------+
|                                              |
|   f"Hello, {name}! You are {age} years old." |
|   |         |                |               |
|   |         |                +-- variable     |
|   |         +-- variable                     |
|   +-- the f makes it an f-string             |
|                                              |
|   Rules:                                     |
|   1. Put f before the opening quote          |
|   2. Use {variable} to insert values         |
|   3. You can do math: {age + 5}              |
|   4. You can call functions: {name.upper()}  |
|                                              |
+----------------------------------------------+
```

### Formatting Numbers in F-Strings

F-strings can also format numbers nicely:

```python
pi = 3.14159265

# Round to 2 decimal places
print(f"Pi is approximately {pi:.2f}")

# Add commas to large numbers
population = 8000000000
print(f"World population: {population:,}")
```

**Expected Output:**

```
Pi is approximately 3.14
World population: 8,000,000,000
```

---

## The None Type

`None` is a special value in Python. It means "nothing" or "no value."

```python
result = None
print(result)
print(type(result))
```

**Expected Output:**

```
None
<class 'NoneType'>
```

Think of `None` as an empty box. The box exists, but nothing is inside it.

```
+----------------------------------------------+
|              None                            |
+----------------------------------------------+
|                                              |
|   result = None                              |
|                                              |
|   +----------+                               |
|   |  result  |  <-- the box exists           |
|   +----------+                               |
|   | (empty)  |  <-- but nothing is inside    |
|   +----------+                               |
|                                              |
|   Common uses:                               |
|   - Default value before calculation         |
|   - "Not found" result                       |
|   - Placeholder for missing data             |
|                                              |
+----------------------------------------------+
```

### When Do You Use None?

```python
# Before you have a result
best_score = None

# After calculating
best_score = 95

# Checking for None
if best_score is None:
    print("No score yet")
else:
    print(f"Best score: {best_score}")
```

**Expected Output:**

```
Best score: 95
```

> **Note:** Use `is None` to check for None, not `== None`. This is a Python best practice we will explain more in later chapters.

---

## Variables Can Change

Variables are not permanent. You can change their value at any time.

```python
score = 0
print(f"Starting score: {score}")

score = 10
print(f"After level 1: {score}")

score = 25
print(f"After level 2: {score}")
```

**Expected Output:**

```
Starting score: 0
After level 1: 10
After level 2: 25
```

The old value is gone. Python only remembers the most recent value.

```
+----------------------------------------------+
|      VARIABLES CAN BE REASSIGNED             |
+----------------------------------------------+
|                                              |
|   score = 0                                  |
|   +-------+                                  |
|   | score |                                  |
|   +-------+     Before: 0                    |
|   |   0   |                                  |
|   +-------+                                  |
|                                              |
|   score = 10                                 |
|   +-------+                                  |
|   | score |     0 is gone!                   |
|   +-------+                                  |
|   |  10   |     Now: 10                      |
|   +-------+                                  |
|                                              |
+----------------------------------------------+
```

You can even change the type:

```python
x = 42        # x is an integer
x = "hello"   # now x is a string
x = True      # now x is a boolean
```

Python allows this. But it is usually a bad idea. It makes your code confusing. Try to keep a variable's type consistent.

---

## Multiple Assignment

Python lets you assign multiple variables in one line:

```python
# Assign different values
x, y, z = 1, 2, 3
print(x)    # Output: 1
print(y)    # Output: 2
print(z)    # Output: 3

# Assign the same value
a = b = c = 0
print(a)    # Output: 0
print(b)    # Output: 0
print(c)    # Output: 0
```

### Swapping Variables

A handy Python trick. Swap two values without a temporary variable:

```python
a = "first"
b = "second"

# Swap them
a, b = b, a

print(a)    # Output: second
print(b)    # Output: first
```

---

## Putting It All Together

Here is a complete program that uses everything from this chapter:

```python
# profile_card.py - Create a simple profile card

# Get information from the user
name = input("Enter your name: ")
age = int(input("Enter your age: "))
height = float(input("Enter your height in meters: "))
is_student = input("Are you a student? (yes/no): ") == "yes"

# Calculate some values
age_in_months = age * 12
height_in_cm = height * 100

# Display the profile card
print()
print("=" * 40)
print(f"       PROFILE CARD")
print("=" * 40)
print(f"  Name:     {name}")
print(f"  Age:      {age} years ({age_in_months} months)")
print(f"  Height:   {height}m ({height_in_cm:.0f}cm)")
print(f"  Student:  {is_student}")
print("=" * 40)
```

**Expected Output:**

```
Enter your name: Alice
Enter your age: 25
Enter your height in meters: 1.65
Are you a student? (yes/no): yes

========================================
       PROFILE CARD
========================================
  Name:     Alice
  Age:      25 years (300 months)
  Height:   1.65m (165cm)
  Student:  True
========================================
```

**Line-by-Line Explanation:**

- `name = input(...)` gets the name as a string.
- `age = int(input(...))` gets the age and converts it to an integer in one step.
- `height = float(input(...))` gets the height and converts it to a float.
- `is_student = input(...) == "yes"` checks if the user typed "yes". The result is a boolean: `True` or `False`.
- `age_in_months = age * 12` calculates months from years.
- `height_in_cm = height * 100` converts meters to centimeters.
- `"=" * 40` creates a line of 40 equal signs. This is string repetition.
- `{height_in_cm:.0f}` formats the number with zero decimal places.

---

## Common Mistakes

**Mistake 1: Using a variable before creating it**

```python
# Wrong - name does not exist yet
print(name)
name = "Alice"

# Right - create first, then use
name = "Alice"
print(name)
```

**Mistake 2: Forgetting to convert input()**

```python
# Wrong - trying to do math with a string
age = input("Age: ")
next_year = age + 1    # TypeError!

# Right - convert to int first
age = int(input("Age: "))
next_year = age + 1    # Works!
```

**Mistake 3: Mixing types with + operator**

```python
# Wrong - cannot add string and integer
age = 25
print("I am " + age + " years old")   # TypeError!

# Right - use f-string
print(f"I am {age} years old")

# Also right - convert to string
print("I am " + str(age) + " years old")
```

**Mistake 4: Wrong capitalization of True/False/None**

```python
# Wrong
is_active = true    # NameError!
result = none       # NameError!

# Right
is_active = True
result = None
```

**Mistake 5: Using a Python keyword as a variable name**

```python
# Wrong
for = 10           # SyntaxError!
class = "Math"     # SyntaxError!

# Right
loop_count = 10
class_name = "Math"
```

---

## Best Practices

1. **Use descriptive variable names.** `student_name` is better than `sn`. `total_price` is better than `tp`.

2. **Use snake_case.** Separate words with underscores: `first_name`, `max_score`, `is_valid`.

3. **Keep types consistent.** If a variable starts as an integer, keep it as an integer.

4. **Convert input immediately.** Write `age = int(input("Age: "))` instead of converting later.

5. **Use f-strings for formatting.** They are cleaner and easier to read than string concatenation.

6. **Initialize variables with sensible defaults.** Use `None` when you do not have a value yet, `0` for counters, `""` for empty strings.

---

## Quick Summary

Variables store data in your program. Every variable has a name and a value. Python has four basic data types: integers (whole numbers), floats (decimal numbers), strings (text), and booleans (True/False). The `type()` function tells you what type a value is. You can convert between types using `int()`, `float()`, and `str()`. The `input()` function gets text from the user (always as a string). F-strings let you combine text and variables cleanly. `None` represents "no value."

---

## Key Points to Remember

- Variables are labeled boxes that store values.
- Use `=` to assign a value to a variable.
- Variable names must start with a letter or underscore.
- Python has four basic types: `int`, `float`, `str`, `bool`.
- `type()` tells you a value's data type.
- `int()`, `float()`, `str()` convert between types.
- `input()` always returns a string. Convert it if you need a number.
- F-strings: `f"Hello, {name}"` -- put `f` before the quotes, variables in `{}`.
- `None` means "no value." Check it with `is None`.
- Variable names should be descriptive and use snake_case.

---

## Practice Questions

**Question 1:** What is the data type of each value?

```python
a = 42
b = "42"
c = 42.0
d = True
e = None
```

<details>
<summary>Answer</summary>

- `a` is `int` (integer -- whole number, no quotes)
- `b` is `str` (string -- it is in quotes)
- `c` is `float` (has a decimal point)
- `d` is `bool` (boolean -- True or False)
- `e` is `NoneType` (the special None value)

</details>

**Question 2:** What does this code print?

```python
x = "10"
y = "20"
print(x + y)
```

<details>
<summary>Answer</summary>

It prints `1020`, not `30`. Both `x` and `y` are strings (they have quotes). The `+` operator concatenates (joins) strings instead of adding numbers.

</details>

**Question 3:** Why does this code cause an error?

```python
age = input("Enter your age: ")
can_vote = age >= 18
```

<details>
<summary>Answer</summary>

`input()` returns a string. You cannot compare a string with `>=` to an integer. You need to convert first: `age = int(input("Enter your age: "))`.

</details>

**Question 4:** What is the difference between `None` and `0`?

<details>
<summary>Answer</summary>

`None` means "no value at all." It is the absence of data. `0` is a value -- it is the integer zero. A variable set to `0` has a value. A variable set to `None` does not have a value yet.

</details>

**Question 5:** What does this f-string produce?

```python
item = "book"
price = 12.5
quantity = 3
print(f"You bought {quantity} {item}s for ${price * quantity:.2f}")
```

<details>
<summary>Answer</summary>

It prints: `You bought 3 books for $37.50`

The f-string inserts `quantity` (3) and `item` (book), and calculates `price * quantity` (37.5), formatting it to two decimal places (37.50).

</details>

---

## Exercises

### Exercise 1: Temperature Converter

Write a program that asks the user for a temperature in Celsius and converts it to Fahrenheit. The formula is: `F = C * 9/5 + 32`

**Example:**

```
Enter temperature in Celsius: 100
100.0°C is 212.0°F
```

**Hint:** Remember to convert the input to a float.

**Solution:**

```python
# temperature_converter.py
celsius = float(input("Enter temperature in Celsius: "))
fahrenheit = celsius * 9/5 + 32
print(f"{celsius}°C is {fahrenheit}°F")
```

### Exercise 2: Personal Info Card

Write a program that asks for the user's first name, last name, birth year, and favorite color. Display all the information in a formatted card. Calculate their approximate age.

**Example:**

```
First name: Alice
Last name: Smith
Birth year: 1999
Favorite color: blue

+---------------------------+
|      PERSONAL INFO        |
+---------------------------+
| Name:  Alice Smith        |
| Age:   ~25 years old      |
| Color: blue               |
+---------------------------+
```

**Solution:**

```python
# personal_info.py
first = input("First name: ")
last = input("Last name: ")
year = int(input("Birth year: "))
color = input("Favorite color: ")

age = 2024 - year

print()
print("+---------------------------+")
print("|      PERSONAL INFO        |")
print("+---------------------------+")
print(f"| Name:  {first} {last}")
print(f"| Age:   ~{age} years old")
print(f"| Color: {color}")
print("+---------------------------+")
```

### Exercise 3: Type Explorer

Write a program that demonstrates type conversion. Create one variable of each type (int, float, str, bool). Print each variable and its type. Then convert each to a different type and print the results.

**Solution:**

```python
# type_explorer.py
my_int = 42
my_float = 3.14
my_str = "100"
my_bool = True

print("Original values and types:")
print(f"  {my_int} -> {type(my_int)}")
print(f"  {my_float} -> {type(my_float)}")
print(f"  {my_str} -> {type(my_str)}")
print(f"  {my_bool} -> {type(my_bool)}")

print()
print("After conversion:")
print(f"  int to float: {float(my_int)} -> {type(float(my_int))}")
print(f"  float to int: {int(my_float)} -> {type(int(my_float))}")
print(f"  str to int:   {int(my_str)} -> {type(int(my_str))}")
print(f"  bool to int:  {int(my_bool)} -> {type(int(my_bool))}")
```

**Expected Output:**

```
Original values and types:
  42 -> <class 'int'>
  3.14 -> <class 'float'>
  100 -> <class 'str'>
  True -> <class 'bool'>

After conversion:
  int to float: 42.0 -> <class 'float'>
  float to int: 3 -> <class 'int'>
  str to int:   100 -> <class 'int'>
  bool to int:  1 -> <class 'bool'>
```

---

## What Is Next?

Now you can store data in variables. But what can you do with that data? In the next chapter, you will learn about **operators** -- the tools that let you do math, compare values, and combine conditions. Operators turn your static data into dynamic calculations.
