# Chapter 22: Eigenvalues, Eigenvectors, and SVD — Finding Hidden Structure in Data

## What You Will Learn

- What eigenvalues and eigenvectors are (in plain English)
- How to compute them with NumPy
- What they mean visually
- What Singular Value Decomposition (SVD) is
- How to compute SVD with NumPy
- Why PCA uses eigenvalues for dimensionality reduction
- How these concepts power real AI systems

## Why This Chapter Matters

Imagine you have a dataset with 100 features. That is a lot. Do you really need all 100? Probably not. Some features carry almost no useful information. Some are duplicates of each other.

Eigenvalues and SVD help you find the **most important directions** in your data. They let you:

- **Compress** images without losing much quality
- **Reduce** 100 features down to 10 (dimensionality reduction)
- **Find patterns** hidden in messy data
- **Power** recommendation systems (like Netflix suggestions)

These tools are the math behind PCA, one of the most widely used techniques in machine learning.

---

## What Are Eigenvectors and Eigenvalues?

### The Simple Idea

When you multiply a matrix by a vector, the vector usually changes both its **direction** and its **length**.

But some special vectors only change their **length**, not their **direction**. These special vectors are called **eigenvectors**. The amount the length changes is called the **eigenvalue**.

### Real-Life Analogy

Think of a spinning top. It spins around an axis. Everything on the top is moving and changing direction. But the axis itself? It stays pointing the same way. It does not change direction.

That axis is like an eigenvector. It is a direction that survives the transformation unchanged.

```
A Spinning Top:

         |         <-- This axis does NOT change direction
         |             It is like an eigenvector!
        /|\
       / | \
      /  |  \
     /   |   \       Everything else spins around
    /____|____\
         |
```

### The Math (Kept Simple)

If A is a matrix and v is a vector:

```
    A * v = lambda * v

    Where:
    - A is the matrix (the transformation)
    - v is the eigenvector (direction that doesn't change)
    - lambda is the eigenvalue (how much the length scales)

    Example:
    If lambda = 2, the vector gets stretched to twice its length.
    If lambda = 0.5, it shrinks to half its length.
    If lambda = -1, it flips direction but keeps the same length.
```

### Visual Intuition

```
Regular vector (changes direction AND length):

    Before:      After multiplying by A:
       ^              /
       |             /
       |            /
       |           /
                      (different direction, different length)


Eigenvector (only length changes):

    Before:      After multiplying by A:
       ^              ^
       |              |
       |              |
       |              |
                      |
                      |    (SAME direction, different length)
                           eigenvalue = 2 (doubled in length)
```

---

## Computing Eigenvalues and Eigenvectors with NumPy

```python
import numpy as np

# Create a 2x2 matrix
A = np.array([
    [4, 2],
    [1, 3]
])

# Compute eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(A)

print("Matrix A:")
print(A)
print("\nEigenvalues:", eigenvalues)
print("\nEigenvectors (as columns):")
print(eigenvectors)
```

**Expected Output:**
```
Matrix A:
[[4 2]
 [1 3]]

Eigenvalues: [5. 2.]

Eigenvectors (as columns):
[[ 0.89442719  0.70710678]
 [ 0.44721360 -0.70710678]]
```

**Line-by-line explanation:**
- `np.linalg.eig(A)` — Returns two things: eigenvalues and eigenvectors.
- `eigenvalues` — An array of eigenvalues: [5.0, 2.0].
- `eigenvectors` — Each **column** is an eigenvector. The first column matches the first eigenvalue.

### Verifying: A * v = lambda * v

Let us check that the math works:

```python
import numpy as np

A = np.array([[4, 2], [1, 3]])
eigenvalues, eigenvectors = np.linalg.eig(A)

# Get the first eigenvector and eigenvalue
v1 = eigenvectors[:, 0]    # First column
lambda1 = eigenvalues[0]    # First eigenvalue

print("Eigenvector v1:", v1)
print("Eigenvalue lambda1:", lambda1)

# Check: A @ v1 should equal lambda1 * v1
left_side = A @ v1
right_side = lambda1 * v1

print("\nA @ v1 =", left_side)
print("lambda1 * v1 =", right_side)
print("Are they equal?", np.allclose(left_side, right_side))
```

**Expected Output:**
```
Eigenvector v1: [0.89442719 0.44721360]
Eigenvalue lambda1: 5.0

A @ v1 = [4.47213595 2.23606798]
lambda1 * v1 = [4.47213595 2.23606798]
Are they equal? True
```

**Line-by-line explanation:**
- `eigenvectors[:, 0]` — Gets the first column (first eigenvector).
- `A @ v1` — Multiplying the matrix by the eigenvector.
- `lambda1 * v1` — Scaling the eigenvector by the eigenvalue.
- Both sides are equal. This confirms v1 is truly an eigenvector with eigenvalue 5.

---

## What Eigenvalues Tell You

Eigenvalues tell you how important each direction is.

```
Eigenvalue Interpretation:

    Large eigenvalue  -->  This direction has a LOT of variation
                           (important, keep it!)

    Small eigenvalue  -->  This direction has very LITTLE variation
                           (not important, can drop it)

    Example:
    Eigenvalues: [100, 50, 2, 0.01]

    The first direction captures most of the information.
    The last direction captures almost nothing.
    We could drop the last direction and lose almost no information!
```

This is the core idea behind **PCA** (Principal Component Analysis). Keep the directions with the biggest eigenvalues. Drop the rest. You reduce the number of features but keep most of the information.

---

## Visualizing Eigenvectors

```python
import numpy as np
import matplotlib.pyplot as plt

# Create a matrix
A = np.array([[3, 1], [1, 2]])

# Compute eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(A)

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(8, 8))

# Draw eigenvectors scaled by eigenvalues
colors = ['red', 'blue']
for i in range(2):
    v = eigenvectors[:, i]
    lam = eigenvalues[i]

    # Draw the eigenvector (scaled by eigenvalue for visibility)
    ax.arrow(0, 0, v[0] * lam, v[1] * lam,
             head_width=0.1, head_length=0.1,
             fc=colors[i], ec=colors[i], linewidth=2)
    ax.text(v[0] * lam + 0.1, v[1] * lam + 0.1,
            f'v{i+1} (lambda={lam:.2f})',
            fontsize=12, color=colors[i])

# Generate random points and transform them
np.random.seed(42)
points = np.random.randn(200, 2)
transformed = points @ A.T

ax.scatter(transformed[:, 0], transformed[:, 1],
          alpha=0.3, s=10, color='gray')

ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='k', linewidth=0.5)
ax.axvline(x=0, color='k', linewidth=0.5)
ax.set_title('Eigenvectors Show the Main Directions of the Data')
ax.set_xlabel('x')
ax.set_ylabel('y')

plt.tight_layout()
plt.savefig('eigenvectors_visualization.png', dpi=100, bbox_inches='tight')
plt.show()
print("Plot saved!")
```

**Expected Output:**
```
Plot saved!
```

A scatter plot appears with transformed data points forming an ellipse. Two arrows show the eigenvectors — they point along the main axes of the data cloud.

---

## Singular Value Decomposition (SVD)

SVD is one of the most powerful tools in linear algebra. It breaks **any** matrix into three simpler matrices.

### The Idea

SVD says: any matrix M can be written as:

```
    M  =  U  x  S  x  V^T

    Where:
    - U contains the "left" directions (like eigenvectors for rows)
    - S is a diagonal matrix of "singular values" (importance scores)
    - V^T contains the "right" directions (like eigenvectors for columns)
```

### Real-Life Analogy

Think of SVD like analyzing a recipe:

```
    Full Recipe (M)  =  Ingredients (U)  x  Amounts (S)  x  Techniques (V^T)

    U tells you WHAT to use
    S tells you HOW MUCH of each
    V^T tells you HOW to combine them
```

Or think of it like image compression:

```
    Original Image   =   Shapes  x  Importance  x  Patterns

    Keep only the most important parts.
    You get a smaller image that still looks good!
```

### How SVD Breaks Down a Matrix

```
SVD Decomposition:

    M          =     U        x      S        x     V^T
  (m x n)         (m x m)        (m x n)         (n x n)

  [ . . . ]     [ . . ]       [s1  0  0]     [ . . . ]
  [ . . . ]  =  [ . . ]   x   [ 0 s2  0]  x  [ . . . ]
  [ . . . ]     [ . . ]       [ 0  0 s3]     [ . . . ]
  [ . . . ]     [ . . ]

  The singular values s1, s2, s3 are always positive.
  They are sorted: s1 >= s2 >= s3 >= ...
  Bigger values = more important directions.
```

---

## Computing SVD with NumPy

```python
import numpy as np

# Create a matrix
M = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    [10, 11, 12]
])

# Compute SVD
U, singular_values, Vt = np.linalg.svd(M)

print("Original matrix M:")
print(M)
print("Shape:", M.shape)

print("\nU matrix:")
print(np.round(U, 2))
print("Shape:", U.shape)

print("\nSingular values:")
print(np.round(singular_values, 2))

print("\nV^T matrix:")
print(np.round(Vt, 2))
print("Shape:", Vt.shape)
```

**Expected Output:**
```
Original matrix M:
[[ 1  2  3]
 [ 4  5  6]
 [ 7  8  9]
 [10 11 12]]
Shape: (4, 3)

U matrix:
[[-0.14 -0.83  0.44 -0.31]
 [-0.34 -0.44 -0.24  0.8 ]
 [-0.55 -0.05 -0.69 -0.47]
 [-0.75  0.34  0.52 -0.01]]
Shape: (4, 4)

Singular values:
[25.46  1.29  0.  ]

V^T matrix:
[[-0.5  -0.57 -0.65]
 [-0.76 -0.07  0.65]
 [-0.41  0.82 -0.41]]
Shape: (3, 3)
```

**Line-by-line explanation:**
- `np.linalg.svd(M)` — Returns three things: U, singular values, and V^T.
- `singular_values` — Note that 25.46 is much larger than 1.29 and 0. The first direction captures most of the information.
- The singular values tell you: this matrix mostly has structure in one main direction.

### Reconstructing the Original Matrix from SVD

```python
import numpy as np

M = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    [10, 11, 12]
])

U, singular_values, Vt = np.linalg.svd(M)

# Reconstruct: M = U @ S @ Vt
# First, build the full S matrix
S = np.zeros(M.shape)
np.fill_diagonal(S, singular_values)

# Reconstruct
M_reconstructed = U @ S @ Vt

print("Original M:")
print(M)
print("\nReconstructed M:")
print(np.round(M_reconstructed, 1))
print("\nAre they the same?", np.allclose(M, M_reconstructed))
```

**Expected Output:**
```
Original M:
[[ 1  2  3]
 [ 4  5  6]
 [ 7  8  9]
 [10 11 12]]

Reconstructed M:
[[ 1.  2.  3.]
 [ 4.  5.  6.]
 [ 7.  8.  9.]
 [10. 11. 12.]]

Are they the same? True
```

**Line-by-line explanation:**
- `np.zeros(M.shape)` — Creates a zero matrix the same shape as M.
- `np.fill_diagonal(S, singular_values)` — Places the singular values on the diagonal.
- `U @ S @ Vt` — Multiplying the three matrices gives back the original.
- `np.allclose()` — Checks if two arrays are equal (within floating-point tolerance).

---

## Low-Rank Approximation: Keeping Only the Important Parts

The real power of SVD is that you can keep only the top k singular values and still get a good approximation.

```
Full SVD:         Keep only top 1:

M = U @ S @ Vt    M_approx = U[:,:1] @ S[:1,:1] @ Vt[:1,:]

This is like keeping only the most important "ingredient"
and throwing away the rest.
```

```python
import numpy as np

# Create a more interesting matrix
np.random.seed(42)
M = np.random.rand(5, 4) * 10

U, singular_values, Vt = np.linalg.svd(M)

print("Singular values:", np.round(singular_values, 2))

# Keep only top 2 singular values (out of 4)
k = 2
U_k = U[:, :k]
S_k = np.diag(singular_values[:k])
Vt_k = Vt[:k, :]

M_approx = U_k @ S_k @ Vt_k

print("\nOriginal M:")
print(np.round(M, 1))

print("\nApproximation (k=2):")
print(np.round(M_approx, 1))

# How much information did we keep?
total_info = np.sum(singular_values ** 2)
kept_info = np.sum(singular_values[:k] ** 2)
print(f"\nInformation kept: {kept_info/total_info*100:.1f}%")
```

**Expected Output:**
```
Singular values: [18.08  5.36  2.71  1.6 ]

Original M:
[[3.7 9.5 7.3 6. ]
 [1.6 1.6 0.6 7.1]
 [0.2 8.3 7.8 8.7]
 [2.7 6.7 7.3 2.8]
 [6.7 4.2 7.6 2.5]]

Approximation (k=2):
[[4.  9.6 6.6 6.4]
 [0.7 0.4 2.  6.2]
 [1.3 9.  6.8 9.4]
 [2.5 6.5 7.6 2.6]
 [6.5 4.  7.8 2.4]]

Information kept: 95.8%
```

**Line-by-line explanation:**
- We keep only 2 out of 4 singular values.
- The approximation is very close to the original.
- We kept 95.8% of the information with only half the components!
- This is the idea behind data compression and dimensionality reduction.

---

## Why PCA Uses Eigenvalues

PCA (Principal Component Analysis) is one of the most popular techniques in machine learning. It reduces the number of features in your data while keeping the important information.

Here is how it works:

```
PCA Step by Step:

1. Center the data (subtract the mean)
2. Compute the covariance matrix
3. Find eigenvalues and eigenvectors of the covariance matrix
4. Sort eigenvectors by eigenvalue (largest first)
5. Keep only the top k eigenvectors
6. Project data onto these k directions

    Original Data (100 features)
            |
            v
    Covariance Matrix (100 x 100)
            |
            v
    Eigenvalues: [500, 200, 50, 10, 2, 0.5, ...]
    Eigenvectors: [v1,   v2,  v3, v4, v5, v6, ...]
            |
            v
    Keep top 3: [v1, v2, v3]
            |
            v
    Reduced Data (3 features!)  <-- 100 features -> 3 features
```

### PCA Example in Python

```python
import numpy as np
import matplotlib.pyplot as plt

# Create 2D data with a clear pattern
np.random.seed(42)
n_points = 200

# Data is mostly spread along one direction
x = np.random.randn(n_points) * 3
y = x * 0.5 + np.random.randn(n_points) * 0.5
data = np.column_stack([x, y])

# Step 1: Center the data
mean = np.mean(data, axis=0)
centered = data - mean

# Step 2: Compute covariance matrix
cov_matrix = np.cov(centered.T)
print("Covariance matrix:")
print(np.round(cov_matrix, 2))

# Step 3: Find eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
print("\nEigenvalues:", np.round(eigenvalues, 2))

# Step 4: Sort by eigenvalue (largest first)
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

# How much variance does each component explain?
total_variance = np.sum(eigenvalues)
for i, ev in enumerate(eigenvalues):
    print(f"PC{i+1} explains {ev/total_variance*100:.1f}% of variance")

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Original data with eigenvectors
axes[0].scatter(data[:, 0], data[:, 1], alpha=0.5, s=20)
for i in range(2):
    v = eigenvectors[:, i] * eigenvalues[i]
    axes[0].arrow(mean[0], mean[1], v[0], v[1],
                  head_width=0.2, head_length=0.1,
                  fc=['red', 'blue'][i], ec=['red', 'blue'][i],
                  linewidth=2)
    axes[0].text(mean[0] + v[0] + 0.2, mean[1] + v[1] + 0.2,
                f'PC{i+1}', fontsize=12, color=['red', 'blue'][i])

axes[0].set_title('Original Data with Principal Components')
axes[0].set_xlabel('Feature 1')
axes[0].set_ylabel('Feature 2')
axes[0].set_aspect('equal')
axes[0].grid(True, alpha=0.3)

# Right: Projected onto first principal component
projection = centered @ eigenvectors[:, 0]
axes[1].hist(projection, bins=30, edgecolor='black', alpha=0.7)
axes[1].set_title('Data Projected onto PC1 (1D)')
axes[1].set_xlabel('PC1 Value')
axes[1].set_ylabel('Count')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('pca_visualization.png', dpi=100, bbox_inches='tight')
plt.show()
print("PCA visualization saved!")
```

**Expected Output:**
```
Covariance matrix:
[[8.79 4.14]
 [4.14 2.23]]

Eigenvalues: [10.65 0.37]

PC1 explains 96.6% of variance
PC2 explains 3.4% of variance
PCA visualization saved!
```

The first principal component captures 96.6% of the variance. The second captures only 3.4%. We could reduce from 2D to 1D and barely lose any information.

---

## SVD for Simple Image Compression

```python
import numpy as np
import matplotlib.pyplot as plt

# Create a simple "image" (a matrix of pixel values)
np.random.seed(42)
image = np.random.rand(50, 50) * 255

# Add some structure (horizontal and vertical lines)
for i in range(0, 50, 10):
    image[i, :] = 255
    image[:, i] = 255

# Perform SVD
U, singular_values, Vt = np.linalg.svd(image)

# Reconstruct with different numbers of singular values
fig, axes = plt.subplots(1, 4, figsize=(16, 4))

ranks = [1, 5, 10, 50]
for idx, k in enumerate(ranks):
    U_k = U[:, :k]
    S_k = np.diag(singular_values[:k])
    Vt_k = Vt[:k, :]
    approx = U_k @ S_k @ Vt_k

    axes[idx].imshow(approx, cmap='gray', vmin=0, vmax=255)
    axes[idx].set_title(f'Rank {k}\n({k*50 + k + k*50} values)')
    axes[idx].axis('off')

    # Original needs 50*50 = 2500 values
    # Rank k needs k*50 + k + k*50 = k*(50+1+50) values
    compression = (k * (50 + 1 + 50)) / (50 * 50) * 100
    axes[idx].set_xlabel(f'{compression:.0f}% of original size')

plt.suptitle('SVD Image Compression', fontsize=14)
plt.tight_layout()
plt.savefig('svd_compression.png', dpi=100, bbox_inches='tight')
plt.show()
print("Compression comparison saved!")
```

**Expected Output:**
```
Compression comparison saved!
```

Four images appear side by side showing progressively better quality as more singular values are kept. Even rank 5 (using only 10% of the data) captures the main structure.

---

## Connecting Eigenvalues, SVD, and PCA

```
How They All Connect:

    Eigenvalues/Eigenvectors
           |
           |  "Find the important directions
           |   of a SQUARE matrix"
           |
           v
    Covariance Matrix ---> PCA
           |                |
           |                |  "Reduce features by keeping
           |                |   the most important directions"
           |                v
           |           Reduced Data
           |
    SVD ---+
           |
           |  "Break ANY matrix into
           |   3 simpler parts"
           |
           v
    U x S x V^T

    SVD can do everything eigenvalues can,
    AND it works on non-square matrices too!
```

---

## Common Mistakes

1. **Forgetting that eigenvectors are COLUMNS, not rows.**
   - In NumPy, `eigenvectors[:, 0]` is the first eigenvector (first column).
   - `eigenvectors[0]` gives you the first ROW, which is wrong.

2. **Confusing eigenvalues with singular values.**
   - Eigenvalues can be negative. Singular values are always positive.
   - For a symmetric matrix, singular values = absolute eigenvalues.

3. **Not sorting eigenvalues.**
   - NumPy does not always return them sorted. Sort them yourself if order matters.

4. **Trying eigendecomposition on non-square matrices.**
   - Eigenvalues only work for square matrices. Use SVD for non-square matrices.

5. **Expecting exact reconstruction with low rank.**
   - Low-rank approximation is an approximation. It is close but not perfect.

---

## Best Practices

1. **Use SVD instead of eigendecomposition when possible.** SVD works on any matrix and is more numerically stable.

2. **Check how much variance each component explains.** Keep enough components to capture 95% or more of the total variance.

3. **Always center your data before PCA.** Subtract the mean from each feature.

4. **Use `np.linalg.svd` with `full_matrices=False` for large matrices.** This computes only what you need and saves memory.

5. **Visualize the singular values.** A sharp drop-off tells you how many components you truly need.

---

## Quick Summary

```
Concept                What It Does                        NumPy Function
-------                ------------                        --------------
Eigenvector            Direction unchanged by transform     np.linalg.eig(A)
Eigenvalue             How much it stretches/shrinks        np.linalg.eig(A)
SVD                    Break any matrix into U S Vt         np.linalg.svd(M)
Singular values        Importance of each direction         np.linalg.svd(M)
Low-rank approx        Keep only top k components           Manual slicing
PCA                    Reduce features using eigenvectors   Covariance + eig
```

---

## Key Points to Remember

1. Eigenvectors are special directions that do not change when you apply a matrix transformation. They only get stretched or shrunk.
2. Eigenvalues tell you how much the stretching or shrinking is. Big eigenvalue = important direction.
3. SVD breaks any matrix into three parts: U, S, and V^T. It works on any matrix, not just square ones.
4. Singular values (in S) are always positive and sorted from largest to smallest.
5. You can approximate a matrix by keeping only the top k singular values. This is the basis of data compression.
6. PCA uses eigenvalues of the covariance matrix to find the most important directions in your data.
7. PCA lets you reduce 100 features to 10 while keeping most of the information.
8. SVD is more general and more stable than eigendecomposition. Prefer it in practice.

---

## Practice Questions

1. In plain English, what is an eigenvector? What is an eigenvalue? Give a real-life analogy.

2. If a matrix has eigenvalues [100, 50, 3, 0.01], which eigenvectors would you keep for dimensionality reduction? Why?

3. What are the three matrices in SVD? What does each one represent?

4. Why does PCA require centering the data (subtracting the mean) before computing eigenvalues?

5. Can you compute eigenvalues for a 3x5 matrix? Why or why not? What would you use instead?

---

## Exercises

### Exercise 1: Eigenvalue Exploration

Create a 3x3 matrix of your choice. Compute its eigenvalues and eigenvectors. Then verify the equation A @ v = lambda * v for each eigenvector.

**Hint:** Loop through each eigenvalue-eigenvector pair and check with `np.allclose()`.

### Exercise 2: SVD Compression

Create a 20x20 matrix with some structure (e.g., a pattern of stripes or a gradient). Perform SVD and reconstruct it with k=1, k=3, k=5, and k=20. Calculate how much information (in percent) each reconstruction keeps.

**Hint:** Information kept = sum of squared kept singular values / sum of all squared singular values.

### Exercise 3: Mini-PCA

Generate 200 random 3D data points where two dimensions are correlated and one is random noise. Perform PCA manually (center, covariance, eigendecomposition). How many principal components capture most of the variance? Reduce to 2D and plot the result.

---

## What Is Next?

You now understand how to find hidden structure inside matrices. In the next chapter, we move to a completely different but equally powerful concept: **derivatives**. Derivatives tell you the rate of change of a function — like how fast a car is going at any moment. They are the foundation of how neural networks learn, because finding the best solution means finding where a function stops changing. Let us dive in.
