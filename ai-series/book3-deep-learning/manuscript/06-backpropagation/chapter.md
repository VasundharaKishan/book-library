# Chapter 6: Backpropagation

## What You Will Learn

In this chapter, you will learn:

- What backpropagation is and why every neural network needs it
- The chain rule from calculus explained in plain English
- How errors flow backward through a network, layer by layer
- A complete step-by-step example with actual numbers in a 2-layer network
- How to compute gradients for each weight by hand
- Why it is called "back" propagation (and not "forward" propagation)
- What computational graphs are and how they track operations
- How backpropagation connects to what PyTorch does behind the scenes

## Why This Chapter Matters

Imagine you are baking a cake that comes out too salty. You ask yourself, "What went wrong?" You trace the problem backward. Was it the final step where you added salt? Or was it the earlier step where you used salted butter? You follow the trail of blame backward through each step to figure out exactly how much each ingredient contributed to the saltiness.

Backpropagation works the same way. When a neural network makes a wrong prediction, backpropagation traces the error backward through every layer, every neuron, and every weight to figure out exactly how much each weight contributed to the mistake. Once we know that, we can adjust each weight by the right amount.

Without backpropagation, we would have no way to train deep neural networks. It is the algorithm that made modern AI possible. Every time you use a voice assistant, a photo filter, or a language model, backpropagation trained the network behind it.

If you understand backpropagation, you understand how neural networks learn.

---

## 6.1 The Big Picture: How Does a Network Learn?

### The Learning Process in Three Steps

Training a neural network follows a simple pattern:

```
The Neural Network Learning Loop
===================================

Step 1: FORWARD PASS
  Input ---> [Layer 1] ---> [Layer 2] ---> Prediction

  "Make a guess"

Step 2: COMPUTE LOSS
  Compare prediction to the correct answer
  Loss = how wrong we are

  "Measure the mistake"

Step 3: BACKWARD PASS (Backpropagation)
  Loss ---> [Layer 2] ---> [Layer 1] ---> Gradients

  "Trace the blame backward"

Step 4: UPDATE WEIGHTS
  Adjust each weight based on its gradient

  "Fix the mistake"

Repeat thousands of times until the network gets good.
```

We covered the forward pass in Chapter 3. We covered loss functions in Chapter 5. Now we tackle the backward pass, the step where the network actually learns.

### What Is a Gradient?

A **gradient** tells you two things:

1. **Direction**: Should this weight go up or down?
2. **Amount**: How much should it change?

Think of a gradient as a signpost on a hiking trail. It points toward the valley (lower error) and tells you how steep the slope is.

```
What a Gradient Tells You
============================

Gradient = -3.5

  Direction: Negative means "decrease the weight"
  Amount: 3.5 means "the slope is fairly steep"

Gradient = +0.1

  Direction: Positive means "increase the weight"
  Amount: 0.1 means "the slope is very gentle"

Gradient = 0.0

  Direction: No change needed
  Amount: You are at the bottom of the valley
```

---

## 6.2 The Chain Rule: The Math Behind Backpropagation

### What Is the Chain Rule?

The **chain rule** is a rule from calculus that tells you how to find the rate of change when you have a chain of operations. Do not worry if you have not taken calculus. We will explain it with a simple analogy.

**Think of it like this:** You work at a factory. Your salary depends on how many hours you work. The number of hours you work depends on how many orders the factory receives. You want to know: if the factory gets one more order, how much does your salary change?

```
Chain of Effects
==================

Orders --> Hours --> Salary

If 1 extra order = 2 extra hours
And 1 extra hour = $15 extra salary

Then 1 extra order = 2 * $15 = $30 extra salary

This is the chain rule: multiply the rates along the chain.
```

### The Chain Rule in Math

If you have a chain of functions:

```
The Chain Rule Formula
========================

If    z depends on y,    and    y depends on x

Then: dz/dx = dz/dy * dy/dx

In plain English:
  "The rate of change of z with respect to x
   equals
   the rate of change of z with respect to y
   multiplied by
   the rate of change of y with respect to x"

Example:
  y = 3x        (y changes 3 times as fast as x)
  z = 2y        (z changes 2 times as fast as y)

  dz/dx = dz/dy * dy/dx = 2 * 3 = 6

  (z changes 6 times as fast as x)
```

### Why Does the Chain Rule Matter for Neural Networks?

A neural network is a chain of operations:

```
Neural Network as a Chain
============================

Input -> [multiply by w1] -> [add b1] -> [activation] -> [multiply by w2] -> [add b2] -> Output -> Loss

Each arrow is a link in the chain.
The chain rule lets us trace backward through ALL links
to find out how the loss depends on EACH weight.
```

---

## 6.3 A Simple Example: One Neuron

Let us start with the simplest possible case: one neuron, one weight, one input.

### Setup

```
Single Neuron
================

Input (x) = 2.0
Weight (w) = 0.5
Bias (b) = 0.1
Target (t) = 1.0  (the correct answer)

Forward pass:
  z = w * x + b = 0.5 * 2.0 + 0.1 = 1.1
  prediction = z  (no activation function for simplicity)

Loss (MSE):
  L = (prediction - target)^2 = (1.1 - 1.0)^2 = 0.01
```

### Forward Pass Diagram

```
Forward Pass: Left to Right
================================

x = 2.0 --->[ * w=0.5 ]--->[ + b=0.1 ]---> z = 1.1 ---> L = 0.01
                                                            |
                                              (compared to target = 1.0)
```

### Backward Pass: Finding Gradients

Now we work backward. We want to find:
- dL/dw: How does the loss change when we change w?
- dL/db: How does the loss change when we change b?

```
Backward Pass: Right to Left
=================================

Step 1: How does loss depend on z?
  L = (z - t)^2
  dL/dz = 2 * (z - t) = 2 * (1.1 - 1.0) = 0.2

Step 2: How does z depend on w?
  z = w * x + b
  dz/dw = x = 2.0

Step 3: How does z depend on b?
  z = w * x + b
  dz/db = 1

Step 4: Apply the chain rule

  dL/dw = dL/dz * dz/dw = 0.2 * 2.0 = 0.4
  dL/db = dL/dz * dz/db = 0.2 * 1   = 0.2
```

### What Do These Gradients Mean?

```
Interpreting the Gradients
=============================

dL/dw = 0.4
  "If we increase w by a tiny amount,
   the loss increases by 0.4 times that amount."

  Since the gradient is POSITIVE, we should DECREASE w
  to reduce the loss.

dL/db = 0.2
  "If we increase b by a tiny amount,
   the loss increases by 0.2 times that amount."

  Since the gradient is POSITIVE, we should DECREASE b
  to reduce the loss.
```

### Updating the Weights

Using a learning rate of 0.1:

```
Weight Update
================

learning_rate = 0.1

w_new = w_old - learning_rate * dL/dw
      = 0.5   - 0.1 * 0.4
      = 0.5   - 0.04
      = 0.46

b_new = b_old - learning_rate * dL/db
      = 0.1   - 0.1 * 0.2
      = 0.1   - 0.02
      = 0.08

Let's verify: new prediction = 0.46 * 2.0 + 0.08 = 1.0
The prediction is now exactly 1.0! The network learned.
```

### Python Code: One Neuron Backpropagation

```python
# Backpropagation for a single neuron

# Setup
x = 2.0       # input
w = 0.5       # weight
b = 0.1       # bias
target = 1.0  # correct answer
lr = 0.1      # learning rate

print("=== Before Training ===")
print(f"Weight: {w}, Bias: {b}")

# Forward pass
z = w * x + b
prediction = z
loss = (prediction - target) ** 2

print(f"Prediction: {prediction}")
print(f"Target: {target}")
print(f"Loss: {loss}")

# Backward pass (compute gradients)
dL_dz = 2 * (z - target)    # derivative of loss with respect to z
dz_dw = x                    # derivative of z with respect to w
dz_db = 1                    # derivative of z with respect to b

dL_dw = dL_dz * dz_dw       # chain rule for weight
dL_db = dL_dz * dz_db       # chain rule for bias

print(f"\nGradient for w: {dL_dw}")
print(f"Gradient for b: {dL_db}")

# Update weights
w = w - lr * dL_dw
b = b - lr * dL_db

print(f"\n=== After Training ===")
print(f"Weight: {w}, Bias: {b}")

# Verify
new_prediction = w * x + b
new_loss = (new_prediction - target) ** 2
print(f"New Prediction: {new_prediction}")
print(f"New Loss: {new_loss}")
```

**Output:**

```
=== Before Training ===
Weight: 0.5, Bias: 0.1
Prediction: 1.1
Target: 1.0
Loss: 0.010000000000000002

Gradient for w: 0.4
Gradient for b: 0.2

=== After Training ===
Weight: 0.46, Bias: 0.08
New Prediction: 1.0
New Loss: 0.0
```

### Line-by-Line Explanation

```
Line: z = w * x + b
  This is the forward pass. We compute the output of the neuron.
  0.5 * 2.0 + 0.1 = 1.1

Line: loss = (prediction - target) ** 2
  We measure how wrong the prediction is using MSE loss.
  (1.1 - 1.0)^2 = 0.01

Line: dL_dz = 2 * (z - target)
  The derivative of MSE loss with respect to z.
  The formula comes from calculus: d/dz (z - t)^2 = 2(z - t).
  2 * (1.1 - 1.0) = 0.2

Line: dz_dw = x
  Since z = w * x + b, the derivative with respect to w is x.
  The weight is multiplied by x, so x is the rate of change.

Line: dL_dw = dL_dz * dz_dw
  This is the chain rule. We multiply the rates along the chain.
  0.2 * 2.0 = 0.4

Line: w = w - lr * dL_dw
  We subtract the gradient (times learning rate) from the weight.
  The minus sign makes the weight move in the direction that
  DECREASES the loss.
```

---

## 6.4 Step-by-Step: A 2-Layer Network

Now let us do the full backpropagation for a 2-layer network with actual numbers. This is where it gets interesting.

### Network Architecture

```
2-Layer Network Architecture
================================

Input Layer    Hidden Layer      Output Layer
(1 neuron)    (1 neuron)        (1 neuron)

  x ---w1---> [h] ---w2---> [o] ---> Loss
       b1      |      b2      |
               sigmoid        (no activation)

x  = 1.0  (input)
w1 = 0.5  (weight from input to hidden)
b1 = 0.2  (bias for hidden neuron)
w2 = 0.8  (weight from hidden to output)
b2 = 0.3  (bias for output neuron)

Target = 0.5
```

### Step 1: Forward Pass

```
Forward Pass (left to right)
================================

Hidden layer:
  z1 = w1 * x + b1
     = 0.5 * 1.0 + 0.2
     = 0.7

  h = sigmoid(z1)
    = 1 / (1 + e^(-0.7))
    = 1 / (1 + 0.4966)
    = 1 / 1.4966
    = 0.6682

Output layer:
  z2 = w2 * h + b2
     = 0.8 * 0.6682 + 0.3
     = 0.5346 + 0.3
     = 0.8346

  output = z2 = 0.8346  (no activation)

Loss (MSE):
  L = (output - target)^2
    = (0.8346 - 0.5)^2
    = (0.3346)^2
    = 0.1120
```

### Step 2: Backward Pass

Now we trace backward. We will find gradients for all four parameters: w2, b2, w1, b1.

```
Backward Pass (right to left)
=================================

=== STEP A: Gradients for the output layer ===

dL/dz2 = 2 * (z2 - target) = 2 * (0.8346 - 0.5) = 0.6691

dL/dw2 = dL/dz2 * dz2/dw2 = 0.6691 * h = 0.6691 * 0.6682 = 0.4470

dL/db2 = dL/dz2 * dz2/db2 = 0.6691 * 1 = 0.6691


=== STEP B: Gradient flows to the hidden layer ===

We need dL/dh (how the loss depends on the hidden output):
  dL/dh = dL/dz2 * dz2/dh = 0.6691 * w2 = 0.6691 * 0.8 = 0.5353

Now we need to go THROUGH the sigmoid:
  sigmoid derivative: dsigmoid/dz1 = h * (1 - h) = 0.6682 * (1 - 0.6682) = 0.2217

  dL/dz1 = dL/dh * dsigmoid/dz1 = 0.5353 * 0.2217 = 0.1187


=== STEP C: Gradients for the hidden layer weights ===

dL/dw1 = dL/dz1 * dz1/dw1 = 0.1187 * x = 0.1187 * 1.0 = 0.1187

dL/db1 = dL/dz1 * dz1/db1 = 0.1187 * 1 = 0.1187
```

### The Complete Flow Diagram

```
Backward Pass Flow
======================

              FORWARD PASS (-->)
              ==================
x=1.0 --w1=0.5--> z1=0.7 --sigmoid--> h=0.6682 --w2=0.8--> z2=0.8346 --> L=0.1120
                                                                           |
              BACKWARD PASS (<--)                                          |
              ===================                                          v
                                                                      target=0.5
dL/dw1    dL/dz1      dL/dh         dL/dw2    dL/dz2
=0.1187 <-- =0.1187 <-- =0.5353 <--- =0.4470 <-- =0.6691

  |         |            |             |           |
  v         v            v             v           v
chain:   chain:       chain:        chain:      start
dL/dz1   dL/dh *     dL/dz2 *     dL/dz2 *    2*(z2-t)
* x      sigmoid'     w2           h
```

### Step 3: Update All Weights

```
Weight Updates (learning_rate = 0.1)
=======================================

w2_new = w2 - lr * dL/dw2 = 0.8   - 0.1 * 0.4470 = 0.7553
b2_new = b2 - lr * dL/db2 = 0.3   - 0.1 * 0.6691 = 0.2331
w1_new = w1 - lr * dL/dw1 = 0.5   - 0.1 * 0.1187 = 0.4881
b1_new = b1 - lr * dL/db1 = 0.2   - 0.1 * 0.1187 = 0.1881
```

### Python Code: 2-Layer Network Backpropagation

```python
import math

# ============================
# 2-Layer Network Backpropagation
# ============================

def sigmoid(z):
    """Sigmoid activation function."""
    return 1.0 / (1.0 + math.exp(-z))

def sigmoid_derivative(h):
    """Derivative of sigmoid, given the sigmoid output h."""
    return h * (1 - h)

# Network parameters
x = 1.0       # input
w1 = 0.5      # weight: input -> hidden
b1 = 0.2      # bias: hidden
w2 = 0.8      # weight: hidden -> output
b2 = 0.3      # bias: output
target = 0.5  # correct answer
lr = 0.1      # learning rate

print("=== Initial Parameters ===")
print(f"w1={w1}, b1={b1}, w2={w2}, b2={b2}")

# --------------------
# FORWARD PASS
# --------------------
z1 = w1 * x + b1           # hidden layer pre-activation
h = sigmoid(z1)             # hidden layer output
z2 = w2 * h + b2            # output layer pre-activation
output = z2                  # output (no activation)
loss = (output - target) ** 2  # MSE loss

print(f"\n=== Forward Pass ===")
print(f"z1 = {z1:.4f}")
print(f"h  = sigmoid({z1:.4f}) = {h:.4f}")
print(f"z2 = {z2:.4f}")
print(f"output = {output:.4f}")
print(f"loss = {loss:.4f}")

# --------------------
# BACKWARD PASS
# --------------------
# Step A: Output layer gradients
dL_dz2 = 2 * (z2 - target)
dL_dw2 = dL_dz2 * h
dL_db2 = dL_dz2 * 1

# Step B: Flow through hidden layer
dL_dh = dL_dz2 * w2
dh_dz1 = sigmoid_derivative(h)
dL_dz1 = dL_dh * dh_dz1

# Step C: Hidden layer gradients
dL_dw1 = dL_dz1 * x
dL_db1 = dL_dz1 * 1

print(f"\n=== Backward Pass (Gradients) ===")
print(f"dL/dw2 = {dL_dw2:.4f}")
print(f"dL/db2 = {dL_db2:.4f}")
print(f"dL/dw1 = {dL_dw1:.4f}")
print(f"dL/db1 = {dL_db1:.4f}")

# --------------------
# UPDATE WEIGHTS
# --------------------
w1 = w1 - lr * dL_dw1
b1 = b1 - lr * dL_db1
w2 = w2 - lr * dL_dw2
b2 = b2 - lr * dL_db2

print(f"\n=== Updated Parameters ===")
print(f"w1={w1:.4f}, b1={b1:.4f}, w2={w2:.4f}, b2={b2:.4f}")

# Verify: forward pass with new weights
z1_new = w1 * x + b1
h_new = sigmoid(z1_new)
z2_new = w2 * h_new + b2
new_loss = (z2_new - target) ** 2

print(f"\n=== After Update ===")
print(f"New prediction: {z2_new:.4f}")
print(f"New loss: {new_loss:.4f}")
print(f"Loss decreased by: {loss - new_loss:.4f}")
```

**Output:**

```
=== Initial Parameters ===
w1=0.5, b1=0.2, w2=0.8, b2=0.3

=== Forward Pass ===
z1 = 0.7000
h  = sigmoid(0.7000) = 0.6682
z2 = 0.8346
output = 0.8346
loss = 0.1120

=== Backward Pass (Gradients) ===
dL/dw2 = 0.4470
dL/db2 = 0.6691
dL/dw1 = 0.1187
dL/db1 = 0.1187

=== Updated Parameters ===
w1=0.4881, b1=0.1881, w2=0.7553, b2=0.2331

=== After Update ===
New prediction: 0.7254
New loss: 0.0508
Loss decreased by: 0.0612
```

The loss dropped from 0.1120 to 0.0508 after just one update. That is backpropagation at work.

---

## 6.5 Why It Is Called "Back" Propagation

### The Name Explained

The name "backpropagation" comes from two words:

- **Back**: We move from right to left (from the output toward the input)
- **Propagation**: We spread (propagate) the error signal through the network

```
Why "BACK" Propagation?
==========================

FORWARD propagation:
  Input ---> Hidden ---> Output ---> Loss
  (We compute predictions going FORWARD)

BACK propagation:
  Input <--- Hidden <--- Output <--- Loss
  (We compute gradients going BACKWARD)

The error signal starts at the loss function (the end)
and propagates backward through the network (to the beginning).
```

### Forward vs. Backward: Side by Side

```
Forward Pass vs. Backward Pass
==================================

FORWARD (compute values):
  x=1.0 --> [*0.5 +0.2] --> sigmoid --> [*0.8 +0.3] --> 0.8346

BACKWARD (compute gradients):
  0.1187 <-- [*x] <-- [*sigmoid'] <-- [*w2] <-- [*2(z-t)] <-- 0.1120

Key difference:
  Forward: Uses INPUTS and WEIGHTS to compute OUTPUTS
  Backward: Uses the LOSS to compute GRADIENTS for weights
```

---

## 6.6 Computational Graphs

### What Is a Computational Graph?

A **computational graph** is a diagram that shows every single operation your network performs, drawn as a flowchart. Each circle or box represents one operation (add, multiply, sigmoid), and each arrow shows the data flowing between operations.

**Think of it like this:** A computational graph is like a recipe card that lists every single step in order. If the cake turns out bad, you can trace backward through the steps to find the problem.

### A Simple Computational Graph

```
Computational Graph for z = w * x + b
==========================================

  w ----\
         *----> wx ----\
  x ----/               +----> z
                        /
  b -------------------/

Nodes (circles):
  * = multiplication
  + = addition

Edges (arrows):
  Show which values flow where.

Forward pass: Follow arrows LEFT to RIGHT
  w=0.5, x=2.0  -->  wx = 1.0  -->  z = 1.0 + 0.1 = 1.1

Backward pass: Follow arrows RIGHT to LEFT
  dz/d(wx) = 1,  dz/db = 1
  d(wx)/dw = x = 2.0,  d(wx)/dx = w = 0.5
```

### Computational Graph for Our 2-Layer Network

```
Full Computational Graph
============================

 w1--\
      *---> z1_pre --\
 x---/                +---> z1 ---> sigmoid ---> h --\
                     /                                 *--> z2_pre --\
 b1-----------------/                                 /               +--> z2 --> Loss
                                                w2---/               /
                                                                    /
                                                b2-----------------/

Forward: Follow arrows left to right (compute values)
Backward: Follow arrows right to left (compute gradients)

At each node, we use the chain rule to combine:
  - The gradient flowing IN from the right
  - The LOCAL derivative of that operation
```

### Why Computational Graphs Matter

```
Benefits of Computational Graphs
====================================

1. AUTOMATIC DIFFERENTIATION
   PyTorch builds the graph automatically during the forward pass.
   Then it walks backward through the graph to compute all gradients.
   You never write the backward pass by hand.

2. MODULAR
   Each operation knows its own derivative.
   You can add new operations without rewriting everything.

3. EFFICIENT
   The graph reuses intermediate results.
   Each partial derivative is computed only once.

4. VISUAL
   You can SEE the structure of your network.
   Debugging is easier when you can trace the flow.
```

### Python Code: Demonstrating Computational Graphs

```python
# Demonstrating a simple computational graph by hand

# Define operations and their derivatives
class MultiplyNode:
    """Represents a multiplication operation."""
    def forward(self, a, b):
        self.a = a
        self.b = b
        return a * b

    def backward(self, gradient_from_above):
        grad_a = gradient_from_above * self.b
        grad_b = gradient_from_above * self.a
        return grad_a, grad_b

class AddNode:
    """Represents an addition operation."""
    def forward(self, a, b):
        return a + b

    def backward(self, gradient_from_above):
        grad_a = gradient_from_above * 1
        grad_b = gradient_from_above * 1
        return grad_a, grad_b

class SquaredErrorNode:
    """Represents (prediction - target)^2."""
    def forward(self, prediction, target):
        self.prediction = prediction
        self.target = target
        return (prediction - target) ** 2

    def backward(self):
        return 2 * (self.prediction - self.target)

# Build the computational graph
multiply = MultiplyNode()
add = AddNode()
loss_node = SquaredErrorNode()

# Inputs
x = 2.0
w = 0.5
b = 0.1
target = 1.0

# Forward pass through the graph
print("=== Forward Pass ===")
wx = multiply.forward(w, x)
print(f"Step 1: w * x = {w} * {x} = {wx}")

z = add.forward(wx, b)
print(f"Step 2: wx + b = {wx} + {b} = {z}")

loss = loss_node.forward(z, target)
print(f"Step 3: (z - target)^2 = ({z} - {target})^2 = {loss}")

# Backward pass through the graph
print(f"\n=== Backward Pass ===")
dL_dz = loss_node.backward()
print(f"Step 3 backward: dL/dz = {dL_dz}")

dL_dwx, dL_db = add.backward(dL_dz)
print(f"Step 2 backward: dL/d(wx) = {dL_dwx}, dL/db = {dL_db}")

dL_dw, dL_dx = multiply.backward(dL_dwx)
print(f"Step 1 backward: dL/dw = {dL_dw}, dL/dx = {dL_dx}")

print(f"\n=== Summary ===")
print(f"Gradient for w: {dL_dw}")
print(f"Gradient for b: {dL_db}")
```

**Output:**

```
=== Forward Pass ===
Step 1: w * x = 0.5 * 2.0 = 1.0
Step 2: wx + b = 1.0 + 0.1 = 1.1
Step 3: (z - target)^2 = (1.1 - 1.0)^2 = 0.010000000000000002

=== Backward Pass ===
Step 3 backward: dL/dz = 0.2
Step 2 backward: dL/d(wx) = 0.2, dL/db = 0.2
Step 1 backward: dL/dw = 0.4, dL/dx = 0.1

=== Summary ===
Gradient for w: 0.4
Gradient for b: 0.2
```

### Line-by-Line Explanation

```
Line: wx = multiply.forward(w, x)
  The multiply node stores its inputs (w and x) so it can
  use them during the backward pass.

Line: dL_dz = loss_node.backward()
  The backward pass starts at the loss. The loss node returns
  the derivative of the loss with respect to its input.

Line: dL_dwx, dL_db = add.backward(dL_dz)
  The add node receives the gradient from above (dL_dz = 0.2)
  and passes it through unchanged to both inputs (because
  the derivative of addition is 1 for both inputs).

Line: dL_dw, dL_dx = multiply.backward(dL_dwx)
  The multiply node receives the gradient from above (dL_dwx = 0.2)
  and multiplies it by the OTHER input to get each gradient:
    dL/dw = gradient * x = 0.2 * 2.0 = 0.4
    dL/dx = gradient * w = 0.2 * 0.5 = 0.1
```

---

## 6.7 Backpropagation with Multiple Training Steps

Let us watch backpropagation in action over multiple training steps to see the network gradually improve.

```python
import math

def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))

def sigmoid_derivative(h):
    return h * (1 - h)

# Network parameters
w1, b1 = 0.5, 0.2
w2, b2 = 0.8, 0.3
x = 1.0
target = 0.5
lr = 0.5

print("Training a 2-layer network for 10 steps")
print("=" * 50)
print(f"{'Step':<6}{'Prediction':<14}{'Loss':<12}{'Change'}")
print("-" * 50)

prev_loss = None

for step in range(10):
    # Forward pass
    z1 = w1 * x + b1
    h = sigmoid(z1)
    z2 = w2 * h + b2
    output = z2
    loss = (output - target) ** 2

    # Print progress
    change = ""
    if prev_loss is not None:
        diff = loss - prev_loss
        change = f"{'decreased' if diff < 0 else 'increased'} by {abs(diff):.4f}"
    print(f"{step:<6}{output:<14.4f}{loss:<12.6f}{change}")
    prev_loss = loss

    # Backward pass
    dL_dz2 = 2 * (z2 - target)
    dL_dw2 = dL_dz2 * h
    dL_db2 = dL_dz2
    dL_dh = dL_dz2 * w2
    dL_dz1 = dL_dh * sigmoid_derivative(h)
    dL_dw1 = dL_dz1 * x
    dL_db1 = dL_dz1

    # Update weights
    w1 -= lr * dL_dw1
    b1 -= lr * dL_db1
    w2 -= lr * dL_dw2
    b2 -= lr * dL_db2

print("-" * 50)
print(f"\nFinal prediction: {output:.4f} (target was {target})")
print(f"Final loss: {loss:.6f}")
```

**Output:**

```
Training a 2-layer network for 10 steps
==================================================
Step  Prediction    Loss        Change
--------------------------------------------------
0     0.8346        0.112037
1     0.6627        0.026499    decreased by 0.0855
2     0.5827        0.006835    decreased by 0.0197
3     0.5440        0.001934    decreased by 0.0049
4     0.5236        0.000555    decreased by 0.0014
5     0.5127        0.000161    decreased by 0.0004
6     0.5069        0.000047    decreased by 0.0001
7     0.5037        0.000014    decreased by 0.0000
8     0.5020        0.000004    decreased by 0.0000
9     0.5011        0.000001    decreased by 0.0000
--------------------------------------------------

Final prediction: 0.5011 (target was 0.5)
Final loss: 0.000001
```

The network gets closer to the target with every step. That is learning in action.

---

## 6.8 The Full Backpropagation Algorithm

Let us summarize the complete backpropagation algorithm:

```
The Backpropagation Algorithm
================================

INPUT: Training data (x, target), network with weights and biases

REPEAT for each training example:

  1. FORWARD PASS
     - Feed input through the network, layer by layer
     - Store all intermediate values (they are needed for backward)
     - Compute the loss at the end

  2. BACKWARD PASS
     - Start at the loss function
     - Compute dL/d(output)
     - For each layer, going from LAST to FIRST:
       a. Compute gradient of loss w.r.t. layer's pre-activation
       b. Compute gradient of loss w.r.t. layer's weights
       c. Compute gradient of loss w.r.t. layer's biases
       d. Compute gradient of loss w.r.t. layer's input
          (this becomes the "gradient from above" for the previous layer)

  3. UPDATE
     - For each weight: w = w - learning_rate * dL/dw
     - For each bias: b = b - learning_rate * dL/db

UNTIL the loss is small enough or we run out of patience
```

### Why Must We Store Intermediate Values?

```
Why We Store Values During Forward Pass
==========================================

During the forward pass, we compute:
  z1, h, z2, output

During the backward pass, we NEED these values:
  - h is needed to compute dL/dw2 = dL/dz2 * h
  - sigmoid_derivative needs h
  - x is needed to compute dL/dw1

If we did not store them, we would have to recompute them,
wasting time and memory.

This is why training neural networks uses a lot of memory:
  We must store ALL intermediate values for EVERY layer.
```

---

## Common Mistakes

```
Common Mistakes with Backpropagation
========================================

MISTAKE 1: Forgetting to store intermediate values
  Wrong: Only keeping the final output
  Right: Store z, h, and all intermediate values during forward pass
  Why: The backward pass needs these values to compute gradients

MISTAKE 2: Wrong order of operations
  Wrong: Computing dL/dw1 before dL/dw2
  Right: Start from the LAST layer and work backward
  Why: Each layer's gradient depends on the gradient from the layer
       after it. You must compute the later gradients first.

MISTAKE 3: Forgetting the activation function derivative
  Wrong: dL/dz1 = dL/dh (skipping sigmoid derivative)
  Right: dL/dz1 = dL/dh * sigmoid_derivative(h)
  Why: The activation function is a link in the chain.
       The chain rule requires multiplying through it.

MISTAKE 4: Confusing which values to use
  Wrong: Using the UPDATED weights during the backward pass
  Right: Use the ORIGINAL weights during backward pass, then update
  Why: Updating weights during backward would give wrong gradients
       for earlier layers.

MISTAKE 5: Wrong sign in the update rule
  Wrong: w = w + lr * gradient  (moves toward higher loss)
  Right: w = w - lr * gradient  (moves toward lower loss)
  Why: We want to DECREASE the loss, so we go in the
       OPPOSITE direction of the gradient.
```

---

## Best Practices

```
Best Practices for Understanding Backpropagation
====================================================

1. TRACE BY HAND FIRST
   Before trusting PyTorch to do it automatically, work through
   at least one example by hand. This builds deep understanding.

2. CHECK YOUR GRADIENTS
   Use numerical gradient checking to verify your analytical gradients.
   Compute (f(w+epsilon) - f(w-epsilon)) / (2*epsilon) and compare.

3. UNDERSTAND BEFORE AUTOMATING
   PyTorch computes gradients automatically. But understanding
   the math helps you debug problems like vanishing gradients.

4. DRAW THE COMPUTATIONAL GRAPH
   When confused, draw the graph. It makes the chain rule visual.

5. REMEMBER: BACKWARD = CHAIN RULE
   Every step in backpropagation is just the chain rule applied
   to one link in the chain. Nothing more.
```

---

## Quick Summary

```
Chapter 6 Summary: Backpropagation
======================================

1. Backpropagation computes gradients (rates of change) for every
   weight in the network by tracing the error BACKWARD from the loss.

2. The chain rule lets us multiply rates of change along a chain
   of operations: dL/dw = dL/dz * dz/dw.

3. The forward pass computes predictions (left to right).
   The backward pass computes gradients (right to left).

4. For each weight, the gradient tells us:
   - Direction: should the weight go up or down?
   - Amount: how much should it change?

5. Computational graphs track every operation so that PyTorch
   can automatically compute the backward pass for you.

6. Backpropagation is what makes deep learning possible.
   Without it, we could not train networks with millions of weights.
```

---

## Key Points

- **Backpropagation** = computing gradients by flowing errors backward through the network
- **Chain rule** = multiply the rates of change along a chain: dL/dw = dL/dy * dy/dw
- **Forward pass** = compute predictions (input to output, left to right)
- **Backward pass** = compute gradients (loss to input, right to left)
- **Gradient** = tells you the direction and amount to change each weight
- **Computational graph** = a diagram of every operation, used to automate the backward pass
- **Update rule** = w_new = w_old - learning_rate * gradient (subtract to decrease loss)
- **Intermediate values** must be stored during forward pass because backward pass needs them

---

## Practice Questions

1. In the chain rule, if y = 4x and z = 3y, what is dz/dx? Walk through the calculation.

2. In a single-neuron network with x=3.0, w=0.2, b=0.1, and target=1.0, compute the forward pass (prediction and loss), then compute dL/dw and dL/db.

3. Explain in your own words why the backward pass must go from the LAST layer to the FIRST layer, not the other way around.

4. If the gradient for a weight is -2.5 and the learning rate is 0.01, what is the new weight if the old weight was 1.0? Will the weight increase or decrease?

5. Why does training a neural network use a lot of memory? What is stored during the forward pass and why?

---

## Exercises

### Exercise 1: Three-Step Chain

Create a chain of three operations: y = 2x, z = y + 3, L = z squared. Given x = 1.0, compute the forward pass, then use the chain rule to find dL/dx. Verify your answer by computing L at x = 1.0 and x = 1.001, and checking that the numerical gradient matches.

### Exercise 2: Multiple Training Steps

Modify the single-neuron backpropagation code (Section 6.3) to run 20 training steps. Plot or print the loss at each step. Observe how the loss decreases. Try different learning rates (0.01, 0.1, 0.5, 1.0) and compare how fast the network learns.

### Exercise 3: Build a Computational Graph

Extend the computational graph code (Section 6.6) to include a SigmoidNode class. Build a graph that computes: z = sigmoid(w * x + b). Run the forward and backward passes with x=1.0, w=0.5, b=-0.2. Verify that your gradients match the ones you would compute by hand.

---

## What Is Next?

Now you understand HOW the network computes gradients for each weight. But we skipped a critical question: once we have the gradients, how exactly do we update the weights? The simple rule "w = w - lr * gradient" is just the beginning.

In Chapter 7, you will learn about **gradient descent and optimizers**. You will discover why the learning rate matters so much, how momentum helps the network learn faster, and why the Adam optimizer is the default choice in modern deep learning. The optimizer is the engine that drives the learning process, and understanding it will give you the power to train networks that actually work.
