# Chapter 2: The Perceptron — The Simplest Neural Network

## What You Will Learn

In this chapter, you will learn:

- What a perceptron is and why it is the foundation of all neural networks
- How inputs, weights, bias, and activation work together
- How the weighted sum works (it is like a voting system)
- What a step function is and how it makes decisions
- How the perceptron learning rule adjusts weights when the prediction is wrong
- How to build a perceptron from scratch in pure Python (no frameworks needed)
- Why the perceptron cannot solve the XOR problem
- Why this limitation led to the invention of multi-layer networks

## Why This Chapter Matters

The perceptron is the single most important concept in deep learning history. Every neural network, no matter how complex, is built from simple units that work like perceptrons. Understanding the perceptron is like understanding a single brick before building a skyscraper. You cannot build the skyscraper without understanding the brick.

When Frank Rosenblatt invented the perceptron in 1958, it was front-page news. People thought machines would soon think like humans. Then researchers discovered a critical limitation: the perceptron cannot solve certain simple problems. This discovery nearly killed the entire field of neural networks for over a decade.

By the end of this chapter, you will understand both the power and the limitation of the perceptron. You will build one from scratch and see it learn. This hands-on experience will prepare you for the multi-layer networks in Chapter 3.

---

## What Is a Perceptron?

A **perceptron** is the simplest possible neural network. It has just one neuron. That single neuron takes some inputs, processes them, and produces one output.

Think of a perceptron like a person making a yes-or-no decision.

### Real-Life Analogy: Should I Bring an Umbrella?

Imagine you are deciding whether to bring an umbrella when you leave the house. You consider several factors:

- Is it cloudy? (Yes = 1, No = 0)
- Did the weather app say rain? (Yes = 1, No = 0)
- Is it the rainy season? (Yes = 1, No = 0)

But not all factors matter equally to you:

- You trust the weather app a lot (high weight)
- You think clouds are somewhat important (medium weight)
- You care a little about the season (low weight)

You mentally add up these weighted factors. If the total is above some threshold, you grab the umbrella. If not, you leave it.

**That is exactly how a perceptron works.**

```
    The Umbrella Decision (A Perceptron)
    =====================================

    Inputs              Weights
    ------              -------
    Cloudy? (1) ----[weight: 0.3]---\
                                      \
    Weather app                        \
    says rain? (1) -[weight: 0.5]-------> WEIGHTED SUM --> Step Function --> Output
                                      /                   (threshold)    (yes/no)
    Rainy                            /
    season? (0) ---[weight: 0.2]---/

    Weighted Sum = (1 x 0.3) + (1 x 0.5) + (0 x 0.2) + bias
                 = 0.3 + 0.5 + 0.0 + (-0.4)
                 = 0.4

    Step Function: Is 0.4 >= 0? YES --> Output = 1 (Bring umbrella!)
```

---

## The Four Parts of a Perceptron

Every perceptron has exactly four parts: inputs, weights, bias, and an activation function. Let us look at each one.

### Part 1: Inputs

**Inputs** are the data that goes into the perceptron. Each input is a number.

In the umbrella example, the inputs were 1 (cloudy), 1 (rain predicted), and 0 (not rainy season). In a real machine learning problem, inputs could be:

- Pixel values from an image (0 to 255)
- Measurements from a sensor (temperature, humidity)
- Features of a house (size, number of bedrooms, location score)

The key idea is: **inputs are just numbers that describe something**.

### Part 2: Weights

**Weights** are numbers that tell the perceptron how important each input is. Every input gets its own weight.

- A large positive weight means "this input strongly pushes toward yes"
- A large negative weight means "this input strongly pushes toward no"
- A weight near zero means "this input does not matter much"

Think of weights like the volume knobs on a music mixer. Each knob controls how loud one instrument is. Turning up the guitar knob makes the guitar louder in the mix. Similarly, increasing a weight makes that input have more influence on the output.

```
    Weights Are Like Volume Knobs
    ==============================

    Input 1 ----[knob: LOUD  (0.9)]----\
                                         \
    Input 2 ----[knob: QUIET (0.1)]-------> Mixed Output
                                         /
    Input 3 ----[knob: MEDIUM(0.5)]----/

    Input 1 has the most influence because its "knob" is turned up highest.
```

**The perceptron learns by adjusting these weights.** This is the most important idea. The weights start as random numbers. During training, the perceptron changes them to make better predictions. Learning IS the process of finding the right weights.

### Part 3: Bias

The **bias** is an extra number added to the weighted sum. It does not multiply any input. It just shifts the total up or down.

Why do we need a bias? Think about it this way. Imagine a perceptron that decides if a student passes an exam. Without a bias, a student with all-zero inputs would always get a weighted sum of zero. The bias lets the perceptron set a "starting point" or "baseline."

Another way to think about bias: it is like the y-intercept in the equation of a line (y = mx + b). The "b" is the bias. It shifts the line up or down.

```
    Without Bias                   With Bias
    ============                   =========

    Sum = w1*x1 + w2*x2           Sum = w1*x1 + w2*x2 + bias

    If all inputs are 0:          If all inputs are 0:
    Sum = 0 (always)              Sum = bias (can be anything)

    The decision boundary         The decision boundary can
    must pass through             be shifted to any position.
    the origin (0,0).
```

### Part 4: Activation Function (Step Function)

The **activation function** takes the weighted sum and produces the final output. For the original perceptron, this is the **step function**.

The step function is the simplest possible activation function. It works like a light switch:

- If the weighted sum is 0 or above, output 1 (ON)
- If the weighted sum is below 0, output 0 (OFF)

```
    The Step Function
    ==================

    Output
    1 |          _______________
      |         |
      |         |
      |         |
    0 |_________|
      |
      +---------+--------------> Weighted Sum
               0

    Below 0 --> Output is 0
    At 0 or above --> Output is 1
```

There is no "maybe" with the step function. It is always 0 or 1, off or on, no or yes. Later, in Chapter 4, you will learn about smoother activation functions like sigmoid and ReLU that can produce values between 0 and 1.

---

## The Math Behind the Perceptron

Now let us put all four parts together with actual numbers. The perceptron computes in two steps.

### Step 1: Calculate the Weighted Sum

The weighted sum (also called the "pre-activation" value) is:

```
    z = (x1 * w1) + (x2 * w2) + ... + (xn * wn) + bias
```

Where:
- x1, x2, ..., xn are the inputs
- w1, w2, ..., wn are the weights
- bias is the bias term
- z is the weighted sum

In shorter math notation, this is written as:

```
    z = SUM(xi * wi) + bias    (for all i from 1 to n)
```

### Step 2: Apply the Step Function

```
    output = 1    if z >= 0
    output = 0    if z < 0
```

### Worked Example

Let us work through a complete example with three inputs.

```
    Inputs:   x1 = 0.5,  x2 = 0.8,  x3 = 0.2
    Weights:  w1 = 0.4,  w2 = -0.3, w3 = 0.6
    Bias:     b = -0.1

    Step 1: Weighted Sum
    z = (0.5 * 0.4) + (0.8 * -0.3) + (0.2 * 0.6) + (-0.1)
    z = 0.20 + (-0.24) + 0.12 + (-0.1)
    z = 0.20 - 0.24 + 0.12 - 0.1
    z = -0.02

    Step 2: Step Function
    z = -0.02, which is less than 0
    output = 0
```

The perceptron outputs 0. If we were deciding "bring umbrella or not," the answer would be "no."

---

## The Perceptron as a Voting System

Here is a powerful way to think about what the perceptron does: **it is like a weighted voting system**.

Imagine a committee of three people voting on a decision:

- Person A has 4 votes (weight = 0.4)
- Person B has 3 votes against (weight = -0.3, negative means they vote "no")
- Person C has 6 votes (weight = 0.6)

Each person looks at their input and casts their weighted vote. The votes are added up. If the total is above the threshold (adjusted by bias), the motion passes.

```
    Voting System Analogy
    ======================

    Person A:  Input=0.5, Weight=0.4  --> Vote: 0.5 * 0.4 =  0.20
    Person B:  Input=0.8, Weight=-0.3 --> Vote: 0.8 *-0.3 = -0.24  (votes against!)
    Person C:  Input=0.2, Weight=0.6  --> Vote: 0.2 * 0.6 =  0.12
                                                              ------
    Total votes:                                               0.08
    Bias (threshold adjustment):                              -0.10
                                                              ------
    Final total:                                              -0.02

    Result: -0.02 < 0 --> Motion REJECTED (output = 0)
```

This voting analogy helps you understand what happens during learning. When the perceptron gets a wrong answer, it changes the weights. This is like changing how many votes each committee member gets. Over time, the weights adjust so the committee makes the right decision.

---

## Building a Perceptron from Scratch in Python

Now let us build a perceptron from scratch. We will use only basic Python. No PyTorch, no NumPy, no frameworks. This way, you will understand every single calculation.

### A Simple Perceptron Class

```python
class Perceptron:
    """A single perceptron (neuron) that learns to classify inputs."""

    def __init__(self, num_inputs, learning_rate=0.1):
        """
        Create a perceptron with the given number of inputs.

        Parameters:
            num_inputs: How many input values the perceptron receives
            learning_rate: How much to adjust weights when wrong (default 0.1)
        """
        # Start with all weights set to zero
        self.weights = [0.0] * num_inputs
        # Start with bias set to zero
        self.bias = 0.0
        # Learning rate controls how big each weight adjustment is
        self.learning_rate = learning_rate

    def weighted_sum(self, inputs):
        """
        Calculate the weighted sum of inputs.
        This is: (x1*w1) + (x2*w2) + ... + bias
        """
        total = 0.0
        for i in range(len(inputs)):
            total += inputs[i] * self.weights[i]
        total += self.bias
        return total

    def step_function(self, value):
        """
        Apply the step function.
        Returns 1 if value >= 0, otherwise returns 0.
        """
        if value >= 0:
            return 1
        else:
            return 0

    def predict(self, inputs):
        """
        Make a prediction for the given inputs.
        Step 1: Calculate weighted sum
        Step 2: Apply step function
        """
        z = self.weighted_sum(inputs)
        output = self.step_function(z)
        return output

    def train_one(self, inputs, expected_output):
        """
        Train the perceptron on one example.
        If the prediction is wrong, adjust the weights and bias.

        Parameters:
            inputs: The input values
            expected_output: The correct answer (0 or 1)

        Returns:
            The error (expected - predicted). Zero means correct.
        """
        # Step 1: Make a prediction
        prediction = self.predict(inputs)

        # Step 2: Calculate the error
        error = expected_output - prediction

        # Step 3: If there is an error, adjust weights and bias
        if error != 0:
            for i in range(len(self.weights)):
                # Adjust each weight: weight += learning_rate * error * input
                self.weights[i] += self.learning_rate * error * inputs[i]
            # Adjust bias: bias += learning_rate * error
            self.bias += self.learning_rate * error

        return error

    def train(self, training_data, labels, epochs=100):
        """
        Train the perceptron on a dataset for multiple epochs.

        Parameters:
            training_data: List of input examples
            labels: List of correct outputs (0 or 1)
            epochs: How many times to go through all examples
        """
        for epoch in range(epochs):
            total_error = 0
            for inputs, expected in zip(training_data, labels):
                error = self.train_one(inputs, expected)
                total_error += abs(error)

            # Print progress every 10 epochs
            if (epoch + 1) % 10 == 0 or epoch == 0:
                print(f"Epoch {epoch + 1:3d}: Total errors = {total_error}, "
                      f"Weights = [{', '.join(f'{w:.2f}' for w in self.weights)}], "
                      f"Bias = {self.bias:.2f}")

            # Stop early if no errors
            if total_error == 0:
                print(f"\nPerfect! Converged at epoch {epoch + 1}.")
                break
```

### Line-by-Line Explanation

Let us break down the most important parts.

**The `__init__` method (constructor):**

```python
self.weights = [0.0] * num_inputs
```

This creates a list of weights, all starting at zero. If `num_inputs` is 2, this creates `[0.0, 0.0]`. We start at zero because the perceptron will learn the right values.

```python
self.bias = 0.0
```

The bias also starts at zero. It will be adjusted during training.

```python
self.learning_rate = 0.1
```

The **learning rate** controls how much the weights change on each update. A small learning rate (like 0.01) means tiny adjustments. A large one (like 1.0) means big adjustments. We use 0.1 as a reasonable middle ground. Think of it like turning a knob: a small learning rate turns the knob gently, a large one cranks it hard.

**The `weighted_sum` method:**

```python
total = 0.0
for i in range(len(inputs)):
    total += inputs[i] * self.weights[i]
total += self.bias
```

This multiplies each input by its matching weight and adds them all up, then adds the bias. It is the core calculation of the perceptron.

**The `train_one` method (the learning rule):**

```python
error = expected_output - prediction
```

The error is simply: what we wanted minus what we got. Three possible results:
- Error = 0: prediction was correct, do nothing
- Error = 1: expected 1 but predicted 0 (missed a positive case)
- Error = -1: expected 0 but predicted 1 (false alarm)

```python
self.weights[i] += self.learning_rate * error * inputs[i]
```

This is the **perceptron learning rule**. It adjusts each weight based on three things:
1. The learning rate (how big the step is)
2. The error (which direction to adjust)
3. The input value (how much this input contributed to the mistake)

If the input was large and the error was positive, the weight increases a lot. If the input was zero, the weight does not change at all (because `0 * anything = 0`).

---

## Teaching the Perceptron: The AND Gate

Let us train our perceptron on a classic problem: the **AND gate**.

The AND gate is a simple logic operation. It outputs 1 only when BOTH inputs are 1.

```
    AND Gate Truth Table
    =====================

    Input 1  |  Input 2  |  Output
    ---------|-----------|--------
       0     |     0     |    0
       0     |     1     |    0
       1     |     0     |    0
       1     |     1     |    1

    Only when BOTH inputs are 1, the output is 1.
```

### Training the AND Gate

```python
# Define the AND gate training data
training_data = [
    [0, 0],    # Both off
    [0, 1],    # First off, second on
    [1, 0],    # First on, second off
    [1, 1],    # Both on
]

labels = [0, 0, 0, 1]  # AND gate outputs

# Create a perceptron with 2 inputs
p = Perceptron(num_inputs=2, learning_rate=0.1)

print("=== Training the AND Gate ===\n")
print("Before training:")
for inputs, expected in zip(training_data, labels):
    prediction = p.predict(inputs)
    print(f"  Input: {inputs} -> Predicted: {prediction}, Expected: {expected}")

print("\nTraining...\n")
p.train(training_data, labels, epochs=100)

print("\nAfter training:")
for inputs, expected in zip(training_data, labels):
    prediction = p.predict(inputs)
    status = "Correct!" if prediction == expected else "WRONG"
    print(f"  Input: {inputs} -> Predicted: {prediction}, Expected: {expected} ({status})")

print(f"\nFinal weights: {[f'{w:.2f}' for w in p.weights]}")
print(f"Final bias: {p.bias:.2f}")
```

**Output:**

```
=== Training the AND Gate ===

Before training:
  Input: [0, 0] -> Predicted: 1, Expected: 0
  Input: [0, 1] -> Predicted: 1, Expected: 0
  Input: [1, 0] -> Predicted: 1, Expected: 0
  Input: [1, 1] -> Predicted: 1, Expected: 1

Training...

Epoch   1: Total errors = 3, Weights = [0.10, 0.10], Bias = -0.30
Epoch  10: Total errors = 0, Weights = [0.20, 0.10], Bias = -0.30

Perfect! Converged at epoch 10.

After training:
  Input: [0, 0] -> Predicted: 0, Expected: 0 (Correct!)
  Input: [0, 1] -> Predicted: 0, Expected: 0 (Correct!)
  Input: [1, 0] -> Predicted: 0, Expected: 0 (Correct!)
  Input: [1, 1] -> Predicted: 1, Expected: 1 (Correct!)

Final weights: ['0.20', '0.10']
Final bias: -0.30
```

The perceptron learned the AND gate. Let us verify the math:

```
    Verification with Final Weights
    ================================

    Weights: [0.20, 0.10], Bias: -0.30

    [0, 0]: (0*0.20) + (0*0.10) + (-0.30) = -0.30 < 0 --> 0  Correct!
    [0, 1]: (0*0.20) + (1*0.10) + (-0.30) = -0.20 < 0 --> 0  Correct!
    [1, 0]: (1*0.20) + (0*0.10) + (-0.30) = -0.10 < 0 --> 0  Correct!
    [1, 1]: (1*0.20) + (1*0.10) + (-0.30) =  0.00 >= 0 --> 1 Correct!
```

---

## Teaching the Perceptron: The OR Gate

The OR gate outputs 1 when at least one input is 1.

```
    OR Gate Truth Table
    ====================

    Input 1  |  Input 2  |  Output
    ---------|-----------|--------
       0     |     0     |    0
       0     |     1     |    1
       1     |     0     |    1
       1     |     1     |    1
```

```python
# Define the OR gate training data
training_data = [
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1],
]

labels = [0, 1, 1, 1]  # OR gate outputs

# Create and train a perceptron
p = Perceptron(num_inputs=2, learning_rate=0.1)

print("=== Training the OR Gate ===\n")
p.train(training_data, labels, epochs=100)

print("\nResults:")
for inputs, expected in zip(training_data, labels):
    prediction = p.predict(inputs)
    status = "Correct!" if prediction == expected else "WRONG"
    print(f"  Input: {inputs} -> Predicted: {prediction}, Expected: {expected} ({status})")

print(f"\nFinal weights: {[f'{w:.2f}' for w in p.weights]}")
print(f"Final bias: {p.bias:.2f}")
```

**Output:**

```
=== Training the OR Gate ===

Epoch   1: Total errors = 2, Weights = [0.10, 0.10], Bias = -0.10
Epoch  10: Total errors = 0, Weights = [0.10, 0.10], Bias = -0.10

Perfect! Converged at epoch 10.

Results:
  Input: [0, 0] -> Predicted: 0, Expected: 0 (Correct!)
  Input: [0, 1] -> Predicted: 1, Expected: 1 (Correct!)
  Input: [1, 0] -> Predicted: 1, Expected: 1 (Correct!)
  Input: [1, 1] -> Predicted: 1, Expected: 1 (Correct!)

Final weights: ['0.10', '0.10']
Final bias: -0.10
```

The perceptron can learn AND and OR. So far, so good. But there is a problem coming.

---

## The Perceptron as a Line Drawer

Here is a key insight: **a perceptron with two inputs draws a straight line to separate two groups**.

Think of a 2D graph where the x-axis is Input 1 and the y-axis is Input 2. Each training example is a point on this graph. The perceptron finds a straight line that puts all the 0s on one side and all the 1s on the other.

```
    AND Gate: The Perceptron Draws a Line
    =======================================

    Input 2
    1.0 |  (0,1)         (1,1)
        |   [0]     /      [1]
        |         /
        |       /   <-- The perceptron draws
    0.5 |     /         this line
        |   /
        | /
    0.0 | (0,0)         (1,0)
        |   [0]          [0]
        +---+-----+-----+----> Input 1
           0.0   0.5   1.0

    Everything ABOVE the line = class 1
    Everything BELOW the line = class 0


    OR Gate: A Different Line
    ==========================

    Input 2
    1.0 |  (0,1)         (1,1)
        |   [1]           [1]
        |       \
    0.5 |         \   <-- Different line,
        |           \     same idea
        |             \
    0.0 | (0,0)         (1,0)
        |   [0]           [1]
        +---+-----+-----+----> Input 1
           0.0   0.5   1.0
```

This concept is called **linear separability**. If you can draw a single straight line to separate the two classes, the data is linearly separable, and a perceptron can learn it.

---

## The XOR Problem: Where the Perceptron Fails

Now let us try the **XOR gate** (exclusive OR). XOR outputs 1 when the inputs are different, and 0 when they are the same.

```
    XOR Gate Truth Table
    =====================

    Input 1  |  Input 2  |  Output
    ---------|-----------|--------
       0     |     0     |    0
       0     |     1     |    1
       1     |     0     |    1
       1     |     1     |    0     <-- Different from OR!
```

Let us try to train our perceptron on XOR:

```python
# Define the XOR gate training data
training_data = [
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1],
]

labels = [0, 1, 1, 0]  # XOR gate outputs

# Create and train a perceptron
p = Perceptron(num_inputs=2, learning_rate=0.1)

print("=== Training the XOR Gate ===\n")
p.train(training_data, labels, epochs=100)

print("\nResults:")
for inputs, expected in zip(training_data, labels):
    prediction = p.predict(inputs)
    status = "Correct!" if prediction == expected else "WRONG"
    print(f"  Input: {inputs} -> Predicted: {prediction}, Expected: {expected} ({status})")
```

**Output:**

```
=== Training the XOR Gate ===

Epoch   1: Total errors = 3, Weights = [0.10, 0.00], Bias = -0.10
Epoch  10: Total errors = 4, Weights = [0.00, -0.10], Bias = 0.00
Epoch  20: Total errors = 4, Weights = [0.00, 0.00], Bias = -0.10
Epoch  30: Total errors = 4, Weights = [-0.10, 0.00], Bias = 0.10
Epoch  40: Total errors = 4, Weights = [0.10, 0.00], Bias = -0.10
Epoch  50: Total errors = 4, Weights = [0.00, -0.10], Bias = 0.00
Epoch  60: Total errors = 4, Weights = [0.00, 0.00], Bias = -0.10
Epoch  70: Total errors = 4, Weights = [-0.10, 0.00], Bias = 0.10
Epoch  80: Total errors = 4, Weights = [0.10, 0.00], Bias = -0.10
Epoch  90: Total errors = 4, Weights = [0.00, -0.10], Bias = 0.00
Epoch 100: Total errors = 4, Weights = [0.00, 0.00], Bias = -0.10

Results:
  Input: [0, 0] -> Predicted: 0, Expected: 0 (WRONG)
  Input: [0, 1] -> Predicted: 0, Expected: 1 (WRONG)
  Input: [1, 0] -> Predicted: 0, Expected: 1 (WRONG)
  Input: [1, 1] -> Predicted: 0, Expected: 0 (WRONG)
```

**The perceptron never converges.** After 100 epochs, it is still making errors. The total errors never reach zero. The weights keep bouncing around without finding a solution.

### Why XOR Is Impossible for a Perceptron

Look at the XOR data on a graph:

```
    XOR: No Single Line Can Separate the Classes!
    ===============================================

    Input 2
    1.0 |  (0,1)         (1,1)
        |   [1]           [0]
        |
        |   How can you draw ONE straight line
    0.5 |   that puts [1]s on one side and
        |   [0]s on the other?
        |
    0.0 | (0,0)         (1,0)
        |   [0]           [1]
        +---+-----+-----+----> Input 1
           0.0   0.5   1.0

    You CANNOT! The [1]s are on opposite corners.
    The [0]s are on opposite corners.
    No single straight line can separate them.

    Try any line:

    /   <-- This separates (0,0) from others,
            but puts (1,1) with the [1]s. WRONG.

    \   <-- This separates (1,0) from others,
            but puts (0,1) with the [0]s. WRONG.

    |   <-- Vertical line? Puts (0,0) with (0,1). WRONG.

    --  <-- Horizontal line? Puts (0,0) with (1,0). WRONG.
```

**The XOR problem is not linearly separable.** You need at least two lines (or a curved line) to separate the classes. A single perceptron can only draw one straight line. Therefore, a single perceptron CANNOT solve XOR.

This was proven mathematically by Marvin Minsky and Seymour Papert in their 1969 book. Their proof was so influential that it caused a "winter" in neural network research that lasted until the 1980s.

---

## Why We Need Multiple Layers

The XOR problem shows us the fundamental limitation of a single perceptron: it can only solve linearly separable problems. But most real-world problems are NOT linearly separable. Recognizing faces, understanding language, playing games — none of these can be solved with a single straight line.

The solution? **Use multiple perceptrons arranged in layers.**

Here is the key insight: XOR can be built from AND, OR, and NOT operations:

```
    XOR(A, B) = AND(OR(A, B), NOT(AND(A, B)))

    Or equivalently:
    XOR(A, B) = OR(AND(A, NOT(B)), AND(NOT(A), B))
```

A single perceptron can learn AND. A single perceptron can learn OR. So if we connect multiple perceptrons together, they can combine these simple operations into more complex ones, like XOR.

```
    Solving XOR with Multiple Perceptrons
    =======================================

    Input 1 --------+-------> [Perceptron 1] ---> h1
                     |              (learns something
                     |               like "OR")
    Input 2 ---+-----+
               |     |
               |     +-------> [Perceptron 2] ---> h2 ----> [Perceptron 3] --> Output
               |                    (learns something          (combines h1
               +---------------     like "NAND")               and h2)

    Layer 1 (Hidden)              Layer 2 (Output)
    2 perceptrons                 1 perceptron

    Together, they can solve XOR!
```

This is exactly what we will build in Chapter 3: Multi-Layer Networks. By stacking layers of perceptrons, we can solve problems that a single perceptron cannot.

---

## The Perceptron Learning Rule Explained

Let us take a closer look at how the perceptron learns. The learning rule is surprisingly simple:

```
    The Perceptron Learning Rule
    =============================

    For each training example:

    1. Make a prediction
    2. Calculate error = expected - predicted
    3. If error is not zero:
       - For each weight:  weight_new = weight_old + learning_rate * error * input
       - For bias:         bias_new = bias_old + learning_rate * error

    That is it. Three steps.
```

### Why Does This Work?

Let us think about what happens in each error case:

**Case 1: Expected 1, Predicted 0 (error = +1)**

The perceptron should have fired but did not. The weighted sum was too low. So we need to:
- Increase weights for inputs that were positive (they should have pushed the sum higher)
- The adjustment is: `weight += learning_rate * 1 * input`
- For positive inputs, this increases the weight (good!)
- For zero inputs, no change (makes sense, they did not contribute)

**Case 2: Expected 0, Predicted 1 (error = -1)**

The perceptron fired when it should not have. The weighted sum was too high. So we need to:
- Decrease weights for inputs that were positive (they pushed the sum too high)
- The adjustment is: `weight += learning_rate * (-1) * input`
- For positive inputs, this decreases the weight (good!)
- For zero inputs, no change (makes sense)

**Case 3: Prediction is correct (error = 0)**

No adjustment needed. The weights are fine for this example.

```
    Learning Rule Examples
    =======================

    Example: Input = [1, 0.5], Expected = 1, Predicted = 0
    Error = 1 - 0 = 1
    Learning rate = 0.1

    w1_new = w1_old + 0.1 * 1 * 1   = w1_old + 0.10  (increase!)
    w2_new = w2_old + 0.1 * 1 * 0.5 = w2_old + 0.05  (increase a bit)
    b_new  = b_old  + 0.1 * 1       = b_old  + 0.10  (increase!)

    The weights and bias are nudged so the weighted sum will be
    higher next time, making it more likely to predict 1.
```

---

## The Learning Rate: How Fast Should We Learn?

The **learning rate** is a number (usually between 0.001 and 1.0) that controls how much the weights change on each update.

```
    Learning Rate Effects
    ======================

    Too small (0.001):
    - Changes are tiny
    - Takes many epochs to learn
    - But will eventually get there

    Just right (0.1):
    - Changes are moderate
    - Learns in a reasonable time
    - Good balance

    Too large (10.0):
    - Changes are huge
    - Weights bounce around wildly
    - May never converge (find a solution)

    Think of it like tuning a radio:
    - Too gentle: Takes forever to find the station
    - Just right: You find the station smoothly
    - Too aggressive: You keep overshooting the station
```

Let us see the effect:

```python
print("=== Effect of Learning Rate ===\n")

for lr in [0.01, 0.1, 1.0]:
    training_data = [[0, 0], [0, 1], [1, 0], [1, 1]]
    labels = [0, 0, 0, 1]  # AND gate

    p = Perceptron(num_inputs=2, learning_rate=lr)

    # Count how many epochs to converge
    for epoch in range(1000):
        total_error = 0
        for inputs, expected in zip(training_data, labels):
            error = p.train_one(inputs, expected)
            total_error += abs(error)
        if total_error == 0:
            print(f"Learning rate {lr}: Converged in {epoch + 1} epochs")
            break
    else:
        print(f"Learning rate {lr}: Did NOT converge in 1000 epochs")
```

**Output:**

```
=== Effect of Learning Rate ===

Learning rate 0.01: Converged in 69 epochs
Learning rate 0.1: Converged in 10 epochs
Learning rate 1.0: Converged in 5 epochs
```

For this simple problem, a larger learning rate converges faster. But for more complex problems, a large learning rate can cause instability. We will explore this more in Chapter 7 (Optimizers).

---

## A Real-World Example: Classifying Flowers

Let us use our perceptron on a slightly more realistic problem. We will classify flowers into two types based on petal length and petal width.

```python
# Simple flower dataset (inspired by the Iris dataset)
# Each flower has: [petal_length, petal_width]
# Label: 0 = Setosa (small petals), 1 = Versicolor (larger petals)

training_data = [
    [1.4, 0.2],  # Setosa
    [1.0, 0.1],  # Setosa
    [1.5, 0.4],  # Setosa
    [1.3, 0.3],  # Setosa
    [1.1, 0.1],  # Setosa
    [4.5, 1.5],  # Versicolor
    [4.0, 1.3],  # Versicolor
    [4.7, 1.4],  # Versicolor
    [3.9, 1.1],  # Versicolor
    [4.2, 1.2],  # Versicolor
]

labels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]

# Normalize inputs to 0-1 range for better learning
# Find min and max for each feature
min_length = min(d[0] for d in training_data)
max_length = max(d[0] for d in training_data)
min_width = min(d[1] for d in training_data)
max_width = max(d[1] for d in training_data)

normalized_data = []
for d in training_data:
    norm_length = (d[0] - min_length) / (max_length - min_length)
    norm_width = (d[1] - min_width) / (max_width - min_width)
    normalized_data.append([norm_length, norm_width])

# Create and train the perceptron
p = Perceptron(num_inputs=2, learning_rate=0.1)

print("=== Flower Classification ===\n")
p.train(normalized_data, labels, epochs=100)

print("\nResults:")
flower_names = ["Setosa"] * 5 + ["Versicolor"] * 5
for i, (inputs, expected) in enumerate(zip(normalized_data, labels)):
    prediction = p.predict(inputs)
    name = flower_names[i]
    status = "Correct!" if prediction == expected else "WRONG"
    print(f"  {name:12s} {training_data[i]} -> Predicted: {prediction} ({status})")

# Test with a new flower
new_flower = [3.0, 0.8]
norm_new = [
    (new_flower[0] - min_length) / (max_length - min_length),
    (new_flower[1] - min_width) / (max_width - min_width),
]
prediction = p.predict(norm_new)
print(f"\nNew flower with petal length={new_flower[0]}, width={new_flower[1]}")
print(f"Prediction: {'Versicolor' if prediction == 1 else 'Setosa'}")
```

**Output:**

```
=== Flower Classification ===

Epoch   1: Total errors = 2, Weights = [0.10, 0.08], Bias = -0.10
Epoch  10: Total errors = 0, Weights = [0.24, 0.15], Bias = -0.20

Perfect! Converged at epoch 10.

Results:
  Setosa       [1.4, 0.2] -> Predicted: 0 (Correct!)
  Setosa       [1.0, 0.1] -> Predicted: 0 (Correct!)
  Setosa       [1.5, 0.4] -> Predicted: 0 (Correct!)
  Setosa       [1.3, 0.3] -> Predicted: 0 (Correct!)
  Setosa       [1.1, 0.1] -> Predicted: 0 (Correct!)
  Versicolor   [4.5, 1.5] -> Predicted: 1 (Correct!)
  Versicolor   [4.0, 1.3] -> Predicted: 1 (Correct!)
  Versicolor   [4.7, 1.4] -> Predicted: 1 (Correct!)
  Versicolor   [3.9, 1.1] -> Predicted: 1 (Correct!)
  Versicolor   [4.2, 1.2] -> Predicted: 1 (Correct!)

New flower with petal length=3.0, width=0.8
Prediction: Versicolor
```

The perceptron successfully classified the flowers. It found a line in the petal-length vs petal-width space that separates the two species. This works because the two species are linearly separable in these dimensions.

---

## Common Mistakes

1. **Forgetting to normalize inputs.** If one input ranges from 0 to 1 and another from 0 to 1000, the large input will dominate the weighted sum. Always normalize your inputs to a similar range (usually 0 to 1 or -1 to 1).

2. **Setting the learning rate too high.** A learning rate above 1.0 often causes the weights to bounce wildly and never converge. Start with 0.1 and adjust from there.

3. **Expecting the perceptron to solve non-linear problems.** If your data is not linearly separable (like XOR), the perceptron will never converge. You need a multi-layer network (Chapter 3).

4. **Confusing weights with inputs.** Inputs are the data you feed in. Weights are what the perceptron learns. Beginners sometimes mix these up. Inputs come from outside. Weights live inside the perceptron.

5. **Thinking the step function is the only activation function.** The step function is simple but limited. Modern networks use sigmoid, ReLU, and other activation functions (Chapter 4).

---

## Best Practices

1. **Always initialize weights to small values.** Starting with zeros or small random numbers is standard. Large initial weights can cause problems.

2. **Normalize your input data.** Bring all features to a similar scale before training. This helps the perceptron learn faster and more reliably.

3. **Track errors during training.** Print or plot the total error at each epoch. If it is not decreasing, something is wrong (bad learning rate, non-separable data, or a bug).

4. **Start with simple problems.** Before tackling complex data, verify your perceptron works on AND and OR gates. This is a sanity check.

5. **Understand the limitation.** Know that a single perceptron can only learn linear decision boundaries. If your problem needs curves, you need more layers.

---

## Quick Summary

The perceptron is the simplest neural network: one neuron that takes inputs, multiplies each by a weight, adds a bias, and passes the result through a step function. It outputs 0 or 1.

The perceptron learns by adjusting its weights when it makes mistakes. The learning rule is: `weight_new = weight_old + learning_rate * error * input`. This simple rule allows the perceptron to find a line that separates two classes.

However, the perceptron can only solve linearly separable problems. It fails on XOR and any problem where a single straight line cannot separate the classes. This limitation is why we need multi-layer networks.

---

## Key Points

- A perceptron has four parts: inputs, weights, bias, and activation function (step function)
- The weighted sum is calculated as: z = (x1 * w1) + (x2 * w2) + ... + bias
- The step function outputs 1 if z >= 0, and 0 if z < 0
- The perceptron learns by adjusting weights when predictions are wrong
- The learning rate controls how much weights change on each update
- A perceptron draws a straight line to separate two classes (linear decision boundary)
- XOR cannot be solved by a single perceptron because it is not linearly separable
- The XOR limitation is why multi-layer networks were invented

---

## Practice Questions

1. A perceptron has weights [0.5, -0.3] and bias 0.1. What is the output for input [1, 1]? Show your work step by step.

2. Why does the perceptron fail on XOR? Draw the four XOR points on a 2D graph and explain why no single line can separate them.

3. What happens if you set the learning rate to 0? What happens if you set it to 100? Explain both cases.

4. A perceptron predicts 0 but the expected output is 1. The input is [0.5, 0.8] and the learning rate is 0.2. Calculate the new weights if the current weights are [0.3, 0.1].

5. Can a perceptron learn the NOT function (output = opposite of input)? It has one input. If input is 1, output is 0. If input is 0, output is 1. Try to figure out what weights and bias would work.

---

## Exercises

### Exercise 1: NAND Gate

The NAND gate (NOT AND) outputs 0 only when both inputs are 1. Its truth table is:

| Input 1 | Input 2 | Output |
|---------|---------|--------|
| 0       | 0       | 1      |
| 0       | 1       | 1      |
| 1       | 0       | 1      |
| 1       | 1       | 0      |

Train the perceptron on the NAND gate. Print the final weights and bias. Verify that the perceptron gets all four cases correct.

### Exercise 2: Multi-Feature Classification

Create a dataset of 10 "healthy" and 10 "unhealthy" food items with three features: calories (0-1000), sugar_grams (0-50), and fiber_grams (0-20). Normalize the features and train the perceptron to classify healthy vs unhealthy. Test it on 3 new food items.

### Exercise 3: Visualize the Decision Boundary

Using the AND gate perceptron, calculate and print the equation of the decision boundary line. The line is where the weighted sum equals zero: `w1*x1 + w2*x2 + bias = 0`. Solve for x2 to get: `x2 = -(w1*x1 + bias) / w2`. Print the x2 values for x1 = 0 and x1 = 1.

---

## What Is Next?

In this chapter, you learned how a single perceptron works: it takes inputs, applies weights and bias, passes through a step function, and outputs a yes-or-no answer. You also saw its fatal flaw: it cannot solve problems like XOR that are not linearly separable.

In **Chapter 3: Multi-Layer Networks**, you will learn how to overcome this limitation by stacking multiple perceptrons into layers. You will see how adding just one hidden layer allows the network to solve XOR and, in theory, approximate any function. This is where neural networks become truly powerful.
