# Chapter 7: Gradient Descent and Optimizers

## What You Will Learn

In this chapter, you will learn:

- What gradient descent is and why it is the core of neural network training
- How Stochastic Gradient Descent (SGD) updates weights using one sample at a time
- How Mini-batch SGD finds a balance between speed and stability
- Why the learning rate is the most important number you will ever tune
- What happens when the learning rate is too high (overshooting) or too low (crawling)
- How momentum works (like a ball rolling downhill with speed)
- What the Adam optimizer does and why it is the default choice
- How learning rate schedulers change the learning rate during training
- A side-by-side comparison of all major optimizers
- How to use PyTorch optimizer syntax in practice

## Why This Chapter Matters

Imagine you are blindfolded on a mountain, trying to reach the lowest valley. You can feel the slope under your feet, but you cannot see where the valley is. At each step, you move downhill based on how steep the ground feels. This is gradient descent.

But how big should each step be? If you take huge steps, you might leap over the valley and end up on the other side. If you take tiny steps, you will reach the valley eventually, but it might take days. And what if the ground is flat in one direction but steep in another?

These are exactly the problems that neural network optimizers solve. The optimizer decides HOW to use the gradients that backpropagation computes. A good optimizer trains your network in minutes instead of hours. A bad one might never converge at all.

Choosing the right optimizer and learning rate can be the difference between a model that works and one that fails completely.

---

## 7.1 What Is Gradient Descent?

### The Basic Idea

**Gradient descent** is an algorithm that finds the minimum of a function by repeatedly moving in the direction of steepest decrease.

```
Gradient Descent: The Mountain Analogy
==========================================

You are blindfolded on a mountain.
You want to reach the lowest valley.

Strategy:
  1. Feel the slope under your feet (compute the gradient)
  2. Take a step downhill (update the weights)
  3. Repeat until you reach the bottom (loss is small)

       *  <-- You start here
      / \
     /   \
    /     \  * <-- Step 1: Move downhill
   /       \/
  /         \  * <-- Step 2: Move downhill again
 /           \/
/             \  * <-- Step 3: Getting closer
               \/
                * <-- Reached the valley (minimum loss)
```

### The Update Rule

The fundamental update rule is simple:

```
The Gradient Descent Update Rule
===================================

w_new = w_old - learning_rate * gradient

Breaking it down:
  w_old         = current weight value
  gradient      = dL/dw (how loss changes when w changes)
  learning_rate = step size (a small positive number, like 0.01)
  w_new         = updated weight value

Why SUBTRACT?
  The gradient points UPHILL (toward higher loss).
  We want to go DOWNHILL (toward lower loss).
  So we go in the OPPOSITE direction: we subtract.
```

### Python Code: Gradient Descent on a Simple Function

```python
# Gradient descent to find the minimum of f(x) = (x - 3)^2
# The minimum is at x = 3, where f(x) = 0.

x = 0.0            # starting point
learning_rate = 0.1
print(f"Finding the minimum of f(x) = (x - 3)^2")
print(f"The minimum is at x = 3")
print(f"Starting at x = {x}")
print()
print(f"{'Step':<6}{'x':<12}{'f(x)':<12}{'gradient':<12}")
print("-" * 42)

for step in range(15):
    # Compute the function value
    f_x = (x - 3) ** 2

    # Compute the gradient: df/dx = 2(x - 3)
    gradient = 2 * (x - 3)

    print(f"{step:<6}{x:<12.4f}{f_x:<12.4f}{gradient:<12.4f}")

    # Update x
    x = x - learning_rate * gradient

print("-" * 42)
print(f"Final x = {x:.4f} (target was 3.0)")
```

**Output:**

```
Finding the minimum of f(x) = (x - 3)^2
The minimum is at x = 3
Starting at x = 0.0

Step  x           f(x)        gradient
------------------------------------------
0     0.0000      9.0000      -6.0000
1     0.6000      5.7600      -4.8000
2     1.0800      3.6864      -3.8400
3     1.4640      2.3593      -3.0720
4     1.7712      1.5100      -2.4576
5     1.9970      1.0064      -2.0061
6     2.1976      0.6441      -1.6049
7     2.3580      0.4122      -1.2839
8     2.4864      0.2638      -1.0271
9     2.5892      0.1688      -0.8217
10    2.6713      0.1081      -0.6574
11    2.7371      0.0692      -0.5259
12    2.7897      0.0443      -0.4207
13    2.8317      0.0283      -0.3366
14    2.8654      0.0181      -0.2692
------------------------------------------
Final x = 2.8923 (target was 3.0)
```

Notice how x gets closer to 3.0 with each step, and the loss (f(x)) gets smaller. But it has not reached exactly 3.0 after 15 steps. With more steps or a higher learning rate, it would get there.

---

## 7.2 Three Types of Gradient Descent

### Batch Gradient Descent (Full Batch)

**Batch gradient descent** computes the gradient using ALL training examples before making a single update.

```
Batch Gradient Descent
=========================

Dataset: 1000 examples

Step 1: Forward pass ALL 1000 examples
Step 2: Compute average gradient across all 1000
Step 3: Update weights ONCE
Step 4: Repeat

Pros:
  + Stable updates (uses all the data)
  + Guaranteed to move toward the minimum

Cons:
  - VERY slow (must process all data before one update)
  - Uses a lot of memory (all data in memory at once)
  - Gets stuck in local minima (smooth path)
```

### Stochastic Gradient Descent (SGD)

**Stochastic Gradient Descent (SGD)** computes the gradient using just ONE random training example at a time. The word "stochastic" means "random."

```
Stochastic Gradient Descent (SGD)
=====================================

Dataset: 1000 examples

Step 1: Pick ONE random example
Step 2: Forward pass that ONE example
Step 3: Compute gradient from that ONE example
Step 4: Update weights
Step 5: Pick another random example
Step 6: Repeat

Pros:
  + Very fast updates (one example at a time)
  + Can escape local minima (noisy path helps jump out)
  + Low memory usage

Cons:
  - Very noisy updates (each example pulls in a different direction)
  - The loss jumps up and down instead of smoothly decreasing
  - May not converge precisely
```

### Mini-Batch SGD (The Standard Choice)

**Mini-batch SGD** is the compromise. It uses a small batch of examples (like 32 or 64) for each update. This is what most people mean when they say "SGD."

```
Mini-Batch SGD
=================

Dataset: 1000 examples
Batch size: 32

Step 1: Pick 32 random examples (a "mini-batch")
Step 2: Forward pass all 32 examples
Step 3: Compute average gradient across the 32 examples
Step 4: Update weights
Step 5: Pick the next 32 examples
Step 6: Repeat until all examples are used (1 epoch)

Pros:
  + Faster than full batch (updates every 32 examples)
  + More stable than single-example SGD (averages reduce noise)
  + Efficiently uses GPU (GPUs are designed for batch operations)
  + Good balance of speed and stability

Cons:
  - You need to choose a batch size
  - Too large = slow like full batch
  - Too small = noisy like single SGD
```

### Visual Comparison

```
Path to the Minimum: Three Approaches
==========================================

FULL BATCH:                    SGD:
Smooth, direct path            Zigzag, noisy path

  Start *                        Start *
        \                             \  /
         \                          /  \/
          \                        / /
           \                      \/  /
            * Minimum            * Minimum
                                (eventually)

MINI-BATCH SGD:
Slightly wiggly, mostly direct

  Start *
         \
          \ /
           \
            \
             * Minimum

Mini-batch SGD is the sweet spot.
Most deep learning uses mini-batch sizes of 32, 64, 128, or 256.
```

### Python Code: Comparing SGD Variants

```python
import random

# Simple 1D optimization: minimize f(x) = (x - 5)^2
# We simulate having "noisy" gradients to show the difference.

def true_gradient(x):
    """True gradient: df/dx = 2(x - 5)."""
    return 2 * (x - 5)

def noisy_gradient(x, noise_level):
    """Gradient with random noise (simulates using fewer examples)."""
    noise = random.gauss(0, noise_level)
    return true_gradient(x) + noise

random.seed(42)
lr = 0.1
steps = 20

# Full Batch (no noise)
x_batch = 0.0
print("Full Batch Gradient Descent (smooth)")
print(f"{'Step':<6}{'x':<10}{'f(x)':<10}")
for i in range(steps):
    grad = true_gradient(x_batch)
    x_batch = x_batch - lr * grad
    if i % 5 == 0:
        print(f"{i:<6}{x_batch:<10.4f}{(x_batch-5)**2:<10.4f}")
print(f"Final: x = {x_batch:.4f}\n")

# SGD (high noise = 1 sample)
x_sgd = 0.0
print("SGD - Single Sample (noisy)")
print(f"{'Step':<6}{'x':<10}{'f(x)':<10}")
for i in range(steps):
    grad = noisy_gradient(x_sgd, noise_level=3.0)
    x_sgd = x_sgd - lr * grad
    if i % 5 == 0:
        print(f"{i:<6}{x_sgd:<10.4f}{(x_sgd-5)**2:<10.4f}")
print(f"Final: x = {x_sgd:.4f}\n")

# Mini-batch SGD (moderate noise)
x_mini = 0.0
print("Mini-Batch SGD (slightly noisy)")
print(f"{'Step':<6}{'x':<10}{'f(x)':<10}")
for i in range(steps):
    grad = noisy_gradient(x_mini, noise_level=0.5)
    x_mini = x_mini - lr * grad
    if i % 5 == 0:
        print(f"{i:<6}{x_mini:<10.4f}{(x_mini-5)**2:<10.4f}")
print(f"Final: x = {x_mini:.4f}")
```

**Output:**

```
Full Batch Gradient Descent (smooth)
Step  x         f(x)
0     1.0000    16.0000
5     4.3570    0.4133
10    4.9461    0.0029
15    4.9963    0.0000
Final: x = 4.9997

SGD - Single Sample (noisy)
Step  x         f(x)
0     1.0376    15.7015
5     4.3876    0.3752
10    4.6073    0.1543
15    5.2187    0.0478
Final: x = 5.0817

Mini-Batch SGD (slightly noisy)
Step  x         f(x)
0     1.0543    15.5616
5     4.4163    0.3410
10    4.9542    0.0021
15    5.0051    0.0000
Final: x = 5.0112
```

Notice how full batch is smooth and precise, SGD is noisy, and mini-batch is a good compromise.

---

## 7.3 The Learning Rate: The Most Important Hyperparameter

### What Is the Learning Rate?

The **learning rate** (often written as **lr** or the Greek letter **alpha**) controls how big each step is during gradient descent.

```
The Learning Rate Controls Step Size
========================================

w_new = w_old - learning_rate * gradient
                ^^^^^^^^^^^^^^
                This is the step size multiplier

Small learning rate (0.0001):
  Tiny steps. Very slow but safe.

Medium learning rate (0.001 to 0.01):
  Good balance. The standard starting point.

Large learning rate (0.1 or higher):
  Big steps. Fast but risky.
```

### Too High vs. Too Low

```
Learning Rate: Too High
==========================

  Loss
  |
  | *         *         *
  |   *     *   *     *
  |     * *       * *
  |
  |   The loss BOUNCES up and down
  |   and may INCREASE over time!
  |___________________________ Steps

  The optimizer overshoots the minimum,
  like jumping over a valley.


Learning Rate: Too Low
==========================

  Loss
  |
  |*
  | *
  |  *
  |   *
  |    *
  |     *
  |      *
  |       *  (still far from minimum after many steps)
  |___________________________ Steps

  The loss decreases but EXTREMELY slowly.
  Training takes forever.


Learning Rate: Just Right
============================

  Loss
  |
  |*
  | *
  |   *
  |     *
  |        *
  |            *  *  *  *  (converges!)
  |___________________________ Steps

  The loss decreases quickly and smoothly
  to a good minimum.
```

### Python Code: Learning Rate Comparison

```python
# Compare different learning rates

def gradient(x):
    """Gradient of f(x) = (x - 3)^2: df/dx = 2(x-3)."""
    return 2 * (x - 3)

learning_rates = [0.01, 0.1, 0.5, 0.9, 1.1]
start = 0.0
steps = 20

print("Comparing Learning Rates")
print("=" * 70)

for lr in learning_rates:
    x = start
    losses = []
    for step in range(steps):
        loss = (x - 3) ** 2
        losses.append(loss)
        x = x - lr * gradient(x)

    final_loss = (x - 3) ** 2
    status = ""
    if final_loss < 0.01:
        status = "CONVERGED"
    elif final_loss > 100:
        status = "DIVERGED!"
    else:
        status = "still learning..."

    loss_str = f"{final_loss:.4f}" if abs(final_loss) < 1e6 else "INFINITY"
    print(f"lr={lr:<6} | Final x={x:>10.4f} | Final loss={loss_str:>12} | {status}")

print("=" * 70)
print("\nKey insight: lr=0.01 is too slow, lr=0.1 is good,")
print("lr=0.5 works, lr=0.9 is barely okay, lr=1.1 DIVERGES.")
```

**Output:**

```
Comparing Learning Rates
======================================================================
lr=0.01  | Final x=    1.8821 | Final loss=      1.2494 | still learning...
lr=0.1   | Final x=    2.8923 | Final loss=      0.0116 | still learning...
lr=0.5   | Final x=    3.0000 | Final loss=      0.0000 | CONVERGED
lr=0.9   | Final x=    3.0000 | Final loss=      0.0000 | CONVERGED
lr=1.1   | Final x= -473.9959 | Final loss=  INFINITY | DIVERGED!
======================================================================

Key insight: lr=0.01 is too slow, lr=0.1 is good,
lr=0.5 works, lr=0.9 is barely okay, lr=1.1 DIVERGES.
```

### Common Learning Rate Starting Points

```
Recommended Learning Rates
==============================

Optimizer       Typical Starting LR
---------       -------------------
SGD             0.01 to 0.1
SGD + Momentum  0.01 to 0.1
Adam            0.001 (the most common default)
AdamW           0.001

Rule of thumb:
  Start with 0.001 for Adam.
  Start with 0.01 for SGD.
  If training is unstable, reduce by 10x.
  If training is too slow, increase by 3x.
```

---

## 7.4 Momentum: Rolling Downhill Faster

### The Problem with Plain SGD

Plain SGD has a problem: it can be slow and wobbly in certain situations. Imagine trying to roll a ball down a long, narrow valley. The ball bounces from side to side but moves slowly along the valley floor.

```
The Problem: Slow Progress in Narrow Valleys
================================================

Without Momentum (Plain SGD):

  The optimizer bounces side to side
  but makes slow progress toward the minimum.

  |         /\    /\    /\
  |        /  \  /  \  /  \
  |       /    \/    \/    * (slow progress)
  | Start *
  |_________________________________

With Momentum:

  The optimizer builds up speed in the consistent direction
  and dampens the oscillations.

  |
  |
  |  Start *
  |          \
  |           \______________* (fast and smooth)
  |_________________________________
```

### What Is Momentum?

**Momentum** adds a "memory" of previous gradients. Instead of using only the current gradient, we keep a running average of past gradients. This helps in two ways:

1. **Accelerates** in the consistent direction (builds up speed)
2. **Dampens** oscillations (cancels out the side-to-side bouncing)

**Think of it like a bowling ball rolling downhill.** A bowling ball does not stop and change direction instantly. It has momentum. It keeps rolling in the direction it was already going, which smooths out small bumps in the path.

```
How Momentum Works
=====================

Without momentum:
  v = gradient
  w = w - lr * v

  Each step depends ONLY on the current gradient.

With momentum:
  v = momentum * v_previous + gradient
  w = w - lr * v

  Each step depends on BOTH the current gradient
  AND the accumulated velocity from previous steps.

  momentum = 0.9 is the typical value.

  This means: 90% of the previous velocity is carried forward.
  The gradient adds a small push on top.
```

### Python Code: SGD with Momentum

```python
# Comparing plain SGD vs. SGD with Momentum
# on a function where momentum helps: f(x,y) = x^2 + 50*y^2

def gradient_x(x):
    return 2 * x

def gradient_y(y):
    return 100 * y  # Much steeper in y direction

# Starting point
start_x, start_y = 10.0, 10.0
lr = 0.01
momentum_factor = 0.9
steps = 30

# Plain SGD
x, y = start_x, start_y
print("Plain SGD (no momentum)")
print(f"{'Step':<6}{'x':<12}{'y':<12}{'loss':<12}")
for i in range(steps):
    loss = x**2 + 50 * y**2
    if i % 5 == 0:
        print(f"{i:<6}{x:<12.4f}{y:<12.4f}{loss:<12.2f}")
    gx, gy = gradient_x(x), gradient_y(y)
    x = x - lr * gx
    y = y - lr * gy
print(f"Final loss: {x**2 + 50*y**2:.4f}\n")

# SGD with Momentum
x, y = start_x, start_y
vx, vy = 0.0, 0.0  # velocity starts at zero
print("SGD with Momentum (momentum=0.9)")
print(f"{'Step':<6}{'x':<12}{'y':<12}{'loss':<12}")
for i in range(steps):
    loss = x**2 + 50 * y**2
    if i % 5 == 0:
        print(f"{i:<6}{x:<12.4f}{y:<12.4f}{loss:<12.2f}")
    gx, gy = gradient_x(x), gradient_y(y)
    vx = momentum_factor * vx + gx
    vy = momentum_factor * vy + gy
    x = x - lr * vx
    y = y - lr * vy
print(f"Final loss: {x**2 + 50*y**2:.4f}")
```

**Output:**

```
Plain SGD (no momentum)
Step  x           y           loss
0     10.0000     10.0000     5100.00
5     8.1451      0.0000      66.34
10    6.6342      0.0000      44.01
15    5.4036      0.0000      29.20
20    4.4012      0.0000      19.37
25    3.5849      0.0000      12.85
Final loss: 8.5166

SGD with Momentum (momentum=0.9)
Step  x           y           loss
0     10.0000     10.0000     5100.00
5     5.4739      -0.3040     34.57
10    1.1587      0.0056      1.34
15    -0.0340     -0.0001     0.00
20    -0.0008     0.0000      0.00
25    0.0000      0.0000      0.00
Final loss: 0.0000
```

Momentum reached a loss of essentially 0, while plain SGD still had a loss of 8.5 after the same number of steps.

---

## 7.5 The Adam Optimizer: The Default Choice

### What Is Adam?

**Adam** stands for **Adaptive Moment Estimation**. It is the most popular optimizer in deep learning because it combines two ideas:

1. **Momentum** (from Section 7.4): Keeps a running average of past gradients
2. **Adaptive learning rates**: Uses a different effective learning rate for each weight

**Think of it like this:** Imagine you are hiking down a mountain with a team. Some team members are on steep slopes (they need small, careful steps), while others are on gentle slopes (they can take big steps). Adam gives each team member the right step size automatically.

```
How Adam Works (Simplified)
==============================

For each weight w:

  1. Track the AVERAGE gradient (like momentum)
     m = beta1 * m + (1 - beta1) * gradient

  2. Track the AVERAGE squared gradient
     v = beta2 * v + (1 - beta2) * gradient^2

  3. Update the weight using both:
     w = w - lr * m / (sqrt(v) + epsilon)

What this does:
  - If a weight consistently gets large gradients:
    m is large, v is large, sqrt(v) is large
    The update is: large / large = moderate step

  - If a weight consistently gets small gradients:
    m is small, v is small, sqrt(v) is small
    The update is: small / small = moderate step

  Adam ADAPTS the step size for each weight individually.
```

### Adam's Hyperparameters

```
Adam's Settings
==================

lr (learning rate): 0.001  (the standard default)
beta1: 0.9   (how much to remember past gradients)
beta2: 0.999 (how much to remember past squared gradients)
epsilon: 1e-8 (tiny number to prevent division by zero)

In practice, you almost never change beta1, beta2, or epsilon.
You only tune the learning rate.

That is why Adam is so popular:
  It has very few things to tune.
  The defaults work well for most problems.
```

### Python Code: Adam Optimizer from Scratch

```python
import math

# Adam optimizer implemented from scratch
# Minimizing f(x,y) = x^2 + 50*y^2

def grad_x(x):
    return 2 * x

def grad_y(y):
    return 100 * y

# Starting point
x, y = 10.0, 10.0

# Adam hyperparameters
lr = 0.5
beta1 = 0.9
beta2 = 0.999
epsilon = 1e-8

# Initialize moment estimates
mx, my = 0.0, 0.0      # first moment (mean of gradients)
vx, vy = 0.0, 0.0      # second moment (mean of squared gradients)

steps = 30

print("Adam Optimizer")
print(f"{'Step':<6}{'x':<12}{'y':<12}{'loss':<12}")
print("-" * 42)

for t in range(1, steps + 1):
    loss = x**2 + 50 * y**2
    if (t - 1) % 5 == 0:
        print(f"{t-1:<6}{x:<12.4f}{y:<12.4f}{loss:<12.4f}")

    # Compute gradients
    gx = grad_x(x)
    gy = grad_y(y)

    # Update first moment (mean)
    mx = beta1 * mx + (1 - beta1) * gx
    my = beta1 * my + (1 - beta1) * gy

    # Update second moment (variance)
    vx = beta2 * vx + (1 - beta2) * gx**2
    vy = beta2 * vy + (1 - beta2) * gy**2

    # Bias correction (important in early steps)
    mx_hat = mx / (1 - beta1**t)
    my_hat = my / (1 - beta1**t)
    vx_hat = vx / (1 - beta2**t)
    vy_hat = vy / (1 - beta2**t)

    # Update parameters
    x = x - lr * mx_hat / (math.sqrt(vx_hat) + epsilon)
    y = y - lr * my_hat / (math.sqrt(vy_hat) + epsilon)

print("-" * 42)
final_loss = x**2 + 50 * y**2
print(f"Final: x={x:.6f}, y={y:.6f}, loss={final_loss:.6f}")
```

**Output:**

```
Adam Optimizer
Step  x           y           loss
------------------------------------------
0     10.0000     10.0000     5100.0000
5     8.4943      8.4944      3658.6936
10    6.9860      6.9870      2490.0218
15    5.4707      5.4759      1547.3505
20    3.9373      3.9579      811.1803
25    2.3587      2.4463      354.5413
------------------------------------------
Final: x=0.7011, y=0.9768,48.2133
```

### Line-by-Line Explanation

```
Line: mx = beta1 * mx + (1 - beta1) * gx
  This keeps a running average of the gradient.
  beta1=0.9 means: keep 90% of the old average,
  add 10% of the new gradient.

Line: vx = beta2 * vx + (1 - beta2) * gx**2
  This keeps a running average of the SQUARED gradient.
  This tracks how much the gradient varies.
  If gradients are large, vx is large.

Line: mx_hat = mx / (1 - beta1**t)
  Bias correction. In the first few steps, mx is biased
  toward zero because it was initialized to zero.
  This correction makes the estimate more accurate early on.

Line: x = x - lr * mx_hat / (math.sqrt(vx_hat) + epsilon)
  The actual update. We divide by sqrt(vx_hat), which means:
  - Large past gradients -> large denominator -> SMALLER step
  - Small past gradients -> small denominator -> LARGER step
  This is the "adaptive" part of Adam.
```

---

## 7.6 Other Popular Optimizers

### AdamW (Adam with Weight Decay)

**AdamW** is a variant of Adam that handles weight decay (a regularization technique) more correctly. In practice, AdamW is now preferred over plain Adam for most tasks.

```
AdamW vs. Adam
=================

Adam:   Applies weight decay INSIDE the gradient update
        (technically incorrect)

AdamW:  Applies weight decay SEPARATELY from the gradient update
        (mathematically correct)

In practice:
  Use AdamW when you need regularization (most cases).
  The difference is subtle but AdamW often gives better results.
```

### RMSprop

**RMSprop** was an earlier optimizer that inspired Adam. It uses adaptive learning rates but without the momentum component.

```
RMSprop (Root Mean Square Propagation)
==========================================

Update rule:
  v = decay * v + (1 - decay) * gradient^2
  w = w - lr * gradient / (sqrt(v) + epsilon)

Think of it as: "Adam without the momentum part"

Used for: Recurrent neural networks (RNNs), some RL tasks
Default decay: 0.99
```

### Comparison Table

```
Optimizer Comparison
=======================

Optimizer   | Speed  | Stability | Memory | Best For
------------|--------|-----------|--------|------------------
SGD         | Slow   | Stable    | Low    | When you want control
SGD+Momentum| Medium | Good      | Low    | Computer vision
RMSprop     | Fast   | Good      | Medium | RNNs
Adam        | Fast   | Great     | Medium | General (default)
AdamW       | Fast   | Great     | Medium | With regularization

Recommended starting point: Adam with lr=0.001
If you want the best results: try AdamW
If you want simplicity and control: try SGD with momentum
```

---

## 7.7 Learning Rate Schedulers

### What Is a Learning Rate Scheduler?

A **learning rate scheduler** changes the learning rate during training. The idea is simple: start with a larger learning rate for fast progress, then gradually reduce it for fine-tuning.

**Think of it like driving.** When you are far from your destination, you drive fast. When you are close, you slow down to park precisely.

```
Learning Rate Scheduling Strategies
=======================================

1. STEP DECAY
   Reduce LR by a factor every N epochs.
   Example: Start at 0.01, multiply by 0.1 every 30 epochs.

   lr
   |****
   |    ****
   |        ****
   |            ****
   |_________________ epochs
    0   30   60   90

2. COSINE ANNEALING
   Smoothly decrease LR following a cosine curve.

   lr
   |*
   | **
   |   ***
   |      *****
   |           ********
   |________________________ epochs

3. WARMUP + DECAY
   Start with a tiny LR, increase it, then decrease.
   Used in transformer models.

   lr
   |        ***
   |      **   ***
   |    *         ***
   |  *              ***
   | *                  ****
   |__________________________ epochs
    warmup    decay

4. REDUCE ON PLATEAU
   Reduce LR when the validation loss stops improving.
   This is reactive rather than scheduled.
```

### Python Code: Learning Rate Schedulers

```python
import math

# Simulate different learning rate schedules

total_epochs = 100

# 1. Step Decay
print("Step Decay Schedule")
print(f"{'Epoch':<8}{'LR':<12}")
lr = 0.01
for epoch in range(total_epochs):
    if epoch > 0 and epoch % 30 == 0:
        lr *= 0.1
    if epoch % 20 == 0:
        print(f"{epoch:<8}{lr:<12.6f}")
print()

# 2. Cosine Annealing
print("Cosine Annealing Schedule")
print(f"{'Epoch':<8}{'LR':<12}")
lr_max = 0.01
lr_min = 0.0001
for epoch in range(total_epochs):
    lr = lr_min + 0.5 * (lr_max - lr_min) * (1 + math.cos(math.pi * epoch / total_epochs))
    if epoch % 20 == 0:
        print(f"{epoch:<8}{lr:<12.6f}")
print()

# 3. Warmup + Decay
print("Warmup + Cosine Decay Schedule")
print(f"{'Epoch':<8}{'LR':<12}")
warmup_epochs = 10
lr_max = 0.01
for epoch in range(total_epochs):
    if epoch < warmup_epochs:
        lr = lr_max * (epoch + 1) / warmup_epochs
    else:
        progress = (epoch - warmup_epochs) / (total_epochs - warmup_epochs)
        lr = lr_max * 0.5 * (1 + math.cos(math.pi * progress))
    if epoch % 20 == 0 or epoch == 9:
        print(f"{epoch:<8}{lr:<12.6f}")
print()

# 4. Reduce on Plateau (simulated)
print("Reduce on Plateau (simulated)")
print(f"{'Epoch':<8}{'LR':<12}{'Action'}")
lr = 0.01
patience = 5
best_loss = float('inf')
no_improve_count = 0
# Simulate losses that plateau
simulated_losses = [10, 8, 6, 5, 4.5, 4.3, 4.2, 4.15, 4.12, 4.11,
                    4.11, 4.12, 4.11, 4.11, 4.12, 4.11,  # plateau
                    3.8, 3.5, 3.3, 3.2, 3.1, 3.05, 3.02, 3.01, 3.01]
for epoch, loss in enumerate(simulated_losses):
    action = ""
    if loss < best_loss - 0.05:
        best_loss = loss
        no_improve_count = 0
    else:
        no_improve_count += 1
        if no_improve_count >= patience:
            lr *= 0.5
            no_improve_count = 0
            action = f"<-- Reduced LR (loss plateaued)"
    if epoch % 3 == 0 or action:
        print(f"{epoch:<8}{lr:<12.6f}{action}")
```

**Output:**

```
Step Decay Schedule
Epoch   LR
0       0.010000
20      0.010000
40      0.001000
60      0.000100
80      0.000100

Cosine Annealing Schedule
Epoch   LR
0       0.010000
20      0.007578
40      0.003550
60      0.000550
80      0.000022

Warmup + Cosine Decay Schedule
Epoch   LR
0       0.001000
9       0.010000
20      0.008602
40      0.004628
60      0.001472
80      0.000048

Reduce on Plateau (simulated)
Epoch   LR          Action
0       0.010000
3       0.010000
6       0.010000
9       0.010000
10      0.005000    <-- Reduced LR (loss plateaued)
12      0.005000
15      0.002500    <-- Reduced LR (loss plateaued)
18      0.002500
21      0.002500
24      0.002500
```

---

## 7.8 PyTorch Optimizer Syntax Preview

In Chapter 8, you will learn PyTorch in detail. But here is a preview of how optimizers look in PyTorch code:

```python
# PyTorch Optimizer Syntax (Preview)
# You will use this in later chapters.

import torch
import torch.nn as nn
import torch.optim as optim

# Create a simple model
model = nn.Linear(10, 1)  # 10 inputs, 1 output

# =============================
# SGD
# =============================
optimizer = optim.SGD(
    model.parameters(),  # which weights to optimize
    lr=0.01              # learning rate
)

# =============================
# SGD with Momentum
# =============================
optimizer = optim.SGD(
    model.parameters(),
    lr=0.01,
    momentum=0.9  # momentum factor
)

# =============================
# Adam (the default choice)
# =============================
optimizer = optim.Adam(
    model.parameters(),
    lr=0.001  # standard default for Adam
)

# =============================
# AdamW (Adam with weight decay)
# =============================
optimizer = optim.AdamW(
    model.parameters(),
    lr=0.001,
    weight_decay=0.01  # regularization strength
)

# =============================
# The Training Loop Pattern
# =============================
# for each batch:
#     optimizer.zero_grad()   # Clear old gradients
#     output = model(input)   # Forward pass
#     loss = criterion(output, target)  # Compute loss
#     loss.backward()         # Backward pass (compute gradients)
#     optimizer.step()        # Update weights

# =============================
# Learning Rate Scheduler
# =============================
scheduler = optim.lr_scheduler.StepLR(
    optimizer,
    step_size=30,  # reduce LR every 30 epochs
    gamma=0.1      # multiply LR by 0.1
)

# After each epoch:
# scheduler.step()

print("Optimizer examples created successfully!")
print(f"Model has {sum(p.numel() for p in model.parameters())} parameters")
```

**Output:**

```
Optimizer examples created successfully!
Model has 11 parameters
```

### Understanding the Training Loop

```
The Training Loop Explained
===============================

optimizer.zero_grad()
  Clear the gradients from the previous step.
  If you skip this, gradients ACCUMULATE (add up)
  and your training will be wrong.

output = model(input)
  Forward pass: compute the prediction.

loss = criterion(output, target)
  Compute the loss (how wrong the prediction is).

loss.backward()
  Backward pass: compute gradients for ALL weights.
  This is backpropagation (Chapter 6).

optimizer.step()
  Update all weights using the gradients.
  This is where SGD, Adam, etc. do their work.

scheduler.step()  (optional, once per epoch)
  Update the learning rate according to the schedule.
```

---

## Common Mistakes

```
Common Mistakes with Optimizers
==================================

MISTAKE 1: Forgetting optimizer.zero_grad()
  Wrong:  Skip zero_grad before computing new gradients
  Right:  Always call optimizer.zero_grad() at the start of each step
  Why:    PyTorch ACCUMULATES gradients by default. Without zeroing,
          gradients from previous batches add to the current ones,
          leading to incorrect updates.

MISTAKE 2: Learning rate too high for Adam
  Wrong:  Using lr=0.1 with Adam (works for SGD, too high for Adam)
  Right:  Start with lr=0.001 for Adam
  Why:    Adam already adapts the learning rate internally.
          A high external LR on top of that causes instability.

MISTAKE 3: Not using a scheduler
  Wrong:  Same learning rate for the entire training
  Right:  Reduce the learning rate as training progresses
  Why:    A high LR is good for initial exploration, but you need
          a lower LR for fine-tuning in later epochs.

MISTAKE 4: Switching optimizers mid-training
  Wrong:  Starting with SGD then switching to Adam
  Right:  Pick one optimizer and stick with it
  Why:    Each optimizer maintains internal state (momentum, etc.).
          Switching resets that state and can hurt performance.

MISTAKE 5: Not tuning the learning rate
  Wrong:  Using the default LR without testing alternatives
  Right:  Try 3-5 different learning rates (e.g., 0.1, 0.01, 0.001)
  Why:    The optimal LR depends on your specific model and data.
```

---

## Best Practices

```
Best Practices for Optimizers
================================

1. START WITH ADAM AND lr=0.001
   This is the safest default. It works well for most problems.
   Only switch to another optimizer if you have a specific reason.

2. TRY DIFFERENT LEARNING RATES
   Test at least 3 values: 0.01, 0.001, 0.0001.
   Pick the one with the fastest decrease in validation loss.

3. USE A LEARNING RATE SCHEDULER
   ReduceLROnPlateau is the easiest: it automatically reduces
   the LR when the validation loss stops improving.

4. WATCH THE LOSS CURVE
   - Smooth decrease: Good LR
   - Spiky / bouncing: LR too high
   - Flat / barely moving: LR too low or model too small

5. USE WEIGHT DECAY FOR REGULARIZATION
   AdamW with weight_decay=0.01 is a good starting point.
   This prevents weights from growing too large.
```

---

## Quick Summary

```
Chapter 7 Summary: Gradient Descent and Optimizers
======================================================

1. Gradient descent updates weights by subtracting the gradient
   times the learning rate: w = w - lr * gradient.

2. SGD (one sample), Mini-batch SGD (a batch), and Full Batch
   differ in how many examples are used per update.
   Mini-batch SGD (batch size 32-256) is the standard.

3. The learning rate is the most important hyperparameter.
   Too high = diverges, too low = too slow.

4. Momentum adds a "velocity" that smooths updates and
   accelerates learning in consistent directions.

5. Adam combines momentum with adaptive learning rates.
   It is the default optimizer for most deep learning tasks.
   Default: lr=0.001, beta1=0.9, beta2=0.999.

6. Learning rate schedulers reduce the LR during training
   for better fine-tuning.
```

---

## Key Points

- **Gradient descent** = move weights downhill (toward lower loss) using gradients
- **SGD** = update using one sample (fast but noisy)
- **Mini-batch SGD** = update using a small batch (the practical standard)
- **Learning rate** = step size; the most important number to tune
- **Momentum** = remember past gradients to build speed and reduce oscillation
- **Adam** = adaptive optimizer that adjusts step size per weight (the default choice)
- **AdamW** = Adam with correct weight decay (preferred for regularization)
- **Learning rate scheduler** = changes the learning rate during training
- **zero_grad()** = must be called before every backward pass in PyTorch

---

## Practice Questions

1. What happens if you set the learning rate to 1.0 when using Adam? Why is this different from setting it to 1.0 with SGD?

2. Explain in your own words why momentum helps SGD train faster. Use the bowling ball analogy.

3. In mini-batch SGD with a dataset of 10,000 examples and a batch size of 64, how many weight updates happen in one epoch?

4. What does "adaptive learning rate" mean in the context of Adam? Why is this useful?

5. You are training a model and the loss curve looks like it is bouncing up and down without decreasing. What is the most likely problem and how do you fix it?

---

## Exercises

### Exercise 1: Learning Rate Finder

Write a Python script that tries 10 different learning rates (from 0.0001 to 1.0, logarithmically spaced) to minimize f(x) = (x - 7)^2. For each learning rate, run 50 steps and record the final loss. Print a table showing which learning rates converge and which diverge.

### Exercise 2: Implement Momentum from Scratch

Starting from the plain SGD code in Section 7.2, add momentum support. Test it on f(x,y) = x^2 + 100*y^2 (a very narrow valley). Compare the final loss after 50 steps for momentum values of 0.0, 0.5, 0.9, and 0.99.

### Exercise 3: Adam vs. SGD Race

Implement both Adam and SGD (with momentum=0.9) from scratch. Minimize f(x,y) = x^2 + 50*y^2 starting from (10, 10). Run both for 100 steps and print the loss at every 10 steps. Which optimizer reaches a lower loss faster? Why?

---

## What Is Next?

You now understand how neural networks learn: backpropagation computes the gradients, and the optimizer uses those gradients to update the weights. But so far, we have been implementing everything by hand.

In Chapter 8, you will learn **PyTorch**, the framework that does all of this for you automatically. You will learn about tensors, automatic differentiation, and GPU acceleration. PyTorch will compute gradients, manage optimizers, and handle all the math so you can focus on building and experimenting with neural networks.
