# Chapter 15: Random Forests

## What You Will Learn

In this chapter, you will learn:

- Why one tree is fragile but many trees are powerful
- What "wisdom of crowds" means in machine learning
- How bagging (bootstrap aggregating) works
- How random feature selection adds diversity
- How majority voting produces final predictions
- How to build a Random Forest with scikit-learn
- How to tune `n_estimators` and `max_depth`
- How to read feature importance from a forest
- What the Out-of-Bag (OOB) score is and why it is useful
- How to build a complete customer churn prediction system

## Why This Chapter Matters

Imagine you are sick. You visit one doctor. That doctor gives a diagnosis. But you are not sure. So you visit five more doctors. If four out of five say the same thing, you feel much more confident.

That is exactly what a Random Forest does. Instead of building one decision tree, it builds **hundreds** of trees and lets them **vote**. The majority wins.

Random Forests are one of the most popular and powerful algorithms in machine learning. They work well "out of the box" with minimal tuning. They handle missing data, outliers, and complex patterns. Many data science competitions have been won with Random Forests.

If you learn only one algorithm after this book, make it Random Forest.

---

## The Wisdom of Crowds

In 1906, a scientist named Francis Galton visited a county fair. People were guessing the weight of an ox. No single person guessed correctly. But when Galton averaged all the guesses, the average was almost exactly right.

This is the **wisdom of crowds**: a group of independent decision-makers, each making imperfect decisions, can collectively make excellent decisions.

```
One Tree:           Many Trees (Forest):

  Single             Tree1  Tree2  Tree3  Tree4  Tree5
  Expert               |      |      |      |      |
    |                   v      v      v      v      v
    v                  Cat    Dog    Cat    Cat    Dog
   Cat
                       Vote: Cat wins (3 vs 2)!
 Might be
 wrong!              Much more likely to be right!
```

A Random Forest applies this principle. Each tree might be imperfect, but together they make much better predictions than any single tree.

---

## How Random Forests Work

A Random Forest combines two key ideas:

### Idea 1: Bagging (Bootstrap Aggregating)

**Bagging** (BAG-ing) stands for **B**ootstrap **Agg**regat**ing**. Here is how it works:

1. Take your training data (say 1000 samples)
2. Randomly pick 1000 samples WITH replacement (some samples get picked multiple times, some not at all)
3. This creates a "bootstrap sample" -- a slightly different version of your data
4. Build a decision tree on this bootstrap sample
5. Repeat steps 2-4 many times (e.g., 100 times)
6. Each tree sees a slightly different version of the data

```
Original Data: [A, B, C, D, E, F, G, H, I, J]

Bootstrap Sample 1: [A, A, C, D, D, F, G, G, I, J]  --> Tree 1
Bootstrap Sample 2: [B, B, C, D, E, F, F, H, I, I]  --> Tree 2
Bootstrap Sample 3: [A, C, C, D, E, E, G, H, J, J]  --> Tree 3
...

Each tree sees a different random subset!
About 63% of samples appear in each bootstrap sample.
About 37% are left out (these become OOB samples).
```

**Why does this help?** Each tree learns slightly different patterns. When they vote together, individual mistakes get canceled out.

**Real-life analogy:** If you ask 10 people to draw a map of your neighborhood from memory, each map will be slightly wrong. But if you overlay all 10 maps, the correct features (roads, buildings) will be reinforced while individual mistakes will fade away.

### Idea 2: Random Feature Selection

This is what makes it a "Random" Forest (not just a "Bagged" Forest).

At each split in each tree, the algorithm **randomly selects a subset of features** and picks the best split from only those features.

```
You have 10 features: [F1, F2, F3, F4, F5, F6, F7, F8, F9, F10]

Tree 1, Split 1: Consider only [F2, F5, F8] --> Best is F5
Tree 1, Split 2: Consider only [F1, F4, F9] --> Best is F1
Tree 2, Split 1: Consider only [F3, F7, F10] --> Best is F7
Tree 2, Split 2: Consider only [F2, F6, F8] --> Best is F6
...

Each split sees a different random subset of features!
```

**Why does this help?** Without this, every tree would pick the same "best" feature for the first split, making all trees very similar. Random feature selection forces diversity. Different trees learn different aspects of the data.

### Majority Voting

For classification, each tree votes for a class. The class with the most votes wins.

```
Prediction for a new sample:

Tree 1 predicts: Churn      |
Tree 2 predicts: No Churn   |
Tree 3 predicts: Churn      |---> Vote: Churn wins (7 vs 3)
Tree 4 predicts: Churn      |          Prediction: Churn
Tree 5 predicts: No Churn   |          Confidence: 70%
Tree 6 predicts: Churn      |
Tree 7 predicts: Churn      |
Tree 8 predicts: No Churn   |
Tree 9 predicts: Churn      |
Tree 10 predicts: Churn     |
```

For regression, the forest takes the **average** of all trees' predictions.

### The Complete Random Forest Algorithm

```
Random Forest Algorithm:
========================

TRAINING:
1. Set number of trees (n_estimators), e.g., 100
2. For each tree:
   a. Create a bootstrap sample (random sampling with replacement)
   b. Build a decision tree:
      - At each node, randomly select sqrt(n_features) features
      - Find the best split among those features
      - Split the node
      - Repeat until max_depth or other stopping criteria
3. Store all trees

PREDICTION:
1. Feed new data to ALL trees
2. Each tree makes its own prediction
3. Classification: Take majority vote
   Regression: Take average
4. Return final prediction
```

---

## Your First Random Forest with Scikit-Learn

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Create sample data
X, y = make_classification(
    n_samples=1000, n_features=10, n_informative=5,
    n_redundant=2, random_state=42
)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create Random Forest
rf = RandomForestClassifier(
    n_estimators=100,     # Build 100 trees
    max_depth=5,          # Each tree max 5 levels deep
    random_state=42
)

# Train the forest
rf.fit(X_train, y_train)

# Make predictions
y_pred = rf.predict(X_test)

# Check accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Random Forest Accuracy: {accuracy:.2%}")

# Compare with a single decision tree
from sklearn.tree import DecisionTreeClassifier

dt = DecisionTreeClassifier(max_depth=5, random_state=42)
dt.fit(X_train, y_train)
dt_accuracy = dt.score(X_test, y_test)

print(f"Single Tree Accuracy:   {dt_accuracy:.2%}")
print(f"Improvement:            {(accuracy - dt_accuracy):.2%}")
```

**Output:**

```
Random Forest Accuracy: 91.50%
Single Tree Accuracy:   86.00%
Improvement:            5.50%
```

**Line-by-line explanation:**

1. `RandomForestClassifier(n_estimators=100)` -- Create a forest of 100 decision trees.
2. `max_depth=5` -- Each tree can be at most 5 levels deep.
3. `rf.fit(X_train, y_train)` -- Train all 100 trees (each on a different bootstrap sample).
4. `rf.predict(X_test)` -- Each tree votes on each test sample. Majority wins.

The Random Forest beats the single tree by 5.5%. That is the power of the crowd.

---

## Tuning n_estimators: How Many Trees?

The `n_estimators` parameter controls how many trees are in the forest. More trees generally means better performance, but with diminishing returns.

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
import numpy as np

# Create data
X, y = make_classification(
    n_samples=1000, n_features=10, n_informative=5,
    n_redundant=2, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Try different numbers of trees
tree_counts = [1, 5, 10, 25, 50, 100, 200, 500]
results = []

print(f"{'Trees':>6} | {'Accuracy':>8} | {'Visual'}")
print("-" * 45)

for n in tree_counts:
    rf = RandomForestClassifier(n_estimators=n, max_depth=5,
                                random_state=42)
    rf.fit(X_train, y_train)
    acc = rf.score(X_test, y_test)
    results.append(acc)

    bar = "#" * int(acc * 40)
    print(f"{n:>6} | {acc:>7.1%} | {bar}")

print(f"\nBest: {tree_counts[np.argmax(results)]} trees "
      f"({max(results):.1%})")
```

**Output:**

```
 Trees | Accuracy | Visual
---------------------------------------------
     1 |   81.5% | ################################
     5 |   87.5% | ###################################
    10 |   90.0% | ####################################
    25 |   91.0% | ####################################
    50 |   91.0% | ####################################
   100 |   91.5% | ####################################
   200 |   91.5% | ####################################
   500 |   91.5% | ####################################

Best: 100 trees (91.5%)
```

Notice that accuracy improves quickly from 1 to 25 trees, then plateaus. After about 100 trees, adding more does not help. But it never hurts to add more trees (except for computation time).

```
Accuracy
  ^
  |                    ___________________________
  |                 __/
  |              __/
  |           __/
  |        __/
  |      _/
  |   __/
  |  /
  | /
  +--+--+--+--+--+--+--+--+--+--+--+--+---> n_estimators
     1  10 25 50 100  200     500

  "More trees = better, but diminishing returns"
  Rule of thumb: Start with 100, rarely need more than 500.
```

---

## Tuning max_depth: How Deep Should Each Tree Be?

```python
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

X, y = make_classification(
    n_samples=1000, n_features=10, n_informative=5,
    n_redundant=2, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

depths = [2, 3, 5, 7, 10, 15, 20, None]  # None = no limit

print(f"{'Depth':>6} | {'Train':>7} | {'Test':>7} | {'Gap':>6}")
print("-" * 40)

for depth in depths:
    rf = RandomForestClassifier(
        n_estimators=100, max_depth=depth, random_state=42
    )
    rf.fit(X_train, y_train)
    train_acc = rf.score(X_train, y_train)
    test_acc = rf.score(X_test, y_test)
    gap = train_acc - test_acc
    depth_str = str(depth) if depth else "None"
    overfit = " !" if gap > 0.1 else ""

    print(f"{depth_str:>6} | {train_acc:>6.1%} | {test_acc:>6.1%} | "
          f"{gap:>5.1%}{overfit}")
```

**Output:**

```
 Depth |   Train |    Test |    Gap
----------------------------------------
     2 |  87.4% |  86.5% |   0.9%
     3 |  90.8% |  89.0% |   1.8%
     5 |  94.9% |  91.5% |   3.4%
     7 |  97.9% |  91.0% |   6.9%
    10 |  99.9% |  91.0% |   8.9%
    15 | 100.0% |  91.5% |   8.5%
    20 | 100.0% |  91.5% |   8.5%
  None | 100.0% |  91.5% |   8.5%
```

With Random Forests, overfitting is less of a problem than with a single tree. Even unlimited depth does not hurt much because the averaging across trees smooths out the noise.

**Rule of thumb:** Start with `max_depth=None` (unlimited) for Random Forests. If you see overfitting, try reducing depth.

---

## Feature Importance

Random Forests provide excellent feature importance scores. They average the importance across all trees, making the ranking more stable than a single tree.

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris

# Load data
iris = load_iris()
X, y = iris.data, iris.target

# Train Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X, y)

# Get feature importance
importances = rf.feature_importances_
feature_names = iris.feature_names

# Sort by importance
sorted_idx = np.argsort(importances)[::-1]

print("Feature Importance (Random Forest):")
print("=" * 50)

for rank, idx in enumerate(sorted_idx, 1):
    bar = "#" * int(importances[idx] * 50)
    print(f"  {rank}. {feature_names[idx]:<20} "
          f"{importances[idx]:.4f} {bar}")

# Compare with single Decision Tree
from sklearn.tree import DecisionTreeClassifier

dt = DecisionTreeClassifier(random_state=42)
dt.fit(X, y)

print("\nFeature Importance (Single Tree):")
print("=" * 50)

dt_importances = dt.feature_importances_
sorted_idx_dt = np.argsort(dt_importances)[::-1]

for rank, idx in enumerate(sorted_idx_dt, 1):
    bar = "#" * int(dt_importances[idx] * 50)
    print(f"  {rank}. {feature_names[idx]:<20} "
          f"{dt_importances[idx]:.4f} {bar}")

print("\nNotice: Random Forest gives smoother, more balanced")
print("importance scores. Single tree is more extreme.")
```

**Output:**

```
Feature Importance (Random Forest):
==================================================
  1. petal length (cm)   0.4428 ######################
  2. petal width (cm)    0.4245 #####################
  3. sepal length (cm)   0.0919 ####
  4. sepal width (cm)    0.0408 ##

Feature Importance (Single Tree):
==================================================
  1. petal width (cm)    0.5514 ###########################
  2. petal length (cm)   0.4173 ####################
  3. sepal length (cm)   0.0313 #
  4. sepal width (cm)    0.0000

Notice: Random Forest gives smoother, more balanced
importance scores. Single tree is more extreme.
```

The Random Forest distributes importance more evenly. Both petal features are important (44% and 42%). The single tree is more extreme (55% and 0%).

---

## Out-of-Bag (OOB) Score

Remember that each bootstrap sample uses about 63% of the data. The remaining 37% are called **Out-of-Bag (OOB)** samples. These are samples that a particular tree never saw during training.

The OOB score uses these left-out samples as a built-in validation set. It is like getting cross-validation for free!

```
Bootstrap Sample for Tree 1: [A, A, C, D, D, F, G, G, I, J]
OOB samples for Tree 1:     [B, E, H]

Bootstrap Sample for Tree 2: [B, B, C, D, E, F, F, H, I, I]
OOB samples for Tree 2:     [A, G, J]

For sample A:
  - Tree 1 used it for training (can't use for OOB)
  - Tree 2 did NOT use it (use Tree 2's prediction)
  - Tree 3 did NOT use it (use Tree 3's prediction)
  --> Average the predictions from trees that didn't see A
  --> This gives us an unbiased estimate of accuracy!
```

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score

X, y = make_classification(
    n_samples=1000, n_features=10, n_informative=5,
    n_redundant=2, random_state=42
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Enable OOB score
rf = RandomForestClassifier(
    n_estimators=100,
    oob_score=True,      # Enable OOB scoring
    random_state=42
)
rf.fit(X_train, y_train)

# Compare OOB score with test accuracy
test_accuracy = rf.score(X_test, y_test)
oob_accuracy = rf.oob_score_

print(f"OOB Score:      {oob_accuracy:.2%}")
print(f"Test Accuracy:  {test_accuracy:.2%}")
print(f"Difference:     {abs(oob_accuracy - test_accuracy):.2%}")
print(f"\nThe OOB score closely matches the test accuracy!")
print(f"This means you can use OOB score to evaluate your")
print(f"model without needing a separate test set.")
```

**Output:**

```
OOB Score:      90.50%
Test Accuracy:  91.50%
Difference:     1.00%

The OOB score closely matches the test accuracy!
This means you can use OOB score to evaluate your
model without needing a separate test set.
```

The OOB score is very close to the actual test accuracy. This is incredibly useful because it means you can evaluate your model without setting aside a test set, which means more data for training.

---

## Complete Example: Customer Churn Prediction

Let us build a complete customer churn prediction system using Random Forests.

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.preprocessing import StandardScaler

# ============================================================
# STEP 1: Create a realistic churn dataset
# ============================================================
np.random.seed(42)
n = 1000

data = pd.DataFrame({
    'Tenure_Months': np.random.randint(1, 72, n),
    'Monthly_Charges': np.round(np.random.uniform(20, 120, n), 2),
    'Total_Charges': np.zeros(n),  # Will calculate
    'Num_Support_Tickets': np.random.randint(0, 10, n),
    'Num_Products': np.random.randint(1, 5, n),
    'Contract_Length': np.random.choice([1, 12, 24], n,
                                        p=[0.5, 0.3, 0.2]),
    'Has_Internet': np.random.choice([0, 1], n, p=[0.3, 0.7]),
    'Age': np.random.randint(18, 80, n),
    'Satisfaction_Score': np.random.randint(1, 11, n),
})

# Calculate total charges
data['Total_Charges'] = (data['Tenure_Months'] *
                         data['Monthly_Charges']).round(2)

# Create churn target based on realistic patterns
churn_score = (
    -data['Tenure_Months'] * 0.03 +          # Longer tenure = less churn
    data['Monthly_Charges'] * 0.02 +          # Higher charges = more churn
    data['Num_Support_Tickets'] * 0.15 +      # More tickets = more churn
    -data['Num_Products'] * 0.3 +             # More products = less churn
    -(data['Contract_Length'] / 12) * 0.5 +   # Longer contract = less churn
    -data['Satisfaction_Score'] * 0.2 +        # Higher satisfaction = less
    np.random.normal(0, 0.5, n)               # Random noise
)

data['Churned'] = (churn_score > np.median(churn_score)).astype(int)

print("=" * 60)
print("CUSTOMER CHURN PREDICTION WITH RANDOM FOREST")
print("=" * 60)
print(f"\nDataset shape: {data.shape}")
print(f"\nFirst 5 rows:")
print(data.head())
print(f"\nChurn distribution:")
print(data['Churned'].value_counts())
print(f"Churn rate: {data['Churned'].mean():.1%}")

# ============================================================
# STEP 2: Prepare the data
# ============================================================
feature_cols = [c for c in data.columns if c != 'Churned']
X = data[feature_cols]
y = data['Churned']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Test samples:     {len(X_test)}")

# ============================================================
# STEP 3: Train Random Forest
# ============================================================
print("\n" + "=" * 60)
print("TRAINING RANDOM FOREST")
print("=" * 60)

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_leaf=5,
    oob_score=True,
    random_state=42,
    n_jobs=-1         # Use all CPU cores for faster training
)

rf.fit(X_train, y_train)

print(f"\nModel trained with {rf.n_estimators} trees")
print(f"OOB Score: {rf.oob_score_:.2%}")

# ============================================================
# STEP 4: Evaluate the model
# ============================================================
y_pred = rf.predict(X_test)
y_proba = rf.predict_proba(X_test)

print("\n" + "=" * 60)
print("MODEL EVALUATION")
print("=" * 60)

accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy: {accuracy:.2%}")

cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"                 Predicted")
print(f"              Stay    Churn")
print(f"Actual Stay  {cm[0][0]:>5}    {cm[0][1]:>5}")
print(f"Actual Churn {cm[1][0]:>5}    {cm[1][1]:>5}")

print(f"\nClassification Report:")
print(classification_report(y_test, y_pred,
                            target_names=['Stay', 'Churn']))

# ============================================================
# STEP 5: Feature importance
# ============================================================
print("=" * 60)
print("FEATURE IMPORTANCE")
print("=" * 60)

importances = rf.feature_importances_
sorted_idx = np.argsort(importances)[::-1]

print(f"\n{'Rank':>4} {'Feature':<25} {'Importance':>10}")
print("-" * 45)
for rank, idx in enumerate(sorted_idx, 1):
    bar = "#" * int(importances[idx] * 50)
    print(f"{rank:>4} {feature_cols[idx]:<25} "
          f"{importances[idx]:>9.4f} {bar}")

# ============================================================
# STEP 6: Compare with single Decision Tree
# ============================================================
print("\n" + "=" * 60)
print("RANDOM FOREST vs. SINGLE TREE")
print("=" * 60)

from sklearn.tree import DecisionTreeClassifier

dt = DecisionTreeClassifier(max_depth=10, random_state=42)
dt.fit(X_train, y_train)
dt_acc = dt.score(X_test, y_test)

print(f"\nSingle Decision Tree Accuracy:  {dt_acc:.2%}")
print(f"Random Forest Accuracy:         {accuracy:.2%}")
print(f"Improvement:                    +{(accuracy - dt_acc):.2%}")

# ============================================================
# STEP 7: Predict new customers
# ============================================================
print("\n" + "=" * 60)
print("PREDICTIONS FOR NEW CUSTOMERS")
print("=" * 60)

new_customers = pd.DataFrame({
    'Tenure_Months': [3, 48, 12, 60, 6],
    'Monthly_Charges': [99.99, 45.00, 85.00, 30.00, 110.00],
    'Total_Charges': [299.97, 2160.00, 1020.00, 1800.00, 660.00],
    'Num_Support_Tickets': [5, 1, 3, 0, 7],
    'Num_Products': [1, 3, 2, 4, 1],
    'Contract_Length': [1, 24, 1, 24, 1],
    'Has_Internet': [1, 1, 1, 0, 1],
    'Age': [25, 55, 35, 65, 28],
    'Satisfaction_Score': [3, 8, 5, 9, 2],
})

predictions = rf.predict(new_customers)
probabilities = rf.predict_proba(new_customers)

for i in range(len(new_customers)):
    cust = new_customers.iloc[i]
    pred = "WILL CHURN" if predictions[i] == 1 else "WILL STAY"
    conf = probabilities[i][predictions[i]] * 100
    risk = probabilities[i][1] * 100

    print(f"\nCustomer {i+1}:")
    print(f"  Tenure: {cust['Tenure_Months']} months, "
          f"Charges: ${cust['Monthly_Charges']}/month")
    print(f"  Products: {cust['Num_Products']}, "
          f"Support Tickets: {cust['Num_Support_Tickets']}")
    print(f"  Contract: {cust['Contract_Length']} months, "
          f"Satisfaction: {cust['Satisfaction_Score']}/10")
    print(f"  Prediction: {pred} (Risk: {risk:.1f}%)")

# ============================================================
# STEP 8: Business insights
# ============================================================
print("\n" + "=" * 60)
print("BUSINESS INSIGHTS")
print("=" * 60)

print("""
Based on the model's feature importance:

1. SATISFACTION SCORE is the #1 predictor of churn.
   Action: Invest in customer satisfaction programs.

2. TENURE is highly important. New customers churn more.
   Action: Focus retention efforts on first-year customers.

3. SUPPORT TICKETS correlate with churn.
   Action: Improve product quality and support response time.

4. MONTHLY CHARGES matter. Higher charges = higher churn.
   Action: Review pricing. Offer loyalty discounts.

5. CONTRACT LENGTH protects against churn.
   Action: Incentivize longer-term contracts with discounts.
""")
```

**Output:**

```
============================================================
CUSTOMER CHURN PREDICTION WITH RANDOM FOREST
============================================================

Dataset shape: (1000, 10)

First 5 rows:
   Tenure_Months  Monthly_Charges  Total_Charges  Num_Support_Tickets  ...
0             52            82.18        4273.36                    6  ...
1              1            31.92          31.92                    9  ...
2             49            67.98        3330.98                    3  ...
3             71            75.77        5379.67                    7  ...
4             48            86.67        4160.16                    8  ...

Churn distribution:
Churned
0    500
1    500
Name: count, dtype: int64
Churn rate: 50.0%

Training samples: 800
Test samples:     200

============================================================
TRAINING RANDOM FOREST
============================================================

Model trained with 200 trees
OOB Score: 85.50%

============================================================
MODEL EVALUATION
============================================================

Accuracy: 86.50%

Confusion Matrix:
                 Predicted
              Stay    Churn
Actual Stay     85       15
Actual Churn    12       88

Classification Report:
              precision    recall  f1-score   support

        Stay       0.88      0.85      0.86       100
       Churn       0.85      0.88      0.87       100

    accuracy                           0.86       200
   macro avg       0.87      0.87      0.87       200
weighted avg       0.87      0.86      0.87       200

============================================================
FEATURE IMPORTANCE
============================================================

Rank Feature                   Importance
---------------------------------------------
   1 Satisfaction_Score             0.1634 ########
   2 Tenure_Months                 0.1521 #######
   3 Num_Support_Tickets           0.1398 ######
   4 Monthly_Charges               0.1312 ######
   5 Total_Charges                 0.1187 #####
   6 Age                           0.0923 ####
   7 Contract_Length               0.0812 ####
   8 Num_Products                  0.0714 ###
   9 Has_Internet                  0.0499 ##

============================================================
RANDOM FOREST vs. SINGLE TREE
============================================================

Single Decision Tree Accuracy:  80.50%
Random Forest Accuracy:         86.50%
Improvement:                    +6.00%

============================================================
PREDICTIONS FOR NEW CUSTOMERS
============================================================

Customer 1:
  Tenure: 3 months, Charges: $99.99/month
  Products: 1, Support Tickets: 5
  Contract: 1 months, Satisfaction: 3/10
  Prediction: WILL CHURN (Risk: 89.2%)

Customer 2:
  Tenure: 48 months, Charges: $45.0/month
  Products: 3, Support Tickets: 1
  Contract: 24 months, Satisfaction: 8/10
  Prediction: WILL STAY (Risk: 8.5%)

Customer 3:
  Tenure: 12 months, Charges: $85.0/month
  Products: 2, Support Tickets: 3
  Contract: 1 months, Satisfaction: 5/10
  Prediction: WILL CHURN (Risk: 62.3%)

Customer 4:
  Tenure: 60 months, Charges: $30.0/month
  Products: 4, Support Tickets: 0
  Contract: 24 months, Satisfaction: 9/10
  Prediction: WILL STAY (Risk: 3.1%)

Customer 5:
  Tenure: 6 months, Charges: $110.0/month
  Products: 1, Support Tickets: 7
  Contract: 1 months, Satisfaction: 2/10
  Prediction: WILL CHURN (Risk: 95.7%)

============================================================
BUSINESS INSIGHTS
============================================================

Based on the model's feature importance:

1. SATISFACTION SCORE is the #1 predictor of churn.
   Action: Invest in customer satisfaction programs.

2. TENURE is highly important. New customers churn more.
   Action: Focus retention efforts on first-year customers.

3. SUPPORT TICKETS correlate with churn.
   Action: Improve product quality and support response time.

4. MONTHLY CHARGES matter. Higher charges = higher churn.
   Action: Review pricing. Offer loyalty discounts.

5. CONTRACT LENGTH protects against churn.
   Action: Incentivize longer-term contracts with discounts.
```

---

## Random Forest vs. Decision Tree: A Visual Comparison

```
+-----------------------------------+-----------------------------------+
|         DECISION TREE             |        RANDOM FOREST              |
+-----------------------------------+-----------------------------------+
|                                   |                                   |
|  One tree                         |  Many trees (100-500)             |
|                                   |                                   |
|  Can memorize noise               |  Averages out noise               |
|  (overfitting)                    |  (resistant to overfitting)       |
|                                   |                                   |
|  Unstable: small data             |  Stable: small data changes       |
|  change = very different tree     |  barely affect the forest         |
|                                   |                                   |
|  Fast to train                    |  Slower to train (many trees)     |
|  Fast to predict                  |  Slower to predict (many trees)   |
|                                   |                                   |
|  Easy to visualize                |  Hard to visualize (too many      |
|  and interpret                    |  trees), but gives feature        |
|                                   |  importance                       |
|                                   |                                   |
|  Lower accuracy                   |  Higher accuracy                  |
|  (usually)                        |  (usually)                        |
+-----------------------------------+-----------------------------------+
```

---

## Common Mistakes

1. **Using too few trees.** Start with at least 100 trees. With fewer, the model may be unstable.

2. **Not checking feature importance.** Random Forests give you free insights into which features matter. Always look at `feature_importances_`.

3. **Forgetting to set `random_state`.** Without it, you will get slightly different results every time, making debugging harder.

4. **Over-tuning.** Random Forests work well with default settings. Do not spend hours tuning when the defaults already give good results.

5. **Ignoring the OOB score.** It is free validation! Use `oob_score=True` to get an accuracy estimate without a separate validation set.

---

## Best Practices

1. **Start with defaults.** `n_estimators=100`, `max_depth=None`. This works surprisingly well.

2. **Use `n_jobs=-1`** to use all CPU cores for faster training.

   ```python
   rf = RandomForestClassifier(n_estimators=100, n_jobs=-1)
   ```

3. **Enable OOB scoring** for a quick performance estimate.

   ```python
   rf = RandomForestClassifier(oob_score=True)
   ```

4. **Check feature importance** to understand what drives predictions and potentially remove unimportant features.

5. **Random Forests do not need feature scaling.** Unlike logistic regression and KNN, trees split on feature values directly.

6. **For imbalanced data**, use `class_weight='balanced'` to give more weight to the minority class.

---

## Quick Summary

```
+------------------------------------------+
|          RANDOM FORESTS                  |
+------------------------------------------+
|                                          |
| Type: Classification and Regression      |
| Also known as: "Ensemble of trees"       |
|                                          |
| How it works:                            |
| 1. Create many bootstrap samples         |
| 2. Build a tree on each sample           |
| 3. At each split, use random features    |
| 4. Classification: majority vote         |
|    Regression: average of predictions    |
|                                          |
| Key parameters:                          |
| - n_estimators: number of trees (100+)   |
| - max_depth: max depth per tree          |
| - min_samples_leaf: min samples in leaf  |
|                                          |
| Special features:                        |
| - OOB score: free validation!            |
| - Feature importance: what matters most  |
| - No scaling needed                      |
|                                          |
| Strengths:                               |
| - Very accurate                          |
| - Resistant to overfitting              |
| - Works on most problems                |
|                                          |
| Weaknesses:                              |
| - Slower than a single tree             |
| - Hard to interpret (black box)         |
| - Large memory footprint                |
+------------------------------------------+
```

---

## Key Points

- A **Random Forest** is a collection of decision trees that vote together.
- **Bagging** creates diversity by training each tree on a random subset of the data (sampling with replacement).
- **Random feature selection** adds more diversity by considering only a random subset of features at each split.
- **Majority voting** (classification) or **averaging** (regression) combines the trees' predictions.
- More trees are generally better, but returns diminish after about 100-200 trees.
- The **OOB score** is a free validation metric that does not require a separate test set.
- **Feature importance** from Random Forests is more stable and reliable than from a single tree.
- Random Forests **do not need feature scaling**.
- They are resistant to **overfitting**, especially compared to a single deep decision tree.
- Always set `n_jobs=-1` for faster training on multi-core machines.

---

## Practice Questions

1. Explain the "wisdom of crowds" concept and how it applies to Random Forests. Why is a group of mediocre trees better than one excellent tree?

2. What is bagging? Why does sampling with replacement help create better models?

3. Why does a Random Forest randomly select a subset of features at each split? What would happen if every tree used all features?

4. You train a Random Forest with 500 trees and get 88% accuracy. You then try 1000 trees and get 88.1% accuracy. Is it worth doubling the trees? Why or why not?

5. What is the OOB score? How is it calculated, and why is it useful?

---

## Exercises

### Exercise 1: Wine Quality Classification

Load the wine dataset from scikit-learn (`load_wine`). Train a Random Forest and a single Decision Tree. Compare their accuracy. Show the feature importance from the Random Forest.

### Exercise 2: Optimal Number of Trees

Using any dataset, train Random Forests with 1, 5, 10, 25, 50, 100, 200, and 500 trees. Plot accuracy vs. number of trees. At what point do you see diminishing returns?

### Exercise 3: OOB Score vs. Test Score

Train a Random Forest with `oob_score=True`. Compare the OOB score with the actual test set accuracy across different `max_depth` values (3, 5, 7, 10, None). How closely do they match?

---

## What Is Next?

You now know four powerful classification algorithms: logistic regression, KNN, decision trees, and Random Forests. But how do you know if your model will work well on new data? How do you compare models fairly?

In Chapter 25, you will learn about **Cross-Validation**, a technique that tells you how well your model truly generalizes. It is like testing your model on multiple exams instead of just one.
