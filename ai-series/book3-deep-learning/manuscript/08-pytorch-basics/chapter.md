# Chapter 8: PyTorch Basics

## What You Will Learn

In this chapter, you will learn:

- What PyTorch is and why it is the most popular deep learning framework
- How to install PyTorch on your computer
- What tensors are (like NumPy arrays, but with superpowers)
- How to create tensors from scratch, from lists, and from NumPy arrays
- Essential tensor operations: add, multiply, reshape, transpose, and more
- How to move tensors to a GPU for faster computation
- What autograd is and how it computes gradients automatically
- How requires_grad=True tells PyTorch to track operations
- How to compute gradients with the .backward() method
- What the computational graph looks like inside PyTorch

## Why This Chapter Matters

In the previous chapters, you learned the theory behind neural networks: forward passes, loss functions, backpropagation, and optimizers. You implemented everything by hand in plain Python. That was important for understanding HOW things work.

But nobody builds real neural networks by hand. Real networks have millions of weights. Computing gradients by hand for millions of weights is impossible. Running computations on a CPU is too slow. You need a framework.

**PyTorch** is that framework. It is like upgrading from a hand calculator to a supercomputer. PyTorch handles three critical tasks for you:

1. **Tensor operations** that run on GPUs (hundreds of times faster than CPU)
2. **Automatic differentiation** that computes all gradients for you (no more manual chain rule)
3. **Building blocks** for layers, losses, and optimizers (ready to use)

PyTorch was created by Facebook (now Meta) and is used by researchers at OpenAI, Tesla, Google, and nearly every AI lab in the world. If you learn PyTorch, you can build anything from simple classifiers to large language models.

This chapter is the bridge between understanding the theory and building real networks.

---

## 8.1 What Is PyTorch?

### PyTorch in One Sentence

PyTorch is an open-source Python library for building, training, and deploying deep learning models.

```
What PyTorch Gives You
=========================

1. TENSORS
   Multi-dimensional arrays (like NumPy) that can run on GPUs.
   A GPU can do math 10-100x faster than a CPU.

2. AUTOGRAD (Automatic Gradients)
   You write the forward pass. PyTorch computes the backward
   pass AUTOMATICALLY. No manual chain rule needed.

3. NEURAL NETWORK BUILDING BLOCKS
   Pre-built layers (Linear, Conv2d, LSTM, Transformer...)
   Pre-built loss functions (MSE, CrossEntropy, ...)
   Pre-built optimizers (SGD, Adam, AdamW, ...)

4. DATA LOADING
   Tools to load, batch, and shuffle your training data.

5. GPU SUPPORT
   One line of code moves your computation to the GPU.
```

### PyTorch vs. NumPy

```
NumPy vs. PyTorch: A Comparison
===================================

Feature           | NumPy          | PyTorch
------------------|----------------|------------------
Array type        | ndarray        | Tensor
GPU support       | No             | Yes
Auto gradients    | No             | Yes (autograd)
Neural net layers | No             | Yes (nn.Module)
Speed on GPU      | CPU only       | 10-100x faster
Syntax            | np.array(...)  | torch.tensor(...)
Interoperability  | -              | Easy conversion

Key point: PyTorch tensors are like NumPy arrays
with GPU support and automatic differentiation.
```

---

## 8.2 Installing PyTorch

### Installation

The easiest way to install PyTorch depends on your setup:

```python
# Option 1: Install with pip (CPU only - simplest)
# Run this in your terminal:
# pip install torch torchvision

# Option 2: Install with pip (GPU support - NVIDIA)
# Visit https://pytorch.org for the exact command for your system.
# It will look something like:
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Option 3: Install with conda
# conda install pytorch torchvision -c pytorch
```

### Verify Your Installation

```python
import torch

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")
else:
    print("No GPU found. Using CPU (this is fine for learning).")
```

**Output (example without GPU):**

```
PyTorch version: 2.2.0
CUDA available: False
No GPU found. Using CPU (this is fine for learning).
```

**Output (example with GPU):**

```
PyTorch version: 2.2.0
CUDA available: True
GPU name: NVIDIA GeForce RTX 3080
GPU memory: 10.0 GB
```

Do not worry if you do not have a GPU. Everything in this book works on CPU. A GPU just makes training faster.

---

## 8.3 Tensors: The Foundation of PyTorch

### What Is a Tensor?

A **tensor** is a multi-dimensional array of numbers. If you know NumPy, you already know what a tensor is. It is the same concept with a different name.

```
Tensors by Dimension
=======================

0-D Tensor (Scalar): A single number
  Example: 42
  Shape: ()

1-D Tensor (Vector): A list of numbers
  Example: [1, 2, 3, 4]
  Shape: (4,)

2-D Tensor (Matrix): A table of numbers
  Example: [[1, 2, 3],
            [4, 5, 6]]
  Shape: (2, 3) = 2 rows, 3 columns

3-D Tensor: A "stack" of matrices
  Example: An RGB image: 3 color channels, each a matrix
  Shape: (3, 224, 224) = 3 channels, 224 height, 224 width

4-D Tensor: A batch of 3-D tensors
  Example: 32 images in a batch
  Shape: (32, 3, 224, 224) = 32 images, 3 channels, 224x224 pixels
```

### Creating Tensors

```python
import torch

# =============================
# Creating Tensors from Values
# =============================

# Scalar (0-D tensor)
scalar = torch.tensor(42)
print(f"Scalar: {scalar}")
print(f"Shape: {scalar.shape}")
print(f"Dimensions: {scalar.ndim}")
print()

# Vector (1-D tensor)
vector = torch.tensor([1.0, 2.0, 3.0, 4.0])
print(f"Vector: {vector}")
print(f"Shape: {vector.shape}")
print(f"Dimensions: {vector.ndim}")
print()

# Matrix (2-D tensor)
matrix = torch.tensor([[1.0, 2.0, 3.0],
                        [4.0, 5.0, 6.0]])
print(f"Matrix:\n{matrix}")
print(f"Shape: {matrix.shape}")
print(f"Dimensions: {matrix.ndim}")
print()

# 3-D Tensor
tensor_3d = torch.tensor([[[1, 2], [3, 4]],
                           [[5, 6], [7, 8]]])
print(f"3-D Tensor:\n{tensor_3d}")
print(f"Shape: {tensor_3d.shape}")
print(f"Dimensions: {tensor_3d.ndim}")
```

**Output:**

```
Scalar: 42
Shape: torch.Size([])
Dimensions: 0

Vector: tensor([1., 2., 3., 4.])
Shape: torch.Size([4])
Dimensions: 1

Matrix:
tensor([[1., 2., 3.],
        [4., 5., 6.]])
Shape: torch.Size([2, 3])
Dimensions: 2

3-D Tensor:
tensor([[[1, 2],
         [3, 4]],
        [[5, 6],
         [7, 8]]])
Shape: torch.Size([2, 2, 2])
Dimensions: 3
```

### Creating Tensors with Built-In Functions

```python
import torch

# Zeros
zeros = torch.zeros(3, 4)
print(f"Zeros (3x4):\n{zeros}\n")

# Ones
ones = torch.ones(2, 3)
print(f"Ones (2x3):\n{ones}\n")

# Random (uniform between 0 and 1)
random_uniform = torch.rand(2, 3)
print(f"Random uniform (2x3):\n{random_uniform}\n")

# Random (normal distribution, mean=0, std=1)
random_normal = torch.randn(2, 3)
print(f"Random normal (2x3):\n{random_normal}\n")

# Range of numbers
arange = torch.arange(0, 10, 2)  # start, stop, step
print(f"Arange (0 to 10, step 2): {arange}\n")

# Linearly spaced
linspace = torch.linspace(0, 1, 5)  # start, end, num_points
print(f"Linspace (0 to 1, 5 points): {linspace}\n")

# Identity matrix
eye = torch.eye(3)
print(f"Identity (3x3):\n{eye}\n")

# Full (fill with a specific value)
full = torch.full((2, 3), 7.0)
print(f"Full of 7s (2x3):\n{full}")
```

**Output:**

```
Zeros (3x4):
tensor([[0., 0., 0., 0.],
        [0., 0., 0., 0.],
        [0., 0., 0., 0.]])

Ones (2x3):
tensor([[1., 1., 1.],
        [1., 1., 1.]])

Random uniform (2x3):
tensor([[0.4963, 0.7682, 0.0885],
        [0.1320, 0.3074, 0.6341]])

Random normal (2x3):
tensor([[ 0.2783, -1.2474, -0.4175],
        [-0.8051,  1.1237, -0.0328]])

Arange (0 to 10, step 2): tensor([0, 2, 4, 6, 8])

Linspace (0 to 1, 5 points): tensor([0.0000, 0.2500, 0.5000, 0.7500, 1.0000])

Identity (3x3):
tensor([[1., 0., 0.],
        [0., 1., 0.],
        [0., 0., 1.]])

Full of 7s (2x3):
tensor([[7., 7., 7.],
        [7., 7., 7.]])
```

### Converting Between NumPy and PyTorch

```python
import torch
import numpy as np

# NumPy array to PyTorch tensor
np_array = np.array([[1, 2, 3], [4, 5, 6]])
tensor_from_np = torch.from_numpy(np_array)
print(f"NumPy array:\n{np_array}")
print(f"PyTorch tensor:\n{tensor_from_np}\n")

# PyTorch tensor to NumPy array
tensor = torch.tensor([[7.0, 8.0], [9.0, 10.0]])
np_from_tensor = tensor.numpy()
print(f"PyTorch tensor:\n{tensor}")
print(f"NumPy array:\n{np_from_tensor}\n")

# Important: they SHARE memory (changes to one affect the other)
np_array[0, 0] = 999
print(f"After changing NumPy array[0,0] to 999:")
print(f"NumPy: {np_array[0, 0]}")
print(f"Tensor: {tensor_from_np[0, 0]}")
print("They share the same memory!")
```

**Output:**

```
NumPy array:
[[1 2 3]
 [4 5 6]]
PyTorch tensor:
tensor([[1, 2, 3],
        [4, 5, 6]])

PyTorch tensor:
tensor([[ 7.,  8.],
        [ 9., 10.]])
NumPy array:
[[ 7.  8.]
 [ 9. 10.]]

After changing NumPy array[0,0] to 999:
NumPy: 999
Tensor: 999
They share the same memory!
```

### Tensor Data Types

```python
import torch

# Integer tensor (default: int64)
int_tensor = torch.tensor([1, 2, 3])
print(f"Integer tensor: {int_tensor}, dtype: {int_tensor.dtype}")

# Float tensor (default: float32)
float_tensor = torch.tensor([1.0, 2.0, 3.0])
print(f"Float tensor: {float_tensor}, dtype: {float_tensor.dtype}")

# Specify dtype explicitly
float64_tensor = torch.tensor([1.0, 2.0], dtype=torch.float64)
print(f"Float64 tensor: {float64_tensor}, dtype: {float64_tensor.dtype}")

# Convert dtype
converted = int_tensor.float()  # int -> float32
print(f"Converted: {converted}, dtype: {converted.dtype}")

# Common data types table
print(f"""
Common PyTorch Data Types
============================
torch.float32  (or torch.float)   - Standard for neural networks
torch.float64  (or torch.double)  - Higher precision (rarely needed)
torch.int32    (or torch.int)     - Integers
torch.int64    (or torch.long)    - Used for class labels
torch.bool                        - True/False values
""")
```

**Output:**

```
Integer tensor: tensor([1, 2, 3]), dtype: torch.int64
Float tensor: tensor([1., 2., 3.]), dtype: torch.float32
Float64 tensor: tensor([1., 2.], dtype=torch.float64), dtype: torch.float64
Converted: tensor([1., 2., 3.]), dtype: torch.float32

Common PyTorch Data Types
============================
torch.float32  (or torch.float)   - Standard for neural networks
torch.float64  (or torch.double)  - Higher precision (rarely needed)
torch.int32    (or torch.int)     - Integers
torch.int64    (or torch.long)    - Used for class labels
torch.bool                        - True/False values
```

---

## 8.4 Tensor Operations

### Basic Math Operations

```python
import torch

a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([4.0, 5.0, 6.0])

# Addition
print(f"a + b = {a + b}")
print(f"torch.add(a, b) = {torch.add(a, b)}")

# Subtraction
print(f"a - b = {a - b}")

# Multiplication (element-wise)
print(f"a * b = {a * b}")

# Division
print(f"a / b = {a / b}")

# Power
print(f"a ** 2 = {a ** 2}")

# Scalar operations
print(f"a + 10 = {a + 10}")
print(f"a * 3 = {a * 3}")
```

**Output:**

```
a + b = tensor([5., 7., 9.])
torch.add(a, b) = tensor([5., 7., 9.])
a - b = tensor([-3., -3., -3.])
a * b = tensor([ 4., 10., 18.])
a / b = tensor([0.2500, 0.4000, 0.5000])
a ** 2 = tensor([1., 4., 9.])
a + 10 = tensor([11., 12., 13.])
a * 3 = tensor([3., 6., 9.])
```

### Matrix Operations

```python
import torch

# Matrix multiplication
A = torch.tensor([[1.0, 2.0],
                  [3.0, 4.0]])
B = torch.tensor([[5.0, 6.0],
                  [7.0, 8.0]])

# Three ways to do matrix multiplication
result1 = A @ B                  # @ operator
result2 = torch.matmul(A, B)     # function
result3 = A.mm(B)                # method

print(f"A:\n{A}")
print(f"B:\n{B}")
print(f"A @ B:\n{result1}\n")

# Dot product (for 1-D tensors)
v1 = torch.tensor([1.0, 2.0, 3.0])
v2 = torch.tensor([4.0, 5.0, 6.0])
dot = torch.dot(v1, v2)
print(f"v1 dot v2 = {dot}")
print(f"(1*4 + 2*5 + 3*6 = {1*4 + 2*5 + 3*6})\n")

# Transpose
print(f"A transposed:\n{A.T}")
print(f"(or A.t() or A.transpose(0, 1))")
```

**Output:**

```
A:
tensor([[1., 2.],
        [3., 4.]])
B:
tensor([[5., 6.],
        [7., 8.]])
A @ B:
tensor([[19., 22.],
        [43., 50.]])

v1 dot v2 = 32.0
(1*4 + 2*5 + 3*6 = 32)

A transposed:
tensor([[1., 3.],
        [2., 4.]])
(or A.t() or A.transpose(0, 1))
```

### Reshaping Tensors

```python
import torch

# Original tensor
x = torch.arange(12)
print(f"Original: {x}")
print(f"Shape: {x.shape}\n")

# Reshape to 3x4
reshaped = x.reshape(3, 4)
print(f"Reshaped (3x4):\n{reshaped}")
print(f"Shape: {reshaped.shape}\n")

# Reshape to 2x2x3
reshaped_3d = x.reshape(2, 2, 3)
print(f"Reshaped (2x2x3):\n{reshaped_3d}")
print(f"Shape: {reshaped_3d.shape}\n")

# Use -1 to let PyTorch figure out one dimension
auto = x.reshape(4, -1)  # -1 means "figure it out" -> 4x3
print(f"Auto reshape (4, -1):\n{auto}")
print(f"Shape: {auto.shape}\n")

# view() works like reshape but shares memory
viewed = x.view(3, 4)
print(f"View (3x4):\n{viewed}")
print(f"Shape: {viewed.shape}\n")

# Flatten: convert any shape to 1-D
matrix = torch.tensor([[1, 2, 3], [4, 5, 6]])
flat = matrix.flatten()
print(f"Matrix:\n{matrix}")
print(f"Flattened: {flat}")

# Squeeze and unsqueeze
# squeeze: remove dimensions of size 1
# unsqueeze: add a dimension of size 1
t = torch.tensor([1, 2, 3])
print(f"\nOriginal shape: {t.shape}")
print(f"Unsqueeze(0) shape: {t.unsqueeze(0).shape}")  # add batch dim
print(f"Unsqueeze(1) shape: {t.unsqueeze(1).shape}")  # add column dim
```

**Output:**

```
Original: tensor([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11])
Shape: torch.Size([12])

Reshaped (3x4):
tensor([[ 0,  1,  2,  3],
        [ 4,  5,  6,  7],
        [ 8,  9, 10, 11]])
Shape: torch.Size([3, 4])

Reshaped (2x2x3):
tensor([[[ 0,  1,  2],
         [ 3,  4,  5]],
        [[ 6,  7,  8],
         [ 9, 10, 11]]])
Shape: torch.Size([2, 2, 3])

Auto reshape (4, -1):
tensor([[ 0,  1,  2],
        [ 3,  4,  5],
        [ 6,  7,  8],
        [ 9, 10, 11]])
Shape: torch.Size([4, 3])

View (3x4):
tensor([[ 0,  1,  2,  3],
        [ 4,  5,  6,  7],
        [ 8,  9, 10, 11]])
Shape: torch.Size([3, 4])

Matrix:
tensor([[1, 2, 3],
        [4, 5, 6]])
Flattened: tensor([1, 2, 3, 4, 5, 6])

Original shape: torch.Size([3])
Unsqueeze(0) shape: torch.Size([1, 3])
Unsqueeze(1) shape: torch.Size([3, 1])
```

### Aggregation Operations

```python
import torch

t = torch.tensor([[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]])

print(f"Tensor:\n{t}\n")

# Sum
print(f"Sum of all: {t.sum()}")
print(f"Sum along rows (dim=0): {t.sum(dim=0)}")
print(f"Sum along cols (dim=1): {t.sum(dim=1)}")

# Mean
print(f"\nMean of all: {t.mean()}")
print(f"Mean along rows (dim=0): {t.mean(dim=0)}")

# Max and min
print(f"\nMax: {t.max()}")
print(f"Min: {t.min()}")
print(f"Argmax (index of max): {t.argmax()}")

# Standard deviation
print(f"\nStd: {t.std():.4f}")
```

**Output:**

```
Tensor:
tensor([[1., 2., 3.],
        [4., 5., 6.]])

Sum of all: 21.0
Sum along rows (dim=0): tensor([5., 7., 9.])
Sum along cols (dim=1): tensor([ 6., 15.])

Mean of all: 3.5
Mean along rows (dim=0): tensor([2.5, 3.5, 4.5])

Max: 6.0
Min: 1.0
Argmax (index of max): 5

Std: 1.8708
```

### Understanding dim (Dimension)

```
Understanding dim=0 vs. dim=1
=================================

tensor = [[1, 2, 3],    (row 0)
          [4, 5, 6]]    (row 1)

dim=0 means "collapse the ROWS" (operate DOWN each column):
  sum(dim=0) = [1+4, 2+5, 3+6] = [5, 7, 9]

  Column 0  Column 1  Column 2
     1         2         3
   + 4       + 5       + 6
   ----      ----      ----
     5         7         9

dim=1 means "collapse the COLUMNS" (operate ACROSS each row):
  sum(dim=1) = [1+2+3, 4+5+6] = [6, 15]

  Row 0: 1 + 2 + 3 = 6
  Row 1: 4 + 5 + 6 = 15

Memory trick:
  dim=0: "Squish rows together" -> result has NO row dimension
  dim=1: "Squish columns together" -> result has NO column dimension
```

---

## 8.5 Moving Tensors to GPU

### Why Use a GPU?

A **GPU** (Graphics Processing Unit) can perform thousands of math operations in parallel. Neural networks are mostly matrix multiplications, which GPUs are designed for.

```
CPU vs. GPU Speed
====================

CPU: Processes operations ONE AT A TIME (or a few at a time)
     [op1] -> [op2] -> [op3] -> [op4] -> ... (sequential)

GPU: Processes THOUSANDS of operations AT THE SAME TIME
     [op1]
     [op2]
     [op3]   All happening simultaneously!
     [op4]
     [...]
     [op1000]

For a matrix multiplication of size 1000x1000:
  CPU: ~10 milliseconds
  GPU: ~0.1 milliseconds (100x faster)

For training a large neural network:
  CPU: Hours to days
  GPU: Minutes to hours
```

### Moving Tensors Between Devices

```python
import torch

# Check if GPU is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Create a tensor on CPU (default)
cpu_tensor = torch.tensor([1.0, 2.0, 3.0])
print(f"CPU tensor: {cpu_tensor}")
print(f"Device: {cpu_tensor.device}")

# Move to GPU (if available)
gpu_tensor = cpu_tensor.to(device)
print(f"\nMoved tensor: {gpu_tensor}")
print(f"Device: {gpu_tensor.device}")

# Create a tensor directly on GPU
if torch.cuda.is_available():
    direct_gpu = torch.tensor([4.0, 5.0, 6.0], device='cuda')
    print(f"\nDirect GPU tensor: {direct_gpu}")
    print(f"Device: {direct_gpu.device}")

# Move back to CPU (needed for NumPy conversion)
back_to_cpu = gpu_tensor.cpu()
print(f"\nBack on CPU: {back_to_cpu}")
print(f"Device: {back_to_cpu.device}")
```

**Output (without GPU):**

```
Using device: cpu
CPU tensor: tensor([1., 2., 3.])
Device: cpu

Moved tensor: tensor([1., 2., 3.])
Device: cpu

Back on CPU: tensor([1., 2., 3.])
Device: cpu
```

**Output (with GPU):**

```
Using device: cuda
CPU tensor: tensor([1., 2., 3.])
Device: cpu

Moved tensor: tensor([1., 2., 3.], device='cuda:0')
Device: cuda:0

Direct GPU tensor: tensor([4., 5., 6.], device='cuda:0')
Device: cuda:0

Back on CPU: tensor([1., 2., 3.])
Device: cpu
```

### Important Rule: All Tensors Must Be on the Same Device

```
Device Mismatch Error
========================

This will cause an error:
  cpu_tensor = torch.tensor([1, 2, 3])           # on CPU
  gpu_tensor = torch.tensor([4, 5, 6]).to('cuda')  # on GPU
  result = cpu_tensor + gpu_tensor                 # ERROR!

Error message:
  RuntimeError: Expected all tensors to be on the same device

Solution: Move both tensors to the same device first.
  cpu_tensor = cpu_tensor.to('cuda')
  result = cpu_tensor + gpu_tensor  # Now both on GPU, works!

Rule of thumb:
  Move everything to GPU at the start of training.
  Move results back to CPU only when you need to print or plot.
```

---

## 8.6 Autograd: Automatic Differentiation

### What Is Autograd?

**Autograd** is PyTorch's system for automatically computing gradients. Remember Chapter 6, where we computed gradients by hand using the chain rule? Autograd does that automatically.

```
Autograd: What It Does
=========================

You write:
  x = torch.tensor(2.0, requires_grad=True)
  y = x ** 2 + 3 * x + 1
  y.backward()
  print(x.grad)  # dy/dx = 2x + 3 = 2(2) + 3 = 7

Behind the scenes, PyTorch:
  1. Builds a computational graph during the forward pass
  2. Walks backward through the graph when you call .backward()
  3. Computes the gradient for every tensor with requires_grad=True
  4. Stores the gradient in the .grad attribute
```

### requires_grad=True: Telling PyTorch to Track

When you set `requires_grad=True`, you are saying: "I want to compute the gradient of the final result with respect to this tensor."

```python
import torch

# Without requires_grad (default)
a = torch.tensor(3.0)
print(f"a.requires_grad = {a.requires_grad}")  # False

# With requires_grad
b = torch.tensor(3.0, requires_grad=True)
print(f"b.requires_grad = {b.requires_grad}")  # True
```

**Output:**

```
a.requires_grad = False
b.requires_grad = True
```

### Computing Gradients with .backward()

```python
import torch

# Simple example: y = x^2
x = torch.tensor(3.0, requires_grad=True)
y = x ** 2

print(f"x = {x}")
print(f"y = x^2 = {y}")

# Compute gradient
y.backward()

print(f"dy/dx = {x.grad}")
print(f"Expected: 2 * x = 2 * 3 = {2 * 3.0}")
```

**Output:**

```
x = 3.0
y = x^2 = 9.0
dy/dx = 6.0
Expected: 2 * x = 2 * 3 = 6.0
```

### More Complex Example

```python
import torch

# y = 2x^3 + 5x^2 - 3x + 7
x = torch.tensor(2.0, requires_grad=True)
y = 2 * x**3 + 5 * x**2 - 3 * x + 7

print(f"x = {x.item()}")
print(f"y = 2x^3 + 5x^2 - 3x + 7 = {y.item()}")

# Compute gradient
y.backward()

# dy/dx = 6x^2 + 10x - 3
print(f"\ndy/dx (autograd) = {x.grad.item()}")
expected = 6 * 2**2 + 10 * 2 - 3
print(f"dy/dx (manual)   = 6(2)^2 + 10(2) - 3 = {expected}")
```

**Output:**

```
x = 2.0
y = 2x^3 + 5x^2 - 3x + 7 = 37.0

dy/dx (autograd) = 41.0
dy/dx (manual)   = 6(2)^2 + 10(2) - 3 = 41
```

### Gradients with Multiple Variables

```python
import torch

# z = 3x^2 + 2xy + y^2
x = torch.tensor(1.0, requires_grad=True)
y = torch.tensor(2.0, requires_grad=True)

z = 3 * x**2 + 2 * x * y + y**2

print(f"x = {x.item()}, y = {y.item()}")
print(f"z = 3x^2 + 2xy + y^2 = {z.item()}")

# Compute gradients for BOTH x and y
z.backward()

print(f"\ndz/dx (autograd) = {x.grad.item()}")
print(f"dz/dx (manual)   = 6x + 2y = 6(1) + 2(2) = {6*1 + 2*2}")

print(f"\ndz/dy (autograd) = {y.grad.item()}")
print(f"dz/dy (manual)   = 2x + 2y = 2(1) + 2(2) = {2*1 + 2*2}")
```

**Output:**

```
x = 1.0, y = 2.0
z = 3x^2 + 2xy + y^2 = 11.0

dz/dx (autograd) = 10.0
dz/dx (manual)   = 6x + 2y = 6(1) + 2(2) = 10

dz/dy (autograd) = 6.0
dz/dy (manual)   = 2x + 2y = 2(1) + 2(2) = 6
```

---

## 8.7 The Computational Graph in PyTorch

### How PyTorch Builds the Graph

Every time you perform an operation on a tensor with `requires_grad=True`, PyTorch records that operation in a computational graph. When you call `.backward()`, it walks backward through the graph to compute gradients.

```
How PyTorch Builds and Uses the Computational Graph
=======================================================

STEP 1: You create tensors with requires_grad=True
  x = torch.tensor(2.0, requires_grad=True)
  w = torch.tensor(3.0, requires_grad=True)

STEP 2: You perform operations (forward pass)
  y = w * x        # PyTorch records: "multiply node"
  z = y + 1        # PyTorch records: "add node"
  loss = z ** 2    # PyTorch records: "power node"

  Behind the scenes, PyTorch builds this graph:

    x ---\
          * ---> y ---> + ---> z ---> **2 ---> loss
    w ---/             |
                       1

STEP 3: You call loss.backward()
  PyTorch walks the graph RIGHT TO LEFT:
    loss -> z -> y -> x, w

  It computes:
    dloss/dz = 2z
    dloss/dy = dloss/dz * 1 = 2z
    dloss/dw = dloss/dy * x = 2z * x
    dloss/dx = dloss/dy * w = 2z * w

STEP 4: Gradients are stored in .grad
  x.grad = dloss/dx
  w.grad = dloss/dw
```

### Python Code: Watching the Graph

```python
import torch

x = torch.tensor(2.0, requires_grad=True)
w = torch.tensor(3.0, requires_grad=True)

# Forward pass (builds the graph)
y = w * x
z = y + 1
loss = z ** 2

print("=== Forward Pass ===")
print(f"x = {x.item()}")
print(f"w = {w.item()}")
print(f"y = w * x = {y.item()}")
print(f"z = y + 1 = {z.item()}")
print(f"loss = z^2 = {loss.item()}")

# Check the graph connections
print(f"\n=== Computational Graph ===")
print(f"loss.grad_fn = {loss.grad_fn}")
print(f"z.grad_fn = {z.grad_fn}")
print(f"y.grad_fn = {y.grad_fn}")
print(f"x.grad_fn = {x.grad_fn}")  # None (it's a leaf)
print(f"w.grad_fn = {w.grad_fn}")  # None (it's a leaf)

# Backward pass
loss.backward()

print(f"\n=== Gradients ===")
print(f"dloss/dx = {x.grad.item()}")
print(f"dloss/dw = {w.grad.item()}")

# Manual verification
# loss = (w*x + 1)^2
# dloss/dx = 2(w*x + 1) * w = 2(3*2 + 1) * 3 = 2(7)(3) = 42
# dloss/dw = 2(w*x + 1) * x = 2(3*2 + 1) * 2 = 2(7)(2) = 28
print(f"\n=== Manual Verification ===")
print(f"dloss/dx should be 2(w*x+1)*w = 2(7)(3) = 42")
print(f"dloss/dw should be 2(w*x+1)*x = 2(7)(2) = 28")
```

**Output:**

```
=== Forward Pass ===
x = 2.0
w = 3.0
y = w * x = 6.0
z = y + 1 = 7.0
loss = z^2 = 49.0

=== Computational Graph ===
loss.grad_fn = <PowBackward0 object at 0x...>
z.grad_fn = <AddBackward0 object at 0x...>
y.grad_fn = <MulBackward0 object at 0x...>
x.grad_fn = None
w.grad_fn = None

=== Gradients ===
dloss/dx = 42.0
dloss/dw = 28.0

=== Manual Verification ===
dloss/dx should be 2(w*x+1)*w = 2(7)(3) = 42
dloss/dw should be 2(w*x+1)*x = 2(7)(2) = 28
```

### Line-by-Line Explanation

```
Line: loss.grad_fn = <PowBackward0 ...>
  This tells us that 'loss' was created by a power operation.
  PyTorch stored this information so it can compute the
  derivative of the power operation during backward.

Line: x.grad_fn = None
  x has no grad_fn because it was created by the user,
  not by an operation. It is a "leaf" node in the graph.
  Leaves are the starting points of the graph.

Line: loss.backward()
  This triggers the backward pass. PyTorch walks from 'loss'
  back through PowBackward0 -> AddBackward0 -> MulBackward0
  and computes the gradient for each leaf tensor.

Line: x.grad.item()
  After backward(), the computed gradient is stored in x.grad.
  .item() converts a scalar tensor to a Python number.
```

### Important: Gradients Accumulate

```python
import torch

x = torch.tensor(3.0, requires_grad=True)

# First backward
y1 = x ** 2
y1.backward()
print(f"After first backward: x.grad = {x.grad}")

# Second backward WITHOUT zeroing
y2 = x ** 2
y2.backward()
print(f"After second backward: x.grad = {x.grad}")
print("The gradient ACCUMULATED (doubled)!")

# The fix: zero the gradient first
x.grad.zero_()
y3 = x ** 2
y3.backward()
print(f"After zeroing + third backward: x.grad = {x.grad}")
print("Now the gradient is correct.")
```

**Output:**

```
After first backward: x.grad = 6.0
After second backward: x.grad = 12.0
The gradient ACCUMULATED (doubled)!
After zeroing + third backward: x.grad = 6.0
Now the gradient is correct.
```

```
Why Gradients Accumulate (and why it matters)
================================================

PyTorch ADDS new gradients to existing ones by default.
It does NOT replace them.

This is why you MUST call:
  optimizer.zero_grad()   (in a training loop)
  or
  tensor.grad.zero_()    (for individual tensors)

BEFORE each backward pass.

If you forget, the gradients will keep growing,
and your weight updates will be completely wrong.
```

---

## 8.8 Putting It All Together: A Complete Example

Let us use everything we have learned to train a simple linear model using pure PyTorch tensors and autograd.

```python
import torch

# ============================================
# Training a Linear Model with PyTorch Autograd
# ============================================

# Generate some data: y = 3x + 2 (with noise)
torch.manual_seed(42)
x_data = torch.linspace(0, 10, 50)
y_data = 3 * x_data + 2 + torch.randn(50) * 1.5

# Initialize weights (what we want to learn)
w = torch.tensor(0.0, requires_grad=True)  # slope (should become ~3)
b = torch.tensor(0.0, requires_grad=True)  # intercept (should become ~2)

learning_rate = 0.01
epochs = 100

print("Training a linear model: y = wx + b")
print(f"True values: w=3.0, b=2.0")
print(f"Starting:    w={w.item():.4f}, b={b.item():.4f}")
print()
print(f"{'Epoch':<8}{'Loss':<12}{'w':<10}{'b':<10}")
print("-" * 40)

for epoch in range(epochs):
    # Forward pass
    y_pred = w * x_data + b

    # Compute loss (MSE)
    loss = ((y_pred - y_data) ** 2).mean()

    # Backward pass (autograd computes gradients)
    loss.backward()

    # Update weights (manually, without optimizer)
    with torch.no_grad():  # Don't track these operations
        w -= learning_rate * w.grad
        b -= learning_rate * b.grad

    # Zero gradients for next iteration
    w.grad.zero_()
    b.grad.zero_()

    # Print progress
    if epoch % 20 == 0 or epoch == epochs - 1:
        print(f"{epoch:<8}{loss.item():<12.4f}{w.item():<10.4f}{b.item():<10.4f}")

print("-" * 40)
print(f"\nLearned: y = {w.item():.2f}x + {b.item():.2f}")
print(f"True:    y = 3.00x + 2.00")
```

**Output:**

```
Training a linear model: y = wx + b
True values: w=3.0, b=2.0
Starting:    w=0.0000, b=0.0000

Epoch   Loss        w         b
----------------------------------------
0       119.6912    1.4768    0.2816
20      3.2032      2.8914    2.1345
40      2.2710      2.9608    2.0395
60      2.2253      2.9746    2.0205
80      2.2233      2.9773    2.0167
99      2.2230      2.9778    2.0160
----------------------------------------

Learned: y = 2.98x + 2.02
True:    y = 3.00x + 2.00
```

### Line-by-Line Explanation

```
Line: w = torch.tensor(0.0, requires_grad=True)
  We create a weight tensor and tell PyTorch to track gradients.

Line: y_pred = w * x_data + b
  Forward pass. PyTorch builds a computational graph.

Line: loss = ((y_pred - y_data) ** 2).mean()
  Compute MSE loss. The graph grows to include this operation.

Line: loss.backward()
  PyTorch walks backward through the entire graph,
  computing dL/dw and dL/db automatically.

Line: with torch.no_grad():
  We temporarily disable gradient tracking because we do NOT
  want PyTorch to track the weight update as part of the graph.
  The weight update is not part of the model; it is the optimizer.

Line: w -= learning_rate * w.grad
  Gradient descent update. We subtract because we want to
  DECREASE the loss.

Line: w.grad.zero_()
  Reset gradients to zero. If we skip this, gradients will
  ACCUMULATE across iterations and training will fail.
```

---

## Common Mistakes

```
Common Mistakes with PyTorch
================================

MISTAKE 1: Forgetting requires_grad=True
  Wrong:  w = torch.tensor(0.5)
  Right:  w = torch.tensor(0.5, requires_grad=True)
  Why:    Without requires_grad, PyTorch will not compute gradients.
          No error message — the gradient will simply be None.

MISTAKE 2: Not zeroing gradients
  Wrong:  Skip w.grad.zero_() between backward passes
  Right:  Always zero gradients before each backward pass
  Why:    PyTorch accumulates gradients. Without zeroing,
          they grow larger each iteration.

MISTAKE 3: Mixing devices
  Wrong:  Adding a CPU tensor and a GPU tensor
  Right:  Move all tensors to the same device first
  Why:    PyTorch cannot do math across devices.
          You will get a RuntimeError.

MISTAKE 4: Calling .numpy() on a GPU tensor
  Wrong:  gpu_tensor.numpy()
  Right:  gpu_tensor.cpu().numpy()
  Why:    NumPy only works on CPU. You must move to CPU first.

MISTAKE 5: Calling .numpy() on a tensor with gradients
  Wrong:  tensor_with_grad.numpy()
  Right:  tensor_with_grad.detach().numpy()
  Why:    You must detach from the computational graph first.

MISTAKE 6: Using torch.tensor() instead of torch.from_numpy()
  Note:   torch.tensor() copies the data (safe but uses more memory)
          torch.from_numpy() shares memory (efficient but changes
          to the NumPy array affect the tensor and vice versa)
```

---

## Best Practices

```
Best Practices for PyTorch
==============================

1. SET A RANDOM SEED FOR REPRODUCIBILITY
   torch.manual_seed(42)
   This ensures your results are the same every time.

2. USE .to(device) FOR DEVICE-AGNOSTIC CODE
   device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
   tensor = tensor.to(device)
   model = model.to(device)

3. USE float32 (NOT float64)
   PyTorch defaults to float32, which is faster on GPUs.
   Do not use float64 unless you need extreme precision.

4. USE .item() TO GET PYTHON NUMBERS
   loss_value = loss.item()  # Not loss (which is a tensor)
   This is cleaner and avoids keeping the graph in memory.

5. USE torch.no_grad() FOR INFERENCE
   with torch.no_grad():
       prediction = model(input)
   This skips building the graph, saving memory and time.

6. PREFER IN-PLACE OPERATIONS FOR GRADIENT ZEROING
   w.grad.zero_()  # In-place (good)
   Not: w.grad = torch.zeros_like(w.grad)  # Creates new tensor
```

---

## Quick Summary

```
Chapter 8 Summary: PyTorch Basics
=====================================

1. PyTorch is a deep learning framework that provides tensors
   (GPU arrays), autograd (automatic gradients), and neural
   network building blocks.

2. Tensors are multi-dimensional arrays, like NumPy arrays
   but with GPU support and gradient tracking.

3. Create tensors with torch.tensor(), torch.zeros(),
   torch.ones(), torch.rand(), torch.randn(), etc.

4. Tensor operations: +, -, *, /, @, reshape, transpose,
   sum, mean, max, min — similar to NumPy.

5. Move tensors to GPU with tensor.to('cuda') and back
   with tensor.cpu(). All tensors in an operation must
   be on the same device.

6. Autograd computes gradients automatically.
   Set requires_grad=True, call .backward(), read .grad.

7. Always zero gradients between iterations.

8. The computational graph is built during the forward pass
   and consumed during the backward pass.
```

---

## Key Points

- **PyTorch** = deep learning framework by Meta (Facebook) for tensors, autograd, and neural networks
- **Tensor** = multi-dimensional array, like NumPy ndarray but with GPU support
- **requires_grad=True** = tells PyTorch to track operations for gradient computation
- **.backward()** = computes gradients by walking the computational graph backward
- **.grad** = attribute that stores the computed gradient after .backward()
- **.to(device)** = moves a tensor to CPU or GPU
- **torch.no_grad()** = context manager that disables gradient tracking (for inference)
- **Gradients accumulate** = always call .zero_() or optimizer.zero_grad() before backward
- **float32** = default and recommended data type for neural networks

---

## Practice Questions

1. What is the difference between torch.tensor([1, 2, 3]) and torch.from_numpy(np.array([1, 2, 3]))? When would you prefer each?

2. Create a 3x4 tensor of random numbers between 0 and 1. Then reshape it to 2x6. What is the constraint on reshaping (why can you reshape 3x4 to 2x6 but not to 2x5)?

3. If x = torch.tensor(4.0, requires_grad=True) and y = 3*x**2 - 2*x + 5, what is dy/dx? Verify using both autograd and manual calculus.

4. Explain why you need to call optimizer.zero_grad() (or tensor.grad.zero_()) before each backward pass. What happens if you forget?

5. Why do you need to use torch.no_grad() when updating weights manually? What would go wrong if you skipped it?

---

## Exercises

### Exercise 1: Tensor Warm-Up

Create the following tensors and print their shapes: (a) A 5x5 identity matrix. (b) A 3x3x3 tensor of ones. (c) A 1-D tensor containing the numbers 0 through 99. (d) Reshape the 1-D tensor from (c) into a 10x10 matrix. (e) Compute the mean of each row and the sum of each column.

### Exercise 2: Autograd Practice

Use PyTorch autograd to compute the gradient of f(x) = sin(x) * x^2 at x = pi/4. Compare your answer to the analytically derived gradient: f'(x) = cos(x) * x^2 + sin(x) * 2x.

### Exercise 3: Train a Quadratic Model

Generate data from y = 2x^2 - 3x + 1 with some noise. Using PyTorch autograd (NOT nn.Module), train three parameters (a, b, c) so that the model y = ax^2 + bx + c fits the data. Print the learned coefficients and compare them to the true values.

---

## What Is Next?

You now know the basics of PyTorch: tensors, operations, GPU support, and autograd. But writing everything with raw tensors and manual weight updates is tedious. Real neural networks have dozens of layers and millions of parameters.

In Chapter 9, you will learn how to use PyTorch's **nn.Module** to build neural networks the proper way. You will define layers, write forward methods, use DataLoaders, and build a complete training loop. By the end of that chapter, you will classify handwritten digits from the MNIST dataset with a real neural network.
