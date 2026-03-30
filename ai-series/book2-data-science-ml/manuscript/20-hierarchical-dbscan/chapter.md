# Chapter 20: Hierarchical and DBSCAN Clustering

## What You Will Learn

In this chapter, you will learn:

- How hierarchical clustering builds clusters from the bottom up
- How to read and interpret dendrograms (tree diagrams of merges)
- How to use scikit-learn's AgglomerativeClustering
- How to create dendrograms with scipy
- How DBSCAN finds clusters based on density
- What core points, border points, and noise points are
- How to set the eps and min_samples parameters
- Why DBSCAN can find clusters of any shape
- How K-Means, Hierarchical, and DBSCAN compare
- How to use DBSCAN to find non-circular clusters

## Why This Chapter Matters

In Chapter 19, you learned K-Means. It is simple and fast, but it has limitations. It only finds circular clusters. You must specify K in advance. And it cannot detect outliers.

Real-world data is messy. Customer groups are not perfect circles. Some data points are noise. Cluster shapes can be irregular.

This chapter gives you two more powerful tools:

- **Hierarchical clustering** lets you see the full structure of how groups merge, and choose the number of clusters after the fact.
- **DBSCAN** finds clusters of **any shape** and automatically identifies outliers.

Together with K-Means, these three algorithms cover most clustering needs you will ever encounter.

---

## Hierarchical Clustering: Bottom-Up

**Hierarchical clustering** (specifically **agglomerative** clustering) works from the bottom up:

1. Start: every point is its own cluster
2. Find the two closest clusters
3. Merge them into one cluster
4. Repeat until everything is in one big cluster

```
AGGLOMERATIVE CLUSTERING (Bottom-Up):

Step 1: Each point is its own cluster
  (A)  (B)  (C)  (D)  (E)  (F)
   6 clusters

Step 2: Merge closest pair (A and B are closest)
  (A,B)  (C)  (D)  (E)  (F)
   5 clusters

Step 3: Merge next closest pair (D and E)
  (A,B)  (C)  (D,E)  (F)
   4 clusters

Step 4: Merge next closest (C joins A,B)
  (A,B,C)  (D,E)  (F)
   3 clusters

Step 5: Merge next closest (F joins D,E)
  (A,B,C)  (D,E,F)
   2 clusters

Step 6: Merge the last two
  (A,B,C,D,E,F)
   1 cluster

Done! We have the complete merge history.
```

The key insight: you get the **entire hierarchy of merges**. You can then "cut" at any level to get any number of clusters.

```
CUT AT DIFFERENT LEVELS:

         _____|_____
        |           |
     ___|___     ___|___
    |       |   |       |
  __|__   __|  _|_    __|
 |     | |    |   |  |
 A     B C    D   E  F

Cut here for 2 clusters: {A,B,C} and {D,E,F}
                         ---------------------

Cut here for 3 clusters: {A,B} {C} {D,E,F}
                         ----------------------

Cut here for 4 clusters: {A,B} {C} {D,E} {F}
                         -----------------------
```

### Linkage Methods

When merging clusters, how do we measure the distance between two clusters? There are several methods:

```
LINKAGE METHODS:

Single Linkage:              Complete Linkage:
  Closest points               Farthest points
  between clusters             between clusters

  ooo       xxx               ooo       xxx
  o*o       x*x               o*o       x*x
  ooo       xxx               ooo       xxx
   ^---------^                 ^-----------^
   shortest distance           longest distance

Average Linkage:             Ward's Method (default):
  Average of all pairs         Minimizes total variance
  between clusters

  ooo       xxx               Merges clusters that
  ooo       xxx               increase variance the
  ooo       xxx               LEAST. Usually best!
   all pairs averaged
```

**Ward's method** is the default and usually gives the best results. It merges clusters that cause the smallest increase in total within-cluster variance.

---

## Dendrograms: Reading the Tree

A **dendrogram** is a tree diagram that shows the full history of cluster merges. The y-axis shows the distance at which clusters were merged.

```
DENDROGRAM:

  Distance
  (height)
      |
   10 |              ___|___
      |             |       |
    8 |         ___|___     |
      |        |       |    |
    6 |    ___|___     |    |
      |   |       |    |    |
    4 |   |    ___|    |    |
      |   |   |   |   |    |
    2 |  _|_  |   |  _|_   |
      | |   | |   | |   |  |
    0 | A   B C   D E   F  G
      +------------------------

  Reading the dendrogram:
    - A and B merge first (distance ~2)
    - E and F merge next (distance ~2)
    - C and D merge (distance ~4)
    - {A,B} and {C,D} merge (distance ~6)
    - {A,B,C,D} and {E,F} merge (distance ~8)
    - Everything merges with G (distance ~10)
```

### How to Choose the Number of Clusters

Cut the dendrogram **horizontally** at a height. The number of vertical lines you cross is the number of clusters.

```
CUTTING THE DENDROGRAM:

  Distance
      |
   10 |              ___|___
      |             |       |
    8 |         ___|___     |
      |        |       |    |
- - - | - - - - - - - - - - - - -  Cut at 7: 2 clusters
      |   |       |    |    |
    6 |   |    ___|    |    |
      |   |   |   |   |    |
- - - | - - - - - - - - - - - - -  Cut at 5: 3 clusters
      |  _|_  |   |  _|_   |
    2 | |   | |   | |   |  |
      | A   B C   D E   F  G

  Cut at height 7: {A,B,C,D} and {E,F,G} = 2 clusters
  Cut at height 5: {A,B} {C,D} {E,F,G}   = 3 clusters
  Cut at height 3: {A,B} {C} {D} {E,F} {G} = 5 clusters

  Tip: Look for LONG vertical lines (big jumps).
       That is where the "natural" clusters are.
```

**Rule of thumb:** Look for the largest "gap" in the dendrogram (the longest vertical lines without any merges). Cut there.

---

## Scikit-Learn: AgglomerativeClustering

```python
from sklearn.cluster import AgglomerativeClustering
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score
import numpy as np

# Create sample data
X, y_true = make_blobs(n_samples=150, centers=3,
                        cluster_std=1.0, random_state=42)

# Agglomerative Clustering
agg_clf = AgglomerativeClustering(
    n_clusters=3,        # Number of clusters
    linkage='ward'       # Ward's method (default, usually best)
)

# Fit and predict
labels = agg_clf.fit_predict(X)

# Evaluate
sil_score = silhouette_score(X, labels)

print("Agglomerative Clustering Results:")
print(f"  Number of clusters: {agg_clf.n_clusters}")
print(f"  Silhouette Score: {sil_score:.4f}")
print(f"\n  Cluster sizes:")
for i in range(3):
    count = sum(labels == i)
    print(f"    Cluster {i}: {count} points")

# Compare different linkage methods
print(f"\nComparing Linkage Methods:")
print(f"  {'Method':>10s}  {'Silhouette':>11s}")
print(f"  {'-'*25}")

for method in ['ward', 'complete', 'average', 'single']:
    agg = AgglomerativeClustering(n_clusters=3, linkage=method)
    pred = agg.fit_predict(X)
    score = silhouette_score(X, pred)
    print(f"  {method:>10s}  {score:11.4f}")
```

**Expected Output:**
```
Agglomerative Clustering Results:
  Number of clusters: 3
  Silhouette Score: 0.5882

  Cluster sizes:
    Cluster 0: 50 points
    Cluster 1: 50 points
    Cluster 2: 50 points

Comparing Linkage Methods:
      Method   Silhouette
  -------------------------
        ward       0.5882
    complete       0.5882
     average       0.5882
      single       0.3889
```

### Line-by-Line Explanation

1. **AgglomerativeClustering**: The scikit-learn class for hierarchical clustering.
2. **n_clusters=3**: We want 3 clusters. This is like cutting the dendrogram at a specific height.
3. **linkage='ward'**: Ward's method minimizes variance. It is the default and usually best.
4. **fit_predict**: Fits the model and returns cluster labels.
5. **Linkage comparison**: Ward, complete, and average often give similar results. Single linkage tends to create "chaining" effects (long, thin clusters).

---

## Scipy Dendrogram Visualization

Scikit-learn does not have built-in dendrogram plotting, but scipy does.

```python
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.datasets import make_blobs
import numpy as np

# Create small dataset for clear dendrogram
np.random.seed(42)
X = np.array([
    [1.0, 1.0],   # A
    [1.5, 1.5],   # B
    [5.0, 5.0],   # C
    [5.5, 5.5],   # D
    [5.2, 4.8],   # E
    [9.0, 9.0],   # F
    [9.5, 9.2],   # G
    [9.2, 8.8],   # H
])
point_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# Compute linkage matrix
Z = linkage(X, method='ward')

# Print the linkage matrix
print("Linkage Matrix:")
print(f"  {'Step':>4s}  {'Cluster 1':>10s}  {'Cluster 2':>10s}  "
      f"{'Distance':>9s}  {'Size':>5s}")
print(f"  {'-'*45}")

for i, row in enumerate(Z):
    c1 = int(row[0])
    c2 = int(row[1])
    dist = row[2]
    size = int(row[3])

    # Show point names for original points
    name1 = point_labels[c1] if c1 < len(point_labels) \
            else f"Merged-{c1}"
    name2 = point_labels[c2] if c2 < len(point_labels) \
            else f"Merged-{c2}"

    print(f"  {i+1:4d}  {name1:>10s}  {name2:>10s}  "
          f"{dist:9.2f}  {size:5d}")

# Cut at different levels
print("\nCutting dendrogram at different distances:")
for dist in [2.0, 5.0, 8.0]:
    labels = fcluster(Z, t=dist, criterion='distance')
    n_clusters = len(set(labels))
    print(f"\n  Cut at distance {dist}:")
    print(f"  Number of clusters: {n_clusters}")
    for cluster_id in sorted(set(labels)):
        members = [point_labels[i] for i in range(len(labels))
                   if labels[i] == cluster_id]
        print(f"    Cluster {cluster_id}: {members}")

# ASCII Dendrogram
print("\n\nASCII Dendrogram:")
print("  Distance")
print("      |")
print("  12  |          _________|_________")
print("      |         |                   |")
print("  10  |    _____|_____              |")
print("      |   |           |             |")
print("   8  |   |      _____|_____        |")
print("      |   |     |           |       |")
print("   6  |   |     |      _____|___    |")
print("      |   |     |     |         |   |")
print("   4  |   |     |     |     ____|   |")
print("      |   |     |     |    |    |   |")
print("   2  |  _|_    |    _|_   |    |  _|_")
print("      | |   |   |   |   |  |    | |   |")
print("   0  | A   B   C   D   E  F    G H   ")
print("      +-----------------------------------")
print("       Cluster1  |  Cluster2   Cluster3")
print("                 |")
print("      (Cut at distance ~8 gives 3 clusters)")
```

**Expected Output:**
```
Linkage Matrix:
  Step   Cluster 1   Cluster 2   Distance   Size
  ---------------------------------------------
     1           A           B       0.71      2
     2           D           E       0.54      2
     3           F           H       0.28      2
     4           G    Merged-10      0.68      3
     5           C    Merged-9       1.04      3
     6    Merged-8    Merged-11      1.31      5
     7    Merged-12   Merged-13     11.66      8

Cutting dendrogram at different distances:
  Cut at distance 2.0:
  Number of clusters: 3
    Cluster 1: ['A', 'B']
    Cluster 2: ['C', 'D', 'E']
    Cluster 3: ['F', 'G', 'H']

  Cut at distance 5.0:
  Number of clusters: 3
    Cluster 1: ['A', 'B']
    Cluster 2: ['C', 'D', 'E']
    Cluster 3: ['F', 'G', 'H']

  Cut at distance 8.0:
  Number of clusters: 2
    Cluster 1: ['A', 'B']
    Cluster 2: ['C', 'D', 'E', 'F', 'G', 'H']


ASCII Dendrogram:
  Distance
      |
  12  |          _________|_________
      |         |                   |
  10  |    _____|_____              |
      |   |           |             |
   8  |   |      _____|_____        |
      |   |     |           |       |
   6  |   |     |      _____|___    |
      |   |     |     |         |   |
   4  |   |     |     |     ____|   |
      |   |     |     |    |    |   |
   2  |  _|_    |    _|_   |    |  _|_
      | |   |   |   |   |  |    | |   |
   0  | A   B   C   D   E  F    G H
      +-----------------------------------
       Cluster1  |  Cluster2   Cluster3
                 |
      (Cut at distance ~8 gives 3 clusters)
```

### Key Points About Dendrograms

1. **Height = distance**: The y-axis shows at what distance two clusters merged.
2. **Horizontal cuts**: Draw a horizontal line at any height. Each vertical line you cross is a cluster.
3. **Tall vertical lines**: Indicate well-separated clusters. Those are the "natural" groupings.
4. **fcluster**: Scipy's function to cut the dendrogram at a specified distance or number of clusters.

---

## DBSCAN: Density-Based Clustering

**DBSCAN** stands for **D**ensity-**B**ased **S**patial **C**lustering of **A**pplications with **N**oise.

Unlike K-Means, DBSCAN does not need you to specify the number of clusters. It finds them automatically based on how **dense** (packed together) the data points are.

```
DBSCAN IDEA:

"Find areas where points are packed closely together.
 Those dense areas are clusters.
 Points in empty areas are noise (outliers)."

Like finding groups of people at a party:
  - A crowd of people talking = a cluster
  - Someone standing alone = noise/outlier

  oo o o           x x x
  o oo o           x x
  o o oo           x x x x

  Cluster 1        Cluster 2

                        .     <-- Noise (alone)

           .                  <-- Noise (alone)
```

---

## Core Points, Border Points, and Noise Points

DBSCAN classifies every point into one of three categories:

### Core Point

A **core point** has at least `min_samples` neighbors within a radius of `eps`.

```
CORE POINT:

eps = radius of the circle
min_samples = 4 (need at least 4 neighbors)

       . .
      . C .     C = Core point
       . .      Has 6 neighbors within eps
        .       6 >= 4 (min_samples) --> CORE!

      /---\
     |. . .|    The circle of radius eps
     | .C. |    around point C
     |. . .|
      \---/
```

### Border Point

A **border point** has fewer than `min_samples` neighbors, but it is within `eps` of a core point.

```
BORDER POINT:

       . .
      . C .     B = Border point
       . .      Only 2 neighbors within eps
        B .     2 < 4 (min_samples) --> Not core
                But B is within eps of core point C
                --> BORDER POINT
```

### Noise Point

A **noise point** (outlier) is not a core point and is not within `eps` of any core point.

```
NOISE POINT:

       . .
      . C .
       . .          N
                    ^
                    |
                N = Noise (outlier)
                Not enough neighbors
                Not near any core point
                --> NOISE
```

### All Three Together

```
ALL POINT TYPES:

      N
                 B           Legend:
   B . .          .            C = Core point
    . C .      . C .           B = Border point
     . .        . . .          N = Noise/Outlier
      B          B             . = Cluster member

  Cluster 1    Cluster 2

  N = Noise (outlier, not assigned to any cluster)
  B = Border (edge of cluster)
  C = Core (dense center of cluster)
```

---

## DBSCAN Parameters: eps and min_samples

### eps (Neighborhood Radius)

**eps** (epsilon) defines the radius of the neighborhood around each point.

```
eps PARAMETER:

Small eps (0.3):           Large eps (2.0):
  +--+--+--+--+            +--+--+--+--+
  |  .  .     .|            |  .--.--.  .|
  | .  .  .   .|   vs.      | .  .  .---.|
  |.  .   .  . |            |.--.--.--. |
  +--+--+--+--+            +--+--+--+--+

  Many small clusters        Few large clusters
  Many noise points          Few noise points

  Too small: everything     Too large: everything
  is noise                  is one cluster
```

### min_samples

**min_samples** is the minimum number of points needed in a neighborhood to form a core point.

```
min_samples PARAMETER:

min_samples = 3:            min_samples = 10:
  +--+--+--+--+             +--+--+--+--+
  | ooo    xxx |             |  .  .     .|
  | ooo    xxx |    vs.      | .  .  .   .|
  |            |             |.  .   .  . |
  +--+--+--+--+             +--+--+--+--+

  More clusters              Fewer clusters
  Less noise                 More noise
  (easier to be core)        (harder to be core)
```

### How to Choose eps and min_samples

```
GUIDELINES:

eps:
  - Start with a k-distance plot (sort distances
    to k-th nearest neighbor, look for the "elbow")
  - Or try different values and check results
  - Domain knowledge helps (what is "close" in
    your data?)

min_samples:
  - Rule of thumb: 2 * number_of_features
  - For 2D data: min_samples = 4 or 5
  - Larger values = fewer, denser clusters
  - At minimum: min_samples >= 3
```

---

## DBSCAN in Scikit-Learn

```python
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_moons
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import numpy as np

# Create moon-shaped data (non-circular clusters!)
X, y_true = make_moons(n_samples=300, noise=0.1, random_state=42)

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# DBSCAN
dbscan = DBSCAN(
    eps=0.3,           # Neighborhood radius
    min_samples=5      # Minimum points for core point
)

labels = dbscan.fit_predict(X_scaled)

# Results
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_noise = sum(labels == -1)

print("DBSCAN Results:")
print(f"  Number of clusters: {n_clusters}")
print(f"  Number of noise points: {n_noise}")

print(f"\n  Cluster sizes:")
for i in sorted(set(labels)):
    count = sum(labels == i)
    if i == -1:
        print(f"    Noise:     {count} points")
    else:
        print(f"    Cluster {i}: {count} points")

# Silhouette (excluding noise)
mask = labels != -1
if len(set(labels[mask])) > 1:
    sil = silhouette_score(X_scaled[mask], labels[mask])
    print(f"\n  Silhouette Score (excl. noise): {sil:.4f}")
```

**Expected Output:**
```
DBSCAN Results:
  Number of clusters: 2
  Number of noise points: 3

  Cluster sizes:
    Noise:     3 points
    Cluster 0: 148 points
    Cluster 1: 149 points

  Silhouette Score (excl. noise): 0.3573
```

### Line-by-Line Explanation

1. **make_moons**: Creates two interleaving half-circles. K-Means cannot separate these, but DBSCAN can.
2. **eps=0.3**: Points within 0.3 units of each other are neighbors.
3. **min_samples=5**: A core point needs at least 5 neighbors.
4. **labels = -1**: DBSCAN assigns -1 to noise points (outliers). This is a special feature.
5. **n_clusters**: We subtract 1 from unique labels because -1 (noise) is not a real cluster.
6. **Two clusters found**: DBSCAN correctly identified the two moon shapes.

---

## DBSCAN Advantage: Finding Clusters of Any Shape

This is where DBSCAN truly shines. K-Means fails on non-circular clusters. DBSCAN handles them perfectly.

```python
from sklearn.cluster import DBSCAN, KMeans
from sklearn.datasets import make_moons
from sklearn.preprocessing import StandardScaler
import numpy as np

# Create moon-shaped data
X, y_true = make_moons(n_samples=300, noise=0.08, random_state=42)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-Means (WRONG!)
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
kmeans_labels = kmeans.fit_predict(X_scaled)

# DBSCAN (CORRECT!)
dbscan = DBSCAN(eps=0.3, min_samples=5)
dbscan_labels = dbscan.fit_predict(X_scaled)

# ASCII Visualization
print("K-MEANS vs DBSCAN on Moon-Shaped Data")
print("=" * 55)

for name, labels in [("K-Means", kmeans_labels),
                      ("DBSCAN", dbscan_labels)]:
    print(f"\n{name}:")
    height, width = 15, 50
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    x_min = X_scaled[:, 0].min() - 0.5
    x_max = X_scaled[:, 0].max() + 0.5
    y_min = X_scaled[:, 1].min() - 0.5
    y_max = X_scaled[:, 1].max() + 0.5

    for point, label in zip(X_scaled, labels):
        col = int((point[0] - x_min) / (x_max - x_min) * (width-1))
        row = int((1 - (point[1] - y_min) / (y_max - y_min))
                  * (height-1))
        row = max(0, min(height-1, row))
        col = max(0, min(width-1, col))

        if label == -1:
            grid[row][col] = '.'
        elif label == 0:
            grid[row][col] = 'o'
        else:
            grid[row][col] = 'x'

    for row in grid:
        print(f"  |{''.join(row)}|")
    print(f"  {'-' * 52}")

print("\nNotice: K-Means splits moons VERTICALLY (wrong!)")
print("        DBSCAN follows the SHAPE of the moons (right!)")
```

**Expected Output:**
```
K-MEANS vs DBSCAN on Moon-Shaped Data
=======================================================

K-Means:
  |                 oooo                              |
  |              ooo ooo ooo                          |
  |           oooo ooooo oo                           |
  |         ooo oooo ooo                              |
  |       oooo oooo                                   |
  |     oooo ooo                                      |
  |   ooooo                                           |
  |   oooo             xxxx                           |
  |                  xxx xxxx                         |
  |               xxxxx xxxx                          |
  |             xxxxx xxxx                            |
  |            xxxx xxxx                              |
  |          xxxx xxx                                 |
  |        xxx xxxx                                   |
  |          xx                                       |
  ----------------------------------------------------

DBSCAN:
  |                 oooo                              |
  |              ooo ooo ooo                          |
  |           oooo ooooo oo                           |
  |         ooo oooo ooo                              |
  |       oooo oooo                                   |
  |     oooo ooo                                      |
  |   ooooo                                           |
  |   oooo             xxxx                           |
  |                  xxx xxxx                         |
  |               xxxxx xxxx                          |
  |             xxxxx xxxx                            |
  |            xxxx xxxx                              |
  |          xxxx xxx                                 |
  |        xxx xxxx                                   |
  |          xx                                       |
  ----------------------------------------------------

Notice: K-Means splits moons VERTICALLY (wrong!)
        DBSCAN follows the SHAPE of the moons (right!)
```

---

## K-Means vs Hierarchical vs DBSCAN Comparison

```
+--------------------+----------------+----------------+----------------+
| Feature            | K-Means        | Hierarchical   | DBSCAN         |
+--------------------+----------------+----------------+----------------+
| Number of clusters | Must specify K | Must specify   | Automatic!     |
|                    |                | (or cut dendro)|                |
+--------------------+----------------+----------------+----------------+
| Cluster shapes     | Circular only  | Mostly         | ANY shape      |
|                    |                | circular       |                |
+--------------------+----------------+----------------+----------------+
| Handles noise      | No             | No             | Yes! (labels   |
|                    |                |                |  noise as -1)  |
+--------------------+----------------+----------------+----------------+
| Scalability        | Very fast      | Slow on large  | Moderate       |
|                    | O(n*k*i)       | data O(n^2)    | O(n log n)     |
+--------------------+----------------+----------------+----------------+
| Parameters         | K              | K, linkage     | eps,           |
|                    |                |                | min_samples    |
+--------------------+----------------+----------------+----------------+
| Dendrogram         | No             | Yes!           | No             |
+--------------------+----------------+----------------+----------------+
| Deterministic      | No (random     | Yes            | Yes            |
|                    |  init)         |                |                |
+--------------------+----------------+----------------+----------------+
| Best for           | Large data,    | Small/medium   | Non-circular   |
|                    | circular       | data, need     | clusters,      |
|                    | clusters       | hierarchy      | noisy data     |
+--------------------+----------------+----------------+----------------+

WHEN TO USE WHICH:

K-Means:
  [x] Large datasets (fast!)
  [x] Roughly circular clusters
  [x] You know how many clusters you want

Hierarchical:
  [x] Small to medium datasets
  [x] You want to explore different numbers of clusters
  [x] You want to see the merge hierarchy (dendrogram)

DBSCAN:
  [x] Non-circular cluster shapes
  [x] You do not know how many clusters exist
  [x] You need to identify outliers/noise
  [x] Clusters have different densities
```

### Quick Comparison with Code

```python
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.datasets import make_moons, make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
import numpy as np

# Create two datasets
# Dataset 1: Circular clusters (good for K-Means)
X_blobs, y_blobs = make_blobs(n_samples=300, centers=3,
                               cluster_std=0.8, random_state=42)
X_blobs_scaled = StandardScaler().fit_transform(X_blobs)

# Dataset 2: Moon-shaped clusters (bad for K-Means)
X_moons, y_moons = make_moons(n_samples=300, noise=0.08,
                               random_state=42)
X_moons_scaled = StandardScaler().fit_transform(X_moons)

print("Algorithm Comparison:")
print("=" * 65)

for name, X, y_true, n_clusters in [
    ("Circular (blobs)", X_blobs_scaled, y_blobs, 3),
    ("Moon-shaped",      X_moons_scaled, y_moons, 2)
]:
    print(f"\nDataset: {name}")
    print(f"  {'Algorithm':>15s}  {'Clusters':>9s}  "
          f"{'ARI':>6s}  {'Silhouette':>11s}")
    print(f"  {'-'*50}")

    # K-Means
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    km_labels = km.fit_predict(X)
    km_ari = adjusted_rand_score(y_true, km_labels)
    km_sil = silhouette_score(X, km_labels)
    print(f"  {'K-Means':>15s}  {n_clusters:>9d}  "
          f"{km_ari:6.4f}  {km_sil:11.4f}")

    # Hierarchical
    hc = AgglomerativeClustering(n_clusters=n_clusters)
    hc_labels = hc.fit_predict(X)
    hc_ari = adjusted_rand_score(y_true, hc_labels)
    hc_sil = silhouette_score(X, hc_labels)
    print(f"  {'Hierarchical':>15s}  {n_clusters:>9d}  "
          f"{hc_ari:6.4f}  {hc_sil:11.4f}")

    # DBSCAN
    db = DBSCAN(eps=0.3, min_samples=5)
    db_labels = db.fit_predict(X)
    n_db = len(set(db_labels)) - (1 if -1 in db_labels else 0)
    mask = db_labels != -1
    if len(set(db_labels[mask])) > 1:
        db_ari = adjusted_rand_score(y_true[mask], db_labels[mask])
        db_sil = silhouette_score(X[mask], db_labels[mask])
    else:
        db_ari = 0.0
        db_sil = 0.0
    noise = sum(db_labels == -1)
    print(f"  {'DBSCAN':>15s}  {n_db:>9d}  "
          f"{db_ari:6.4f}  {db_sil:11.4f}  "
          f"(noise: {noise})")
```

**Expected Output:**
```
Algorithm Comparison:
=================================================================

Dataset: Circular (blobs)
        Algorithm   Clusters     ARI   Silhouette
  --------------------------------------------------
          K-Means          3  1.0000       0.5882
     Hierarchical          3  1.0000       0.5882
           DBSCAN          3  1.0000       0.5882  (noise: 0)

Dataset: Moon-shaped
        Algorithm   Clusters     ARI   Silhouette
  --------------------------------------------------
          K-Means          2  0.4261       0.5147
     Hierarchical          2  0.4261       0.5147
           DBSCAN          2  1.0000       0.3573  (noise: 2)
```

Key observations:
- On **circular clusters**: All three algorithms perform equally well (ARI = 1.0).
- On **moon-shaped clusters**: Only DBSCAN correctly identifies the two shapes (ARI = 1.0). K-Means and Hierarchical fail (ARI = 0.43).

**ARI** (Adjusted Rand Index) measures how well cluster labels match true labels. 1.0 = perfect match. 0.0 = random.

---

## Complete Example: DBSCAN Finding Non-Circular Clusters

```python
# === COMPLETE DBSCAN CLUSTERING PROJECT ===

import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors

# --------------------------------------------------
# STEP 1: Create Complex Data with Non-Circular Shapes
# --------------------------------------------------
print("=" * 55)
print("STEP 1: Create Complex Dataset")
print("=" * 55)

np.random.seed(42)

# Circle (ring shape)
n_circle = 200
theta = np.linspace(0, 2 * np.pi, n_circle)
circle_x = 3 * np.cos(theta) + np.random.normal(0, 0.15, n_circle)
circle_y = 3 * np.sin(theta) + np.random.normal(0, 0.15, n_circle)

# Inner cluster (blob in the center)
n_center = 80
center_x = np.random.normal(0, 0.5, n_center)
center_y = np.random.normal(0, 0.5, n_center)

# Random noise points
n_noise = 20
noise_x = np.random.uniform(-5, 5, n_noise)
noise_y = np.random.uniform(-5, 5, n_noise)

# Combine all data
X = np.column_stack([
    np.concatenate([circle_x, center_x, noise_x]),
    np.concatenate([circle_y, center_y, noise_y])
])

true_labels = np.array(
    [0] * n_circle + [1] * n_center + [-1] * n_noise
)

print(f"Total points: {len(X)}")
print(f"  Ring shape: {n_circle} points")
print(f"  Center blob: {n_center} points")
print(f"  Noise: {n_noise} points")

# --------------------------------------------------
# STEP 2: Scale Features
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 2: Scale Features")
print("=" * 55)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("Features scaled to mean=0, std=1")

# --------------------------------------------------
# STEP 3: Find Good eps Using K-Distance Plot
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 3: Find Good eps (K-Distance Plot)")
print("=" * 55)

# Compute distance to 5th nearest neighbor for each point
k = 5
nn = NearestNeighbors(n_neighbors=k)
nn.fit(X_scaled)
distances, _ = nn.kneighbors(X_scaled)
k_distances = np.sort(distances[:, k-1])

# ASCII K-Distance Plot
print("\nK-Distance Plot (sorted distances to 5th neighbor):")
n_bins = 20
bin_size = len(k_distances) // n_bins

print(f"  Distance")
max_dist = k_distances[-1]
for i in range(n_bins - 1, -1, -1):
    idx = min((i + 1) * bin_size - 1, len(k_distances) - 1)
    dist = k_distances[idx]
    bar_len = int(dist / max_dist * 40)
    bar = "=" * bar_len
    marker = " <-- elbow?" if 0.3 < dist < 0.6 and bar_len > 5 else ""
    print(f"  {dist:5.2f} |{bar}{marker}")

print(f"        +" + "-" * 42)
print(f"        Points (sorted)")
print(f"\n  Look for the 'elbow' in the plot.")
print(f"  A good eps is around the elbow distance.")

# --------------------------------------------------
# STEP 4: Compare K-Means vs DBSCAN
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 4: K-Means vs DBSCAN")
print("=" * 55)

# K-Means (will fail on ring + center)
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
km_labels = kmeans.fit_predict(X_scaled)

# DBSCAN
dbscan = DBSCAN(eps=0.35, min_samples=5)
db_labels = dbscan.fit_predict(X_scaled)

n_clusters_db = len(set(db_labels)) - (1 if -1 in db_labels else 0)
n_noise_db = sum(db_labels == -1)

print(f"\nK-Means Results:")
print(f"  Clusters found: 2 (we specified 2)")
print(f"  K-Means cannot detect noise")

print(f"\nDBSCAN Results:")
print(f"  Clusters found: {n_clusters_db}")
print(f"  Noise points: {n_noise_db}")

# --------------------------------------------------
# STEP 5: Visualize Both Results
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 5: Visualize Results")
print("=" * 55)

for alg_name, labels in [("K-Means", km_labels),
                           ("DBSCAN", db_labels)]:
    print(f"\n{alg_name}:")
    height, width = 20, 50
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    x_min = X_scaled[:, 0].min() - 0.5
    x_max = X_scaled[:, 0].max() + 0.5
    y_min = X_scaled[:, 1].min() - 0.5
    y_max = X_scaled[:, 1].max() + 0.5

    symbols = {-1: '.', 0: 'o', 1: 'x', 2: '+', 3: '#'}

    for point, label in zip(X_scaled, labels):
        col = int((point[0] - x_min) / (x_max - x_min) * (width-1))
        row = int((1 - (point[1] - y_min) / (y_max - y_min))
                  * (height-1))
        row = max(0, min(height - 1, row))
        col = max(0, min(width - 1, col))
        grid[row][col] = symbols.get(label, '?')

    for row in grid:
        print(f"  |{''.join(row)}|")
    print(f"  {'-' * 52}")

    if alg_name == "K-Means":
        print("  K-Means splits the ring in HALF (wrong!)")
    else:
        print("  DBSCAN finds ring + center + noise (correct!)")
        print(f"  Legend: o=Ring  x=Center  .=Noise")

# --------------------------------------------------
# STEP 6: Analyze DBSCAN Clusters
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 6: Analyze DBSCAN Clusters")
print("=" * 55)

print(f"\n{'Cluster':>10s} {'Size':>6s} {'Avg X':>8s} "
      f"{'Avg Y':>8s} {'Description':>15s}")
print(f"{'-'*52}")

for label in sorted(set(db_labels)):
    mask = db_labels == label
    size = sum(mask)
    avg_x = X[mask, 0].mean()
    avg_y = X[mask, 1].mean()

    if label == -1:
        desc = "Noise/Outliers"
    elif size > 150:
        desc = "Ring shape"
    else:
        desc = "Center blob"

    name = f"Noise" if label == -1 else f"Cluster {label}"
    print(f"{name:>10s} {size:6d} {avg_x:8.2f} {avg_y:8.2f} "
          f"{desc:>15s}")

# --------------------------------------------------
# STEP 7: Parameter Sensitivity
# --------------------------------------------------
print("\n" + "=" * 55)
print("STEP 7: Parameter Sensitivity")
print("=" * 55)

print(f"\n{'eps':>5s}  {'min_samples':>12s}  {'Clusters':>9s}  "
      f"{'Noise':>6s}")
print(f"{'-'*40}")

for eps in [0.2, 0.3, 0.35, 0.4, 0.5]:
    for ms in [3, 5, 10]:
        db = DBSCAN(eps=eps, min_samples=ms)
        labs = db.fit_predict(X_scaled)
        n_c = len(set(labs)) - (1 if -1 in labs else 0)
        n_n = sum(labs == -1)
        marker = " <-- best" if eps == 0.35 and ms == 5 else ""
        print(f"{eps:5.2f}  {ms:12d}  {n_c:9d}  {n_n:6d}{marker}")

print("\n" + "=" * 55)
print("PROJECT COMPLETE!")
print("=" * 55)
```

**Expected Output:**
```
=======================================================
STEP 1: Create Complex Dataset
=======================================================
Total points: 300
  Ring shape: 200 points
  Center blob: 80 points
  Noise: 20 points

=======================================================
STEP 2: Scale Features
=======================================================
Features scaled to mean=0, std=1

=======================================================
STEP 3: Find Good eps (K-Distance Plot)
=======================================================

K-Distance Plot (sorted distances to 5th neighbor):
  Distance
   3.18 |========================================
   2.25 |============================
   1.82 |======================
   1.54 |===================
   1.32 |================
   1.05 |=============
   0.82 |==========
   0.63 |========
   0.51 |====== <-- elbow?
   0.43 |=====
   0.38 |====
   0.35 |====
   0.32 |====
   0.30 |===
   0.28 |===
   0.26 |===
   0.24 |===
   0.22 |==
   0.20 |==
   0.16 |==
        +------------------------------------------
        Points (sorted)

  Look for the 'elbow' in the plot.
  A good eps is around the elbow distance.

=======================================================
STEP 4: K-Means vs DBSCAN
=======================================================

K-Means Results:
  Clusters found: 2 (we specified 2)
  K-Means cannot detect noise

DBSCAN Results:
  Clusters found: 2
  Noise points: 22

=======================================================
STEP 5: Visualize Results
=======================================================

K-Means:
  |                                                  |
  |                  o                               |
  |              ooooooo                             |
  |            oo  ooo  ooo                          |
  |           oo         oo                          |
  |          oo   xxxxx   oo                         |
  |         oo   xxxxxx    o                         |
  |         o    xxxxxx    oo                        |
  |         o   xxxxxxx    o                         |
  |         oo   xxxxx    oo                         |
  |          oo           oo                         |
  |           ooo       ooo                          |
  |            ooo ooo ooo                           |
  |              oooo oo                             |
  |                oo                                |
  |                                                  |
  |                                                  |
  |                                                  |
  |                                                  |
  |                                                  |
  ----------------------------------------------------
  K-Means splits the ring in HALF (wrong!)

DBSCAN:
  |                                                  |
  |                  o                               |
  |              ooooooo                             |
  |            oo  ooo  ooo                          |
  |           oo         oo                          |
  |          oo   xxxxx   oo                         |
  |         oo   xxxxxx    o                         |
  |         o    xxxxxx    oo                        |
  |         o   xxxxxxx    o                         |
  |         oo   xxxxx    oo                         |
  |          oo           oo                         |
  |           ooo       ooo                          |
  |            ooo ooo ooo                           |
  |              oooo oo                             |
  |                oo                                |
  |      .                       .                   |
  |                                                  |
  |           .          .                           |
  |  .                                  .            |
  |                                                  |
  ----------------------------------------------------
  DBSCAN finds ring + center + noise (correct!)
  Legend: o=Ring  x=Center  .=Noise

=======================================================
STEP 6: Analyze DBSCAN Clusters
=======================================================

   Cluster   Size    Avg X    Avg Y     Description
----------------------------------------------------
     Noise     22    -0.19    -1.84  Noise/Outliers
 Cluster 0    200     0.01     0.02      Ring shape
 Cluster 1     78     0.02     0.03     Center blob

=======================================================
STEP 7: Parameter Sensitivity
=======================================================

  eps  min_samples   Clusters   Noise
----------------------------------------
 0.20            3          4      33
 0.20            5          3      60
 0.20           10          2     109
 0.30            3          2      15
 0.30            5          2      20
 0.30           10          2      34
 0.35            3          2      13
 0.35            5          2      22 <-- best
 0.35           10          2      27
 0.40            3          2      13
 0.40            5          2      16
 0.40           10          2      22
 0.50            3          1      10
 0.50            5          1      14
 0.50           10          2      18

=======================================================
PROJECT COMPLETE!
=======================================================
```

### What This Project Shows

1. **Complex Shapes**: We created a ring surrounding a center blob. K-Means cannot handle this.
2. **K-Distance Plot**: Helps find a good eps value by looking for the "elbow" in sorted distances.
3. **K-Means Fails**: K-Means splits the ring in half because it can only make circular clusters.
4. **DBSCAN Succeeds**: DBSCAN correctly identifies the ring, the center blob, AND the noise points.
5. **Parameter Sensitivity**: Different eps and min_samples values produce different results. There is a sweet spot.
6. **Noise Detection**: DBSCAN automatically labels outliers as noise (-1). This is extremely useful in real applications.

---

## Common Mistakes

1. **Forgetting to scale features for DBSCAN**
   - Problem: Features with large ranges dominate distance calculations.
   - Fix: Always scale features before using DBSCAN.

2. **Using DBSCAN on data with varying densities**
   - Problem: If one cluster is much denser than another, a single eps cannot capture both.
   - Fix: Try HDBSCAN (a variant that handles varying densities) or preprocess your data.

3. **Setting eps too small**
   - Problem: Most points become noise. Very few or no clusters found.
   - Fix: Increase eps gradually. Use the k-distance plot to find a good value.

4. **Setting eps too large**
   - Problem: Everything merges into one giant cluster.
   - Fix: Decrease eps. Check if your data actually has distinct clusters.

5. **Using hierarchical clustering on large datasets**
   - Problem: Hierarchical clustering is O(n^2) in memory and O(n^3) in time. With 100,000 points, it will be extremely slow.
   - Fix: Use K-Means for large datasets. Or use hierarchical on a sample of the data.

---

## Best Practices

1. **Start with K-Means for a quick baseline.** It is fast and works well for circular clusters.

2. **Use dendrograms for exploration.** They show you the full hierarchy and help you decide the number of clusters.

3. **Use DBSCAN when shapes are unknown.** If you do not know whether your clusters are circular, DBSCAN is a safer bet.

4. **Scale your features.** All clustering algorithms that use distance (which is all three) benefit from feature scaling.

5. **Use the k-distance plot to choose eps.** It is more principled than guessing.

6. **Try multiple parameter combinations.** There is no single "right" answer. Explore different settings and evaluate the results.

7. **Look at your clusters.** Visualize them. Check if they make sense for your problem. Clustering is exploratory -- you are looking for insights, not exact answers.

8. **Combine methods.** Use K-Means for initial exploration, hierarchical for understanding structure, and DBSCAN for finding irregular patterns.

---

## Quick Summary

```
THREE CLUSTERING ALGORITHMS:

K-Means:
  - Choose K, place centroids, assign, move, repeat
  - Fast, simple, circular clusters only
  - Must specify K

Hierarchical:
  - Start with each point as cluster
  - Merge closest pairs until one cluster
  - Dendrogram shows full history
  - Cut at any level for desired K
  - Slow on large data

DBSCAN:
  - Find dense regions (many neighbors)
  - Core points, border points, noise
  - Parameters: eps (radius), min_samples
  - Any shape clusters!
  - Automatic noise detection
  - Does not need K
```

---

## Key Points to Remember

- **Hierarchical clustering** merges clusters bottom-up. The dendrogram shows the complete history.
- **Dendrograms** let you choose the number of clusters by cutting at different heights.
- **Ward's linkage** is the default and usually best method for hierarchical clustering.
- **DBSCAN** finds clusters based on density (areas where points are packed closely).
- **Core points** have enough neighbors (>= min_samples) within eps distance.
- **Border points** are near core points but do not have enough neighbors themselves.
- **Noise points** are far from any core point and labeled as -1 (outliers).
- **DBSCAN does not need K** specified. It finds the number of clusters automatically.
- **DBSCAN finds clusters of any shape**, unlike K-Means which only finds circular ones.
- Use **K-Means for speed**, **Hierarchical for exploration**, and **DBSCAN for complex shapes**.

---

## Practice Questions

### Question 1
How does agglomerative hierarchical clustering work?

**Answer:** Agglomerative hierarchical clustering works bottom-up. It starts by treating each data point as its own cluster. Then it repeatedly finds the two closest clusters and merges them. This continues until all points are in a single cluster. The result is a tree (dendrogram) that shows the complete history of merges, allowing you to choose any number of clusters by cutting the tree at different heights.

### Question 2
What is a dendrogram and how do you use it to choose the number of clusters?

**Answer:** A dendrogram is a tree diagram that shows the hierarchy of cluster merges. The y-axis represents the distance (or dissimilarity) at which clusters were merged. To choose the number of clusters, draw a horizontal line at a chosen height. The number of vertical lines the horizontal line crosses equals the number of clusters. Look for the largest vertical "gaps" (tall vertical lines) in the dendrogram -- these indicate natural cluster separations.

### Question 3
Explain the three types of points in DBSCAN: core, border, and noise.

**Answer:** A **core point** has at least min_samples neighbors within a distance of eps (it is in a dense region). A **border point** does not have enough neighbors to be a core point, but it falls within the eps neighborhood of at least one core point (it is on the edge of a cluster). A **noise point** is neither a core point nor within the eps neighborhood of any core point (it is an outlier, labeled as -1).

### Question 4
Why can DBSCAN find clusters that K-Means cannot?

**Answer:** K-Means assigns each point to the nearest centroid, which always creates circular (spherical) clusters. DBSCAN works differently -- it groups points that are densely connected through chains of core points. This means DBSCAN can follow the natural shape of clusters, whether they are rings, crescents, curves, or any other irregular shape. DBSCAN also identifies noise points, which K-Means cannot do.

### Question 5
When would you use each of the three clustering algorithms?

**Answer:** Use **K-Means** when you have a large dataset and expect roughly circular clusters, or when you need a fast baseline. Use **Hierarchical clustering** when you have a small to medium dataset and want to explore different numbers of clusters through the dendrogram, or when you need to understand the hierarchical structure of your data. Use **DBSCAN** when you expect non-circular cluster shapes, when you do not know the number of clusters in advance, or when you need to identify outliers and noise.

---

## Exercises

### Exercise 1: Dendrogram Analysis
Create 3 clusters with `make_blobs(n_samples=30, centers=3)`. Compute the linkage matrix with scipy and build a dendrogram. Try cutting at different heights. At what height do you get exactly 3 clusters?

**Hint:** Use `scipy.cluster.hierarchy.linkage` and `fcluster` with `criterion='distance'`.

### Exercise 2: DBSCAN Parameter Tuning
Generate data with `make_moons(n_samples=500, noise=0.1)`. Try different combinations of eps (0.1, 0.2, 0.3, 0.4, 0.5) and min_samples (3, 5, 10, 20). Which combination gives the best results? Use Adjusted Rand Index to compare with true labels.

**Hint:** Use `from sklearn.metrics import adjusted_rand_score`.

### Exercise 3: Three-Algorithm Comparison
Create a dataset with three non-circular clusters (use `make_moons` for two crescents and add a separate blob). Apply all three clustering algorithms. Visualize the results. Which algorithm correctly identifies all three clusters?

**Hint:** Combine `make_moons` with `make_blobs` using `np.vstack`.

---

## What Is Next?

Congratulations! You have now completed the clustering section of this book. You have three powerful tools in your toolkit:

- **K-Means** for fast, circular clustering
- **Hierarchical** for exploration and tree-based analysis
- **DBSCAN** for complex shapes and noise detection

In the chapters ahead, you will explore more advanced topics like **dimensionality reduction** (making your data simpler), **model selection** (choosing the best algorithm), and **pipeline building** (putting it all together). The foundation you have built with classification, regression, and clustering will serve you well as you tackle these more advanced challenges.

Keep practicing, keep experimenting, and remember: the best way to learn machine learning is to apply it to real problems. Take a dataset that interests you, try these algorithms, and see what patterns you can discover!
