# Chapter 19: K-Means Clustering

## What You Will Learn

In this chapter, you will learn:

- What unsupervised learning is and how it differs from supervised learning
- What clustering means and why it is useful
- How K-Means clustering works step by step
- How to visualize the K-Means algorithm with ASCII diagrams
- How to choose K using the Elbow Method
- What Silhouette Score measures and how to use it
- How to use scikit-learn's KMeans
- How to visualize clusters with scatter plots
- The limitations of K-Means
- How to build a complete customer segmentation project

## Why This Chapter Matters

Until now, every algorithm you learned was **supervised**. You gave the model data AND labels. The model learned to predict labels for new data.

But what if you have **no labels**?

What if you have a pile of customer data and you want to find natural groups? What if you have millions of documents and you want to organize them into topics? What if you have sensor readings and you want to find unusual patterns?

This is where **unsupervised learning** comes in. And K-Means is the most popular and easiest-to-understand unsupervised algorithm. It is used every day by companies for customer segmentation, image compression, anomaly detection, and more.

---

## What Is Unsupervised Learning?

In **supervised learning**, you have a teacher. The teacher gives you questions (features) AND answers (labels). Your job is to learn the pattern so you can answer new questions.

In **unsupervised learning**, there is **no teacher**. You only have the data. No labels. No answers. Your job is to find **structure** and **patterns** on your own.

```
SUPERVISED vs UNSUPERVISED:

SUPERVISED (Chapters 1-18):
  Data:    [age=25, income=50K, city=NYC]  -> Label: "Will Buy"
  Data:    [age=45, income=80K, city=LA]   -> Label: "Won't Buy"
  Data:    [age=35, income=60K, city=CHI]  -> Label: "Will Buy"

  You KNOW the answers. Learn to predict them.


UNSUPERVISED (This chapter):
  Data:    [age=25, income=50K, city=NYC]  -> ???
  Data:    [age=45, income=80K, city=LA]   -> ???
  Data:    [age=35, income=60K, city=CHI]  -> ???

  No answers! Find PATTERNS and GROUPS yourself.
```

### Types of Unsupervised Learning

```
UNSUPERVISED LEARNING:

+-- Clustering (This chapter!)
|     Group similar items together
|     Examples: K-Means, DBSCAN, Hierarchical
|
+-- Dimensionality Reduction
|     Reduce number of features
|     Examples: PCA, t-SNE
|
+-- Association Rules
|     Find items that appear together
|     Example: "People who buy bread also buy butter"
|
+-- Anomaly Detection
      Find unusual data points
      Example: Fraud detection
```

---

## What Is Clustering?

**Clustering** means grouping similar things together.

You do this naturally every day:

```
CLUSTERING IN DAILY LIFE:

Sorting laundry:        Organizing a bookshelf:
  +--------+              +---------+
  | Whites |              | Fiction |
  +--------+              +---------+
  | Colors |              | Science |
  +--------+              +---------+
  | Darks  |              | History |
  +--------+              +---------+

Organizing music:       Grouping friends:
  +------+                +----------+
  | Rock |                | Work     |
  +------+                +----------+
  | Jazz |                | School   |
  +------+                +----------+
  | Pop  |                | Hobbies  |
  +------+                +----------+

You look at items and group SIMILAR ones together.
No one tells you the groups. You figure them out.
```

In machine learning, clustering does the same thing with data. Given a set of data points, a clustering algorithm finds groups where:
- Points **within** a group are similar to each other
- Points in **different** groups are different from each other

---

## How K-Means Works Step by Step

K-Means is the simplest clustering algorithm. The "K" stands for the **number of clusters** you want. You choose K before running the algorithm.

### The Algorithm

```
K-MEANS ALGORITHM:

1. CHOOSE K (number of clusters)
2. PLACE K centroids randomly
3. ASSIGN each point to nearest centroid
4. MOVE centroids to center of their points
5. REPEAT steps 3-4 until centroids stop moving
```

A **centroid** is the center point of a cluster. Think of it as the "average location" of all points in the cluster.

### Step-by-Step Example

Let us trace K-Means with K=2 on simple 2D data.

**Initial Data Points:**
```
     10 |
      9 |     B
      8 |  A     C
      7 |
      6 |
      5 |
      4 |
      3 |        F
      2 |  D  E
      1 |
      0 +--+--+--+--+--+
        0  1  2  3  4  5

  Points: A(1,8), B(2,9), C(3,8),
          D(1,2), E(2,2), F(3,3)
```

### Iteration 1: Place Centroids Randomly

```
     10 |
      9 |     B
      8 |  A  *1 C      * = Centroid
      7 |
      6 |
      5 |
      4 |
      3 |     *2 F
      2 |  D  E
      1 |
      0 +--+--+--+--+--+
        0  1  2  3  4  5

  Centroid 1 placed at (2, 8)
  Centroid 2 placed at (2, 3)
```

### Iteration 1: Assign Points to Nearest Centroid

Each point goes to the nearest centroid:

```
     10 |
      9 |     B .... cluster 1
      8 |  A ..... C
      7 |     (1)          cluster 1: A, B, C
      6 |                  cluster 2: D, E, F
      5 |
      4 |
      3 |     (2) F
      2 |  D ..... E .... cluster 2
      1 |
      0 +--+--+--+--+--+
        0  1  2  3  4  5

  A(1,8) -> Centroid 1 (distance 1.0)  CLUSTER 1
  B(2,9) -> Centroid 1 (distance 1.0)  CLUSTER 1
  C(3,8) -> Centroid 1 (distance 1.0)  CLUSTER 1
  D(1,2) -> Centroid 2 (distance 1.4)  CLUSTER 2
  E(2,2) -> Centroid 2 (distance 1.0)  CLUSTER 2
  F(3,3) -> Centroid 2 (distance 1.0)  CLUSTER 2
```

### Iteration 1: Move Centroids to Cluster Centers

```
     10 |
      9 |     B
      8 |  A  *1 C       Centroid 1: avg of A, B, C
      7 |                  = ((1+2+3)/3, (8+9+8)/3)
      6 |                  = (2.0, 8.3)
      5 |
      4 |
      3 |        F
      2 |  D *2E          Centroid 2: avg of D, E, F
      1 |                  = ((1+2+3)/3, (2+2+3)/3)
      0 +--+--+--+--+--+  = (2.0, 2.3)
        0  1  2  3  4  5
```

### Iteration 2: Reassign Points

With the new centroid positions, we check if any points should switch clusters:

```
     10 |
      9 |     B
      8 |  A  *1 C       All points still assigned
      7 |                 to the same clusters!
      6 |
      5 |                 Centroids barely moved.
      4 |
      3 |        F
      2 |  D *2E          CONVERGED!
      1 |                 (No changes = algorithm stops)
      0 +--+--+--+--+--+
        0  1  2  3  4  5

  FINAL CLUSTERS:
    Cluster 1 (top):    A, B, C  (centroid at 2.0, 8.3)
    Cluster 2 (bottom): D, E, F  (centroid at 2.0, 2.3)
```

The algorithm found two natural groups: the top cluster and the bottom cluster.

### Full Algorithm Animation

```
K-MEANS ANIMATION:

  STEP 1: Random centroids    STEP 2: Assign points
  +---+---+---+---+          +---+---+---+---+
  | .   .         |          | o   o         |
  |         .   . |    =>    |         x   x |
  |   .       .   |          |   o       x   |
  |     * . *     |          |     * . *     |
  +---+---+---+---+          +---+---+---+---+

  STEP 3: Move centroids     STEP 4: Reassign
  +---+---+---+---+          +---+---+---+---+
  | o   o         |          | o   o         |
  |  *      x   x |    =>    |  *      x   x |
  |   o     * x   |          |   o     * x   |
  |       .       |          |       o       |
  +---+---+---+---+          +---+---+---+---+

  STEP 5: Move centroids     DONE! (Converged)
  +---+---+---+---+          +---+---+---+---+
  | o   o         |          | o   o         |
  |  *      x   x |          | *       x   x |
  |   o     * x   |          |   o      *x   |
  |  o            |          |  o            |
  +---+---+---+---+          +---+---+---+---+
```

---

## Choosing K: The Elbow Method

The hardest part of K-Means is choosing K (the number of clusters). How do you know how many groups are in your data?

The **Elbow Method** helps you choose K.

### What Is Inertia?

**Inertia** (also called WCSS -- Within-Cluster Sum of Squares) measures how spread out the points are within their clusters. Lower inertia = tighter, more compact clusters.

```
LOW INERTIA (tight clusters):    HIGH INERTIA (spread out):

  ooo     xxx                    o   o     x   x
  ooo     xxx                       o    x
  ooo     xxx                    o     x    x
                                   o
  Points are close to             Points are far from
  their centroids                 their centroids
```

### The Elbow Method

Run K-Means for K=1, 2, 3, ..., 10. Plot the inertia for each K. Look for the "elbow" -- the point where adding more clusters stops helping much.

```
THE ELBOW METHOD:

Inertia
  |
  |X
  |  \
  |   \
  |    \
  |     \_____         <-- ELBOW here!
  |           \______
  |                  \____
  +--+--+--+--+--+--+--+--> K
     1  2  3  4  5  6  7

  K=1: Very high inertia (everything in one cluster)
  K=2: Much lower (two groups)
  K=3: Lower still
  K=4: Elbow! After this, improvement is small
  K=5+: Only tiny improvements

  Best K = 4 (at the elbow)
```

**Why does it look like an elbow?** Adding the first few clusters makes a big difference (each cluster captures a real group). After a certain point, you are just splitting existing groups unnecessarily, so the improvement shrinks.

```python
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
import numpy as np

# Create sample data with 4 natural clusters
X, _ = make_blobs(n_samples=300, centers=4,
                  cluster_std=1.0, random_state=42)

# Try different values of K
inertias = []
K_range = range(1, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)

# Print the elbow curve
print("Elbow Method Results:")
print("-" * 45)
print(f"{'K':>3s}  {'Inertia':>10s}  {'Drop':>10s}  Plot")
print("-" * 45)

for i, (k, inertia) in enumerate(zip(K_range, inertias)):
    drop = ""
    if i > 0:
        drop = f"{inertias[i-1] - inertia:>10.1f}"
    bar = "=" * int(inertia / max(inertias) * 30)
    print(f"{k:3d}  {inertia:10.1f}  {drop:>10s}  {bar}")

print("\nLook for the 'elbow' -- where the drop becomes small.")
print("The elbow is at K=4 (data has 4 natural clusters).")
```

**Expected Output:**
```
Elbow Method Results:
---------------------------------------------
  K     Inertia        Drop  Plot
---------------------------------------------
  1      3878.5              ==============================
  2      1831.7      2046.8  ==============
  3      1198.3       633.4  =========
  4       574.8       623.5  ====
  5       467.0       107.8  ===
  6       384.6        82.4  ==
  7       323.8        60.8  ==
  8       274.0        49.8  ==
  9       228.2        45.8  =
 10       195.3        32.9  =

Look for the 'elbow' -- where the drop becomes small.
The elbow is at K=4 (data has 4 natural clusters).
```

Notice how the inertia drops dramatically from K=1 to K=4, then the drops become much smaller. K=4 is the elbow.

---

## Silhouette Score

The **Silhouette Score** measures how well each point fits in its cluster. It ranges from -1 to +1.

```
SILHOUETTE SCORE:

  +1.0  Perfect! Point is far from other clusters,
        close to its own cluster.

   0.0  Point is on the boundary between clusters.

  -1.0  Terrible! Point is probably in the WRONG cluster.

VISUALIZATION:

  Score = +0.8:          Score = 0.0:          Score = -0.5:
  ooo  x  xxx            ooo x xxx             ooo xxx x
  ooo     xxx            ooo   xxx             ooo xxx
  ooo     xxx            ooo   xxx             ooo xxx

  x is clearly in        x is between          x is in the
  the right cluster      clusters              WRONG cluster
```

### How Silhouette Score Works

For each point:
1. Calculate **a** = average distance to all other points in the **same** cluster
2. Calculate **b** = average distance to all points in the **nearest** other cluster
3. Silhouette = (b - a) / max(a, b)

```
  If b >> a: (b-a)/b is close to +1 (good!)
     Point is much closer to its cluster than others.

  If a >> b: (b-a)/a is close to -1 (bad!)
     Point is closer to another cluster than its own.
```

```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.datasets import make_blobs

# Create data with 4 clusters
X, _ = make_blobs(n_samples=300, centers=4,
                  cluster_std=1.0, random_state=42)

# Calculate silhouette score for different K
print("Silhouette Scores:")
print("-" * 40)

for k in range(2, 8):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    score = silhouette_score(X, labels)
    bar = "=" * int(score * 40)
    print(f"  K={k}: {score:.4f} {bar}")

print("\nHighest silhouette score = best K")
```

**Expected Output:**
```
Silhouette Scores:
----------------------------------------
  K=2: 0.5817 =======================
  K=3: 0.5516 ======================
  K=4: 0.6870 ===========================
  K=5: 0.5728 ======================
  K=6: 0.5320 =====================
  K=7: 0.5108 ====================

Highest silhouette score = best K
```

K=4 has the highest silhouette score, confirming it is the best choice.

---

## Scikit-Learn KMeans

```python
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
import numpy as np

# Create sample data
X, y_true = make_blobs(
    n_samples=300,    # 300 data points
    centers=4,        # 4 true clusters
    cluster_std=1.0,  # Standard deviation within clusters
    random_state=42
)

# Create and fit KMeans
kmeans = KMeans(
    n_clusters=4,     # We want 4 clusters
    random_state=42,
    n_init=10         # Run 10 times with different seeds
)

# Fit and predict cluster labels
labels = kmeans.fit_predict(X)

# Results
print("K-Means Clustering Results:")
print(f"  Number of clusters: {kmeans.n_clusters}")
print(f"  Inertia (WCSS): {kmeans.inertia_:.2f}")

print(f"\n  Cluster sizes:")
for i in range(4):
    count = sum(labels == i)
    print(f"    Cluster {i}: {count} points")

print(f"\n  Centroid locations:")
for i, centroid in enumerate(kmeans.cluster_centers_):
    print(f"    Cluster {i}: ({centroid[0]:.2f}, {centroid[1]:.2f})")

# Predict cluster for new points
new_points = np.array([[0, 0], [5, 5], [-5, -5]])
new_labels = kmeans.predict(new_points)
print(f"\n  New point predictions:")
for point, label in zip(new_points, new_labels):
    print(f"    Point ({point[0]}, {point[1]}) -> Cluster {label}")
```

**Expected Output:**
```
K-Means Clustering Results:
  Number of clusters: 4
  Inertia (WCSS): 574.80

  Cluster sizes:
    Cluster 0: 75 points
    Cluster 1: 75 points
    Cluster 2: 75 points
    Cluster 3: 75 points

  Centroid locations:
    Cluster 0: (-1.56, 3.00)
    Cluster 1: (-1.72, 7.73)
    Cluster 2: (1.98, 0.96)
    Cluster 3: (5.78, 1.22)

  New point predictions:
    Point (0, 0) -> Cluster 2
    Point (5, 5) -> Cluster 3
    Point (-5, -5) -> Cluster 0
```

### Line-by-Line Explanation

1. **make_blobs**: Creates synthetic data with known clusters. Perfect for testing.
2. **n_clusters=4**: We tell KMeans to find 4 clusters.
3. **n_init=10**: KMeans is sensitive to initial centroid placement. Running it 10 times with different random starts and keeping the best result reduces this problem.
4. **fit_predict**: Fits the model AND returns cluster labels in one step.
5. **inertia_**: The total within-cluster sum of squares. Lower = tighter clusters.
6. **cluster_centers_**: The final centroid positions.
7. **predict**: Assign new points to the nearest centroid.

---

## Visualizing Clusters with Scatter Plots

```python
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
import numpy as np

# Create data
X, y_true = make_blobs(n_samples=300, centers=4,
                        cluster_std=1.0, random_state=42)

# Cluster
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
labels = kmeans.fit_predict(X)
centers = kmeans.cluster_centers_

# ASCII scatter plot
print("Cluster Visualization (ASCII):")
print("=" * 52)

# Create a grid
height, width = 25, 50
grid = [[' ' for _ in range(width)] for _ in range(height)]

# Scale data to grid
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1

symbols = ['o', 'x', '+', '#']

for i, (point, label) in enumerate(zip(X, labels)):
    col = int((point[0] - x_min) / (x_max - x_min) * (width - 1))
    row = int((1 - (point[1] - y_min) / (y_max - y_min)) * (height - 1))
    row = max(0, min(height - 1, row))
    col = max(0, min(width - 1, col))
    grid[row][col] = symbols[label]

# Place centroids
for i, center in enumerate(centers):
    col = int((center[0] - x_min) / (x_max - x_min) * (width - 1))
    row = int((1 - (center[1] - y_min) / (y_max - y_min)) * (height - 1))
    row = max(0, min(height - 1, row))
    col = max(0, min(width - 1, col))
    grid[row][col] = '*'

for row in grid:
    print('  |' + ''.join(row) + '|')

print("  " + "-" * 52)
print(f"\n  Legend: o=Cluster 0  x=Cluster 1  "
      f"+=Cluster 2  #=Cluster 3  *=Centroid")

# Summary statistics
print(f"\n  Cluster Statistics:")
print(f"  {'Cluster':>10s} {'Size':>6s} {'Center X':>10s} {'Center Y':>10s}")
print(f"  {'-'*40}")
for i in range(4):
    mask = labels == i
    print(f"  {'Cluster '+str(i):>10s} {sum(mask):6d} "
          f"{centers[i][0]:10.2f} {centers[i][1]:10.2f}")
```

**Expected Output:**
```
Cluster Visualization (ASCII):
====================================================
  |        xx                                        |
  |         xxx x x                                  |
  |         xxxx                                     |
  |         x*xxxx                                   |
  |          xxxx x                                  |
  |           xx                                     |
  |                                                  |
  |  oo                                              |
  |  oooo o                                          |
  | oooo                                             |
  | oo*ooo                                           |
  |  ooooo                                           |
  |   ooo                                            |
  |                        ++                   ##   |
  |                      +++++                 ####  |
  |                      ++++              ## ###    |
  |                       +*++             ##*###    |
  |                       ++++               ####    |
  |                        ++++               ##     |
  |                        +  +                      |
  |                                                  |
  |                                                  |
  |                                                  |
  |                                                  |
  |                                                  |
  ----------------------------------------------------

  Legend: o=Cluster 0  x=Cluster 1  +=Cluster 2  #=Cluster 3  *=Centroid

  Cluster Statistics:
     Cluster   Size   Center X   Center Y
  ----------------------------------------
   Cluster 0     75      -1.56       3.00
   Cluster 1     75      -1.72       7.73
   Cluster 2     75       1.98       0.96
   Cluster 3     75       5.78       1.22
```

---

## Limitations of K-Means

K-Means is simple and effective, but it has important limitations:

### 1. You Must Choose K in Advance

```
Problem: You must specify K BEFORE running the algorithm.
         But you often don't know K!

Solution: Use Elbow Method and Silhouette Score.
          But these are guidelines, not guarantees.
```

### 2. Assumes Circular (Spherical) Clusters

```
K-Means works well:          K-Means FAILS:

  ooo     xxx                   oooooooooo
  ooo     xxx                   xxxxxxxxxx
  ooo     xxx                   oooooooooo

  Circular clusters             Elongated shapes
  (K-Means is happy)            (K-Means splits them wrong)

  Also FAILS:

    xxxxxxxxxxxx
    x  oooooo  x
    x  oooooo  x
    xxxxxxxxxxxx

    Nested shapes
    (K-Means cannot handle this)
```

### 3. Sensitive to Initialization

```
INITIALIZATION PROBLEM:

Bad initialization:           Good initialization:

  *  o o                        o * o
  o  o *                        o  o   *
         x x                         x x
         x x                         x x

  Centroids placed              Centroids placed
  in wrong spots.               near real centers.
  Bad clusters!                 Good clusters!

Solution: Use n_init=10 (run 10 times, keep best)
```

### 4. Sensitive to Outliers

```
OUTLIER PROBLEM:

Without outlier:              With outlier:

  ooo  *  xxx                  ooo     xxx
  ooo     xxx                  ooo  *  xxx     *
  ooo     xxx                  ooo     xxx
                                                 Z <-- Outlier!

  Good centroid                Centroid pulled toward outlier.
  placement.                   Cluster assignment is wrong.
```

### Limitations Summary

```
+-------------------------+----------------------------+
| Limitation              | Workaround                 |
+-------------------------+----------------------------+
| Must choose K           | Elbow Method, Silhouette   |
| Circular clusters only  | Use DBSCAN (Chapter 20)    |
| Sensitive to init       | n_init=10 (multiple runs)  |
| Sensitive to outliers   | Remove outliers first      |
| Sensitive to scale      | Scale features first       |
+-------------------------+----------------------------+
```

---

## Complete Example: Customer Segmentation

Let us build a complete customer segmentation project. We will group customers based on their spending behavior.

```python
# === COMPLETE K-MEANS CUSTOMER SEGMENTATION ===

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# --------------------------------------------------
# STEP 1: Create Customer Data
# --------------------------------------------------
print("=" * 55)
print("STEP 1: Create Customer Data")
print("=" * 55)

# Simulate customer data
np.random.seed(42)

# Group 1: Young, low income, high online spending
g1_age = np.random.normal(25, 3, 50)
g1_income = np.random.normal(30, 5, 50)
g1_spending = np.random.normal(70, 10, 50)

# Group 2: Middle-aged, high income, high spending
g2_age = np.random.normal(45, 5, 50)
g2_income = np.random.normal(80, 10, 50)
g2_spending = np.random.normal(80, 8, 50)

# Group 3: Older, medium income, low spending
g3_age = np.random.normal(60, 5, 50)
g3_income = np.random.normal(50, 8, 50)
g3_spending = np.random.normal(30, 10, 50)

# Group 4: Young professionals, medium income, medium spending
g4_age = np.random.normal(30, 4, 50)
g4_income = np.random.normal(55, 8, 50)
g4_spending = np.random.normal(50, 10, 50)

# Combine all groups
ages = np.concatenate([g1_age, g2_age, g3_age, g4_age])
incomes = np.concatenate([g1_income, g2_income, g3_income, g4_income])
spendings = np.concatenate([g1_spending, g2_spending, g3_spending,
                            g4_spending])

X = np.column_stack([ages, incomes, spendings])

print(f"Number of customers: {X.shape[0]}")
print(f"Features: Age, Annual Income ($K), Spending Score (0-100)")
print(f"\nSample customers:")
print(f"  {'Customer':>10s} {'Age':>5s} {'Income($K)':>11s} "
      f"{'Spending':>9s}")
print(f"  {'-'*40}")
for i in range(5):
    print(f"  {'#' + str(i+1):>10s} {X[i][0]:5.0f} "
          f"{X[i][1]:11.0f} {X[i][2]:9.0f}")

# --------------------------------------------------
# STEP 2: Scale Features
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 2: Scale Features")
print("=" * 55)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("Before scaling:")
print(f"  Age range:      {X[:, 0].min():.0f} - {X[:, 0].max():.0f}")
print(f"  Income range:   {X[:, 1].min():.0f} - {X[:, 1].max():.0f}")
print(f"  Spending range: {X[:, 2].min():.0f} - {X[:, 2].max():.0f}")
print("\nAfter scaling:")
print(f"  Age range:      {X_scaled[:, 0].min():.2f} - "
      f"{X_scaled[:, 0].max():.2f}")
print(f"  Income range:   {X_scaled[:, 1].min():.2f} - "
      f"{X_scaled[:, 1].max():.2f}")
print(f"  Spending range: {X_scaled[:, 2].min():.2f} - "
      f"{X_scaled[:, 2].max():.2f}")

# --------------------------------------------------
# STEP 3: Find Optimal K (Elbow Method)
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 3: Find Optimal K")
print("=" * 55)

print("\nElbow Method:")
print(f"  {'K':>3s}  {'Inertia':>10s}  {'Silhouette':>11s}  Plot")
print(f"  {'-'*50}")

best_k = 2
best_silhouette = -1

for k in range(2, 9):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    sil_score = silhouette_score(X_scaled, labels)
    bar = "=" * int(kmeans.inertia_ / 10)
    print(f"  {k:3d}  {kmeans.inertia_:10.1f}  {sil_score:11.4f}  {bar}")

    if sil_score > best_silhouette:
        best_silhouette = sil_score
        best_k = k

print(f"\n  Best K by silhouette score: {best_k}")

# --------------------------------------------------
# STEP 4: Run K-Means with Best K
# --------------------------------------------------
print("\n" + "=" * 55)
print(f"STEP 4: Run K-Means with K={best_k}")
print("=" * 55)

kmeans_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
final_labels = kmeans_final.fit_predict(X_scaled)

# Convert centroids back to original scale
centroids_original = scaler.inverse_transform(
    kmeans_final.cluster_centers_
)

print(f"\nFinal clustering complete!")
print(f"Inertia: {kmeans_final.inertia_:.2f}")
print(f"Silhouette Score: "
      f"{silhouette_score(X_scaled, final_labels):.4f}")

# --------------------------------------------------
# STEP 5: Analyze Clusters
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 5: Analyze Customer Segments")
print("=" * 55)

print(f"\n{'Segment':>12s} {'Size':>6s} {'Avg Age':>8s} "
      f"{'Avg Income':>11s} {'Avg Spending':>13s}")
print(f"{'-'*55}")

segment_names = []
for i in range(best_k):
    mask = final_labels == i
    avg_age = X[mask, 0].mean()
    avg_income = X[mask, 1].mean()
    avg_spending = X[mask, 2].mean()

    # Auto-name segments based on characteristics
    if avg_age < 30 and avg_spending > 60:
        name = "Young Spender"
    elif avg_income > 70 and avg_spending > 70:
        name = "High Value"
    elif avg_age > 50 and avg_spending < 40:
        name = "Conservative"
    elif avg_spending > 40 and avg_spending < 60:
        name = "Moderate"
    else:
        name = f"Segment {i}"

    segment_names.append(name)

    print(f"{name:>12s} {sum(mask):6d} {avg_age:8.1f} "
          f"{avg_income:11.1f} {avg_spending:13.1f}")

# --------------------------------------------------
# STEP 6: Visualize Clusters (ASCII)
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 6: Cluster Visualization (Age vs Spending)")
print("=" * 55)

height, width = 20, 50
grid = [[' ' for _ in range(width)] for _ in range(height)]

symbols = ['o', 'x', '+', '#', '@', '%', '&', '!']

ages_data = X[:, 0]
spend_data = X[:, 2]
x_min, x_max = ages_data.min() - 2, ages_data.max() + 2
y_min, y_max = spend_data.min() - 2, spend_data.max() + 2

for point_age, point_spend, label in zip(ages_data, spend_data,
                                          final_labels):
    col = int((point_age - x_min) / (x_max - x_min) * (width - 1))
    row = int((1 - (point_spend - y_min) / (y_max - y_min))
              * (height - 1))
    row = max(0, min(height - 1, row))
    col = max(0, min(width - 1, col))
    grid[row][col] = symbols[label % len(symbols)]

print(f"\n  Spending")
for i, row in enumerate(grid):
    if i == 0:
        print(f"  High |{''.join(row)}|")
    elif i == height - 1:
        print(f"  Low  |{''.join(row)}|")
    else:
        print(f"       |{''.join(row)}|")
print(f"        {'Young':<25s}{'Old':>25s}")
print(f"        {'Age -->':^50s}")

legend = "  Legend: "
for i, name in enumerate(segment_names):
    legend += f"{symbols[i]}={name}  "
print(legend)

# --------------------------------------------------
# STEP 7: Predict New Customers
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 7: Predict New Customer Segments")
print("=" * 55)

new_customers = np.array([
    [22, 25, 85],    # Young, low income, high spending
    [55, 90, 75],    # Older, high income, high spending
    [65, 45, 20],    # Old, low income, low spending
    [28, 60, 55],    # Young professional
])

new_scaled = scaler.transform(new_customers)
new_labels = kmeans_final.predict(new_scaled)

print(f"\n{'Customer':>10s} {'Age':>5s} {'Income':>7s} "
      f"{'Spending':>9s} {'Segment':>15s}")
print(f"{'-'*50}")
for i, (cust, label) in enumerate(zip(new_customers, new_labels)):
    print(f"{'New #' + str(i+1):>10s} {cust[0]:5.0f} "
          f"{cust[1]:7.0f} {cust[2]:9.0f} "
          f"{segment_names[label]:>15s}")

print("\n" + "=" * 55)
print("PROJECT COMPLETE!")
print("=" * 55)
```

**Expected Output:**
```
=======================================================
STEP 1: Create Customer Data
=======================================================
Number of customers: 200
Features: Age, Annual Income ($K), Spending Score (0-100)

Sample customers:
    Customer   Age  Income($K)  Spending
  ----------------------------------------
          #1    26          32        65
          #2    24          29        81
          #3    26          33        76
          #4    30          38        65
          #5    24          29        52

=======================================================
STEP 2: Scale Features
=======================================================
Before scaling:
  Age range:      15 - 73
  Income range:   14 - 107
  Spending range: 3 - 100
After scaling:
  Age range:      -2.44 - 2.43
  Income range:   -2.51 - 2.49
  Spending range: -2.60 - 2.19

=======================================================
STEP 3: Find Optimal K
=======================================================

Elbow Method:
    K     Inertia   Silhouette  Plot
  --------------------------------------------------
    2       340.4       0.3466  ==================================
    3       225.1       0.3751  ======================
    4       150.4       0.4202  ===============
    5       121.8       0.3803  ============
    6       100.5       0.3614  ==========
    7        83.7       0.3465  ========
    8        72.2       0.3384  =======

  Best K by silhouette score: 4

=======================================================
STEP 4: Run K-Means with K=4
=======================================================

Final clustering complete!
Inertia: 150.40
Silhouette Score: 0.4202

=======================================================
STEP 5: Analyze Customer Segments
=======================================================

     Segment   Size  Avg Age  Avg Income  Avg Spending
-------------------------------------------------------
Young Spender     50    25.0         29.7          69.7
  High Value     50    44.8         80.3          79.7
Conservative     50    60.1         50.3          30.0
    Moderate     50    30.0         55.0          50.3

=======================================================
STEP 6: Cluster Visualization (Age vs Spending)
=======================================================

  Spending
  High |  o oo o o       x                            |
       |  ooooo  o      xx x x                        |
       | o ooooo o       x x                          |
       |   oooo o      xxxx                           |
       |  ooooo oo     x xx x                         |
       |   ooooo o      xxx xx                        |
       |  oo   ooo     xx x x                         |
       |    o   o      xxx                             |
       |            + + +xx                            |
       |            + ++++                             |
       |           ++++ +++                            |
       |            + +++ +                            |
       |           +++++++                             |
       |             ++   +                     #      |
       |           +  +                      ## ##     |
       |                                   # # ##     |
       |                                   ######     |
       |                                  # # ### #   |
       |                                    ##  ##    |
  Low  |                                   # ##       |
        Young                                      Old
                              Age -->
  Legend: o=Young Spender  x=High Value  +=Moderate  #=Conservative

=======================================================
STEP 7: Predict New Customer Segments
=======================================================

  Customer   Age  Income  Spending         Segment
--------------------------------------------------
    New #1    22      25       85   Young Spender
    New #2    55      90       75      High Value
    New #3    65      45       20    Conservative
    New #4    28      60       55        Moderate

=======================================================
PROJECT COMPLETE!
=======================================================
```

### What This Project Shows

1. **Feature Scaling**: Essential for K-Means since it uses distances.
2. **Elbow Method + Silhouette**: Both point to K=4 as the best choice.
3. **Clear Segments**: Four distinct customer groups emerged.
4. **Business Value**: Marketing teams can now target each segment differently.
5. **Prediction**: New customers are automatically assigned to the right segment.

---

## Common Mistakes

1. **Forgetting to scale features**
   - Problem: Features with large ranges dominate the distance calculations.
   - Fix: Always use StandardScaler before K-Means.

2. **Using only the Elbow Method to choose K**
   - Problem: The elbow is not always clear.
   - Fix: Combine the Elbow Method with Silhouette Score. Also consider domain knowledge.

3. **Running K-Means only once**
   - Problem: Bad initialization leads to bad clusters.
   - Fix: Use `n_init=10` (or higher) to run multiple times with different initial centroids.

4. **Assuming K-Means always finds the "right" clusters**
   - Problem: K-Means finds circular clusters. If your data has elongated or irregular shapes, it will fail.
   - Fix: Use DBSCAN (Chapter 20) for non-circular clusters.

5. **Not examining the clusters after fitting**
   - Problem: The clusters might not make sense for your domain.
   - Fix: Always analyze and interpret the clusters. Check sizes, means, and distributions.

---

## Best Practices

1. **Always scale your features.** K-Means uses Euclidean distance. Unscaled features will bias the results.

2. **Use n_init=10 or higher.** Multiple initializations dramatically improve results.

3. **Combine Elbow and Silhouette methods.** Neither alone is definitive. Use both.

4. **Analyze your clusters.** Look at cluster statistics. Give them meaningful names. Make sure they make business sense.

5. **Try different K values.** Even if metrics suggest K=4, check what K=3 and K=5 look like. The "best" K depends on your use case.

6. **Visualize when possible.** Scatter plots (2D) help you understand your clusters. Use PCA to reduce to 2D if you have more features.

7. **Consider domain knowledge.** The algorithm finds mathematical groups. But do they make sense for your problem? You are the expert.

---

## Quick Summary

```
K-MEANS IN A NUTSHELL:

  1. Choose K (number of clusters)
  2. Place K centroids randomly
  3. Assign each point to nearest centroid
  4. Move centroids to cluster centers
  5. Repeat until stable

  HOW TO CHOOSE K:
    - Elbow Method (plot inertia vs K)
    - Silhouette Score (higher is better)
    - Domain knowledge

  REMEMBER:
    - Scale features FIRST
    - Use n_init=10+
    - Only finds circular clusters
    - Sensitive to outliers and initialization
```

---

## Key Points to Remember

- **Unsupervised learning** has no labels. The algorithm finds structure on its own.
- **Clustering** groups similar items together.
- **K-Means** finds K clusters by iteratively assigning points to centroids and moving centroids.
- You must **choose K** before running. Use the **Elbow Method** and **Silhouette Score**.
- **Inertia** measures how compact clusters are (lower is better).
- **Silhouette Score** measures how well points fit their clusters (-1 to +1, higher is better).
- **Feature scaling is essential** for K-Means.
- K-Means assumes **circular clusters**. It fails with elongated or nested shapes.
- Use **n_init=10** to reduce sensitivity to initialization.
- Always **analyze and interpret** your clusters to make sure they are meaningful.

---

## Practice Questions

### Question 1
What is the difference between supervised and unsupervised learning?

**Answer:** In supervised learning, the data has labels (known answers), and the algorithm learns to predict those labels for new data. In unsupervised learning, there are no labels. The algorithm must find patterns, groups, or structure in the data on its own. Examples of supervised learning include classification and regression. Examples of unsupervised learning include clustering and dimensionality reduction.

### Question 2
Explain the K-Means algorithm in simple steps.

**Answer:** (1) Choose K, the number of clusters. (2) Place K centroids at random positions. (3) Assign each data point to the nearest centroid. (4) Move each centroid to the center (average) of its assigned points. (5) Repeat steps 3 and 4 until the centroids stop moving (convergence). The result is K groups of similar data points.

### Question 3
What is the Elbow Method and how do you use it?

**Answer:** The Elbow Method helps choose the optimal K for K-Means. You run K-Means for different values of K (e.g., 1 through 10) and record the inertia (within-cluster sum of squares) for each. Then you plot inertia vs K. The plot looks like an arm, and you look for the "elbow" -- the point where adding more clusters stops significantly reducing inertia. This K is usually the best choice.

### Question 4
Why does K-Means require feature scaling?

**Answer:** K-Means uses Euclidean distance to assign points to the nearest centroid. If features have different scales (for example, age 20-70 and income 20,000-100,000), the feature with larger values will dominate the distance calculations. Income differences of thousands would overshadow age differences of tens. Scaling ensures all features contribute equally to the clustering.

### Question 5
What are two limitations of K-Means?

**Answer:** (1) K-Means assumes clusters are circular (spherical). It cannot find elongated, irregular, or nested cluster shapes. (2) K-Means is sensitive to initialization -- poor initial centroid placement can lead to bad clustering results. Other limitations include the need to specify K in advance and sensitivity to outliers.

---

## Exercises

### Exercise 1: Find the Right K
Generate data with `make_blobs(n_samples=500, centers=5, random_state=42)`. Use both the Elbow Method and Silhouette Score to find the optimal K. Do both methods agree?

**Hint:** Try K from 2 to 10 and compare the results.

### Exercise 2: Effect of Scaling
Run K-Means on data where one feature has a much larger range than others (for example, age 20-60 vs salary 20000-100000). Compare results with and without scaling. How does scaling affect the clusters?

**Hint:** Use `StandardScaler` and compare silhouette scores.

### Exercise 3: Iris Clustering
Apply K-Means to the iris dataset (which has 3 known classes). Use K=3. Compare the cluster assignments with the actual labels. How well does K-Means recover the true groups?

**Hint:** Use `from sklearn.metrics import adjusted_rand_score` to compare cluster labels with true labels.

---

## What Is Next?

You now know how to use K-Means to find groups in your data. But K-Means has limitations. It only finds circular clusters and you must choose K.

In the next chapter, you will learn about two more clustering algorithms: **Hierarchical Clustering** and **DBSCAN**. Hierarchical clustering builds a tree of merges, letting you choose different numbers of clusters after the fact. DBSCAN finds clusters of any shape and automatically detects outliers. Together with K-Means, these three algorithms will give you a complete clustering toolkit!
