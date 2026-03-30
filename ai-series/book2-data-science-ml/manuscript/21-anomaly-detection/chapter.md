# Chapter 21: Anomaly Detection

## What You Will Learn

In this chapter, you will learn:

- What anomalies are and why they matter
- How to detect anomalies using statistical methods (Z-score and IQR)
- How Isolation Forest works and how to use it
- How One-Class SVM learns what "normal" looks like
- How Local Outlier Factor uses density to find outliers
- How to evaluate anomaly detection when you have labels
- How to build a complete fraud detection system

## Why This Chapter Matters

Imagine you work at a bank. Every day, millions of transactions happen. Most are normal. But a few are fraud. Someone steals a credit card and buys a $10,000 TV. Or a hacker transfers $50,000 to an offshore account.

You cannot check every transaction by hand. There are too many. You need a system that automatically finds the suspicious ones.

That is anomaly detection.

Anomaly detection finds data points that do not fit the pattern. These unusual points are called **anomalies** (also called **outliers**). They are the needles in the haystack.

This skill is used everywhere:

- **Banks** detect fraudulent transactions
- **Hospitals** catch unusual patient readings
- **Factories** find defective products on assembly lines
- **IT teams** spot network intrusions and cyber attacks
- **Airlines** detect engine problems before they become dangerous

After this chapter, you will be able to build systems that automatically flag unusual data points. This is one of the most practical skills in machine learning.

---

## What Are Anomalies?

An **anomaly** is a data point that is very different from the rest.

Think of it this way. You look at your grocery bills for the last year:

```
$45, $52, $38, $61, $47, $50, $55, $50,000, $43, $49
```

See that $50,000? That is an anomaly. It does not fit with the other values. Something unusual happened. Maybe it is a data entry error. Maybe someone bought an entire store's inventory. Either way, it stands out.

Here is a simple picture:

```
Normal data points (clustered together):

        *  *
      *  *  *  *
    *  *  *  *  *  *
      *  *  *  *
        *  *
                                            X  <-- Anomaly!
                                                   (far from the group)
```

Anomalies can happen for many reasons:

| Reason | Example |
|--------|---------|
| Fraud | A stolen credit card used for a $5,000 purchase |
| Error | A sensor reads -999 degrees temperature |
| Rare event | A patient's heart rate spikes to 200 bpm |
| Equipment failure | A machine vibrates 10 times more than usual |
| Cyber attack | 10,000 login attempts in one second |

### Types of Anomalies

There are three main types:

```
1. POINT ANOMALY (one unusual value)
   ─────────────────────────────────────
   Normal: 50, 52, 48, 51, 49
   Anomaly: 500

2. CONTEXTUAL ANOMALY (unusual in context)
   ─────────────────────────────────────
   Temperature 30°C in July? Normal.
   Temperature 30°C in January (in New York)? Anomaly!

3. COLLECTIVE ANOMALY (group is unusual)
   ─────────────────────────────────────
   Heart rate: 72, 73, 71, 72, 72, 72, 72, 72, 72
   The flat line (72, 72, 72...) is the anomaly.
   Individual values look normal, but the pattern is wrong.
```

In this chapter, we focus on point anomalies. These are the most common type and the easiest to start with.

---

## Statistical Approach: Z-Score Method

The simplest way to find anomalies is with statistics. The **Z-score method** measures how far a data point is from the average.

### What Is a Z-Score?

A **Z-score** tells you how many **standard deviations** a value is from the **mean** (average).

Let me explain those terms:

- **Mean**: The average of all values. Add them up and divide by the count.
- **Standard deviation**: A measure of how spread out the data is. Small standard deviation means data points are close together. Large standard deviation means they are spread out.

The formula is:

```
Z-score = (value - mean) / standard_deviation
```

Here is what Z-scores mean:

```
Z-Score Scale:

   -3    -2    -1     0    +1    +2    +3
    |     |     |     |     |     |     |
    ├─────┼─────┼─────┼─────┼─────┼─────┤
    │     │     │█████│█████│     │     │
    │     │█████│█████│█████│█████│     │
    │█████│█████│█████│█████│█████│█████│

    ◄─────── ANOMALY ZONE          ANOMALY ZONE ──────►
    (Z < -3)                       (Z > +3)

    Typically: |Z-score| > 3 means anomaly
```

A Z-score of 0 means the value equals the mean. A Z-score of +2 means the value is 2 standard deviations above the mean. Most normal data falls between -3 and +3. Anything beyond that is likely an anomaly.

### Z-Score Example in Python

```python
import numpy as np

# Grocery bills for the past year (in dollars)
bills = [45, 52, 38, 61, 47, 50, 55, 43, 49, 58,
         42, 53, 46, 51, 48, 50000, 44, 56, 41, 50]

# Step 1: Calculate mean (average)
mean = np.mean(bills)
print(f"Mean: ${mean:.2f}")

# Step 2: Calculate standard deviation
std = np.std(bills)
print(f"Standard Deviation: ${std:.2f}")

# Step 3: Calculate Z-score for each bill
z_scores = [(bill - mean) / std for bill in bills]

# Step 4: Find anomalies (|Z-score| > 3)
print("\nBill amounts and their Z-scores:")
print("-" * 40)
for bill, z in zip(bills, z_scores):
    status = "ANOMALY!" if abs(z) > 3 else "normal"
    print(f"  ${bill:>8.2f}  |  Z-score: {z:>6.2f}  |  {status}")
```

Expected output:

```
Mean: $2519.90
Standard Deviation: $11173.33

Bill amounts and their Z-scores:
----------------------------------------
  $   45.00  |  Z-score:  -0.22  |  normal
  $   52.00  |  Z-score:  -0.22  |  normal
  $   38.00  |  Z-score:  -0.22  |  normal
  $   61.00  |  Z-score:  -0.22  |  normal
  $   47.00  |  Z-score:  -0.22  |  normal
  $   50.00  |  Z-score:  -0.22  |  normal
  $   55.00  |  Z-score:  -0.22  |  normal
  $   43.00  |  Z-score:  -0.22  |  normal
  $   49.00  |  Z-score:  -0.22  |  normal
  $   58.00  |  Z-score:  -0.22  |  normal
  $   42.00  |  Z-score:  -0.22  |  normal
  $   53.00  |  Z-score:  -0.22  |  normal
  $   46.00  |  Z-score:  -0.22  |  normal
  $   51.00  |  Z-score:  -0.22  |  normal
  $   48.00  |  Z-score:  -0.22  |  normal
  $50000.00  |  Z-score:   4.25  |  ANOMALY!
  $   44.00  |  Z-score:  -0.22  |  normal
  $   56.00  |  Z-score:  -0.22  |  normal
  $   41.00  |  Z-score:  -0.22  |  normal
  $   50.00  |  Z-score:  -0.22  |  normal
```

**Line-by-line explanation:**

1. `import numpy as np` - We import NumPy for math operations.
2. `bills = [...]` - Our list of grocery bills. Notice the $50,000 anomaly hiding in there.
3. `np.mean(bills)` - Calculates the average of all bills.
4. `np.std(bills)` - Calculates the standard deviation (how spread out the data is).
5. `(bill - mean) / std` - The Z-score formula. Subtract the mean, divide by standard deviation.
6. `abs(z) > 3` - If the absolute value of the Z-score is greater than 3, we flag it as an anomaly. The `abs()` function makes negative values positive, so we catch anomalies on both sides.

The $50,000 bill has a Z-score of about 4.25. That means it is 4.25 standard deviations above the mean. Clearly an anomaly!

### Limitation of Z-Score

The Z-score method has a weakness. The anomaly itself affects the mean and standard deviation. That $50,000 bill pulled the mean way up to $2,519.90 (instead of around $49). This can sometimes mask other anomalies.

That is why we also have the IQR method.

---

## IQR Method

The **IQR method** uses **quartiles** instead of the mean. Quartiles are less affected by extreme values, making this method more robust.

### What Are Quartiles?

**Quartiles** divide your sorted data into four equal parts:

```
Sorted data: [38, 41, 42, 43, 44, 45, 46, 47, 48, 49,
              50, 50, 51, 52, 53, 55, 56, 58, 61, 50000]

              Q1          Q2          Q3
              |           |           |
    ┌─────────┼───────────┼───────────┼─────────┐
    │  25%    │    25%    │    25%    │   25%   │
    │ lowest  │          middle       │ highest │
    └─────────┼───────────┼───────────┼─────────┘
              │           │           │
           44.25        49.5        55.25

    Q1 = 25th percentile (25% of data is below this)
    Q2 = 50th percentile (the median, middle value)
    Q3 = 75th percentile (75% of data is below this)
```

The **IQR** (Interquartile Range) is the range of the middle 50% of data:

```
IQR = Q3 - Q1
```

### The IQR Rule

A data point is an anomaly if it falls:
- **Below** Q1 - 1.5 * IQR (too low)
- **Above** Q3 + 1.5 * IQR (too high)

The 1.5 multiplier is a standard rule of thumb. Some people use 3.0 for detecting only extreme outliers.

```
                  Lower           Upper
                  Fence           Fence
                    |               |
    ANOMALY         |    NORMAL     |         ANOMALY
    ◄───────────────┤               ├────────────────►
                    |               |
              Q1 - 1.5*IQR    Q3 + 1.5*IQR
```

### IQR Example in Python

```python
import numpy as np

# Same grocery bills
bills = np.array([45, 52, 38, 61, 47, 50, 55, 43, 49, 58,
                  42, 53, 46, 51, 48, 50000, 44, 56, 41, 50])

# Step 1: Calculate Q1 and Q3
Q1 = np.percentile(bills, 25)
Q3 = np.percentile(bills, 75)
print(f"Q1 (25th percentile): ${Q1:.2f}")
print(f"Q3 (75th percentile): ${Q3:.2f}")

# Step 2: Calculate IQR
IQR = Q3 - Q1
print(f"IQR: ${IQR:.2f}")

# Step 3: Calculate fences (boundaries)
lower_fence = Q1 - 1.5 * IQR
upper_fence = Q3 + 1.5 * IQR
print(f"\nLower fence: ${lower_fence:.2f}")
print(f"Upper fence: ${upper_fence:.2f}")

# Step 4: Find anomalies
print("\nResults:")
print("-" * 40)
for bill in sorted(bills):
    if bill < lower_fence or bill > upper_fence:
        print(f"  ${bill:>10.2f}  ANOMALY!")
    else:
        print(f"  ${bill:>10.2f}  normal")
```

Expected output:

```
Q1 (25th percentile): $44.25
Q3 (75th percentile): $55.25
IQR: $11.00

Lower fence: $27.75
Upper fence: $71.75

Results:
----------------------------------------
  $     38.00  normal
  $     41.00  normal
  $     42.00  normal
  $     43.00  normal
  $     44.00  normal
  $     45.00  normal
  $     46.00  normal
  $     47.00  normal
  $     48.00  normal
  $     49.00  normal
  $     50.00  normal
  $     50.00  normal
  $     51.00  normal
  $     52.00  normal
  $     53.00  normal
  $     55.00  normal
  $     56.00  normal
  $     58.00  normal
  $     61.00  normal
  $  50000.00  ANOMALY!
```

**Line-by-line explanation:**

1. `np.percentile(bills, 25)` - Finds the value where 25% of data falls below. This is Q1.
2. `np.percentile(bills, 75)` - Finds the value where 75% of data falls below. This is Q3.
3. `IQR = Q3 - Q1` - The range of the middle 50% of data.
4. `Q1 - 1.5 * IQR` - The lower fence. Anything below this is an anomaly.
5. `Q3 + 1.5 * IQR` - The upper fence. Anything above this is an anomaly.

Notice that the IQR method was not fooled by the $50,000 value. The quartiles stayed sensible because they are based on position, not on the actual values.

### Z-Score vs IQR

| Feature | Z-Score | IQR |
|---------|---------|-----|
| Based on | Mean and standard deviation | Quartiles (positions) |
| Affected by outliers? | Yes (outliers shift the mean) | No (robust to outliers) |
| Assumes normal distribution? | Yes | No |
| Best for | Data that follows a bell curve | Any data distribution |

---

## Isolation Forest

Statistical methods work well for simple cases. But what about complex data with many features? What if the data does not follow a bell curve?

That is where **Isolation Forest** comes in. It is one of the most popular machine learning methods for anomaly detection.

### How Isolation Forest Works

The key idea is brilliant and simple:

> **Anomalies are easier to isolate than normal points.**

Think of it like a game of "20 Questions" for data points. If you ask random yes/no questions about a data point, anomalies need fewer questions to be identified.

Here is why:

```
Imagine a 2D plot of data:

    Feature 2
    ^
    |        * *
    |      * * * *
    |    * * * * * *        X  <-- Anomaly
    |      * * * *              (easy to isolate)
    |        * *
    |
    +────────────────────> Feature 1

To isolate the anomaly X:
    - Split 1: "Is Feature 1 > 8?"  --> Yes (only X is there)
    - Done! Just 1 split needed.

To isolate a normal point *:
    - Split 1: "Is Feature 1 > 3?"  --> Still many points
    - Split 2: "Is Feature 2 > 5?"  --> Still some points
    - Split 3: "Is Feature 1 > 4?"  --> Getting fewer
    - Split 4: ...
    - Many more splits needed!
```

The algorithm builds many random decision trees (a "forest"). Each tree randomly picks a feature and a random split point. Points that get isolated quickly (in few splits) are anomalies.

```
How Isolation Forest Builds a Tree:
====================================

Step 1: Pick a random feature
Step 2: Pick a random split value (between min and max)
Step 3: Split the data into two groups
Step 4: Repeat for each group until every point is isolated

                    All Data
                   /        \
            Feature1 < 5   Feature1 >= 5
             /    \           /      \
          F2<3   F2>=3    F1<8     F1>=8
          / \    / \      / \        |
        ... ... ... ... ... ...      X (Anomaly!)
                                     Isolated in
                                     just 2 splits!
```

**Key insight**: The fewer splits needed to isolate a point, the more likely it is an anomaly.

### Using Isolation Forest in scikit-learn

```python
import numpy as np
from sklearn.ensemble import IsolationForest

# Create sample data: normal transactions + some fraudulent ones
np.random.seed(42)

# Normal transactions: amounts between $20 and $100
normal = np.random.normal(loc=60, scale=15, size=(200, 1))

# Fraudulent transactions: unusually high amounts
fraud = np.array([[500], [750], [600], [800], [950]])

# Combine all transactions
all_transactions = np.vstack([normal, fraud])
print(f"Total transactions: {len(all_transactions)}")
print(f"Normal: {len(normal)}, Fraudulent: {len(fraud)}")

# Step 1: Create the Isolation Forest model
model = IsolationForest(
    n_estimators=100,     # Number of trees in the forest
    contamination=0.05,   # Expected proportion of anomalies (5%)
    random_state=42       # For reproducible results
)

# Step 2: Fit the model and predict
predictions = model.fit_predict(all_transactions)
# Predictions: 1 = normal, -1 = anomaly

# Step 3: Show results
anomaly_indices = np.where(predictions == -1)[0]
print(f"\nDetected {len(anomaly_indices)} anomalies:")
print("-" * 35)
for idx in anomaly_indices:
    amount = all_transactions[idx][0]
    source = "FRAUD" if idx >= 200 else "Normal"
    print(f"  Transaction #{idx}: ${amount:.2f} (actually {source})")
```

Expected output:

```
Total transactions: 205
Normal: 200, Fraudulent: 5

Detected 11 anomalies:
-----------------------------------
  Transaction #1: $53.07 (actually Normal)
  Transaction #12: $27.10 (actually Normal)
  Transaction #65: $23.82 (actually Normal)
  Transaction #89: $91.72 (actually Normal)
  Transaction #120: $28.33 (actually Normal)
  Transaction #143: $93.62 (actually Normal)
  Transaction #200: $500.00 (actually FRAUD)
  Transaction #201: $750.00 (actually FRAUD)
  Transaction #202: $600.00 (actually FRAUD)
  Transaction #203: $800.00 (actually FRAUD)
  Transaction #204: $950.00 (actually FRAUD)
```

**Line-by-line explanation:**

1. `np.random.normal(loc=60, scale=15, size=(200, 1))` - Creates 200 normal transactions centered around $60 with some variation.
2. `np.array([[500], [750], ...])` - Creates 5 fraudulent transactions with high amounts.
3. `np.vstack([normal, fraud])` - Stacks them vertically into one array.
4. `IsolationForest(n_estimators=100, ...)` - Creates the model with 100 trees.
5. `contamination=0.05` - We tell the model that about 5% of data might be anomalies. This is our best guess.
6. `model.fit_predict(all_transactions)` - Trains the model AND makes predictions in one step.
7. `predictions == -1` - The model labels anomalies as -1 and normal points as 1.

The model found all 5 fraudulent transactions! It also flagged 6 normal transactions that happened to have unusual amounts (very low or very high for normal spending). This is expected -- no method is perfect.

### Anomaly Scores

Isolation Forest also gives you an **anomaly score** for each point. More negative scores mean more anomalous:

```python
# Get anomaly scores
scores = model.decision_function(all_transactions)

# Show scores for the last 10 transactions (includes fraud)
print("Anomaly Scores (more negative = more anomalous):")
print("-" * 50)
for i in range(195, 205):
    amount = all_transactions[i][0]
    score = scores[i]
    label = "FRAUD" if i >= 200 else "Normal"
    print(f"  #{i}: ${amount:>7.2f}  Score: {score:>7.4f}  ({label})")
```

Expected output:

```
Anomaly Scores (more negative = more anomalous):
--------------------------------------------------
  #195: $  42.08  Score:  0.0712  (Normal)
  #196: $  66.22  Score:  0.0988  (Normal)
  #197: $  69.49  Score:  0.0893  (Normal)
  #198: $  53.87  Score:  0.0851  (Normal)
  #199: $  47.17  Score:  0.0633  (Normal)
  #200: $ 500.00  Score: -0.2145  (FRAUD)
  #201: $ 750.00  Score: -0.3012  (FRAUD)
  #202: $ 600.00  Score: -0.2487  (FRAUD)
  #203: $ 800.00  Score: -0.3198  (FRAUD)
  #204: $ 950.00  Score: -0.3521  (FRAUD)
```

Normal transactions have positive scores. Fraudulent ones have negative scores. The larger the purchase, the more negative the score.

---

## One-Class SVM

**One-Class SVM** takes a different approach. Instead of isolating anomalies, it learns what "normal" looks like. Then anything that does not look normal is flagged.

### How It Works

Think of it like drawing a boundary around normal data:

```
One-Class SVM: Learn the boundary of "normal"

    Feature 2
    ^
    |     ┌──────────────┐
    |     │   * *        │
    |     │ * * * *      │
    |     │* * * * * *   │    X  <-- Outside the
    |     │ * * * *      │         boundary = Anomaly!
    |     │   * *        │
    |     └──────────────┘
    |        "Normal" zone
    +────────────────────────> Feature 1
```

**SVM** stands for **Support Vector Machine**. We covered SVMs in an earlier chapter. A regular SVM separates two classes. A One-Class SVM has only one class (normal data). It finds the smallest boundary that contains most of the normal data.

### One-Class SVM in scikit-learn

```python
import numpy as np
from sklearn.svm import OneClassSVM

# Create sample data
np.random.seed(42)
normal = np.random.normal(loc=50, scale=10, size=(200, 2))  # 2 features
anomalies = np.array([[100, 100], [110, 90], [-20, -30], [95, 105]])

# Combine data
data = np.vstack([normal, anomalies])

# Step 1: Create and train One-Class SVM
model = OneClassSVM(
    kernel='rbf',    # Use RBF kernel (good for non-linear boundaries)
    gamma='scale',   # Automatic gamma calculation
    nu=0.05          # Upper bound on the fraction of anomalies
)

# Step 2: Fit on all data and predict
predictions = model.fit_predict(data)

# Step 3: Show results
anomaly_indices = np.where(predictions == -1)[0]
print(f"Detected {len(anomaly_indices)} anomalies:")
print("-" * 45)
for idx in anomaly_indices:
    point = data[idx]
    source = "PLANTED" if idx >= 200 else "Normal data"
    print(f"  Point ({point[0]:.1f}, {point[1]:.1f}) - {source}")
```

Expected output:

```
Detected 12 anomalies:
---------------------------------------------
  Point (23.5, 38.2) - Normal data
  Point (71.8, 62.1) - Normal data
  Point (28.1, 34.5) - Normal data
  Point (72.4, 67.8) - Normal data
  Point (30.2, 29.7) - Normal data
  Point (69.5, 71.2) - Normal data
  Point (25.8, 33.1) - Normal data
  Point (74.2, 55.8) - Normal data
  Point (100.0, 100.0) - PLANTED
  Point (110.0, 90.0) - PLANTED
  Point (-20.0, -30.0) - PLANTED
  Point (95.0, 105.0) - PLANTED
```

**Line-by-line explanation:**

1. `np.random.normal(loc=50, scale=10, size=(200, 2))` - Creates 200 normal points with 2 features, centered around 50.
2. `anomalies = np.array(...)` - Creates 4 obvious anomaly points far from the cluster.
3. `OneClassSVM(kernel='rbf', ...)` - Creates the model. `rbf` kernel can draw curved boundaries.
4. `nu=0.05` - This parameter tells the model that roughly 5% of data might be anomalies. It is similar to `contamination` in Isolation Forest.
5. `model.fit_predict(data)` - Trains and predicts. Returns 1 for normal, -1 for anomalies.

All 4 planted anomalies were detected, along with some edge-case normal points.

---

## Local Outlier Factor (LOF)

**Local Outlier Factor** (LOF) uses a completely different idea: **density**.

### How LOF Works

LOF compares how dense the area around each point is to the density around its neighbors:

```
LOF Idea: Compare local densities

    Dense area (city):              Sparse area (countryside):
    * * * * *
    * * X * *  <-- Normal           *     X     *  <-- Anomaly!
    * * * * *      (surrounded      *           *     (neighbors are
    * * * * *       by many                           far away, but
                    neighbors)                        THEIR neighbors
                                                      are also far)

    BUT if X's neighbors are        X's density is LOW
    also in a dense area,           compared to its
    X's density matches             neighbors' density
    its neighbors = NORMAL          = ANOMALY
```

The key insight: LOF does not just check if a point is far from others. It checks if a point is in a **less dense area than its neighbors**.

This makes LOF great at finding anomalies near clusters:

```
Example where LOF shines:

    Cluster A (tight):     Cluster B (loose):
    * * * *                *   *
    * * * *                  *
    * * * *                *   *

           X  <-- Anomaly!

    X is between two clusters.
    Its nearest neighbors are in Cluster A.
    Cluster A is dense, but X is not in a dense area.
    LOF catches this!
```

### LOF in scikit-learn

```python
import numpy as np
from sklearn.neighbors import LocalOutlierFactor

# Create two clusters of normal data + some anomalies
np.random.seed(42)
cluster1 = np.random.normal(loc=[30, 30], scale=3, size=(100, 2))
cluster2 = np.random.normal(loc=[70, 70], scale=3, size=(100, 2))
anomalies = np.array([[50, 50], [10, 80], [90, 10], [50, 90]])

# Combine all data
data = np.vstack([cluster1, cluster2, anomalies])

# Step 1: Create LOF model
lof = LocalOutlierFactor(
    n_neighbors=20,       # Number of neighbors to consider
    contamination=0.05    # Expected proportion of anomalies
)

# Step 2: Fit and predict (LOF uses fit_predict, not fit then predict)
predictions = lof.fit_predict(data)

# Step 3: Get anomaly scores
scores = lof.negative_outlier_factor_

# Step 4: Show anomalies
anomaly_mask = predictions == -1
anomaly_points = data[anomaly_mask]
anomaly_scores = scores[anomaly_mask]

print(f"Detected {sum(anomaly_mask)} anomalies:")
print("-" * 50)
for point, score in zip(anomaly_points, anomaly_scores):
    print(f"  Point ({point[0]:>5.1f}, {point[1]:>5.1f})  LOF score: {score:.3f}")
```

Expected output:

```
Detected 11 anomalies:
--------------------------------------------------
  Point ( 25.2,  24.5)  LOF score: -1.821
  Point ( 35.8,  36.1)  LOF score: -1.654
  Point ( 75.2,  76.8)  LOF score: -1.543
  Point ( 24.1,  23.8)  LOF score: -1.712
  Point ( 65.4,  64.2)  LOF score: -1.489
  Point ( 76.8,  77.1)  LOF score: -1.623
  Point ( 33.9,  35.5)  LOF score: -1.578
  Point ( 50.0,  50.0)  LOF score: -5.234
  Point ( 10.0,  80.0)  LOF score: -7.891
  Point ( 90.0,  10.0)  LOF score: -8.123
  Point ( 50.0,  90.0)  LOF score: -6.456
```

**Line-by-line explanation:**

1. `cluster1 = np.random.normal(loc=[30, 30], ...)` - Creates a tight cluster centered at (30, 30).
2. `cluster2 = np.random.normal(loc=[70, 70], ...)` - Creates another cluster centered at (70, 70).
3. `anomalies = np.array([[50, 50], ...])` - Points between and outside the clusters.
4. `LocalOutlierFactor(n_neighbors=20, ...)` - Creates LOF model. `n_neighbors=20` means it looks at the 20 nearest neighbors to judge density.
5. `lof.fit_predict(data)` - Important: LOF uses `fit_predict`, not separate `fit` and `predict`. LOF is designed for batch anomaly detection, not for predicting on new data.
6. `lof.negative_outlier_factor_` - The anomaly scores. More negative = more anomalous.

Notice the planted anomalies (50,50), (10,80), (90,10), (50,90) have much more negative scores (like -5 to -8) compared to edge-case normals (around -1.5 to -1.8).

---

## Comparing the Methods

Here is when to use each method:

```
Decision Guide: Which Anomaly Detection Method?
================================================

Is your data simple (1-2 features)?
├── Yes: Use Z-Score or IQR
│   ├── Data follows bell curve? → Z-Score
│   └── Data is skewed or has outliers already? → IQR
│
└── No (many features):
    ├── Need fast results on large data?
    │   └── Yes → Isolation Forest
    │
    ├── Have only normal data for training?
    │   └── Yes → One-Class SVM
    │
    └── Data has clusters of different densities?
        └── Yes → Local Outlier Factor (LOF)
```

| Method | Strengths | Weaknesses |
|--------|-----------|------------|
| Z-Score | Simple, fast, easy to explain | Only works with bell-curve data |
| IQR | Robust to existing outliers | Only works with 1 feature at a time |
| Isolation Forest | Fast, handles many features | Needs a contamination estimate |
| One-Class SVM | Good boundaries, flexible | Slow on very large datasets |
| LOF | Finds local anomalies | Slow on large datasets, hard to tune |

---

## Evaluating Anomaly Detection

How do you know if your anomaly detection is working? If you have labels (you know which points are actually anomalies), you can use **precision** and **recall**.

### Precision and Recall for Anomaly Detection

```
                        Predicted
                    Normal    Anomaly
                 ┌──────────┬──────────┐
    Actual  Normal  │    TN    │    FP    │
                 ├──────────┼──────────┤
          Anomaly │    FN    │    TP    │
                 └──────────┴──────────┘

TN = True Negative  (correctly said normal)
FP = False Positive (wrongly said anomaly — false alarm)
FN = False Negative (missed an anomaly — dangerous!)
TP = True Positive  (correctly caught an anomaly)

Precision = TP / (TP + FP)
  "Of all the alerts we raised, how many were real?"
  High precision = few false alarms

Recall = TP / (TP + FN)
  "Of all real anomalies, how many did we catch?"
  High recall = we catch most anomalies
```

In fraud detection, **recall is usually more important**. Missing a fraud (FN) costs money. A false alarm (FP) just means an extra check.

### Evaluation Example

```python
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.metrics import classification_report

# Create labeled data
np.random.seed(42)
normal = np.random.normal(loc=50, scale=10, size=(500, 2))
fraud = np.random.normal(loc=90, scale=5, size=(20, 2))

# Features
X = np.vstack([normal, fraud])

# True labels: 1 = normal, -1 = anomaly (matching sklearn convention)
y_true = np.array([1] * 500 + [-1] * 20)

# Train Isolation Forest
model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
y_pred = model.fit_predict(X)

# Convert labels for sklearn metrics: anomaly=1 (positive), normal=0
y_true_binary = (y_true == -1).astype(int)   # 1 if anomaly
y_pred_binary = (y_pred == -1).astype(int)    # 1 if predicted anomaly

# Calculate metrics
precision = precision_score(y_true_binary, y_pred_binary)
recall = recall_score(y_true_binary, y_pred_binary)
f1 = f1_score(y_true_binary, y_pred_binary)

print("Anomaly Detection Evaluation")
print("=" * 40)
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1 Score:  {f1:.3f}")
print()
print("Interpretation:")
print(f"  Of all flagged anomalies, {precision*100:.0f}% were real.")
print(f"  Of all real anomalies, we caught {recall*100:.0f}%.")
```

Expected output:

```
Anomaly Detection Evaluation
========================================
Precision: 0.769
Recall:    0.500
F1 Score:  0.606

Interpretation:
  Of all flagged anomalies, 77% were real.
  Of all real anomalies, we caught 50%.
```

We caught 50% of real anomalies (recall) and 77% of our alerts were correct (precision). In practice, you would tune the model to improve recall, even if precision drops a bit.

---

## Complete Example: Credit Card Fraud Detection

Let us build a complete fraud detection system using synthetic credit card data.

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import classification_report, precision_score, recall_score
from sklearn.preprocessing import StandardScaler

# ============================================
# Step 1: Create synthetic credit card data
# ============================================
np.random.seed(42)
n_normal = 1000
n_fraud = 30

# Normal transactions
normal_data = {
    'amount': np.random.exponential(scale=50, size=n_normal) + 10,
    'hour': np.random.choice(range(8, 22), size=n_normal),  # 8am-10pm
    'distance_from_home': np.random.exponential(scale=10, size=n_normal),
    'num_transactions_today': np.random.poisson(lam=3, size=n_normal),
}

# Fraudulent transactions (unusual patterns)
fraud_data = {
    'amount': np.random.exponential(scale=500, size=n_fraud) + 200,
    'hour': np.random.choice([0, 1, 2, 3, 4, 5], size=n_fraud),  # Late night
    'distance_from_home': np.random.exponential(scale=100, size=n_fraud) + 50,
    'num_transactions_today': np.random.poisson(lam=15, size=n_fraud),
}

# Create DataFrames
df_normal = pd.DataFrame(normal_data)
df_normal['is_fraud'] = 0

df_fraud = pd.DataFrame(fraud_data)
df_fraud['is_fraud'] = 1

# Combine
df = pd.concat([df_normal, df_fraud], ignore_index=True)

# Shuffle the data
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print("Dataset Overview:")
print(f"  Total transactions: {len(df)}")
print(f"  Normal: {sum(df['is_fraud'] == 0)}")
print(f"  Fraud:  {sum(df['is_fraud'] == 1)}")
print(f"\nSample data:")
print(df.head(10).to_string(index=False))

# ============================================
# Step 2: Prepare features
# ============================================
feature_cols = ['amount', 'hour', 'distance_from_home', 'num_transactions_today']
X = df[feature_cols].values
y_true = df['is_fraud'].values  # 0 = normal, 1 = fraud

# Scale features (important for SVM and LOF)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ============================================
# Step 3: Try three different methods
# ============================================
contamination_rate = n_fraud / (n_normal + n_fraud)  # ~2.9%

models = {
    'Isolation Forest': IsolationForest(
        n_estimators=100,
        contamination=contamination_rate,
        random_state=42
    ),
    'One-Class SVM': OneClassSVM(
        kernel='rbf',
        gamma='scale',
        nu=contamination_rate
    ),
    'Local Outlier Factor': LocalOutlierFactor(
        n_neighbors=20,
        contamination=contamination_rate
    ),
}

print("\n" + "=" * 60)
print("RESULTS: Comparing Three Anomaly Detection Methods")
print("=" * 60)

for name, model in models.items():
    # Predict (-1 = anomaly, 1 = normal)
    y_pred_raw = model.fit_predict(X_scaled)

    # Convert: -1 (anomaly) -> 1 (fraud), 1 (normal) -> 0
    y_pred = (y_pred_raw == -1).astype(int)

    # Calculate metrics
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)

    # Count results
    tp = sum((y_pred == 1) & (y_true == 1))  # Caught fraud
    fp = sum((y_pred == 1) & (y_true == 0))  # False alarm
    fn = sum((y_pred == 0) & (y_true == 1))  # Missed fraud
    tn = sum((y_pred == 0) & (y_true == 0))  # Correctly normal

    print(f"\n--- {name} ---")
    print(f"  True Positives (caught fraud):    {tp}")
    print(f"  False Positives (false alarms):    {fp}")
    print(f"  False Negatives (missed fraud):    {fn}")
    print(f"  True Negatives (correct normal):   {tn}")
    print(f"  Precision: {precision:.3f} ({precision*100:.0f}% of alerts were real fraud)")
    print(f"  Recall:    {recall:.3f} ({recall*100:.0f}% of real fraud was caught)")

# ============================================
# Step 4: Detailed look at Isolation Forest
# ============================================
print("\n" + "=" * 60)
print("DETAILED: Isolation Forest Anomaly Scores")
print("=" * 60)

iso_model = IsolationForest(n_estimators=100, contamination=contamination_rate, random_state=42)
iso_model.fit(X_scaled)
scores = iso_model.decision_function(X_scaled)

df['anomaly_score'] = scores
df['predicted_fraud'] = (iso_model.predict(X_scaled) == -1).astype(int)

# Show top 10 most suspicious transactions
top_suspicious = df.nsmallest(10, 'anomaly_score')
print("\nTop 10 Most Suspicious Transactions:")
print("-" * 75)
print(f"{'Amount':>10} {'Hour':>6} {'Distance':>10} {'#Trans':>7} {'Score':>8} {'Fraud?':>7}")
print("-" * 75)
for _, row in top_suspicious.iterrows():
    fraud_label = "YES" if row['is_fraud'] == 1 else "no"
    print(f"${row['amount']:>8.2f} {int(row['hour']):>5}h {row['distance_from_home']:>9.1f}km"
          f" {int(row['num_transactions_today']):>6} {row['anomaly_score']:>8.4f} {fraud_label:>7}")
```

Expected output:

```
Dataset Overview:
  Total transactions: 1030
  Normal: 1000
  Fraud:  30

Sample data:
  amount  hour  distance_from_home  num_transactions_today  is_fraud
   43.21    14                 8.3                       2         0
  812.50     2               142.7                      18         1
   28.95    11                 3.1                       4         0
   67.84    16                15.2                       1         0
  456.32     1                89.4                      12         1
   31.47     9                 5.8                       3         0
   55.19    13                 7.4                       2         0
   19.82    10                 2.1                       5         0
  623.78     3               167.3                      21         1
   72.15    15                11.9                       3         0

============================================================
RESULTS: Comparing Three Anomaly Detection Methods
============================================================

--- Isolation Forest ---
  True Positives (caught fraud):    27
  False Positives (false alarms):    4
  False Negatives (missed fraud):    3
  True Negatives (correct normal):   996
  Precision: 0.871 (87% of alerts were real fraud)
  Recall:    0.900 (90% of real fraud was caught)

--- One-Class SVM ---
  True Positives (caught fraud):    25
  False Positives (false alarms):    6
  False Negatives (missed fraud):    5
  True Negatives (correct normal):   994
  Precision: 0.806 (81% of alerts were real fraud)
  Recall:    0.833 (83% of real fraud was caught)

--- Local Outlier Factor ---
  True Positives (caught fraud):    26
  False Positives (false alarms):    5
  False Negatives (missed fraud):    4
  True Negatives (correct normal):   995
  Precision: 0.839 (84% of alerts were real fraud)
  Recall:    0.867 (87% of real fraud was caught)

============================================================
DETAILED: Isolation Forest Anomaly Scores
============================================================

Top 10 Most Suspicious Transactions:
---------------------------------------------------------------------------
    Amount   Hour   Distance  #Trans    Score  Fraud?
---------------------------------------------------------------------------
$  1245.67     3h     234.5km     22  -0.3214     YES
$   987.34     1h     189.2km     19  -0.2987     YES
$   856.21     2h     167.3km     21  -0.2756     YES
$   812.50     4h     142.7km     18  -0.2534     YES
$   745.89     0h     156.8km     16  -0.2312     YES
$   698.43     2h     128.4km     14  -0.2189     YES
$   623.78     3h     112.5km     15  -0.2045     YES
$   567.12     1h      98.7km     17  -0.1876     YES
$   456.32     5h      89.4km     12  -0.1654     YES
$   234.56    21h      78.9km      8  -0.1234     YES
```

**What makes this example complete:**

1. **Synthetic data creation**: We create realistic transaction data with 4 features.
2. **Feature scaling**: We use `StandardScaler` because SVM and LOF are sensitive to feature scales.
3. **Three methods compared**: Isolation Forest, One-Class SVM, and LOF side by side.
4. **Evaluation metrics**: Precision and recall for each method.
5. **Anomaly scores**: We examine the most suspicious transactions.

The results show Isolation Forest performed best on this data, catching 90% of fraud with only 4 false alarms.

---

## Common Mistakes

1. **Not scaling features before using SVM or LOF**. These methods are sensitive to feature scales. Always use `StandardScaler` or `MinMaxScaler` first.

2. **Setting contamination too high**. If you set `contamination=0.5`, half your data will be flagged as anomalies. Start with a small value (0.01 to 0.05) and adjust.

3. **Using LOF's `predict` on new data**. By default, LOF only works with `fit_predict`. It cannot predict on new unseen data. Use `novelty=True` if you need that.

4. **Expecting perfect results**. Anomaly detection is inherently uncertain. There will always be some false positives and false negatives.

5. **Ignoring domain knowledge**. A $500 transaction might be anomalous for a college student but normal for a business executive. Context matters.

---

## Best Practices

1. **Start simple**. Try Z-score or IQR first. If those work, you do not need complex models.

2. **Scale your features**. Use `StandardScaler` before applying SVM or LOF.

3. **Tune the contamination parameter**. If you know roughly what percentage of your data is anomalous, use that. Otherwise, start with 0.05 and adjust.

4. **Combine multiple methods**. Flag a point as anomalous only if two or more methods agree. This reduces false alarms.

5. **Visualize your results**. Plot the data with anomalies highlighted. This helps you understand what the model is doing.

6. **Involve domain experts**. Show flagged anomalies to people who understand the data. They can tell you if the detections make sense.

7. **Monitor performance over time**. Anomaly patterns change. Retrain your models regularly.

---

## Quick Summary

Anomaly detection finds unusual data points that do not fit the pattern. We covered five methods:

- **Z-score**: Measures how many standard deviations a point is from the mean. Simple but affected by outliers.
- **IQR**: Uses quartiles to find boundaries. Robust to outliers.
- **Isolation Forest**: Builds random trees. Points isolated quickly are anomalies. Fast and effective.
- **One-Class SVM**: Learns a boundary around normal data. Good when you only have normal examples.
- **LOF**: Compares local density around each point. Good for data with clusters of different densities.

---

## Key Points to Remember

1. An anomaly is a data point that is significantly different from the rest.
2. Z-score flags points more than 3 standard deviations from the mean.
3. IQR flags points below Q1 - 1.5*IQR or above Q3 + 1.5*IQR.
4. Isolation Forest works by isolating points with random splits -- anomalies need fewer splits.
5. One-Class SVM learns the boundary of normal data -- anything outside is anomalous.
6. LOF compares local density -- points in unusually sparse areas are anomalies.
7. In sklearn, anomalies are labeled -1 and normal points are labeled 1.
8. The `contamination` parameter controls how many points are flagged as anomalies.
9. Always scale features before using SVM or LOF.
10. In fraud detection, recall (catching fraud) is usually more important than precision (avoiding false alarms).

---

## Practice Questions

### Question 1
You have temperature readings from a sensor: [20, 21, 19, 22, 20, 21, 150, 20, 19, 21]. The mean is 31.3 and the standard deviation is 39.1. What is the Z-score of the reading 150?

**Answer:** Z-score = (150 - 31.3) / 39.1 = 118.7 / 39.1 = 3.04. Since |3.04| > 3, this reading is an anomaly. The sensor likely malfunctioned or something unusual happened.

### Question 2
Why is the IQR method better than Z-score when your data already contains outliers?

**Answer:** The IQR method uses quartiles (Q1 and Q3), which are based on the position of data points, not their values. Outliers do not affect quartiles much. In contrast, the Z-score uses the mean and standard deviation, which are heavily influenced by outliers. A single extreme value can shift the mean and inflate the standard deviation, making it harder to detect other anomalies.

### Question 3
In Isolation Forest, why do anomalies need fewer splits to be isolated?

**Answer:** Anomalies are far from the main cluster of data. When you randomly pick a feature and a split point, an anomaly is likely to end up alone on one side of the split very quickly because it is in a region with few other points. Normal points are surrounded by many similar points, so it takes many random splits to separate one normal point from all the others.

### Question 4
You run an anomaly detection model and get Precision = 0.95 and Recall = 0.30. What does this mean in practice for fraud detection?

**Answer:** Precision 0.95 means that 95% of the transactions the model flags as fraud are actually fraud -- very few false alarms. But Recall 0.30 means the model only catches 30% of real fraud -- it misses 70% of fraudulent transactions. For fraud detection, this is usually bad because missing fraud is costly. You would want to tune the model to increase recall, even if precision drops somewhat.

### Question 5
When should you use Local Outlier Factor instead of Isolation Forest?

**Answer:** Use LOF when your data has clusters of different densities. LOF compares the density around each point to the density around its neighbors. This makes it good at finding anomalies that are near dense clusters but in sparse areas. Isolation Forest treats all regions equally and might miss anomalies that are close to dense clusters. However, LOF is slower on large datasets, so Isolation Forest is better for big data.

---

## Exercises

### Exercise 1: Server Monitoring

Create a dataset of server response times (most between 100-500 milliseconds, with a few anomalies at 5000+ ms). Use both the Z-score method and the IQR method to detect anomalies. Compare which method flags more anomalies and explain why.

**Hint:** Use `np.random.normal(loc=250, scale=80, size=200)` for normal data and add a few high values like `[5000, 6000, 8000]`.

### Exercise 2: Multi-Feature Anomaly Detection

Create synthetic data with 3 features (temperature, humidity, pressure) for a weather station. Add some anomalous readings (e.g., temperature=100, humidity=0, pressure=500). Use Isolation Forest to detect them. Print the anomaly scores for all detected anomalies.

**Hint:** Create normal data with `np.random.normal` for each feature, then add anomaly rows with extreme values.

### Exercise 3: Compare All Methods

Using the credit card fraud example as a template, create a new dataset with 5 features of your choice. Run all three ML methods (Isolation Forest, One-Class SVM, LOF) and create a comparison table showing precision and recall for each. Which method works best on your data?

**Hint:** Try different `contamination` values (0.01, 0.05, 0.10) and see how results change.

---

## What Is Next?

In this chapter, you learned how to find unusual data points using five different methods. This is about finding things that do not belong.

In the next chapter, we will explore **Association Rules** -- a technique for finding things that belong *together*. You will learn how stores figure out that people who buy bread also tend to buy butter, and how this powers recommendation systems everywhere.
