# Chapter 3: Multi-Layer Networks — Breaking Through the Perceptron's Limits

## What You Will Learn

In this chapter, you will learn:

- Why adding hidden layers solves problems that a single perceptron cannot
- What input layers, hidden layers, and output layers do
- How forward propagation works, step by step, with actual numbers
- How each layer transforms the data into something more useful
- What the universal approximation theorem says (in plain English)
- How to build a multi-layer network from scratch in Python
- How to solve the XOR problem that defeated the single perceptron

## Why This Chapter Matters

In Chapter 2, you hit a wall. The single perceptron could not solve XOR. That same wall blocks almost every real-world problem. Recognizing a handwritten digit, detecting spam email, predicting stock trends — none of these can be solved by drawing a single straight line through the data.

Multi-layer networks tear down that wall. By stacking layers of neurons, networks can learn curves, spirals, and any shape of decision boundary. This is the architecture that makes deep learning work. Every modern neural network, from image classifiers to language models, is a multi-layer network at its core.

Understanding how data flows through layers is essential. Without it, the rest of this book will not make sense. This chapter gives you that understanding through hands-on computation with real numbers.

---

## The Problem: One Line Is Not Enough

Let us revisit why the perceptron fails on XOR. Remember: a single perceptron draws one straight line to separate two classes.

```
    XOR Cannot Be Separated by One Line
    =====================================

    Input 2
    1.0 |  (0,1)         (1,1)
        |   [1]           [0]
        |
    0.5 |     No single line works!
        |
        |
    0.0 | (0,0)         (1,0)
        |   [0]           [1]
        +---+-----+-----+----> Input 1
           0.0   0.5   1.0
```

But what if we could use TWO lines?

```
    XOR CAN Be Separated by Two Lines
    ====================================

    Input 2
    1.0 |  (0,1)    |    (1,1)
        |   [1]     |     [0]
        |           |   /
    0.5 |     Line 1|  / Line 2
        |           | /
        |           |/
    0.0 | (0,0)   / |   (1,0)
        |   [0]  /  |    [1]
        +---+--/----+---------> Input 1

    Between the two lines = class 1
    Outside the two lines = class 0
```

Two lines create a region in the middle where the output is 1. This is exactly what a hidden layer does: it gives us multiple lines, and then the output layer combines them.

---

## The Solution: Add a Hidden Layer

A multi-layer network has three types of layers:

1. **Input layer:** Receives the raw data. It does no computation. It just passes the data forward.
2. **Hidden layer(s):** One or more layers between input and output. Each neuron in a hidden layer draws its own line. The hidden layer finds patterns in the data.
3. **Output layer:** Combines the patterns from the hidden layer to make a final decision.

```
    A Multi-Layer Network
    ======================

    INPUT LAYER        HIDDEN LAYER        OUTPUT LAYER
    (receives data)    (finds patterns)    (makes decision)

        x1 ---------> [ h1 ] -------\
                  \  /                 \
                   \/                   --> [ output ]
                   /\                 /
                  /  \               /
        x2 ---------> [ h2 ] ------/

    x1, x2 = inputs (raw data)
    h1, h2 = hidden neurons (each finds a pattern)
    output = final answer

    Every input connects to every hidden neuron.
    Every hidden neuron connects to the output.
    Each connection has its own weight.
```

### Why Is It Called "Hidden"?

The hidden layer is called "hidden" because you do not directly see its inputs or outputs from the outside. You feed data into the input layer, and you read the answer from the output layer. The hidden layer is an internal processing step. It is like the engine of a car: you see the steering wheel (input) and the movement of the car (output), but the engine (hidden layer) does the real work inside where you cannot see it.

---

## How Data Flows Through the Network: Forward Propagation

**Forward propagation** (also called a **forward pass**) is the process of pushing data through the network from input to output, layer by layer. Let us walk through it step by step with actual numbers.

### Setting Up the Network

We will build a network to solve XOR:
- 2 input neurons
- 2 hidden neurons
- 1 output neuron

```
    Our XOR Network
    ================

    Weights from Input to Hidden:        Weights from Hidden to Output:

        x1 --[w11]--> h1                     h1 --[v1]--> output
        x1 --[w12]--> h2                     h2 --[v2]--> output
        x2 --[w21]--> h1
        x2 --[w22]--> h2                     bias_output = bo

        bias_h1 = b1
        bias_h2 = b2

    Naming convention:
    - w11 = weight from input 1 to hidden neuron 1
    - w12 = weight from input 1 to hidden neuron 2
    - v1  = weight from hidden neuron 1 to output
    - b1  = bias for hidden neuron 1
    - bo  = bias for output neuron
```

Let us use specific weights that solve XOR (we will choose them carefully so you can follow the math):

```
    Chosen Weights and Biases
    ==========================

    Input to Hidden:
    w11 =  1.0    (input 1 to hidden 1)
    w21 =  1.0    (input 2 to hidden 1)
    b1  = -0.5    (bias for hidden 1)

    w12 =  1.0    (input 1 to hidden 2)
    w22 =  1.0    (input 2 to hidden 2)
    b2  = -1.5    (bias for hidden 2)

    Hidden to Output:
    v1 =  1.0     (hidden 1 to output)
    v2 = -2.0     (hidden 2 to output)
    bo = -0.5     (bias for output)
```

### Forward Pass for Input [0, 0] (Expected Output: 0)

Let us trace the computation step by step.

**Step 1: Hidden Layer Computation**

Hidden neuron 1:
```
    z_h1 = (x1 * w11) + (x2 * w21) + b1
         = (0 * 1.0) + (0 * 1.0) + (-0.5)
         = 0 + 0 - 0.5
         = -0.5

    Apply step function: -0.5 < 0, so h1 = 0
```

Hidden neuron 2:
```
    z_h2 = (x1 * w12) + (x2 * w22) + b2
         = (0 * 1.0) + (0 * 1.0) + (-1.5)
         = 0 + 0 - 1.5
         = -1.5

    Apply step function: -1.5 < 0, so h2 = 0
```

**Step 2: Output Layer Computation**

```
    z_out = (h1 * v1) + (h2 * v2) + bo
          = (0 * 1.0) + (0 * -2.0) + (-0.5)
          = 0 + 0 - 0.5
          = -0.5

    Apply step function: -0.5 < 0, so output = 0
```

**Result: Input [0, 0] gives output 0. Correct!**

### Forward Pass for Input [0, 1] (Expected Output: 1)

**Step 1: Hidden Layer**

```
    h1: z = (0 * 1.0) + (1 * 1.0) + (-0.5) = 0.5    >= 0 --> h1 = 1
    h2: z = (0 * 1.0) + (1 * 1.0) + (-1.5) = -0.5   < 0  --> h2 = 0
```

**Step 2: Output Layer**

```
    z_out = (1 * 1.0) + (0 * -2.0) + (-0.5) = 0.5   >= 0 --> output = 1
```

**Result: Input [0, 1] gives output 1. Correct!**

### Forward Pass for Input [1, 0] (Expected Output: 1)

**Step 1: Hidden Layer**

```
    h1: z = (1 * 1.0) + (0 * 1.0) + (-0.5) = 0.5    >= 0 --> h1 = 1
    h2: z = (1 * 1.0) + (0 * 1.0) + (-1.5) = -0.5   < 0  --> h2 = 0
```

**Step 2: Output Layer**

```
    z_out = (1 * 1.0) + (0 * -2.0) + (-0.5) = 0.5   >= 0 --> output = 1
```

**Result: Input [1, 0] gives output 1. Correct!**

### Forward Pass for Input [1, 1] (Expected Output: 0)

**Step 1: Hidden Layer**

```
    h1: z = (1 * 1.0) + (1 * 1.0) + (-0.5) = 1.5    >= 0 --> h1 = 1
    h2: z = (1 * 1.0) + (1 * 1.0) + (-1.5) = 0.5    >= 0 --> h2 = 1
```

**Step 2: Output Layer**

```
    z_out = (1 * 1.0) + (1 * -2.0) + (-0.5) = -1.5  < 0  --> output = 0
```

**Result: Input [1, 1] gives output 0. Correct!**

### Summary of All XOR Results

```
    XOR Results with Our Multi-Layer Network
    ==========================================

    Input    h1    h2    Output    Expected    Match?
    -----    --    --    ------    --------    ------
    [0,0]     0     0       0         0        Yes!
    [0,1]     1     0       1         1        Yes!
    [1,0]     1     0       1         1        Yes!
    [1,1]     1     1       0         0        Yes!

    All four cases are correct! XOR is solved!
```

---

## What Each Layer Does

Let us understand what just happened by looking at what each layer does.

### The Hidden Layer: Feature Extraction

Each hidden neuron computes a different "question" about the input.

**Hidden neuron 1** asks: "Is at least one input active?" (it acts like an OR gate with a threshold of 0.5)

**Hidden neuron 2** asks: "Are BOTH inputs active?" (it acts like an AND gate with a threshold of 1.5)

```
    What the Hidden Neurons Compute
    =================================

    Hidden Neuron 1 (OR-like):        Hidden Neuron 2 (AND-like):

    Input    h1 output                Input    h2 output
    -----    ---------                -----    ---------
    [0,0]       0                     [0,0]       0
    [0,1]       1                     [0,1]       0
    [1,0]       1                     [1,0]       0
    [1,1]       1                     [1,1]       1
```

### The Output Layer: Combining Features

The output neuron combines the answers from the hidden layer:
- Take h1 (OR result) with weight +1
- Take h2 (AND result) with weight -2
- Add bias -0.5

This effectively computes: "OR is true AND both-on is NOT true" which is exactly XOR.

```
    How the Output Combines Hidden Outputs
    ========================================

    h1 (OR)    h2 (AND)    Weighted Sum                Output
    -------    --------    -------------------------    ------
       0          0        (0*1) + (0*-2) + (-0.5) = -0.5 --> 0
       1          0        (1*1) + (0*-2) + (-0.5) =  0.5 --> 1
       1          0        (1*1) + (0*-2) + (-0.5) =  0.5 --> 1
       1          1        (1*1) + (1*-2) + (-0.5) = -1.5 --> 0

    The output neuron has learned:
    "If OR is true but AND is false, then XOR is true"
```

### The Big Picture: Data Transformation

Each layer transforms the data. The original data (the XOR inputs) is not linearly separable. But after the hidden layer transforms it, the data BECOMES linearly separable.

```
    Data Transformation Through Layers
    ====================================

    BEFORE Hidden Layer              AFTER Hidden Layer
    (Input Space)                    (Hidden Space)

    x2                               h2
    1 |  [1]      [0]               1 |           [0]
      |                               |           (1,1)
      |                               |
    0 |  [0]      [1]               0 |  [0]      [1]
      +---------> x1                  |  (0,0)    (1,0)
      0           1                   +---------> h1
                                      0           1

    In input space:                  In hidden space:
    XOR is NOT linearly              The data IS linearly
    separable. No single             separable! A single
    line works.                      line can separate [1]
                                     from [0].

    The hidden layer TRANSFORMED the data into a space
    where it CAN be separated by a single line!
```

This is the fundamental power of multi-layer networks. Each layer transforms the data, making it easier for the next layer to work with. By the time data reaches the output layer, the problem has been transformed from something hard into something easy.

---

## Building a Multi-Layer Network in Python

Let us implement this step by step in pure Python.

```python
class MultiLayerNetwork:
    """A neural network with one hidden layer."""

    def __init__(self):
        """
        Create a network for XOR with pre-set weights.
        Architecture: 2 inputs -> 2 hidden -> 1 output
        """
        # Weights from input layer to hidden layer
        # weights_ih[i][j] = weight from input i to hidden neuron j
        self.weights_ih = [
            [1.0, 1.0],   # From input 1 to [hidden 1, hidden 2]
            [1.0, 1.0],   # From input 2 to [hidden 1, hidden 2]
        ]

        # Biases for hidden neurons
        self.biases_h = [-0.5, -1.5]

        # Weights from hidden layer to output layer
        self.weights_ho = [1.0, -2.0]  # From [hidden 1, hidden 2] to output

        # Bias for output neuron
        self.bias_o = -0.5

    def step_function(self, value):
        """Step function: returns 1 if value >= 0, else 0."""
        return 1 if value >= 0 else 0

    def forward(self, inputs, verbose=False):
        """
        Perform forward propagation.
        Push data through the network from input to output.

        Parameters:
            inputs: List of 2 input values
            verbose: If True, print each computation step

        Returns:
            The output (0 or 1)
        """
        if verbose:
            print(f"\n  Input: {inputs}")

        # ---- Hidden Layer ----
        hidden_outputs = []
        for j in range(2):  # For each hidden neuron
            # Calculate weighted sum
            z = 0.0
            for i in range(2):  # For each input
                z += inputs[i] * self.weights_ih[i][j]
            z += self.biases_h[j]

            # Apply step function
            h = self.step_function(z)
            hidden_outputs.append(h)

            if verbose:
                print(f"  Hidden neuron {j+1}: z = {z:.1f} -> output = {h}")

        # ---- Output Layer ----
        z_out = 0.0
        for j in range(2):  # For each hidden output
            z_out += hidden_outputs[j] * self.weights_ho[j]
        z_out += self.bias_o

        output = self.step_function(z_out)

        if verbose:
            print(f"  Output neuron: z = {z_out:.1f} -> output = {output}")

        return output


# Create the network
network = MultiLayerNetwork()

# Test on all XOR inputs
print("=== Multi-Layer Network Solving XOR ===\n")

xor_data = [[0, 0], [0, 1], [1, 0], [1, 1]]
xor_labels = [0, 1, 1, 0]

for inputs, expected in zip(xor_data, xor_labels):
    result = network.forward(inputs, verbose=True)
    status = "Correct!" if result == expected else "WRONG"
    print(f"  Result: {result}, Expected: {expected} --> {status}")
```

**Output:**

```
=== Multi-Layer Network Solving XOR ===

  Input: [0, 0]
  Hidden neuron 1: z = -0.5 -> output = 0
  Hidden neuron 2: z = -1.5 -> output = 0
  Output neuron: z = -0.5 -> output = 0
  Result: 0, Expected: 0 --> Correct!

  Input: [0, 1]
  Hidden neuron 1: z = 0.5 -> output = 1
  Hidden neuron 2: z = -0.5 -> output = 0
  Output neuron: z = 0.5 -> output = 1
  Result: 1, Expected: 1 --> Correct!

  Input: [1, 0]
  Hidden neuron 1: z = 0.5 -> output = 1
  Hidden neuron 2: z = -0.5 -> output = 0
  Output neuron: z = 0.5 -> output = 1
  Result: 1, Expected: 1 --> Correct!

  Input: [1, 1]
  Hidden neuron 1: z = 1.5 -> output = 1
  Hidden neuron 2: z = 0.5 -> output = 1
  Output neuron: z = -1.5 -> output = 0
  Result: 0, Expected: 0 --> Correct!
```

All four XOR cases are correct. The multi-layer network succeeded where the single perceptron failed.

---

## A Larger Network: More Layers, More Power

Real neural networks have many more layers and neurons. Here is what a slightly larger network looks like:

```
    A Network with Two Hidden Layers
    ==================================

    INPUT          HIDDEN 1         HIDDEN 2         OUTPUT
    LAYER          LAYER            LAYER            LAYER
    (3 neurons)    (4 neurons)      (4 neurons)      (2 neurons)

     [x1] ------> [h1_1] -------> [h2_1] -------> [o1]
       \   \  /    [h1_2]    /  \   [h2_2]    /  \  [o2]
        \   \/      [h1_3]  /    \   [h2_3]  /
         \  /\      [h1_4] /      \  [h2_4] /
     [x2] -------> connects       connects
       \    to every neuron    to every neuron
        \   in next layer      in next layer
     [x3] -->

    Total connections:
    Layer 1 to 2: 3 x 4 = 12 weights + 4 biases = 16 parameters
    Layer 2 to 3: 4 x 4 = 16 weights + 4 biases = 20 parameters
    Layer 3 to 4: 4 x 2 = 8 weights + 2 biases  = 10 parameters
                                                    ----
    Total:                                          46 parameters

    Each "parameter" is a number the network learns during training.
```

### How Each Layer Builds on the Previous One

Think of layers like an assembly line in a factory:

```
    The Assembly Line Analogy
    ==========================

    Raw             Worker         Worker          Worker         Finished
    Materials  -->  Team 1    -->  Team 2    -->   Team 3    -->  Product
    (Input)         (Hidden 1)     (Hidden 2)      (Output)

    Example: Image Recognition

    Pixels     -->  Find edges --> Find shapes --> Classify  -->  "It's a cat"
                    and colors     (ears, eyes,
                                   whiskers)

    Each layer finds more complex patterns by building on
    the simpler patterns found by the previous layer.
```

Layer 1 might find simple things like edges and color patches. Layer 2 combines those edges into shapes like ears or eyes. Layer 3 combines those shapes to recognize the whole object. Each layer builds on what the previous layer found.

---

## Forward Propagation: The General Algorithm

Now that you have seen forward propagation with specific numbers, let us write the general algorithm. This works for any number of layers and any number of neurons per layer.

```
    Forward Propagation Algorithm
    ==============================

    For each layer (from input to output):
        For each neuron in the current layer:
            1. Multiply each input by its weight
            2. Add all the products together
            3. Add the bias
            4. Apply the activation function
            5. This output becomes input for the next layer

    That is it. Just repeat for each layer.
```

### Implementation for Any Architecture

```python
class FlexibleNetwork:
    """A neural network that can have any number of layers."""

    def __init__(self, layer_sizes):
        """
        Create a network with specified architecture.

        Parameters:
            layer_sizes: List of integers, e.g., [2, 3, 1]
                         means 2 inputs, 3 hidden, 1 output
        """
        self.layer_sizes = layer_sizes
        self.num_layers = len(layer_sizes)

        # Initialize weights and biases for each layer connection
        self.weights = []  # weights[l][i][j] = weight from neuron i in layer l to neuron j in layer l+1
        self.biases = []   # biases[l][j] = bias for neuron j in layer l+1

        for l in range(self.num_layers - 1):
            # Create weight matrix for this layer connection
            layer_weights = []
            for i in range(layer_sizes[l]):
                neuron_weights = [0.0] * layer_sizes[l + 1]
                layer_weights.append(neuron_weights)
            self.weights.append(layer_weights)

            # Create bias vector for next layer
            layer_biases = [0.0] * layer_sizes[l + 1]
            self.biases.append(layer_biases)

    def step_function(self, value):
        """Step activation function."""
        return 1 if value >= 0 else 0

    def forward(self, inputs):
        """
        Push data through the entire network.
        Returns the output of each layer (useful for understanding).
        """
        current_values = list(inputs)  # Start with the input values
        all_layer_outputs = [current_values]  # Store outputs of each layer

        # Process each layer
        for l in range(self.num_layers - 1):
            next_values = []

            # For each neuron in the next layer
            for j in range(self.layer_sizes[l + 1]):
                # Calculate weighted sum
                z = 0.0
                for i in range(len(current_values)):
                    z += current_values[i] * self.weights[l][i][j]
                z += self.biases[l][j]

                # Apply activation
                output = self.step_function(z)
                next_values.append(output)

            current_values = next_values
            all_layer_outputs.append(current_values)

        return current_values, all_layer_outputs

    def set_weights(self, layer_index, weights_matrix, biases_vector):
        """Manually set weights and biases for a layer connection."""
        self.weights[layer_index] = weights_matrix
        self.biases[layer_index] = biases_vector


# Build XOR network using the flexible class
network = FlexibleNetwork([2, 2, 1])

# Set weights for input->hidden
network.set_weights(0,
    weights_matrix=[[1.0, 1.0],    # From input 1 to [hidden 1, hidden 2]
                    [1.0, 1.0]],   # From input 2 to [hidden 1, hidden 2]
    biases_vector=[-0.5, -1.5]
)

# Set weights for hidden->output
network.set_weights(1,
    weights_matrix=[[1.0],     # From hidden 1 to output
                    [-2.0]],   # From hidden 2 to output
    biases_vector=[-0.5]
)

# Test XOR
print("=== Flexible Network Solving XOR ===\n")
print(f"Architecture: {network.layer_sizes}")
print(f"Number of layers: {network.num_layers}\n")

xor_data = [[0, 0], [0, 1], [1, 0], [1, 1]]
xor_labels = [0, 1, 1, 0]

for inputs, expected in zip(xor_data, xor_labels):
    output, all_layers = network.forward(inputs)
    result = output[0]
    status = "Correct!" if result == expected else "WRONG"
    print(f"Input: {inputs}")
    print(f"  Layer outputs: {all_layers}")
    print(f"  Final: {result}, Expected: {expected} --> {status}\n")
```

**Output:**

```
=== Flexible Network Solving XOR ===

Architecture: [2, 2, 1]
Number of layers: 3

Input: [0, 0]
  Layer outputs: [[0, 0], [0, 0], [0]]
  Final: 0, Expected: 0 --> Correct!

Input: [0, 1]
  Layer outputs: [[0, 1], [1, 0], [1]]
  Final: 1, Expected: 1 --> Correct!

Input: [1, 0]
  Layer outputs: [[1, 0], [1, 0], [1]]
  Final: 1, Expected: 1 --> Correct!

Input: [1, 1]
  Layer outputs: [[1, 1], [1, 1], [0]]
  Final: 0, Expected: 0 --> Correct!
```

---

## Counting Parameters: How Big Is My Network?

A **parameter** is any number that the network learns during training. This includes all weights and all biases. The total number of parameters tells you how "big" or "complex" a network is.

```
    Counting Parameters
    ====================

    For a network with layers [2, 3, 1]:

    Connection 1: Input (2) -> Hidden (3)
        Weights: 2 x 3 = 6
        Biases:  3
        Subtotal: 9

    Connection 2: Hidden (3) -> Output (1)
        Weights: 3 x 1 = 3
        Biases:  1
        Subtotal: 4

    Total parameters: 9 + 4 = 13

    General formula for one connection:
    parameters = (neurons_in * neurons_out) + neurons_out
               = neurons_out * (neurons_in + 1)

    The "+1" is for the biases.
```

Let us write code to count parameters:

```python
def count_parameters(layer_sizes):
    """Count total trainable parameters in a network."""
    total = 0
    for i in range(len(layer_sizes) - 1):
        weights = layer_sizes[i] * layer_sizes[i + 1]
        biases = layer_sizes[i + 1]
        connection_params = weights + biases
        print(f"  Layer {i+1} -> Layer {i+2}: "
              f"{layer_sizes[i]} x {layer_sizes[i+1]} weights + "
              f"{layer_sizes[i+1]} biases = {connection_params}")
        total += connection_params
    print(f"  Total parameters: {total}")
    return total

print("=== Parameter Counts ===\n")

print("XOR network [2, 2, 1]:")
count_parameters([2, 2, 1])

print("\nSmall network [3, 4, 4, 2]:")
count_parameters([3, 4, 4, 2])

print("\nMedium network [784, 128, 64, 10]:")
count_parameters([784, 128, 64, 10])
```

**Output:**

```
=== Parameter Counts ===

XOR network [2, 2, 1]:
  Layer 1 -> Layer 2: 2 x 2 weights + 2 biases = 6
  Layer 2 -> Layer 3: 2 x 1 weights + 1 biases = 3
  Total parameters: 9

Small network [3, 4, 4, 2]:
  Layer 1 -> Layer 2: 3 x 4 weights + 4 biases = 16
  Layer 2 -> Layer 3: 4 x 4 weights + 4 biases = 20
  Layer 3 -> Layer 4: 4 x 2 weights + 2 biases = 10
  Total parameters: 46

Medium network [784, 128, 64, 10]:
  Layer 1 -> Layer 2: 784 x 128 weights + 128 biases = 100480
  Layer 2 -> Layer 3: 128 x 64 weights + 64 biases = 8256
  Layer 3 -> Layer 4: 64 x 10 weights + 10 biases = 650
  Total parameters: 109386
```

Notice that the medium network (which could classify handwritten digits) has over 100,000 parameters. Modern deep learning models have billions of parameters. That is why we need GPUs and frameworks like PyTorch.

---

## The Universal Approximation Theorem (Simplified)

There is a famous mathematical result called the **Universal Approximation Theorem**. In plain English, it says:

> A neural network with just one hidden layer (and enough neurons in that layer) can learn to approximate any continuous function to any desired level of accuracy.

What does this mean? It means that in theory, a single hidden layer is enough to solve any problem, as long as you have enough neurons in it. Whether you want to recognize images, translate languages, or predict the weather — a network with one big hidden layer could, in theory, do it.

```
    Universal Approximation Theorem (Simplified)
    ================================================

    ANY function (any input-output mapping) can be
    approximated by a network like this:

    Input -->  [very large hidden layer] --> Output
               (with enough neurons)

    Example: Learning a complex curve

    y
    5 |        **
    4 |      **  **
    3 |    **      **
    2 |  **          **
    1 | *              **
    0 |*                 ***
      +-----------------------> x

    A network with enough hidden neurons can learn this shape.
    Each hidden neuron contributes one "bump" or "step" to the
    overall shape. More neurons = more detail.
```

### The Catch

However, just because it is theoretically possible does not mean it is practical. A single hidden layer might need millions of neurons to solve a complex problem. In practice, it is much more efficient to use multiple smaller layers (deep networks) rather than one enormous layer. This is why "deep" learning uses many layers.

```
    One Wide Layer vs. Many Narrow Layers
    ========================================

    Wide and Shallow:                Deep and Narrow:
    (works in theory,               (works in practice,
     but needs MANY neurons)         much more efficient)

    Input -> [1000 neurons] -> Out   Input -> [10] -> [10] -> [10] -> Out

    The deep network can reuse        Each layer builds on the previous
    patterns across layers.           one, so fewer total neurons needed.
```

---

## Putting It All Together: XOR with Traced Computation

Let us create one final, clear visualization of the entire XOR computation.

```python
def solve_xor_verbose():
    """Solve XOR and show every computation step."""

    # Network weights (hand-chosen to solve XOR)
    # Input -> Hidden
    w_ih = [[1.0, 1.0],   # input 1 weights to [h1, h2]
            [1.0, 1.0]]   # input 2 weights to [h1, h2]
    b_h = [-0.5, -1.5]    # hidden biases

    # Hidden -> Output
    w_ho = [1.0, -2.0]    # hidden weights to output
    b_o = -0.5            # output bias

    test_cases = [
        ([0, 0], 0),
        ([0, 1], 1),
        ([1, 0], 1),
        ([1, 1], 0),
    ]

    print("=== Complete XOR Forward Propagation ===")
    print("=" * 50)

    for inputs, expected in test_cases:
        print(f"\nInput: x1={inputs[0]}, x2={inputs[1]}")
        print("-" * 40)

        # Hidden layer
        print("Hidden Layer:")
        h = []
        for j in range(2):
            z = inputs[0] * w_ih[0][j] + inputs[1] * w_ih[1][j] + b_h[j]
            activated = 1 if z >= 0 else 0
            h.append(activated)
            print(f"  h{j+1}: ({inputs[0]}*{w_ih[0][j]}) + "
                  f"({inputs[1]}*{w_ih[1][j]}) + ({b_h[j]}) "
                  f"= {z:.1f} --> step --> {activated}")

        # Output layer
        z_out = h[0] * w_ho[0] + h[1] * w_ho[1] + b_o
        output = 1 if z_out >= 0 else 0
        print("Output Layer:")
        print(f"  out: ({h[0]}*{w_ho[0]}) + ({h[1]}*{w_ho[1]}) + ({b_o}) "
              f"= {z_out:.1f} --> step --> {output}")

        status = "CORRECT" if output == expected else "WRONG"
        print(f"  Result: {output}  Expected: {expected}  [{status}]")

    print("\n" + "=" * 50)
    print("XOR solved with a 2-layer network!")

solve_xor_verbose()
```

**Output:**

```
=== Complete XOR Forward Propagation ===
==================================================

Input: x1=0, x2=0
----------------------------------------
Hidden Layer:
  h1: (0*1.0) + (0*1.0) + (-0.5) = -0.5 --> step --> 0
  h2: (0*1.0) + (0*1.0) + (-1.5) = -1.5 --> step --> 0
Output Layer:
  out: (0*1.0) + (0*-2.0) + (-0.5) = -0.5 --> step --> 0
  Result: 0  Expected: 0  [CORRECT]

Input: x1=0, x2=1
----------------------------------------
Hidden Layer:
  h1: (0*1.0) + (1*1.0) + (-0.5) = 0.5 --> step --> 1
  h2: (0*1.0) + (1*1.0) + (-1.5) = -0.5 --> step --> 0
Output Layer:
  out: (1*1.0) + (0*-2.0) + (-0.5) = 0.5 --> step --> 1
  Result: 1  Expected: 1  [CORRECT]

Input: x1=1, x2=0
----------------------------------------
Hidden Layer:
  h1: (1*1.0) + (0*1.0) + (-0.5) = 0.5 --> step --> 1
  h2: (1*1.0) + (0*1.0) + (-1.5) = -0.5 --> step --> 0
Output Layer:
  out: (1*1.0) + (0*-2.0) + (-0.5) = 0.5 --> step --> 1
  Result: 1  Expected: 1  [CORRECT]

Input: x1=1, x2=1
----------------------------------------
Hidden Layer:
  h1: (1*1.0) + (1*1.0) + (-0.5) = 1.5 --> step --> 1
  h2: (1*1.0) + (1*1.0) + (-1.5) = 0.5 --> step --> 1
Output Layer:
  out: (1*1.0) + (1*-2.0) + (-0.5) = -1.5 --> step --> 0
  Result: 0  Expected: 0  [CORRECT]

==================================================
XOR solved with a 2-layer network!
```

---

## Common Mistakes

1. **Confusing the input layer with a computational layer.** The input layer does NO computation. It simply passes data forward. When people say "a 3-layer network," they usually mean 1 input layer + 1 hidden layer + 1 output layer. The input layer does not count as a "real" layer in some conventions, which causes confusion.

2. **Thinking more layers always means better performance.** Adding layers increases the network's capacity, but it also makes training harder. With step functions, you cannot even train a multi-layer network using the simple perceptron learning rule. You need backpropagation (Chapter 6) and smooth activation functions (Chapter 4).

3. **Forgetting biases.** Every neuron (except input neurons) needs a bias. Forgetting biases limits the network's ability to shift its decision boundaries.

4. **Mixing up weight indices.** With multiple layers, keeping track of which weight connects which neurons is tricky. Use clear naming conventions: `weights_ih` (input to hidden), `weights_ho` (hidden to output).

5. **Assuming the network will find the right weights automatically.** In this chapter, we hand-picked the weights. In reality, networks learn weights through backpropagation (Chapter 6). The hand-picked approach only works for tiny examples.

---

## Best Practices

1. **Start with a simple architecture.** Begin with one hidden layer. Add more layers only if the simple network cannot solve the problem.

2. **Count your parameters.** Know how many trainable parameters your network has. Too many parameters with too little data leads to overfitting (memorizing the training data instead of learning patterns).

3. **Draw your network before coding.** Sketch the architecture on paper: how many layers, how many neurons per layer, how they connect. This prevents confusion during implementation.

4. **Verify with known examples.** Before training on real data, test your network on simple problems like XOR where you know the correct answer. This catches bugs early.

5. **Use clear variable names.** Name your weight matrices to show which layers they connect: `weights_input_hidden`, `weights_hidden_output`. This makes debugging much easier.

---

## Quick Summary

A multi-layer network overcomes the perceptron's limitation by stacking layers of neurons. The hidden layer transforms the data so that it becomes linearly separable, allowing the output layer to make the final decision. Forward propagation pushes data through the network one layer at a time: compute weighted sum, add bias, apply activation function, pass output to next layer.

The universal approximation theorem tells us that a single hidden layer with enough neurons can approximate any function. In practice, deeper networks (more layers with fewer neurons each) are more efficient. This is why modern deep learning uses many layers, giving us "deep" networks.

---

## Key Points

- Multi-layer networks solve problems that single perceptrons cannot (like XOR)
- The input layer passes raw data, hidden layers find patterns, the output layer decides
- Forward propagation moves data through the network layer by layer
- Each neuron computes: weighted sum + bias, then applies an activation function
- Hidden layers transform data into a representation where the problem is easier to solve
- The universal approximation theorem says one hidden layer with enough neurons can approximate any function
- In practice, deep networks (many layers) are more efficient than wide networks (one huge layer)
- The number of parameters = sum of (weights + biases) across all layer connections

---

## Practice Questions

1. A network has architecture [3, 4, 2]. How many total parameters (weights + biases) does it have? Show your work.

2. Why is the hidden layer called "hidden"? What makes it different from the input and output layers?

3. In our XOR network, hidden neuron 1 acts like an OR gate and hidden neuron 2 acts like an AND gate. How does the output neuron combine them to produce XOR? Explain with the weights.

4. If a single hidden layer can approximate any function (universal approximation theorem), why do we use deep networks with many layers in practice?

5. Trace the forward propagation for input [1, 0] through a network with these weights: input-to-hidden weights = [[0.5, -0.5], [0.3, 0.7]], hidden biases = [-0.2, 0.1], hidden-to-output weights = [0.8, -0.6], output bias = -0.1. Use the step function.

---

## Exercises

### Exercise 1: Three-Input XOR

Design a multi-layer network (on paper or in code) that computes three-input XOR. Three-input XOR outputs 1 when an odd number of inputs are 1. The truth table has 8 rows. Hint: you might need more hidden neurons.

### Exercise 2: Parameter Calculator

Write a function that takes a list of layer sizes (like [784, 256, 128, 10]) and prints a detailed breakdown of parameters per layer and the total. Test it with at least three different architectures.

### Exercise 3: Trace Forward Propagation

Create a network with architecture [2, 3, 2] (2 inputs, 3 hidden, 2 outputs). Choose your own weights and biases. Trace the forward propagation for three different inputs. Show every calculation step. Verify your code matches your hand calculations.

---

## What Is Next?

In this chapter, you learned how multi-layer networks solve problems that a single perceptron cannot. You traced forward propagation step by step and saw how hidden layers transform data.

But we used the step function as our activation, which only outputs 0 or 1. This hard yes-or-no decision has a critical problem: it is not smooth enough for the network to learn from. Modern networks need smoother activation functions.

In **Chapter 4: Activation Functions**, you will explore the activation functions that make modern deep learning possible: sigmoid, tanh, ReLU, and more. You will learn why each exists, when to use them, and what happens when you choose the wrong one.
