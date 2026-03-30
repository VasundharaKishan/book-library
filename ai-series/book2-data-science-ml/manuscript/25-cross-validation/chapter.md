# Chapter 25: Cross-Validation

## What You Will Learn

In this chapter, you will learn:

- Why a single train/test split is not reliable enough
- What K-Fold Cross-Validation is and how it works
- How to visualize K-Fold with ASCII diagrams
- How to use `cross_val_score` in scikit-learn
- What Stratified K-Fold is and when to use it
- What Leave-One-Out Cross-Validation is
- When to use which cross-validation strategy
- How to compare five different models using cross-validation

## Why This Chapter Matters

Imagine you are a teacher who writes an exam. You test your students once. One student who usually struggles gets lucky and scores high. Another strong student has a bad day and scores low.

If you judge students by just one exam, your evaluation is unreliable. But if you give **five** different exams and average the scores, you get a much more accurate picture.

That is exactly the problem with a single train/test split. Depending on which data ends up in the test set, your accuracy can swing wildly. A model that looks great on one split might look average on another.

**Cross-validation** solves this by testing your model multiple times on different splits. It gives you a reliable, honest estimate of how well your model will perform on new data.

Every data scientist uses cross-validation. It is not optional. It is how you truly evaluate a model.

---

## The Problem with a Single Train/Test Split

Let us first see why a single split is unreliable.

```python
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

# Load data
X, y = load_iris(return_X_y=True)

# Try different random splits
print("Accuracy with different random splits:")
print("-" * 40)

for seed in range(10):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=seed
    )
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)

    bar = "#" * int(accuracy * 30)
    print(f"  Split {seed}: {accuracy:.2%}  {bar}")

print("\nSee how the accuracy changes just based on")
print("which data ends up in the test set!")
```

**Output:**

```
Accuracy with different random splits:
----------------------------------------
  Split 0: 95.56%  ############################
  Split 1: 95.56%  ############################
  Split 2: 100.00%  ##############################
  Split 3: 95.56%  ############################
  Split 4: 93.33%  ############################
  Split 5: 93.33%  ############################
  Split 6: 95.56%  ############################
  Split 7: 91.11%  ###########################
  Split 8: 97.78%  #############################
  Split 9: 100.00%  ##############################

See how the accuracy changes just based on
which data ends up in the test set!
```

The accuracy ranges from 91.11% to 100.00%. That is a 9% difference just from changing which data goes where! Which number should you report? Is your model 91% accurate or 100% accurate?

Cross-validation answers this question by testing on **every** piece of data.

---

## K-Fold Cross-Validation

**K-Fold Cross-Validation** divides your data into K equal parts (called "folds"). It then trains and tests the model K times, each time using a different fold as the test set and the remaining folds as the training set.

Here is how 5-Fold Cross-Validation works:

```
5-Fold Cross-Validation
========================

Your data is split into 5 equal parts (folds):

Fold:    |  1  |  2  |  3  |  4  |  5  |

Round 1: [TEST][ TRAIN ][ TRAIN ][ TRAIN ][ TRAIN ] --> Score 1
Round 2: [ TRAIN ][TEST][ TRAIN ][ TRAIN ][ TRAIN ] --> Score 2
Round 3: [ TRAIN ][ TRAIN ][TEST][ TRAIN ][ TRAIN ] --> Score 3
Round 4: [ TRAIN ][ TRAIN ][ TRAIN ][TEST][ TRAIN ] --> Score 4
Round 5: [ TRAIN ][ TRAIN ][ TRAIN ][ TRAIN ][TEST] --> Score 5

Final Score = Average(Score 1, Score 2, Score 3, Score 4, Score 5)
```

Every data point gets to be in the test set exactly **once**. This means every data point is used for both training and testing. Nothing is wasted.

**Real-life analogy:** Imagine a basketball team practicing for a tournament. Instead of always having the same 5 players on the court, they rotate. Every player gets a chance to sit out and watch (be "tested"). This way, you evaluate every player's contribution, not just the starters.

### How K-Fold Works Step by Step

```
Step 1: Split data into K folds (e.g., K=5)

Data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

Fold 1: [1,  2,  3]
Fold 2: [4,  5,  6]
Fold 3: [7,  8,  9]
Fold 4: [10, 11, 12]
Fold 5: [13, 14, 15]

Step 2: For each round, use one fold as test, rest as train

Round 1:
  Train on: [4,5,6, 7,8,9, 10,11,12, 13,14,15]  (12 samples)
  Test on:  [1,2,3]                                (3 samples)
  --> Accuracy: 93%

Round 2:
  Train on: [1,2,3, 7,8,9, 10,11,12, 13,14,15]  (12 samples)
  Test on:  [4,5,6]                                (3 samples)
  --> Accuracy: 87%

... (continue for all 5 rounds)

Step 3: Average the scores
  Final accuracy = (93 + 87 + 90 + 95 + 88) / 5 = 90.6%
  Standard deviation tells you how stable the model is
```

---

## Using cross_val_score in Scikit-Learn

Scikit-learn makes cross-validation incredibly easy with `cross_val_score`.

```python
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
import numpy as np

# Load data
X, y = load_iris(return_X_y=True)

# Create model
model = DecisionTreeClassifier(random_state=42)

# Perform 5-fold cross-validation
scores = cross_val_score(model, X, y, cv=5)

print("5-Fold Cross-Validation Results:")
print("-" * 40)
for i, score in enumerate(scores, 1):
    bar = "#" * int(score * 30)
    print(f"  Fold {i}: {score:.4f}  {bar}")

print(f"\n  Mean Accuracy: {scores.mean():.4f}")
print(f"  Std Deviation: {scores.std():.4f}")
print(f"\n  Report: {scores.mean():.2%} (+/- {scores.std() * 2:.2%})")
```

**Output:**

```
5-Fold Cross-Validation Results:
----------------------------------------
  Fold 1: 0.9667  #############################
  Fold 2: 0.9667  #############################
  Fold 3: 0.9000  ###########################
  Fold 4: 0.9333  ############################
  Fold 5: 1.0000  ##############################

  Mean Accuracy: 0.9533
  Std Deviation: 0.0327

  Report: 95.33% (+/- 6.53%)
```

**Line-by-line explanation:**

1. `cross_val_score(model, X, y, cv=5)` -- This does everything:
   - Splits data into 5 folds
   - Trains the model 5 times (each time with a different fold held out)
   - Returns 5 accuracy scores
2. `scores.mean()` -- The average accuracy across all folds. This is your best estimate of true model performance.
3. `scores.std()` -- How much the scores vary. Low = stable model. High = unstable model.
4. `+/- {scores.std() * 2:.2%}` -- The "95% confidence interval". It means you can expect the true accuracy to fall within this range.

### Using Different Scoring Metrics

You can use metrics other than accuracy:

```python
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)
model = DecisionTreeClassifier(random_state=42)

# Different scoring metrics
metrics = ['accuracy', 'f1_macro', 'precision_macro', 'recall_macro']

print(f"{'Metric':<20} {'Mean':>8} {'Std':>8}")
print("-" * 40)

for metric in metrics:
    scores = cross_val_score(model, X, y, cv=5, scoring=metric)
    print(f"{metric:<20} {scores.mean():>7.4f} {scores.std():>7.4f}")
```

**Output:**

```
Metric                  Mean      Std
----------------------------------------
accuracy               0.9533   0.0327
f1_macro               0.9525   0.0339
precision_macro        0.9567   0.0311
recall_macro           0.9533   0.0327
```

---

## Stratified K-Fold Cross-Validation

Regular K-Fold just splits the data into equal chunks. But what if your classes are imbalanced?

Imagine you have 100 samples: 90 class A and 10 class B. A regular 5-fold split might put all 10 class B samples in the same fold. That fold would have 18 class B samples (all of them!) while other folds have zero.

**Stratified K-Fold** fixes this by ensuring each fold has approximately the same proportion of classes as the original data.

```
Regular K-Fold (BAD for imbalanced data):

Original: 90% class A, 10% class B

Fold 1: [A A A A A A A A A A A A B B B B B B B B]  (60% A, 40% B)
Fold 2: [A A A A A A A A A A A A A A A A A A A A]  (100% A, 0% B)
Fold 3: [A A A A A A A A A A A A A A A A A A A A]  (100% A, 0% B)

Not representative! Some folds have all of class B!


Stratified K-Fold (GOOD for imbalanced data):

Original: 90% class A, 10% class B

Fold 1: [A A A A A A A A A A A A A A A A A A B B]  (90% A, 10% B)
Fold 2: [A A A A A A A A A A A A A A A A A A B B]  (90% A, 10% B)
Fold 3: [A A A A A A A A A A A A A A A A A A B B]  (90% A, 10% B)

Each fold preserves the original class distribution!
```

```python
from sklearn.model_selection import (cross_val_score,
                                     StratifiedKFold, KFold)
from sklearn.tree import DecisionTreeClassifier
import numpy as np

# Create imbalanced dataset
np.random.seed(42)
X = np.random.randn(200, 5)
y = np.array([0] * 180 + [1] * 20)  # 90% class 0, 10% class 1

model = DecisionTreeClassifier(random_state=42)

# Regular K-Fold
kf = KFold(n_splits=5, shuffle=True, random_state=42)
regular_scores = cross_val_score(model, X, y, cv=kf)

# Stratified K-Fold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
stratified_scores = cross_val_score(model, X, y, cv=skf)

print("Regular K-Fold:")
print(f"  Scores: {regular_scores}")
print(f"  Mean: {regular_scores.mean():.4f}, Std: {regular_scores.std():.4f}")

print(f"\nStratified K-Fold:")
print(f"  Scores: {stratified_scores}")
print(f"  Mean: {stratified_scores.mean():.4f}, Std: {stratified_scores.std():.4f}")

# Show class distribution per fold
print("\nClass distribution in each fold (Stratified):")
for i, (train_idx, test_idx) in enumerate(skf.split(X, y)):
    y_test_fold = y[test_idx]
    class_0 = (y_test_fold == 0).sum()
    class_1 = (y_test_fold == 1).sum()
    total = len(y_test_fold)
    print(f"  Fold {i+1}: Class 0 = {class_0} ({class_0/total:.0%}), "
          f"Class 1 = {class_1} ({class_1/total:.0%})")
```

**Output:**

```
Regular K-Fold:
  Scores: [0.875  0.925  0.9    0.925  0.85 ]
  Mean: 0.8950, Std: 0.0285

Stratified K-Fold:
  Scores: [0.9    0.9    0.875  0.925  0.9  ]
  Mean: 0.9000, Std: 0.0158

Class distribution in each fold (Stratified):
  Fold 1: Class 0 = 36 (90%), Class 1 = 4 (10%)
  Fold 2: Class 0 = 36 (90%), Class 1 = 4 (10%)
  Fold 3: Class 0 = 36 (90%), Class 1 = 4 (10%)
  Fold 4: Class 0 = 36 (90%), Class 1 = 4 (10%)
  Fold 5: Class 0 = 36 (90%), Class 1 = 4 (10%)
```

Notice that stratified K-Fold has a **lower standard deviation** (0.0158 vs. 0.0285). This means more consistent and reliable results.

**Important:** `cross_val_score` uses Stratified K-Fold **by default** for classification problems. You get it for free!

---

## Leave-One-Out Cross-Validation (LOOCV)

**Leave-One-Out** (LOO) is the extreme version of K-Fold where K equals the number of samples. Each sample gets its own fold.

```
LOOCV with 5 samples:

Round 1: Train on [2,3,4,5], Test on [1] --> Score
Round 2: Train on [1,3,4,5], Test on [2] --> Score
Round 3: Train on [1,2,4,5], Test on [3] --> Score
Round 4: Train on [1,2,3,5], Test on [4] --> Score
Round 5: Train on [1,2,3,4], Test on [5] --> Score

Every single sample gets tested exactly once.
```

```python
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_iris
import numpy as np

X, y = load_iris(return_X_y=True)

model = KNeighborsClassifier(n_neighbors=5)

# Leave-One-Out
loo = LeaveOneOut()
loo_scores = cross_val_score(model, X, y, cv=loo)

print(f"Leave-One-Out Cross-Validation:")
print(f"  Number of rounds: {len(loo_scores)}")
print(f"  Correct predictions: {loo_scores.sum():.0f} / {len(loo_scores)}")
print(f"  Mean Accuracy: {loo_scores.mean():.4f}")

# Compare with 5-Fold and 10-Fold
for k in [5, 10]:
    scores = cross_val_score(model, X, y, cv=k)
    print(f"\n{k}-Fold Cross-Validation:")
    print(f"  Mean Accuracy: {scores.mean():.4f} "
          f"(+/- {scores.std() * 2:.4f})")
```

**Output:**

```
Leave-One-Out Cross-Validation:
  Number of rounds: 150
  Correct predictions: 144 / 150
  Mean Accuracy: 0.9667

5-Fold Cross-Validation:
  Mean Accuracy: 0.9667 (+/- 0.0447)

10-Fold Cross-Validation:
  Mean Accuracy: 0.9667 (+/- 0.0553)
```

### When to Use LOOCV

**Pros:**
- Uses maximum data for training (N-1 samples)
- No randomness in the split (results are always the same)
- Best for very small datasets

**Cons:**
- Very slow (trains N models for N samples)
- High variance (each test set has only 1 sample)
- Not practical for large datasets

**Rule of thumb:** Use LOOCV only when you have fewer than 100 samples.

---

## When to Use Which Cross-Validation?

```
+--------------------+--------------------+---------------------+
|    5-Fold CV       |  Stratified K-Fold |    Leave-One-Out    |
+--------------------+--------------------+---------------------+
| Default choice     | Imbalanced classes | Very small datasets |
| Good balance of    | Preserves class    | (<100 samples)      |
| speed and accuracy | proportions        |                     |
|                    |                    | Uses maximum data   |
| Works for most     | DEFAULT in sklearn | for training        |
| datasets           | for classification |                     |
|                    |                    | Very slow for       |
| Use K=5 or K=10   | Always use for     | large datasets      |
|                    | classification     |                     |
+--------------------+--------------------+---------------------+

Decision Guide:

Is your dataset small (< 100 samples)?
  YES --> Use Leave-One-Out (LOOCV)
  NO  --> Is it a classification problem?
            YES --> Use Stratified K-Fold (K=5 or K=10)
            NO  --> Use regular K-Fold (K=5 or K=10)
```

### Choosing K (Number of Folds)

| K Value | Training Data | Pros | Cons |
|---------|--------------|------|------|
| K=5 | 80% | Fast, good for large data | Slightly higher bias |
| K=10 | 90% | Standard choice, balanced | Slower than K=5 |
| K=20 | 95% | Low bias | Slow, high variance |
| K=N (LOOCV) | 99.x% | Maximum training data | Very slow |

**The standard choice is K=5 or K=10.** Use K=5 for large datasets (faster) and K=10 for smaller datasets (more reliable).

---

## Comparing Five Models with Cross-Validation

This is where cross-validation truly shines: comparing multiple models fairly.

```python
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# Load data
X, y = load_iris(return_X_y=True)

# Define models to compare
models = {
    'Logistic Regression': LogisticRegression(max_iter=200,
                                              random_state=42),
    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5),
    'Decision Tree':       DecisionTreeClassifier(random_state=42),
    'Random Forest':       RandomForestClassifier(n_estimators=100,
                                                  random_state=42),
    'SVM (RBF kernel)':    SVC(random_state=42),
}

# Compare models using 10-fold cross-validation
print("=" * 65)
print("MODEL COMPARISON USING 10-FOLD CROSS-VALIDATION")
print("=" * 65)

results = {}

print(f"\n{'Model':<25} {'Mean':>7} {'Std':>7} {'Min':>7} "
      f"{'Max':>7} {'Visual'}")
print("-" * 65)

for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=10, scoring='accuracy')
    results[name] = scores

    bar = "#" * int(scores.mean() * 30)
    print(f"{name:<25} {scores.mean():>6.1%} {scores.std():>6.1%} "
          f"{scores.min():>6.1%} {scores.max():>6.1%} {bar}")

# Find the best model
best_model = max(results, key=lambda k: results[k].mean())
print(f"\nBest Model: {best_model} "
      f"({results[best_model].mean():.2%})")

# Show individual fold scores for top 2 models
print(f"\n{'Detailed Fold Scores':}")
print("-" * 65)

sorted_models = sorted(results.items(),
                       key=lambda x: x[1].mean(), reverse=True)

for name, scores in sorted_models[:2]:
    print(f"\n{name}:")
    for i, score in enumerate(scores, 1):
        bar = "#" * int(score * 20)
        print(f"  Fold {i:>2}: {score:.4f} {bar}")
    print(f"  Mean:    {scores.mean():.4f}")
```

**Output:**

```
=================================================================
MODEL COMPARISON USING 10-FOLD CROSS-VALIDATION
=================================================================

Model                        Mean     Std     Min     Max Visual
-----------------------------------------------------------------
Logistic Regression         97.3%   3.5%   86.7%  100.0% #############################
K-Nearest Neighbors         96.7%   4.5%   86.7%  100.0% #############################
Decision Tree               95.3%   5.0%   86.7%  100.0% ############################
Random Forest               96.0%   4.3%   86.7%  100.0% ############################
SVM (RBF kernel)            98.0%   3.1%   93.3%  100.0% #############################

Best Model: SVM (RBF kernel) (98.00%)

Detailed Fold Scores:
-----------------------------------------------------------------

SVM (RBF kernel):
  Fold  1: 1.0000 ####################
  Fold  2: 0.9333 ##################
  Fold  3: 1.0000 ####################
  Fold  4: 1.0000 ####################
  Fold  5: 1.0000 ####################
  Fold  6: 0.9333 ##################
  Fold  7: 1.0000 ####################
  Fold  8: 1.0000 ####################
  Fold  9: 1.0000 ####################
  Fold 10: 1.0000 ####################
  Mean:    0.9800

Logistic Regression:
  Fold  1: 1.0000 ####################
  Fold  2: 0.8667 #################
  Fold  3: 0.9333 ##################
  Fold  4: 1.0000 ####################
  Fold  5: 1.0000 ####################
  Fold  6: 1.0000 ####################
  Fold  7: 1.0000 ####################
  Fold  8: 1.0000 ####################
  Fold  9: 1.0000 ####################
  Fold 10: 0.9333 ##################
  Mean:    0.9733
```

### Interpreting the Results

When comparing models, look at:

1. **Mean accuracy:** Higher is better. But only if the difference is meaningful.
2. **Standard deviation:** Lower is better. It means the model is more stable.
3. **Minimum score:** How bad can the model get? A high minimum means reliable performance.

**Important:** A difference of less than 1-2% is usually not significant. In this case, SVM (98.0%) and Logistic Regression (97.3%) are practically equivalent.

---

## Cross-Validation with Preprocessing (Pipelines)

When you use feature scaling with cross-validation, you must be careful. You must scale INSIDE each fold, not before. Otherwise, test data "leaks" into the training process.

```python
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)

# WRONG WAY: Scale all data first, then cross-validate
# (test data leaks into training via the scaler!)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Sees ALL data, including test!
model = KNeighborsClassifier(n_neighbors=5)
wrong_scores = cross_val_score(model, X_scaled, y, cv=5)

# RIGHT WAY: Use a Pipeline (scales inside each fold)
pipeline = Pipeline([
    ('scaler', StandardScaler()),    # Scale features
    ('knn', KNeighborsClassifier(n_neighbors=5))  # Classify
])
right_scores = cross_val_score(pipeline, X, y, cv=5)

print("Wrong way (scale first, then CV):")
print(f"  Mean: {wrong_scores.mean():.4f} (+/- {wrong_scores.std()*2:.4f})")

print("\nRight way (scale inside CV with Pipeline):")
print(f"  Mean: {right_scores.mean():.4f} (+/- {right_scores.std()*2:.4f})")

print("\nThe Pipeline ensures scaling happens correctly!")
print("Each fold scales based only on its training data.")
```

**Output:**

```
Wrong way (scale first, then CV):
  Mean: 0.9667 (+/- 0.0447)

Right way (scale inside CV with Pipeline):
  Mean: 0.9600 (+/- 0.0533)

The Pipeline ensures scaling happens correctly!
Each fold scales based only on its training data.
```

The scores might look similar here (Iris is an easy dataset), but on real-world data, the wrong way can give overly optimistic results. Always use Pipelines with cross-validation.

```
WRONG: Data leaks!                RIGHT: No data leaks!

[Scale ALL data]                  For each fold:
      |                             [Scale ONLY training data]
[Cross-validate]                          |
      |                             [Transform test data]
Test data was already                     |
seen by the scaler!               [Train and evaluate]
```

---

## A Larger Model Comparison Example

Let us compare models on a more challenging dataset.

```python
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.datasets import make_classification
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# Create a harder dataset
X, y = make_classification(
    n_samples=1000, n_features=20, n_informative=10,
    n_redundant=5, n_classes=3, n_clusters_per_class=2,
    random_state=42
)

print("=" * 65)
print("COMPREHENSIVE MODEL COMPARISON")
print("=" * 65)
print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, "
      f"{len(np.unique(y))} classes")

# Define models (with Pipelines for scaling where needed)
models = {
    'Logistic Regression': Pipeline([
        ('scaler', StandardScaler()),
        ('model', LogisticRegression(max_iter=1000, random_state=42))
    ]),
    'KNN (K=5)': Pipeline([
        ('scaler', StandardScaler()),
        ('model', KNeighborsClassifier(n_neighbors=5))
    ]),
    'KNN (K=10)': Pipeline([
        ('scaler', StandardScaler()),
        ('model', KNeighborsClassifier(n_neighbors=10))
    ]),
    'Decision Tree': DecisionTreeClassifier(
        max_depth=5, random_state=42
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42
    ),
}

# Compare using 10-fold cross-validation
results = {}

print(f"\n{'Model':<25} {'Accuracy':>10} {'Std':>8} {'Status'}")
print("-" * 60)

for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=10, scoring='accuracy')
    results[name] = scores

    # Determine status
    if scores.mean() == max(s.mean() for s in results.values()):
        status = "<-- BEST SO FAR"
    elif scores.std() > 0.05:
        status = "(high variance!)"
    else:
        status = ""

    print(f"{name:<25} {scores.mean():>9.2%} {scores.std():>7.2%} {status}")

# Statistical comparison
print("\n" + "=" * 65)
print("DETAILED ANALYSIS")
print("=" * 65)

best_name = max(results, key=lambda k: results[k].mean())
best_scores = results[best_name]

print(f"\nBest Model: {best_name}")
print(f"  Mean Accuracy:  {best_scores.mean():.2%}")
print(f"  Std Deviation:  {best_scores.std():.2%}")
print(f"  95% CI:         {best_scores.mean():.2%} "
      f"+/- {best_scores.std() * 2:.2%}")
print(f"  Worst Fold:     {best_scores.min():.2%}")
print(f"  Best Fold:      {best_scores.max():.2%}")

# Show rankings
print(f"\nFinal Rankings:")
sorted_models = sorted(results.items(),
                       key=lambda x: x[1].mean(), reverse=True)
for rank, (name, scores) in enumerate(sorted_models, 1):
    bar = "#" * int(scores.mean() * 30)
    medal = {1: "  [Gold]", 2: "  [Silver]", 3: "  [Bronze]"}.get(rank, "")
    print(f"  {rank}. {name:<25} {scores.mean():.2%} {bar}{medal}")
```

**Output:**

```
=================================================================
COMPREHENSIVE MODEL COMPARISON
=================================================================
Dataset: 1000 samples, 20 features, 3 classes

Model                      Accuracy      Std Status
------------------------------------------------------------
Logistic Regression          74.80%    3.56% <-- BEST SO FAR
KNN (K=5)                    72.60%    4.27%
KNN (K=10)                   72.90%    3.87%
Decision Tree                67.50%    3.22%
Random Forest                79.40%    3.18% <-- BEST SO FAR

=================================================================
DETAILED ANALYSIS
=================================================================

Best Model: Random Forest
  Mean Accuracy:  79.40%
  Std Deviation:  3.18%
  95% CI:         79.40% +/- 6.36%
  Worst Fold:     74.00%
  Best Fold:      85.00%

Final Rankings:
  1. Random Forest              79.40% #######################  [Gold]
  2. Logistic Regression        74.80% ######################  [Silver]
  3. KNN (K=10)                 72.90% #####################  [Bronze]
  4. KNN (K=5)                  72.60% #####################
  5. Decision Tree              67.50% ####################
```

This comparison clearly shows that Random Forest is the best model for this dataset, with 79.40% accuracy and a relatively low standard deviation.

---

## Common Mistakes

1. **Scaling data before cross-validation.** If you call `fit_transform` on all data before `cross_val_score`, the test folds have already been "seen" by the scaler. Use Pipelines to avoid this.

2. **Using too few folds.** With K=2, each fold only uses 50% of the data for training. Use K=5 or K=10.

3. **Ignoring the standard deviation.** A model with 95% +/- 1% is much better than a model with 95% +/- 10%. The second model is unstable.

4. **Reporting single train/test split accuracy.** Always use cross-validation for the final model comparison.

5. **Using LOOCV on large datasets.** With 10,000 samples, LOOCV trains 10,000 models. Use 5-fold or 10-fold instead.

---

## Best Practices

1. **Use Stratified K-Fold for classification.** This is the default in `cross_val_score` for classification, but be explicit when using `KFold` directly.

2. **Use Pipelines** to include preprocessing (scaling, encoding) inside cross-validation.

3. **Use K=5 for large datasets** and K=10 for smaller datasets.

4. **Report mean and standard deviation.** Say "95.3% +/- 3.5%" instead of just "95.3%".

5. **Compare models on the same folds.** Use the same random seed or the same fold object for fair comparison.

6. **Cross-validation is for evaluation, not training.** Train your final model on ALL the training data, not on a single fold.

---

## Quick Summary

```
+------------------------------------------+
|        CROSS-VALIDATION                  |
+------------------------------------------+
|                                          |
| Purpose: Reliable model evaluation       |
|                                          |
| K-Fold:                                  |
| - Split data into K parts               |
| - Train K times, each time holding out   |
|   1 part for testing                     |
| - Average the K scores                   |
|                                          |
| Types:                                   |
| - K-Fold: basic, works for regression   |
| - Stratified K-Fold: for classification  |
|   (preserves class proportions)          |
| - LOOCV: K=N, for tiny datasets         |
|                                          |
| Scikit-learn:                            |
| - cross_val_score(model, X, y, cv=5)    |
| - Use Pipeline for preprocessing        |
|                                          |
| Report: "Accuracy: 95% +/- 3%"          |
+------------------------------------------+
```

---

## Key Points

- A **single train/test split** can be unreliable. The accuracy depends on which data lands in the test set.
- **K-Fold Cross-Validation** trains and tests the model K times, each time using a different fold as the test set.
- **Stratified K-Fold** preserves class proportions in each fold. It is the default for classification in scikit-learn.
- **Leave-One-Out (LOOCV)** tests every single sample individually. Use it only for very small datasets.
- Use `cross_val_score(model, X, y, cv=5)` for easy cross-validation.
- Always report **mean and standard deviation**: "95% +/- 3%".
- Use **Pipelines** to include scaling inside cross-validation and prevent data leakage.
- Cross-validation is the standard way to **compare models fairly**.
- Standard choices are **K=5 or K=10**.

---

## Practice Questions

1. Why is a single train/test split unreliable? Give an example of how two different random splits could give very different accuracy scores.

2. Explain 5-Fold Cross-Validation to someone who has never heard of machine learning. Use a real-life analogy.

3. What is the difference between regular K-Fold and Stratified K-Fold? When should you use Stratified K-Fold?

4. Why should you use a Pipeline instead of scaling data before cross-validation? What problem does it prevent?

5. You compare two models using 10-fold CV. Model A gets 92% +/- 2%. Model B gets 93% +/- 8%. Which would you choose and why?

---

## Exercises

### Exercise 1: Comparing K Values

Using the Iris dataset, perform cross-validation with K=3, K=5, K=10, K=20, and LOOCV. Compare the mean accuracy and standard deviation for each. Which K gives the most stable results?

### Exercise 2: Five-Model Showdown

Load the wine dataset from scikit-learn. Compare Logistic Regression, KNN (K=3, K=7), Decision Tree, and Random Forest using 10-fold stratified cross-validation. Which model wins? By how much?

### Exercise 3: Pipeline Cross-Validation

Create a Pipeline that includes StandardScaler and KNeighborsClassifier. Use cross-validation with this pipeline on a dataset of your choice. Verify that the Pipeline correctly scales inside each fold by comparing results with manual (incorrect) pre-scaling.

---

## What Is Next?

You now have the tools to build models, evaluate them properly with cross-validation, and compare them fairly. It is time to put everything together.

In Chapter 30, you will tackle a **complete end-to-end project: Customer Churn Prediction**. You will load real-world data, clean it, engineer features, handle class imbalance, build a pipeline, train multiple models, evaluate them with everything you have learned, and extract business insights. It is the grand finale of this book.
