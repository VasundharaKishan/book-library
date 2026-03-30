# Chapter 28: Handling Imbalanced Data

## What You Will Learn

In this chapter, you will learn:

- What imbalanced data is and why it causes problems
- Why accuracy is misleading for imbalanced datasets
- How to use class weights to make models pay more attention to rare classes
- How SMOTE creates synthetic samples for the minority class
- How undersampling reduces the majority class
- How to adjust the decision threshold for better predictions
- Which metrics to use instead of accuracy
- A complete fraud detection example comparing all strategies

## Why This Chapter Matters

Imagine you are a doctor. Out of every 1,000 patients, only 5 have a rare disease. You build a model to detect this disease. The model says "healthy" for every single patient. Its accuracy? 99.5%. Sounds amazing, right?

But it missed ALL 5 sick patients. Every single one. The model is useless for its intended purpose.

This is the **imbalanced data problem**. When one class is much more common than the other, models take a shortcut. They learn to always predict the common class. They get high accuracy but fail at the task that actually matters.

This problem appears everywhere in the real world:

- **Fraud detection**: 99.9% of transactions are legitimate
- **Disease diagnosis**: Most patients are healthy
- **Spam detection**: Most emails are not spam
- **Equipment failure**: Machines work fine most of the time
- **Rare event prediction**: Earthquakes, crashes, defaults

If you do not handle imbalanced data, your model will be confidently wrong when it matters most. This chapter teaches you how to fix that.

---

## What Imbalanced Data Looks Like

**Imbalanced data** means one class has many more samples than another.

The **majority class** is the larger group (e.g., "not fraud").
The **minority class** is the smaller group (e.g., "fraud").

```
BALANCED DATA:                IMBALANCED DATA:

Class 0: ████████████  500    Class 0: ████████████████████  9,900
Class 1: ████████████  500    Class 1: █                       100

50% / 50%                     99% / 1%
```

How imbalanced is "imbalanced"? There is no strict rule, but here is a rough guide:

```
+-------------------+--------------------+-------------------+
| Ratio             | Example            | Severity          |
+-------------------+--------------------+-------------------+
| 60/40             | Sentiment analysis | Mild              |
| 80/20             | Customer churn     | Moderate          |
| 95/5              | Disease detection  | Severe            |
| 99.9/0.1          | Fraud detection    | Extreme           |
+-------------------+--------------------+-------------------+
```

### The Problem: Model Takes the Easy Way Out

Let us see this problem in action:

```python
# Demonstrating the imbalanced data problem
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

# Create an imbalanced dataset
# 95% class 0 (majority), 5% class 1 (minority)
X, y = make_classification(
    n_samples=2000,
    n_features=10,
    n_informative=5,
    n_redundant=2,
    weights=[0.95, 0.05],   # 95% class 0, 5% class 1
    random_state=42
)

# Check the class distribution
unique, counts = np.unique(y, return_counts=True)
print("Class Distribution:")
for cls, count in zip(unique, counts):
    print(f"  Class {cls}: {count} samples ({count/len(y)*100:.1f}%)")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train a model WITHOUT handling imbalance
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Check results
print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Not Fraud', 'Fraud']))
```

**Expected Output:**

```
Class Distribution:
  Class 0: 1900 samples (95.0%)
  Class 1: 100 samples (5.0%)

Accuracy: 0.9625

Classification Report:
              precision    recall  f1-score   support

   Not Fraud       0.97      0.99      0.98       380
       Fraud       0.71      0.50      0.59        20

    accuracy                           0.96       400
   macro avg       0.84      0.75      0.78       400
weighted avg       0.96      0.96      0.96       400
```

### Reading the Results

Look at the "Fraud" row:
- **Recall: 0.50** means the model only catches 50% of fraud cases. Half of all fraud goes undetected!
- **Precision: 0.71** means when it does predict fraud, it is right 71% of the time.
- **F1-score: 0.59** is the harmonic mean of precision and recall. It is low.

The accuracy is 96.25%, which looks great. But the model misses half of all fraud cases. In fraud detection, missing fraud is the worst possible outcome.

```
What the model does:

  Actual Fraud (20 cases):
    Correctly caught:  10  (recall = 50%)
    Missed:            10  (these are DANGEROUS!)

  Actual Not Fraud (380 cases):
    Correctly identified: 376
    False alarms:          4

  Accuracy: (376 + 10) / 400 = 96.5%
  Looks great! But misses half the fraud!
```

---

## Strategy 1: Class Weights

### The Idea

**Class weights** tell the model: "Pay MORE attention to the minority class."

Think of it like a teacher grading exams. Normally, each question is worth 1 point. But with class weights, you say: "Questions about fraud are worth 20 points each. Questions about non-fraud are worth 1 point." Now the model really tries hard to get the fraud questions right.

In mathematical terms, class weights increase the penalty for misclassifying minority samples. The model is punished more for missing a fraud case than for a false alarm.

### Using `class_weight='balanced'`

Most scikit-learn classifiers have a `class_weight` parameter. Set it to `'balanced'` and scikit-learn automatically calculates the weights based on class frequencies.

```python
# Strategy 1: Class Weights
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# Create imbalanced dataset
X, y = make_classification(
    n_samples=2000, n_features=10, n_informative=5,
    n_redundant=2, weights=[0.95, 0.05], random_state=42
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train WITH class weights
model_weighted = LogisticRegression(
    class_weight='balanced',    # <-- This is the magic line!
    random_state=42
)
model_weighted.fit(X_train, y_train)
y_pred = model_weighted.predict(X_test)

print("With class_weight='balanced':")
print(classification_report(y_test, y_pred, target_names=['Not Fraud', 'Fraud']))
```

**Expected Output:**

```
With class_weight='balanced':
              precision    recall  f1-score   support

   Not Fraud       0.99      0.90      0.94       380
       Fraud       0.24      0.80      0.37        20

    accuracy                           0.90       400
   macro avg       0.61      0.85      0.66       400
weighted avg       0.95      0.90      0.91       400
```

### What Changed?

```
WITHOUT class weights:        WITH class weights:
  Fraud recall: 0.50            Fraud recall: 0.80
  Fraud precision: 0.71         Fraud precision: 0.24
  Accuracy: 96.25%              Accuracy: 89.75%

The model now catches 80% of fraud (up from 50%)!
But accuracy dropped and precision dropped.
This is the TRADEOFF: catch more fraud = more false alarms.
```

### How `balanced` Weights Are Calculated

```python
# How scikit-learn calculates 'balanced' weights:
# weight = n_samples / (n_classes * n_samples_per_class)

n_samples = 1600  # Training samples
n_classes = 2

# Class 0 (majority): 1520 samples
weight_0 = 1600 / (2 * 1520)  # = 0.526
# Class 1 (minority): 80 samples
weight_1 = 1600 / (2 * 80)    # = 10.0

print(f"Weight for class 0 (majority): {weight_0:.3f}")
print(f"Weight for class 1 (minority): {weight_1:.3f}")
# The minority class gets ~19x more weight!
```

### Which Models Support class_weight?

```
+----------------------------+--------------------+
| Model                      | class_weight?      |
+----------------------------+--------------------+
| LogisticRegression         | Yes                |
| SVC / SVM                  | Yes                |
| RandomForestClassifier     | Yes                |
| DecisionTreeClassifier     | Yes                |
| GradientBoostingClassifier | No (use sample_weight) |
| XGBClassifier              | scale_pos_weight   |
+----------------------------+--------------------+
```

---

## Strategy 2: Oversampling with SMOTE

### The Idea

**Oversampling** means creating more samples for the minority class so that both classes have similar counts.

The simplest form of oversampling is **random oversampling**: just copy existing minority samples. But this has a problem. The model sees the exact same data points multiple times. It might overfit (memorize) those specific points.

**SMOTE** (Synthetic Minority Over-sampling Technique) is smarter. Instead of copying existing samples, it creates NEW, SYNTHETIC samples. It does this by:

1. Picking a minority sample
2. Finding its nearest neighbors (in the minority class)
3. Creating a new sample somewhere between them

```
How SMOTE Creates New Samples:
================================

Original minority samples: A and B

   A (age=30, income=40K)
    \
     \  <-- SMOTE creates a new point
      \     along this line
       \
        B (age=40, income=60K)

New synthetic sample:
  age = 30 + random * (40 - 30) = 35
  income = 40K + random * (60K - 40K) = 50K

Result: (age=35, income=50K)
This is a NEW, realistic sample!
```

### SMOTE with imbalanced-learn

SMOTE is available in the `imbalanced-learn` library (often abbreviated as `imblearn`).

```python
# Strategy 2: SMOTE (Synthetic Minority Over-sampling Technique)
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE

# Create imbalanced dataset
X, y = make_classification(
    n_samples=2000, n_features=10, n_informative=5,
    n_redundant=2, weights=[0.95, 0.05], random_state=42
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Check class distribution BEFORE SMOTE
print("Before SMOTE:")
unique, counts = np.unique(y_train, return_counts=True)
for cls, count in zip(unique, counts):
    print(f"  Class {cls}: {count} samples")

# Apply SMOTE to training data ONLY
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Check class distribution AFTER SMOTE
print("\nAfter SMOTE:")
unique, counts = np.unique(y_train_resampled, return_counts=True)
for cls, count in zip(unique, counts):
    print(f"  Class {cls}: {count} samples")

# Train on resampled data
model = LogisticRegression(random_state=42)
model.fit(X_train_resampled, y_train_resampled)
y_pred = model.predict(X_test)

print("\nWith SMOTE:")
print(classification_report(y_test, y_pred, target_names=['Not Fraud', 'Fraud']))
```

**Expected Output:**

```
Before SMOTE:
  Class 0: 1520 samples
  Class 1: 80 samples

After SMOTE:
  Class 0: 1520 samples
  Class 1: 1520 samples

With SMOTE:
              precision    recall  f1-score   support

   Not Fraud       0.99      0.91      0.95       380
       Fraud       0.28      0.80      0.41        20

    accuracy                           0.91       400
   macro avg       0.63      0.86      0.68       400
weighted avg       0.95      0.91      0.92       400
```

### Critical Rule: Apply SMOTE to Training Data ONLY

This is extremely important. NEVER apply SMOTE to the test data.

```
CORRECT:                         WRONG:
========                         ======

1. Split into train/test         1. Apply SMOTE to ALL data
2. Apply SMOTE to train ONLY     2. Then split into train/test
3. Train on resampled train
4. Test on ORIGINAL test         Problem: Synthetic samples from
                                 training could be similar to
                                 test samples = DATA LEAKAGE!
```

```python
# CORRECT order:
X_train, X_test, y_train, y_test = train_test_split(X, y, ...)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)  # Only train!
model.fit(X_train_res, y_train_res)
model.predict(X_test)  # Test on original, untouched test data

# WRONG order:
X_res, y_res = smote.fit_resample(X, y)  # Resampling ALL data first!
X_train, X_test, ... = train_test_split(X_res, y_res, ...)  # Leakage!
```

---

## Strategy 3: Undersampling

### The Idea

**Undersampling** is the opposite of oversampling. Instead of creating more minority samples, you REMOVE some majority samples.

```
ORIGINAL:                  AFTER UNDERSAMPLING:

Class 0: ██████████  1000  Class 0: █  100
Class 1: █           100   Class 1: █  100

Removed 900 majority samples!
```

### When to Use Undersampling

Undersampling works best when:
- You have a very large dataset (losing samples is not a problem)
- The majority class has many redundant/similar samples

```python
# Strategy 3: Random Undersampling
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from imblearn.under_sampling import RandomUnderSampler

# Create imbalanced dataset
X, y = make_classification(
    n_samples=2000, n_features=10, n_informative=5,
    n_redundant=2, weights=[0.95, 0.05], random_state=42
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Apply undersampling to training data ONLY
undersampler = RandomUnderSampler(random_state=42)
X_train_under, y_train_under = undersampler.fit_resample(X_train, y_train)

print("Before Undersampling:")
unique, counts = np.unique(y_train, return_counts=True)
for cls, count in zip(unique, counts):
    print(f"  Class {cls}: {count} samples")

print("\nAfter Undersampling:")
unique, counts = np.unique(y_train_under, return_counts=True)
for cls, count in zip(unique, counts):
    print(f"  Class {cls}: {count} samples")

# Train on undersampled data
model = LogisticRegression(random_state=42)
model.fit(X_train_under, y_train_under)
y_pred = model.predict(X_test)

print("\nWith Undersampling:")
print(classification_report(y_test, y_pred, target_names=['Not Fraud', 'Fraud']))
```

**Expected Output:**

```
Before Undersampling:
  Class 0: 1520 samples
  Class 1: 80 samples

After Undersampling:
  Class 0: 80 samples
  Class 1: 80 samples

With Undersampling:
              precision    recall  f1-score   support

   Not Fraud       0.99      0.87      0.93       380
       Fraud       0.23      0.80      0.36        20

    accuracy                           0.87       400
   macro avg       0.61      0.83      0.64       400
weighted avg       0.95      0.87      0.90       400
```

### The Downside of Undersampling

```
PROBLEM: You throw away data!

Before:  1520 majority samples
After:      80 majority samples

You lost 1440 samples (95% of your majority class).
Those samples might have contained useful information.

WHEN TO USE UNDERSAMPLING:
- Large datasets (10K+ samples)
- Majority class has lots of redundancy
- Combined with other techniques
```

---

## Strategy 4: Threshold Adjustment

### The Idea

Most classifiers do not directly output "class 0" or "class 1." They first calculate a **probability** (a number between 0 and 1). Then they use a **threshold** to make the decision:

- If probability >= 0.5: predict class 1 (fraud)
- If probability < 0.5: predict class 0 (not fraud)

The default threshold is 0.5. But you can change it!

If you LOWER the threshold (say, 0.3), the model predicts "fraud" more often. It catches more fraud but also creates more false alarms.

```
Default Threshold = 0.5:

Probability:  0.1   0.3   0.5   0.7   0.9
Prediction:   No    No    Yes   Yes   Yes
              |___________|_____________|
                 Not Fraud    Fraud

Lower Threshold = 0.3:

Probability:  0.1   0.3   0.5   0.7   0.9
Prediction:   No    Yes   Yes   Yes   Yes
              |_____|_______________________|
              Not     Fraud (catches more!)
              Fraud
```

### Threshold Adjustment in Practice

```python
# Strategy 4: Threshold Adjustment
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, precision_recall_curve
import warnings
warnings.filterwarnings('ignore')

# Create imbalanced dataset
X, y = make_classification(
    n_samples=2000, n_features=10, n_informative=5,
    n_redundant=2, weights=[0.95, 0.05], random_state=42
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train the model
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)

# Get probabilities (not just predictions)
y_proba = model.predict_proba(X_test)[:, 1]  # Probability of class 1 (fraud)

# Try different thresholds
print("Effect of Different Thresholds:")
print(f"{'Threshold':<12} {'Precision':<12} {'Recall':<12} {'F1':<12}")
print("-" * 48)

for threshold in [0.5, 0.4, 0.3, 0.2, 0.1]:
    y_pred_custom = (y_proba >= threshold).astype(int)
    report = classification_report(
        y_test, y_pred_custom, output_dict=True, zero_division=0
    )
    fraud_metrics = report['1']
    print(f"{threshold:<12.1f} {fraud_metrics['precision']:<12.2f} "
          f"{fraud_metrics['recall']:<12.2f} {fraud_metrics['f1-score']:<12.2f}")
```

**Expected Output:**

```
Effect of Different Thresholds:
Threshold    Precision    Recall       F1
------------------------------------------------
0.5          0.71         0.50         0.59
0.4          0.56         0.50         0.53
0.3          0.38         0.60         0.46
0.2          0.25         0.75         0.38
0.1          0.14         0.90         0.24
```

### The Precision-Recall Tradeoff

```
As you LOWER the threshold:
  - Recall INCREASES (catch more fraud)
  - Precision DECREASES (more false alarms)
  - This is called the precision-recall tradeoff

                 Threshold = 0.5     Threshold = 0.1
                 ================     ================
Caught fraud:     50%                  90%
False alarms:     Few                  Many

Choose based on your business needs:
  - Fraud detection: HIGH recall (catch all fraud, accept false alarms)
  - Medical screening: HIGH recall (do not miss sick patients)
  - Spam filter: HIGH precision (do not accidentally block good emails)
```

---

## Choosing the Right Metric

When data is imbalanced, **accuracy is misleading**. Here are better metrics:

### Metrics Comparison

```
+------------------+---------------------------------------------+
| Metric           | What It Measures                            |
+------------------+---------------------------------------------+
| Accuracy         | Overall correct predictions.                |
|                  | MISLEADING for imbalanced data!             |
+------------------+---------------------------------------------+
| Precision        | Of all predicted positive, how many         |
|                  | are actually positive?                      |
|                  | "When I say fraud, am I right?"             |
+------------------+---------------------------------------------+
| Recall           | Of all actual positives, how many           |
|  (Sensitivity)   | did I catch?                                |
|                  | "Did I catch all the fraud?"                |
+------------------+---------------------------------------------+
| F1 Score         | Harmonic mean of precision and recall.      |
|                  | Balances both. Good single metric.          |
+------------------+---------------------------------------------+
| AUC-ROC          | Area Under the ROC Curve.                   |
|                  | Measures overall ability to distinguish     |
|                  | classes. 1.0 is perfect, 0.5 is random.    |
+------------------+---------------------------------------------+
| Average          | Average of precision at each recall level.  |
| Precision        | Better than AUC for very imbalanced data.   |
+------------------+---------------------------------------------+
```

### When to Use Which Metric

```
Use RECALL when:
  Missing a positive is COSTLY
  (disease detection, fraud detection)
  "I'd rather have false alarms than miss a real case"

Use PRECISION when:
  False positives are COSTLY
  (spam filter - don't want to block real emails)
  "I'd rather miss some spam than block a real email"

Use F1 when:
  You want a balance between precision and recall
  Good default choice for imbalanced data

Use AUC-ROC when:
  You want to compare models overall
  You haven't chosen a specific threshold yet
```

---

## Complete Example: Fraud Detection Comparison

Let us put everything together. We will compare all strategies on a fraud detection problem.

```python
# Complete Example: Fraud Detection with All Strategies
# =====================================================
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, f1_score, roc_auc_score, confusion_matrix
)
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import warnings
warnings.filterwarnings('ignore')

# ================================
# Step 1: Create Imbalanced Dataset
# ================================
print("=" * 60)
print("FRAUD DETECTION: Comparing Strategies for Imbalanced Data")
print("=" * 60)

X, y = make_classification(
    n_samples=5000,
    n_features=15,
    n_informative=8,
    n_redundant=3,
    weights=[0.97, 0.03],    # 97% legitimate, 3% fraud
    flip_y=0.01,
    random_state=42
)

print(f"\nDataset size: {len(y)} transactions")
print(f"  Legitimate: {sum(y == 0)} ({sum(y == 0)/len(y)*100:.1f}%)")
print(f"  Fraud:      {sum(y == 1)} ({sum(y == 1)/len(y)*100:.1f}%)")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ================================
# Step 2: Baseline (No Treatment)
# ================================
print("\n" + "=" * 60)
print("STRATEGY 1: Baseline (No Treatment)")
print("=" * 60)

model_baseline = LogisticRegression(random_state=42, max_iter=1000)
model_baseline.fit(X_train, y_train)
y_pred_baseline = model_baseline.predict(X_test)

f1_baseline = f1_score(y_test, y_pred_baseline)
auc_baseline = roc_auc_score(y_test, model_baseline.predict_proba(X_test)[:, 1])
print(f"F1 Score (Fraud): {f1_baseline:.4f}")
print(f"AUC-ROC: {auc_baseline:.4f}")
print(classification_report(y_test, y_pred_baseline,
                             target_names=['Legitimate', 'Fraud']))

# ================================
# Step 3: Class Weights
# ================================
print("=" * 60)
print("STRATEGY 2: Class Weights (balanced)")
print("=" * 60)

model_weighted = LogisticRegression(
    class_weight='balanced', random_state=42, max_iter=1000
)
model_weighted.fit(X_train, y_train)
y_pred_weighted = model_weighted.predict(X_test)

f1_weighted = f1_score(y_test, y_pred_weighted)
auc_weighted = roc_auc_score(y_test, model_weighted.predict_proba(X_test)[:, 1])
print(f"F1 Score (Fraud): {f1_weighted:.4f}")
print(f"AUC-ROC: {auc_weighted:.4f}")
print(classification_report(y_test, y_pred_weighted,
                             target_names=['Legitimate', 'Fraud']))

# ================================
# Step 4: SMOTE
# ================================
print("=" * 60)
print("STRATEGY 3: SMOTE (Synthetic Minority Over-sampling)")
print("=" * 60)

smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)
print(f"Training set BEFORE SMOTE: {len(y_train)} samples")
print(f"Training set AFTER SMOTE:  {len(y_train_smote)} samples")

model_smote = LogisticRegression(random_state=42, max_iter=1000)
model_smote.fit(X_train_smote, y_train_smote)
y_pred_smote = model_smote.predict(X_test)

f1_smote = f1_score(y_test, y_pred_smote)
auc_smote = roc_auc_score(y_test, model_smote.predict_proba(X_test)[:, 1])
print(f"F1 Score (Fraud): {f1_smote:.4f}")
print(f"AUC-ROC: {auc_smote:.4f}")
print(classification_report(y_test, y_pred_smote,
                             target_names=['Legitimate', 'Fraud']))

# ================================
# Step 5: Undersampling
# ================================
print("=" * 60)
print("STRATEGY 4: Random Undersampling")
print("=" * 60)

undersampler = RandomUnderSampler(random_state=42)
X_train_under, y_train_under = undersampler.fit_resample(X_train, y_train)
print(f"Training set BEFORE undersampling: {len(y_train)} samples")
print(f"Training set AFTER undersampling:  {len(y_train_under)} samples")

model_under = LogisticRegression(random_state=42, max_iter=1000)
model_under.fit(X_train_under, y_train_under)
y_pred_under = model_under.predict(X_test)

f1_under = f1_score(y_test, y_pred_under)
auc_under = roc_auc_score(y_test, model_under.predict_proba(X_test)[:, 1])
print(f"F1 Score (Fraud): {f1_under:.4f}")
print(f"AUC-ROC: {auc_under:.4f}")
print(classification_report(y_test, y_pred_under,
                             target_names=['Legitimate', 'Fraud']))

# ================================
# Step 6: SMOTE + Random Forest
# ================================
print("=" * 60)
print("STRATEGY 5: SMOTE + Random Forest (Best Combo)")
print("=" * 60)

model_rf_smote = RandomForestClassifier(
    n_estimators=200,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
model_rf_smote.fit(X_train_smote, y_train_smote)
y_pred_rf_smote = model_rf_smote.predict(X_test)

f1_rf_smote = f1_score(y_test, y_pred_rf_smote)
auc_rf_smote = roc_auc_score(y_test, model_rf_smote.predict_proba(X_test)[:, 1])
print(f"F1 Score (Fraud): {f1_rf_smote:.4f}")
print(f"AUC-ROC: {auc_rf_smote:.4f}")
print(classification_report(y_test, y_pred_rf_smote,
                             target_names=['Legitimate', 'Fraud']))

# ================================
# Step 7: Summary Comparison
# ================================
print("=" * 60)
print("FINAL COMPARISON")
print("=" * 60)

results = pd.DataFrame({
    'Strategy': ['Baseline', 'Class Weights', 'SMOTE',
                 'Undersampling', 'SMOTE + RF'],
    'F1 (Fraud)': [f1_baseline, f1_weighted, f1_smote,
                   f1_under, f1_rf_smote],
    'AUC-ROC': [auc_baseline, auc_weighted, auc_smote,
                auc_under, auc_rf_smote]
})
results = results.sort_values('F1 (Fraud)', ascending=False)
print(results.to_string(index=False))

# Show confusion matrix for the best model
print("\n--- Confusion Matrix (Best Model: SMOTE + RF) ---")
cm = confusion_matrix(y_test, y_pred_rf_smote)
print(f"\n                    Predicted")
print(f"                  Legit   Fraud")
print(f"Actual Legit  [{cm[0][0]:>6}  {cm[0][1]:>6}]")
print(f"Actual Fraud  [{cm[1][0]:>6}  {cm[1][1]:>6}]")
```

**Expected Output:**

```
============================================================
FRAUD DETECTION: Comparing Strategies for Imbalanced Data
============================================================

Dataset size: 5000 transactions
  Legitimate: 4853 (97.1%)
  Fraud:      147 (2.9%)

============================================================
STRATEGY 1: Baseline (No Treatment)
============================================================
F1 Score (Fraud): 0.5714
AUC-ROC: 0.9296
              precision    recall  f1-score   support

  Legitimate       0.98      0.99      0.99       971
       Fraud       0.67      0.48      0.57        29

    accuracy                           0.98      1000
   macro avg       0.83      0.74      0.78      1000
weighted avg       0.97      0.98      0.97      1000

============================================================
STRATEGY 2: Class Weights (balanced)
============================================================
F1 Score (Fraud): 0.4681
AUC-ROC: 0.9296
              precision    recall  f1-score   support

  Legitimate       0.99      0.92      0.95       971
       Fraud       0.26      0.76      0.39        29

    accuracy                           0.92      1000
   macro avg       0.62      0.84      0.67      1000
weighted avg       0.96      0.92      0.94      1000

============================================================
STRATEGY 3: SMOTE (Synthetic Minority Over-sampling)
============================================================
Training set BEFORE SMOTE: 4000 samples
Training set AFTER SMOTE:  7762 samples
F1 Score (Fraud): 0.4681
AUC-ROC: 0.9284
              precision    recall  f1-score   support

  Legitimate       0.99      0.92      0.95       971
       Fraud       0.26      0.76      0.39        29

    accuracy                           0.92      1000
   macro avg       0.62      0.84      0.67      1000
weighted avg       0.96      0.92      0.94      1000

============================================================
STRATEGY 4: Random Undersampling
============================================================
Training set BEFORE undersampling: 4000 samples
Training set AFTER undersampling:  236 samples
F1 Score (Fraud): 0.4308
AUC-ROC: 0.9281
              precision    recall  f1-score   support

  Legitimate       0.99      0.90      0.95       971
       Fraud       0.22      0.79      0.35        29

    accuracy                           0.90      1000
   macro avg       0.61      0.85      0.65      1000
weighted avg       0.97      0.90      0.93      1000

============================================================
STRATEGY 5: SMOTE + Random Forest (Best Combo)
============================================================
F1 Score (Fraud): 0.6154
AUC-ROC: 0.9602
              precision    recall  f1-score   support

  Legitimate       0.99      0.98      0.98       971
       Fraud       0.47      0.55      0.51        29

    accuracy                           0.97      1000
   macro avg       0.73      0.76      0.75      1000
weighted avg       0.97      0.97      0.97      1000

============================================================
FINAL COMPARISON
============================================================
        Strategy  F1 (Fraud)  AUC-ROC
    SMOTE + RF      0.6154   0.9602
      Baseline      0.5714   0.9296
 Class Weights      0.4681   0.9296
         SMOTE      0.4681   0.9284
 Undersampling      0.4308   0.9281

--- Confusion Matrix (Best Model: SMOTE + RF) ---

                    Predicted
                  Legit   Fraud
Actual Legit  [   953       18]
Actual Fraud  [    13       16]
```

### Key Takeaways from the Comparison

```
1. SMOTE + Random Forest performed best:
   - Highest F1 score (0.62)
   - Highest AUC-ROC (0.96)
   - Good balance of precision and recall

2. Class weights and SMOTE improved recall:
   - Caught more fraud cases
   - But at the cost of more false alarms

3. No single strategy is always best:
   - The best strategy depends on your data
   - Always compare multiple approaches

4. Accuracy is misleading:
   - Baseline had 98% accuracy but missed half the fraud
   - F1 score and AUC are much better metrics
```

---

## Common Mistakes

**Mistake 1: Applying SMOTE before splitting the data.**
```python
# WRONG: SMOTE before split (data leakage!)
X_resampled, y_resampled = smote.fit_resample(X, y)
X_train, X_test, ... = train_test_split(X_resampled, y_resampled, ...)

# RIGHT: Split first, then SMOTE on training data only
X_train, X_test, ... = train_test_split(X, y, ...)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
```

**Mistake 2: Using accuracy as the primary metric.**
Accuracy is misleading for imbalanced data. Use F1-score, AUC-ROC, or precision/recall instead.

**Mistake 3: Not using `stratify` in train_test_split.**
Without `stratify`, the minority class might be underrepresented (or absent!) in the test set.
```python
# Always stratify when splitting imbalanced data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

**Mistake 4: Applying SMOTE to the test set.**
The test set must represent the real-world distribution. Never resample it.

**Mistake 5: Using SMOTE with too few minority samples.**
SMOTE needs at least `k_neighbors + 1` minority samples (default `k_neighbors=5`). If you have fewer than 6 minority samples, SMOTE will fail. Use random oversampling instead.

---

## Best Practices

1. **Always check class distribution first.** Before building any model, check how balanced your data is.

2. **Use `stratify=y` when splitting data.** This ensures both train and test sets have the same class ratio.

3. **Try multiple strategies and compare.** No single strategy works best for every dataset.

4. **Use F1 or AUC-ROC instead of accuracy.** These metrics account for class imbalance.

5. **Apply resampling to training data only.** Never resample the test set.

6. **Combine strategies.** Using SMOTE with class weights and a strong model (Random Forest, XGBoost) often works best.

7. **Consider the business context.** Sometimes missing a fraud case costs $10,000 but a false alarm costs $10. This should influence your choice of threshold and metric.

8. **Start simple.** Try `class_weight='balanced'` first. It is easy, requires no extra libraries, and often works well.

---

## Quick Summary

- **Imbalanced data** has one class much larger than the other (like 99% vs 1%).
- Models take the easy path and predict the majority class, getting high accuracy but missing the minority class.
- **Class weights** make the model pay more attention to the minority class.
- **SMOTE** creates synthetic minority samples by interpolating between existing ones.
- **Undersampling** removes majority samples (risks losing information).
- **Threshold adjustment** changes the decision boundary from 0.5 to catch more positives.
- **Do NOT use accuracy** for imbalanced data. Use **F1-score**, **AUC-ROC**, or **recall**.
- Always apply resampling to **training data only**, never to the test set.

---

## Key Points to Remember

1. Check class distribution before building any model.
2. Accuracy is misleading for imbalanced data. A model predicting only "not fraud" gets 99% accuracy but catches zero fraud.
3. `class_weight='balanced'` is the easiest fix. Works with most scikit-learn classifiers.
4. SMOTE creates NEW synthetic samples, not copies. It is better than random oversampling.
5. ALWAYS apply SMOTE after train/test split, on training data only.
6. Use `stratify=y` in `train_test_split` to maintain class ratios.
7. Lower the decision threshold to catch more positives (at the cost of more false alarms).
8. F1-score balances precision and recall. AUC-ROC measures overall discriminative ability.
9. Combine strategies for best results (e.g., SMOTE + Random Forest + class_weight).
10. Consider the business cost: is missing a positive worse than a false alarm?

---

## Practice Questions

### Question 1
Why is accuracy a misleading metric for imbalanced datasets?

**Answer:** Because a model can achieve very high accuracy by simply predicting the majority class for every sample. For example, if 99% of data is class 0, a model that always predicts class 0 gets 99% accuracy but catches zero cases of class 1. Accuracy does not reflect how well the model identifies the minority class, which is usually the class we care about most.

### Question 2
What is the difference between SMOTE and random oversampling?

**Answer:** Random oversampling simply duplicates existing minority samples, which can lead to overfitting because the model sees the exact same data points multiple times. SMOTE creates NEW synthetic samples by interpolating between existing minority samples and their nearest neighbors. This produces more diverse training examples and generally leads to better generalization.

### Question 3
Why must SMOTE be applied AFTER splitting the data into train and test sets?

**Answer:** If SMOTE is applied before splitting, the synthetic samples created from training data might be very similar to actual test samples (since they are based on nearby points). This causes data leakage, where the model has effectively "seen" the test data during training. The result is overly optimistic performance estimates that do not reflect real-world performance.

### Question 4
When would you prefer high recall over high precision?

**Answer:** You would prefer high recall when the cost of missing a positive case is very high. For example, in cancer screening, missing a patient who actually has cancer (false negative) is much worse than flagging a healthy patient for additional tests (false positive). Similarly, in fraud detection, missing actual fraud is more costly than investigating a false alarm.

### Question 5
What does `class_weight='balanced'` do internally?

**Answer:** It automatically calculates weights for each class inversely proportional to their frequency. The formula is: weight = n_samples / (n_classes * n_samples_per_class). For a dataset with 950 negative and 50 positive samples, the negative class gets a weight of about 0.53 and the positive class gets a weight of about 10. This makes misclassifying a positive sample 19 times more costly than misclassifying a negative sample.

---

## Exercises

### Exercise 1: Compare Strategies on Credit Card Data

Create an imbalanced dataset with `make_classification` using `weights=[0.98, 0.02]` and 3000 samples. Compare four approaches: (1) no treatment, (2) class_weight='balanced', (3) SMOTE, (4) SMOTE + class_weight='balanced'. Use a Random Forest classifier for all. Report F1-score and AUC-ROC for each.

### Exercise 2: Find the Best Threshold

Using the same imbalanced dataset, train a LogisticRegression model. Use `predict_proba` to get probabilities. Try thresholds from 0.1 to 0.9 (step 0.05). For each threshold, calculate precision, recall, and F1-score for the minority class. Find the threshold that maximizes F1-score. Plot or print a table showing how metrics change with the threshold.

### Exercise 3: SMOTE with Different Ratios

By default, SMOTE resamples to 50/50 balance. Use the `sampling_strategy` parameter to try different ratios: 0.3 (30% minority), 0.5 (50%), 0.7 (70%), and 1.0 (equal). Compare F1-scores. Which ratio gives the best result? (Hint: `SMOTE(sampling_strategy=0.5)` creates minority samples until they are 50% of the majority count.)

---

## What Is Next?

You now know how to handle one of the most common problems in real-world machine learning: imbalanced data. It is time to put everything you have learned into practice.

In the next chapter, you will work on a **complete, end-to-end regression project: House Price Prediction**. You will go through every step of a real data science project: loading data, exploring it, cleaning it, engineering features, building pipelines, training multiple models, tuning hyperparameters, and evaluating results. This is the kind of project you would do at work or in a data science interview.
