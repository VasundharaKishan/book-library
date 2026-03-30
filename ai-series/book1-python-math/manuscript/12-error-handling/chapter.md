# Chapter 12: Error Handling

## What You Will Learn

- What errors are and why they happen
- The different types of errors in Python
- How to use `try/except` to catch errors
- How to use `try/except/else/finally` for complete error handling
- How to raise your own exceptions
- How to read error messages (tracebacks)
- Common debugging tips to fix problems faster

## Why This Chapter Matters

Errors are not your enemy. They are Python's way of **talking to you**. When something goes wrong, Python does not just crash silently. It tells you exactly what happened and where.

Think of errors like warning lights on a car dashboard. The check engine light does not mean your car is ruined. It means something needs attention. Python errors work the same way.

Every programmer — beginner and expert — encounters errors every single day. The difference is that experienced programmers know how to **read** error messages and **handle** them gracefully.

In this chapter, you will learn to turn scary red error messages into useful information.

---

## 12.1 What Is an Error?

An error happens when Python cannot do what you asked. There are two main categories:

```
+-------------------+       +-------------------+
|   Syntax Errors   |       |  Runtime Errors    |
+-------------------+       +-------------------+
| Found BEFORE      |       | Found WHILE        |
| your code runs    |       | your code runs     |
|                   |       |                    |
| Like a typo in    |       | Like trying to     |
| a recipe that     |       | divide by zero     |
| makes no sense    |       | while cooking      |
+-------------------+       +-------------------+
```

**Syntax errors** are like grammatical mistakes. Python reads your code before running it. If the grammar is wrong, it stops immediately.

**Runtime errors** (also called **exceptions**) happen while your code is running. The grammar is correct, but something unexpected happens.

---

## 12.2 Types of Errors

### SyntaxError — "I cannot understand what you wrote."

This is the most common error for beginners. It means Python's grammar rules were broken.

```python
# Missing colon
if x > 5
    print("big")
```

**Error:**
```
  File "main.py", line 2
    if x > 5
            ^
SyntaxError: expected ':'
```

```python
# Missing closing parenthesis
print("hello"
```

**Error:**
```
  File "main.py", line 1
    print("hello"
                 ^
SyntaxError: '(' was never closed
```

**How to fix:** Look at the line Python points to. Check for missing colons, parentheses, or quotes.

### TypeError — "You are using the wrong type."

This happens when you try to do something with the wrong kind of data.

```python
# Adding a string and a number
result = "age: " + 25
```

**Error:**
```
TypeError: can only concatenate str (not "int") to str
```

```python
# Calling something that is not a function
x = 5
x()
```

**Error:**
```
TypeError: 'int' object is not callable
```

**How to fix:** Check the types of your variables. Use `type()` to see what type something is. Use `str()`, `int()`, or `float()` to convert between types.

### NameError — "I do not know what that name means."

This happens when you use a variable or function that does not exist.

```python
print(message)
```

**Error:**
```
NameError: name 'message' is not defined
```

**How to fix:** Check for typos. Make sure you defined the variable before using it.

### ValueError — "The value does not make sense."

The type is correct, but the value is wrong.

```python
number = int("hello")
```

**Error:**
```
ValueError: invalid literal for int() with base 10: 'hello'
```

```python
import math
math.sqrt(-1)
```

**Error:**
```
ValueError: math domain error
```

**How to fix:** Check what values you are passing to functions.

### IndexError — "That position does not exist."

You tried to access a list item that is out of range.

```python
fruits = ["apple", "banana", "cherry"]
print(fruits[5])
```

**Error:**
```
IndexError: list index out of range
```

```
fruits list:
Index:  0        1        2
       apple   banana   cherry

You asked for index 5, but the list only has indices 0, 1, and 2.
```

**How to fix:** Check the length of your list with `len()`. Remember that indices start at 0.

### KeyError — "That key does not exist in the dictionary."

```python
student = {"name": "Alice", "age": 20}
print(student["grade"])
```

**Error:**
```
KeyError: 'grade'
```

**How to fix:** Check what keys exist with `dict.keys()`. Use `dict.get("key", default)` to avoid the error.

### FileNotFoundError — "I cannot find that file."

```python
with open("data.csv") as f:
    content = f.read()
```

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'
```

**How to fix:** Check the file path. Make sure the file exists. Use `os.path.exists()` to check before opening.

### Quick Reference Table

```
+--------------------+-----------------------------------+
| Error Type         | What It Means                     |
+--------------------+-----------------------------------+
| SyntaxError        | Bad grammar in your code          |
| TypeError          | Wrong data type                   |
| NameError          | Variable/function not found       |
| ValueError         | Right type, wrong value           |
| IndexError         | List position out of range        |
| KeyError           | Dictionary key not found          |
| FileNotFoundError  | File does not exist               |
| ZeroDivisionError  | Tried to divide by zero           |
| AttributeError     | Object does not have that method  |
| ImportError        | Module not found or bad import    |
+--------------------+-----------------------------------+
```

---

## 12.3 try/except — Catching Errors

The `try/except` block lets you **catch** errors instead of letting your program crash.

Think of it like a safety net:

```
Without try/except:          With try/except:

Your code runs               Your code runs
     |                            |
   ERROR!                      ERROR!
     |                            |
  CRASH! Program               Caught by safety net
  stops completely.            Program keeps running.
```

### Example 1: Basic try/except

```python
try:
    number = int(input("Enter a number: "))
    print(f"You entered: {number}")
except ValueError:
    print("That is not a valid number!")
```

**If user enters "5":**
```
Enter a number: 5
You entered: 5
```

**If user enters "hello":**
```
Enter a number: hello
That is not a valid number!
```

**Line-by-line explanation:**

- `try:` — "Try to run the code below. It might cause an error."
- `number = int(input(...))` — This might fail if the user types something that is not a number.
- `except ValueError:` — "If a ValueError happens, run this code instead of crashing."
- `print("That is not a valid number!")` — The friendly error message.

### Example 2: Catching multiple error types

```python
try:
    numbers = [10, 20, 30]
    index = int(input("Enter an index: "))
    print(numbers[index])
except ValueError:
    print("Please enter a whole number!")
except IndexError:
    print("That index is out of range! Use 0, 1, or 2.")
```

**If user enters "abc":**
```
Enter an index: abc
Please enter a whole number!
```

**If user enters "5":**
```
Enter an index: 5
That index is out of range! Use 0, 1, or 2.
```

**If user enters "1":**
```
Enter an index: 1
20
```

### Example 3: Catching any error

```python
try:
    result = 10 / 0
except Exception as e:
    print(f"Something went wrong: {e}")
```

**Expected Output:**
```
Something went wrong: division by zero
```

**Line-by-line explanation:**

- `except Exception as e:` — `Exception` catches almost any error. `as e` stores the error message in the variable `e`.
- `print(f"Something went wrong: {e}")` — Prints the error message without crashing.

```
The flow of try/except:

try:
    code that might fail       <-- Python tries this
         |
    +----+----+
    |         |
  Success   Error!
    |         |
    v         v
(skip       except:
 except)     handle the error
    |         |
    +---------+
         |
    rest of program continues
```

---

## 12.4 try/except/else/finally

Python gives you four blocks for complete error handling:

```
try:        "Try this code"
except:     "If it fails, do this"
else:       "If it succeeds, do this"
finally:    "Always do this, no matter what"
```

### Example 4: The full try/except/else/finally

```python
try:
    number = int(input("Enter a number: "))
except ValueError:
    print("Invalid input!")
else:
    print(f"Success! You entered {number}")
    print(f"Double that is {number * 2}")
finally:
    print("This always runs.")
```

**If user enters "7":**
```
Enter a number: 7
Success! You entered 7
Double that is 14
This always runs.
```

**If user enters "abc":**
```
Enter a number: abc
Invalid input!
This always runs.
```

**Line-by-line explanation:**

- `try:` — Try to convert the input to an integer.
- `except ValueError:` — If the conversion fails, print "Invalid input!"
- `else:` — Only runs if the `try` block succeeded with NO errors.
- `finally:` — Runs no matter what. Error or no error. Always.

### Example 5: finally for cleanup

The `finally` block is great for cleanup tasks — like closing files.

```python
file = None
try:
    file = open("data.txt", "r")
    content = file.read()
    print(content)
except FileNotFoundError:
    print("File not found!")
finally:
    if file is not None:
        file.close()
        print("File closed.")
```

**If file does not exist:**
```
File not found!
```

**If file exists:**
```
Hello, World!
File closed.
```

The `finally` block makes sure the file gets closed, even if an error happened.

---

## 12.5 Raising Exceptions

Sometimes YOU want to create an error on purpose. This is called **raising** an exception.

Why would you do this? To stop your code when something should not happen.

### Example 6: Raising an exception

```python
def set_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative!")
    if age > 150:
        raise ValueError("Age cannot be more than 150!")
    print(f"Age set to {age}")

set_age(25)
set_age(-5)
```

**Expected Output:**
```
Age set to 25
Traceback (most recent call last):
  File "main.py", line 8, in <module>
    set_age(-5)
  File "main.py", line 3, in set_age
    raise ValueError("Age cannot be negative!")
ValueError: Age cannot be negative!
```

**Line-by-line explanation:**

- `raise ValueError("Age cannot be negative!")` — This creates a ValueError with a custom message. The program stops here (unless someone catches it with try/except).

### Example 7: Raising and catching

```python
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("You cannot divide by zero!")
    return a / b

try:
    result = divide(10, 0)
except ZeroDivisionError as e:
    print(f"Error: {e}")
    result = 0

print(f"Result: {result}")
```

**Expected Output:**
```
Error: You cannot divide by zero!
Result: 0
```

---

## 12.6 Reading Error Messages (Tracebacks)

When an error occurs, Python shows a **traceback**. It is like a trail of breadcrumbs showing you exactly where the error happened.

### Example 8: Reading a traceback

```python
def calculate_average(numbers):
    total = sum(numbers)
    average = total / len(numbers)
    return average

def process_data(data):
    result = calculate_average(data)
    return result

scores = []
final = process_data(scores)
print(final)
```

**Error:**
```
Traceback (most recent call last):
  File "main.py", line 11, in <module>
    final = process_data(scores)
  File "main.py", line 7, in process_data
    result = calculate_average(data)
  File "main.py", line 3, in calculate_average
    average = total / len(numbers)
ZeroDivisionError: division by zero
```

How to read this traceback:

```
READ FROM BOTTOM TO TOP!

Bottom:  ZeroDivisionError: division by zero
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         This is WHAT went wrong.

Line 3:  average = total / len(numbers)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         This is WHERE it went wrong.
         len(numbers) is 0, so we divided by zero.

Line 7:  result = calculate_average(data)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         This is HOW we got there.

Line 11: final = process_data(scores)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         This is WHERE it started.
         scores = [] (empty list)
```

### The Golden Rule: Read tracebacks from BOTTOM to TOP.

```
+----------------------------------------+
| Traceback (most recent call last):     |
|                                        |
|   File "main.py", line 11  <-- START  |  Read
|   File "main.py", line 7              |  from
|   File "main.py", line 3   <-- HERE   |  bottom
|                                        |  to
|   ZeroDivisionError  <-- WHAT HAPPENED |  top
+----------------------------------------+
```

1. **Last line** — What type of error and the error message.
2. **Lines above** — The chain of function calls that led to the error.
3. **Arrow (^)** — Points to the exact spot in the code.

---

## 12.7 Common Debugging Tips

### Tip 1: Use print() to check values

```python
def calculate(x, y):
    print(f"DEBUG: x = {x}, y = {y}")     # Add this
    result = x / y
    print(f"DEBUG: result = {result}")      # Add this
    return result

calculate(10, 0)
```

This shows you what values your variables have right before the error.

### Tip 2: Check types with type()

```python
data = "42"
print(type(data))   # <class 'str'>  -- It is a string, not a number!

# Fix:
data = int(data)
print(type(data))   # <class 'int'>  -- Now it is a number.
```

### Tip 3: Use len() before accessing indices

```python
my_list = [10, 20, 30]

index = 5
if index < len(my_list):
    print(my_list[index])
else:
    print(f"Index {index} is out of range. List has {len(my_list)} items.")
```

### Tip 4: Use .get() for dictionaries

```python
student = {"name": "Alice", "age": 20}

# This crashes if key does not exist:
# print(student["grade"])   # KeyError!

# This returns a default value instead:
print(student.get("grade", "N/A"))   # N/A
```

### Tip 5: Validate input before using it

```python
def safe_divide(a, b):
    if not isinstance(a, (int, float)):
        print("Error: First argument must be a number")
        return None
    if not isinstance(b, (int, float)):
        print("Error: Second argument must be a number")
        return None
    if b == 0:
        print("Error: Cannot divide by zero")
        return None
    return a / b

print(safe_divide(10, 3))    # 3.333...
print(safe_divide(10, 0))    # Error message, returns None
print(safe_divide("a", 3))   # Error message, returns None
```

### Tip 6: Handle errors close to where they happen

```python
# Good: Handle error right where it might occur
def read_config(filename):
    try:
        with open(filename) as f:
            return f.read()
    except FileNotFoundError:
        print(f"Config file '{filename}' not found. Using defaults.")
        return "default settings"

config = read_config("settings.txt")
```

### Tip 7: Rubber duck debugging

Explain your code out loud, line by line, to a rubber duck (or anything). Often, you will find the bug just by explaining what your code is supposed to do.

```
+--------+    "On line 5, I take the input
| (o  o) |     and convert it to an integer...
|  (__/  |     Wait. What if the input is empty?
|  Duck  |     THAT'S the bug!"
+--------+
```

---

## 12.8 Real-World Example: Safe User Input

Here is a complete example that puts everything together.

### Example 9: Robust number input

```python
def get_number(prompt):
    """Keep asking until the user enters a valid number."""
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("That is not a valid number. Please try again.")

def get_integer(prompt, min_val=None, max_val=None):
    """Get an integer within an optional range."""
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}.")
                continue
            return value
        except ValueError:
            print("Please enter a whole number.")

# Using these functions:
age = get_integer("Enter your age (1-120): ", min_val=1, max_val=120)
height = get_number("Enter your height in meters: ")

print(f"Age: {age}, Height: {height}")
```

**Sample interaction:**
```
Enter your age (1-120): abc
Please enter a whole number.
Enter your age (1-120): -5
Value must be at least 1.
Enter your age (1-120): 200
Value must be at most 120.
Enter your age (1-120): 25
Enter your height in meters: tall
That is not a valid number. Please try again.
Enter your height in meters: 1.75
Age: 25, Height: 1.75
```

---

## Common Mistakes

### Mistake 1: Catching too broad an exception

```python
# Bad: This hides ALL errors, even ones you did not expect
try:
    result = do_something()
except:
    pass    # Silently ignore everything

# Good: Catch specific errors
try:
    result = do_something()
except ValueError:
    print("Invalid value!")
except TypeError:
    print("Wrong type!")
```

### Mistake 2: Using try/except instead of fixing the problem

```python
# Bad: Using try/except to avoid thinking
try:
    print(my_list[10])
except IndexError:
    print("Oops")

# Good: Prevent the error in the first place
if len(my_list) > 10:
    print(my_list[10])
else:
    print("List is too short")
```

### Mistake 3: Not reading the error message

```
Most beginners see red text and panic.
STOP. READ THE MESSAGE.
It tells you exactly what went wrong and where.
```

### Mistake 4: Empty except blocks

```python
# Bad: Silently swallowing errors
try:
    data = load_data()
except:
    pass    # What went wrong? Nobody knows!

# Good: At least log the error
try:
    data = load_data()
except Exception as e:
    print(f"Error loading data: {e}")
    data = []
```

### Mistake 5: Putting too much code in the try block

```python
# Bad: Too much code in try — hard to know what caused the error
try:
    file = open("data.txt")
    content = file.read()
    numbers = content.split(",")
    total = sum(int(n) for n in numbers)
    average = total / len(numbers)
except:
    print("Something went wrong")

# Good: Only wrap the risky part
try:
    file = open("data.txt")
except FileNotFoundError:
    print("File not found")
else:
    content = file.read()
    file.close()
    # Process content...
```

---

## Best Practices

1. **Catch specific exceptions.** Use `except ValueError` instead of bare `except`.
2. **Read error messages carefully.** They tell you what went wrong and where.
3. **Use `finally` for cleanup.** Close files, database connections, etc.
4. **Do not silence errors.** Never use `except: pass` unless you have a very good reason.
5. **Validate input early.** Check data before processing it.
6. **Use `else` for success code.** Code that should only run when `try` succeeds goes in `else`.
7. **Keep try blocks small.** Only wrap the code that might actually fail.
8. **Raise exceptions for invalid data.** If your function gets bad input, raise an exception.

---

## Quick Summary

| Concept | What It Does | Example |
|---|---|---|
| `try/except` | Catch and handle errors | `try: ... except ValueError: ...` |
| `else` | Runs if no error occurred | `else: print("Success!")` |
| `finally` | Always runs (cleanup) | `finally: file.close()` |
| `raise` | Create an error on purpose | `raise ValueError("Bad!")` |
| `as e` | Store the error message | `except ValueError as e:` |
| Traceback | Shows where the error happened | Read from bottom to top |

---

## Key Points to Remember

1. Errors are Python telling you something is wrong. They are helpful, not scary.
2. Syntax errors happen before your code runs. Runtime errors happen while it runs.
3. Common errors: SyntaxError, TypeError, NameError, ValueError, IndexError, KeyError, FileNotFoundError.
4. `try/except` catches errors so your program does not crash.
5. Catch specific error types, not everything.
6. `else` runs only when `try` succeeds. `finally` runs no matter what.
7. `raise` lets you create errors on purpose when something should not happen.
8. Read tracebacks from bottom to top.
9. Use print statements and type() to debug.
10. Never use `except: pass` — it hides problems.

---

## Practice Questions

**Question 1:** What is the difference between a SyntaxError and a ValueError?

**Answer:** A SyntaxError means your code has bad grammar — Python cannot even understand it. It happens before the code runs. A ValueError means the code grammar is fine, but you gave a function a value that does not make sense (like `int("hello")`). It happens while the code runs.

**Question 2:** What does the `finally` block do?

**Answer:** The `finally` block runs no matter what — whether an error happened or not. It is used for cleanup tasks like closing files or database connections.

**Question 3:** What is wrong with this code?

```python
try:
    x = int(input("Number: "))
except:
    pass
print(x)
```

**Answer:** Two problems. First, the bare `except: pass` silently swallows all errors without telling the user anything. Second, if an error occurs, `x` is never defined, so `print(x)` will cause a NameError.

**Question 4:** How do you read a traceback?

**Answer:** Read from bottom to top. The very last line tells you what type of error occurred and the error message. The lines above show the chain of function calls that led to the error, with file names and line numbers. The line closest to the bottom is where the error actually happened.

**Question 5:** When should you use `raise`?

**Answer:** Use `raise` when your function receives data that should not be allowed. For example, if a function expects a positive number and gets a negative one, you should raise a ValueError with a clear message explaining what went wrong.

---

## Exercises

### Exercise 1: Safe Calculator

Build a simple calculator that handles all possible errors gracefully.

```python
# Your calculator should:
# 1. Ask for two numbers
# 2. Ask for an operation (+, -, *, /)
# 3. Handle: non-numeric input, division by zero, invalid operation
# 4. Keep running until the user types "quit"
```

**Sample Solution:**

```python
def calculator():
    print("Simple Calculator (type 'quit' to exit)")
    print("-" * 40)

    while True:
        first = input("\nFirst number (or 'quit'): ")
        if first.lower() == "quit":
            print("Goodbye!")
            break

        try:
            num1 = float(first)
        except ValueError:
            print("That is not a valid number!")
            continue

        try:
            num2 = float(input("Second number: "))
        except ValueError:
            print("That is not a valid number!")
            continue

        operation = input("Operation (+, -, *, /): ")

        try:
            if operation == "+":
                result = num1 + num2
            elif operation == "-":
                result = num1 - num2
            elif operation == "*":
                result = num1 * num2
            elif operation == "/":
                result = num1 / num2
            else:
                print(f"Unknown operation: {operation}")
                continue

            print(f"{num1} {operation} {num2} = {result}")

        except ZeroDivisionError:
            print("Cannot divide by zero!")

calculator()
```

### Exercise 2: File Reader with Error Handling

Write a program that reads a file and counts the number of words, lines, and characters. Handle all possible errors.

**Sample Solution:**

```python
import os

def analyze_file(filename):
    if not isinstance(filename, str):
        raise TypeError("Filename must be a string!")

    if not filename.strip():
        raise ValueError("Filename cannot be empty!")

    try:
        with open(filename, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: '{filename}' does not exist.")
        return
    except PermissionError:
        print(f"Error: No permission to read '{filename}'.")
        return

    lines = content.split("\n")
    words = content.split()
    chars = len(content)

    print(f"File: {filename}")
    print(f"Lines: {len(lines)}")
    print(f"Words: {len(words)}")
    print(f"Characters: {chars}")

# Test it:
analyze_file("my_file.txt")
```

### Exercise 3: Validate Student Data

Write a function that validates student data and raises appropriate exceptions.

**Sample Solution:**

```python
def validate_student(name, age, grade):
    errors = []

    if not isinstance(name, str) or len(name.strip()) == 0:
        errors.append("Name must be a non-empty string")

    if not isinstance(age, int):
        errors.append("Age must be an integer")
    elif age < 5 or age > 100:
        errors.append("Age must be between 5 and 100")

    if not isinstance(grade, (int, float)):
        errors.append("Grade must be a number")
    elif grade < 0 or grade > 100:
        errors.append("Grade must be between 0 and 100")

    if errors:
        for error in errors:
            print(f"  - {error}")
        raise ValueError(f"Invalid student data: {len(errors)} error(s)")

    print(f"Student '{name}' is valid!")
    return True

# Test with valid data:
try:
    validate_student("Alice", 20, 95)
except ValueError as e:
    print(e)

# Test with invalid data:
try:
    validate_student("", -1, 200)
except ValueError as e:
    print(e)
```

---

## What Is Next?

You now know how to handle errors and debug your code like a professional. In the next chapter, we will start working with **NumPy** — Python's library for fast math on arrays. This is where we begin moving from basic Python into the tools used for data science and AI.
