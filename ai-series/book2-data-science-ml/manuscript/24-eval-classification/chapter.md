# Chapter 24: Model Evaluation — Classification

## What You Will Learn

In this chapter, you will learn:

- Why accuracy can be dangerously misleading
- How to read a confusion matrix and what TP, TN, FP, FN mean
- What precision and recall measure and why both matter
- What the F1 score is and when to use it
- The precision-recall tradeoff and how to navigate it
- How ROC curves and AUC work
- How to use sklearn's classification_report, confusion_matrix, and roc_auc_score
- How multi-class metrics work (macro, micro, weighted averaging)
- How to evaluate a complete disease prediction model

## Why This Chapter Matters

Imagine you build a model to detect cancer from medical scans. You test it on 1,000 patients. Your model predicts "No Cancer" for everyone. Your accuracy? 99%.

Sounds amazing, right? But wait. Out of those 1,000 patients, 10 actually had cancer. Your model missed every single one of them. Those 10 people think they are healthy when they are not. That "99% accurate" model could cost lives.

This is the **accuracy paradox**. When one class is much more common than the other, accuracy becomes meaningless.

In this chapter, you will learn metrics that expose this problem and give you the full picture. These metrics are essential for any classification problem, especially when the stakes are high (medical diagnosis, fraud detection, security systems).

---

## Why Accuracy Is Misleading

**Accuracy** is the percentage of correct predictions:

```
Accuracy = (Correct Predictions) / (Total Predictions)
```

Here is why it fails:

```
The Accuracy Trap:
══════════════════

Dataset: 10,000 emails
  - 9,900 are NOT spam (99%)
  - 100 ARE spam (1%)

Model A: Predicts "NOT SPAM" for everything
  Accuracy = 9,900 / 10,000 = 99%  ← Looks great!
  Spam caught: 0 out of 100         ← Completely useless!

Model B: Actually tries to detect spam
  Accuracy = 9,700 / 10,000 = 97%  ← Looks worse!
  Spam caught: 90 out of 100        ← Actually useful!

Accuracy says Model A is better.
In reality, Model B is far more useful.
```

The problem gets worse with more imbalanced data. If only 0.01% of transactions are fraud, a model that says "not fraud" for everything gets 99.99% accuracy.

We need better metrics. Enter the confusion matrix.

---

## The Confusion Matrix

A **confusion matrix** is a table that shows exactly what your model got right and wrong.

### The Four Outcomes

Every prediction falls into one of four categories:

```
                           What the Model Predicted
                        ┌──────────────┬──────────────┐
                        │  Predicted   │  Predicted   │
                        │  NEGATIVE    │  POSITIVE    │
           ┌────────────┼──────────────┼──────────────┤
  What     │  Actually  │     TN       │     FP       │
  Actually │  NEGATIVE  │ True Negative│False Positive│
  Happened ├────────────┼──────────────┼──────────────┤
           │  Actually  │     FN       │     TP       │
           │  POSITIVE  │False Negative│True Positive │
           └────────────┴──────────────┴──────────────┘
```

### Medical Test Analogy

Let us use a medical test for a disease to make this concrete:

```
Medical Test Results:
═════════════════════

TRUE NEGATIVE (TN): "Test says healthy, patient IS healthy"
  ✓ Correct! Nothing to worry about.
  Example: You do not have the flu. Test says no flu. Good.

FALSE POSITIVE (FP): "Test says sick, patient IS healthy"
  ✗ False alarm! Unnecessary worry and follow-up tests.
  Example: You are healthy. Test says you have the flu. Annoying.

FALSE NEGATIVE (FN): "Test says healthy, patient IS sick"
  ✗ DANGEROUS! Patient thinks they are fine but they are not!
  Example: You have the flu. Test says no flu. You spread it.

TRUE POSITIVE (TP): "Test says sick, patient IS sick"
  ✓ Correct! Patient gets the treatment they need.
  Example: You have the flu. Test catches it. You get treated.
```

A handy way to remember:
- **True/False** = Was the prediction correct?
- **Positive/Negative** = What did the model predict?

```
Memory Trick:
═════════════

TRUE  = Prediction was CORRECT
FALSE = Prediction was WRONG

POSITIVE = Model said YES (has disease, is spam, is fraud)
NEGATIVE = Model said NO  (no disease, not spam, not fraud)

So:
  True Positive  = Correctly said YES ✓
  True Negative  = Correctly said NO  ✓
  False Positive = Wrongly said YES   ✗ (false alarm)
  False Negative = Wrongly said NO    ✗ (missed it)
```

### Confusion Matrix in Python

```python
import numpy as np
from sklearn.metrics import confusion_matrix

# Medical test results
# 1 = has disease, 0 = healthy
y_actual = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0])
y_predicted = np.array([0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0])

# Calculate confusion matrix
cm = confusion_matrix(y_actual, y_predicted)

print("Confusion Matrix:")
print(cm)

# Label the results clearly
tn, fp, fn, tp = cm.ravel()  # Unpack the matrix

print(f"\nDetailed Results:")
print(f"  True Negatives  (TN): {tn}  (correctly said healthy)")
print(f"  False Positives (FP): {fp}  (wrongly said sick - false alarm)")
print(f"  False Negatives (FN): {fn}  (wrongly said healthy - MISSED!)")
print(f"  True Positives  (TP): {tp}  (correctly said sick)")

print(f"\nTotal patients: {len(y_actual)}")
print(f"  Actually healthy: {sum(y_actual == 0)}")
print(f"  Actually sick:    {sum(y_actual == 1)}")
print(f"  Correctly diagnosed: {tn + tp}")
print(f"  Accuracy: {(tn + tp) / len(y_actual):.1%}")
```

Expected output:

```
Confusion Matrix:
[[12  1]
 [ 2  5]]

Detailed Results:
  True Negatives  (TN): 12  (correctly said healthy)
  False Positives (FP): 1   (wrongly said sick - false alarm)
  False Negatives (FN): 2   (wrongly said healthy - MISSED!)
  True Positives  (TP): 5   (correctly said sick)

Total patients: 20
  Actually healthy: 13
  Actually sick:    7
  Correctly diagnosed: 17
  Accuracy: 85.0%
```

**Line-by-line explanation:**

1. `confusion_matrix(y_actual, y_predicted)` - Creates the confusion matrix. First argument is actual labels, second is predictions.
2. `cm.ravel()` - Flattens the 2x2 matrix into four values: TN, FP, FN, TP.
3. The matrix shows: 12 healthy patients correctly identified, 1 false alarm, 2 missed diseases, 5 correctly caught diseases.

---

## Precision

**Precision** answers: "Of all the patients the model said were sick, how many actually were sick?"

```
Precision = TP / (TP + FP)

           = True Positives / (True Positives + False Positives)

           = Correct positive predictions / All positive predictions
```

```
Precision Visualization:
════════════════════════

All predictions of "POSITIVE" (sick):

    ┌─────────────────────────────┐
    │  TP  TP  TP  TP  TP │ FP   │
    │  (really sick)       │(not) │
    └─────────────────────────────┘
         5 correct           1 wrong

    Precision = 5 / (5 + 1) = 5/6 = 0.833

    "83% of patients we flagged as sick were actually sick."
```

**High precision means few false alarms.**

When is precision important?
- Spam filters: You do not want legitimate emails sent to spam (FP is bad)
- Search engines: You want results that are actually relevant
- Drug testing: You want to be sure a drug works before approving it

```python
from sklearn.metrics import precision_score

precision = precision_score(y_actual, y_predicted)
print(f"Precision: {precision:.3f}")
print(f"Of all patients we said were sick, {precision:.0%} actually were.")
```

Expected output:

```
Precision: 0.833
Of all patients we said were sick, 83% actually were.
```

---

## Recall (Sensitivity)

**Recall** answers: "Of all patients who were actually sick, how many did we catch?"

```
Recall = TP / (TP + FN)

       = True Positives / (True Positives + False Negatives)

       = Correct positive predictions / All actual positives
```

```
Recall Visualization:
═════════════════════

All patients who ARE ACTUALLY SICK:

    ┌─────────────────────────────┐
    │  TP  TP  TP  TP  TP │ FN FN│
    │  (we caught them)    │(miss)│
    └─────────────────────────────┘
         5 caught           2 missed

    Recall = 5 / (5 + 2) = 5/7 = 0.714

    "We caught 71% of sick patients."
```

**High recall means we catch most positive cases.**

When is recall important?
- Cancer screening: Missing a cancer patient (FN) could be fatal
- Fraud detection: Missing fraud (FN) costs money
- Airport security: Missing a threat (FN) is dangerous

```python
from sklearn.metrics import recall_score

recall = recall_score(y_actual, y_predicted)
print(f"Recall: {recall:.3f}")
print(f"We caught {recall:.0%} of all sick patients.")
print(f"We MISSED {1-recall:.0%} of sick patients.")
```

Expected output:

```
Recall: 0.714
We caught 71% of all sick patients.
We MISSED 29% of sick patients.
```

---

## F1 Score

The **F1 Score** is the balance between precision and recall. It is their **harmonic mean**.

```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

### Why Not Just Average?

The regular average can be misleading:

```
Why Harmonic Mean, Not Regular Average?
═══════════════════════════════════════

Scenario: Precision = 1.0, Recall = 0.01

Regular average: (1.0 + 0.01) / 2 = 0.505  ← Seems OK!
Harmonic mean:   2 * (1.0 * 0.01) / (1.0 + 0.01) = 0.020  ← Terrible!

The harmonic mean punishes imbalance.
If either precision or recall is low, F1 is low.
You cannot hide behind one good metric.
```

### F1 Score Scale

```
F1 Score Interpretation:
════════════════════════

0.0          0.5          0.7          0.9          1.0
 |            |            |            |            |
 ├────────────┼────────────┼────────────┼────────────┤
 │    Poor    │    Fair    │    Good    │ Excellent  │
 │            │            │            │            │

F1 = 1.0  → Perfect precision AND recall
F1 = 0.0  → Either precision or recall is 0
```

```python
from sklearn.metrics import f1_score

f1 = f1_score(y_actual, y_predicted)
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1 Score:  {f1:.3f}")
```

Expected output:

```
Precision: 0.833
Recall:    0.714
F1 Score:  0.769
```

---

## The Precision-Recall Tradeoff

Here is an uncomfortable truth: **you cannot maximize both precision and recall at the same time.** Improving one usually hurts the other.

### Why the Tradeoff Exists

Most classifiers output a **probability** (e.g., "70% chance of disease"). We choose a **threshold** to convert that probability to a prediction. Changing the threshold shifts the balance:

```
The Threshold Effect:
═════════════════════

Threshold = 0.5 (default):
  Predict "sick" if probability > 50%
  → Balanced precision and recall

Threshold = 0.3 (lower, more sensitive):
  Predict "sick" if probability > 30%
  → Catches more sick patients (higher recall ↑)
  → More false alarms (lower precision ↓)

Threshold = 0.8 (higher, more cautious):
  Predict "sick" if probability > 80%
  → Very sure about positive predictions (higher precision ↑)
  → Misses more sick patients (lower recall ↓)

    Precision
    ^
    |  *
    |    *
    |      *
    |        *
    |          *
    |            *
    |              *
    +──────────────────> Recall

    As recall increases, precision tends to decrease.
```

### Choosing Your Priority

```
Which matters more?
═══════════════════

PRECISION is more important when:
  - False positives are costly or harmful
  - Example: Spam filter (legitimate email in spam = bad)
  - Example: Criminal conviction (convicting innocent = terrible)

RECALL is more important when:
  - False negatives are costly or harmful
  - Example: Cancer screening (missing cancer = dangerous)
  - Example: Fraud detection (missing fraud = money lost)
  - Example: Airport security (missing threat = catastrophic)

F1 is the right choice when:
  - Both false positives and false negatives matter equally
  - You need a single number to compare models
```

---

## ROC Curve and AUC

The **ROC curve** (Receiver Operating Characteristic) is a powerful visualization that shows how your model performs across all possible thresholds.

### What Is the ROC Curve?

The ROC curve plots:
- **X-axis**: False Positive Rate (FPR) = FP / (FP + TN) -- "How many healthy people did we wrongly flag?"
- **Y-axis**: True Positive Rate (TPR) = TP / (TP + FN) -- same as Recall -- "How many sick people did we catch?"

```
ROC Curve:
══════════

True Positive Rate (Recall)
    ^
1.0 |         ........───────
    |       .·
    |     .·
    |    ·         ← Your model's curve
    |   ·            (higher and to the left is better)
    |  ·
    | ·
    |·
0.0 |─────────────────────> False Positive Rate
    0.0                   1.0

    ─── Perfect model (hugs the top-left corner)
    ... Good model (curves above the diagonal)
    ─·─ Diagonal = random guessing (50/50 coin flip)
    ___ Below diagonal = worse than random!
```

### What Is AUC?

**AUC** (Area Under the Curve) is the area under the ROC curve. It gives you a single number summarizing the curve:

```
AUC Interpretation:
═══════════════════

AUC = 1.0   → Perfect model (never wrong)
AUC = 0.9   → Excellent
AUC = 0.8   → Good
AUC = 0.7   → Fair
AUC = 0.5   → Random guessing (useless)
AUC < 0.5   → Worse than random (predictions are inverted)
```

### ROC Curve in Python

```python
import numpy as np
from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Simulated model probabilities and actual labels
np.random.seed(42)
n_samples = 200

# Create realistic data: sick patients get higher probabilities
y_actual = np.array([0] * 150 + [1] * 50)  # 150 healthy, 50 sick

# Model outputs probabilities (not perfect)
probs_healthy = np.random.beta(2, 5, 150)    # Healthy: lower probabilities
probs_sick = np.random.beta(5, 2, 50)        # Sick: higher probabilities
y_probs = np.concatenate([probs_healthy, probs_sick])

# Calculate ROC curve
fpr, tpr, thresholds = roc_curve(y_actual, y_probs)
auc = roc_auc_score(y_actual, y_probs)

print(f"AUC Score: {auc:.4f}")
print(f"\nSample threshold analysis:")
print(f"{'Threshold':>10} {'TPR (Recall)':>13} {'FPR':>8}")
print("-" * 35)

# Show metrics at selected thresholds
for t in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
    idx = np.argmin(np.abs(thresholds - t))
    print(f"{t:>10.1f} {tpr[idx]:>12.3f} {fpr[idx]:>8.3f}")

# Plot ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', linewidth=2, label=f'Model (AUC = {auc:.3f})')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--', label='Random (AUC = 0.500)')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate (Recall)')
plt.title('ROC Curve')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('roc_curve.png', dpi=100)
print("\nROC curve saved as 'roc_curve.png'")
```

Expected output:

```
AUC Score: 0.8934

Sample threshold analysis:
 Threshold  TPR (Recall)      FPR
-----------------------------------
       0.2        0.960    0.287
       0.3        0.920    0.180
       0.4        0.860    0.107
       0.5        0.780    0.060
       0.6        0.660    0.027
       0.7        0.500    0.013
       0.8        0.320    0.007

ROC curve saved as 'roc_curve.png'
```

**Line-by-line explanation:**

1. `np.random.beta(2, 5, 150)` - Creates probabilities for healthy patients. The beta(2,5) distribution produces mostly low values (good -- healthy people should get low disease probability).
2. `np.random.beta(5, 2, 50)` - Creates probabilities for sick patients. The beta(5,2) distribution produces mostly high values.
3. `roc_curve(y_actual, y_probs)` - Calculates TPR and FPR at every possible threshold. Returns three arrays: FPR values, TPR values, and the thresholds used.
4. `roc_auc_score(y_actual, y_probs)` - Calculates the AUC (area under the ROC curve).
5. The threshold table shows the tradeoff: lowering the threshold increases TPR (catches more sick people) but also increases FPR (more false alarms).

---

## sklearn's classification_report

The `classification_report` function gives you everything in one clean table:

```python
from sklearn.metrics import classification_report

y_actual = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0])
y_predicted = np.array([0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0])

print("Classification Report:")
print("=" * 55)
print(classification_report(
    y_actual,
    y_predicted,
    target_names=['Healthy', 'Sick']
))
```

Expected output:

```
Classification Report:
=======================================================
              precision    recall  f1-score   support

     Healthy       0.86      0.92      0.89        13
        Sick       0.83      0.71      0.77         7

    accuracy                           0.85        20
   macro avg       0.85      0.82      0.83        20
weighted avg       0.85      0.85      0.85        20
```

**Reading the report:**

- **Precision for Healthy (0.86)**: Of patients predicted healthy, 86% actually were.
- **Recall for Sick (0.71)**: We caught 71% of sick patients.
- **Support**: Number of actual samples in each class (13 healthy, 7 sick).
- **Macro avg**: Simple average of both classes (treats each class equally).
- **Weighted avg**: Average weighted by support (larger classes count more).

---

## Multi-Class Metrics

So far we have focused on binary classification (two classes). But what if you have three or more classes?

### The Challenge

With multiple classes, each class has its own precision and recall. How do you combine them into one number?

```
Multi-Class Example: Animal Classification

                   Predicted
              Cat    Dog    Bird
         ┌────────┬────────┬────────┐
    Cat  │   45   │    3   │    2   │  50 actual cats
Actual   ├────────┼────────┼────────┤
    Dog  │    5   │   40   │    5   │  50 actual dogs
         ├────────┼────────┼────────┤
    Bird │    2   │    3   │   45   │  50 actual birds
         └────────┴────────┴────────┘
```

### Three Averaging Methods

```
Averaging Methods:
══════════════════

MACRO Average: Simple average across classes
  Precision_macro = (P_cat + P_dog + P_bird) / 3
  Treats all classes equally.
  Good when all classes are equally important.

MICRO Average: Calculate globally (total TP / total predictions)
  Precision_micro = total_TP / (total_TP + total_FP)
  Gives more weight to larger classes.
  Equals accuracy in multi-class setting.

WEIGHTED Average: Weighted by class size (support)
  Precision_weighted = (P_cat*50 + P_dog*50 + P_bird*50) / 150
  Accounts for class imbalance.
  Good when some classes have more samples than others.
```

### Multi-Class Example in Python

```python
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

# Three-class classification: cat (0), dog (1), bird (2)
np.random.seed(42)
y_actual = np.array([0]*50 + [1]*50 + [2]*50)  # 50 each

# Simulated predictions (mostly correct with some errors)
y_predicted = y_actual.copy()
# Add some errors
error_indices = np.random.choice(150, size=20, replace=False)
for idx in error_indices:
    wrong_classes = [c for c in [0, 1, 2] if c != y_actual[idx]]
    y_predicted[idx] = np.random.choice(wrong_classes)

# Confusion matrix
cm = confusion_matrix(y_actual, y_predicted)
print("Confusion Matrix:")
print(f"         Predicted")
print(f"         Cat  Dog  Bird")
for i, label in enumerate(['Cat ', 'Dog ', 'Bird']):
    print(f"  {label}  {cm[i]}")

# Classification report with all averaging methods
print("\nClassification Report:")
print(classification_report(
    y_actual,
    y_predicted,
    target_names=['Cat', 'Dog', 'Bird']
))

# Show all three averaging methods
from sklearn.metrics import precision_score, recall_score, f1_score

for avg in ['macro', 'micro', 'weighted']:
    p = precision_score(y_actual, y_predicted, average=avg)
    r = recall_score(y_actual, y_predicted, average=avg)
    f = f1_score(y_actual, y_predicted, average=avg)
    print(f"{avg:>8} averaging:  Precision={p:.3f}  Recall={r:.3f}  F1={f:.3f}")
```

Expected output:

```
Confusion Matrix:
         Predicted
         Cat  Dog  Bird
  Cat   [43  4  3]
  Dog   [3  44  3]
  Bird  [2  3  45]

Classification Report:
              precision    recall  f1-score   support

         Cat       0.90      0.86      0.88        50
         Dog       0.86      0.88      0.87        50
        Bird       0.88      0.90      0.89        50

    accuracy                           0.88       150
   macro avg       0.88      0.88      0.88       150
weighted avg       0.88      0.88      0.88       150

   macro averaging:  Precision=0.880  Recall=0.880  F1=0.880
   micro averaging:  Precision=0.880  Recall=0.880  F1=0.880
weighted averaging:  Precision=0.880  Recall=0.880  F1=0.880
```

In this case, all three averaging methods give the same result because the classes are perfectly balanced (50 samples each). With imbalanced classes, the results would differ.

### When to Use Which Average

| Average | Use When |
|---------|----------|
| Macro | All classes equally important, regardless of size |
| Micro | You care about overall correctness across all predictions |
| Weighted | Classes have different sizes and you want to account for that |

---

## Complete Example: Disease Prediction Model

Let us build and evaluate a complete disease prediction system.

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, roc_curve,
                              precision_score, recall_score, f1_score)
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================
# Step 1: Create synthetic medical data
# ============================================
np.random.seed(42)
n_total = 2000
n_sick = 200   # 10% have the disease (imbalanced!)
n_healthy = n_total - n_sick

# Healthy patients
healthy_data = {
    'age': np.random.normal(45, 15, n_healthy).clip(18, 90),
    'blood_pressure': np.random.normal(120, 10, n_healthy),
    'cholesterol': np.random.normal(200, 30, n_healthy),
    'blood_sugar': np.random.normal(90, 10, n_healthy),
    'heart_rate': np.random.normal(72, 8, n_healthy),
}

# Sick patients (different distributions)
sick_data = {
    'age': np.random.normal(60, 12, n_sick).clip(18, 90),
    'blood_pressure': np.random.normal(145, 15, n_sick),
    'cholesterol': np.random.normal(260, 35, n_sick),
    'blood_sugar': np.random.normal(130, 20, n_sick),
    'heart_rate': np.random.normal(85, 12, n_sick),
}

# Combine
df_healthy = pd.DataFrame(healthy_data)
df_healthy['disease'] = 0

df_sick = pd.DataFrame(sick_data)
df_sick['disease'] = 1

df = pd.concat([df_healthy, df_sick], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print("Medical Dataset")
print("=" * 50)
print(f"Total patients: {len(df)}")
print(f"Healthy: {sum(df['disease'] == 0)} ({sum(df['disease'] == 0)/len(df):.0%})")
print(f"Sick:    {sum(df['disease'] == 1)} ({sum(df['disease'] == 1)/len(df):.0%})")

# ============================================
# Step 2: Prepare data
# ============================================
features = ['age', 'blood_pressure', 'cholesterol', 'blood_sugar', 'heart_rate']
X = df[features].values
y = df['disease'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"\nTraining: {len(X_train)} patients")
print(f"Testing:  {len(X_test)} patients")

# ============================================
# Step 3: Train and evaluate three models
# ============================================
models = {
    'Logistic Regression': LogisticRegression(random_state=42),
    'Decision Tree': DecisionTreeClassifier(max_depth=5, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
}

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

best_auc = 0
best_model_name = ""

for name, model in models.items():
    # Train
    model.fit(X_train_scaled, y_train)

    # Predict
    y_pred = model.predict(X_test_scaled)
    y_probs = model.predict_proba(X_test_scaled)[:, 1]

    # Calculate metrics
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_probs)

    if auc > best_auc:
        best_auc = auc
        best_model_name = name

    print(f"\n--- {name} ---")
    print(f"  Confusion Matrix:")
    print(f"                    Predicted")
    print(f"                 Healthy  Sick")
    print(f"    Actual Healthy  {tn:>4}    {fp:>4}")
    print(f"    Actual Sick     {fn:>4}    {tp:>4}")
    print(f"\n  Precision: {precision:.3f} ({precision:.0%} of positive predictions correct)")
    print(f"  Recall:    {recall:.3f} ({recall:.0%} of sick patients caught)")
    print(f"  F1 Score:  {f1:.3f}")
    print(f"  AUC:       {auc:.3f}")
    print(f"\n  Full Report:")
    print(classification_report(y_test, y_pred, target_names=['Healthy', 'Sick']))

# ============================================
# Step 4: Detailed analysis of best model
# ============================================
print("=" * 70)
print(f"BEST MODEL: {best_model_name} (AUC = {best_auc:.3f})")
print("=" * 70)

best_model = models[best_model_name]
y_pred = best_model.predict(X_test_scaled)
y_probs = best_model.predict_proba(X_test_scaled)[:, 1]

# Show impact of different thresholds
print("\nThreshold Analysis:")
print(f"{'Threshold':>10} {'Precision':>10} {'Recall':>8} {'F1':>6} {'FP':>5} {'FN':>5}")
print("-" * 50)

for threshold in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    y_pred_threshold = (y_probs >= threshold).astype(int)
    if sum(y_pred_threshold) == 0:  # Skip if no positive predictions
        continue
    p = precision_score(y_test, y_pred_threshold, zero_division=0)
    r = recall_score(y_test, y_pred_threshold, zero_division=0)
    f = f1_score(y_test, y_pred_threshold, zero_division=0)
    cm = confusion_matrix(y_test, y_pred_threshold)
    tn, fp, fn, tp = cm.ravel()
    print(f"{threshold:>10.1f} {p:>10.3f} {r:>7.3f} {f:>6.3f} {fp:>5} {fn:>5}")

# ============================================
# Step 5: ROC Curve comparison
# ============================================
plt.figure(figsize=(8, 6))

for name, model in models.items():
    y_probs = model.predict_proba(X_test_scaled)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_probs)
    auc = roc_auc_score(y_test, y_probs)
    plt.plot(fpr, tpr, linewidth=2, label=f'{name} (AUC={auc:.3f})')

plt.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Random (AUC=0.500)')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves - Model Comparison')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('roc_comparison.png', dpi=100)
print("\nROC comparison saved as 'roc_comparison.png'")

# ============================================
# Step 6: Medical recommendation
# ============================================
print("\n" + "=" * 70)
print("MEDICAL SCREENING RECOMMENDATION")
print("=" * 70)
print(f"""
For medical screening, we recommend:

1. Use {best_model_name} (AUC = {best_auc:.3f})

2. Set threshold to 0.3 (lower than default 0.5)
   - This INCREASES recall (catches more sick patients)
   - At the cost of more false alarms (lower precision)
   - In medical screening, missing a disease is worse than
     a false alarm that leads to extra testing.

3. Patients flagged by the model should get additional
   tests to confirm the diagnosis.

4. Retrain the model quarterly with new patient data.
""")
```

Expected output:

```
Medical Dataset
==================================================
Total patients: 2000
Healthy: 1800 (90%)
Sick:    200 (10%)

Training: 1600 patients
Testing:  400 patients

======================================================================
MODEL COMPARISON
======================================================================

--- Logistic Regression ---
  Confusion Matrix:
                    Predicted
                 Healthy  Sick
    Actual Healthy   348      12
    Actual Sick        6      34

  Precision: 0.739 (74% of positive predictions correct)
  Recall:    0.850 (85% of sick patients caught)
  F1 Score:  0.791
  AUC:       0.967

  Full Report:
              precision    recall  f1-score   support

     Healthy       0.98      0.97      0.97       360
        Sick       0.74      0.85      0.79        40

    accuracy                           0.96       400
   macro avg       0.86      0.91      0.88       400
weighted avg       0.96      0.96      0.96       400

--- Decision Tree ---
  Confusion Matrix:
                    Predicted
                 Healthy  Sick
    Actual Healthy   345      15
    Actual Sick        8      32

  Precision: 0.681 (68% of positive predictions correct)
  Recall:    0.800 (80% of sick patients caught)
  F1 Score:  0.736
  AUC:       0.942

  Full Report:
              precision    recall  f1-score   support

     Healthy       0.98      0.96      0.97       360
        Sick       0.68      0.80      0.74        40

    accuracy                           0.94       400
   macro avg       0.83      0.88      0.85       400
weighted avg       0.95      0.94      0.95       400

--- Random Forest ---
  Confusion Matrix:
                    Predicted
                 Healthy  Sick
    Actual Healthy   352       8
    Actual Sick        4      36

  Precision: 0.818 (82% of positive predictions correct)
  Recall:    0.900 (90% of sick patients caught)
  F1 Score:  0.857
  AUC:       0.982

  Full Report:
              precision    recall  f1-score   support

     Healthy       0.99      0.98      0.98       360
        Sick       0.82      0.90      0.86        40

    accuracy                           0.97       400
   macro avg       0.90      0.94      0.92       400
weighted avg       0.97      0.97      0.97       400

======================================================================
BEST MODEL: Random Forest (AUC = 0.982)
======================================================================

Threshold Analysis:
 Threshold  Precision   Recall     F1    FP    FN
--------------------------------------------------
       0.1      0.506    1.000  0.672    39     0
       0.2      0.667    0.950  0.784    19     2
       0.3      0.760    0.950  0.844    12     2
       0.4      0.795    0.925  0.855     9     3
       0.5      0.818    0.900  0.857     8     4
       0.6      0.871    0.675  0.760     4    13
       0.7      0.923    0.600  0.727     2    16
       0.8      1.000    0.450  0.621     0    22
       0.9      1.000    0.250  0.400     0    30

ROC comparison saved as 'roc_comparison.png'

======================================================================
MEDICAL SCREENING RECOMMENDATION
======================================================================

For medical screening, we recommend:

1. Use Random Forest (AUC = 0.982)

2. Set threshold to 0.3 (lower than default 0.5)
   - This INCREASES recall (catches more sick patients)
   - At the cost of more false alarms (lower precision)
   - In medical screening, missing a disease is worse than
     a false alarm that leads to extra testing.

3. Patients flagged by the model should get additional
   tests to confirm the diagnosis.

4. Retrain the model quarterly with new patient data.
```

**Key observations:**

1. **Random Forest** performs best with AUC of 0.982 and the highest F1 score.
2. The **threshold analysis** shows the precision-recall tradeoff clearly. At threshold 0.3, we catch 95% of sick patients but have more false alarms.
3. **Accuracy** for all models is above 94%, which looks great. But the real story is in precision and recall for the sick class.
4. For medical screening, we lower the threshold to prioritize recall over precision.

---

## Common Mistakes

1. **Relying on accuracy for imbalanced data**. If 95% of your data is one class, a model that always predicts that class gets 95% accuracy. Use precision, recall, F1, and AUC instead.

2. **Ignoring the confusion matrix**. Summary metrics hide important details. Always look at the confusion matrix to understand WHERE the model is making mistakes.

3. **Using the default 0.5 threshold for all problems**. The right threshold depends on the cost of false positives vs false negatives. Tune it for your specific use case.

4. **Forgetting to use `predict_proba` for AUC**. The `roc_auc_score` function needs probability scores, not binary predictions. Use `model.predict_proba(X)[:, 1]` to get probabilities.

5. **Comparing AUC across different datasets**. AUC depends on the data distribution. An AUC of 0.9 on easy data might be worse than 0.8 on hard data.

---

## Best Practices

1. **Always start with the confusion matrix**. It gives you the most complete picture of what is happening.

2. **Choose metrics based on business impact**. In medical diagnosis, recall matters most. In spam filtering, precision matters most. In most other cases, F1 is a good default.

3. **Use ROC-AUC for model comparison**. AUC is threshold-independent, making it fair for comparing different models.

4. **Use `classification_report`** for a quick overview. It gives you precision, recall, F1, and support for each class in one call.

5. **For imbalanced data, always use stratified splitting**. Use `stratify=y` in `train_test_split` to preserve class proportions.

6. **Consider the threshold as a tunable parameter**. Do not just accept 0.5 as the threshold. Optimize it for your specific use case.

7. **Report confidence intervals when possible**. A single F1 score can vary depending on the test set. Cross-validation (next chapter!) helps with this.

---

## Quick Summary

Classification models need more than accuracy. The confusion matrix shows exactly what the model gets right and wrong. Precision measures how many positive predictions are correct. Recall measures how many actual positives are caught. F1 balances both. ROC-AUC evaluates performance across all thresholds. For multi-class problems, choose macro, micro, or weighted averaging based on your needs.

---

## Key Points to Remember

1. Accuracy is misleading for imbalanced datasets.
2. The confusion matrix has four outcomes: TP, TN, FP, FN.
3. Precision = TP / (TP + FP) -- "How many positive predictions are correct?"
4. Recall = TP / (TP + FN) -- "How many actual positives did we catch?"
5. F1 Score is the harmonic mean of precision and recall.
6. There is always a tradeoff between precision and recall.
7. ROC curve plots TPR vs FPR across all thresholds.
8. AUC (Area Under the ROC Curve) summarizes model performance in one number.
9. For medical/security applications, prioritize recall (catching all positives).
10. For spam/recommendation systems, prioritize precision (avoiding false alarms).

---

## Practice Questions

### Question 1
A spam filter has: TP=90, FP=10, FN=30, TN=870. Calculate accuracy, precision, recall, and F1 score.

**Answer:**
- Accuracy = (90 + 870) / (90 + 10 + 30 + 870) = 960/1000 = 0.96 (96%)
- Precision = 90 / (90 + 10) = 90/100 = 0.90 (90%)
- Recall = 90 / (90 + 30) = 90/120 = 0.75 (75%)
- F1 = 2 * (0.90 * 0.75) / (0.90 + 0.75) = 1.35/1.65 = 0.818

The filter is precise (90% of flagged emails are actually spam) but misses 25% of spam (recall is 75%).

### Question 2
Your cancer screening model has 99% accuracy on a dataset where 1% of patients have cancer. Is this model useful?

**Answer:** Probably not. If the model simply predicts "no cancer" for every patient, it would achieve 99% accuracy because 99% of patients are actually healthy. The model might have 0% recall -- it catches zero cancer patients. To evaluate this model properly, you need to check precision and recall for the cancer class. A useful model should have high recall (catch most cancer cases), even if it means lower precision (some false alarms that get cleared by follow-up testing).

### Question 3
Model A has AUC = 0.85. Model B has AUC = 0.92. Can we always say Model B is better?

**Answer:** Model B has a better AUC, which means overall it does a better job separating positive from negative cases across all thresholds. However, there are situations where Model A might still be preferred: (1) If you only care about performance at a specific threshold, Model A might be better at that particular operating point. (2) The ROC curves might cross -- Model A might be better at low FPR while Model B is better at high FPR. (3) If Model A is much faster or simpler to deploy, the AUC difference might not justify the complexity. But in general, higher AUC indicates a better model.

### Question 4
What is the difference between macro and weighted averaging for multi-class F1?

**Answer:** Macro averaging calculates F1 for each class separately, then takes the unweighted mean. Every class counts equally regardless of its size. Weighted averaging calculates F1 for each class, then averages weighted by the number of samples in each class (support). Larger classes count more. Use macro when all classes are equally important. Use weighted when you want the metric to reflect the overall performance accounting for class sizes. For example, if you have classes with 1000, 500, and 50 samples, macro averaging treats all three equally, while weighted averaging gives the class with 1000 samples the most influence.

---

## Exercises

### Exercise 1: Build a Spam Classifier

Create a synthetic email dataset with features like word count, number of links, and number of exclamation marks. Make 5% of emails spam. Train a Logistic Regression model. Evaluate using the confusion matrix, precision, recall, F1, and ROC-AUC. Try three different thresholds (0.3, 0.5, 0.7) and compare results.

**Hint:** Spam emails typically have more links and exclamation marks. Use `np.random.normal` with different parameters for spam vs non-spam.

### Exercise 2: Multi-Class Evaluation

Create a dataset for classifying news articles into 4 categories: sports, politics, technology, entertainment. Make the classes imbalanced (e.g., 40% sports, 30% politics, 20% technology, 10% entertainment). Train a Random Forest classifier. Report all three averaging methods (macro, micro, weighted) and explain which is most appropriate for this problem.

### Exercise 3: Threshold Optimization

Using the disease prediction example, find the optimal threshold that maximizes the F1 score. Then find the threshold that ensures at least 95% recall. Compare the precision at both thresholds and explain which you would recommend for a hospital screening program.

**Hint:** Loop through thresholds from 0.01 to 0.99 in steps of 0.01. For each threshold, calculate F1 and recall.

---

## What Is Next?

In this chapter, you learned how to properly evaluate classification models using metrics that go far beyond accuracy. You now understand precision, recall, F1, ROC curves, and AUC.

But there is one more critical evaluation technique we have not covered: **Cross-Validation**. In the next chapter, you will learn how to get more reliable evaluation scores by testing your model multiple times on different data splits. This technique is essential for every machine learning project.
