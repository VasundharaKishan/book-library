# Chapter 8: Functions — Reusable Recipes for Your Code

## What You Will Learn

- What functions are and why they matter
- How to define functions using `def`
- The difference between parameters and arguments
- How to return values from functions
- How to use default parameters
- What `*args` and `**kwargs` do
- How scope works (local vs global variables)
- What lambda functions are
- How to write docstrings
- Why functions are essential for code reuse

## Why This Chapter Matters

Imagine you bake cookies every weekend. Would you reinvent the recipe each time? No. You write the recipe once and follow it every time.

Functions are recipes for your code. You write the instructions once. Then you use them whenever you need them.

Without functions, your code would be a long, messy, repetitive list of instructions. With functions, your code is organized, reusable, and easy to understand.

In AI and machine learning, functions are everywhere. You will write functions to:
- Clean data
- Calculate metrics
- Build model layers
- Process results

Learning functions is one of the most important steps in your programming journey.

---

## 8.1 What Is a Function?

A function is a **named block of code** that does a specific task. You define it once. You use it as many times as you want.

```
+---------------------------------------------+
|              Function = Recipe               |
+---------------------------------------------+
|                                              |
|  Recipe Name:  make_sandwich                 |
|                                              |
|  Ingredients:  bread, filling  (parameters)  |
|                                              |
|  Steps:                                      |
|    1. Take two slices of bread               |
|    2. Add the filling                        |
|    3. Put slices together                    |
|                                              |
|  Result:       a sandwich      (return)      |
+---------------------------------------------+
```

### Your First Function

```python
def greet():
    print("Hello, World!")

# Call the function
greet()
greet()
greet()
```

**Expected Output:**
```
Hello, World!
Hello, World!
Hello, World!
```

**Line-by-line explanation:**
- **Line 1:** `def` is the keyword to **define** a function. `greet` is the function name. The parentheses `()` hold parameters (none in this case). The colon `:` starts the function body.
- **Line 2:** This is the function body. It is indented. Everything indented under `def` belongs to the function.
- **Line 5-7:** We **call** the function by writing its name followed by `()`. Each call runs the code inside the function.

```
+----------------------------------------------+
|  Defining vs Calling a Function               |
+----------------------------------------------+
|                                               |
|  def greet():       <-- DEFINE (create it)    |
|      print("Hi!")                             |
|                                               |
|  greet()            <-- CALL (use it)         |
|                                               |
|  You define ONCE. You call MANY times.        |
+----------------------------------------------+
```

---

## 8.2 Parameters and Arguments

A **parameter** is a variable in the function definition. It is like a placeholder.

An **argument** is the actual value you pass when calling the function.

Think of it this way: A parameter is an empty box with a label. An argument is what you put in the box.

```python
def greet(name):        # 'name' is a PARAMETER
    print(f"Hello, {name}!")

greet("Alice")          # "Alice" is an ARGUMENT
greet("Bob")            # "Bob" is an ARGUMENT
```

**Expected Output:**
```
Hello, Alice!
Hello, Bob!
```

**Line-by-line explanation:**
- **Line 1:** `name` is a parameter. It is a placeholder. It does not have a value yet.
- **Line 4:** We call the function with `"Alice"`. Now `name` equals `"Alice"` inside the function.
- **Line 5:** We call it again with `"Bob"`. Now `name` equals `"Bob"`.

### Multiple Parameters

```python
def introduce(name, age, city):
    print(f"My name is {name}.")
    print(f"I am {age} years old.")
    print(f"I live in {city}.")
    print()

introduce("Alice", 25, "New York")
introduce("Bob", 30, "London")
```

**Expected Output:**
```
My name is Alice.
I am 25 years old.
I live in New York.

My name is Bob.
I am 30 years old.
I live in London.

```

```
+-----------------------------------------------+
|  Parameters vs Arguments                       |
+-----------------------------------------------+
|                                                |
|  def add(a, b):     <-- a, b are PARAMETERS   |
|      return a + b        (in the definition)   |
|                                                |
|  add(3, 5)           <-- 3, 5 are ARGUMENTS   |
|                          (in the call)         |
+-----------------------------------------------+
```

### Keyword Arguments

You can also pass arguments by name. This makes your code clearer.

```python
def describe_pet(name, animal_type):
    print(f"{name} is a {animal_type}.")

# Positional arguments (order matters)
describe_pet("Buddy", "dog")

# Keyword arguments (order does NOT matter)
describe_pet(animal_type="cat", name="Whiskers")
```

**Expected Output:**
```
Buddy is a dog.
Whiskers is a cat.
```

**Line-by-line explanation:**
- **Line 5:** Positional: "Buddy" goes to `name`, "dog" goes to `animal_type`. Order matters.
- **Line 8:** Keyword: We say exactly which parameter gets which value. Order does not matter.

---

## 8.3 Return Values

A function can **give back** a result using the `return` keyword.

Think of a vending machine. You put in money (argument). You press a button (call the function). A drink comes out (return value).

```python
def add(a, b):
    result = a + b
    return result

# Use the return value
total = add(3, 5)
print("Total:", total)

# You can also use it directly
print("Sum:", add(10, 20))
```

**Expected Output:**
```
Total: 8
Sum: 30
```

**Line-by-line explanation:**
- **Line 3:** `return result` sends the value back to wherever the function was called.
- **Line 6:** The returned value (8) is stored in `total`.
- **Line 9:** You can use the function call directly in `print()`.

### Returning Multiple Values

Python lets you return multiple values. They come back as a tuple.

```python
def min_max(numbers):
    return min(numbers), max(numbers)

lowest, highest = min_max([4, 2, 9, 1, 7])
print(f"Lowest: {lowest}")
print(f"Highest: {highest}")
```

**Expected Output:**
```
Lowest: 1
Highest: 9
```

**Line-by-line explanation:**
- **Line 2:** Return two values separated by a comma. Python packs them into a tuple.
- **Line 4:** Tuple unpacking. The first value goes to `lowest`, the second to `highest`.

### Functions Without Return

If a function has no `return` statement, it returns `None`.

```python
def say_hello(name):
    print(f"Hello, {name}!")

result = say_hello("Alice")
print("Return value:", result)
```

**Expected Output:**
```
Hello, Alice!
Return value: None
```

---

## 8.4 Default Parameters

You can give parameters **default values**. If the caller does not provide an argument, the default is used.

```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

# Use the default greeting
greet("Alice")

# Override the default
greet("Bob", "Good morning")
```

**Expected Output:**
```
Hello, Alice!
Good morning, Bob!
```

**Line-by-line explanation:**
- **Line 1:** `greeting="Hello"` sets a default value. If no greeting is given, "Hello" is used.
- **Line 5:** Only `name` is provided. `greeting` uses its default "Hello".
- **Line 8:** Both are provided. "Good morning" replaces the default.

```python
def create_profile(name, age, job="Student", city="Unknown"):
    print(f"Name: {name}, Age: {age}, Job: {job}, City: {city}")

create_profile("Alice", 20)
create_profile("Bob", 25, "Engineer")
create_profile("Charlie", 30, "Designer", "Paris")
```

**Expected Output:**
```
Name: Alice, Age: 20, Job: Student, City: Unknown
Name: Bob, Age: 25, Job: Engineer, City: Unknown
Name: Charlie, Age: 30, Job: Designer, City: Paris
```

```
+-----------------------------------------------+
|  Rule for Default Parameters:                  |
|                                                |
|  Parameters WITH defaults must come AFTER      |
|  parameters WITHOUT defaults.                  |
|                                                |
|  CORRECT:  def f(a, b, c=10)                  |
|  WRONG:    def f(a, c=10, b)   <-- Error!     |
+-----------------------------------------------+
```

---

## 8.5 *args and **kwargs — Flexible Arguments

Sometimes you do not know how many arguments a function will receive. Python has two special tools for this.

### *args — Variable Number of Arguments

`*args` collects extra positional arguments into a tuple.

```python
def add_all(*numbers):
    total = sum(numbers)
    return total

print(add_all(1, 2))
print(add_all(1, 2, 3))
print(add_all(1, 2, 3, 4, 5))
```

**Expected Output:**
```
3
6
15
```

**Line-by-line explanation:**
- **Line 1:** `*numbers` means "accept any number of arguments and put them in a tuple called `numbers`."
- **Line 5-7:** We can call the function with 2, 3, or 5 arguments. It works for any number.

```python
# What does *args actually look like?
def show_args(*args):
    print(f"Type: {type(args)}")
    print(f"Values: {args}")

show_args(1, "hello", True)
```

**Expected Output:**
```
Type: <class 'tuple'>
Values: (1, 'hello', True)
```

### **kwargs — Variable Keyword Arguments

`**kwargs` collects extra keyword arguments into a dictionary.

```python
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

print("Person 1:")
print_info(name="Alice", age=25, city="NYC")

print("\nPerson 2:")
print_info(name="Bob", job="Engineer")
```

**Expected Output:**
```
Person 1:
  name: Alice
  age: 25
  city: NYC

Person 2:
  name: Bob
  job: Engineer
```

**Line-by-line explanation:**
- **Line 1:** `**kwargs` means "collect any keyword arguments into a dictionary."
- **Line 6:** We pass three keyword arguments. Inside the function, `kwargs` is `{"name": "Alice", "age": 25, "city": "NYC"}`.

### Using Both Together

```python
def flexible(required, *args, **kwargs):
    print(f"Required: {required}")
    print(f"Extra positional: {args}")
    print(f"Extra keyword: {kwargs}")

flexible("hello", 1, 2, 3, color="red", size="large")
```

**Expected Output:**
```
Required: hello
Extra positional: (1, 2, 3)
Extra keyword: {'color': 'red', 'size': 'large'}
```

```
+---------------------------------------------------+
|  *args and **kwargs Summary                        |
+---------------------------------------------------+
|                                                    |
|  *args    -> collects extra positional arguments   |
|              stored as a TUPLE                     |
|              Example: def f(*args)                 |
|                                                    |
|  **kwargs -> collects extra keyword arguments       |
|              stored as a DICTIONARY                |
|              Example: def f(**kwargs)              |
|                                                    |
|  Order:   def f(regular, *args, **kwargs)          |
+---------------------------------------------------+
```

---

## 8.6 Scope — Local vs Global Variables

**Scope** determines where a variable can be used. Think of it like rooms in a house. A variable created inside a room (function) stays in that room.

### Local Variables

```python
def my_function():
    local_var = "I am local"
    print("Inside function:", local_var)

my_function()

# This will cause an error:
try:
    print(local_var)
except NameError as e:
    print("Error:", e)
```

**Expected Output:**
```
Inside function: I am local
Error: name 'local_var' is not defined
```

**Line-by-line explanation:**
- **Line 2:** `local_var` is created inside the function. It only exists inside the function.
- **Line 9:** Outside the function, `local_var` does not exist. Python raises a `NameError`.

### Global Variables

```python
global_var = "I am global"

def my_function():
    print("Inside function:", global_var)

my_function()
print("Outside function:", global_var)
```

**Expected Output:**
```
Inside function: I am global
Outside function: I am global
```

**Line-by-line explanation:**
- **Line 1:** `global_var` is created outside any function. It is global.
- **Line 4:** Functions can READ global variables.

### The Scope Rule

```
+-----------------------------------------------+
|  Scope Rule: LEGB                              |
+-----------------------------------------------+
|                                                |
|  L - Local:     Inside the current function    |
|  E - Enclosing: Inside an outer function       |
|  G - Global:    At the top level of the file   |
|  B - Built-in:  Python's built-in names        |
|                                                |
|  Python searches for variables in this order.  |
|  It stops when it finds the first match.       |
+-----------------------------------------------+
```

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print("Inner sees:", x)

    inner()
    print("Outer sees:", x)

outer()
print("Global sees:", x)
```

**Expected Output:**
```
Inner sees: local
Outer sees: enclosing
Global sees: global
```

### Modifying Global Variables (Use Sparingly)

```python
counter = 0

def increment():
    global counter   # Tell Python we want the GLOBAL counter
    counter += 1

increment()
increment()
increment()
print("Counter:", counter)
```

**Expected Output:**
```
Counter: 3
```

**Line-by-line explanation:**
- **Line 4:** The `global` keyword tells Python: "I want to modify the global variable, not create a local one."
- **Important:** Avoid using `global` when possible. It makes code harder to understand. Instead, pass values as arguments and return results.

---

## 8.7 Lambda Functions — Quick One-Liners

A **lambda** is a small, anonymous function written in one line.

Think of it as a sticky note with a quick instruction, versus a full recipe card.

```python
# Regular function
def double(x):
    return x * 2

# Same thing as a lambda
double_lambda = lambda x: x * 2

print(double(5))
print(double_lambda(5))
```

**Expected Output:**
```
10
10
```

**Line-by-line explanation:**
- **Line 6:** `lambda x: x * 2` is a function that takes `x` and returns `x * 2`. No `def`, no `return` keyword, no name needed.

### When Lambdas Are Useful

Lambdas are most useful when you need a quick function for a short task.

```python
# Sorting a list of tuples by the second item
students = [("Alice", 90), ("Bob", 75), ("Charlie", 88)]

# Sort by grade (second item in each tuple)
students_sorted = sorted(students, key=lambda s: s[1])
print("By grade:", students_sorted)

# Sort by name (first item)
students_sorted = sorted(students, key=lambda s: s[0])
print("By name:", students_sorted)
```

**Expected Output:**
```
By grade: [('Bob', 75), ('Charlie', 88), ('Alice', 90)]
By name: [('Alice', 90), ('Bob', 75), ('Charlie', 88)]
```

**Line-by-line explanation:**
- **Line 5:** `sorted()` can take a `key` argument. The lambda tells it: "For each student `s`, use `s[1]` (the grade) to decide the order."
- **Line 9:** Same idea, but sort by `s[0]` (the name).

```python
# Using lambda with map() and filter()
numbers = [1, 2, 3, 4, 5]

# Double each number
doubled = list(map(lambda x: x * 2, numbers))
print("Doubled:", doubled)

# Keep only even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("Evens:", evens)
```

**Expected Output:**
```
Doubled: [2, 4, 6, 8, 10]
Evens: [2, 4]
```

```
+-----------------------------------------------+
|  Lambda vs Regular Function                    |
+-----------------------------------------------+
|                                                |
|  Regular:                                      |
|    def square(x):                              |
|        return x ** 2                           |
|                                                |
|  Lambda:                                       |
|    square = lambda x: x ** 2                   |
|                                                |
|  Use lambda for: short, simple operations      |
|  Use def for: anything more complex            |
+-----------------------------------------------+
```

---

## 8.8 Docstrings — Documenting Your Functions

A **docstring** is a string that describes what a function does. It goes right after the `def` line.

```python
def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.

    Parameters:
        numbers (list): A list of numbers.

    Returns:
        float: The average of the numbers.
    """
    return sum(numbers) / len(numbers)

# Use the function
result = calculate_average([10, 20, 30, 40, 50])
print("Average:", result)

# View the docstring
print("\nDocstring:")
print(calculate_average.__doc__)
```

**Expected Output:**
```
Average: 30.0

Docstring:

    Calculate the average of a list of numbers.

    Parameters:
        numbers (list): A list of numbers.

    Returns:
        float: The average of the numbers.

```

**Line-by-line explanation:**
- **Lines 2-10:** The docstring. It uses triple quotes `"""`. It describes what the function does, what it takes, and what it returns.
- **Line 19:** `.__doc__` lets you access the docstring. This is how Python's `help()` function works.

```
+-----------------------------------------------+
|  Good Docstring Template:                      |
+-----------------------------------------------+
|                                                |
|  """                                           |
|  Short description of what the function does.  |
|                                                |
|  Parameters:                                   |
|      param1 (type): Description.               |
|      param2 (type): Description.               |
|                                                |
|  Returns:                                      |
|      type: Description of return value.        |
|  """                                           |
+-----------------------------------------------+
```

---

## 8.9 Why Functions Matter for Code Reuse

### Without Functions (Repetitive Code)

```python
# Calculate area of 3 rectangles without functions
width1, height1 = 5, 3
area1 = width1 * height1
print(f"Rectangle 1: {width1}x{height1} = {area1}")

width2, height2 = 8, 4
area2 = width2 * height2
print(f"Rectangle 2: {width2}x{height2} = {area2}")

width3, height3 = 10, 6
area3 = width3 * height3
print(f"Rectangle 3: {width3}x{height3} = {area3}")
```

### With Functions (Clean and Reusable)

```python
def rectangle_area(width, height):
    """Calculate and display the area of a rectangle."""
    area = width * height
    print(f"Rectangle: {width}x{height} = {area}")
    return area

# Now it is clean and easy
rectangle_area(5, 3)
rectangle_area(8, 4)
rectangle_area(10, 6)
```

**Expected Output:**
```
Rectangle: 5x3 = 15
Rectangle: 8x4 = 32
Rectangle: 10x6 = 60
```

### Real-World Example: Data Processing

```python
def clean_data(raw_values):
    """Remove negative values and return sorted list."""
    cleaned = [v for v in raw_values if v >= 0]
    cleaned.sort()
    return cleaned

def calculate_stats(values):
    """Calculate basic statistics."""
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values)
    }

# Use the functions together
raw_data = [45, -3, 82, 67, -1, 91, 23, -8, 55, 73]
print("Raw data:", raw_data)

clean = clean_data(raw_data)
print("Cleaned:", clean)

stats = calculate_stats(clean)
print("Statistics:")
for key, value in stats.items():
    print(f"  {key}: {value}")
```

**Expected Output:**
```
Raw data: [45, -3, 82, 67, -1, 91, 23, -8, 55, 73]
Cleaned: [23, 45, 55, 67, 73, 82, 91]
Statistics:
  count: 7
  mean: 62.285714285714285
  min: 23
  max: 91
```

---

## 8.10 Putting It All Together

```python
def create_student(name, *grades, **info):
    """
    Create a student record with grades and extra info.

    Parameters:
        name (str): Student name.
        *grades: Variable number of grade values.
        **info: Additional student information.

    Returns:
        dict: A dictionary with student data.
    """
    student = {
        "name": name,
        "grades": list(grades),
        "average": sum(grades) / len(grades) if grades else 0,
        **info
    }
    return student

# Create students
alice = create_student("Alice", 90, 85, 92, year=2, major="CS")
bob = create_student("Bob", 78, 82, 88, year=1)

print("Alice:", alice)
print("Bob:", bob)
print(f"\nAlice's average: {alice['average']:.1f}")
print(f"Bob's average: {bob['average']:.1f}")
```

**Expected Output:**
```
Alice: {'name': 'Alice', 'grades': [90, 85, 92], 'average': 89.0, 'year': 2, 'major': 'CS'}
Bob: {'name': 'Bob', 'grades': [78, 82, 88], 'average': 82.66666666666667, 'year': 1}
Alice's average: 89.0
Bob's average: 82.7
```

---

## Common Mistakes

### Mistake 1: Forgetting Parentheses When Calling

```python
def greet():
    return "Hello!"

# WRONG - this prints the function object, not the result
print(greet)

# RIGHT - call the function with ()
print(greet())
```

**Expected Output:**
```
<function greet at 0x...>
Hello!
```

### Mistake 2: Forgetting to Return

```python
# WRONG - forgot return
def add_wrong(a, b):
    result = a + b
    # Oops, no return!

# RIGHT
def add_right(a, b):
    result = a + b
    return result

print("Wrong:", add_wrong(3, 5))
print("Right:", add_right(3, 5))
```

**Expected Output:**
```
Wrong: None
Right: 8
```

### Mistake 3: Using a Mutable Default Argument

```python
# WRONG - the list is shared between calls!
def add_item_wrong(item, my_list=[]):
    my_list.append(item)
    return my_list

print(add_item_wrong("a"))
print(add_item_wrong("b"))  # Surprise! Contains both!

# RIGHT - use None as default
def add_item_right(item, my_list=None):
    if my_list is None:
        my_list = []
    my_list.append(item)
    return my_list

print(add_item_right("a"))
print(add_item_right("b"))  # Clean!
```

**Expected Output:**
```
['a']
['a', 'b']
['a']
['b']
```

### Mistake 4: Modifying Global Variables Without `global`

```python
x = 10

def change_x():
    # This creates a LOCAL x, does not change global
    x = 20
    print("Inside:", x)

change_x()
print("Outside:", x)  # Still 10!
```

**Expected Output:**
```
Inside: 20
Outside: 10
```

---

## Best Practices

1. **One function, one job.** Each function should do one thing well.
2. **Use descriptive names.** `calculate_average` is better than `ca` or `func1`.
3. **Write docstrings.** Future you (and others) will thank you.
4. **Avoid global variables.** Pass data through parameters and return values.
5. **Keep functions short.** If a function is over 20-30 lines, consider splitting it.
6. **Use default parameters wisely.** Never use mutable objects (like lists) as defaults.
7. **Return values instead of printing.** This makes functions more flexible and testable.

---

## Quick Summary

| Concept | Syntax | Example |
|---------|--------|---------|
| Define function | `def name():` | `def greet():` |
| Parameters | `def name(param):` | `def greet(name):` |
| Return value | `return value` | `return total` |
| Default param | `def f(x=10):` | `def greet(name="World"):` |
| *args | `def f(*args):` | `def add(*nums):` |
| **kwargs | `def f(**kwargs):` | `def info(**data):` |
| Lambda | `lambda x: expr` | `lambda x: x * 2` |
| Docstring | `"""text"""` | See section 8.8 |

---

## Key Points to Remember

1. **`def` defines a function.** The colon and indentation are required.
2. **Parameters are placeholders.** Arguments are actual values.
3. **`return` sends a value back.** Without it, the function returns `None`.
4. **Default parameters** provide fallback values.
5. **`*args` collects extra arguments** into a tuple.
6. **`**kwargs` collects keyword arguments** into a dictionary.
7. **Local variables** only exist inside their function.
8. **Lambda functions** are short, one-line functions for simple tasks.

---

## Practice Questions

**Question 1:** What will this code print?
```python
def multiply(a, b=2):
    return a * b

print(multiply(5))
print(multiply(5, 3))
```

<details>
<summary>Answer</summary>

```
10
15
```
The first call uses the default `b=2`, so 5 * 2 = 10. The second call overrides `b` with 3, so 5 * 3 = 15.
</details>

---

**Question 2:** What is the difference between a parameter and an argument?

<details>
<summary>Answer</summary>

A **parameter** is the variable in the function definition. An **argument** is the actual value you pass when calling the function.

```python
def greet(name):    # 'name' is a parameter
    print(name)

greet("Alice")      # "Alice" is an argument
```
</details>

---

**Question 3:** What will this code print?
```python
x = 10

def change():
    x = 20

change()
print(x)
```

<details>
<summary>Answer</summary>

```
10
```
The function creates a local variable `x` (value 20), but the global `x` remains unchanged. The local `x` disappears when the function ends.
</details>

---

**Question 4:** When should you use a lambda instead of a regular function?

<details>
<summary>Answer</summary>

Use a lambda for short, simple operations that you need only once. Common uses include:
- As a `key` argument in `sorted()` or `max()`
- With `map()` or `filter()`

For anything complex, use a regular function with `def`.
</details>

---

**Question 5:** Why should you avoid using a mutable default argument like `def f(x=[]):`?

<details>
<summary>Answer</summary>

Because the default list is created once and shared across all calls. Each call that modifies the list affects future calls. Use `None` as the default and create a new list inside the function instead:

```python
def f(x=None):
    if x is None:
        x = []
    # now safe to use x
```
</details>

---

## Exercises

### Exercise 1: Temperature Converter

Write two functions:
1. `celsius_to_fahrenheit(celsius)` — converts Celsius to Fahrenheit. Formula: F = C * 9/5 + 32
2. `fahrenheit_to_celsius(fahrenheit)` — converts Fahrenheit to Celsius. Formula: C = (F - 32) * 5/9

Test both functions with at least 3 values each.

<details>
<summary>Solution</summary>

```python
def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return celsius * 9/5 + 32

def fahrenheit_to_celsius(fahrenheit):
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9

# Test celsius_to_fahrenheit
print("Celsius to Fahrenheit:")
print(f"  0°C = {celsius_to_fahrenheit(0):.1f}°F")
print(f"  100°C = {celsius_to_fahrenheit(100):.1f}°F")
print(f"  37°C = {celsius_to_fahrenheit(37):.1f}°F")

# Test fahrenheit_to_celsius
print("\nFahrenheit to Celsius:")
print(f"  32°F = {fahrenheit_to_celsius(32):.1f}°C")
print(f"  212°F = {fahrenheit_to_celsius(212):.1f}°C")
print(f"  98.6°F = {fahrenheit_to_celsius(98.6):.1f}°C")
```

**Expected Output:**
```
Celsius to Fahrenheit:
  0°C = 32.0°F
  100°C = 212.0°F
  37°C = 98.6°F

Fahrenheit to Celsius:
  32°F = 0.0°C
  212°F = 100.0°C
  98.6°F = 37.0°C
```
</details>

---

### Exercise 2: Statistics Calculator

Write a function called `statistics(numbers)` that takes a list of numbers and returns a dictionary with these keys: "count", "sum", "mean", "min", "max", "range". Test it with a list of your choice.

<details>
<summary>Solution</summary>

```python
def statistics(numbers):
    """
    Calculate basic statistics for a list of numbers.

    Parameters:
        numbers (list): A list of numbers.

    Returns:
        dict: A dictionary with count, sum, mean, min, max, range.
    """
    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "range": max(numbers) - min(numbers)
    }

# Test
data = [23, 45, 12, 67, 34, 89, 56]
stats = statistics(data)

print(f"Data: {data}")
print(f"Statistics:")
for key, value in stats.items():
    if isinstance(value, float):
        print(f"  {key}: {value:.2f}")
    else:
        print(f"  {key}: {value}")
```

**Expected Output:**
```
Data: [23, 45, 12, 67, 34, 89, 56]
Statistics:
  count: 7
  sum: 326
  mean: 46.57
  min: 12
  max: 89
  range: 77
```
</details>

---

### Exercise 3: Flexible Greeting

Write a function called `greeting` that:
1. Takes a required `name` parameter.
2. Takes an optional `greeting` parameter (default: "Hello").
3. Takes `**kwargs` for any extra info.
4. Prints the greeting and any extra info provided.

<details>
<summary>Solution</summary>

```python
def greeting(name, greeting="Hello", **kwargs):
    """
    Print a personalized greeting with optional extra info.

    Parameters:
        name (str): The person's name.
        greeting (str): The greeting word (default: "Hello").
        **kwargs: Any additional information to display.
    """
    print(f"{greeting}, {name}!")
    if kwargs:
        for key, value in kwargs.items():
            print(f"  {key}: {value}")
    print()

# Test with different levels of detail
greeting("Alice")
greeting("Bob", "Good morning")
greeting("Charlie", "Welcome", role="Student", year=2, campus="Main")
```

**Expected Output:**
```
Hello, Alice!

Good morning, Bob!

Welcome, Charlie!
  role: Student
  year: 2
  campus: Main

```
</details>

---

## What Is Next?

You can now write reusable functions to organize your code. In Chapter 9, you will learn about **file handling** — how to read data from files and write results to files. This is a critical skill for AI and data science, where you constantly work with data files. You will learn to read CSV files, write output files, and handle data that lives outside your program.
