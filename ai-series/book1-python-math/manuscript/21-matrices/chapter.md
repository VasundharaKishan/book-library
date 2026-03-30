# Chapter 21: Matrices — The Spreadsheets of Mathematics

## What You Will Learn

- What a matrix is and why it looks like a spreadsheet
- How to create matrices using NumPy
- How to add, subtract, and multiply matrices
- What the transpose, identity matrix, inverse, and determinant are
- Why matrices are the foundation of machine learning

## Why This Chapter Matters

Every dataset you will ever work with in machine learning is a matrix.

Think about it. A spreadsheet with 1000 rows and 10 columns? That is a matrix. An image with 28 x 28 pixels? That is a matrix. A table of student grades? Also a matrix.

When you train a neural network, you are doing matrix math. When you load a dataset, you are loading a matrix. When you make predictions, you are multiplying matrices.

If you understand matrices, you understand how data flows through AI systems.

---

## What Is a Matrix?

A matrix is a grid of numbers arranged in rows and columns.

Think of a spreadsheet. Each row is a record. Each column is a feature. The whole spreadsheet is a matrix.

```
A simple matrix with 2 rows and 3 columns:

    Column 1   Column 2   Column 3
    --------   --------   --------
Row 1 |   1         2         3   |
Row 2 |   4         5         6   |
    ---------------------------------

We write this as:

    [ 1  2  3 ]
    [ 4  5  6 ]

This is a "2 x 3" matrix (2 rows, 3 columns).
```

The size of a matrix is always written as **rows x columns**. A 2 x 3 matrix has 2 rows and 3 columns.

### Real-Life Analogy

Imagine a classroom grade book:

```
              Math    Science    English
              ----    -------    -------
    Alice  |   90       85         92   |
    Bob    |   78       91         88   |
    Carol  |   95       89         76   |

    This is a 3 x 3 matrix.
    3 students (rows) and 3 subjects (columns).
```

Each number sits at a specific position. Alice's Science grade is in row 1, column 2. Its value is 85.

---

## Creating Matrices with NumPy

In Python, we use NumPy to create and work with matrices. NumPy stores matrices as "arrays."

### Creating a Matrix from a List of Lists

```python
import numpy as np

# Create a 2x3 matrix
matrix = np.array([
    [1, 2, 3],
    [4, 5, 6]
])

print(matrix)
print("Shape:", matrix.shape)
```

**Expected Output:**
```
[[1 2 3]
 [4 5 6]]
Shape: (2, 3)
```

**Line-by-line explanation:**
- `import numpy as np` — Load the NumPy library. We call it `np` for short.
- `np.array([...])` — Create a NumPy array from a list of lists.
- Each inner list `[1, 2, 3]` becomes one row of the matrix.
- `matrix.shape` — Returns the size as (rows, columns). Here it is (2, 3).

### Creating Special Matrices

NumPy has shortcuts for common matrices:

```python
import numpy as np

# Matrix of all zeros (3 rows, 4 columns)
zeros = np.zeros((3, 4))
print("Zeros matrix:")
print(zeros)

# Matrix of all ones (2 rows, 2 columns)
ones = np.ones((2, 2))
print("\nOnes matrix:")
print(ones)

# Matrix with random numbers (2 rows, 3 columns)
random_matrix = np.random.rand(2, 3)
print("\nRandom matrix:")
print(random_matrix)
```

**Expected Output:**
```
Zeros matrix:
[[0. 0. 0. 0.]
 [0. 0. 0. 0.]
 [0. 0. 0. 0.]]

Ones matrix:
[[1. 1.]
 [1. 1.]]

Random matrix:
[[0.5488 0.7152 0.6028]
 [0.5449 0.4237 0.6459]]
```

**Line-by-line explanation:**
- `np.zeros((3, 4))` — Creates a 3x4 matrix filled with zeros. Notice the double parentheses — the shape is a tuple.
- `np.ones((2, 2))` — Creates a 2x2 matrix filled with ones.
- `np.random.rand(2, 3)` — Creates a 2x3 matrix with random numbers between 0 and 1. Your numbers will be different each time.

### Accessing Elements

You can grab any number from a matrix using its row and column index. Remember: Python counts from 0.

```python
import numpy as np

matrix = np.array([
    [10, 20, 30],
    [40, 50, 60],
    [70, 80, 90]
])

# Get the element at row 0, column 1
print(matrix[0, 1])    # 20

# Get the entire first row
print(matrix[0])        # [10 20 30]

# Get the entire second column
print(matrix[:, 1])     # [20 50 80]
```

**Expected Output:**
```
20
[10 20 30]
[20 50 80]
```

**Line-by-line explanation:**
- `matrix[0, 1]` — Row 0, Column 1. That is the number 20.
- `matrix[0]` — The entire first row: [10, 20, 30].
- `matrix[:, 1]` — The colon `:` means "all rows." So this grabs column 1 from every row.

```
Visualizing matrix[0, 1]:

    [ 10   (20)   30 ]    <-- Row 0
    [ 40    50     60 ]
    [ 70    80     90 ]
            ^
         Column 1

    Answer: 20
```

---

## Matrix Addition and Subtraction

Adding two matrices is simple. You add matching positions together.

Both matrices must have the same shape.

```
Matrix Addition:

    [ 1  2 ]     [ 10  20 ]     [ 1+10   2+20 ]     [ 11  22 ]
    [ 3  4 ]  +  [ 30  40 ]  =  [ 3+30   4+40 ]  =  [ 33  44 ]
```

### Python Code

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[10, 20], [30, 40]])

# Addition
C = A + B
print("A + B =")
print(C)

# Subtraction
D = B - A
print("\nB - A =")
print(D)
```

**Expected Output:**
```
A + B =
[[11 22]
 [33 44]]

B - A =
[[ 9 18]
 [27 36]]
```

**Line-by-line explanation:**
- `A + B` — Adds each element of A to the matching element of B. Position (0,0): 1+10=11. Position (0,1): 2+20=22. And so on.
- `B - A` — Subtracts each element of A from B. Position (0,0): 10-1=9.

---

## Scalar Multiplication

A "scalar" is just a single number. Multiplying a matrix by a scalar means multiplying every element by that number.

```
Scalar Multiplication:

    3  x  [ 1  2 ]  =  [ 3x1   3x2 ]  =  [ 3   6 ]
          [ 4  5 ]     [ 3x4   3x5 ]     [ 12  15 ]
```

### Python Code

```python
import numpy as np

A = np.array([[1, 2], [4, 5]])

# Multiply every element by 3
result = 3 * A
print("3 * A =")
print(result)
```

**Expected Output:**
```
3 * A =
[[ 3  6]
 [12 15]]
```

**Line-by-line explanation:**
- `3 * A` — NumPy multiplies every element in A by 3. Simple and clean.

---

## Matrix Multiplication

This is the big one. Matrix multiplication is NOT element-by-element. It follows a special pattern: **row times column**.

### The Rule

To multiply matrix A by matrix B:
- Take a **row** from A
- Take a **column** from B
- Multiply matching elements and add them up
- That sum goes into the result

**Important:** The number of columns in A must equal the number of rows in B.

```
Matrix Multiplication Step by Step:

    A (2x3)              B (3x2)              C (2x2)
    [ 1  2  3 ]     [ 7   10 ]
    [ 4  5  6 ]  x  [ 8   11 ]  =  [ ?  ? ]
                    [ 9   12 ]     [ ?  ? ]

Step 1: Row 1 of A times Column 1 of B

    [ 1  2  3 ]  dot  [ 7 ]
                      [ 8 ]  = 1x7 + 2x8 + 3x9
                      [ 9 ]  = 7 + 16 + 27
                             = 50

    C[0,0] = 50

Step 2: Row 1 of A times Column 2 of B

    [ 1  2  3 ]  dot  [ 10 ]
                      [ 11 ]  = 1x10 + 2x11 + 3x12
                      [ 12 ]  = 10 + 22 + 36
                              = 68

    C[0,1] = 68

Step 3: Row 2 of A times Column 1 of B

    [ 4  5  6 ]  dot  [ 7 ]
                      [ 8 ]  = 4x7 + 5x8 + 6x9
                      [ 9 ]  = 28 + 40 + 54
                             = 122

    C[1,0] = 122

Step 4: Row 2 of A times Column 2 of B

    [ 4  5  6 ]  dot  [ 10 ]
                      [ 11 ]  = 4x10 + 5x11 + 6x12
                      [ 12 ]  = 40 + 55 + 72
                              = 167

    C[1,1] = 167

Result:
    C = [ 50   68  ]
        [ 122  167 ]
```

### Shape Rule for Matrix Multiplication

```
    A         x         B        =        C
(m x n)             (n x p)           (m x p)
              ^
              |
    These must match!

Example:
(2 x 3)  x  (3 x 2)  =  (2 x 2)
      ^       ^
      |       |
      +-------+
      Both are 3. OK!
```

### Python Code

```python
import numpy as np

A = np.array([
    [1, 2, 3],
    [4, 5, 6]
])

B = np.array([
    [7, 10],
    [8, 11],
    [9, 12]
])

# Matrix multiplication
C = np.dot(A, B)
print("A x B =")
print(C)

# Alternative syntax (same result)
C2 = A @ B
print("\nA @ B =")
print(C2)
```

**Expected Output:**
```
A x B =
[[ 50  68]
 [122 167]]

A @ B =
[[ 50  68]
 [122 167]]
```

**Line-by-line explanation:**
- `np.dot(A, B)` — Performs matrix multiplication following the row-times-column rule.
- `A @ B` — The `@` operator does the same thing. It is shorter and easier to read.
- Both give the same result: a 2x2 matrix.

> **Warning:** `A * B` does element-wise multiplication, NOT matrix multiplication. Use `@` or `np.dot()` for real matrix multiplication.

---

## Transpose

The transpose of a matrix flips it. Rows become columns. Columns become rows.

```
Original Matrix A:                  Transpose of A (written A^T):

    [ 1  2  3 ]                        [ 1  4 ]
    [ 4  5  6 ]          --->          [ 2  5 ]
                                       [ 3  6 ]
    (2 x 3)                            (3 x 2)
```

Think of it like rotating the matrix 90 degrees and flipping it.

### Python Code

```python
import numpy as np

A = np.array([
    [1, 2, 3],
    [4, 5, 6]
])

# Transpose
A_T = A.T
print("Original A:")
print(A)
print("Shape:", A.shape)

print("\nTranspose A^T:")
print(A_T)
print("Shape:", A_T.shape)
```

**Expected Output:**
```
Original A:
[[1 2 3]
 [4 5 6]]
Shape: (2, 3)

Transpose A^T:
[[1 4]
 [2 5]
 [3 6]]
Shape: (3, 2)
```

**Line-by-line explanation:**
- `A.T` — Returns the transpose of A. The `.T` is a property, not a function, so no parentheses.
- The shape changes from (2, 3) to (3, 2). Rows and columns swap.

---

## Identity Matrix

The identity matrix is a special square matrix with 1s on the diagonal and 0s everywhere else.

```
2x2 Identity:        3x3 Identity:

    [ 1  0 ]             [ 1  0  0 ]
    [ 0  1 ]             [ 0  1  0 ]
                          [ 0  0  1 ]
```

It is the matrix equivalent of the number 1. Any matrix multiplied by the identity matrix stays the same.

```
    [ 5  3 ]     [ 1  0 ]     [ 5  3 ]
    [ 2  7 ]  x  [ 0  1 ]  =  [ 2  7 ]

    A         x    I       =    A

    Just like:  5  x  1  =  5
```

### Python Code

```python
import numpy as np

# Create a 3x3 identity matrix
I = np.eye(3)
print("Identity matrix:")
print(I)

# Multiply any matrix by identity
A = np.array([[5, 3], [2, 7]])
I2 = np.eye(2)

result = A @ I2
print("\nA x I =")
print(result)
```

**Expected Output:**
```
Identity matrix:
[[1. 0. 0.]
 [0. 1. 0.]
 [0. 0. 1.]]

A x I =
[[5. 3.]
 [2. 7.]]
```

**Line-by-line explanation:**
- `np.eye(3)` — Creates a 3x3 identity matrix. "eye" sounds like "I" for Identity.
- `A @ I2` — Multiplying A by the identity gives back A. The matrix is unchanged.

---

## Inverse of a Matrix

The inverse of a matrix is like division. If you multiply a matrix by its inverse, you get the identity matrix.

```
    A  x  A^(-1)  =  I

    Just like:  5  x  (1/5)  =  1
```

Not every matrix has an inverse. Only square matrices (same number of rows and columns) can have one, and even then, some do not.

### Python Code

```python
import numpy as np

A = np.array([
    [4, 7],
    [2, 6]
])

# Compute the inverse
A_inv = np.linalg.inv(A)
print("A:")
print(A)
print("\nInverse of A:")
print(A_inv)

# Verify: A x A_inv should be the identity matrix
result = A @ A_inv
print("\nA x A_inv (should be identity):")
print(np.round(result, 2))
```

**Expected Output:**
```
A:
[[4 7]
 [2 6]]

Inverse of A:
[[ 0.6 -0.7]
 [-0.2  0.4]]

A x A_inv (should be identity):
[[1. 0.]
 [0. 1.]]
```

**Line-by-line explanation:**
- `np.linalg.inv(A)` — Computes the inverse of matrix A. `linalg` stands for "linear algebra."
- `A @ A_inv` — Multiplying A by its inverse gives the identity matrix. This confirms the inverse is correct.
- `np.round(result, 2)` — Rounds to 2 decimal places. Computers sometimes give tiny errors like 0.0000000001 instead of 0.

---

## Determinant

The determinant is a single number calculated from a square matrix. It tells you important things:

- If the determinant is **zero**, the matrix has **no inverse**
- If the determinant is **not zero**, the matrix **has an inverse**

For a 2x2 matrix, the formula is simple:

```
    [ a  b ]
    [ c  d ]

    Determinant = a*d - b*c

    Example:
    [ 4  7 ]
    [ 2  6 ]

    Determinant = 4*6 - 7*2 = 24 - 14 = 10
```

### Python Code

```python
import numpy as np

A = np.array([[4, 7], [2, 6]])

# Compute the determinant
det = np.linalg.det(A)
print("Matrix A:")
print(A)
print("Determinant:", round(det, 2))

# A matrix with determinant = 0 (no inverse)
B = np.array([[1, 2], [2, 4]])
det_B = np.linalg.det(B)
print("\nMatrix B:")
print(B)
print("Determinant:", round(det_B, 2))
print("B has an inverse?", round(det_B, 2) != 0)
```

**Expected Output:**
```
Matrix A:
[[4 7]
 [2 6]]
Determinant: 10.0

Matrix B:
[[1 2]
 [2 4]]
Determinant: 0.0
B has an inverse? False
```

**Line-by-line explanation:**
- `np.linalg.det(A)` — Computes the determinant of A. The result is 10.
- For matrix B, the determinant is 0. This means B has no inverse. Row 2 is just Row 1 multiplied by 2.

---

## Why Matrices Matter in Machine Learning

In machine learning, your data IS a matrix.

```
A dataset with 4 samples and 3 features:

                   Feature 1    Feature 2    Feature 3
                   (Height)     (Weight)     (Age)
                   ---------    ---------    -----
    Sample 1   |    170          65           25    |
    Sample 2   |    180          80           30    |
    Sample 3   |    160          55           22    |
    Sample 4   |    175          72           28    |

    This is a 4 x 3 matrix.
    4 rows (samples) and 3 columns (features).

    In ML notation:
    - m = number of samples = 4
    - n = number of features = 3
    - X is the data matrix (m x n)
```

When a neural network processes your data:

```
    Input       Weights       Output
    (1 x 3)  x  (3 x 2)   =  (1 x 2)

    [170 65 25]  x  [ w1  w2 ]   =  [ prediction1  prediction2 ]
                    [ w3  w4 ]
                    [ w5  w6 ]

    This is matrix multiplication!
```

### Practical Example: Dataset as a Matrix

```python
import numpy as np

# Create a dataset: 5 students, 3 test scores each
dataset = np.array([
    [90, 85, 92],   # Student 1
    [78, 91, 88],   # Student 2
    [95, 89, 76],   # Student 3
    [62, 74, 80],   # Student 4
    [88, 93, 91]    # Student 5
])

print("Dataset shape:", dataset.shape)
print("Number of students:", dataset.shape[0])
print("Number of tests:", dataset.shape[1])

# Average score for each student (average across columns)
student_averages = np.mean(dataset, axis=1)
print("\nStudent averages:", student_averages)

# Average score for each test (average across rows)
test_averages = np.mean(dataset, axis=0)
print("Test averages:", test_averages)

# Normalize scores (scale to 0-1 range)
min_score = dataset.min()
max_score = dataset.max()
normalized = (dataset - min_score) / (max_score - min_score)
print("\nNormalized dataset:")
print(np.round(normalized, 2))
```

**Expected Output:**
```
Dataset shape: (5, 3)
Number of students: 5
Number of tests: 3

Student averages: [89.         85.66666667 86.66666667 72.         90.66666667]
Test averages: [82.6 86.4 85.4]

Normalized dataset:
[[0.85 0.7  0.91]
 [0.48 0.88 0.79]
 [1.   0.82 0.42]
 [0.   0.36 0.55]
 [0.79 0.94 0.88]]
```

**Line-by-line explanation:**
- `dataset.shape` — Shows (5, 3): 5 students and 3 tests.
- `np.mean(dataset, axis=1)` — `axis=1` means "average across columns" (for each row/student).
- `np.mean(dataset, axis=0)` — `axis=0` means "average across rows" (for each column/test).
- The normalization formula `(x - min) / (max - min)` scales all values to between 0 and 1. This is common in machine learning.

### Visualizing a Matrix as a Heatmap

```python
import numpy as np
import matplotlib.pyplot as plt

# Student scores dataset
dataset = np.array([
    [90, 85, 92],
    [78, 91, 88],
    [95, 89, 76],
    [62, 74, 80],
    [88, 93, 91]
])

# Create a heatmap
plt.figure(figsize=(8, 5))
plt.imshow(dataset, cmap='YlOrRd', aspect='auto')
plt.colorbar(label='Score')
plt.xlabel('Test Number')
plt.ylabel('Student Number')
plt.title('Student Scores as a Matrix Heatmap')
plt.xticks([0, 1, 2], ['Test 1', 'Test 2', 'Test 3'])
plt.yticks([0, 1, 2, 3, 4], ['Student 1', 'Student 2', 'Student 3',
                               'Student 4', 'Student 5'])

# Add score values on each cell
for i in range(5):
    for j in range(3):
        plt.text(j, i, str(dataset[i, j]),
                ha='center', va='center', fontsize=14)

plt.tight_layout()
plt.savefig('matrix_heatmap.png', dpi=100, bbox_inches='tight')
plt.show()
print("Heatmap saved!")
```

**Expected Output:**
```
Heatmap saved!
```

A colorful heatmap appears showing each student's scores. Higher scores appear darker/redder.

---

## Common Mistakes

1. **Confusing `*` with `@` for matrix multiplication.**
   - `A * B` does element-wise multiplication (each element times its match).
   - `A @ B` does real matrix multiplication (row-times-column).
   - These give completely different results!

2. **Wrong shape for multiplication.**
   - You can only multiply A (m x n) by B (n x p). The inner numbers must match.
   - A (2x3) times B (2x3) will cause an error. B needs to be (3x something).

3. **Forgetting that indexing starts at 0.**
   - `matrix[1, 2]` is row 1 (second row), column 2 (third column).

4. **Trying to invert a non-square or singular matrix.**
   - Only square matrices can have inverses.
   - Even some square matrices have no inverse (determinant = 0).

5. **Mixing up rows and columns.**
   - Shape is always (rows, columns). A 3x2 matrix has 3 rows and 2 columns, not the other way around.

---

## Best Practices

1. **Always check shapes before multiplying.** Print `A.shape` and `B.shape` to make sure they are compatible.

2. **Use `@` instead of `np.dot()`.** The `@` operator is cleaner and easier to read.

3. **Use `np.round()` when printing results.** Floating-point math can produce ugly numbers like 0.9999999999. Rounding cleans them up.

4. **Name your matrices meaningfully.** Use `X` for data, `W` for weights, `y` for targets. This follows ML conventions.

5. **Use `np.eye()` to verify inverses.** If `A @ A_inv` gives the identity matrix, your inverse is correct.

---

## Quick Summary

```
Matrix Operations Cheat Sheet:

    Operation          Python Code           Notes
    ---------          -----------           -----
    Create             np.array([[...]])     List of lists
    Zeros              np.zeros((m, n))      All zeros
    Ones               np.ones((m, n))       All ones
    Identity           np.eye(n)             Diagonal 1s
    Shape              A.shape               (rows, cols)
    Add                A + B                 Same shape needed
    Subtract           A - B                 Same shape needed
    Scalar multiply    3 * A                 Every element x 3
    Matrix multiply    A @ B                 Inner dims match
    Transpose          A.T                   Flip rows/cols
    Inverse            np.linalg.inv(A)      Square only
    Determinant        np.linalg.det(A)      Square only
```

---

## Key Points to Remember

1. A matrix is a grid of numbers with rows and columns, just like a spreadsheet.
2. Matrix shape is written as (rows, columns). Always rows first.
3. Matrix addition requires both matrices to have the same shape.
4. Matrix multiplication uses the row-times-column rule, NOT element-by-element.
5. For A @ B to work, the number of columns in A must equal the number of rows in B.
6. The transpose flips rows and columns.
7. The identity matrix is like the number 1 — multiplying by it changes nothing.
8. The inverse is like division — A times its inverse gives the identity.
9. If the determinant is zero, the matrix has no inverse.
10. In machine learning, datasets ARE matrices. Rows are samples. Columns are features.

---

## Practice Questions

1. What is the shape of a matrix with 5 rows and 3 columns? Can you multiply it by a 3x2 matrix? What shape would the result be?

2. Given A = [[1, 2], [3, 4]] and B = [[5, 6], [7, 8]], calculate A + B by hand. Then verify with NumPy.

3. What is the difference between `A * B` and `A @ B` in NumPy? Give an example where they produce different results.

4. Can a 2x3 matrix have an inverse? Why or why not?

5. If a matrix has a determinant of 0, what does that tell you about the matrix?

---

## Exercises

### Exercise 1: Build a Student Dataset

Create a matrix with 6 students and 4 test scores each (make up the numbers). Then:
- Print the shape
- Calculate the average score for each student
- Find the highest score in the entire matrix
- Normalize all scores to the 0-1 range

**Hint:** Use `np.mean()` with `axis=1`, `np.max()`, and the normalization formula.

### Exercise 2: Matrix Multiplication by Hand and Code

Given:
```
A = [[2, 1],     B = [[1, 3],
     [0, 3]]          [2, 1]]
```

1. Calculate A @ B by hand using the row-times-column method
2. Calculate B @ A by hand
3. Verify both with NumPy
4. Are A @ B and B @ A the same? What does this tell you about matrix multiplication?

### Exercise 3: Verify the Inverse

Create any 3x3 matrix of your choice. Compute its inverse with `np.linalg.inv()`. Then multiply the original by the inverse. Verify that you get the identity matrix (use `np.round()` to clean up tiny floating-point errors).

---

## What Is Next?

Now that you understand matrices, you are ready for something powerful. In the next chapter, you will learn about **eigenvalues, eigenvectors, and SVD** — tools that reveal the hidden structure inside matrices. These concepts power dimensionality reduction, recommendation systems, and image compression. They sound intimidating, but we will make them crystal clear.
