# Chapter 13: NumPy — Fast Math on Arrays

## What You Will Learn

- What NumPy is and why it exists
- How to install NumPy
- How to create arrays (from lists, zeros, ones, arange, linspace)
- Array attributes: shape, dtype, ndim
- Indexing and slicing arrays
- Basic math operations (element-wise)
- What broadcasting is and how it works
- Useful functions: sum, mean, max, min, reshape
- Dot product and matrix multiplication with `@`
- How to generate random numbers
- Why NumPy is faster than regular Python lists

## Why This Chapter Matters

Python lists are great for everyday programming. But when you need to do math on thousands or millions of numbers, lists are **slow**.

NumPy (Numerical Python) is a library that makes math on large collections of numbers incredibly fast. It is the **foundation** of almost every data science and AI library in Python.

Think of it this way:

- **Python list** = a bicycle. Fine for short trips.
- **NumPy array** = a sports car. Built for speed.

If you want to learn data science, machine learning, or AI, you **must** learn NumPy. Almost every tool in these fields — Pandas, Matplotlib, TensorFlow, PyTorch — is built on top of NumPy.

---

## 13.1 What Is NumPy?

NumPy is a Python library that gives you a powerful data structure called an **array**. An array is like a Python list, but:

- It is much **faster** for math operations
- It uses much **less memory**
- It supports **multi-dimensional** data (tables, cubes, etc.)

```
Python List:                NumPy Array:

[1, 2, 3, 4, 5]           [1, 2, 3, 4, 5]

Stored in different        Stored in one
places in memory.          continuous block.
Slow to process.           Fast to process.

+--+ +--+ +--+ +--+       +--+--+--+--+--+
| 1| | 2| | 3| | 4|       | 1| 2| 3| 4| 5|
+--+ +--+ +--+ +--+       +--+--+--+--+--+
scattered                  continuous (fast!)
```

---

## 13.2 Installing NumPy

Open your terminal and type:

```bash
pip install numpy
```

That is it. Now you can use it in your Python programs.

The standard way to import NumPy:

```python
import numpy as np
```

Everyone uses `np` as the alias. It is the universal convention.

---

## 13.3 Creating Arrays

### From a Python List

```python
import numpy as np

# 1D array (like a row of numbers)
numbers = np.array([1, 2, 3, 4, 5])
print(numbers)
print(type(numbers))
```

**Expected Output:**
```
[1 2 3 4 5]
<class 'numpy.ndarray'>
```

**Line-by-line explanation:**

- `np.array([1, 2, 3, 4, 5])` — Converts a Python list into a NumPy array.
- Notice the output has **no commas**. That is how you can tell it is a NumPy array, not a list.
- `numpy.ndarray` — The type of a NumPy array. "ndarray" means "N-dimensional array."

### 2D Array (Like a Table)

```python
import numpy as np

table = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9]])
print(table)
```

**Expected Output:**
```
[[1 2 3]
 [4 5 6]
 [7 8 9]]
```

```
How to visualize a 2D array:

        Column 0  Column 1  Column 2
Row 0 [    1         2         3    ]
Row 1 [    4         5         6    ]
Row 2 [    7         8         9    ]
```

### Arrays of Zeros and Ones

```python
import numpy as np

# Array of zeros
zeros = np.zeros(5)
print(zeros)

# 2D array of zeros (3 rows, 4 columns)
zero_table = np.zeros((3, 4))
print(zero_table)

# Array of ones
ones = np.ones(4)
print(ones)

# 2D array of ones
one_table = np.ones((2, 3))
print(one_table)
```

**Expected Output:**
```
[0. 0. 0. 0. 0.]
[[0. 0. 0. 0.]
 [0. 0. 0. 0.]
 [0. 0. 0. 0.]]
[1. 1. 1. 1.]
[[1. 1. 1.]
 [1. 1. 1.]]
```

**Note:** The dots (like `0.` and `1.`) mean these are floating-point numbers (decimals), not integers.

### arange — Like range() but for Arrays

```python
import numpy as np

# Numbers from 0 to 9
a = np.arange(10)
print(a)

# Numbers from 2 to 10 (step of 2)
b = np.arange(2, 11, 2)
print(b)

# Floating-point range
c = np.arange(0, 1, 0.2)
print(c)
```

**Expected Output:**
```
[0 1 2 3 4 5 6 7 8 9]
[ 2  4  6  8 10]
[0.  0.2 0.4 0.6 0.8]
```

**Line-by-line explanation:**

- `np.arange(10)` — Creates numbers from 0 up to (but not including) 10. Like Python's `range()`.
- `np.arange(2, 11, 2)` — Start at 2, go up to 11, step by 2. Gives 2, 4, 6, 8, 10.
- `np.arange(0, 1, 0.2)` — Unlike `range()`, arange works with decimals!

### linspace — Evenly Spaced Numbers

```python
import numpy as np

# 5 numbers evenly spaced from 0 to 1
a = np.linspace(0, 1, 5)
print(a)

# 4 numbers evenly spaced from 0 to 10
b = np.linspace(0, 10, 4)
print(b)
```

**Expected Output:**
```
[0.   0.25 0.5  0.75 1.  ]
[ 0.          3.33333333  6.66666667 10.        ]
```

**Line-by-line explanation:**

- `np.linspace(0, 1, 5)` — "Give me exactly 5 numbers, evenly spaced, from 0 to 1." The endpoints ARE included.
- `np.linspace(0, 10, 4)` — "Give me exactly 4 numbers from 0 to 10." That is 0, 3.33, 6.67, 10.

```
arange vs linspace:

arange(0, 1, 0.25)  -->  You choose the STEP SIZE
  [0, 0.25, 0.5, 0.75]   (does NOT include endpoint)

linspace(0, 1, 5)   -->  You choose HOW MANY numbers
  [0, 0.25, 0.5, 0.75, 1.0]  (INCLUDES endpoint)
```

---

## 13.4 Array Attributes

Every NumPy array has properties that tell you about its structure.

```python
import numpy as np

arr = np.array([[1, 2, 3, 4],
                [5, 6, 7, 8],
                [9, 10, 11, 12]])

print(f"Shape: {arr.shape}")     # (rows, columns)
print(f"Dimensions: {arr.ndim}") # number of dimensions
print(f"Data type: {arr.dtype}") # type of elements
print(f"Size: {arr.size}")       # total number of elements
```

**Expected Output:**
```
Shape: (3, 4)
Dimensions: 2
Data type: int64
Size: 12
```

**Line-by-line explanation:**

- `arr.shape` — (3, 4) means 3 rows and 4 columns.
- `arr.ndim` — 2 means it is a 2-dimensional array (a table).
- `arr.dtype` — `int64` means each element is a 64-bit integer.
- `arr.size` — 12 means there are 12 elements total (3 x 4 = 12).

```
shape = (3, 4) means:

     4 columns
    +--+--+--+--+
    | 1| 2| 3| 4|   3
    +--+--+--+--+   rows
    | 5| 6| 7| 8|
    +--+--+--+--+
    | 9|10|11|12|
    +--+--+--+--+

ndim = 2 (two dimensions: rows and columns)
size = 12 (total elements)
dtype = int64 (integers)
```

---

## 13.5 Indexing and Slicing

### 1D Array Indexing

Works just like Python lists.

```python
import numpy as np

arr = np.array([10, 20, 30, 40, 50])

print(arr[0])     # First element
print(arr[-1])    # Last element
print(arr[1:4])   # Elements at index 1, 2, 3
print(arr[:3])    # First 3 elements
print(arr[2:])    # From index 2 to the end
```

**Expected Output:**
```
10
50
[20 30 40]
[10 20 30]
[30 40 50]
```

### 2D Array Indexing

For 2D arrays, you use two indices: `[row, column]`.

```python
import numpy as np

table = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9]])

print(table[0, 0])    # Row 0, Column 0
print(table[1, 2])    # Row 1, Column 2
print(table[2, :])    # Entire row 2
print(table[:, 1])    # Entire column 1
print(table[0:2, 1:3]) # Sub-table
```

**Expected Output:**
```
1
6
[7 8 9]
[2 5 8]
[[2 3]
 [5 6]]
```

**Line-by-line explanation:**

- `table[0, 0]` — Row 0, Column 0 = 1.
- `table[1, 2]` — Row 1, Column 2 = 6.
- `table[2, :]` — All columns of row 2. The `:` means "everything."
- `table[:, 1]` — All rows of column 1. Gives [2, 5, 8].
- `table[0:2, 1:3]` — Rows 0-1, Columns 1-2. A smaller table.

```
table[0:2, 1:3] selects:

        Col 0  Col 1  Col 2
Row 0 [  1     [2      3]   ]    <-- rows 0:2
Row 1 [  4     [5      6]   ]    <--
Row 2 [  7      8      9    ]    (not included)
               ^       ^
            cols 1:3 selected

Result: [[2, 3],
         [5, 6]]
```

### Boolean Indexing (Filtering)

You can use conditions to select elements. This is very powerful.

```python
import numpy as np

scores = np.array([85, 92, 78, 96, 65, 88])

# Which scores are above 80?
mask = scores > 80
print(mask)

# Get only the scores above 80
high_scores = scores[scores > 80]
print(high_scores)

# Get scores between 80 and 90
mid_scores = scores[(scores >= 80) & (scores <= 90)]
print(mid_scores)
```

**Expected Output:**
```
[ True  True False  True False  True]
[85 92 96 88]
[85 88]
```

**Line-by-line explanation:**

- `scores > 80` — Creates a True/False array. True where the score is above 80.
- `scores[scores > 80]` — Uses the True/False array as a filter. Only keeps the True values.
- `(scores >= 80) & (scores <= 90)` — Combines two conditions with `&` (AND). Use `|` for OR. Always wrap conditions in parentheses.

---

## 13.6 Basic Math Operations

Here is where NumPy really shines. Math operations work on **every element at once**.

### Element-wise Operations

```python
import numpy as np

a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

print(a + b)      # Add element by element
print(a - b)      # Subtract
print(a * b)      # Multiply
print(a / b)      # Divide
print(a ** 2)     # Square each element
```

**Expected Output:**
```
[11 22 33 44]
[ -9 -18 -27 -36]
[ 10  40  90 160]
[0.1 0.1 0.1 0.1]
[ 1  4  9 16]
```

```
Element-wise addition:

  a:  [ 1,  2,  3,  4]
      +   +   +   +
  b:  [10, 20, 30, 40]
      =   =   =   =
  result: [11, 22, 33, 44]

Each element pairs up with the element at the same position.
```

### Comparing with Python Lists

```python
# With Python lists (does NOT do math):
list_a = [1, 2, 3]
list_b = [4, 5, 6]
print(list_a + list_b)      # Concatenates: [1, 2, 3, 4, 5, 6]

# With NumPy arrays (does math):
arr_a = np.array([1, 2, 3])
arr_b = np.array([4, 5, 6])
print(arr_a + arr_b)         # Adds: [5, 7, 9]
```

**Expected Output:**
```
[1, 2, 3, 4, 5, 6]
[5 7 9]
```

---

## 13.7 Broadcasting — The Magic Trick

Broadcasting is NumPy's way of doing math between arrays of **different sizes**. It "stretches" the smaller array to match the bigger one.

### Example: Array + Scalar (Single Number)

```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])

# Add 10 to every element
print(arr + 10)

# Multiply every element by 3
print(arr * 3)
```

**Expected Output:**
```
[11 12 13 14 15]
[ 3  6  9 12 15]
```

```
Broadcasting with a scalar:

arr:       [1,  2,  3,  4,  5]
           +   +   +   +   +
10:        [10, 10, 10, 10, 10]   <-- NumPy "stretches" 10
           =   =   =   =   =
result:    [11, 12, 13, 14, 15]
```

### Example: 2D Array + 1D Array

```python
import numpy as np

table = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9]])

row = np.array([10, 20, 30])

print(table + row)
```

**Expected Output:**
```
[[11 22 33]
 [14 25 36]
 [17 28 39]]
```

```
Broadcasting a 1D array across a 2D array:

table:  [[1,  2,  3],       row:  [10, 20, 30]
         [4,  5,  6],             [10, 20, 30]  <-- stretched
         [7,  8,  9]]             [10, 20, 30]  <-- stretched

result: [[11, 22, 33],
         [14, 25, 36],
         [17, 28, 39]]
```

### Real-World Example: Converting Temperatures

```python
import numpy as np

# Temperatures in Celsius
celsius = np.array([0, 20, 37, 100])

# Convert to Fahrenheit: F = C * 9/5 + 32
fahrenheit = celsius * 9/5 + 32
print(fahrenheit)
```

**Expected Output:**
```
[ 32.   68.   98.6 212. ]
```

Broadcasting lets you write `celsius * 9/5 + 32` instead of looping through each element. Clean, simple, and fast.

---

## 13.8 Useful Functions

### sum, mean, max, min

```python
import numpy as np

scores = np.array([85, 92, 78, 96, 65, 88])

print(f"Sum:  {np.sum(scores)}")
print(f"Mean: {np.mean(scores)}")
print(f"Max:  {np.max(scores)}")
print(f"Min:  {np.min(scores)}")
print(f"Std:  {np.std(scores):.2f}")
```

**Expected Output:**
```
Sum:  504
Mean: 84.0
Max:  96
Min:  65
Std:  10.26
```

### Axis Parameter (Rows vs Columns)

For 2D arrays, you can compute along rows or columns.

```python
import numpy as np

table = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9]])

print(f"Total sum: {np.sum(table)}")
print(f"Sum of each column: {np.sum(table, axis=0)}")
print(f"Sum of each row:    {np.sum(table, axis=1)}")
```

**Expected Output:**
```
Total sum: 45
Sum of each column: [12 15 18]
Sum of each row:    [ 6 15 24]
```

```
axis=0 means "go DOWN" (collapse rows):

    [1, 2, 3]
    [4, 5, 6]     axis=0
    [7, 8, 9]     goes DOWN
    ----------          |
   [12,15,18]          v

axis=1 means "go RIGHT" (collapse columns):

    [1, 2, 3] --> 6
    [4, 5, 6] --> 15    axis=1 goes RIGHT -->
    [7, 8, 9] --> 24
```

### reshape — Change the Shape

```python
import numpy as np

a = np.arange(12)
print(a)
print(a.shape)

# Reshape to 3 rows, 4 columns
b = a.reshape(3, 4)
print(b)
print(b.shape)

# Reshape to 4 rows, 3 columns
c = a.reshape(4, 3)
print(c)

# Use -1 to let NumPy figure out one dimension
d = a.reshape(2, -1)   # 2 rows, NumPy figures out columns
print(d)
print(d.shape)
```

**Expected Output:**
```
[ 0  1  2  3  4  5  6  7  8  9 10 11]
(12,)
[[ 0  1  2  3]
 [ 4  5  6  7]
 [ 8  9 10 11]]
(3, 4)
[[ 0  1  2]
 [ 3  4  5]
 [ 6  7  8]
 [ 9 10 11]]
[[ 0  1  2  3  4  5]
 [ 6  7  8  9 10 11]]
(2, 6)
```

**Line-by-line explanation:**

- `a.reshape(3, 4)` — Takes the 12 elements and arranges them into 3 rows and 4 columns.
- `a.reshape(4, 3)` — Same 12 elements, but 4 rows and 3 columns.
- `a.reshape(2, -1)` — The `-1` means "figure it out." 12 elements in 2 rows = 6 columns each.

**Important:** The total number of elements must stay the same. You cannot reshape 12 elements into a 5x3 array (that needs 15).

---

## 13.9 Dot Product and Matrix Multiplication

### Dot Product

The dot product multiplies matching elements and then adds them up. It is essential in AI and machine learning.

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

result = np.dot(a, b)
print(result)
```

**Expected Output:**
```
32
```

```
Dot product step by step:

a = [1, 2, 3]
b = [4, 5, 6]

Step 1: Multiply matching elements
  1*4 = 4
  2*5 = 10
  3*6 = 18

Step 2: Add them all up
  4 + 10 + 18 = 32
```

### Matrix Multiplication with @

The `@` operator does matrix multiplication. It is the standard way in Python.

```python
import numpy as np

A = np.array([[1, 2],
              [3, 4]])

B = np.array([[5, 6],
              [7, 8]])

result = A @ B
print(result)
```

**Expected Output:**
```
[[19 22]
 [43 50]]
```

```
Matrix multiplication:

A = [[1, 2],     B = [[5, 6],
     [3, 4]]          [7, 8]]

Result[0,0] = (1*5) + (2*7) = 5 + 14 = 19
Result[0,1] = (1*6) + (2*8) = 6 + 16 = 22
Result[1,0] = (3*5) + (4*7) = 15 + 28 = 43
Result[1,1] = (3*6) + (4*8) = 18 + 32 = 50

Result = [[19, 22],
          [43, 50]]
```

**Rule:** To multiply two matrices, the number of **columns** in the first must equal the number of **rows** in the second.

```
(2, 3) @ (3, 4) = (2, 4)   OK! 3 matches 3
 ^  ^     ^  ^     ^  ^
 |  |     |  |     |  +-- columns from B
 |  +-----|--+     +-- rows from A
 |        |
 |        +-- must match!
```

### Example: Using @ in a practical context

```python
import numpy as np

# Student scores (3 students, 4 subjects)
scores = np.array([[85, 90, 78, 92],
                    [88, 76, 95, 84],
                    [92, 88, 82, 90]])

# Weights for each subject
weights = np.array([0.3, 0.3, 0.2, 0.2])

# Weighted average for each student
weighted_avg = scores @ weights
print(weighted_avg)
```

**Expected Output:**
```
[86.5 83.8 89.4]
```

---

## 13.10 Random Numbers with NumPy

NumPy has its own random number generator that is faster and more powerful than Python's built-in `random` module.

```python
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Random floats between 0 and 1
print(np.random.rand(5))

# Random integers between 1 and 10
print(np.random.randint(1, 11, size=5))

# Random numbers from a normal distribution
# (mean=0, std=1)
print(np.random.randn(5))

# Random 2D array
print(np.random.rand(3, 4))

# Random choice from an array
fruits = np.array(["apple", "banana", "cherry"])
print(np.random.choice(fruits, 5))
```

**Expected Output:**
```
[0.37454012 0.95071431 0.73199394 0.59865848 0.15601864]
[ 2  1  5  4 10]
[ 0.14404357  1.45427351  0.76103773  0.12167502  0.44386323]
[[0.33367433 0.15634897 0.74002136 0.36755911]
 [0.59199282 0.35760344 0.22448773 0.69780624]
 [0.86511186 0.64079285 0.72467045 0.29116607]]
['cherry' 'cherry' 'apple' 'banana' 'cherry']
```

**Line-by-line explanation:**

- `np.random.seed(42)` — Sets the random seed. Same seed = same "random" numbers every time. Great for testing.
- `np.random.rand(5)` — 5 random numbers between 0 and 1.
- `np.random.randint(1, 11, size=5)` — 5 random integers from 1 to 10.
- `np.random.randn(5)` — 5 numbers from a normal distribution (bell curve).
- `np.random.rand(3, 4)` — A 3x4 table of random numbers.
- `np.random.choice(fruits, 5)` — Randomly pick 5 items from the array.

---

## 13.11 Why NumPy Is Faster Than Python Lists

Let me show you the speed difference.

```python
import numpy as np
import time

size = 1_000_000

# --- Python list ---
list_a = list(range(size))
list_b = list(range(size))

start = time.time()
list_c = [a + b for a, b in zip(list_a, list_b)]
list_time = time.time() - start

# --- NumPy array ---
arr_a = np.arange(size)
arr_b = np.arange(size)

start = time.time()
arr_c = arr_a + arr_b
numpy_time = time.time() - start

print(f"Python list: {list_time:.4f} seconds")
print(f"NumPy array: {numpy_time:.4f} seconds")
print(f"NumPy is {list_time / numpy_time:.0f}x faster!")
```

**Expected Output (approximate):**
```
Python list: 0.1200 seconds
NumPy array: 0.0015 seconds
NumPy is 80x faster!
```

### Why is NumPy so fast?

```
Python List:
+--------+--------+--------+--------+
| int obj| int obj| int obj| int obj|  Each item is a
| type   | type   | type   | type   |  full Python object.
| value:1| value:2| value:3| value:4|  Lots of overhead.
+--------+--------+--------+--------+
  scattered in memory

NumPy Array:
+---+---+---+---+
| 1 | 2 | 3 | 4 |  Raw numbers packed
+---+---+---+---+  tightly together.
  continuous in memory  No overhead.
```

Three reasons NumPy is faster:

1. **Memory layout** — NumPy stores data in one continuous block. CPUs love this.
2. **No type checking** — All elements have the same type. No need to check each one.
3. **Compiled C code** — NumPy operations run in highly optimized C code, not Python.

---

## Common Mistakes

### Mistake 1: Confusing * with @ for matrix operations

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# Element-wise multiplication (NOT matrix multiplication):
print(A * B)
# Output: [[ 5, 12], [21, 32]]

# Matrix multiplication:
print(A @ B)
# Output: [[19, 22], [43, 50]]
```

`*` multiplies element by element. `@` does real matrix multiplication.

### Mistake 2: Forgetting that reshape does not change the original

```python
import numpy as np

a = np.arange(6)
b = a.reshape(2, 3)

print(a.shape)  # Still (6,) — a is unchanged!
print(b.shape)  # (2, 3) — b is the reshaped version
```

### Mistake 3: Shape mismatch in operations

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([1, 2])

# This will cause an error:
# print(a + b)
# ValueError: operands could not be broadcast together
```

Both arrays must have compatible shapes for operations.

### Mistake 4: Modifying a slice modifies the original

```python
import numpy as np

original = np.array([1, 2, 3, 4, 5])
slice_view = original[1:4]
slice_view[0] = 99

print(original)   # [1, 99, 3, 4, 5]  -- original changed!
```

NumPy slices are **views**, not copies. Use `.copy()` if you need an independent copy.

### Mistake 5: Using Python's sum() instead of np.sum()

```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])

# Slow (Python's built-in sum):
total = sum(arr)

# Fast (NumPy's sum):
total = np.sum(arr)
```

Always use NumPy functions on NumPy arrays.

---

## Best Practices

1. **Always use `np` as the alias.** `import numpy as np` is the universal standard.
2. **Use NumPy functions, not Python built-ins.** Use `np.sum()`, not `sum()`. Use `np.max()`, not `max()`.
3. **Avoid loops.** If you are writing a `for` loop over a NumPy array, there is probably a faster NumPy way.
4. **Use broadcasting instead of loops.** `arr * 2` is better than `[x * 2 for x in arr]`.
5. **Set random seeds for reproducibility.** `np.random.seed(42)` so your results are the same each time.
6. **Use `.copy()` when you need an independent copy.** Slices are views, not copies.
7. **Check shapes before operations.** Use `.shape` to make sure arrays are compatible.
8. **Use `-1` in reshape** to let NumPy calculate one dimension automatically.

---

## Quick Summary

| Function | What It Does | Example |
|---|---|---|
| `np.array()` | Create array from list | `np.array([1, 2, 3])` |
| `np.zeros()` | Array of zeros | `np.zeros((3, 4))` |
| `np.ones()` | Array of ones | `np.ones(5)` |
| `np.arange()` | Range of numbers | `np.arange(0, 10, 2)` |
| `np.linspace()` | Evenly spaced numbers | `np.linspace(0, 1, 5)` |
| `.shape` | Array dimensions | `arr.shape` |
| `.reshape()` | Change shape | `arr.reshape(3, 4)` |
| `np.sum()` | Sum of elements | `np.sum(arr)` |
| `np.mean()` | Average | `np.mean(arr)` |
| `np.dot()` | Dot product | `np.dot(a, b)` |
| `@` | Matrix multiplication | `A @ B` |
| `np.random.rand()` | Random numbers | `np.random.rand(5)` |

---

## Key Points to Remember

1. NumPy is the foundation of data science in Python. Learn it well.
2. NumPy arrays are faster and use less memory than Python lists.
3. All elements in a NumPy array must have the same type.
4. Operations are element-wise: `[1,2,3] + [4,5,6]` = `[5,7,9]`.
5. Broadcasting lets you do math between arrays of different sizes.
6. Use `@` for matrix multiplication, `*` for element-wise multiplication.
7. `axis=0` goes down (columns), `axis=1` goes right (rows).
8. Slices are views, not copies. Use `.copy()` when needed.
9. Always use NumPy functions (`np.sum`) instead of Python built-ins (`sum`).
10. Set random seeds (`np.random.seed()`) for reproducible results.

---

## Practice Questions

**Question 1:** What is the difference between `np.arange(0, 10, 2)` and `np.linspace(0, 10, 5)`?

**Answer:** `np.arange(0, 10, 2)` creates numbers from 0 to 10 (not including 10) with a step of 2, giving `[0, 2, 4, 6, 8]`. `np.linspace(0, 10, 5)` creates exactly 5 numbers evenly spaced from 0 to 10 (including both endpoints), giving `[0, 2.5, 5, 7.5, 10]`.

**Question 2:** What does `axis=0` mean in `np.sum(table, axis=0)`?

**Answer:** `axis=0` means "go down the rows." It collapses all rows into one, giving you the sum of each column. For a 3x4 table, the result would be a 1D array with 4 elements — one sum per column.

**Question 3:** What is the difference between `*` and `@` for NumPy arrays?

**Answer:** `*` does element-wise multiplication — each element is multiplied by the corresponding element. `@` does matrix multiplication — it follows the linear algebra rules where rows and columns are combined using dot products.

**Question 4:** Why is `np.random.seed(42)` useful?

**Answer:** It makes the "random" numbers reproducible. Every time you run your code with the same seed, you get the same sequence of random numbers. This is essential for debugging and for making experiments repeatable.

**Question 5:** What happens if you try `np.array([1, 2, 3]) + np.array([1, 2])`?

**Answer:** You get a ValueError because the shapes are not compatible for broadcasting. The first array has 3 elements and the second has 2. They cannot be added because NumPy does not know how to align them.

---

## Exercises

### Exercise 1: Student Grade Analysis

Create a NumPy array of student scores and calculate statistics.

```python
# Create an array of 20 random test scores between 50 and 100
# Calculate: mean, median, standard deviation
# Find how many students scored above the mean
# Find the top 3 scores
```

**Sample Solution:**

```python
import numpy as np

np.random.seed(42)
scores = np.random.randint(50, 101, size=20)
print(f"Scores: {scores}")

mean = np.mean(scores)
median = np.median(scores)
std = np.std(scores)

print(f"Mean:   {mean:.1f}")
print(f"Median: {median:.1f}")
print(f"Std:    {std:.1f}")

above_mean = np.sum(scores > mean)
print(f"Students above mean: {above_mean}")

sorted_scores = np.sort(scores)[::-1]   # Sort descending
print(f"Top 3 scores: {sorted_scores[:3]}")
```

### Exercise 2: Temperature Converter

Create an array of temperatures and convert between scales.

```python
import numpy as np

celsius = np.array([0, 10, 20, 30, 37, 100])

fahrenheit = celsius * 9/5 + 32
kelvin = celsius + 273.15

print("Celsius    | Fahrenheit | Kelvin")
print("-" * 38)
for c, f, k in zip(celsius, fahrenheit, kelvin):
    print(f"{c:10.1f} | {f:10.1f} | {k:7.2f}")
```

### Exercise 3: Matrix Operations

Practice with matrix multiplication.

```python
import numpy as np

# Create two 3x3 matrices
# Calculate: A + B, A * B (element-wise), A @ B (matrix multiply)
# Find the transpose of A (use A.T)
# Calculate the determinant of A (use np.linalg.det(A))
```

**Sample Solution:**

```python
import numpy as np

A = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

B = np.array([[9, 8, 7],
              [6, 5, 4],
              [3, 2, 1]])

print("A + B:")
print(A + B)

print("\nA * B (element-wise):")
print(A * B)

print("\nA @ B (matrix multiplication):")
print(A @ B)

print("\nTranspose of A:")
print(A.T)

print(f"\nDeterminant of A: {np.linalg.det(A):.2f}")
```

---

## What Is Next?

You now have the power of NumPy for fast numerical computing. In the next chapter, we will learn **Pandas** — a library built on top of NumPy that makes working with tabular data (like spreadsheets) incredibly easy. Think of it as "Excel in Python."
