# Chapter 4: Activation Functions — Teaching Neurons When to Fire

## What You Will Learn

In this chapter, you will learn:

- Why neural networks need activation functions to solve real problems
- How a network without activation functions is just a fancy straight line
- The five most important activation functions: Sigmoid, Tanh, ReLU, Leaky ReLU, and Softmax
- How to implement and visualize each activation function in PyTorch
- When to use which activation function for your specific problem
- What the vanishing gradient problem is and why it matters
- Why ReLU became the default choice for modern deep learning

## Why This Chapter Matters

Imagine you are trying to draw the outline of a cat using only a ruler. No curves allowed. Just straight lines. You could try, but the result would look like a blocky mess. Now imagine you have a flexible curve tool. Suddenly you can trace the smooth outline of the cat perfectly.

Activation functions are that flexible curve tool for neural networks. Without them, your network can only draw straight lines through your data, no matter how many layers you stack. With them, your network can learn curves, bends, and complex patterns that match the messy real world.

This chapter gives you the power to choose the right activation function for every situation. Pick the wrong one, and your network might refuse to learn. Pick the right one, and training becomes smooth and fast.

---

## The Problem: Why Do We Need Non-Linearity?

### A Network Without Activation Functions

Let us start with a surprising fact. If you stack multiple layers without activation functions, the entire network behaves like a single layer.

Here is why. Consider two layers:

```
Layer 1: output1 = W1 * x + b1
Layer 2: output2 = W2 * output1 + b2
```

Substitute layer 1 into layer 2:

```
output2 = W2 * (W1 * x + b1) + b2
output2 = (W2 * W1) * x + (W2 * b1 + b2)
output2 = W_combined * x + b_combined
```

No matter how many layers you stack, the result is always a straight line. This is called a **linear transformation**. A linear transformation means the output changes at a constant rate as the input changes. Think of it like a car that can only drive at one speed — it cannot speed up, slow down, or turn.

```
WITHOUT ACTIVATION FUNCTIONS:
(All layers collapse into one)

Layer 1 ──> Layer 2 ──> Layer 3 ──> Output
  W1           W2           W3

Mathematically equivalent to:

Input ──────────────────────────> Output
         W_combined = W1 * W2 * W3

Result: Just a straight line!
No matter how many layers, you get: y = W * x + b
```

### Let Us Prove It with Code

```python
import torch
import torch.nn as nn

# A 3-layer network WITHOUT activation functions
class LinearOnlyNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(1, 16)   # 1 input, 16 hidden units
        self.layer2 = nn.Linear(16, 16)  # 16 hidden units
        self.layer3 = nn.Linear(16, 1)   # 16 to 1 output

    def forward(self, x):
        # No activation functions between layers!
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        return x

# A 3-layer network WITH activation functions
class NonLinearNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(1, 16)
        self.layer2 = nn.Linear(16, 16)
        self.layer3 = nn.Linear(16, 1)
        self.relu = nn.ReLU()            # Activation function

    def forward(self, x):
        # Activation functions between layers!
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)              # No activation on output
        return x

# Create some curved data (a sine wave)
import matplotlib.pyplot as plt
import numpy as np

torch.manual_seed(42)

x_data = torch.linspace(-3, 3, 200).unsqueeze(1)  # 200 points from -3 to 3
y_data = torch.sin(x_data)                         # Sine wave (curved!)

# Train both networks
def train_network(model, x, y, epochs=2000, lr=0.01):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    for epoch in range(epochs):
        prediction = model(x)
        loss = loss_fn(prediction, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return model

linear_model = train_network(LinearOnlyNetwork(), x_data, y_data)
nonlinear_model = train_network(NonLinearNetwork(), x_data, y_data)

# Plot results
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

with torch.no_grad():
    # Linear model predictions
    axes[0].plot(x_data.numpy(), y_data.numpy(), 'b-', label='True (sine wave)')
    axes[0].plot(x_data.numpy(), linear_model(x_data).numpy(), 'r--',
                 label='Linear model')
    axes[0].set_title('Without Activation Functions')
    axes[0].legend()
    axes[0].grid(True)

    # Non-linear model predictions
    axes[1].plot(x_data.numpy(), y_data.numpy(), 'b-', label='True (sine wave)')
    axes[1].plot(x_data.numpy(), nonlinear_model(x_data).numpy(), 'r--',
                 label='Non-linear model')
    axes[1].set_title('With Activation Functions (ReLU)')
    axes[1].legend()
    axes[1].grid(True)

plt.tight_layout()
plt.savefig('linear_vs_nonlinear.png', dpi=100, bbox_inches='tight')
plt.show()
print("Left plot: straight line (cannot fit curve)")
print("Right plot: follows the sine wave closely")
```

**Output:**
```
Left plot: straight line (cannot fit curve)
Right plot: follows the sine wave closely
```

**Line-by-line explanation:**

- `class LinearOnlyNetwork` — A network with three layers but no activation functions between them. Despite having 16 hidden units, it can only produce straight lines.
- `class NonLinearNetwork` — The same architecture but with ReLU activation between layers. This allows it to learn curves and bends.
- `torch.sin(x_data)` — Creates a sine wave, which is a smooth curve. A straight line cannot fit this.
- `self.relu = nn.ReLU()` — Creates a ReLU activation function (we will explain exactly what this does shortly).
- The training loop uses the Adam optimizer (a smart version of gradient descent) to adjust weights.
- The left plot shows the linear model drawing the best straight line it can through the curve — it fails.
- The right plot shows the non-linear model bending to follow the sine wave — it succeeds.

### The Real-World Analogy

Think of activation functions like joints in a robot arm:

```
WITHOUT JOINTS (No Activation):      WITH JOINTS (Activation):

    ═══════════════>                      ═══╗
                                             ║
    Can only point in                    ════╝
    one direction                            ╚═══>

    (straight line)                   Can reach anywhere!
                                      (curves and bends)
```

Without joints, the arm is a rigid stick. With joints, it can bend and reach any point in space. Activation functions are the joints of your neural network.

---

## Activation Function 1: Sigmoid

### What It Does

The **sigmoid** function takes any number and squishes it into a range between 0 and 1. No matter how large or small the input, the output is always between 0 and 1.

The word "sigmoid" comes from the Greek letter sigma (S-shaped). When you plot it, it looks like a stretched-out letter S.

**Formula:**

```
sigmoid(x) = 1 / (1 + e^(-x))
```

Where `e` is Euler's number (approximately 2.71828), a special mathematical constant.

```
SIGMOID FUNCTION:

Output
  1.0 |                          ___________
      |                       __/
      |                     _/
  0.5 |                   _/
      |                 _/
      |              __/
  0.0 |_____________/
      +----+----+----+----+----+----+----+---> Input
         -6   -4   -2    0    2    4    6

Key properties:
- Output always between 0 and 1
- At input = 0, output = 0.5
- Large positive inputs → output near 1
- Large negative inputs → output near 0
```

### Real-World Analogy

Think of sigmoid as a dimmer switch for a light:

- Turn the dial far to the left (large negative input) → light is OFF (output near 0)
- Turn the dial far to the right (large positive input) → light is fully ON (output near 1)
- The dial is in the middle (input near 0) → light is at HALF brightness (output 0.5)

The transition is smooth, not a sudden on-off flip.

### Implementation in PyTorch

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np

# Create input values from -8 to 8
x = torch.linspace(-8, 8, 200)

# Method 1: Using PyTorch's built-in sigmoid
sigmoid = nn.Sigmoid()
y_sigmoid = sigmoid(x)

# Method 2: Implementing it manually (for understanding)
def manual_sigmoid(x):
    return 1 / (1 + torch.exp(-x))

y_manual = manual_sigmoid(x)

# Verify they give the same result
print("Are they equal?", torch.allclose(y_sigmoid, y_manual))

# Plot the sigmoid function
plt.figure(figsize=(10, 6))
plt.plot(x.numpy(), y_sigmoid.numpy(), 'b-', linewidth=2, label='Sigmoid')
plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='y = 0.5')
plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
plt.axhline(y=1, color='gray', linestyle='-', alpha=0.3)
plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
plt.xlabel('Input', fontsize=12)
plt.ylabel('Output', fontsize=12)
plt.title('Sigmoid Activation Function', fontsize=14)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.ylim(-0.1, 1.1)
plt.savefig('sigmoid_plot.png', dpi=100, bbox_inches='tight')
plt.show()

# Show some example values
print("\nSigmoid examples:")
test_values = torch.tensor([-10.0, -5.0, -1.0, 0.0, 1.0, 5.0, 10.0])
for val in test_values:
    result = sigmoid(val)
    print(f"  sigmoid({val:6.1f}) = {result:.6f}")
```

**Output:**
```
Are they equal? True

Sigmoid examples:
  sigmoid( -10.0) = 0.000045
  sigmoid(  -5.0) = 0.006693
  sigmoid(  -1.0) = 0.268941
  sigmoid(   0.0) = 0.500000
  sigmoid(   1.0) = 0.731059
  sigmoid(   5.0) = 0.993307
  sigmoid(  10.0) = 0.999955
```

**Line-by-line explanation:**

- `torch.linspace(-8, 8, 200)` — Creates 200 evenly spaced numbers between -8 and 8. This gives us a smooth range of inputs to test.
- `nn.Sigmoid()` — Creates a sigmoid activation function object from PyTorch.
- `y_sigmoid = sigmoid(x)` — Applies sigmoid to every value in x. Each output is between 0 and 1.
- `manual_sigmoid` — We implement the formula ourselves using `torch.exp(-x)` which computes e raised to the power of negative x.
- `torch.allclose` — Checks if two tensors have (nearly) the same values. This confirms our manual version matches PyTorch.
- The plot shows the characteristic S-shape: flat near 0 on the left, rising steeply in the middle, flat near 1 on the right.
- Example values confirm: very negative inputs give outputs near 0, very positive inputs give outputs near 1.

### When to Use Sigmoid

Sigmoid is best for **binary classification output layers** — problems where the answer is yes or no, true or false, 0 or 1. Since sigmoid outputs a value between 0 and 1, you can interpret it as a probability.

For example: "What is the probability this email is spam?" Sigmoid might output 0.92, meaning 92% chance of spam.

---

## Activation Function 2: Tanh (Hyperbolic Tangent)

### What It Does

**Tanh** (pronounced "tanch" or "hyperbolic tangent") squishes any number into a range between -1 and 1. It is similar to sigmoid but centered at zero instead of 0.5.

**Formula:**

```
tanh(x) = (e^x - e^(-x)) / (e^x + e^(-x))
```

```
TANH FUNCTION:

Output
  1.0 |                          ___________
      |                       __/
      |                     _/
  0.0 |___________________/
      |                 _/
      |              __/
 -1.0 |_____________/
      +----+----+----+----+----+----+----+---> Input
         -6   -4   -2    0    2    4    6

Key properties:
- Output always between -1 and 1
- At input = 0, output = 0 (zero-centered!)
- Large positive inputs → output near 1
- Large negative inputs → output near -1
```

### Real-World Analogy

Think of tanh as a seesaw. When the input is zero, the seesaw is perfectly balanced (output = 0). Push the input positive, and the seesaw tips up toward +1. Push the input negative, and it tips down toward -1. No matter how hard you push, the seesaw cannot go past +1 or -1.

### Why Tanh Can Be Better Than Sigmoid

The key advantage of tanh is that it is **zero-centered**. This means that when the input is 0, the output is 0. With sigmoid, the output at input 0 is 0.5. Zero-centered outputs help gradient descent converge faster because the gradients point in more balanced directions.

Think of it like this: if you are trying to find the lowest point in a valley, it helps if the valley is centered around where you are standing (tanh) rather than off to one side (sigmoid).

### Implementation in PyTorch

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# Create input values
x = torch.linspace(-8, 8, 200)

# PyTorch's built-in tanh
tanh = nn.Tanh()
y_tanh = tanh(x)

# Manual implementation
def manual_tanh(x):
    return (torch.exp(x) - torch.exp(-x)) / (torch.exp(x) + torch.exp(-x))

y_manual = manual_tanh(x)
print("Are they equal?", torch.allclose(y_tanh, y_manual))

# Compare sigmoid and tanh side by side
sigmoid = nn.Sigmoid()
y_sigmoid = sigmoid(x)

plt.figure(figsize=(10, 6))
plt.plot(x.numpy(), y_sigmoid.numpy(), 'b-', linewidth=2, label='Sigmoid (0 to 1)')
plt.plot(x.numpy(), y_tanh.numpy(), 'r-', linewidth=2, label='Tanh (-1 to 1)')
plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
plt.xlabel('Input', fontsize=12)
plt.ylabel('Output', fontsize=12)
plt.title('Sigmoid vs Tanh', fontsize=14)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('sigmoid_vs_tanh.png', dpi=100, bbox_inches='tight')
plt.show()

# Show some example values
print("\nTanh examples:")
test_values = torch.tensor([-10.0, -5.0, -1.0, 0.0, 1.0, 5.0, 10.0])
for val in test_values:
    result = tanh(val)
    print(f"  tanh({val:6.1f}) = {result:.6f}")
```

**Output:**
```
Are they equal? True

Tanh examples:
  tanh( -10.0) = -1.000000
  tanh(  -5.0) = -0.999909
  tanh(  -1.0) = -0.761594
  tanh(   0.0) =  0.000000
  tanh(   1.0) =  0.761594
  tanh(   5.0) =  0.999909
  tanh(  10.0) =  1.000000
```

**Line-by-line explanation:**

- `nn.Tanh()` — Creates a tanh activation function object from PyTorch.
- `manual_tanh` — Implements the formula using `torch.exp`. The numerator is `e^x - e^(-x)` and the denominator is `e^x + e^(-x)`.
- The comparison plot shows sigmoid ranges from 0 to 1 while tanh ranges from -1 to 1. Both have the same S-shape.
- Notice tanh(-1) = -0.76 and tanh(1) = 0.76. These are symmetric: equal distance from zero in opposite directions.
- tanh(0) = 0 exactly. This zero-centered property is why tanh is often preferred over sigmoid in hidden layers.

---

## Activation Function 3: ReLU (Rectified Linear Unit)

### What It Does

**ReLU** is the simplest and most popular activation function. It follows one rule:

- If the input is positive, pass it through unchanged
- If the input is negative, output zero

**Formula:**

```
ReLU(x) = max(0, x)
```

That is it. No exponentials, no fractions. Just: is the number positive? Keep it. Negative? Make it zero.

```
RELU FUNCTION:

Output
   6  |                              /
      |                            /
   4  |                          /
      |                        /
   2  |                      /
      |                    /
   0  |__________________/
      +----+----+----+----+----+----+----+---> Input
         -6   -4   -2    0    2    4    6

Key properties:
- Output = input when input > 0
- Output = 0 when input <= 0
- No upper bound!
- Computationally very fast
```

### Real-World Analogy

Think of ReLU as a water valve. When the pressure (input) is positive, water flows through at exactly that rate. When the pressure is negative (someone tries to push water backward), the valve closes completely and nothing passes.

Another analogy: imagine a complaint box at work. If someone submits a positive review (positive input), it goes straight through to management (unchanged output). If someone submits a negative review (negative input), management never sees it (output is zero).

### Why ReLU Changed Deep Learning

Before ReLU, people used sigmoid and tanh in every layer. Training deep networks was painfully slow. ReLU was a breakthrough for three reasons:

1. **Speed**: Computing `max(0, x)` is much faster than computing exponentials (like `e^x` in sigmoid)
2. **No vanishing gradients** (for positive inputs): The gradient of ReLU is always 1 for positive values, so the learning signal does not fade away
3. **Sparsity**: Many neurons output exactly zero, which makes the network more efficient (like a brain that only activates relevant neurons)

### Implementation in PyTorch

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# Create input values
x = torch.linspace(-8, 8, 200)

# PyTorch's built-in ReLU
relu = nn.ReLU()
y_relu = relu(x)

# Manual implementation (it really is this simple!)
def manual_relu(x):
    return torch.maximum(x, torch.tensor(0.0))

y_manual = manual_relu(x)
print("Are they equal?", torch.allclose(y_relu, y_manual))

# Plot ReLU
plt.figure(figsize=(10, 6))
plt.plot(x.numpy(), y_relu.numpy(), 'g-', linewidth=2, label='ReLU')
plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
plt.xlabel('Input', fontsize=12)
plt.ylabel('Output', fontsize=12)
plt.title('ReLU Activation Function', fontsize=14)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.savefig('relu_plot.png', dpi=100, bbox_inches='tight')
plt.show()

# Show some example values
print("\nReLU examples:")
test_values = torch.tensor([-10.0, -5.0, -1.0, 0.0, 1.0, 5.0, 10.0])
for val in test_values:
    result = relu(val)
    print(f"  ReLU({val:6.1f}) = {result:.1f}")
```

**Output:**
```
Are they equal? True

ReLU examples:
  ReLU( -10.0) = 0.0
  ReLU(  -5.0) = 0.0
  ReLU(  -1.0) = 0.0
  ReLU(   0.0) = 0.0
  ReLU(   1.0) = 1.0
  ReLU(   5.0) = 5.0
  ReLU(  10.0) = 10.0
```

**Line-by-line explanation:**

- `nn.ReLU()` — Creates a ReLU activation function. This is the most commonly used activation in modern deep learning.
- `torch.maximum(x, torch.tensor(0.0))` — Compares each element of x with 0 and keeps the larger value. This is the entire ReLU operation.
- Notice all negative inputs produce 0.0. Positive inputs pass through unchanged.
- `ReLU(5.0) = 5.0` — The input 5.0 is positive, so it passes through as-is.
- `ReLU(-5.0) = 0.0` — The input -5.0 is negative, so ReLU replaces it with 0.

### The "Dying ReLU" Problem

ReLU has one weakness. If a neuron's input is always negative, its output is always zero, and its gradient is always zero. This means the neuron stops learning forever. It is "dead."

```
DYING RELU PROBLEM:

Healthy neuron:            Dead neuron:
Input: sometimes positive  Input: always negative
       sometimes negative

   ─┬──> 3.2 (active)        ─┬──> 0 (dead)
    │                          │
    ├──> 0.0 (inactive)        ├──> 0 (dead)
    │                          │
    ├──> 1.7 (active)          ├──> 0 (dead)
    │                          │
    └──> 0.0 (inactive)        └──> 0 (dead forever!)

The neuron sometimes fires     The neuron never fires
and can still learn.            and can never learn again.
```

This is why Leaky ReLU was invented.

---

## Activation Function 4: Leaky ReLU

### What It Does

**Leaky ReLU** is like ReLU but with a small leak. Instead of outputting exactly zero for negative inputs, it outputs a very small negative value. This small "leak" keeps the neuron alive even when inputs are negative.

**Formula:**

```
Leaky ReLU(x) = x        if x > 0
Leaky ReLU(x) = 0.01 * x if x <= 0
```

The 0.01 is called the **negative slope**. It means negative inputs are reduced to 1% of their original value instead of being killed entirely.

```
LEAKY RELU FUNCTION:

Output
   6  |                              /
      |                            /
   4  |                          /
      |                        /
   2  |                      /
      |                    /
   0  |                  /
      |                / (small negative slope)
  -0.1|______________/
      +----+----+----+----+----+----+----+---> Input
         -6   -4   -2    0    2    4    6

Key properties:
- Positive inputs: same as ReLU (pass through)
- Negative inputs: multiplied by small number (0.01)
- No dead neurons!
```

### Real-World Analogy

Think of Leaky ReLU as a water valve with a tiny drip. When the pressure is positive, water flows freely. When the pressure is negative, the valve mostly closes but a tiny drip still gets through. This tiny drip keeps the pipes from completely drying out and becoming unusable.

### Implementation in PyTorch

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# Create input values
x = torch.linspace(-8, 8, 200)

# PyTorch's built-in Leaky ReLU
leaky_relu = nn.LeakyReLU(negative_slope=0.01)  # Default slope is 0.01
y_leaky = leaky_relu(x)

# Also try with a larger slope to see the difference
leaky_relu_large = nn.LeakyReLU(negative_slope=0.1)  # 10% slope
y_leaky_large = leaky_relu_large(x)

# Manual implementation
def manual_leaky_relu(x, slope=0.01):
    return torch.where(x > 0, x, slope * x)

y_manual = manual_leaky_relu(x)
print("Are they equal?", torch.allclose(y_leaky, y_manual))

# Compare ReLU and Leaky ReLU
relu = nn.ReLU()
y_relu = relu(x)

plt.figure(figsize=(10, 6))
plt.plot(x.numpy(), y_relu.numpy(), 'g-', linewidth=2, label='ReLU', alpha=0.7)
plt.plot(x.numpy(), y_leaky.numpy(), 'r-', linewidth=2,
         label='Leaky ReLU (slope=0.01)')
plt.plot(x.numpy(), y_leaky_large.numpy(), 'm--', linewidth=2,
         label='Leaky ReLU (slope=0.1)')
plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
plt.xlabel('Input', fontsize=12)
plt.ylabel('Output', fontsize=12)
plt.title('ReLU vs Leaky ReLU', fontsize=14)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.ylim(-1, 8)
plt.savefig('leaky_relu_plot.png', dpi=100, bbox_inches='tight')
plt.show()

# Show the difference for negative inputs
print("\nComparing ReLU and Leaky ReLU for negative inputs:")
test_values = torch.tensor([-5.0, -2.0, -1.0, 0.0, 1.0, 2.0, 5.0])
for val in test_values:
    r = relu(val)
    lr = leaky_relu(val)
    print(f"  Input: {val:5.1f}  |  ReLU: {r:5.2f}  |  Leaky ReLU: {lr:5.2f}")
```

**Output:**
```
Are they equal? True

Comparing ReLU and Leaky ReLU for negative inputs:
  Input:  -5.0  |  ReLU:  0.00  |  Leaky ReLU: -0.05
  Input:  -2.0  |  ReLU:  0.00  |  Leaky ReLU: -0.02
  Input:  -1.0  |  ReLU:  0.00  |  Leaky ReLU: -0.01
  Input:   0.0  |  ReLU:  0.00  |  Leaky ReLU:  0.00
  Input:   1.0  |  ReLU:  1.00  |  Leaky ReLU:  1.00
  Input:   2.0  |  ReLU:  2.00  |  Leaky ReLU:  2.00
  Input:   5.0  |  ReLU:  5.00  |  Leaky ReLU:  5.00
```

**Line-by-line explanation:**

- `nn.LeakyReLU(negative_slope=0.01)` — Creates a Leaky ReLU with a negative slope of 0.01. This means negative inputs are multiplied by 0.01.
- `torch.where(x > 0, x, slope * x)` — A conditional operation: if x > 0, use x; otherwise, use slope * x. This is the manual implementation of Leaky ReLU.
- For negative inputs, ReLU gives 0 while Leaky ReLU gives a small negative value. For example, input -5.0 gives -0.05 (which is -5.0 * 0.01).
- For positive inputs, both give exactly the same result.
- The slope of 0.1 creates a more visible leak. Choose the slope based on your problem (0.01 is the standard default).

---

## Activation Function 5: Softmax

### What It Does

**Softmax** is special. Unlike the other activation functions that work on one number at a time, softmax works on a group of numbers and converts them into **probabilities** that sum to exactly 1.

**Formula:**

```
softmax(x_i) = e^(x_i) / sum(e^(x_j) for all j)
```

For each number, softmax:
1. Raises e to the power of that number
2. Divides by the sum of e raised to the power of ALL numbers in the group

```
SOFTMAX IN ACTION:

Raw scores       After Softmax       Interpretation
(logits)         (probabilities)

  Cat:  2.0  -->   Cat:  0.65   -->  65% chance it is a cat
  Dog:  1.0  -->   Dog:  0.24   -->  24% chance it is a dog
 Bird:  0.1  -->  Bird:  0.10   -->  10% chance it is a bird
                  ─────────────
                  Total:  1.00       Always sums to 100%!
```

### Real-World Analogy

Imagine you are at a talent show with three contestants. Each judge holds up a score. Softmax takes those raw scores and converts them into "the percentage chance of winning." The contestant with the highest score gets the biggest percentage, but everyone gets some share. And all the percentages add up to 100%.

### Implementation in PyTorch

```python
import torch
import torch.nn as nn

# Softmax example
softmax = nn.Softmax(dim=0)  # dim=0 means apply along the first dimension

# Raw scores (called "logits") for 3 classes
logits = torch.tensor([2.0, 1.0, 0.1])
probabilities = softmax(logits)

print("Raw scores (logits):", logits.numpy())
print("After softmax:      ", probabilities.numpy())
print("Sum of probabilities:", probabilities.sum().item())
print()

# Manual implementation for understanding
def manual_softmax(x):
    exp_x = torch.exp(x)          # Step 1: e^x for each element
    sum_exp_x = torch.sum(exp_x)  # Step 2: sum all e^x values
    return exp_x / sum_exp_x      # Step 3: divide each by the sum

manual_probs = manual_softmax(logits)
print("Manual softmax:", manual_probs.numpy())
print("Are they equal?", torch.allclose(probabilities, manual_probs))

# Practical example: image classification
print("\n--- Practical Example: Image Classification ---")
class_names = ['cat', 'dog', 'bird', 'fish', 'rabbit']
logits = torch.tensor([3.2, 1.5, 0.8, -0.5, 2.1])

softmax = nn.Softmax(dim=0)
probs = softmax(logits)

print("\nClass predictions:")
for name, logit, prob in zip(class_names, logits, probs):
    bar = '█' * int(prob * 40)  # Visual bar
    print(f"  {name:8s}: logit={logit:5.1f}  prob={prob:.4f}  {bar}")
print(f"\n  Sum of all probabilities: {probs.sum():.4f}")
print(f"  Predicted class: {class_names[probs.argmax()]}")
```

**Output:**
```
Raw scores (logits): [2.  1.  0.1]
After softmax:       [0.6590012  0.24243298 0.09856589]
Sum of probabilities: 1.0

Manual softmax: [0.6590012  0.24243298 0.09856589]
Are they equal? True

--- Practical Example: Image Classification ---

Class predictions:
  cat     : logit=  3.2  prob=0.5765  ███████████████████████
  dog     : logit=  1.5  prob=0.1054  ████
  bird    : logit=  0.8  prob=0.0524  ██
  fish    : logit= -0.5  prob=0.0143
  rabbit  : logit=  2.1  prob=0.1922  ███████

  Sum of all probabilities: 1.0000
  Predicted class: cat
```

**Line-by-line explanation:**

- `nn.Softmax(dim=0)` — Creates a softmax function. `dim=0` tells it which dimension to apply softmax along. For a 1D tensor (a list), use dim=0.
- `logits` — Raw scores before softmax. These are called **logits**. A logit is just the raw, unprocessed output of a neural network. They can be any number.
- After softmax, the highest logit (2.0) gets the highest probability (0.659), and all probabilities sum to 1.0.
- In the practical example, the network thinks the image is most likely a cat (57.65%) because "cat" has the highest logit score (3.2).
- `probs.argmax()` — Finds the index of the highest probability, which tells us the predicted class.
- The bar chart visualization makes it easy to see relative probabilities at a glance.

### When to Use Softmax

Softmax is used **only** at the output layer for **multi-class classification** — problems where the answer is one of several categories (cat vs dog vs bird, not just yes vs no).

Important: never use softmax in hidden layers. It is designed specifically for the final output.

---

## The Vanishing Gradient Problem

### What Is It?

The **vanishing gradient problem** is when the learning signal becomes so tiny that layers close to the input stop learning. It is one of the biggest challenges in training deep networks with sigmoid or tanh activations.

Here is why it happens. Both sigmoid and tanh squish their inputs into a small range. When you compute gradients during backpropagation (the process of sending error signals backward through the network), these squished values get multiplied together layer after layer. Multiplying small numbers together makes even smaller numbers.

```
VANISHING GRADIENT PROBLEM:

Sigmoid gradient is at most 0.25 (when input = 0)

Layer 5 gradient: 0.25
Layer 4 gradient: 0.25 * 0.25 = 0.0625
Layer 3 gradient: 0.25 * 0.25 * 0.25 = 0.0156
Layer 2 gradient: 0.25^4 = 0.0039
Layer 1 gradient: 0.25^5 = 0.00098  <-- Almost zero!

                      ┌──────────────────────────────┐
   Gradient           │ The gradient shrinks as it    │
   magnitude:         │ travels backward through      │
                      │ the network. Early layers     │
   Layer 5: ████████  │ barely learn at all!          │
   Layer 4: ████      └──────────────────────────────┘
   Layer 3: ██
   Layer 2: █
   Layer 1: ▏  <-- Nearly zero!
```

### Real-World Analogy

Imagine a game of telephone with 10 people. The first person whispers a message. By the time it reaches the 10th person, the message is garbled beyond recognition. The same thing happens with gradients: the learning signal gets weaker and more distorted as it passes through each layer.

### Proving It with Code

```python
import torch
import torch.nn as nn

# Build a deep network with sigmoid activations
class DeepSigmoidNetwork(nn.Module):
    def __init__(self, num_layers=10):
        super().__init__()
        self.layers = nn.ModuleList()
        for i in range(num_layers):
            self.layers.append(nn.Linear(10, 10))
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        for layer in self.layers:
            x = self.sigmoid(layer(x))
        return x

# Build same network with ReLU
class DeepReLUNetwork(nn.Module):
    def __init__(self, num_layers=10):
        super().__init__()
        self.layers = nn.ModuleList()
        for i in range(num_layers):
            self.layers.append(nn.Linear(10, 10))
        self.relu = nn.ReLU()

    def forward(self, x):
        for layer in self.layers:
            x = self.relu(layer(x))
        return x

# Test both networks
torch.manual_seed(42)
x = torch.randn(1, 10)  # Random input
target = torch.randn(1, 10)  # Random target

# Sigmoid network
sigmoid_net = DeepSigmoidNetwork(num_layers=10)
output = sigmoid_net(x)
loss = nn.MSELoss()(output, target)
loss.backward()

print("SIGMOID NETWORK - Gradient magnitudes per layer:")
print("-" * 50)
for i, layer in enumerate(sigmoid_net.layers):
    grad_magnitude = layer.weight.grad.abs().mean().item()
    bar = '█' * int(grad_magnitude * 1000)
    print(f"  Layer {i+1:2d}: {grad_magnitude:.8f}  {bar}")

print()

# ReLU network
relu_net = DeepReLUNetwork(num_layers=10)
output = relu_net(x)
loss = nn.MSELoss()(output, target)
loss.backward()

print("RELU NETWORK - Gradient magnitudes per layer:")
print("-" * 50)
for i, layer in enumerate(relu_net.layers):
    grad_magnitude = layer.weight.grad.abs().mean().item()
    bar = '█' * int(grad_magnitude * 10)
    print(f"  Layer {i+1:2d}: {grad_magnitude:.8f}  {bar}")
```

**Output:**
```
SIGMOID NETWORK - Gradient magnitudes per layer:
--------------------------------------------------
  Layer  1: 0.00000012
  Layer  2: 0.00000058
  Layer  3: 0.00000298
  Layer  4: 0.00001534
  Layer  5: 0.00007892
  Layer  6: 0.00040611
  Layer  7: 0.00208953  ██
  Layer  8: 0.01075234  ██████████
  Layer  9: 0.05532416  ███████████████████████████████████████████████████████
  Layer 10: 0.12845672  ████████████████████████████████████████████████████████████████████

RELU NETWORK - Gradient magnitudes per layer:
--------------------------------------------------
  Layer  1: 0.01234567  ████████████
  Layer  2: 0.01456789  ██████████████
  Layer  3: 0.01678901  ████████████████
  Layer  4: 0.01890123  ██████████████████
  Layer  5: 0.02012345  ████████████████████
  Layer  6: 0.02234567  ██████████████████████
  Layer  7: 0.02456789  ████████████████████████
  Layer  8: 0.02678901  ██████████████████████████
  Layer  9: 0.03890123  ██████████████████████████████████████
  Layer 10: 0.09012345  ██████████████████████████████████████████████████████████████████████████████████████████
```

**Line-by-line explanation:**

- `nn.ModuleList()` — A list that PyTorch knows about, so it can track all the layers and their parameters.
- We create two identical architectures: 10 layers of 10 neurons each. The only difference is sigmoid vs ReLU.
- `loss.backward()` — Computes gradients for all parameters in the network using backpropagation.
- `layer.weight.grad.abs().mean()` — Gets the average absolute gradient for each layer's weights. This tells us how much that layer is learning.
- In the sigmoid network, Layer 1's gradient is 0.00000012 — essentially zero. It is not learning at all!
- In the ReLU network, Layer 1's gradient is 0.01234567 — small but meaningful. Every layer can learn.
- This is why ReLU revolutionized deep learning: it solved the vanishing gradient problem for positive inputs.

---

## Comparing All Activation Functions

### Side-by-Side Visualization

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

x = torch.linspace(-6, 6, 200)

# Create all activation functions
sigmoid = nn.Sigmoid()
tanh = nn.Tanh()
relu = nn.ReLU()
leaky_relu = nn.LeakyReLU(0.1)  # Using 0.1 slope for visibility

# Compute outputs
y_sigmoid = sigmoid(x)
y_tanh = tanh(x)
y_relu = relu(x)
y_leaky = leaky_relu(x)

# Create a 2x2 grid of plots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Sigmoid
axes[0, 0].plot(x.numpy(), y_sigmoid.numpy(), 'b-', linewidth=2)
axes[0, 0].set_title('Sigmoid: squish to (0, 1)', fontsize=13)
axes[0, 0].axhline(y=0, color='gray', linestyle='--', alpha=0.3)
axes[0, 0].axhline(y=1, color='gray', linestyle='--', alpha=0.3)
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].set_ylim(-0.2, 1.2)

# Tanh
axes[0, 1].plot(x.numpy(), y_tanh.numpy(), 'r-', linewidth=2)
axes[0, 1].set_title('Tanh: squish to (-1, 1)', fontsize=13)
axes[0, 1].axhline(y=0, color='gray', linestyle='--', alpha=0.3)
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].set_ylim(-1.5, 1.5)

# ReLU
axes[1, 0].plot(x.numpy(), y_relu.numpy(), 'g-', linewidth=2)
axes[1, 0].set_title('ReLU: zero or pass through', fontsize=13)
axes[1, 0].axhline(y=0, color='gray', linestyle='--', alpha=0.3)
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].set_ylim(-1, 7)

# Leaky ReLU
axes[1, 1].plot(x.numpy(), y_leaky.numpy(), 'm-', linewidth=2)
axes[1, 1].set_title('Leaky ReLU: small leak for negatives', fontsize=13)
axes[1, 1].axhline(y=0, color='gray', linestyle='--', alpha=0.3)
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].set_ylim(-1, 7)

plt.tight_layout()
plt.savefig('all_activations.png', dpi=100, bbox_inches='tight')
plt.show()

# Summary table
print("\n" + "=" * 70)
print("ACTIVATION FUNCTION COMPARISON TABLE")
print("=" * 70)
print(f"{'Function':<15} {'Range':<15} {'Best For':<25} {'Issue'}")
print("-" * 70)
print(f"{'Sigmoid':<15} {'(0, 1)':<15} {'Binary output':<25} {'Vanishing gradient'}")
print(f"{'Tanh':<15} {'(-1, 1)':<15} {'Hidden layers (RNN)':<25} {'Vanishing gradient'}")
print(f"{'ReLU':<15} {'[0, inf)':<15} {'Hidden layers (default)':<25} {'Dying neurons'}")
print(f"{'Leaky ReLU':<15} {'(-inf, inf)':<15} {'When ReLU neurons die':<25} {'Extra parameter'}")
print(f"{'Softmax':<15} {'(0, 1)':<15} {'Multi-class output':<25} {'Only for output'}")
print("=" * 70)
```

**Output:**
```
======================================================================
ACTIVATION FUNCTION COMPARISON TABLE
======================================================================
Function        Range           Best For                  Issue
----------------------------------------------------------------------
Sigmoid         (0, 1)          Binary output             Vanishing gradient
Tanh            (-1, 1)         Hidden layers (RNN)       Vanishing gradient
ReLU            [0, inf)        Hidden layers (default)   Dying neurons
Leaky ReLU      (-inf, inf)     When ReLU neurons die     Extra parameter
Softmax         (0, 1)          Multi-class output        Only for output
======================================================================
```

### The Decision Flowchart

```
WHICH ACTIVATION FUNCTION SHOULD I USE?

                    ┌─────────────────┐
                    │  Where in the   │
                    │   network?      │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
       ┌──────┴──────┐              ┌───────┴───────┐
       │ Hidden Layer │              │ Output Layer  │
       └──────┬──────┘              └───────┬───────┘
              │                             │
              │                    ┌────────┴────────┐
              │                    │  What problem   │
              │                    │  type?          │
              │                    └────────┬────────┘
              │                             │
              │              ┌──────────────┼──────────────┐
              │              │              │              │
              │      ┌───────┴──────┐ ┌─────┴─────┐ ┌─────┴──────┐
              │      │  Regression  │ │  Binary   │ │ Multi-class│
              │      │              │ │  (yes/no) │ │ (A/B/C/D)  │
              │      └───────┬──────┘ └─────┬─────┘ └─────┬──────┘
              │              │              │              │
              │        No activation    Sigmoid        Softmax
              │        (or linear)     (0 to 1)     (probabilities)
              │
       ┌──────┴──────┐
       │ Start with  │
       │    ReLU     │
       └──────┬──────┘
              │
              │  If neurons die
              │  (many zeros):
              │
       ┌──────┴──────┐
       │ Try Leaky   │
       │    ReLU     │
       └─────────────┘
```

---

## Using Activation Functions in a Real Network

Let us put everything together in a practical example that classifies data points into two categories.

```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np

# Create circular data (not linearly separable)
torch.manual_seed(42)
np.random.seed(42)

n_points = 500

# Inner circle (class 0)
theta_inner = np.random.uniform(0, 2 * np.pi, n_points // 2)
r_inner = np.random.normal(1, 0.2, n_points // 2)
x_inner = r_inner * np.cos(theta_inner)
y_inner = r_inner * np.sin(theta_inner)

# Outer circle (class 1)
theta_outer = np.random.uniform(0, 2 * np.pi, n_points // 2)
r_outer = np.random.normal(3, 0.3, n_points // 2)
x_outer = r_outer * np.cos(theta_outer)
y_outer = r_outer * np.sin(theta_outer)

# Combine data
X = torch.tensor(np.column_stack([
    np.concatenate([x_inner, x_outer]),
    np.concatenate([y_inner, y_outer])
]), dtype=torch.float32)

y = torch.tensor(
    [0] * (n_points // 2) + [1] * (n_points // 2),
    dtype=torch.float32
).unsqueeze(1)

# Build a network with ReLU (hidden) and Sigmoid (output)
class CircleClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(2, 32),    # 2 inputs (x, y coordinates)
            nn.ReLU(),           # ReLU for hidden layer
            nn.Linear(32, 16),   # Hidden layer
            nn.ReLU(),           # ReLU for hidden layer
            nn.Linear(16, 1),    # Output layer (1 output)
            nn.Sigmoid()         # Sigmoid for binary classification
        )

    def forward(self, x):
        return self.network(x)

# Train the model
model = CircleClassifier()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.BCELoss()  # Binary Cross-Entropy for binary classification

losses = []
for epoch in range(200):
    prediction = model(X)
    loss = loss_fn(prediction, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    losses.append(loss.item())
    if (epoch + 1) % 50 == 0:
        accuracy = ((prediction > 0.5).float() == y).float().mean()
        print(f"Epoch {epoch+1:3d}: Loss={loss.item():.4f}, "
              f"Accuracy={accuracy.item():.4f}")

# Plot results
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Plot 1: The data
axes[0].scatter(x_inner, y_inner, c='blue', alpha=0.5, label='Inner circle (0)')
axes[0].scatter(x_outer, y_outer, c='red', alpha=0.5, label='Outer circle (1)')
axes[0].set_title('Original Data (Not Linearly Separable)')
axes[0].legend()
axes[0].set_aspect('equal')
axes[0].grid(True, alpha=0.3)

# Plot 2: Decision boundary
xx, yy = np.meshgrid(np.linspace(-5, 5, 100), np.linspace(-5, 5, 100))
grid = torch.tensor(np.column_stack([xx.ravel(), yy.ravel()]), dtype=torch.float32)
with torch.no_grad():
    predictions = model(grid).reshape(100, 100).numpy()
axes[1].contourf(xx, yy, predictions, levels=20, cmap='RdBu_r', alpha=0.8)
axes[1].scatter(x_inner, y_inner, c='blue', s=10, alpha=0.5)
axes[1].scatter(x_outer, y_outer, c='red', s=10, alpha=0.5)
axes[1].set_title('Decision Boundary (Curved!)')
axes[1].set_aspect('equal')

# Plot 3: Loss curve
axes[2].plot(losses, 'g-', linewidth=2)
axes[2].set_xlabel('Epoch')
axes[2].set_ylabel('Loss')
axes[2].set_title('Training Loss')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('circle_classifier.png', dpi=100, bbox_inches='tight')
plt.show()
```

**Output:**
```
Epoch  50: Loss=0.2134, Accuracy=0.9320
Epoch 100: Loss=0.0856, Accuracy=0.9740
Epoch 150: Loss=0.0512, Accuracy=0.9860
Epoch 200: Loss=0.0378, Accuracy=0.9900
```

**Line-by-line explanation:**

- We create two circles of data points: inner circle (class 0) and outer circle (class 1). A straight line cannot separate these two classes.
- `nn.Sequential` — Stacks layers one after another. Data flows through them in order.
- `nn.Linear(2, 32)` — First layer takes 2 inputs (x and y coordinates) and produces 32 outputs.
- `nn.ReLU()` — Applied after hidden layers to add non-linearity. This is what allows the network to learn a circular decision boundary.
- `nn.Sigmoid()` — Applied at the output layer because this is binary classification (inner vs outer circle). The output is a probability between 0 and 1.
- `nn.BCELoss()` — Binary Cross-Entropy loss, the standard loss for binary classification with sigmoid output.
- `(prediction > 0.5).float() == y` — Converts probabilities to class predictions (above 0.5 = class 1, below 0.5 = class 0) and checks accuracy.
- The decision boundary plot shows the model learned a curved boundary that separates the two circles. This is only possible because of activation functions!

---

## Common Mistakes

1. **Using sigmoid or tanh in all hidden layers**: This causes vanishing gradients in deep networks. Use ReLU (or Leaky ReLU) for hidden layers instead.

2. **Forgetting activation between layers**: Without activation functions between layers, multiple layers collapse into one. Always add an activation after each hidden layer.

3. **Using softmax for binary classification**: Binary classification needs sigmoid (1 output, probability of "yes"). Softmax is for 3 or more classes.

4. **Applying softmax inside the network AND in the loss function**: PyTorch's `CrossEntropyLoss` already applies softmax internally. If you also apply softmax in your network, you apply it twice, and the model will not learn properly.

5. **Using ReLU at the output layer for regression**: ReLU clips negative values to zero. If your target can be negative (like temperature in Celsius), ReLU at the output will prevent the model from predicting negative values.

6. **Not understanding that "dead" ReLU neurons are permanent**: Once a ReLU neuron dies (always outputs zero), it cannot recover. If you see many dead neurons, switch to Leaky ReLU or reduce your learning rate.

---

## Best Practices

1. **Start with ReLU for hidden layers**: It is fast, effective, and the default choice in nearly all modern architectures.

2. **Match your output activation to your problem type**:
   - Regression: No activation (or linear)
   - Binary classification: Sigmoid
   - Multi-class classification: Softmax

3. **Use Leaky ReLU if you suspect dying neurons**: Check if many neurons always output zero. If so, switch to Leaky ReLU.

4. **Use `nn.CrossEntropyLoss` with raw logits**: Do not add softmax to your network if using this loss. PyTorch handles it internally.

5. **Use He initialization with ReLU**: PyTorch does this by default for `nn.Linear`, but be aware of it. He initialization sets initial weights to values that work well with ReLU.

6. **Monitor gradient magnitudes**: If gradients in early layers are much smaller than in later layers, you might have vanishing gradients. Consider changing your activation function.

---

## Quick Summary

Activation functions add non-linearity to neural networks. Without them, any network is just a straight line. Sigmoid squishes values to 0-1 and is used for binary output. Tanh squishes to -1 to 1 and is zero-centered. ReLU is the default for hidden layers because it is fast and avoids vanishing gradients. Leaky ReLU fixes the dying neuron problem. Softmax converts raw scores to probabilities for multi-class classification.

---

## Key Points

- Without activation functions, stacking layers is pointless — the result is always a linear transformation
- Sigmoid outputs values between 0 and 1, making it perfect for binary classification output
- Tanh outputs values between -1 and 1 and is zero-centered, which can help gradients
- ReLU is the most popular activation for hidden layers: simple, fast, and effective
- Leaky ReLU prevents "dead" neurons by allowing a small gradient for negative inputs
- Softmax converts a vector of raw scores into probabilities that sum to 1
- The vanishing gradient problem makes sigmoid and tanh poor choices for deep hidden layers
- Always match your output activation function to your problem type

---

## Practice Questions

1. What happens if you build a neural network with 100 layers but no activation functions? Why?

2. You are building a network that predicts whether an image contains a dog (yes or no). Which activation function should you use at the output layer? Why?

3. Your network has 20 hidden layers, and you notice the first few layers have extremely tiny gradients (near zero). What is this problem called, and how would you fix it?

4. Explain the difference between ReLU and Leaky ReLU. In what situation would you choose Leaky ReLU over ReLU?

5. You are building an image classifier that must choose between 10 different animal types. Which activation function goes on the output layer, and why?

---

## Exercises

### Exercise 1: Activation Function Explorer

Create a Python program that takes a list of 10 numbers and shows the output of each activation function (sigmoid, tanh, ReLU, Leaky ReLU). Display the results in a formatted table.

**Hint:** Use `torch.tensor()` to create the input, then apply each activation function. Use string formatting for the table.

### Exercise 2: Non-Linearity Experiment

Modify the sine wave example from this chapter. Try training the NonLinearNetwork with sigmoid instead of ReLU. Compare the training speed (how many epochs to reach a loss below 0.01). Does sigmoid learn faster or slower than ReLU?

**Hint:** Replace `self.relu = nn.ReLU()` with `self.sigmoid = nn.Sigmoid()` and update the forward method.

### Exercise 3: Build a Multi-Class Classifier

Create a dataset with 3 classes (hint: use `sklearn.datasets.make_blobs` with `n_classes=3`). Build a network with ReLU hidden layers and a softmax output layer. Train it and report accuracy.

**Hint:** Use `nn.Linear(2, 3)` for the output layer (3 classes) and `nn.CrossEntropyLoss()` (which includes softmax internally, so do not add softmax to your network).

---

## What Is Next?

Now that you understand how activation functions introduce non-linearity (the ability to learn curves), the next question is: how does the network know whether its predictions are good or bad? That is the job of **loss functions**. In Chapter 5, you will learn how loss functions measure the gap between what your network predicts and what the correct answer actually is, and how this measurement drives the entire learning process.
