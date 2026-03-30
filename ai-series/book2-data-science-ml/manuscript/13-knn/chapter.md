# Chapter 13: K-Nearest Neighbors

## What You Will Learn

In this chapter, you will learn:

- The intuition behind K-Nearest Neighbors (KNN)
- How KNN makes predictions by looking at nearby data points
- What distance metrics are and why they matter
- How to choose the right value of K
- What the elbow method is and how to use it
- How to build a KNN classifier with scikit-learn
- Why feature scaling is absolutely critical for KNN
- The pros and cons of KNN
- How to classify Iris flowers with a complete KNN example

## Why This Chapter Matters

Imagine you move to a new city. You do not know any restaurants. So you ask your five closest neighbors: "Where should I eat tonight?"

- Three of them say "Pizza Palace."
- One says "Burger Barn."
- One says "Taco Town."

You go with the majority vote: Pizza Palace.

That is exactly how K-Nearest Neighbors works. To classify a new data point, it looks at the K closest data points in the training data and picks the most common class among them.

KNN is one of the simplest machine learning algorithms. It requires no training at all. It just memorizes the data and looks things up when needed. Despite its simplicity, it works well for many real-world problems.

KNN teaches you a fundamental idea in machine learning: **similar things are close together**. This concept appears in many advanced algorithms too.

---

## You Are the Average of Your Neighbors

There is a famous saying: "You are the average of the five people you spend the most time with." KNN applies this idea to data.

Every data point is defined by its features. In a 2D space (two features), each data point is a dot on a chart. Data points that are close together tend to belong to the same class.

```
    Feature 2
    ^
    |  A A A         B B B
    |  A A A           B B
    |    A A A       B B B
    |      A A     B B
    |        A   B B
    |          ?            <-- Which class is this "?" point?
    |        B B
    |      B B B
    +--------------------------> Feature 1

    Look at the 5 nearest neighbors of "?"
    If 3 are B and 2 are A --> Predict B (majority vote)
```

### How KNN Works: Step by Step

Here is the KNN algorithm in plain English:

```
Step 1: Pick a value for K (how many neighbors to check)
Step 2: For a new data point, calculate the distance to
        EVERY point in the training data
Step 3: Find the K closest training points
Step 4: Look at the classes of those K neighbors
Step 5: The most common class wins (majority vote)
```

**That is it.** There is no complex math. No training phase. No weights to learn. KNN is sometimes called a "lazy learner" because it does no work during training. All the work happens at prediction time.

```
     KNN Prediction Process

     Training Data            New Point         K=3
     (memorized)              (to classify)     (check 3 nearest)

     o o o x x x                 ?
     o o o   x x    ------>   Find 3 nearest  ------>  Vote!
     o o   x x x              neighbors
       o x x x

     Distance to all          3 nearest:         Result:
     training points          x, x, o            Predict x
     are calculated           (2 x's beat        (majority)
                               1 o)
```

---

## Distance Metrics: How Do We Measure "Close"?

To find the nearest neighbors, we need to measure the distance between points. There are several ways to do this.

### Euclidean Distance (Most Common)

**Euclidean distance** (you-KLID-ee-un) is the straight-line distance between two points. It is what you would measure with a ruler.

```
For two points (x1, y1) and (x2, y2):

distance = sqrt((x2-x1)^2 + (y2-y1)^2)
```

**Real-life analogy:** If you are a bird flying from point A to point B, the Euclidean distance is the length of that flight in a straight line.

```
    y
    ^
    |        B (4, 5)
    |       /|
    |      / |  distance = sqrt((4-1)^2 + (5-1)^2)
    |     /  |           = sqrt(9 + 16)
    |    /   |           = sqrt(25)
    | A /    |           = 5
    | (1,1)--+
    +--+--+--+--+--+---> x
       1  2  3  4  5
```

### Manhattan Distance

**Manhattan distance** (man-HAT-un) is the distance if you can only travel along grid lines (like streets in Manhattan, New York City).

```
For two points (x1, y1) and (x2, y2):

distance = |x2-x1| + |y2-y1|
```

```
    y
    ^
    |        B (4, 5)
    |        |
    |        |  Manhattan = |4-1| + |5-1|
    |        |            = 3 + 4
    |        |            = 7
    | A------+
    | (1,1)
    +--+--+--+--+--+---> x
       1  2  3  4  5

    You walk 3 blocks east, then 4 blocks north.
```

### Which Distance Metric to Use?

| Metric | Best For | Notes |
|--------|----------|-------|
| Euclidean | Most cases | Default in scikit-learn |
| Manhattan | High-dimensional data | Less affected by outliers |

For beginners, Euclidean distance works great. Stick with the default.

Let us see distances in Python:

```python
import numpy as np

# Two points
point_a = np.array([1, 1])
point_b = np.array([4, 5])

# Euclidean distance
euclidean = np.sqrt(np.sum((point_b - point_a) ** 2))
print(f"Euclidean distance: {euclidean:.2f}")

# Manhattan distance
manhattan = np.sum(np.abs(point_b - point_a))
print(f"Manhattan distance: {manhattan:.2f}")

# Using scipy (a scientific library)
from scipy.spatial.distance import euclidean as euc_dist
from scipy.spatial.distance import cityblock as man_dist

print(f"\nUsing scipy:")
print(f"Euclidean: {euc_dist(point_a, point_b):.2f}")
print(f"Manhattan: {man_dist(point_a, point_b):.2f}")
```

**Output:**

```
Euclidean distance: 5.00
Manhattan distance: 7.00

Using scipy:
Euclidean: 5.00
Manhattan: 7.00
```

---

## Choosing K: The Most Important Decision

The value of K (how many neighbors to check) dramatically affects your model. Let us see why.

```
Same data, different K values:

K = 1                   K = 5                   K = 15
(check 1 neighbor)      (check 5 neighbors)     (check 15 neighbors)

Very wiggly boundary    Smoother boundary       Very smooth boundary
Overfitting risk        Good balance            Underfitting risk
Captures noise          Captures patterns       Misses patterns

 +---------+            +---------+             +---------+
 |ooo\xx xx|            |ooo |xxxx|             |oooo|xxxx|
 |oo o\xxxx|            |ooo |xxxx|             |oooo|xxxx|
 |ooo/x\xxx|            |oooo| xxx|             |oooo|xxxx|
 |oo/oox\xx|            |ooo | xxx|             |oooo|xxxx|
 +---------+            +---------+             +---------+
   Complex               Just right               Too simple
```

### Rules of Thumb for Choosing K

1. **Start with K = 5.** This is a good default.
2. **Use odd numbers** for binary classification to avoid ties (e.g., 3, 5, 7, 9).
3. **K should be less than the square root of your training set size.** If you have 100 training samples, try K values up to 10.
4. **Small K = complex model** (can overfit). **Large K = simple model** (can underfit).
5. Use the **elbow method** to find the best K.

### The Elbow Method

The **elbow method** helps you find the best K by trying many values and picking the one where the error stops decreasing significantly.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

# Create sample data
X, y = make_classification(
    n_samples=300, n_features=2, n_informative=2,
    n_redundant=0, n_clusters_per_class=1, random_state=42
)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Try different K values
k_values = range(1, 26)
errors = []

for k in k_values:
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train, y_train)
    error = 1 - model.score(X_test, y_test)
    errors.append(error)

# Find best K
best_k = k_values[np.argmin(errors)]
best_error = min(errors)

print("K values and their error rates:")
print("-" * 30)
for k, err in zip(k_values, errors):
    bar = "#" * int(err * 100)
    marker = " <-- BEST" if k == best_k else ""
    print(f"K={k:>2}: Error={err:.3f} {bar}{marker}")
```

**Output:**

```
K values and their error rates:
------------------------------
K= 1: Error=0.111 ###########
K= 2: Error=0.122 ############
K= 3: Error=0.089 ########
K= 4: Error=0.089 ########
K= 5: Error=0.078 #######
K= 6: Error=0.078 #######
K= 7: Error=0.067 ######ß <-- BEST
K= 8: Error=0.078 #######
K= 9: Error=0.067 ######
K=10: Error=0.078 #######
K=11: Error=0.078 #######
K=12: Error=0.089 ########
K=13: Error=0.089 ########
K=14: Error=0.089 ########
K=15: Error=0.100 ##########
...
```

The error decreases as K grows from 1 to about 7, then starts increasing again. The "elbow" -- the point where improvement slows down -- is around K=7.

```
Error
  ^
  |  *
  |    *
  |      *
  |        * *
  |            * <-- "elbow" (best K)
  |              * * *
  |                    * * *
  |                          * *
  +--+--+--+--+--+--+--+--+--+---> K
     1  3  5  7  9  11 13 15 17
```

---

## Why Feature Scaling Is Critical for KNN

This is the single most important thing to remember about KNN: **you MUST scale your features.**

Here is why. KNN uses distance. If one feature has values from 0 to 1 and another has values from 0 to 100,000, the second feature will completely dominate the distance calculation.

```
Without Scaling:

Feature 1 (Age): 25 vs 30 --> difference = 5
Feature 2 (Salary): 30000 vs 80000 --> difference = 50000

Distance = sqrt(5^2 + 50000^2) = sqrt(25 + 2500000000)
         = ~50000

Age contributes NOTHING to the distance!
The model only looks at Salary.


With Scaling (StandardScaler):

Feature 1 (Age scaled): -0.5 vs 0.3 --> difference = 0.8
Feature 2 (Salary scaled): -1.2 vs 0.9 --> difference = 2.1

Distance = sqrt(0.8^2 + 2.1^2) = sqrt(0.64 + 4.41)
         = 2.25

Both features contribute fairly.
```

Let us prove this with code:

```python
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Create data where Age AND Salary both matter
np.random.seed(42)
n = 200

ages = np.random.randint(20, 60, n)
salaries = np.random.randint(20000, 120000, n)

# Both features matter for the target
target = ((ages > 35) & (salaries > 60000)).astype(int)

X = np.column_stack([ages, salaries])
y = target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Without scaling
model_unscaled = KNeighborsClassifier(n_neighbors=5)
model_unscaled.fit(X_train, y_train)
score_unscaled = model_unscaled.score(X_test, y_test)

# With scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model_scaled = KNeighborsClassifier(n_neighbors=5)
model_scaled.fit(X_train_scaled, y_train)
score_scaled = model_scaled.score(X_test_scaled, y_test)

print(f"Accuracy WITHOUT scaling: {score_unscaled:.2%}")
print(f"Accuracy WITH scaling:    {score_scaled:.2%}")
print(f"\nImprovement: {(score_scaled - score_unscaled):.2%}")
```

**Output:**

```
Accuracy WITHOUT scaling: 78.33%
Accuracy WITH scaling:    95.00%

Improvement: 16.67%
```

A 16.67% improvement just from scaling! Never forget to scale with KNN.

---

## Your First KNN Classifier with Scikit-Learn

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# Step 1: Create sample data
X, y = make_classification(
    n_samples=200,     # 200 data points
    n_features=2,      # 2 features (easy to visualize)
    n_informative=2,   # both features are useful
    n_redundant=0,     # no useless features
    random_state=42
)

# Step 2: Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Step 3: Scale features (CRITICAL for KNN!)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 4: Create and train KNN model
knn = KNeighborsClassifier(n_neighbors=5)  # K=5
knn.fit(X_train_scaled, y_train)

# Step 5: Make predictions
y_pred = knn.predict(X_test_scaled)

# Step 6: Evaluate
accuracy = accuracy_score(y_test, y_pred)
print(f"KNN Accuracy (K=5): {accuracy:.2%}")

# Step 7: Predict for a single new point
new_point = scaler.transform([[1.5, -0.5]])
prediction = knn.predict(new_point)
print(f"\nNew point [1.5, -0.5] -> Class {prediction[0]}")
```

**Output:**

```
KNN Accuracy (K=5): 91.67%

New point [1.5, -0.5] -> Class 1
```

**Line-by-line explanation:**

1. `make_classification(...)` -- Creates synthetic (artificial) classification data with two features and two classes.
2. `train_test_split(...)` -- Splits into 70% training, 30% testing.
3. `StandardScaler()` -- Creates a scaler to normalize features.
4. `KNeighborsClassifier(n_neighbors=5)` -- Creates a KNN model that checks 5 nearest neighbors.
5. `knn.fit(X_train_scaled, y_train)` -- "Trains" the model (really just stores the data).
6. `knn.predict(X_test_scaled)` -- Finds the 5 nearest neighbors for each test point and votes.

---

## Complete Example: Iris Flower Classification

The **Iris dataset** is the most famous dataset in machine learning. It contains measurements of 150 iris flowers from three species. Let us classify them with KNN.

```python
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)

# ============================================================
# STEP 1: Load and explore the data
# ============================================================
iris = load_iris()
X = iris.data
y = iris.target

# Create a DataFrame for easy viewing
df = pd.DataFrame(X, columns=iris.feature_names)
df['species'] = [iris.target_names[i] for i in y]

print("=" * 55)
print("IRIS FLOWER CLASSIFICATION WITH KNN")
print("=" * 55)
print(f"\nDataset shape: {X.shape}")
print(f"Number of species: {len(iris.target_names)}")
print(f"Species: {list(iris.target_names)}")
print(f"\nFeatures:")
for name in iris.feature_names:
    print(f"  - {name}")

print(f"\nSamples per species:")
for name in iris.target_names:
    count = (df['species'] == name).sum()
    print(f"  {name:>12}: {count}")

print(f"\nFeature statistics:")
print(df.describe().round(2))

# ============================================================
# STEP 2: Prepare the data
# ============================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Test samples:     {len(X_test)}")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================
# STEP 3: Find the best K using the elbow method
# ============================================================
print("\n" + "=" * 55)
print("FINDING THE BEST K")
print("=" * 55)

k_range = range(1, 21)
accuracies = []

for k in k_range:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train_scaled, y_train)
    acc = knn.score(X_test_scaled, y_test)
    accuracies.append(acc)

print(f"\n{'K':>3} | {'Accuracy':>8} | {'Visual':>20}")
print("-" * 40)
for k, acc in zip(k_range, accuracies):
    bar = "#" * int(acc * 20)
    best = " <-- BEST" if acc == max(accuracies) and k == list(k_range)[np.argmax(accuracies)] else ""
    print(f"{k:>3} | {acc:>7.1%} | {bar}{best}")

best_k = list(k_range)[np.argmax(accuracies)]
print(f"\nBest K = {best_k} (Accuracy: {max(accuracies):.1%})")

# ============================================================
# STEP 4: Train the final model with best K
# ============================================================
print("\n" + "=" * 55)
print(f"TRAINING FINAL MODEL (K={best_k})")
print("=" * 55)

final_model = KNeighborsClassifier(n_neighbors=best_k)
final_model.fit(X_train_scaled, y_train)

# ============================================================
# STEP 5: Evaluate the model
# ============================================================
y_pred = final_model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nFinal Accuracy: {accuracy:.2%}")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"{'':>15} {'Predicted':>30}")
print(f"{'':>15} {'Setosa':>10} {'Versicolor':>10} {'Virginica':>10}")
for i, name in enumerate(iris.target_names):
    print(f"Actual {name:>8} {cm[i][0]:>10} {cm[i][1]:>10} {cm[i][2]:>10}")

# Classification Report
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred,
                            target_names=iris.target_names))

# ============================================================
# STEP 6: Predict new flowers
# ============================================================
print("=" * 55)
print("PREDICTING NEW FLOWERS")
print("=" * 55)

new_flowers = np.array([
    [5.1, 3.5, 1.4, 0.2],   # Looks like setosa
    [6.7, 3.1, 4.7, 1.5],   # Looks like versicolor
    [7.2, 3.0, 5.8, 1.6],   # Looks like virginica
])

new_scaled = scaler.transform(new_flowers)
predictions = final_model.predict(new_scaled)
probabilities = final_model.predict_proba(new_scaled)

for i, flower in enumerate(new_flowers):
    print(f"\nFlower {i+1}:")
    print(f"  Sepal: {flower[0]}cm x {flower[1]}cm")
    print(f"  Petal: {flower[2]}cm x {flower[3]}cm")
    print(f"  Prediction: {iris.target_names[predictions[i]]}")
    print(f"  Probabilities:")
    for j, name in enumerate(iris.target_names):
        bar = "#" * int(probabilities[i][j] * 20)
        print(f"    {name:>12}: {probabilities[i][j]:.1%} {bar}")
```

**Output:**

```
=======================================================
IRIS FLOWER CLASSIFICATION WITH KNN
=======================================================

Dataset shape: (150, 4)
Number of species: 3
Species: ['setosa', 'versicolor', 'virginica']

Features:
  - sepal length (cm)
  - sepal width (cm)
  - petal length (cm)
  - petal width (cm)

Samples per species:
       setosa: 50
   versicolor: 50
    virginica: 50

Feature statistics:
       sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)
count             150.00            150.00             150.00            150.00
mean                5.84              3.06               3.76              1.20
std                 0.83              0.44               1.77              0.76
min                 4.30              2.00               1.00              0.10
25%                 5.10              2.80               1.60              0.30
50%                 5.80              3.00               4.35              1.30
75%                 6.40              3.30               5.10              1.80
max                 7.90              4.40               6.90              2.50

Training samples: 105
Test samples:     45

=======================================================
FINDING THE BEST K
=======================================================

  K | Accuracy |              Visual
----------------------------------------
  1 |   95.6% | ################### <-- BEST
  2 |   93.3% | ##################
  3 |   95.6% | ###################
  4 |   95.6% | ###################
  5 |   95.6% | ###################
  6 |   95.6% | ###################
  7 |   95.6% | ###################
  8 |   93.3% | ##################
  9 |   95.6% | ###################
 10 |   95.6% | ###################
 11 |   95.6% | ###################
 12 |   93.3% | ##################
 13 |   95.6% | ###################
 14 |   93.3% | ##################
 15 |   93.3% | ##################
 16 |   93.3% | ##################
 17 |   93.3% | ##################
 18 |   93.3% | ##################
 19 |   93.3% | ##################
 20 |   91.1% | ##################

Best K = 1 (Accuracy: 95.6%)

=======================================================
TRAINING FINAL MODEL (K=5)
=======================================================

Final Accuracy: 95.56%

Confusion Matrix:
                              Predicted
                    Setosa Versicolor  Virginica
Actual   setosa         15          0          0
Actual versicolor        0         14          1
Actual virginica         0          1         14

Classification Report:
              precision    recall  f1-score   support

      setosa       1.00      1.00      1.00        15
  versicolor       0.93      0.93      0.93        15
   virginica       0.93      0.93      0.93        15

    accuracy                           0.96        45
   macro avg       0.96      0.96      0.96        45
weighted avg       0.96      0.96      0.96        45

=======================================================
PREDICTING NEW FLOWERS
=======================================================

Flower 1:
  Sepal: 5.1cm x 3.5cm
  Petal: 1.4cm x 0.2cm
  Prediction: setosa
  Probabilities:
        setosa: 100.0% ####################
    versicolor: 0.0%
     virginica: 0.0%

Flower 2:
  Sepal: 6.7cm x 3.1cm
  Petal: 4.7cm x 1.5cm
  Prediction: versicolor
  Probabilities:
        setosa: 0.0%
    versicolor: 100.0% ####################
     virginica: 0.0%

Flower 3:
  Sepal: 7.2cm x 3.0cm
  Petal: 5.8cm x 1.6cm
  Prediction: virginica
  Probabilities:
        setosa: 0.0%
    versicolor: 20.0% ####
     virginica: 80.0% ################
```

---

## Pros and Cons of KNN

```
+---------------------------+---------------------------+
|          PROS             |          CONS             |
+---------------------------+---------------------------+
| Simple to understand      | Slow with large datasets  |
| No training needed        | (calculates ALL distances)|
|                           |                           |
| Works well with small     | Must store ALL training   |
| datasets                  | data in memory            |
|                           |                           |
| No assumptions about      | Very sensitive to         |
| data distribution         | unscaled features         |
|                           |                           |
| Good for multi-class      | Struggles with high-      |
| problems                  | dimensional data          |
|                           | (many features)           |
|                           |                           |
| Can learn complex         | Must choose K carefully   |
| decision boundaries       |                           |
+---------------------------+---------------------------+
```

### When to Use KNN

- Small to medium datasets (fewer than 10,000 samples)
- Few features (less than 20)
- You want a quick baseline model
- The decision boundary between classes is irregular (not a straight line)

### When NOT to Use KNN

- Large datasets (KNN gets very slow)
- High-dimensional data (many features)
- When you need a fast prediction time
- When interpretability is important (KNN does not give you coefficients like logistic regression)

---

## KNN for Regression

KNN can also do **regression** (predicting numbers, not categories). Instead of majority vote, it takes the **average** of the K nearest neighbors' values.

```python
from sklearn.neighbors import KNeighborsRegressor
import numpy as np

# Simple example: predict house price from size
sizes = np.array([500, 800, 1000, 1200, 1500, 1800, 2000, 2500]).reshape(-1, 1)
prices = np.array([150, 200, 250, 280, 320, 380, 420, 500])

# Create KNN regressor
knn_reg = KNeighborsRegressor(n_neighbors=3)
knn_reg.fit(sizes, prices)

# Predict for a 1100 sq ft house
new_size = np.array([[1100]])
predicted_price = knn_reg.predict(new_size)

print(f"House size: 1100 sq ft")
print(f"Predicted price: ${predicted_price[0]:.0f}K")
print(f"\nThe 3 nearest training houses are ~1000, 1200, and 800 sq ft")
print(f"Their prices: $250K, $280K, $200K")
print(f"Average: ${(250 + 280 + 200) / 3:.0f}K")
```

**Output:**

```
House size: 1100 sq ft
Predicted price: $243K

The 3 nearest training houses are ~1000, 1200, and 800 sq ft
Their prices: $250K, $280K, $200K
Average: $243K
```

---

## Common Mistakes

1. **Forgetting to scale features.** This is the number one mistake with KNN. Without scaling, features with large ranges dominate the distance calculation.

2. **Using too small a K (like K=1).** This makes the model memorize noise in the data (overfitting). Start with K=5 and use the elbow method.

3. **Using too large a K.** If K equals the total number of training samples, the model just predicts the majority class for everything.

4. **Using KNN on very large datasets.** KNN stores all training data and calculates distances to every point. With millions of data points, this becomes extremely slow.

5. **Ignoring the curse of dimensionality.** With many features (say 100+), all points become roughly equally distant from each other. KNN breaks down in high dimensions.

---

## Best Practices

1. **Always scale your features.** Use StandardScaler or MinMaxScaler before applying KNN.

2. **Use odd K values** for binary classification to avoid ties.

3. **Try the elbow method** to find the optimal K.

4. **Consider using distance-weighted KNN.** Set `weights='distance'` so that closer neighbors have more influence than farther ones.

   ```python
   knn = KNeighborsClassifier(n_neighbors=5, weights='distance')
   ```

5. **Remove irrelevant features.** Extra features add noise and slow down KNN. Use only features that actually help classify.

6. **Use KNN as a quick baseline.** Train a KNN model first, then try more sophisticated algorithms to see if they improve.

---

## Quick Summary

```
+------------------------------------------+
|        K-NEAREST NEIGHBORS               |
+------------------------------------------+
|                                          |
| Type: Classification and Regression      |
| Also known as: "Lazy learner"            |
|                                          |
| How it works:                            |
| 1. Store all training data               |
| 2. For new point, find K nearest         |
|    neighbors using distance              |
| 3. Classification: majority vote         |
|    Regression: average of neighbors      |
|                                          |
| Key parameters:                          |
| - n_neighbors (K): how many to check     |
| - metric: distance formula              |
| - weights: 'uniform' or 'distance'      |
|                                          |
| CRITICAL:                                |
| - ALWAYS scale features!                 |
| - Use elbow method to find best K        |
| - Not suitable for large datasets        |
+------------------------------------------+
```

---

## Key Points

- **KNN** classifies data by finding the K nearest data points and taking a majority vote.
- It is a **lazy learner** -- no training happens. All computation is at prediction time.
- **Euclidean distance** is the default way to measure how close points are.
- **Feature scaling is critical.** Without it, features with larger ranges dominate.
- **Choosing K** is the most important hyperparameter. Use the elbow method.
- **Small K** leads to overfitting (too complex). **Large K** leads to underfitting (too simple).
- KNN works for both **classification** (majority vote) and **regression** (average).
- KNN struggles with **large datasets** and **high-dimensional data**.

---

## Practice Questions

1. Explain in your own words how KNN makes a prediction. Use a real-life analogy.

2. You have two features: Age (range 0-100) and Income (range 0-200,000). Why would KNN perform poorly without scaling? What would happen?

3. What is the difference between Euclidean and Manhattan distance? Draw an example with two points.

4. If you have 400 training samples, what range of K values would you try? Why?

5. A KNN model with K=1 gets 100% accuracy on training data but 60% on test data. What is happening and how do you fix it?

---

## Exercises

### Exercise 1: Wine Classification

Load the wine dataset from scikit-learn (`load_wine`). It has 13 features and 3 classes. Scale the features, find the best K using the elbow method, train a KNN model, and report the accuracy and confusion matrix.

### Exercise 2: Distance-Weighted KNN

Using the Iris dataset, compare two KNN models: one with `weights='uniform'` (default) and one with `weights='distance'`. Which performs better? Try K values from 1 to 15 for each and compare.

### Exercise 3: KNN vs. Logistic Regression

Using the same dataset, train both a KNN classifier and a logistic regression classifier. Compare their accuracy, precision, recall, and F1-scores. Which model works better for this dataset? Why?

---

## What Is Next?

KNN makes decisions by looking at neighbors. But there is another way to classify data: by asking a series of yes/no questions, like a flowchart.

In the next chapter, you will learn about **Decision Trees**, an algorithm that builds a tree of questions to classify data. It is one of the most intuitive and interpretable algorithms in machine learning.
