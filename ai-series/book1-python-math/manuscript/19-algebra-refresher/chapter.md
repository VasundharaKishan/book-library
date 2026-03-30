# Chapter 19: Algebra Refresher — The Language of Machine Learning

## What You Will Learn

In this chapter, you will learn how to:

- Understand variables in math vs variables in programming
- Work with linear equations (y = mx + b) — the foundation of linear regression
- Solve simple equations step by step
- Understand functions as input-output machines
- Graph mathematical functions using Matplotlib
- Solve systems of equations
- Work with inequalities
- Read sigma notation (summation) — used everywhere in ML formulas
- Connect every algebra concept to real machine learning applications

## Why This Chapter Matters

Machine learning is built on math. Not complicated, scary math — but fundamental algebra that you probably learned in school and may have forgotten.

Here is the secret: **the core equation of linear regression is just y = mx + b**. That is the equation of a straight line. If you understand that one equation, you already understand the idea behind one of the most important ML algorithms.

```
+--------------------------------------------------+
|  Why Algebra Matters for AI                       |
+--------------------------------------------------+
|                                                   |
|  Algebra Concept     -->   ML Application         |
|  ----------------         ----------------        |
|  y = mx + b          -->  Linear regression       |
|  Functions            -->  Neural network layers   |
|  Systems of equations -->  Optimization            |
|  Summation (sigma)    -->  Loss functions          |
|  Variables            -->  Features and weights    |
|                                                   |
+--------------------------------------------------+
```

Do not worry if you feel rusty. This chapter starts from the very basics and builds up gently. Every concept includes Python code so you can see the math in action.

---

## 19.1 Variables in Math vs Programming

You already know variables in Python:

```python
x = 10
name = "Alice"
```

Math variables work the same way — they are placeholders for values.

```
Programming:               Math:

x = 10                     x = 10
y = x + 5                  y = x + 5
print(y)  # 15             y = 15
```

**The key difference:** In math, `=` means "is equal to" (a statement of fact). In Python, `=` means "assign this value" (a command).

```
Math:    x = 5    means "x IS 5"
Python:  x = 5    means "STORE 5 in x"

Math:    x + 3 = 8    is a statement (true when x=5)
Python:  x + 3 = 8    is an ERROR (can't assign to x + 3)
Python:  x + 3 == 8   checks equality (True or False)
```

### Common Math Variables in ML

In machine learning, certain letters are used by convention:

```
+--------------------------------------------------+
|  Common Variable Names in ML                      |
+--------------------------------------------------+
|  x  = input data (features)                      |
|  y  = output data (labels/targets)               |
|  w  = weights (what the model learns)            |
|  b  = bias (an offset value)                     |
|  m  = slope (rate of change)                     |
|  n  = number of samples                          |
|  i  = index (counter in loops)                   |
|  f  = function                                   |
+--------------------------------------------------+
```

```python
# In Python, these are just regular variables
x = 5       # an input value
w = 2.0     # a weight
b = 1.0     # a bias
y = w * x + b   # the prediction
print(f"Prediction: {y}")
```

**Expected Output:**

```
Prediction: 11.0
```

---

## 19.2 Linear Equations — The Heart of Linear Regression

A **linear equation** describes a straight line. The most common form is:

```
y = mx + b
```

Where:

- **y** = the output (what you want to predict)
- **m** = the slope (how steep the line is)
- **x** = the input (what you know)
- **b** = the y-intercept (where the line crosses the y-axis)

**Real-life analogy:** Imagine you are a taxi driver. You charge a base fare of $3 plus $2 per mile. Your equation is:

```
total_cost = 2 * miles + 3

This IS y = mx + b where:
  y = total_cost
  m = 2 (price per mile)
  x = miles driven
  b = 3 (base fare)
```

```python
# Taxi fare calculator
def taxi_fare(miles):
    m = 2     # $2 per mile (slope)
    b = 3     # $3 base fare (intercept)
    return m * miles + b

# Calculate fares for different distances
for miles in [1, 3, 5, 10]:
    fare = taxi_fare(miles)
    print(f"{miles} miles = ${fare}")
```

**Expected Output:**

```
1 miles = $5
3 miles = $9
5 miles = $13
10 miles = $23
```

### Understanding Slope (m)

The slope tells you how much y changes when x increases by 1.

```
Positive slope (m > 0):     Negative slope (m < 0):     Zero slope (m = 0):

      /                     \                            ___________
    /                         \
  /                             \                        "Flat line"
"Going uphill"              "Going downhill"
```

```python
import matplotlib.pyplot as plt

x = [0, 1, 2, 3, 4, 5]

# Different slopes
y_positive = [b + 2 * xi for xi, b in zip(x, [1]*6)]  # m = 2
y_negative = [10 + (-1.5) * xi for xi in x]            # m = -1.5
y_zero = [5] * 6                                        # m = 0

# Simpler way to calculate
y_pos = [2 * xi + 1 for xi in x]     # slope = 2, intercept = 1
y_neg = [-1.5 * xi + 10 for xi in x] # slope = -1.5, intercept = 10
y_flat = [5 for xi in x]              # slope = 0, intercept = 5

plt.plot(x, y_pos, label="m=2 (steep uphill)", marker="o")
plt.plot(x, y_neg, label="m=-1.5 (downhill)", marker="s")
plt.plot(x, y_flat, label="m=0 (flat)", marker="^")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Effect of Different Slopes")
plt.legend()
plt.grid(True)
plt.show()
```

**Expected Output:**

Three lines on one chart. The blue line goes up steeply. The orange line goes down. The green line is flat.

### Understanding Intercept (b)

The intercept is where the line crosses the y-axis (where x = 0).

```python
import matplotlib.pyplot as plt

x = [0, 1, 2, 3, 4, 5]

# Same slope, different intercepts
y1 = [2 * xi + 0 for xi in x]    # b = 0
y2 = [2 * xi + 3 for xi in x]    # b = 3
y3 = [2 * xi + 6 for xi in x]    # b = 6

plt.plot(x, y1, label="b=0", marker="o")
plt.plot(x, y2, label="b=3", marker="o")
plt.plot(x, y3, label="b=6", marker="o")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Same Slope, Different Intercepts")
plt.legend()
plt.grid(True)
plt.show()
```

**Expected Output:**

Three parallel lines. They have the same steepness but start at different y-values.

### This IS Linear Regression

In machine learning, linear regression finds the best values of `m` and `b` to fit a line to your data.

```
Given data points:             Linear regression finds:

  *          *                  *     ___*___
     *    *                      * __/  *
  *    *                      * _/  *
     *                         /  *
                              The best-fit line!

  "Messy data"                "y = 0.8x + 2.1"
                              m = 0.8, b = 2.1
```

```python
import numpy as np
import matplotlib.pyplot as plt

# Some data points (study hours vs test score)
hours = np.array([1, 2, 3, 4, 5, 6, 7, 8])
scores = np.array([45, 50, 55, 62, 68, 72, 78, 85])

# Find the best m and b using NumPy
m, b = np.polyfit(hours, scores, 1)
print(f"Best fit: y = {m:.2f}x + {b:.2f}")

# Plot data points and the best-fit line
plt.scatter(hours, scores, color="blue", label="Actual data")
plt.plot(hours, m * hours + b, color="red", label=f"y = {m:.1f}x + {b:.1f}")
plt.xlabel("Hours Studied")
plt.ylabel("Test Score")
plt.title("Linear Regression: Study Hours vs Scores")
plt.legend()
plt.grid(True)
plt.show()
```

**Expected Output:**

```
Best fit: y = 5.60x + 39.50
```

A chart with blue dots (actual data) and a red line (the best-fit line) running through them.

**Line-by-line explanation:**

```python
m, b = np.polyfit(hours, scores, 1)
```

`np.polyfit()` finds the best slope (`m`) and intercept (`b`) for a polynomial of degree 1 (which is a straight line). This is linear regression in one line of code.

---

## 19.3 Solving Equations

Solving an equation means finding the value of the unknown variable.

### Simple Equations

```
Equation:     2x + 3 = 11
Goal:         Find x

Step 1:       2x + 3 = 11
Step 2:       2x = 11 - 3     (subtract 3 from both sides)
Step 3:       2x = 8
Step 4:       x = 8 / 2       (divide both sides by 2)
Step 5:       x = 4
```

In Python, you can verify:

```python
x = 4
result = 2 * x + 3
print(f"2 * {x} + 3 = {result}")
print(f"Does it equal 11? {result == 11}")
```

**Expected Output:**

```
2 * 4 + 3 = 11
Does it equal 11? True
```

### Using SymPy to Solve Equations

SymPy is a Python library for symbolic math. It can solve equations for you.

```python
from sympy import symbols, solve

# Define x as a mathematical symbol
x = symbols("x")

# Solve 2x + 3 = 11
# SymPy expects equation = 0, so we write: 2x + 3 - 11 = 0
solution = solve(2*x + 3 - 11, x)
print(f"Solution: x = {solution}")
```

**Expected Output:**

```
Solution: x = [4]
```

**Line-by-line explanation:**

```python
x = symbols("x")
```

This creates a symbolic variable. Unlike a regular Python variable, it does not hold a number. It represents an unknown value.

```python
solution = solve(2*x + 3 - 11, x)
```

`solve()` takes an expression (set equal to zero) and the variable to solve for. It returns a list of solutions.

### Why This Matters for ML

In machine learning, the training process is essentially solving equations. The model adjusts weights to minimize error. This is equation-solving at scale — with thousands or millions of variables.

---

## 19.4 Functions — Input-Output Machines

A **function** in math takes an input and produces an output. Just like a Python function.

```
Math function:              Python function:

f(x) = 2x + 1              def f(x):
                                return 2 * x + 1
f(3) = 2(3) + 1 = 7
                            f(3)  # returns 7
```

**Real-life analogy:** Think of a function as a vending machine. You put in money (input), press a button (the function), and get a snack (output). Same input always gives the same output.

```
+---------------------+
|  FUNCTION MACHINE   |
|                     |
|  Input: x = 3       |
|     |               |
|     v               |
|  [ f(x) = 2x + 1 ] |
|     |               |
|     v               |
|  Output: 7          |
+---------------------+
```

```python
# A simple math function
def f(x):
    return 2 * x + 1

# Test with different inputs
for x in range(-3, 4):
    print(f"f({x}) = {f(x)}")
```

**Expected Output:**

```
f(-3) = -5
f(-2) = -3
f(-1) = -1
f(0) = 1
f(1) = 3
f(2) = 5
f(3) = 7
```

### Common Math Functions

```python
import math

# Square function: f(x) = x^2
def square(x):
    return x ** 2

# Absolute value: f(x) = |x|
def absolute(x):
    return abs(x)

# Square root: f(x) = sqrt(x)
def sqrt(x):
    return math.sqrt(x)

print(f"square(4) = {square(4)}")
print(f"absolute(-7) = {absolute(-7)}")
print(f"sqrt(16) = {sqrt(16)}")
```

**Expected Output:**

```
square(4) = 16
absolute(-7) = 7
sqrt(16) = 4.0
```

### Functions in ML

In neural networks, each layer is a function. The whole network is a chain of functions:

```
Input --> f1() --> f2() --> f3() --> Output

Each function transforms the data.
The network LEARNS what these functions should be.
```

---

## 19.5 Graphing Functions with Matplotlib

Visualizing functions helps you understand their behavior.

```python
import numpy as np
import matplotlib.pyplot as plt

# Create x values from -5 to 5
x = np.linspace(-5, 5, 100)

# Define functions
y_linear = 2 * x + 1           # linear: f(x) = 2x + 1
y_quadratic = x ** 2           # quadratic: f(x) = x^2
y_cubic = x ** 3               # cubic: f(x) = x^3

# Plot all three
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].plot(x, y_linear, color="blue")
axes[0].set_title("Linear: f(x) = 2x + 1")
axes[0].grid(True)
axes[0].axhline(y=0, color="black", linewidth=0.5)
axes[0].axvline(x=0, color="black", linewidth=0.5)

axes[1].plot(x, y_quadratic, color="red")
axes[1].set_title("Quadratic: f(x) = x^2")
axes[1].grid(True)
axes[1].axhline(y=0, color="black", linewidth=0.5)
axes[1].axvline(x=0, color="black", linewidth=0.5)

axes[2].plot(x, y_cubic, color="green")
axes[2].set_title("Cubic: f(x) = x^3")
axes[2].grid(True)
axes[2].axhline(y=0, color="black", linewidth=0.5)
axes[2].axvline(x=0, color="black", linewidth=0.5)

plt.tight_layout()
plt.show()
```

**Expected Output:**

Three side-by-side charts showing a straight line, a U-shaped parabola, and an S-shaped cubic curve.

```
Linear:          Quadratic:       Cubic:

     /           |  U  |               /
    /            | / \ |              /
   /             |/   \|         ____/
--/---          -+-----+-       /----
 /               |     |       /
```

**Line-by-line explanation:**

```python
x = np.linspace(-5, 5, 100)
```

Creates 100 evenly spaced numbers from -5 to 5. This gives us smooth curves when plotted.

```python
axes[0].axhline(y=0, color="black", linewidth=0.5)
axes[0].axvline(x=0, color="black", linewidth=0.5)
```

These draw the x-axis and y-axis lines through the origin (0, 0). This helps you see where the function crosses zero.

---

## 19.6 Systems of Equations

A **system of equations** is two or more equations with the same variables. The solution is the values that satisfy ALL equations at once.

**Real-life analogy:** Imagine two friends meet at a restaurant. Alice walks east at 3 mph. Bob walks north at 4 mph. Where are they after 2 hours? You need two equations (one for each person) to find the answer.

### Two Equations, Two Unknowns

```
Equation 1:   2x + y = 10
Equation 2:   x - y = 2

Find x and y that make BOTH true.
```

Solving by hand:

```
Add both equations:
  2x + y = 10
+  x - y =  2
-----------
  3x     = 12
   x     = 4

Substitute x = 4 into Equation 2:
  4 - y = 2
  y = 2

Solution: x = 4, y = 2
```

### Solving with NumPy

```python
import numpy as np

# 2x + y = 10
# x - y = 2

# Coefficient matrix (left side)
A = np.array([
    [2, 1],    # coefficients of equation 1: 2x + 1y
    [1, -1]    # coefficients of equation 2: 1x + (-1)y
])

# Constants (right side)
b = np.array([10, 2])

# Solve the system
solution = np.linalg.solve(A, b)
print(f"x = {solution[0]}")
print(f"y = {solution[1]}")
```

**Expected Output:**

```
x = 4.0
y = 2.0
```

**Line-by-line explanation:**

```python
A = np.array([[2, 1], [1, -1]])
```

The coefficient matrix. Each row is one equation. Each column is one variable (x, y). The values are the numbers in front of the variables.

```python
b = np.array([10, 2])
```

The constants on the right side of each equation.

```python
solution = np.linalg.solve(A, b)
```

`np.linalg.solve()` solves the system `Ax = b`. It uses linear algebra under the hood — the same math that powers machine learning.

### Visualizing the Solution

The solution is where two lines intersect.

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 6, 100)

# Equation 1: 2x + y = 10 --> y = 10 - 2x
y1 = 10 - 2 * x

# Equation 2: x - y = 2 --> y = x - 2
y2 = x - 2

plt.plot(x, y1, label="2x + y = 10", color="blue")
plt.plot(x, y2, label="x - y = 2", color="red")
plt.scatter([4], [2], color="green", s=100, zorder=5, label="Solution (4, 2)")
plt.xlabel("x")
plt.ylabel("y")
plt.title("System of Equations: Lines Intersect at Solution")
plt.legend()
plt.grid(True)
plt.show()
```

**Expected Output:**

Two lines crossing at the point (4, 2), marked with a green dot.

```
y
10|  \
 8|    \       /
 6|      \   /
 4|        X        <-- intersection at (4, 2)
 2|      /   \
 0|    /       \
  +--+--+--+--+--+-- x
     1  2  3  4  5
```

### Why This Matters for ML

Training a machine learning model involves solving systems of equations (often with thousands of variables). The model finds the weights that best satisfy all the data points simultaneously.

---

## 19.7 Inequalities

An **inequality** is like an equation, but instead of `=`, it uses `<`, `>`, `<=`, or `>=`.

```
Equation:      x = 5       (one answer)
Inequality:    x > 5       (many answers: 6, 7, 8, 100, ...)
```

Common inequality symbols:

```
>     greater than          x > 5    means x is more than 5
<     less than             x < 5    means x is less than 5
>=    greater or equal      x >= 5   means x is 5 or more
<=    less or equal         x <= 5   means x is 5 or less
```

```python
# Checking inequalities in Python
x = 7

print(f"x = {x}")
print(f"x > 5:  {x > 5}")     # True
print(f"x < 5:  {x < 5}")     # False
print(f"x >= 7: {x >= 7}")    # True
print(f"x <= 3: {x <= 3}")    # False
```

**Expected Output:**

```
x = 7
x > 5:  True
x < 5:  False
x >= 7: True
x <= 3: False
```

### Inequalities with Multiple Conditions

```python
# Filtering data with inequalities
import numpy as np

temperatures = np.array([15, 22, 18, 30, 25, 12, 28, 35, 20, 17])

# Find temperatures above 25
hot_days = temperatures[temperatures > 25]
print(f"Hot days (above 25): {hot_days}")

# Find temperatures between 18 and 28
comfortable = temperatures[(temperatures >= 18) & (temperatures <= 28)]
print(f"Comfortable (18-28): {comfortable}")
```

**Expected Output:**

```
Hot days (above 25): [30 28 35]
Comfortable (18-28): [22 18 25 28 20]
```

### Why This Matters for ML

Inequalities are used in:

- **Decision trees** — "if temperature > 25, predict 'hot'"
- **Data filtering** — selecting subsets of data for training
- **Constraints** — setting boundaries on model predictions
- **Activation functions** — ReLU returns max(0, x), which is an inequality

---

## 19.8 Sigma Notation — Summation

The Greek letter sigma looks like this in math textbooks:

```
  n
  E    means "sum from i=1 to n"
 i=1
```

We write it as a capital E here since we cannot display the real symbol easily. In textbooks, it is the Greek letter that looks like a sideways M.

**Real-life analogy:** Sigma notation is just a compact way to write "add up all these things." Instead of writing `1 + 2 + 3 + 4 + 5`, you write "sum of i from 1 to 5."

```
Math notation:          What it means:              Python:

  5
  E  i                  1 + 2 + 3 + 4 + 5          sum(range(1, 6))
 i=1

  4
  E  i^2                1 + 4 + 9 + 16             sum(i**2 for i in range(1, 5))
 i=1

  n
  E  x_i                x_1 + x_2 + ... + x_n      sum(x)
 i=1
```

### Sigma in Python

```python
# Sum of numbers 1 to 10
result = sum(range(1, 11))
print(f"Sum of 1 to 10: {result}")

# Sum of squares: 1^2 + 2^2 + 3^2 + ... + 5^2
result = sum(i**2 for i in range(1, 6))
print(f"Sum of squares (1-5): {result}")

# Sum of elements in a list
x = [10, 20, 30, 40, 50]
result = sum(x)
print(f"Sum of x: {result}")
```

**Expected Output:**

```
Sum of 1 to 10: 55
Sum of squares (1-5): 55
Sum of x: 150
```

### The Mean (Average) Uses Sigma

The formula for the mean is:

```
         1    n
mean = ----- E  x_i
         n  i=1

Translation: "Add up all values, then divide by how many there are."
```

```python
import numpy as np

data = [10, 20, 30, 40, 50]

# Calculate mean manually using sigma
n = len(data)
total = sum(data)       # This is the sigma part
mean = total / n
print(f"Manual mean: {mean}")

# Using NumPy (does the same thing)
print(f"NumPy mean:  {np.mean(data)}")
```

**Expected Output:**

```
Manual mean: 30.0
NumPy mean:  30.0
```

### Mean Squared Error (MSE) — A Key ML Formula

One of the most important formulas in machine learning is the Mean Squared Error:

```
          1    n
MSE = ------- E  (y_i - y_hat_i)^2
          n  i=1

Translation:
1. For each data point, find the error (actual - predicted)
2. Square each error
3. Add them all up (sigma)
4. Divide by n (mean)
```

```python
import numpy as np

# Actual values
y_actual = np.array([3, 5, 7, 9])

# Predicted values (from our model)
y_predicted = np.array([2.8, 5.2, 6.5, 9.1])

# Calculate MSE step by step
errors = y_actual - y_predicted           # Step 1: differences
squared_errors = errors ** 2              # Step 2: square them
sum_of_squared = np.sum(squared_errors)   # Step 3: sum (sigma)
mse = sum_of_squared / len(y_actual)      # Step 4: divide by n

print(f"Errors:          {errors}")
print(f"Squared errors:  {squared_errors}")
print(f"Sum:             {sum_of_squared}")
print(f"MSE:             {mse}")
```

**Expected Output:**

```
Errors:          [ 0.2 -0.2  0.5 -0.1]
Squared errors:  [0.04 0.04 0.25 0.01]
Sum:             0.34
MSE:             0.085
```

**Line-by-line explanation:**

```python
errors = y_actual - y_predicted
```

The difference between what actually happened and what our model predicted. Positive means we predicted too low. Negative means too high.

```python
squared_errors = errors ** 2
```

We square the errors for two reasons: (1) it makes all errors positive, and (2) it penalizes large errors more than small ones.

```python
mse = sum_of_squared / len(y_actual)
```

Dividing by n gives us the average error. This is the MSE — the number machine learning tries to minimize.

---

## 19.9 Real-World Examples Connecting Algebra to ML

### Example 1: Predicting House Prices

```python
import numpy as np
import matplotlib.pyplot as plt

# House size (sq ft) and price ($1000s)
size = np.array([800, 1000, 1200, 1500, 1800, 2000, 2500])
price = np.array([150, 200, 230, 300, 350, 400, 500])

# Find best-fit line: price = m * size + b
m, b = np.polyfit(size, price, 1)
print(f"Formula: price = {m:.4f} * size + {b:.2f}")
print(f"Slope: ${m*1000:.2f} per extra sq ft")

# Predict price for a 1600 sq ft house
new_size = 1600
predicted_price = m * new_size + b
print(f"\nPredicted price for {new_size} sq ft: ${predicted_price:.0f}k")

# Visualize
plt.scatter(size, price, color="blue", label="Actual data")
x_line = np.linspace(600, 2700, 100)
plt.plot(x_line, m * x_line + b, color="red", label="Best-fit line")
plt.scatter([new_size], [predicted_price], color="green", s=100,
            zorder=5, label=f"Prediction: ${predicted_price:.0f}k")
plt.xlabel("House Size (sq ft)")
plt.ylabel("Price ($1000s)")
plt.title("House Price Prediction with Linear Equation")
plt.legend()
plt.grid(True)
plt.show()
```

**Expected Output:**

```
Formula: price = 0.2015 * size + -12.14
Slope: $201.49 per extra sq ft

Predicted price for 1600 sq ft: $310k
```

### Example 2: Temperature Conversion

The formula to convert Celsius to Fahrenheit is a linear equation:

```
F = 1.8 * C + 32

This is y = mx + b where m = 1.8 and b = 32
```

```python
def celsius_to_fahrenheit(c):
    return 1.8 * c + 32

# Convert some temperatures
for c in [0, 20, 37, 100]:
    f = celsius_to_fahrenheit(c)
    print(f"{c}C = {f}F")
```

**Expected Output:**

```
0C = 32.0F
20C = 68.0F
37C = 98.6F
100C = 212.0F
```

### Example 3: Summation in Practice — Calculating Accuracy

```python
import numpy as np

# Model predictions and actual labels
predictions = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1])
actual =      np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 0])

# Accuracy = (1/n) * sum(prediction == actual)
n = len(predictions)
correct = np.sum(predictions == actual)   # sigma notation!
accuracy = correct / n

print(f"Correct: {correct} out of {n}")
print(f"Accuracy: {accuracy:.0%}")
```

**Expected Output:**

```
Correct: 7 out of 10
Accuracy: 70%
```

---

## Common Mistakes

**Mistake 1: Confusing `=` and `==` in Python.**

```python
x = 5       # assignment (stores a value)
x == 5      # comparison (checks equality, returns True/False)
```

**Fix:** Use `=` to store values. Use `==` to check if things are equal.

---

**Mistake 2: Forgetting order of operations.**

```python
# Wrong: 2 + 3 * 4 = 20?
result = 2 + 3 * 4     # Actually 14! Multiplication first.

# Right: use parentheses
result = (2 + 3) * 4   # 20
```

**Fix:** Use parentheses to make the order explicit. Python follows PEMDAS: Parentheses, Exponents, Multiplication/Division, Addition/Subtraction.

---

**Mistake 3: Integer division surprises.**

```python
# In Python 3, / always gives a float
result = 7 / 2     # 3.5 (correct)

# Use // for integer division (rounds down)
result = 7 // 2    # 3
```

**Fix:** Know the difference between `/` (true division) and `//` (floor division).

---

**Mistake 4: Using `^` for exponents instead of `**`.**

```python
result = 2 ^ 3      # This is XOR (bitwise), not power! Result: 1
result = 2 ** 3     # This is power. Result: 8
```

**Fix:** Always use `**` for exponents in Python. `^` means something completely different.

---

## Best Practices

1. **Use NumPy for math operations.** It is faster and handles arrays naturally.

2. **Always visualize equations.** Plot them with Matplotlib. A picture makes abstract math concrete.

3. **Connect every concept to ML.** Ask yourself: "Where does this appear in machine learning?"

4. **Use parentheses generously.** They make your code clearer and prevent order-of-operations bugs.

5. **Practice translating formulas to code.** Every ML formula can be written in Python. Start with the sigma and work outward.

6. **Do not memorize formulas. Understand them.** If you understand what MSE means (average squared error), you can always reconstruct the formula.

---

## Quick Summary

```
+----------------------------------------------------------+
|  Algebra for ML Quick Reference                           |
+----------------------------------------------------------+
|  Linear equation:  y = mx + b                             |
|    m = slope (rate of change)                              |
|    b = intercept (starting value)                          |
|                                                           |
|  Solve equations:  np.linalg.solve(A, b)                  |
|  Best-fit line:    np.polyfit(x, y, 1)                    |
|                                                           |
|  Functions: input --> process --> output                   |
|  Graph:     np.linspace() + plt.plot()                    |
|                                                           |
|  Sigma = summation = sum() in Python                      |
|  Mean = sum / n = np.mean()                               |
|  MSE = mean of squared errors                             |
+----------------------------------------------------------+
```

---

## Key Points to Remember

1. **y = mx + b** is the equation of a straight line AND the equation behind linear regression. The slope `m` is the weight. The intercept `b` is the bias.

2. **Variables in math** are just like variables in Python — placeholders for values.

3. **Functions** are input-output machines. Neural networks are chains of functions.

4. **Systems of equations** can be solved with `np.linalg.solve()`. ML training solves systems with millions of variables.

5. **Sigma notation** means "sum everything up." In Python, it is just `sum()` or `np.sum()`.

6. **Mean Squared Error (MSE)** is the most common loss function. It uses both sigma (summation) and squaring.

7. **Every algebra concept maps to something in ML.** Slope becomes weight. Intercept becomes bias. Summation becomes loss calculation.

---

## Practice Questions

**Question 1:** In the equation y = 3x + 7, what are the slope and y-intercept?

**Answer:** The slope (m) is 3, meaning y increases by 3 for every 1 unit increase in x. The y-intercept (b) is 7, meaning the line crosses the y-axis at y = 7 (when x = 0).

---

**Question 2:** What does sigma notation represent, and how do you write it in Python?

**Answer:** Sigma notation represents the sum of a series of values. For example, the sum of i from i=1 to n means adding up 1 + 2 + 3 + ... + n. In Python, you write this as `sum(range(1, n+1))` or `np.sum(array)`. It appears in almost every ML formula, especially in loss functions like MSE.

---

**Question 3:** Why do we square the errors in Mean Squared Error instead of just averaging them?

**Answer:** We square errors for two reasons. First, squaring makes all errors positive. Without squaring, positive and negative errors would cancel each other out, making the average misleadingly small. Second, squaring penalizes large errors more heavily. An error of 10 becomes 100 when squared, while an error of 2 becomes only 4. This means the model is strongly motivated to fix its biggest mistakes.

---

**Question 4:** How does the equation y = mx + b relate to linear regression?

**Answer:** Linear regression finds the best values for m (slope/weight) and b (intercept/bias) that make the line y = mx + b fit the data as closely as possible. The slope m tells you how much y changes for each unit change in x. The intercept b is the predicted y when x is zero. In ML terminology, m is called the weight and b is called the bias.

---

**Question 5:** Solve the system: x + y = 10 and x - y = 4. What are x and y?

**Answer:** Adding both equations: 2x = 14, so x = 7. Substituting back: 7 + y = 10, so y = 3. You can verify: 7 + 3 = 10 (correct) and 7 - 3 = 4 (correct). In NumPy: `np.linalg.solve([[1,1],[1,-1]], [10,4])` returns `[7, 3]`.

---

## Exercises

### Exercise 1: Taxi Fare Calculator

Write a function `calculate_fare(miles)` that implements the equation:

```
fare = 2.5 * miles + 3.0
```

Test it with 0, 5, 10, and 20 miles. Then plot the fare vs miles using Matplotlib. What is the slope? What does it mean in real-world terms?

**Hint:** The slope is the price per mile. The intercept is the base fare.

---

### Exercise 2: Manual MSE Calculator

Given these actual and predicted values:

- Actual: [10, 20, 30, 40, 50]
- Predicted: [12, 18, 33, 37, 52]

Calculate the MSE step by step:
1. Find the errors (actual - predicted)
2. Square each error
3. Sum the squared errors
4. Divide by the number of data points

Then verify your answer using NumPy.

**Hint:** The formula is `MSE = (1/n) * sum((actual - predicted)^2)`.

---

### Exercise 3: System of Equations Solver

Solve this system using both hand calculation and NumPy:

```
3x + 2y = 16
x - y = 3
```

Then plot both equations on the same chart and mark the intersection point.

**Hint:** Rearrange each equation to y = ... form for plotting. Use `np.linalg.solve()` for the numerical solution.

---

## What Is Next?

Now that you have refreshed your algebra skills, you are ready for the next big concept: **vectors**. Vectors are lists of numbers that represent direction and magnitude. In machine learning, every data point is a vector. Every feature set is a vector. Understanding vectors is essential for understanding how ML models process data.
