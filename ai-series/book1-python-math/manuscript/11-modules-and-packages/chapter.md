# Chapter 11: Modules and Packages

## What You Will Learn

- What modules are and why they exist
- How to import modules using `import`, `from...import`, and `as`
- How to install packages using `pip`
- What virtual environments are and why you need them
- How to use common built-in modules: `math`, `random`, `os`, and `datetime`

## Why This Chapter Matters

Imagine you are building a house. You would not make every single nail, screw, and brick from scratch. You would go to a hardware store and buy ready-made parts. Python works the same way.

Other programmers have already solved thousands of common problems. They put their solutions into **modules** and **packages**. You can use their work instead of writing everything yourself.

This is one of the biggest reasons Python is so popular. There is a module for almost everything — math, dates, files, web scraping, machine learning, and much more.

Without modules, every Python program would be thousands of lines long. With modules, you can do powerful things in just a few lines.

---

## 11.1 What Is a Module?

A module is a file that contains Python code. That is it. Really.

Think of a module like a **toolbox**. A carpenter has a toolbox with hammers, screwdrivers, and saws. Each tool does a specific job. A Python module is a toolbox full of functions, classes, and variables that do specific jobs.

```
+---------------------------+
|       TOOLBOX (Module)    |
+---------------------------+
|  Hammer    (function 1)   |
|  Screwdriver (function 2) |
|  Saw       (function 3)   |
|  Nails     (variable 1)   |
+---------------------------+
```

There are three kinds of modules:

1. **Built-in modules** — Come with Python. Already installed. Free to use.
2. **Third-party modules** — Made by other people. You install them with `pip`.
3. **Your own modules** — Files you write yourself.

---

## 11.2 The `import` Statement

The `import` statement brings a module into your program. It is like opening a toolbox so you can use the tools inside.

### Example 1: Importing the `math` module

```python
import math

result = math.sqrt(25)
print(result)
```

**Expected Output:**
```
5.0
```

**Line-by-line explanation:**

- `import math` — This tells Python: "I want to use the math toolbox."
- `result = math.sqrt(25)` — `math.sqrt()` is a function inside the math module. It calculates the square root. We use `math.` before the function name to say "this function lives inside the math module."
- `print(result)` — Prints the answer: 5.0.

Think of it like this:

```
+---------------------+
|  Your Program       |
|                     |
|  "Hey math module,  |
|   what is the       |
|   square root of    |
|   25?"              |
|                     |
|  math.sqrt(25)      |
|  Answer: 5.0        |
+---------------------+
```

### Example 2: Using multiple functions from a module

```python
import math

print(math.pi)
print(math.ceil(4.2))
print(math.floor(4.8))
print(math.pow(2, 3))
```

**Expected Output:**
```
3.141592653589793
5
4
8.0
```

**Line-by-line explanation:**

- `math.pi` — This is a variable (not a function) inside the math module. It holds the value of pi.
- `math.ceil(4.2)` — Rounds UP to the nearest whole number. 4.2 becomes 5.
- `math.floor(4.8)` — Rounds DOWN to the nearest whole number. 4.8 becomes 4.
- `math.pow(2, 3)` — Calculates 2 raised to the power of 3. That is 2 * 2 * 2 = 8.

---

## 11.3 The `from...import` Statement

Sometimes you only need one tool from the toolbox. You do not want to carry the whole toolbox around.

The `from...import` statement lets you grab specific items from a module.

### Example 3: Importing specific items

```python
from math import sqrt, pi

result = sqrt(36)
print(result)
print(pi)
```

**Expected Output:**
```
6.0
3.141592653589793
```

**Line-by-line explanation:**

- `from math import sqrt, pi` — This says: "From the math toolbox, I only want the sqrt function and the pi variable."
- `result = sqrt(36)` — Notice we write `sqrt(36)`, not `math.sqrt(36)`. We do not need the `math.` prefix anymore because we imported `sqrt` directly.
- `print(pi)` — Same thing. We write `pi`, not `math.pi`.

```
Full import:           from...import:

import math            from math import sqrt

math.sqrt(25)          sqrt(25)
^^^^ required          No prefix needed!
```

### Example 4: Importing everything (use with caution)

```python
from math import *

print(sqrt(49))
print(pi)
print(ceil(3.1))
```

**Expected Output:**
```
7.0
3.141592653589793
4
```

The `*` means "import everything." This works, but it is **not recommended** for big programs. Why? Because you cannot tell where each function came from. It can cause confusion.

---

## 11.4 The `as` Keyword (Aliases)

Sometimes module names are long. Typing them over and over is annoying. The `as` keyword lets you create a **nickname** (alias) for a module.

### Example 5: Using aliases

```python
import math as m

print(m.sqrt(100))
print(m.pi)
```

**Expected Output:**
```
10.0
3.141592653589793
```

**Line-by-line explanation:**

- `import math as m` — Import the math module but call it `m` instead. It is a shorter name.
- `m.sqrt(100)` — Use `m.` instead of `math.`. Same function, shorter name.

### Example 6: Aliasing specific imports

```python
from math import sqrt as square_root

print(square_root(64))
```

**Expected Output:**
```
8.0
```

You can rename individual functions too. This is useful when function names are confusing or when two modules have functions with the same name.

```
Common aliases you will see in the wild:

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

These are so common that everyone uses them.
```

---

## 11.5 Creating Your Own Module

Any Python file can be a module. Let me show you.

### Example 7: Making a simple module

**Step 1:** Create a file called `my_tools.py`:

```python
# my_tools.py

def greet(name):
    return f"Hello, {name}!"

def add(a, b):
    return a + b

PI = 3.14159
```

**Step 2:** Use it in another file (in the same folder):

```python
# main.py

import my_tools

print(my_tools.greet("Alice"))
print(my_tools.add(5, 3))
print(my_tools.PI)
```

**Expected Output:**
```
Hello, Alice!
8
3.14159
```

```
Folder structure:

my_project/
    my_tools.py    <-- Your module
    main.py        <-- Your program that uses the module
```

**Line-by-line explanation:**

- `import my_tools` — Python looks for a file called `my_tools.py` in the same folder.
- `my_tools.greet("Alice")` — Calls the `greet` function from your module.
- `my_tools.add(5, 3)` — Calls the `add` function.
- `my_tools.PI` — Accesses the `PI` variable.

---

## 11.6 `pip` — The App Store for Python

Your phone has an app store where you download apps. Python has something similar called **pip**. It stands for "Pip Installs Packages."

`pip` connects to the **Python Package Index (PyPI)** — a website with over 400,000 packages made by people around the world.

```
+---------------------------+
|      PyPI (App Store)     |
+---------------------------+
|  numpy     - Fast math    |
|  pandas    - Data tables  |
|  requests  - Web stuff    |
|  flask     - Websites     |
|  ...400,000+ packages     |
+---------------------------+
        |
        | pip install numpy
        v
+---------------------------+
|    Your Computer          |
|    numpy is now installed |
+---------------------------+
```

### Using pip

Open your **terminal** (Command Prompt on Windows, Terminal on Mac/Linux) and type:

```bash
# Install a package
pip install numpy

# Install a specific version
pip install numpy==1.24.0

# Upgrade a package
pip install --upgrade numpy

# Uninstall a package
pip uninstall numpy

# See what is installed
pip list

# See details about a package
pip show numpy
```

### Example 8: Installing and using a package

```bash
pip install requests
```

```python
import requests

response = requests.get("https://httpbin.org/json")
print(response.status_code)
```

**Expected Output:**
```
200
```

**Line-by-line explanation:**

- `pip install requests` — Downloads and installs the `requests` package.
- `import requests` — Brings the package into your program.
- `requests.get(...)` — Makes a request to a website. Like opening a URL in your browser, but from Python.
- `response.status_code` — 200 means "OK, it worked." (Like a thumbs up from the website.)

---

## 11.7 Virtual Environments (venv)

### The Problem

Imagine you have two projects:

- Project A needs `numpy version 1.21`
- Project B needs `numpy version 1.24`

If you install numpy once on your computer, you can only have ONE version. This causes problems.

### The Solution: Virtual Environments

A virtual environment is like giving each project its own **private room** with its own packages. What happens in one room does not affect the other.

```
Your Computer
+---------------------------------------------------+
|                                                   |
|   Project A's Room         Project B's Room       |
|   +-----------------+     +-----------------+    |
|   | numpy 1.21      |     | numpy 1.24      |    |
|   | pandas 1.3      |     | pandas 2.0      |    |
|   | requests 2.26   |     | flask 2.3       |    |
|   +-----------------+     +-----------------+    |
|                                                   |
|   No conflicts! Each project has its own stuff.   |
+---------------------------------------------------+
```

### How to Create a Virtual Environment

**Step 1:** Open your terminal and go to your project folder.

```bash
cd my_project
```

**Step 2:** Create the virtual environment.

```bash
python -m venv myenv
```

This creates a folder called `myenv` that holds all the private packages.

**Step 3:** Activate the virtual environment.

```bash
# On Windows:
myenv\Scripts\activate

# On Mac/Linux:
source myenv/bin/activate
```

When activated, you will see the environment name in your terminal:

```
(myenv) $
```

**Step 4:** Install packages (they go into the virtual environment only).

```bash
pip install numpy pandas
```

**Step 5:** When you are done, deactivate it.

```bash
deactivate
```

### Saving and Sharing Your Package List

```bash
# Save the list of installed packages
pip freeze > requirements.txt

# Someone else can install the same packages
pip install -r requirements.txt
```

The `requirements.txt` file looks like this:

```
numpy==1.24.0
pandas==2.0.0
requests==2.28.0
```

It is like a shopping list of packages.

---

## 11.8 Common Built-in Modules

Python comes with many useful modules. You do not need to install them. They are already there.

### The `math` Module

For mathematical operations.

```python
import math

# Square root
print(math.sqrt(144))       # 12.0

# Power
print(math.pow(2, 10))      # 1024.0

# Rounding
print(math.ceil(4.1))       # 5   (round up)
print(math.floor(4.9))      # 4   (round down)

# Constants
print(math.pi)              # 3.141592653589793
print(math.e)               # 2.718281828459045

# Logarithm
print(math.log(100, 10))    # 2.0  (log base 10 of 100)

# Trigonometry (uses radians)
print(math.sin(math.pi / 2))  # 1.0
print(math.cos(0))             # 1.0

# Convert degrees to radians
angle = math.radians(90)
print(math.sin(angle))      # 1.0
```

**Expected Output:**
```
12.0
1024.0
5
4
3.141592653589793
2.718281828459045
2.0
1.0
1.0
1.0
```

### The `random` Module

For generating random numbers. Great for games, simulations, and testing.

```python
import random

# Random float between 0 and 1
print(random.random())

# Random integer between 1 and 10 (inclusive)
print(random.randint(1, 10))

# Random choice from a list
colors = ["red", "blue", "green", "yellow"]
print(random.choice(colors))

# Shuffle a list (changes the original list)
cards = [1, 2, 3, 4, 5]
random.shuffle(cards)
print(cards)

# Random sample (pick N items without repeats)
winners = random.sample(range(1, 50), 6)
print(winners)
```

**Expected Output (yours will differ — it is random!):**
```
0.7234567891234
7
blue
[3, 1, 5, 2, 4]
[12, 34, 7, 45, 23, 1]
```

### The `os` Module

For working with your operating system — files, folders, paths.

```python
import os

# Get the current working directory
print(os.getcwd())

# List files in a directory
print(os.listdir("."))

# Check if a file exists
print(os.path.exists("my_file.txt"))

# Join path parts (works on any operating system)
path = os.path.join("folder", "subfolder", "file.txt")
print(path)

# Get the file name from a path
print(os.path.basename("/home/user/data.csv"))

# Get the folder from a path
print(os.path.dirname("/home/user/data.csv"))

# Create a new directory
# os.mkdir("new_folder")

# Get file size in bytes
# print(os.path.getsize("my_file.txt"))
```

**Expected Output (depends on your system):**
```
/home/user/my_project
['main.py', 'data.csv', 'my_tools.py']
False
folder/subfolder/file.txt
data.csv
/home/user
```

### The `datetime` Module

For working with dates and times.

```python
from datetime import datetime, date, timedelta

# Current date and time
now = datetime.now()
print(now)

# Just today's date
today = date.today()
print(today)

# Create a specific date
birthday = date(1995, 6, 15)
print(birthday)

# Format dates as strings
print(now.strftime("%B %d, %Y"))     # March 25, 2026
print(now.strftime("%H:%M:%S"))       # 14:30:45

# Date arithmetic
tomorrow = today + timedelta(days=1)
print(tomorrow)

next_week = today + timedelta(weeks=1)
print(next_week)

# Difference between dates
days_alive = today - birthday
print(f"Days alive: {days_alive.days}")
```

**Expected Output (depends on when you run it):**
```
2026-03-25 14:30:45.123456
2026-03-25
1995-06-15
March 25, 2026
14:30:45
2026-03-26
2026-04-01
Days alive: 11241
```

**Line-by-line explanation:**

- `datetime.now()` — Gets the current date AND time.
- `date.today()` — Gets just today's date (no time).
- `date(1995, 6, 15)` — Creates a date: year, month, day.
- `strftime()` — Formats a date as a string. `%B` = full month name, `%d` = day, `%Y` = four-digit year.
- `timedelta(days=1)` — Represents a duration of time. You can add or subtract it from dates.

Common format codes:

```
+--------+------------------+----------+
| Code   | Meaning          | Example  |
+--------+------------------+----------+
| %Y     | Year (4 digits)  | 2026     |
| %m     | Month (01-12)    | 03       |
| %d     | Day (01-31)      | 25       |
| %H     | Hour (00-23)     | 14       |
| %M     | Minute (00-59)   | 30       |
| %S     | Second (00-59)   | 45       |
| %B     | Month name       | March    |
| %A     | Day name         | Tuesday  |
+--------+------------------+----------+
```

---

## 11.9 How Python Finds Modules

When you write `import something`, Python searches in this order:

```
Search Order:
+------------------------------------------+
| 1. Current directory                     |
|    (where your script is)                |
+------------------------------------------+
          |  Not found? Keep looking...
          v
+------------------------------------------+
| 2. Built-in modules                      |
|    (math, os, random, etc.)              |
+------------------------------------------+
          |  Not found? Keep looking...
          v
+------------------------------------------+
| 3. Installed packages                    |
|    (numpy, pandas, etc.)                 |
+------------------------------------------+
          |  Not found?
          v
+------------------------------------------+
| 4. ModuleNotFoundError!                  |
|    "No module named 'something'"         |
+------------------------------------------+
```

You can see the search paths with:

```python
import sys
print(sys.path)
```

---

## Common Mistakes

### Mistake 1: Naming your file the same as a module

```python
# If your file is named "math.py":
import math
print(math.sqrt(25))
# ERROR! Python imports YOUR file instead of the real math module.
```

**Fix:** Never name your files the same as built-in modules. Do not create files named `math.py`, `random.py`, `os.py`, etc.

### Mistake 2: Forgetting to install a package

```python
import numpy
# ModuleNotFoundError: No module named 'numpy'
```

**Fix:** Run `pip install numpy` in your terminal first.

### Mistake 3: Installing packages globally instead of in a virtual environment

```bash
# Bad (installs for your whole computer):
pip install numpy

# Good (installs only for this project):
python -m venv myenv
source myenv/bin/activate
pip install numpy
```

### Mistake 4: Using `from module import *` in large programs

```python
from math import *
from numpy import *

# Both have a 'sqrt' function. Which one is Python using?
# It is confusing!
```

**Fix:** Import specific items or use the full module name.

### Mistake 5: Forgetting the module prefix

```python
import math

# Wrong:
result = sqrt(25)    # NameError: name 'sqrt' is not defined

# Right:
result = math.sqrt(25)
```

---

## Best Practices

1. **Use virtual environments for every project.** Always. No exceptions.
2. **Import at the top of your file.** Put all imports at the beginning of your program, not scattered throughout.
3. **Be specific with imports.** Use `from math import sqrt` instead of `from math import *`.
4. **Use standard aliases.** Use `import numpy as np`, `import pandas as pd`. Everyone knows these.
5. **Keep a `requirements.txt` file.** So others can install the same packages.
6. **Group your imports.** Put built-in modules first, then third-party, then your own:

```python
# Built-in modules
import os
import math
from datetime import datetime

# Third-party modules
import numpy as np
import pandas as pd

# Your own modules
from my_tools import greet
```

---

## Quick Summary

| Concept | What It Does | Example |
|---|---|---|
| `import` | Loads a whole module | `import math` |
| `from...import` | Loads specific items | `from math import sqrt` |
| `as` | Creates an alias | `import numpy as np` |
| `pip install` | Downloads a package | `pip install numpy` |
| `venv` | Creates isolated environment | `python -m venv myenv` |
| Built-in module | Comes with Python | `math`, `random`, `os` |
| Third-party module | Installed with pip | `numpy`, `pandas` |

---

## Key Points to Remember

1. A module is just a Python file with reusable code.
2. Use `import` to bring modules into your program.
3. `from...import` lets you grab specific items without the module prefix.
4. `as` gives modules or functions shorter names (aliases).
5. `pip` installs third-party packages from the internet.
6. Virtual environments keep project dependencies separate.
7. Always use virtual environments for real projects.
8. Python has many useful built-in modules: `math`, `random`, `os`, `datetime`.
9. Never name your files the same as a module.
10. Put all imports at the top of your file.

---

## Practice Questions

**Question 1:** What is the difference between `import math` and `from math import sqrt`?

**Answer:** `import math` loads the entire module. You must use `math.sqrt()` to call functions. `from math import sqrt` loads only the `sqrt` function. You can call it directly as `sqrt()` without the `math.` prefix.

**Question 2:** What does `pip install requests` do?

**Answer:** It downloads and installs the `requests` package from PyPI (Python Package Index) onto your computer so you can use it in your Python programs.

**Question 3:** Why should you use virtual environments?

**Answer:** Virtual environments keep packages separate for each project. Without them, different projects might need different versions of the same package, causing conflicts. Each virtual environment is like a private room with its own packages.

**Question 4:** What is wrong with this code?

```python
import math as m
print(math.sqrt(16))
```

**Answer:** After using `as m`, you must use `m`, not `math`. The correct code is `print(m.sqrt(16))`.

**Question 5:** What happens if you create a file called `random.py` in your project folder?

**Answer:** Python will import YOUR `random.py` file instead of the built-in `random` module. This will cause errors because your file does not have the functions that the real `random` module has.

---

## Exercises

### Exercise 1: Random Password Generator

Write a program that generates a random password of a given length. Use the `random` and `string` modules.

**Hint:**

```python
import random
import string

# string.ascii_letters gives all letters (a-z, A-Z)
# string.digits gives all digits (0-9)
# string.punctuation gives special characters (!@#$...)

# Use random.choice() to pick random characters
```

**Sample Solution:**

```python
import random
import string

def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ""
    for i in range(length):
        password += random.choice(characters)
    return password

print(generate_password(12))
print(generate_password(8))
```

### Exercise 2: Days Until Your Birthday

Write a program that asks for a birthday and calculates how many days until the next birthday.

**Sample Solution:**

```python
from datetime import date

birth_month = int(input("Enter your birth month (1-12): "))
birth_day = int(input("Enter your birth day (1-31): "))

today = date.today()

# Try this year first
next_birthday = date(today.year, birth_month, birth_day)

# If the birthday already passed this year, use next year
if next_birthday < today:
    next_birthday = date(today.year + 1, birth_month, birth_day)

days_left = (next_birthday - today).days
print(f"Days until your next birthday: {days_left}")
```

### Exercise 3: File Explorer

Write a program that lists all files in the current directory and shows their sizes.

**Sample Solution:**

```python
import os

current_dir = os.getcwd()
print(f"Files in: {current_dir}\n")

for item in os.listdir(current_dir):
    full_path = os.path.join(current_dir, item)
    if os.path.isfile(full_path):
        size = os.path.getsize(full_path)
        print(f"  {item:30s} {size:>10,} bytes")
    else:
        print(f"  {item:30s} [FOLDER]")
```

---

## What Is Next?

Now you know how to use other people's code through modules and packages. But what happens when things go wrong? In the next chapter, you will learn about **error handling** — how to catch problems, fix them, and make your programs more reliable.
