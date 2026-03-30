# Chapter 8: Dimensionality Reduction

## What You Will Learn

In this chapter, you will learn:

- What "dimensionality" means and why too many features cause problems
- The Curse of Dimensionality and how it hurts your model
- How PCA (Principal Component Analysis) reduces features while keeping important information
- How to use sklearn PCA step by step
- How to choose the right number of components using cumulative explained variance
- How to visualize high-dimensional data in 2D using PCA
- How t-SNE works for visualization
- When to use PCA versus t-SNE

## Why This Chapter Matters

Imagine you are packing for a trip. You have 100 items you could bring, but your suitcase only fits 20. You need to pick the 20 items that matter most. You leave behind the duplicates and the things you will never use.

Dimensionality reduction does the same thing with data. If your dataset has 100 features (columns), many of them might be redundant or unimportant. Dimensionality reduction shrinks your data down to the features that matter most. Your model trains faster, uses less memory, and often performs better.

Without this skill, you will struggle with datasets that have dozens or hundreds of features. With it, you can simplify complex data and even visualize it in ways that reveal hidden patterns.

---

## 8.1 What Is Dimensionality?

### Dimensions = Features = Columns

In machine learning, each feature in your dataset is one **dimension**. A dataset with 3 features has 3 dimensions. A dataset with 100 features has 100 dimensions.

```
Dimensions in Data
====================

1 Feature  = 1 Dimension  (a line)
   Age: ----[25]--[30]--[35]----

2 Features = 2 Dimensions (a flat surface)
   Salary |
          |     *   *
          |  *     *
          |___________ Age

3 Features = 3 Dimensions (a cube)
   You can still draw this on paper (barely).

4+ Features = 4+ Dimensions
   You CANNOT visualize this.
   But the math still works the same way.
```

### Why More Features Can Be Bad

You might think: "More features means more information. That should be better!" Not always. Here is why.

**Problem 1: Redundant features waste resources.**

If your dataset has "temperature in Celsius" and "temperature in Fahrenheit," those two columns carry the same information. One is enough.

**Problem 2: Irrelevant features add noise.**

If you are predicting house prices and one of your features is "owner's shoe size," that feature adds random noise. It makes the model work harder to find the real patterns.

**Problem 3: Too many features need too much data.**

This is the big one. It is called the Curse of Dimensionality.

---

## 8.2 The Curse of Dimensionality

### The Problem

As you add more dimensions, the amount of data you need grows **exponentially**. With 2 features, 100 data points might be enough. With 20 features, you might need 10,000. With 200 features, you might need millions.

**Think of it like this:** Imagine you are looking for your friend in a building.

```
The Curse of Dimensionality
==============================

1D: Your friend is somewhere on a line (a hallway).
    You search 10 spots. Easy!
    [--*---------]

2D: Your friend is somewhere on a floor (a grid).
    You need 10 x 10 = 100 spots to search.
    [. . . . . . . . . .]
    [. . . * . . . . . .]
    [. . . . . . . . . .]

3D: Your friend is somewhere in a building (a cube).
    You need 10 x 10 x 10 = 1,000 spots.

10D: You need 10^10 = 10,000,000,000 spots!
     Practically impossible to search thoroughly.
```

### What This Means for Machine Learning

```
More dimensions = More empty space = Less reliable predictions

With few dimensions:        With many dimensions:
  Data points are           Data points are
  close together.           far apart.
  Patterns are clear.       Patterns are hidden.

  * * * *                   *
  * * * *                           *
  * * * *                       *
  (Dense, clear)                *         *
                            (Sparse, unclear)
```

When data points are far apart, the model cannot find patterns. It needs more data to fill the space. If you do not have enough data, reducing dimensions is the solution.

### A Code Example: Distance Grows with Dimensions

```python
import numpy as np

# Generate two random points in different dimensions
np.random.seed(42)

for n_dims in [2, 10, 50, 100, 500, 1000]:
    # Two random points in n_dims dimensions
    point_a = np.random.rand(n_dims)
    point_b = np.random.rand(n_dims)

    # Calculate Euclidean distance
    distance = np.sqrt(np.sum((point_a - point_b) ** 2))

    print(f"Dimensions: {n_dims:5d}  |  Distance: {distance:.2f}")
```

**Expected Output:**
```
Dimensions:     2  |  Distance: 0.76
Dimensions:    10  |  Distance: 1.69
Dimensions:    50  |  Distance: 3.91
Dimensions:   100  |  Distance: 5.67
Dimensions:   500  |  Distance: 12.71
Dimensions:  1000  |  Distance: 18.05
```

As dimensions increase, the distance between random points grows. In high dimensions, everything is far from everything else. Algorithms like KNN that rely on distance become unreliable.

---

## 8.3 PCA: Principal Component Analysis

### The Big Idea

PCA finds new directions in your data that capture the most variation. It then keeps only the most important directions and drops the rest.

**Think of it like this:** Imagine you are photographing a long, thin boat from different angles.

```
Photographing a Boat
======================

Top view (most info):        Side view (less info):
  _________________________
 /                         \         ___
|___________________________|       |___|

Front view (least info):
    __
   |  |
   |__|

The top view captures the MOST information about the boat's shape.
PCA finds this "best angle" for your data.
```

PCA looks at all your features and asks: "Which direction captures the most spread (variance) in the data?" That becomes the first **principal component**. Then it asks: "What is the next best direction, perpendicular to the first?" That becomes the second component. And so on.

### PCA Step by Step

```
How PCA Works
===============

Step 1: Center the data (subtract the mean)
Step 2: Find the direction of maximum variance (first component)
Step 3: Find the next direction (perpendicular) of maximum variance
Step 4: Repeat until you have as many components as original features
Step 5: Keep only the top K components
Step 6: Project (transform) data onto those K components

Before PCA (2D):              After PCA (1D):
  y                            PC1
  |    * *                     |
  |  *  *  *                   * * * * * * *
  | * *  *                     |
  |_________ x
                               Most variance is captured
                               in one direction!
```

### Visual Intuition

```
PCA Finds the Best Axis
==========================

Original 2D data:               PCA rotates to find
                                the axis of maximum spread:
   y|     *  *
    |   *  **  *                    /  *  *
    | *  * *  *                    / * ** *
    |  *  *                       / * * *
    |____________ x              /____________

    The data spreads mostly      PC1 (this diagonal) captures
    along a diagonal.            most of the information.

Project onto PC1:
    * *  *** **  * *
    |_________________________ PC1

You went from 2D to 1D and kept most of the information!
```

---

## 8.4 PCA with sklearn

### A Simple Example

```python
import numpy as np
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Create correlated 2D data
np.random.seed(42)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100) * 0.5  # y is correlated with x

data = np.column_stack([x, y])
print("Original data shape:", data.shape)
print("Original data (first 5 rows):")
print(data[:5])
print()

# Apply PCA to reduce from 2D to 1D
pca = PCA(n_components=1)
data_reduced = pca.fit_transform(data)

print("Reduced data shape:", data_reduced.shape)
print("Reduced data (first 5 rows):")
print(data_reduced[:5])
print()

# How much variance is captured?
print(f"Variance explained by PC1: {pca.explained_variance_ratio_[0]:.4f}")
print(f"That means PC1 captures {pca.explained_variance_ratio_[0]*100:.1f}% of the information!")
```

**Expected Output:**
```
Original data shape: (100, 2)
Original data (first 5 rows):
[[ 0.49671415  1.49786506]
 [-0.1382643   0.12387288]
 [ 0.64768854  1.06804547]
 [ 1.52302986  3.43046923]
 [-0.23415337 -0.38013609]]

Reduced data shape: (100, 1)
Reduced data (first 5 rows):
[[-0.70424625]
 [ 0.07551283]
 [-0.47992265]
 [-1.73825973]
 [ 0.21689582]]

Variance explained by PC1: 0.9513
That means PC1 captures 95.1% of the information!
```

**Line-by-line explanation:**

- We created 2D data where `y` is strongly correlated with `x`. This means the two features carry similar information.
- `PCA(n_components=1)` tells PCA to keep only 1 component (reduce from 2D to 1D).
- `fit_transform(data)` learns the principal components and transforms the data in one step.
- `explained_variance_ratio_` tells us how much information each component captures. PC1 captures 95.1%, meaning we lost only 4.9% of the information by going from 2D to 1D.

### PCA on a Larger Dataset

```python
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Load wine dataset (13 features)
wine = load_wine()
X = wine.data
y = wine.target

print(f"Original shape: {X.shape}")
print(f"Number of features: {X.shape[1]}")
print(f"Feature names: {wine.feature_names}")
print()

# Step 1: ALWAYS scale before PCA
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 2: Apply PCA - keep all components first to see variance
pca_full = PCA()
pca_full.fit(X_scaled)

# Show variance explained by each component
print("Variance explained by each component:")
for i, var in enumerate(pca_full.explained_variance_ratio_):
    print(f"  PC{i+1:2d}: {var:.4f} ({var*100:.1f}%)")
```

**Expected Output:**
```
Original shape: (178, 13)
Number of features: 13
Feature names: ['alcohol', 'malic_acid', 'ash', 'alcalinity_of_ash', 'magnesium', 'total_phenols', 'flavanoids', 'nonflavanoid_phenols', 'proanthocyanins', 'color_intensity', 'hue', 'od280/od315_of_diluted_wines', 'proline']

Variance explained by each component:
  PC 1: 0.3620 (36.2%)
  PC 2: 0.1921 (19.2%)
  PC 3: 0.1112 (11.1%)
  PC 4: 0.0707 (7.1%)
  PC 5: 0.0630 (6.3%)
  PC 6: 0.0496 (5.0%)
  PC 7: 0.0394 (3.9%)
  PC 8: 0.0328 (3.3%)
  PC 9: 0.0241 (2.4%)
  PC10: 0.0220 (2.2%)
  PC11: 0.0169 (1.7%)
  PC12: 0.0093 (0.9%)
  PC13: 0.0068 (0.7%)
```

**Important:** Always scale your data before PCA! PCA looks for directions of maximum variance. If one feature has large numbers (e.g., 0 to 1,000,000), it will dominate PCA just because its numbers are big, not because it is important.

---

## 8.5 Choosing the Number of Components

### Cumulative Explained Variance

The key question is: "How many components should I keep?" The answer comes from the **cumulative explained variance** plot.

```python
import numpy as np
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Load and scale
wine = load_wine()
X_scaled = StandardScaler().fit_transform(wine.data)

# Fit PCA with all components
pca = PCA()
pca.fit(X_scaled)

# Calculate cumulative variance
cumulative_variance = np.cumsum(pca.explained_variance_ratio_)

print("Cumulative variance explained:")
print("-" * 40)
for i, cum_var in enumerate(cumulative_variance):
    bar = "#" * int(cum_var * 50)
    marker = " <-- 95% threshold" if i == np.argmax(cumulative_variance >= 0.95) else ""
    print(f"  PC{i+1:2d}: {cum_var:.4f} ({cum_var*100:.1f}%) {bar}{marker}")
```

**Expected Output:**
```
Cumulative variance explained:
----------------------------------------
  PC 1: 0.3620 (36.2%) ##################
  PC 2: 0.5541 (55.4%) ###########################
  PC 3: 0.6653 (66.5%) #################################
  PC 4: 0.7360 (73.6%) ####################################
  PC 5: 0.7990 (79.9%) #######################################
  PC 6: 0.8486 (84.9%) ##########################################
  PC 7: 0.8880 (88.8%) ############################################
  PC 8: 0.9208 (92.1%) ##############################################
  PC 9: 0.9449 (94.5%) ###############################################
  PC10: 0.9669 (96.7%) ################################################ <-- 95% threshold
  PC11: 0.9838 (98.4%) #################################################
  PC12: 0.9932 (99.3%) #################################################
  PC13: 1.0000 (100.0%) ##################################################
```

### The 95% Rule

A common guideline: **keep enough components to explain 95% of the variance.**

```
How to Read the Cumulative Variance
=====================================

Components:  1    2    3    4    5    6    7    8    9    10
Cumulative: 36%  55%  67%  74%  80%  85%  89%  92%  95%  97%
                                                     ^
                                               95% threshold!
                                         Keep 9-10 components.

You went from 13 features to ~10 features.
That is a 23% reduction.
```

### Automatic Component Selection

```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_wine

# Load and scale
wine = load_wine()
X_scaled = StandardScaler().fit_transform(wine.data)

# Let PCA choose: keep 95% of variance
pca_95 = PCA(n_components=0.95)
X_reduced = pca_95.fit_transform(X_scaled)

print(f"Original features:  {X_scaled.shape[1]}")
print(f"Reduced features:   {X_reduced.shape[1]}")
print(f"Variance retained:  {sum(pca_95.explained_variance_ratio_):.4f}")
print(f"Features removed:   {X_scaled.shape[1] - X_reduced.shape[1]}")
```

**Expected Output:**
```
Original features:  13
Reduced features:   10
Variance retained:  0.9669
Features removed:   3
```

**Line-by-line explanation:**

- `PCA(n_components=0.95)` tells PCA to automatically keep enough components to explain 95% of the variance.
- It chose 10 components, reducing from 13 to 10 features while keeping 96.7% of the information.

---

## 8.6 Visualizing Data in 2D with PCA

### Reducing to 2 Components for Plotting

One of the most powerful uses of PCA is visualization. You can reduce any dataset to 2 dimensions and plot it:

```python
import numpy as np
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Load and scale
wine = load_wine()
X_scaled = StandardScaler().fit_transform(wine.data)
y = wine.target

# Reduce to 2D
pca_2d = PCA(n_components=2)
X_2d = pca_2d.fit_transform(X_scaled)

print(f"Original shape: {X_scaled.shape}")
print(f"Reduced shape:  {X_2d.shape}")
print(f"Variance explained: {sum(pca_2d.explained_variance_ratio_):.4f} ({sum(pca_2d.explained_variance_ratio_)*100:.1f}%)")
print()

# Show how the classes separate in 2D
class_names = wine.target_names
for class_idx in range(3):
    mask = y == class_idx
    points = X_2d[mask]
    print(f"Class '{class_names[class_idx]}': {mask.sum()} points")
    print(f"  PC1 range: {points[:, 0].min():.2f} to {points[:, 0].max():.2f}")
    print(f"  PC2 range: {points[:, 1].min():.2f} to {points[:, 1].max():.2f}")
```

**Expected Output:**
```
Original shape: (178, 13)
Reduced shape:  (178, 2)
Variance explained: 0.5541 (55.4%)

Class 'class_0': 59 points
  PC1 range: 1.22 to 5.24
  PC2 range: -3.49 to 3.15
Class 'class_1': 71 points
  PC1 range: -2.98 to 3.39
  PC2 range: -2.79 to 2.83
Class 'class_2': 48 points
  PC1 range: -5.96 to -0.72
  PC2 range: -3.19 to 2.90
```

### ASCII Visualization

```
PCA 2D Visualization of Wine Data
====================================

PC2 (19.2%)
  ^
  3|    0 0
  2|  0 0 0 0        1 1
  1|  0 0 0 0 0   1  1 1 1
  0|   0 0 0 0  1 1 1 1 1    2 2
 -1|    0 0     1 1 1 1 1  2 2 2 2
 -2|      0      1 1 1   2 2 2 2 2
 -3|              1       2 2 2
  -+----+----+----+----+----+----+-> PC1 (36.2%)
  -6   -4   -2    0    2    4    6

0 = class_0 (type 1 wine)
1 = class_1 (type 2 wine)
2 = class_2 (type 3 wine)

Even with just 2 components (55% of info),
the three wine types form distinct clusters!
```

### Creating a Real Plot

```python
import numpy as np
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load, scale, and reduce
wine = load_wine()
X_scaled = StandardScaler().fit_transform(wine.data)
pca_2d = PCA(n_components=2)
X_2d = pca_2d.fit_transform(X_scaled)

# Plot
fig, ax = plt.subplots(figsize=(10, 7))
colors = ['red', 'green', 'blue']
for class_idx in range(3):
    mask = wine.target == class_idx
    ax.scatter(
        X_2d[mask, 0], X_2d[mask, 1],
        c=colors[class_idx],
        label=wine.target_names[class_idx],
        alpha=0.7,
        edgecolors='black',
        linewidth=0.5
    )

ax.set_xlabel(f'PC1 ({pca_2d.explained_variance_ratio_[0]*100:.1f}% variance)')
ax.set_ylabel(f'PC2 ({pca_2d.explained_variance_ratio_[1]*100:.1f}% variance)')
ax.set_title('Wine Dataset - PCA 2D Projection')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('wine_pca_2d.png', dpi=100)
print("Plot saved as wine_pca_2d.png")
```

**Expected Output:**
```
Plot saved as wine_pca_2d.png
```

---

## 8.7 t-SNE for Visualization

### What Is t-SNE?

**t-SNE** stands for **t-distributed Stochastic Neighbor Embedding**. That is a mouthful. Here is what it means in simple terms:

t-SNE is a technique that reduces data to 2D (or 3D) specifically for **visualization**. It is excellent at revealing clusters and groups in your data.

**Think of it like this:** PCA tries to preserve the overall structure (global shape) of your data. t-SNE tries to preserve which points are **neighbors** (local structure). Points that are close together in the original space stay close together in the 2D visualization.

```
PCA vs t-SNE
===============

PCA:                              t-SNE:
  Preserves global structure        Preserves local structure
  (overall spread and shape)        (who is near whom)

  Good for general reduction        Good for finding clusters
  Fast to compute                   Slow to compute
  Deterministic (same result)       Random (different each time)
  Can reduce to any number          Usually only 2D or 3D
  of dimensions                     (for visualization only)
```

### t-SNE with sklearn

```python
import numpy as np
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE

# Load and scale
wine = load_wine()
X_scaled = StandardScaler().fit_transform(wine.data)

# Apply t-SNE
tsne = TSNE(
    n_components=2,      # Reduce to 2D
    random_state=42,     # For reproducibility
    perplexity=30,       # How many neighbors to consider
    n_iter=1000          # Number of iterations
)
X_tsne = tsne.fit_transform(X_scaled)

print(f"Original shape: {X_scaled.shape}")
print(f"t-SNE shape:    {X_tsne.shape}")
print()

# Show cluster separation
for class_idx in range(3):
    mask = wine.target == class_idx
    points = X_tsne[mask]
    center = points.mean(axis=0)
    print(f"Class '{wine.target_names[class_idx]}':")
    print(f"  Center: ({center[0]:.1f}, {center[1]:.1f})")
    print(f"  Points: {mask.sum()}")
```

**Expected Output:**
```
Original shape: (178, 13)
t-SNE shape:    (178, 2)

Class 'class_0':
  Center: (18.2, -3.4)
  Points: 59
Class 'class_1':
  Center: (-15.8, 9.1)
  Points: 71
Class 'class_2':
  Center: (-0.3, -8.5)
  Points: 48
```

**Key parameters explained:**

- `n_components=2`: Reduce to 2 dimensions. t-SNE is almost always used with 2 or 3 components.
- `perplexity=30`: Controls how many neighbors each point considers. Think of it as the "neighborhood size." Try values between 5 and 50. Higher values consider more global structure.
- `n_iter=1000`: How many optimization steps to run. More iterations give better results but take longer.
- `random_state=42`: t-SNE uses randomness. Set this for reproducible results.

### The Perplexity Parameter

The perplexity parameter has a big effect on the result:

```
Effect of Perplexity
======================

Low perplexity (5):           Medium perplexity (30):      High perplexity (50):
  Many small clusters           Balanced view                Broader clusters
  May show false structure      Usually the best choice      May lose detail

   ** **  **                    ****    ****                  *********
  ** ** ** **                   ****    ****                  *********
   ** **  **                    ****    ****                  *********
     **                            ****                      *********

  Too focused on                Just right                   Too focused on
  local detail                                               global structure
```

```python
import numpy as np
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE

wine = load_wine()
X_scaled = StandardScaler().fit_transform(wine.data)

# Try different perplexities
for perp in [5, 15, 30, 50]:
    tsne = TSNE(n_components=2, perplexity=perp, random_state=42, n_iter=1000)
    X_tsne = tsne.fit_transform(X_scaled)

    # Measure cluster separation (distance between class centers)
    centers = []
    for c in range(3):
        mask = wine.target == c
        centers.append(X_tsne[mask].mean(axis=0))

    avg_dist = np.mean([
        np.linalg.norm(centers[i] - centers[j])
        for i in range(3) for j in range(i+1, 3)
    ])

    print(f"Perplexity={perp:2d}: avg distance between cluster centers = {avg_dist:.1f}")
```

**Expected Output:**
```
Perplexity= 5: avg distance between cluster centers = 41.7
Perplexity=15: avg distance between cluster centers = 29.0
Perplexity=30: avg distance between cluster centers = 22.1
Perplexity=50: avg distance between cluster centers = 20.3
```

---

## 8.8 PCA vs t-SNE: When to Use Which

### Side-by-Side Comparison

```
PCA vs t-SNE Comparison
==========================

Feature            PCA                        t-SNE
-------            ---                        -----
Purpose            General reduction          Visualization only
Speed              Very fast                  Slow (especially big data)
Deterministic?     Yes (same result each      No (different each run
                   time)                      unless you set random_state)
Can reduce to      Any number                 2 or 3 (usually 2)
  N dimensions?
Preserves          Global structure           Local structure
                   (distances, variance)      (neighborhoods, clusters)
Can transform      Yes (pca.transform)        No (must refit every time)
  new data?
Use for            Feature reduction +        Exploration and
                   exploration                visualization
Use before         Yes                        No (not for model input)
  modeling?
```

### Decision Guide

```
When Should I Use PCA or t-SNE?
==================================

Do you want to REDUCE FEATURES for a model?
  -> Use PCA.
     t-SNE output should NOT be used as model input.

Do you want to VISUALIZE clusters in your data?
  -> Use t-SNE first. It shows clusters better.
  -> Also try PCA. It is faster and sometimes good enough.

Do you need to TRANSFORM NEW DATA the same way?
  -> Use PCA. It can transform new data.
  -> t-SNE cannot transform new data without refitting.

Is your dataset VERY LARGE (100,000+ rows)?
  -> Use PCA. It handles large data well.
  -> t-SNE is too slow for large datasets.
  -> Alternative: Use PCA to reduce to 50 features first,
     then apply t-SNE on the reduced data.
```

### Combined Example: PCA then t-SNE

For large datasets, a common strategy is to use PCA first to reduce dimensions, then t-SNE for final visualization:

```python
import numpy as np
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# Load and scale
wine = load_wine()
X_scaled = StandardScaler().fit_transform(wine.data)

# Step 1: PCA to reduce from 13 to 5 features
pca = PCA(n_components=5)
X_pca = pca.fit_transform(X_scaled)
print(f"After PCA:  {X_scaled.shape} -> {X_pca.shape}")
print(f"Variance retained: {sum(pca.explained_variance_ratio_)*100:.1f}%")

# Step 2: t-SNE on the PCA-reduced data
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
X_final = tsne.fit_transform(X_pca)
print(f"After t-SNE: {X_pca.shape} -> {X_final.shape}")
print()
print("This 2-step approach is faster than running t-SNE on all 13 features.")
print("PCA removes noise, making t-SNE clusters cleaner.")
```

**Expected Output:**
```
After PCA:  (178, 13) -> (178, 5)
Variance retained: 79.9%
After t-SNE: (178, 5) -> (178, 2)

This 2-step approach is faster than running t-SNE on all 13 features.
PCA removes noise, making t-SNE clusters cleaner.
```

---

## 8.9 Complete Example: Reducing the Digits Dataset

Let's apply everything to a real problem. The digits dataset has images of handwritten digits (0-9). Each image is 8x8 pixels, giving us 64 features. We will reduce them and visualize the results.

```python
import numpy as np
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Load digits dataset
digits = load_digits()
X = digits.data
y = digits.target

print(f"Dataset: {X.shape[0]} images of handwritten digits")
print(f"Features: {X.shape[1]} (8x8 pixel values)")
print(f"Classes: {len(np.unique(y))} digits (0-9)")
print()

# Show what a digit looks like as numbers
print("Digit '3' as an 8x8 grid of pixel values:")
sample_3 = X[y == 3][0].reshape(8, 8)
for row in sample_3:
    print("  ", " ".join(f"{int(v):2d}" for v in row))
```

**Expected Output:**
```
Dataset: 1797 images of handwritten digits
Features: 64 (8x8 pixel values)
Classes: 10 digits (0-9)

Digit '3' as an 8x8 grid of pixel values:
    0  0  7 15 12  0  0  0
    0  0 11 15 15  7  0  0
    0  0  0  0 13  9  0  0
    0  0  4 12 16  7  0  0
    0  0  0  0 13 11  0  0
    0  0  0  0  7 14  0  0
    0  0  6 15 14  1  0  0
    0  0  7 15  5  0  0  0
```

```python
# Scale the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply PCA - see how many components we need
pca_full = PCA()
pca_full.fit(X_scaled)

cumulative = np.cumsum(pca_full.explained_variance_ratio_)

# Find where we hit 90% and 95%
n_90 = np.argmax(cumulative >= 0.90) + 1
n_95 = np.argmax(cumulative >= 0.95) + 1

print(f"Components for 90% variance: {n_90} (out of 64)")
print(f"Components for 95% variance: {n_95} (out of 64)")
print(f"\nThat means we can throw away {64 - n_95} features and keep 95% of the info!")
```

**Expected Output:**
```
Components for 90% variance: 21 (out of 64)
Components for 95% variance: 29 (out of 64)

That means we can throw away 35 features and keep 95% of the info!
```

```python
# Reduce to 2D and visualize
pca_2d = PCA(n_components=2)
X_2d = pca_2d.fit_transform(X_scaled)

print(f"Variance explained by 2 components: {sum(pca_2d.explained_variance_ratio_)*100:.1f}%")
print()

# Show where each digit cluster lands
print("Digit cluster centers in 2D:")
print(f"{'Digit':<8} {'PC1':>8} {'PC2':>8} {'Count':>8}")
print("-" * 35)
for digit in range(10):
    mask = y == digit
    center = X_2d[mask].mean(axis=0)
    print(f"{digit:<8} {center[0]:8.2f} {center[1]:8.2f} {mask.sum():8d}")
```

**Expected Output:**
```
Variance explained by 2 components: 28.5%

Digit cluster centers in 2D:
Digit         PC1      PC2    Count
-----------------------------------
0           -2.17    -2.74      178
1            3.38     2.38      182
2           -0.76     2.85      177
3            0.78     0.31      183
4            0.93    -2.49      181
5           -0.44    -0.98      182
6           -2.99    -0.28      181
7            1.89    -1.37      179
8            0.01     1.80      174
9            0.46     0.15      180
```

```python
# Now try t-SNE for better cluster visualization
from sklearn.manifold import TSNE

# Use PCA first to speed up t-SNE
pca_50 = PCA(n_components=30)
X_pca = pca_50.fit_transform(X_scaled)

tsne = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=1000)
X_tsne = tsne.fit_transform(X_pca)

print("t-SNE cluster centers:")
print(f"{'Digit':<8} {'Dim1':>8} {'Dim2':>8}")
print("-" * 26)
for digit in range(10):
    mask = y == digit
    center = X_tsne[mask].mean(axis=0)
    print(f"{digit:<8} {center[0]:8.1f} {center[1]:8.1f}")

print("\nt-SNE separates the digit clusters much better than PCA!")
print("Each digit forms a tight, distinct group.")
```

**Expected Output:**
```
t-SNE cluster centers:
Digit        Dim1     Dim2
--------------------------
0             9.4    -29.7
1            38.7     13.2
2           -11.2     24.6
3            25.4     26.2
4           -33.3     -2.2
5            14.2      3.5
6           -25.8    -22.5
7            22.3    -17.7
8            -9.2      6.3
9           -14.1    -10.5

t-SNE separates the digit clusters much better than PCA!
Each digit forms a tight, distinct group.
```

---

## Common Mistakes

```
Mistake 1: Forgetting to scale before PCA
-------------------------------------------
WRONG:  pca.fit(X)  where X has features on different scales
RIGHT:  X_scaled = StandardScaler().fit_transform(X)
        pca.fit(X_scaled)
PCA is sensitive to scale! Always standardize first.

Mistake 2: Using t-SNE output as model features
-------------------------------------------
WRONG:  model.fit(X_tsne, y)
RIGHT:  model.fit(X_pca, y)
t-SNE is for VISUALIZATION only. Use PCA for model input.

Mistake 3: Comparing distances in t-SNE plots
-------------------------------------------
WRONG:  "Cluster A is far from Cluster B in t-SNE, so they are very different."
RIGHT:  t-SNE distorts distances. Only NEIGHBORS are meaningful.
        Cluster distances can be misleading.

Mistake 4: Not using PCA before t-SNE on large data
-------------------------------------------
WRONG:  tsne.fit_transform(X)  where X has 500 features
RIGHT:  X_pca = PCA(n_components=50).fit_transform(X)
        tsne.fit_transform(X_pca)
This is faster and often gives better results.

Mistake 5: Fitting PCA on test data
-------------------------------------------
WRONG:  pca.fit_transform(X_test)
RIGHT:  pca.fit(X_train)
        X_train_pca = pca.transform(X_train)
        X_test_pca = pca.transform(X_test)
Fit on training data only. Transform both.
```

---

## Best Practices

1. **Always scale before PCA.** Use `StandardScaler` to standardize your features. Without scaling, features with large numbers dominate PCA.

2. **Use the 95% variance rule as a starting point.** Keep enough components to explain 95% of the variance. Adjust based on your specific needs.

3. **Use PCA for dimensionality reduction in modeling.** If you need to reduce features before training a model, PCA is the right choice.

4. **Use t-SNE for exploration and visualization.** When you want to see if your data has natural clusters, t-SNE is excellent. But never use its output as model input.

5. **Combine PCA and t-SNE for large datasets.** First reduce with PCA to 30-50 dimensions, then apply t-SNE. This is faster and often produces better visualizations.

6. **Try different perplexity values for t-SNE.** The default of 30 is usually good, but experiment with 5, 15, 30, and 50 to see which reveals the most structure.

7. **Fit PCA on training data only.** When building a model, fit PCA on the training set and transform both train and test sets.

8. **Do not over-reduce.** If you reduce too aggressively, you lose important information. Check your model's performance with different numbers of components.

---

## Quick Summary

```
Dimensionality Reduction Summary
===================================

Technique     Purpose              Speed    Best For
---------     -------              -----    --------
PCA           Feature reduction    Fast     Reducing features for models
              + visualization               Removing redundant features
                                            Visualizing in 2D/3D

t-SNE         Visualization only   Slow     Finding clusters
                                            Exploring data structure
                                            Visualizing high-D data in 2D

Key Steps for PCA:
  1. Scale your data (StandardScaler)
  2. Fit PCA on training data
  3. Check cumulative explained variance
  4. Choose components (95% rule or experiment)
  5. Transform data

Key Steps for t-SNE:
  1. Scale your data
  2. (Optional) Reduce with PCA first
  3. Apply t-SNE with n_components=2
  4. Plot the result
  5. Try different perplexity values
```

---

## Key Points

1. **Dimensionality** means the number of features in your dataset. More features can mean more problems (Curse of Dimensionality).

2. **The Curse of Dimensionality** means that as features increase, you need exponentially more data. Distances become meaningless in very high dimensions.

3. **PCA** finds new directions (principal components) that capture the most variance in your data. It can reduce many features to a few while keeping most of the information.

4. **Always scale before PCA.** Features with large numbers will dominate PCA if you skip scaling.

5. **Use cumulative explained variance** to choose the number of components. The 95% rule is a good starting point.

6. **t-SNE** is a visualization technique that preserves local structure (neighborhoods). It is great for finding clusters but should not be used for feature reduction.

7. **PCA for modeling, t-SNE for visualization.** This is the golden rule of dimensionality reduction.

---

## Practice Questions

1. You have a dataset with 200 features and 500 data points. Explain why the Curse of Dimensionality might cause problems. What would you do?

2. After running PCA, the first 5 components explain 42%, 18%, 12%, 8%, and 5% of the variance. What is the cumulative variance after 5 components? Would you keep more?

3. Why must you scale your data before applying PCA? What happens if one feature ranges from 0 to 1,000,000 and another from 0 to 1?

4. You run t-SNE and see two clusters far apart in the 2D plot. Can you conclude that those clusters are truly very different? Why or why not?

5. Explain why you should use PCA output (not t-SNE output) as input features for a machine learning model.

---

## Exercises

### Exercise 1: PCA on Iris Dataset

Load the Iris dataset (`from sklearn.datasets import load_iris`). Scale the data. Apply PCA. Answer: How many components are needed to explain 95% of the variance? Reduce to 2D and print the cluster centers for each species.

### Exercise 2: t-SNE Exploration

Load the digits dataset. Apply t-SNE with perplexity values of 5, 15, 30, and 50. For each, calculate the average distance between cluster centers for all 10 digits. Which perplexity gives the best separation?

### Exercise 3: PCA for Faster Modeling

Load the digits dataset. Train a KNN classifier (K=5) on the full 64 features and measure the accuracy and training time. Then reduce to 20 components with PCA and train KNN again. Compare accuracy and speed. How much faster is the PCA version? How much accuracy did you lose (if any)?

---

## What Is Next?

You now know how to handle too many features. You can reduce dimensions with PCA and visualize complex data with t-SNE. These are essential skills for any data scientist.

In Chapter 9, we dive into our first real machine learning algorithm: **Linear Regression**. You will learn the math behind the famous equation y = mx + b, how to measure prediction quality, and how to build a complete salary prediction model. This is where machine learning truly begins.
