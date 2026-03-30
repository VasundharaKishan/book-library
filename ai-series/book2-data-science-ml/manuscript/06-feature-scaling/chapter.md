# Chapter 6: Feature Scaling

## What You Will Learn

In this chapter, you will learn:

- Why features on different scales cause problems for some models
- How Min-Max Normalization squeezes values into the 0-1 range
- How Standardization centers data around zero
- When to use normalization versus standardization
- Which models need scaling and which do not
- How to use sklearn MinMaxScaler and StandardScaler
- The critical rule: fit on training data, transform both train and test
- How to visualize data before and after scaling

## Why This Chapter Matters

Imagine you are comparing two athletes. One runs 100 meters in 10 seconds. The other lifts 200 kilograms. Which one is "better"? You cannot compare them directly. The numbers are on completely different scales.

Machine learning models face the same problem. When one feature ranges from 0 to 1 and another ranges from 0 to 1,000,000, some models get confused. They think the bigger numbers are more important. Feature scaling fixes this problem. It puts all features on a level playing field.

Without scaling, your model might give terrible results. With scaling, the same model might work perfectly. This chapter teaches you how and when to scale your data.

---

## 6.1 Why Scaling Matters

### The Problem: Features on Different Scales

Let's say you are building a model to predict house prices. You have two features:

- **Number of bedrooms**: ranges from 1 to 6
- **Square footage**: ranges from 500 to 5,000

Here is what this looks like:

```
Feature Ranges (Before Scaling)
===============================

Bedrooms:    |==|                                    (1 to 6)
             0        1000       2000       3000       4000       5000

Sq Footage:  |========================================| (500 to 5000)
             0        1000       2000       3000       4000       5000
```

The square footage numbers are hundreds of times larger than bedroom numbers. Some models will think square footage is more important just because the numbers are bigger. That is wrong. A house with 5 bedrooms versus 1 bedroom is a huge difference. But the model might ignore it because the number "5" is tiny compared to "5000."

### Which Models Care About Scale?

Not all models are affected by feature scales. Here is a simple guide:

```
Models That NEED Scaling          Models That DO NOT Need Scaling
==============================    ================================
K-Nearest Neighbors (KNN)        Decision Trees
Support Vector Machines (SVM)    Random Forests
Neural Networks                  Gradient Boosted Trees (XGBoost)
Linear Regression*               Rule-based models
Logistic Regression*
K-Means Clustering

* These work without scaling but often perform better with it.
```

**Why do some models need scaling?**

- **KNN** measures distances between points. If one feature has huge numbers, it dominates the distance calculation.
- **SVM** finds boundaries between classes. Large features push the boundary in their direction.
- **Neural Networks** use gradient descent. Different scales cause the gradients to be uneven, making training slow or unstable.

**Why do tree-based models not care?**

Decision trees split data by asking "Is feature X greater than some value?" They only care about the order of values, not the actual numbers. Splitting at 1000 or splitting at 0.5 works the same way for a tree.

### A Simple Example: KNN Without Scaling

```python
import numpy as np

# Two houses: [bedrooms, square_footage]
house_a = np.array([3, 1500])
house_b = np.array([5, 1510])
house_c = np.array([3, 3000])

# Distance from house_a to house_b
dist_ab = np.sqrt((3-5)**2 + (1500-1510)**2)
print(f"Distance A to B: {dist_ab:.2f}")

# Distance from house_a to house_c
dist_ac = np.sqrt((3-3)**2 + (1500-3000)**2)
print(f"Distance A to C: {dist_ac:.2f}")
```

**Expected Output:**
```
Distance A to B: 10.20
Distance A to C: 1500.00
```

**What is wrong here?**

House A and House B have different bedrooms (3 vs 5) but similar square footage. House A and House C have the same bedrooms but very different square footage. The distance calculation is completely dominated by square footage. The bedroom difference barely matters. KNN would say House B is the nearest neighbor to House A, even though House C has the same number of bedrooms.

---

## 6.2 Min-Max Normalization

### The Idea

Min-Max Normalization squeezes all values into the range 0 to 1. The smallest value becomes 0. The largest value becomes 1. Everything else falls in between.

**The formula:**

```
                   value - min
scaled_value = -----------------
                  max - min
```

**Think of it like this:** You have a thermometer. The coldest day was 0 degrees. The hottest day was 100 degrees. Today is 50 degrees. After normalization, today's temperature is 0.5 (right in the middle).

### Step-by-Step Example

```
Original values: [200, 400, 600, 800, 1000]

min = 200
max = 1000
range = max - min = 800

Scaled values:
  200 -> (200 - 200) / 800 = 0.000
  400 -> (400 - 200) / 800 = 0.250
  600 -> (600 - 200) / 800 = 0.500
  800 -> (800 - 200) / 800 = 0.750
 1000 -> (1000 - 200) / 800 = 1.000
```

```
Before:  |--200------400------600------800------1000--|
After:   |--0.0------0.25-----0.5------0.75-----1.0--|
```

### Min-Max Normalization in Python

```python
import numpy as np

# Original data
data = np.array([200, 400, 600, 800, 1000]).reshape(-1, 1)

# Manual Min-Max scaling
min_val = data.min()
max_val = data.max()
scaled = (data - min_val) / (max_val - min_val)

print("Original:", data.flatten())
print("Scaled:  ", scaled.flatten())
```

**Expected Output:**
```
Original: [ 200  400  600  800 1000]
Scaled:   [0.   0.25 0.5  0.75 1.  ]
```

**Line-by-line explanation:**

1. `data = np.array([200, 400, 600, 800, 1000]).reshape(-1, 1)` -- Create a NumPy array. The `.reshape(-1, 1)` makes it a column (which sklearn requires later).
2. `min_val = data.min()` -- Find the smallest value (200).
3. `max_val = data.max()` -- Find the largest value (1000).
4. `scaled = (data - min_val) / (max_val - min_val)` -- Apply the formula to every value at once. NumPy does the math for each element automatically.
5. `.flatten()` -- Converts the column back to a flat list for clean printing.

### Using sklearn MinMaxScaler

In practice, you use sklearn instead of doing it manually.

```python
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Sample data: [salary, age]
data = np.array([
    [30000, 25],
    [50000, 35],
    [70000, 45],
    [90000, 55],
    [110000, 65]
])

# Create the scaler
scaler = MinMaxScaler()

# Fit and transform
scaled_data = scaler.fit_transform(data)

print("Original data:")
print(data)
print("\nScaled data (0 to 1):")
print(scaled_data)
```

**Expected Output:**
```
Original data:
[[ 30000    25]
 [ 50000    35]
 [ 70000    45]
 [ 90000    55]
 [110000    65]]

Scaled data (0 to 1):
[[0.   0.  ]
 [0.25 0.25]
 [0.5  0.5 ]
 [0.75 0.75]
 [1.   1.  ]]
```

**Line-by-line explanation:**

1. `from sklearn.preprocessing import MinMaxScaler` -- Import the scaler from sklearn.
2. `data = np.array([...])` -- Create a 2D array with two features: salary and age.
3. `scaler = MinMaxScaler()` -- Create a scaler object. It does not do anything yet.
4. `scaled_data = scaler.fit_transform(data)` -- Two steps in one: `fit` learns the min and max of each column, then `transform` applies the formula. Each column is scaled independently.
5. Now both salary (30,000 to 110,000) and age (25 to 65) are on the same 0 to 1 scale.

---

## 6.3 Standardization (Z-Score Scaling)

### The Idea

Standardization transforms your data so it has a mean (average) of 0 and a standard deviation of 1. Instead of squeezing values into 0-1, it centers them around zero.

**The formula:**

```
                  value - mean
scaled_value = -----------------
               standard_deviation
```

**Think of it like this:** In a class test, the average score is 70 and the standard deviation is 10. If you scored 90, your z-score is (90 - 70) / 10 = 2.0. That means you scored 2 standard deviations above average. If you scored 60, your z-score is (60 - 70) / 10 = -1.0. One standard deviation below average.

```
Standard Deviation (std) = how spread out the data is

Low std:   Most values are close to the mean
           |    ****    |
           |   ******   |
           |  ********  |
           | ********** |
           +------------+

High std:  Values are spread far from the mean
           |*          *|
           |**        **|
           |***      ***|
           |****    ****|
           +------------+
```

### Step-by-Step Example

```
Original values: [10, 20, 30, 40, 50]

mean = (10 + 20 + 30 + 40 + 50) / 5 = 30
std  = 14.14  (standard deviation)

Scaled values:
  10 -> (10 - 30) / 14.14 = -1.414
  20 -> (20 - 30) / 14.14 = -0.707
  30 -> (30 - 30) / 14.14 =  0.000
  40 -> (40 - 30) / 14.14 =  0.707
  50 -> (50 - 30) / 14.14 =  1.414
```

```
Before:  |--10-------20-------30-------40-------50--|
After:   |--(-1.41)--(-0.71)--(0.0)----(0.71)---(1.41)--|
                               ^
                          mean = 0
```

### Standardization in Python

```python
import numpy as np

# Original data
data = np.array([10, 20, 30, 40, 50], dtype=float)

# Manual standardization
mean = data.mean()
std = data.std()
scaled = (data - mean) / std

print(f"Mean: {mean}")
print(f"Std:  {std:.2f}")
print(f"Original:      {data}")
print(f"Standardized:  {np.round(scaled, 3)}")
print(f"New mean:      {scaled.mean():.1f}")
print(f"New std:       {scaled.std():.1f}")
```

**Expected Output:**
```
Mean: 30.0
Std:  14.14
Original:      [10. 20. 30. 40. 50.]
Standardized:  [-1.414 -0.707  0.     0.707  1.414]
New mean:      0.0
New std:       1.0
```

### Using sklearn StandardScaler

```python
from sklearn.preprocessing import StandardScaler
import numpy as np

# Sample data: [salary, age]
data = np.array([
    [30000, 25],
    [50000, 35],
    [70000, 45],
    [90000, 55],
    [110000, 65]
])

# Create the scaler
scaler = StandardScaler()

# Fit and transform
scaled_data = scaler.fit_transform(data)

print("Original data:")
print(data)
print("\nStandardized data:")
print(np.round(scaled_data, 2))
print(f"\nMean of each column: {np.round(scaled_data.mean(axis=0), 1)}")
print(f"Std of each column:  {np.round(scaled_data.std(axis=0), 1)}")
```

**Expected Output:**
```
Original data:
[[ 30000    25]
 [ 50000    35]
 [ 70000    45]
 [ 90000    55]
 [110000    65]]

Standardized data:
[[-1.41 -1.41]
 [-0.71 -0.71]
 [ 0.    0.  ]
 [ 0.71  0.71]
 [ 1.41  1.41]]

Mean of each column: [0. 0.]
Std of each column:  [1. 1.]
```

**Line-by-line explanation:**

1. `scaler = StandardScaler()` -- Create a StandardScaler object.
2. `scaler.fit_transform(data)` -- `fit` calculates the mean and standard deviation for each column. `transform` applies the z-score formula to each value.
3. After scaling, each column has mean = 0 and standard deviation = 1.

---

## 6.4 When to Use Which

### Normalization (Min-Max) vs Standardization (Z-Score)

```
+---------------------+---------------------------+---------------------------+
| Aspect              | Min-Max Normalization     | Standardization (Z-Score) |
+---------------------+---------------------------+---------------------------+
| Output range        | 0 to 1                    | No fixed range            |
| Affected by         | Yes, strongly             | Less affected             |
| outliers?           |                           |                           |
| Best for            | Neural networks,          | Most ML algorithms,       |
|                     | image pixel values,       | when data has outliers,   |
|                     | when you need bounded     | Linear/Logistic Regression|
|                     | values                    | SVM, KNN                  |
| Preserves           | Yes                       | Yes                       |
| zero values?        | No (unless 0 is the min)  | Only if 0 equals the mean |
+---------------------+---------------------------+---------------------------+
```

### Quick Decision Guide

```
Do you need values between 0 and 1?
  |
  +-- YES --> Use Min-Max Normalization
  |            (neural networks, image data)
  |
  +-- NO --> Does your data have outliers?
              |
              +-- YES --> Use Standardization
              |            (outliers won't squash other values)
              |
              +-- NO --> Either works, but Standardization
                          is the safer default choice
```

### Why Outliers Matter

Consider this data: `[10, 20, 30, 40, 1000]`

The value 1000 is an outlier (an unusually large value).

```python
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

data = np.array([10, 20, 30, 40, 1000]).reshape(-1, 1)

# Min-Max scaling
minmax = MinMaxScaler()
mm_scaled = minmax.fit_transform(data)

# Standardization
standard = StandardScaler()
std_scaled = standard.fit_transform(data)

print("Original  | Min-Max | Standardized")
print("-" * 40)
for i in range(len(data)):
    print(f"{data[i][0]:8.0f}  | {mm_scaled[i][0]:7.4f} | {std_scaled[i][0]:7.4f}")
```

**Expected Output:**
```
Original  | Min-Max | Standardized
----------------------------------------
      10  |  0.0000 | -0.4813
      20  |  0.0101 | -0.4560
      30  |  0.0202 | -0.4307
      40  |  0.0303 | -0.4054
    1000  |  1.0000 |  1.7733
```

**Look at the Min-Max column.** The first four values (10, 20, 30, 40) are all squished near zero (0.00 to 0.03). The outlier (1000) takes the entire range. All the useful variation between 10 and 40 is lost.

**Look at the Standardized column.** The first four values are spread between -0.48 and -0.41. The outlier is at 1.77. The differences between normal values are still visible.

**Lesson:** When you have outliers, standardization handles them better.

---

## 6.5 The Golden Rule: Fit on Train, Transform Both

This is the most important rule in feature scaling. Getting it wrong is a very common mistake.

### The Rule

```
+----------------------------------------------------------+
|                  THE GOLDEN RULE                          |
|                                                          |
|  1. FIT the scaler on TRAINING data only                 |
|  2. TRANSFORM the training data                          |
|  3. TRANSFORM the test data (using the SAME scaler)      |
|                                                          |
|  NEVER fit on test data!                                 |
+----------------------------------------------------------+
```

### Why This Rule Exists

When you fit a scaler, it learns the min, max, mean, and standard deviation from the data. If you fit on the test data, you are "peeking" at information you should not have during training. This is called **data leakage**.

Think of it this way. You are a teacher creating a grading curve. You set the curve based on this year's students (training data). When a transfer student arrives (test data), you grade them using the same curve. You do not change the curve to fit the new student.

```
CORRECT Workflow:
=================

Training Data                    Test Data
     |                               |
     v                               |
  scaler.fit()                       |
  (learn min/max/mean/std)           |
     |                               |
     v                               v
  scaler.transform()          scaler.transform()
  (scale training data)       (scale test data with
                               SAME parameters)

WRONG Workflow:
===============

Training Data          Test Data
     |                      |
     v                      v
  scaler.fit()         scaler.fit()      <-- WRONG! Do not fit again!
     |                      |
     v                      v
  scaler.transform()   scaler.transform()
```

### Correct Example

```python
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import numpy as np

# Create sample data
np.random.seed(42)
X = np.random.randn(100, 2) * [50, 10] + [100, 50]
y = np.random.randint(0, 2, 100)

# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training set size: {X_train.shape[0]}")
print(f"Test set size:     {X_test.shape[0]}")

# CORRECT: Fit on train, transform both
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # fit + transform
X_test_scaled = scaler.transform(X_test)         # transform only!

print(f"\nTraining data mean:  {np.round(X_train_scaled.mean(axis=0), 2)}")
print(f"Training data std:   {np.round(X_train_scaled.std(axis=0), 2)}")
print(f"Test data mean:      {np.round(X_test_scaled.mean(axis=0), 2)}")
print(f"Test data std:       {np.round(X_test_scaled.std(axis=0), 2)}")
```

**Expected Output:**
```
Training set size: 80
Test set size:     20

Training data mean:  [0. 0.]
Training data std:   [1. 1.]
Test data mean:      [-0.12  0.08]
Test data std:       [ 0.95  1.1 ]
```

**Line-by-line explanation:**

1. We create random data with 100 samples and 2 features.
2. We split into 80% training and 20% test data.
3. `scaler.fit_transform(X_train)` -- This fits the scaler on training data (learns mean and std) AND transforms it. The training data will have mean = 0 and std = 1 exactly.
4. `scaler.transform(X_test)` -- This only transforms. It uses the mean and std learned from training data. Notice we did NOT call `fit` again.
5. The test data mean and std are close to 0 and 1, but not exactly. That is normal and expected. The test data comes from a slightly different sample.

### The Common Mistake

```python
# WRONG - DO NOT DO THIS!
# scaler.fit_transform(X_test)  # This fits again on test data = DATA LEAKAGE!

# CORRECT
# scaler.transform(X_test)      # Uses the same parameters from training
```

---

## 6.6 Before and After: Seeing Scaling in Action

Let's see a complete example with visualization using text-based charts.

```python
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np

# Create a dataset: [income, age, credit_score]
np.random.seed(42)
data = np.column_stack([
    np.random.normal(50000, 15000, 20),  # income: mean 50k
    np.random.normal(35, 10, 20),         # age: mean 35
    np.random.normal(700, 50, 20)         # credit score: mean 700
])

feature_names = ['Income', 'Age', 'Credit Score']

print("=" * 55)
print("BEFORE SCALING")
print("=" * 55)
for i, name in enumerate(feature_names):
    col = data[:, i]
    print(f"\n{name}:")
    print(f"  Min:  {col.min():>10.1f}")
    print(f"  Max:  {col.max():>10.1f}")
    print(f"  Mean: {col.mean():>10.1f}")
    print(f"  Std:  {col.std():>10.1f}")

# Apply MinMax scaling
mm_scaler = MinMaxScaler()
data_minmax = mm_scaler.fit_transform(data)

print("\n" + "=" * 55)
print("AFTER MIN-MAX SCALING (0 to 1)")
print("=" * 55)
for i, name in enumerate(feature_names):
    col = data_minmax[:, i]
    print(f"\n{name}:")
    print(f"  Min:  {col.min():>10.4f}")
    print(f"  Max:  {col.max():>10.4f}")
    print(f"  Mean: {col.mean():>10.4f}")
    print(f"  Std:  {col.std():>10.4f}")

# Apply Standard scaling
std_scaler = StandardScaler()
data_standard = std_scaler.fit_transform(data)

print("\n" + "=" * 55)
print("AFTER STANDARDIZATION (mean=0, std=1)")
print("=" * 55)
for i, name in enumerate(feature_names):
    col = data_standard[:, i]
    print(f"\n{name}:")
    print(f"  Min:  {col.min():>10.4f}")
    print(f"  Max:  {col.max():>10.4f}")
    print(f"  Mean: {col.mean():>10.4f}")
    print(f"  Std:  {col.std():>10.4f}")
```

**Expected Output:**
```
=======================================================
BEFORE SCALING
=======================================================

Income:
  Min:   20654.1
  Max:   78587.4
  Mean:  49008.9
  Std:   14167.2

Age:
  Min:      14.5
  Max:      53.4
  Mean:     34.4
  Std:       9.6

Credit Score:
  Min:     601.6
  Max:     784.3
  Mean:    700.3
  Std:      47.3

=======================================================
AFTER MIN-MAX SCALING (0 to 1)
=======================================================

Income:
  Min:      0.0000
  Max:      1.0000
  Mean:     0.4896
  Std:      0.2447

Age:
  Min:      0.0000
  Max:      1.0000
  Mean:     0.5115
  Std:      0.2468

Credit Score:
  Min:      0.0000
  Max:      1.0000
  Mean:     0.5403
  Std:      0.2590

=======================================================
AFTER STANDARDIZATION (mean=0, std=1)
=======================================================

Income:
  Min:     -2.0005
  Max:      2.0881
  Mean:     0.0000
  Std:      1.0000

Age:
  Min:     -2.0755
  Max:      1.9835
  Mean:     0.0000
  Std:      1.0000

Credit Score:
  Min:     -2.0859
  Max:      1.7755
  Mean:     0.0000
  Std:      1.0000
```

**What to notice:**

- **Before scaling:** Income is in the tens of thousands. Age is in the tens. Credit scores are in the hundreds. Totally different scales.
- **After Min-Max:** All three features range from 0 to 1. They are now comparable.
- **After Standardization:** All three features have mean = 0 and std = 1. They are centered and equally spread.

### ASCII Visualization: Feature Ranges

```
BEFORE SCALING:
                    0         20k        40k        60k        80k
Income:             |==========[====================]============|
Age:                [=======]
Credit Score:                                          [========]

Each feature lives on a completely different part of the number line.


AFTER MIN-MAX SCALING:
                    0.0       0.25       0.5        0.75       1.0
Income:             [================================================]
Age:                [================================================]
Credit Score:       [================================================]

All features now share the same 0-to-1 range.


AFTER STANDARDIZATION:
                   -2.0      -1.0       0.0        1.0        2.0
Income:             [================================================]
Age:                [================================================]
Credit Score:       [================================================]

All features centered at 0 with similar spread.
```

---

## 6.7 Complete Workflow Example

Here is a complete example that brings everything together. We scale features and use them with KNN.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_wine
import numpy as np

# Load the wine dataset
wine = load_wine()
X = wine.data
y = wine.target

print(f"Dataset shape: {X.shape}")
print(f"Number of classes: {len(np.unique(y))}")
print(f"\nFeature ranges before scaling:")
print(f"{'Feature':<30} {'Min':>8} {'Max':>8}")
print("-" * 48)
for i, name in enumerate(wine.feature_names):
    print(f"{name:<30} {X[:, i].min():>8.2f} {X[:, i].max():>8.2f}")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# WITHOUT scaling
knn_no_scale = KNeighborsClassifier(n_neighbors=5)
knn_no_scale.fit(X_train, y_train)
score_no_scale = knn_no_scale.score(X_test, y_test)

# WITH scaling (correct way)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

knn_scaled = KNeighborsClassifier(n_neighbors=5)
knn_scaled.fit(X_train_scaled, y_train)
score_scaled = knn_scaled.score(X_test_scaled, y_test)

print(f"\nKNN Accuracy WITHOUT scaling: {score_no_scale:.4f}")
print(f"KNN Accuracy WITH scaling:    {score_scaled:.4f}")
print(f"Improvement:                  {score_scaled - score_no_scale:+.4f}")
```

**Expected Output:**
```
Dataset shape: (178, 13)
Number of classes: 3

Feature ranges before scaling:
Feature                             Min      Max
------------------------------------------------
alcohol                           11.03    14.83
malic_acid                         0.74     5.80
ash                                1.36     3.23
alcalinity_of_ash                 10.60    30.00
magnesium                         70.00   162.00
total_phenols                      0.98     3.88
flavanoids                         0.34     5.08
nonflavanoid_phenols               0.13     0.66
proanthocyanins                    0.41     3.58
color_intensity                    1.28    13.00
hue                                0.48     1.71
od280/od315_of_diluted_wines       1.27     4.00
proline                          278.00  1680.00

KNN Accuracy WITHOUT scaling: 0.6944
KNN Accuracy WITH scaling:    0.9722
Improvement:                  +0.2778
```

**This is dramatic!** The same KNN model jumps from about 69% accuracy to 97% accuracy just by scaling the features. The "proline" feature ranges from 278 to 1680, while "hue" ranges from 0.48 to 1.71. Without scaling, KNN almost entirely ignores the smaller features.

---

## Common Mistakes

1. **Fitting the scaler on the entire dataset before splitting.** This leaks test data information into the training process. Always split first, then fit on training data only.

2. **Fitting the scaler again on test data.** Use `scaler.transform(X_test)`, not `scaler.fit_transform(X_test)`. The scaler must use the same parameters it learned from training data.

3. **Scaling the target variable (y).** You typically do not scale the labels or target. Only scale the input features (X).

4. **Scaling features for tree-based models unnecessarily.** Decision trees, random forests, and gradient boosted trees do not need scaling. It will not hurt, but it wastes time.

5. **Forgetting to apply the same scaling when making predictions on new data.** If you trained with a scaler, you must scale new data with that same scaler before predicting.

6. **Using Min-Max when data has outliers.** Outliers will squash all normal values into a tiny range. Use standardization instead.

---

## Best Practices

1. **Default to StandardScaler.** It works well for most algorithms and handles outliers better than Min-Max.

2. **Use MinMaxScaler for neural networks.** Neural networks often work better with values in the 0-1 range.

3. **Save your scaler.** After training, save the scaler object (using joblib or pickle) along with your model. You will need it to scale new data during prediction.

4. **Check your data ranges after scaling.** A quick print of min, max, mean, and std confirms the scaling worked correctly.

5. **Scale after train-test split, not before.** This prevents data leakage.

6. **Use pipelines.** sklearn Pipelines combine scaling and modeling into one step, reducing the chance of mistakes. (We will cover pipelines in a later chapter.)

---

## Quick Summary

Feature scaling puts all features on a similar range so models can treat them fairly.

- **Min-Max Normalization** squeezes values into 0 to 1. Best for neural networks and when you need bounded values. Sensitive to outliers.
- **Standardization (Z-Score)** centers data at mean = 0 with std = 1. Best for most ML algorithms. More robust to outliers.
- **Tree-based models** (Decision Trees, Random Forests, XGBoost) do not need scaling.
- **Distance-based models** (KNN, SVM) and **gradient-based models** (Neural Networks, Linear Regression) benefit greatly from scaling.
- **Golden Rule:** Fit the scaler on training data only. Transform both training and test data with the same scaler.

---

## Key Points to Remember

1. Features on different scales can mislead distance-based and gradient-based models.
2. Min-Max Normalization maps values to [0, 1]. Formula: (value - min) / (max - min).
3. Standardization maps values to mean = 0, std = 1. Formula: (value - mean) / std.
4. Standardization is the safer default because it handles outliers better.
5. Always fit on training data, then transform both train and test.
6. Never fit the scaler on test data -- that causes data leakage.
7. Tree-based models do not need scaling. KNN, SVM, and neural networks do.
8. Scaling can dramatically improve model accuracy (as we saw with the wine dataset).

---

## Practice Questions

### Question 1
What is the Min-Max scaled value of 60 if the minimum is 20 and the maximum is 100?

**Answer:** (60 - 20) / (100 - 20) = 40 / 80 = 0.5

### Question 2
After standardization, what is the mean and standard deviation of the transformed data?

**Answer:** The mean is 0 and the standard deviation is 1. That is the entire point of standardization -- it centers the data at zero and scales the spread to one.

### Question 3
You are training a Random Forest model. Should you scale your features?

**Answer:** No, it is not necessary. Random Forests are tree-based models. They make decisions based on feature value thresholds (greater than or less than), not distances. Scaling will not change the results.

### Question 4
Your dataset has a feature "annual salary" that ranges from 20,000 to 5,000,000 (most people earn 40,000-80,000 but a few CEOs earn millions). Which scaling method should you use?

**Answer:** Standardization (StandardScaler). The CEO salaries are outliers. Min-Max would squash most salaries near zero (because the max is 5,000,000). Standardization handles this better because it is based on mean and standard deviation, not min and max.

### Question 5
What is wrong with this code?

```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)        # Scale ALL data
X_train, X_test = train_test_split(X_scaled)  # Then split
```

**Answer:** The scaler was fit on the entire dataset (including test data) before splitting. This is data leakage. The correct approach is to split first, then fit the scaler on training data only, then transform both sets.

---

## Exercises

### Exercise 1: Manual Scaling
Given the data `[100, 200, 300, 400, 500]`:
1. Calculate the Min-Max scaled values by hand.
2. Calculate the mean and standard deviation.
3. Calculate the standardized (z-score) values by hand.
4. Verify your answers using sklearn's MinMaxScaler and StandardScaler.

### Exercise 2: Scaling Impact on KNN
1. Load the Iris dataset (`from sklearn.datasets import load_iris`).
2. Split into train and test sets (80/20).
3. Train a KNN classifier (k=5) WITHOUT scaling. Record accuracy.
4. Train a KNN classifier (k=5) WITH StandardScaler. Record accuracy.
5. Compare the results. Did scaling help? Why or why not?

### Exercise 3: Outlier Investigation
1. Create a dataset with 100 normal values between 0 and 100.
2. Add 5 outlier values of 10,000.
3. Apply both MinMaxScaler and StandardScaler.
4. Print the scaled values for a few normal data points.
5. Which scaler preserved the differences between normal values better?

---

## What Is Next?

Your features are now properly scaled. But what about features that are not numbers at all? Words like "red," "blue," and "green" cannot be scaled -- they need to be converted to numbers first.

In the next chapter, you will learn how to handle categorical variables. You will discover Label Encoding, One-Hot Encoding, and when to use each approach. This is another essential preprocessing step that you will use in almost every real-world project.
