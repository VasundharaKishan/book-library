# Chapter 23: Derivatives — Measuring How Things Change

## What You Will Learn

- What a derivative is and why it measures change
- The difference between the slope of a line and the slope of a curve
- Basic derivative rules (power, constant, sum)
- The chain rule (for nested functions)
- Partial derivatives (changing one variable at a time)
- How to compute derivatives numerically in Python
- Why derivatives matter: finding the minimum of a function

## Why This Chapter Matters

Here is the big secret of machine learning: **training a model means finding the minimum of a function.**

When you train a neural network, you have an "error function" that measures how wrong the model is. You want to make that error as small as possible. How do you find the lowest point of a function? You use **derivatives**.

Derivatives tell you which direction is "downhill." They point you toward better answers. Without derivatives, neural networks could not learn.

This is not abstract math. This is the engine that powers every AI system.

---

## What Is a Derivative?

A derivative measures **how fast something is changing**.

### Real-Life Analogy: Speed

You are driving a car. Your position changes over time.

- **Position** tells you WHERE you are (10 miles from home).
- **Speed** tells you HOW FAST your position is changing (60 miles per hour).

Speed is the **derivative** of position. It is the rate of change.

```
Position vs. Speed:

    Position (miles)
    |
    |          ___________
    |        /
    |      /                  <-- Steep = going fast
    |    /
    |  /
    |/________________________ Time (hours)

    Speed (miles/hour)
    |
    |  ____
    | |    |
    | |    |____
    | |         |
    | |         |________
    |_________________________ Time (hours)

    Speed = derivative of position
    Speed tells you how fast position is changing at each moment.
```

### The Math Idea

If you have a function f(x), the derivative f'(x) tells you:

> "If I increase x by a tiny amount, how much does f(x) change?"

```
    Derivative = Change in output / Change in input

    f'(x) = lim     f(x + h) - f(x)
            h -> 0  -----------------
                           h

    In plain English:
    - Make a tiny step h in x
    - See how much f changes
    - Divide the change by the step size
    - Make h infinitely small
```

---

## Slope of a Line vs. Slope of a Curve

### Slope of a Line

A straight line has the same slope everywhere. The slope is constant.

```
    y = 2x + 1

    y
    |        /
    |      /
    |    /     slope = 2 everywhere
    |  /
    |/
    +-----------> x

    The derivative of y = 2x + 1 is just 2.
    It never changes.
```

### Slope of a Curve

A curve has a different slope at every point. The slope keeps changing.

```
    y = x^2

    y
    |          *
    |        *
    |      *
    |    *          slope = 6 here (steep)
    |   *
    |  *            slope = 2 here (moderate)
    | *
    |*              slope = 0 here (flat, at the bottom)
    +-----------> x

    The derivative of y = x^2 is 2x.
    At x=0, slope = 0 (flat).
    At x=1, slope = 2.
    At x=3, slope = 6 (steep).
```

### Computing and Plotting Slopes

```python
import numpy as np
import matplotlib.pyplot as plt

# The function: f(x) = x^2
x = np.linspace(-3, 3, 100)
y = x ** 2

# The derivative: f'(x) = 2x
y_derivative = 2 * x

# Plot both
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: The function
axes[0].plot(x, y, 'b-', linewidth=2)
axes[0].set_title('f(x) = x^2')
axes[0].set_xlabel('x')
axes[0].set_ylabel('f(x)')
axes[0].grid(True, alpha=0.3)

# Mark a point and its tangent line
x0 = 1.5
y0 = x0 ** 2
slope = 2 * x0
tangent_x = np.linspace(x0 - 1.5, x0 + 1.5, 50)
tangent_y = slope * (tangent_x - x0) + y0

axes[0].plot(tangent_x, tangent_y, 'r--', linewidth=2, label=f'Tangent at x={x0}')
axes[0].plot(x0, y0, 'ro', markersize=10)
axes[0].text(x0 + 0.2, y0 + 0.5, f'slope = {slope}', fontsize=12, color='red')
axes[0].legend()

# Right: The derivative
axes[1].plot(x, y_derivative, 'g-', linewidth=2)
axes[1].set_title("f'(x) = 2x (the derivative)")
axes[1].set_xlabel('x')
axes[1].set_ylabel("f'(x)")
axes[1].grid(True, alpha=0.3)
axes[1].axhline(y=0, color='k', linewidth=0.5)

# Mark the same point
axes[1].plot(x0, slope, 'ro', markersize=10)
axes[1].text(x0 + 0.2, slope + 0.3, f"f'({x0}) = {slope}", fontsize=12, color='red')

plt.tight_layout()
plt.savefig('function_and_derivative.png', dpi=100, bbox_inches='tight')
plt.show()
print("Plot saved!")
```

**Expected Output:**
```
Plot saved!
```

Two plots appear. The left shows the parabola x^2 with a tangent line at x=1.5 showing slope=3. The right shows the derivative 2x, which is a straight line.

---

## Basic Derivative Rules

You do not need to use the limit definition every time. There are shortcuts.

### Rule 1: Power Rule

```
    If f(x) = x^n

    Then f'(x) = n * x^(n-1)

    "Bring the exponent down, subtract 1 from the exponent."

    Examples:
    f(x) = x^3    -->  f'(x) = 3x^2
    f(x) = x^5    -->  f'(x) = 5x^4
    f(x) = x^2    -->  f'(x) = 2x
    f(x) = x^1    -->  f'(x) = 1
    f(x) = x^0.5  -->  f'(x) = 0.5 * x^(-0.5)
```

### Rule 2: Constant Rule

```
    If f(x) = c  (a constant, like 5)

    Then f'(x) = 0

    "Constants don't change, so their rate of change is zero."

    Examples:
    f(x) = 5      -->  f'(x) = 0
    f(x) = 100    -->  f'(x) = 0
    f(x) = -3     -->  f'(x) = 0
```

### Rule 3: Constant Multiple Rule

```
    If f(x) = c * g(x)

    Then f'(x) = c * g'(x)

    "Constants just come along for the ride."

    Examples:
    f(x) = 3x^2   -->  f'(x) = 3 * 2x = 6x
    f(x) = 5x^4   -->  f'(x) = 5 * 4x^3 = 20x^3
```

### Rule 4: Sum Rule

```
    If f(x) = g(x) + h(x)

    Then f'(x) = g'(x) + h'(x)

    "Take the derivative of each part separately."

    Example:
    f(x) = x^3 + 2x + 5
    f'(x) = 3x^2 + 2 + 0
    f'(x) = 3x^2 + 2
```

### Python Verification

```python
import numpy as np

# Verify derivatives numerically
# f(x) = x^3 + 2x + 5
# f'(x) = 3x^2 + 2

def f(x):
    return x**3 + 2*x + 5

def f_derivative(x):
    return 3*x**2 + 2

# Check at x = 2
x = 2.0
h = 0.0001  # tiny step

# Numerical derivative (approximation)
numerical = (f(x + h) - f(x)) / h

# Exact derivative from our formula
exact = f_derivative(x)

print(f"f(x) = x^3 + 2x + 5")
print(f"f'(x) = 3x^2 + 2")
print(f"\nAt x = {x}:")
print(f"  Numerical derivative:  {numerical:.6f}")
print(f"  Exact derivative:      {exact:.6f}")
print(f"  Difference:            {abs(numerical - exact):.8f}")
```

**Expected Output:**
```
f(x) = x^3 + 2x + 5
f'(x) = 3x^2 + 2

At x = 2.0:
  Numerical derivative:  14.000600
  Exact derivative:      14.000000
  Difference:            0.00060001
```

**Line-by-line explanation:**
- We compute the derivative two ways: numerically (using the formula with tiny h) and exactly (using our derivative rules).
- They match to 4 decimal places. The tiny difference is because h is not infinitely small.

---

## The Chain Rule

The chain rule handles **nested functions** — functions inside other functions.

### Real-Life Analogy

Imagine a factory assembly line:

```
    Raw Material  -->  Machine A  -->  Machine B  -->  Final Product

    If Machine A doubles things, and Machine B triples things:
    Total change = 2 x 3 = 6

    The chain rule says: multiply the rates together.
```

### The Math

```
    If f(x) = g(h(x))  (g wraps around h)

    Then f'(x) = g'(h(x)) * h'(x)

    "Derivative of the outer times derivative of the inner."

    Example:
    f(x) = (3x + 1)^2

    Outer function: g(u) = u^2     --> g'(u) = 2u
    Inner function: h(x) = 3x + 1  --> h'(x) = 3

    f'(x) = 2(3x + 1) * 3 = 6(3x + 1)
```

### Step-by-Step Diagram

```
Chain Rule for f(x) = (3x + 1)^2:

    x
    |
    v
    [Inner: 3x + 1]  ---->  u = 3x + 1
    |                        |
    |  derivative: 3         |  derivative: 2u
    |                        |
    v                        v
    [Outer: u^2]     ---->  f = u^2

    Total derivative = 3 * 2u = 3 * 2(3x+1) = 6(3x+1)

    Multiply the derivatives along the chain!
```

### Python Verification

```python
import numpy as np

# f(x) = (3x + 1)^2
# f'(x) = 6(3x + 1)

def f(x):
    return (3*x + 1) ** 2

def f_derivative(x):
    return 6 * (3*x + 1)

# Check at x = 2
x = 2.0
h = 0.0001

numerical = (f(x + h) - f(x)) / h
exact = f_derivative(x)

print(f"f(x) = (3x + 1)^2")
print(f"f'(x) = 6(3x + 1)")
print(f"\nAt x = {x}:")
print(f"  f({x}) = {f(x)}")
print(f"  Numerical derivative: {numerical:.4f}")
print(f"  Exact derivative:     {exact:.4f}")
```

**Expected Output:**
```
f(x) = (3x + 1)^2
f'(x) = 6(3x + 1)

At x = 2.0:
  f(2.0) = 49.0
  Numerical derivative: 42.0018
  Exact derivative:     42.0000
```

---

## Partial Derivatives

When a function has **multiple variables**, a partial derivative measures how the function changes when you change **one variable** while keeping the others **fixed**.

### Real-Life Analogy

Imagine the temperature in a room depends on two things:
- x = number of heaters turned on
- y = number of windows open

The partial derivative with respect to x asks: "If I turn on one more heater (and keep the windows the same), how much does the temperature change?"

The partial derivative with respect to y asks: "If I open one more window (and keep the heaters the same), how much does the temperature change?"

```
Partial Derivatives:

    f(x, y) = x^2 + 3xy + y^2

    Partial derivative with respect to x (treat y as a constant):
    df/dx = 2x + 3y

    Partial derivative with respect to y (treat x as a constant):
    df/dy = 3x + 2y

    "Change one variable. Freeze the others."
```

### Python Computation

```python
import numpy as np

# f(x, y) = x^2 + 3xy + y^2
def f(x, y):
    return x**2 + 3*x*y + y**2

# Exact partial derivatives
def df_dx(x, y):
    return 2*x + 3*y

def df_dy(x, y):
    return 3*x + 2*y

# Numerical partial derivatives
x, y = 2.0, 3.0
h = 0.0001

# Partial with respect to x: change x, keep y fixed
numerical_dx = (f(x + h, y) - f(x, y)) / h

# Partial with respect to y: change y, keep x fixed
numerical_dy = (f(x, y + h) - f(x, y)) / h

print(f"f(x, y) = x^2 + 3xy + y^2")
print(f"\nAt x={x}, y={y}:")
print(f"  f({x}, {y}) = {f(x, y)}")
print(f"\n  df/dx:")
print(f"    Numerical: {numerical_dx:.4f}")
print(f"    Exact:     {df_dx(x, y):.4f}")
print(f"\n  df/dy:")
print(f"    Numerical: {numerical_dy:.4f}")
print(f"    Exact:     {df_dy(x, y):.4f}")
```

**Expected Output:**
```
f(x, y) = x^2 + 3xy + y^2

At x=2.0, y=3.0:
  f(2.0, 3.0) = 31.0

  df/dx:
    Numerical: 13.0001
    Exact:     13.0000

  df/dy:
    Numerical: 12.0001
    Exact:     12.0000
```

**Line-by-line explanation:**
- `f(x + h, y) - f(x, y)` — We change x by h but keep y the same. This gives the partial derivative with respect to x.
- `f(x, y + h) - f(x, y)` — We change y by h but keep x the same. This gives the partial derivative with respect to y.

---

## Computing Derivatives Numerically in Python

Sometimes you cannot find the derivative formula by hand. No problem. You can always compute it numerically.

### Three Methods

```
Method 1: Forward Difference (simplest)
    f'(x) ≈ [f(x+h) - f(x)] / h

Method 2: Central Difference (more accurate)
    f'(x) ≈ [f(x+h) - f(x-h)] / (2h)

Method 3: Using NumPy's gradient function
    np.gradient(y_values, x_values)
```

```python
import numpy as np

# Function: f(x) = sin(x)
# Exact derivative: f'(x) = cos(x)

def f(x):
    return np.sin(x)

x = 1.0  # Check at x = 1
h = 0.0001

# Method 1: Forward difference
forward = (f(x + h) - f(x)) / h

# Method 2: Central difference (more accurate)
central = (f(x + h) - f(x - h)) / (2 * h)

# Exact
exact = np.cos(x)

print("Derivative of sin(x) at x = 1:")
print(f"  Forward difference:  {forward:.10f}")
print(f"  Central difference:  {central:.10f}")
print(f"  Exact (cos(1)):      {exact:.10f}")
print(f"\n  Forward error:       {abs(forward - exact):.2e}")
print(f"  Central error:       {abs(central - exact):.2e}")
```

**Expected Output:**
```
Derivative of sin(x) at x = 1:
  Forward difference:  0.5402801884
  Central difference:  0.5403023059
  Exact (cos(1)):      0.5403023059

  Forward error:       2.21e-05
  Central error:       1.67e-11
```

**Line-by-line explanation:**
- The central difference is much more accurate than the forward difference. The error is 1 million times smaller!
- Always prefer the central difference method when computing numerical derivatives.

### Computing Derivatives of an Entire Array

```python
import numpy as np
import matplotlib.pyplot as plt

# Create data points for f(x) = x^3 - 3x
x = np.linspace(-3, 3, 200)
y = x**3 - 3*x

# Compute numerical derivative using np.gradient
dy_dx = np.gradient(y, x)

# Exact derivative: f'(x) = 3x^2 - 3
exact_derivative = 3*x**2 - 3

# Plot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(x, y, 'b-', linewidth=2)
axes[0].set_title('f(x) = x^3 - 3x')
axes[0].set_xlabel('x')
axes[0].set_ylabel('f(x)')
axes[0].grid(True, alpha=0.3)
axes[0].axhline(y=0, color='k', linewidth=0.5)

axes[1].plot(x, dy_dx, 'r-', linewidth=2, label='Numerical (np.gradient)')
axes[1].plot(x, exact_derivative, 'g--', linewidth=2, label='Exact (3x^2 - 3)')
axes[1].set_title("f'(x) = 3x^2 - 3")
axes[1].set_xlabel('x')
axes[1].set_ylabel("f'(x)")
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].axhline(y=0, color='k', linewidth=0.5)

plt.tight_layout()
plt.savefig('numerical_derivative.png', dpi=100, bbox_inches='tight')
plt.show()
print("Plot saved!")
```

**Expected Output:**
```
Plot saved!
```

The numerical derivative (red) matches the exact derivative (green dashed) almost perfectly.

---

## Why Derivatives Matter: Finding the Minimum

Here is the connection to machine learning. The derivative tells you which way is "downhill."

```
Finding the Minimum:

    f(x)
    |
    |  *                              *
    |    *                          *
    |      *                      *
    |        *      minimum     *
    |          *   here!      *
    |            * _______ *
    |              |
    +---+---+---+--+---+---+---+--> x

    At the minimum, the derivative is ZERO.
    f'(x) = 0 at the bottom.

    To the LEFT of the minimum:  f'(x) < 0  (slope goes down)
    To the RIGHT of the minimum: f'(x) > 0  (slope goes up)
    AT the minimum:              f'(x) = 0  (flat!)
```

### Finding the Minimum in Python

```python
import numpy as np
import matplotlib.pyplot as plt

# Function: f(x) = (x - 3)^2 + 2
# This is a parabola with minimum at x = 3, y = 2
# Derivative: f'(x) = 2(x - 3)
# Setting f'(x) = 0: 2(x - 3) = 0  -->  x = 3

def f(x):
    return (x - 3)**2 + 2

def f_prime(x):
    return 2 * (x - 3)

x = np.linspace(0, 6, 200)
y = f(x)
dy = f_prime(x)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Function plot
axes[0].plot(x, y, 'b-', linewidth=2)
axes[0].plot(3, f(3), 'ro', markersize=12, label='Minimum at x=3')
axes[0].set_title('f(x) = (x-3)^2 + 2')
axes[0].set_xlabel('x')
axes[0].set_ylabel('f(x)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Derivative plot
axes[1].plot(x, dy, 'g-', linewidth=2)
axes[1].axhline(y=0, color='k', linewidth=1)
axes[1].plot(3, 0, 'ro', markersize=12, label="f'(3) = 0 (minimum!)")
axes[1].fill_between(x[x < 3], dy[x < 3], alpha=0.2, color='red',
                      label='Negative slope (going down)')
axes[1].fill_between(x[x > 3], dy[x > 3], alpha=0.2, color='green',
                      label='Positive slope (going up)')
axes[1].set_title("f'(x) = 2(x-3)")
axes[1].set_xlabel('x')
axes[1].set_ylabel("f'(x)")
axes[1].legend(fontsize=9)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('finding_minimum.png', dpi=100, bbox_inches='tight')
plt.show()

# Find minimum numerically
print("Minimum is at x = 3")
print(f"f(3) = {f(3)}")
print(f"f'(3) = {f_prime(3)} (zero = flat = minimum!)")
```

**Expected Output:**
```
Minimum is at x = 3
f(3) = 2.0
f'(3) = 0.0 (zero = flat = minimum!)
```

**Line-by-line explanation:**
- The function has its lowest point at x=3 where f(3)=2.
- The derivative f'(3) = 0, confirming it is a minimum.
- To the left of x=3, the derivative is negative (function is decreasing).
- To the right of x=3, the derivative is positive (function is increasing).

---

## The Connection to Machine Learning

```
In Machine Learning:

    f(x) is the LOSS FUNCTION (measures how wrong the model is)
    x represents the MODEL PARAMETERS (weights)
    f'(x) tells you HOW TO ADJUST the parameters

    Goal: Find the x that makes f(x) as small as possible.
    Method: Use the derivative to walk downhill.

    This is called GRADIENT DESCENT.
    (You will learn it in detail in the next chapter!)

    Training Loop:
    1. Compute the loss (how wrong are we?)
    2. Compute the derivative (which way is downhill?)
    3. Take a small step downhill (update the weights)
    4. Repeat until you reach the bottom
```

---

## Common Mistakes

1. **Forgetting the chain rule.**
   - The derivative of (2x+1)^3 is NOT just 3(2x+1)^2. You must multiply by the inner derivative (2), giving 6(2x+1)^2.

2. **Using too large an h for numerical derivatives.**
   - h = 1 gives a terrible approximation. Use h = 0.0001 or smaller.
   - But do not make h too small (like 1e-15). Floating-point errors will creep in.

3. **Confusing partial derivatives with total derivatives.**
   - Partial derivatives change one variable and hold the rest constant.
   - You need ALL partial derivatives to know the full picture.

4. **Thinking the derivative IS the function.**
   - f(x) = x^2 is the function. f'(x) = 2x is the derivative. They are different things.
   - The derivative tells you the slope, not the value.

5. **Forgetting that derivative = 0 can also be a maximum.**
   - f'(x) = 0 at both peaks AND valleys. Check the second derivative or look at the graph to tell them apart.

---

## Best Practices

1. **Use central differences for numerical derivatives.** They are much more accurate than forward differences, with almost no extra work.

2. **Choose h = 1e-5 to 1e-7 for numerical derivatives.** This balances accuracy against floating-point errors.

3. **Always verify numerical derivatives against known formulas.** If you know the derivative formula, check that your numerical result matches.

4. **Draw the function and its derivative.** Seeing them together builds intuition. The derivative crosses zero wherever the function has a peak or valley.

5. **Practice the chain rule.** It appears constantly in machine learning, especially in backpropagation through neural networks.

---

## Quick Summary

```
Derivative Rules Cheat Sheet:

    Function          Derivative          Rule Name
    --------          ----------          ---------
    c (constant)      0                   Constant
    x^n               n * x^(n-1)         Power
    c * f(x)          c * f'(x)           Constant multiple
    f(x) + g(x)       f'(x) + g'(x)      Sum
    f(g(x))           f'(g(x)) * g'(x)   Chain

    Numerical Methods:
    Forward:   [f(x+h) - f(x)] / h
    Central:   [f(x+h) - f(x-h)] / (2h)     <-- Use this one!
    NumPy:     np.gradient(y_values, x_values)
```

---

## Key Points to Remember

1. A derivative measures the rate of change — how fast a function's output changes when you change the input.
2. Speed is the derivative of position. This is the most common real-life example.
3. The power rule is the most used rule: the derivative of x^n is n*x^(n-1).
4. The chain rule handles functions within functions: multiply the outer derivative by the inner derivative.
5. Partial derivatives change one variable at a time while holding all others constant.
6. The central difference method is the best way to compute derivatives numerically.
7. At a minimum, the derivative equals zero. This is how we find optimal solutions.
8. In machine learning, we use derivatives to find the minimum of the loss function. This is how models learn.

---

## Practice Questions

1. Using the power rule, what is the derivative of f(x) = 4x^3 + 2x^2 - 7x + 10?

2. What is the derivative of f(x) = (5x - 2)^4 using the chain rule?

3. If f(x, y) = x^2*y + 3y^2, what are the partial derivatives df/dx and df/dy?

4. Why is the central difference method more accurate than the forward difference method?

5. If the derivative of a loss function is negative at the current point, should you increase or decrease your parameter to reduce the loss? Why?

---

## Exercises

### Exercise 1: Derivative Calculator

Write a Python function that takes any function f, a point x, and a step size h, and returns the numerical derivative using the central difference method. Test it on f(x) = x^4 at x = 2. Compare with the exact answer (4*2^3 = 32).

**Hint:** Your function signature should be `def numerical_derivative(f, x, h=1e-5):`

### Exercise 2: Find the Minimum

The function f(x) = x^4 - 8x^2 + 5 has two local minima. Plot the function and its derivative on the range [-3, 3]. Find the approximate x values where f'(x) = 0 by looking at where the derivative crosses zero.

**Hint:** Use `np.gradient()` and look for sign changes.

### Exercise 3: Partial Derivative Surface

Create a 3D surface plot of f(x, y) = x^2 + y^2 using `matplotlib`'s `plot_surface`. Compute the partial derivatives numerically at the point (1, 1) and verify they match the exact values (df/dx = 2x = 2, df/dy = 2y = 2).

**Hint:** Use `from mpl_toolkits.mplot3d import Axes3D` and `ax.plot_surface()`.

---

## What Is Next?

You now know what derivatives are and how to compute them. But in machine learning, we do not have just one variable — we have thousands or millions of parameters. In the next chapter, you will learn about **gradients** (the multi-variable version of derivatives) and **gradient descent** — the algorithm that actually walks downhill to find the best parameters. This is the beating heart of how neural networks learn.
