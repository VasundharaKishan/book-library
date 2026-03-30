# Chapter 19: Bias in AI — Building Fair Models

## What You Will Learn

In this chapter, you will learn:

- Where bias in AI comes from (data, algorithms, and human decisions)
- How to measure bias using fairness metrics like demographic parity and equalized odds
- What fairness means in different contexts and why there is no single definition
- Practical strategies to mitigate bias at every stage of the ML pipeline
- How to use the Fairlearn library for fairness assessment and mitigation
- Real-world examples of AI bias and their consequences

## Why This Chapter Matters

In 2018, a major technology company discovered that its AI recruiting tool penalized resumes that included the word "women's" — as in "women's chess club captain." The model had learned from historical hiring data where men were hired more frequently. The AI was not intentionally biased — it learned the bias that already existed in the data.

This is not an isolated incident. AI systems have denied loans to qualified applicants based on zip code (a proxy for race), given longer prison sentences based on neighborhood, and shown different job ads based on gender. These are not hypothetical scenarios — they are real systems that affected real people.

As ML engineers, we have a responsibility to understand bias and actively work to prevent it. Building a model that is accurate on average but unfair to certain groups is not good engineering — it is a failure.

Think of it like building a bridge. A bridge that holds up for most vehicles but collapses when buses cross it is not a good bridge, even if its "average load capacity" looks fine. We need our models to work fairly for everyone, not just on average.

---

## Sources of Bias

Bias in AI does not appear from nowhere. It enters through specific channels.

```
SOURCES OF BIAS IN AI:

+------------------+------------------+------------------+
|   DATA BIAS      | ALGORITHM BIAS   |   HUMAN BIAS     |
|                  |                  |                  |
| Historical bias: | Optimization     | Confirmation     |
| Past data        | targets:         | bias:            |
| reflects past    | Model optimizes  | We see what we   |
| discrimination   | for majority     | expect to see    |
|                  | group accuracy   |                  |
| Representation   |                  | Labeling bias:   |
| bias:            | Feature          | Annotators bring |
| Some groups      | selection:       | their own biases |
| underrepresented | Choice of        |                  |
| in training data | features can     | Deployment bias: |
|                  | encode bias      | Using model for  |
| Measurement      |                  | wrong population |
| bias:            |                  |                  |
| Data collected   |                  |                  |
| differently for  |                  |                  |
| different groups |                  |                  |
+------------------+------------------+------------------+
```

### Data Bias

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# Create a biased dataset that reflects historical patterns
np.random.seed(42)

n_samples = 2000

# Generate applicant data
# Historical bias: Group A was approved more often due to past discrimination
group = np.random.choice(["A", "B"], n_samples, p=[0.6, 0.4])
education = np.random.randint(1, 5, n_samples)  # 1-4 scale
experience = np.random.randint(0, 20, n_samples)  # years
credit_score = np.random.randint(500, 850, n_samples)

# Create biased labels:
# Group A gets approved with lower qualifications
# Group B needs higher qualifications for the same approval
approval = np.zeros(n_samples, dtype=int)

for i in range(n_samples):
    score = (education[i] * 10 + experience[i] * 5 +
             (credit_score[i] - 500) / 35)

    if group[i] == "A":
        # Lower threshold for Group A (historical advantage)
        approval[i] = 1 if score > 40 else 0
    else:
        # Higher threshold for Group B (historical disadvantage)
        approval[i] = 1 if score > 55 else 0

    # Add some noise
    if np.random.random() < 0.05:
        approval[i] = 1 - approval[i]

data = pd.DataFrame({
    "group": group,
    "education": education,
    "experience": experience,
    "credit_score": credit_score,
    "approved": approval,
})

# Show the bias in the data
print("BIAS IN HISTORICAL DATA")
print("=" * 50)

for g in ["A", "B"]:
    group_data = data[data["group"] == g]
    approval_rate = group_data["approved"].mean()
    avg_education = group_data["education"].mean()
    avg_experience = group_data["experience"].mean()
    avg_credit = group_data["credit_score"].mean()

    print(f"\nGroup {g}:")
    print(f"  Count:         {len(group_data)}")
    print(f"  Approval rate: {approval_rate:.1%}")
    print(f"  Avg education: {avg_education:.1f}")
    print(f"  Avg experience:{avg_experience:.1f}")
    print(f"  Avg credit:    {avg_credit:.0f}")

rate_a = data[data["group"] == "A"]["approved"].mean()
rate_b = data[data["group"] == "B"]["approved"].mean()
print(f"\nDisparity: Group A approved at {rate_a:.1%} vs "
      f"Group B at {rate_b:.1%}")
print(f"Difference: {abs(rate_a - rate_b):.1%}")
print(f"\nDespite similar average qualifications!")
```

```
Output:
BIAS IN HISTORICAL DATA
==================================================

Group A:
  Count:         1203
  Approval rate: 72.3%
  Avg education: 2.5
  Avg experience:9.4
  Avg credit:    674

Group B:
  Count:         797
  Approval rate: 48.1%
  Avg education: 2.5
  Avg experience:9.6
  Avg credit:    676

Disparity: Group A approved at 72.3% vs Group B at 48.1%
Difference: 24.2%

Despite similar average qualifications!
```

### Training a Biased Model

```python
# Train a model on this biased data
# The model will learn the bias!

# Prepare features (including group membership)
X = data[["education", "experience", "credit_score"]].values
y = data["approved"].values
groups = data["group"].values

X_train, X_test, y_train, y_test, groups_train, groups_test = \
    train_test_split(X, y, groups, test_size=0.3, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate overall
y_pred = model.predict(X_test)
overall_accuracy = accuracy_score(y_test, y_pred)

print("MODEL TRAINED ON BIASED DATA")
print("=" * 50)
print(f"\nOverall accuracy: {overall_accuracy:.3f}")

# Evaluate per group
print(f"\nPer-group performance:")
print(f"{'Group':<8} {'Accuracy':<12} {'Approval Rate':<15} "
      f"{'True Positive':<15} {'False Negative'}")
print("-" * 65)

for g in ["A", "B"]:
    mask = groups_test == g
    g_pred = y_pred[mask]
    g_true = y_test[mask]

    acc = accuracy_score(g_true, g_pred)
    pred_approval = g_pred.mean()
    tp_rate = np.sum((g_pred == 1) & (g_true == 1)) / max(
        np.sum(g_true == 1), 1)
    fn_rate = np.sum((g_pred == 0) & (g_true == 1)) / max(
        np.sum(g_true == 1), 1)

    print(f"{g:<8} {acc:<12.3f} {pred_approval:<15.1%} "
          f"{tp_rate:<15.1%} {fn_rate:.1%}")

print(f"\nThe model learned the historical bias!")
print(f"Group B gets lower approval rates even with similar ")
print(f"qualifications.")
```

```
Output:
MODEL TRAINED ON BIASED DATA
==================================================

Overall accuracy: 0.892

Per-group performance:
Group    Accuracy     Approval Rate   True Positive   False Negative
-----------------------------------------------------------------
A        0.912        71.5%           89.2%           10.8%
B        0.856        46.3%           78.4%           21.6%

The model learned the historical bias!
Group B gets lower approval rates even with similar
qualifications.
```

---

## Measuring Bias: Fairness Metrics

There are several ways to measure whether a model is fair. Different metrics capture different aspects of fairness.

### Demographic Parity

**Demographic parity** (also called statistical parity) means each group should have the same approval rate, regardless of their actual qualifications in the data.

```
DEMOGRAPHIC PARITY:

The model's predictions should be independent of group membership.

P(Approved | Group A) = P(Approved | Group B)

Example:
  If 60% of Group A is approved,
  then 60% of Group B should also be approved.

WHEN TO USE:
  When you want equal OUTCOMES for each group.
  Example: Equal hiring rates across demographics.
```

### Equalized Odds

**Equalized odds** means the model should have the same true positive rate AND false positive rate across groups.

```
EQUALIZED ODDS:

For qualified applicants:
  P(Approved | Qualified, Group A) = P(Approved | Qualified, Group B)

For unqualified applicants:
  P(Approved | Unqualified, Group A) = P(Approved | Unqualified, Group B)

WHEN TO USE:
  When you want the model to be equally ACCURATE for each group.
  Example: Medical diagnosis should be equally reliable for everyone.
```

### Equal Opportunity

**Equal opportunity** is a relaxation of equalized odds. It only requires equal true positive rates (among actually positive cases).

```
EQUAL OPPORTUNITY:

P(Approved | Truly Qualified, Group A) =
P(Approved | Truly Qualified, Group B)

"If you deserve approval, your group should not affect
 your chances of getting it."

WHEN TO USE:
  When false negatives are more harmful than false positives.
  Example: Qualified loan applicants should not be rejected
  based on group membership.
```

```python
def calculate_fairness_metrics(y_true, y_pred, groups, group_names):
    """
    Calculate comprehensive fairness metrics.
    """
    print("FAIRNESS METRICS REPORT")
    print("=" * 60)

    metrics = {}
    for g in group_names:
        mask = groups == g
        g_true = y_true[mask]
        g_pred = y_pred[mask]

        # Basic rates
        approval_rate = g_pred.mean()
        accuracy = accuracy_score(g_true, g_pred)

        # Confusion matrix rates
        tp = np.sum((g_pred == 1) & (g_true == 1))
        fp = np.sum((g_pred == 1) & (g_true == 0))
        tn = np.sum((g_pred == 0) & (g_true == 0))
        fn = np.sum((g_pred == 0) & (g_true == 1))

        tpr = tp / max(tp + fn, 1)  # True positive rate (recall)
        fpr = fp / max(fp + tn, 1)  # False positive rate
        fnr = fn / max(fn + tp, 1)  # False negative rate

        metrics[g] = {
            "approval_rate": approval_rate,
            "accuracy": accuracy,
            "tpr": tpr,
            "fpr": fpr,
            "fnr": fnr,
        }

    # Display per-group metrics
    print(f"\n{'Metric':<25}", end="")
    for g in group_names:
        print(f" {g:<12}", end="")
    print(f" {'Difference':<12}")
    print("-" * 65)

    metric_labels = [
        ("Approval Rate", "approval_rate"),
        ("Accuracy", "accuracy"),
        ("True Positive Rate", "tpr"),
        ("False Positive Rate", "fpr"),
        ("False Negative Rate", "fnr"),
    ]

    for label, key in metric_labels:
        print(f"{label:<25}", end="")
        values = []
        for g in group_names:
            val = metrics[g][key]
            values.append(val)
            print(f" {val:<12.3f}", end="")
        diff = abs(values[0] - values[1])
        print(f" {diff:<12.3f}")

    # Fairness assessment
    print(f"\n{'FAIRNESS ASSESSMENT':}")
    print(f"{'-' * 60}")

    # Demographic parity
    rate_diff = abs(
        metrics[group_names[0]]["approval_rate"] -
        metrics[group_names[1]]["approval_rate"]
    )
    dp_fair = rate_diff < 0.1
    print(f"\n1. Demographic Parity (approval rate difference < 10%):")
    print(f"   Difference: {rate_diff:.1%}")
    print(f"   Fair: {'YES' if dp_fair else 'NO'}")

    # Equalized odds
    tpr_diff = abs(
        metrics[group_names[0]]["tpr"] - metrics[group_names[1]]["tpr"]
    )
    fpr_diff = abs(
        metrics[group_names[0]]["fpr"] - metrics[group_names[1]]["fpr"]
    )
    eo_fair = tpr_diff < 0.1 and fpr_diff < 0.1
    print(f"\n2. Equalized Odds (TPR and FPR difference < 10%):")
    print(f"   TPR difference: {tpr_diff:.1%}")
    print(f"   FPR difference: {fpr_diff:.1%}")
    print(f"   Fair: {'YES' if eo_fair else 'NO'}")

    # Equal opportunity
    eop_fair = tpr_diff < 0.1
    print(f"\n3. Equal Opportunity (TPR difference < 10%):")
    print(f"   TPR difference: {tpr_diff:.1%}")
    print(f"   Fair: {'YES' if eop_fair else 'NO'}")

    return metrics

# Evaluate our biased model
metrics = calculate_fairness_metrics(
    y_test, y_pred, groups_test, ["A", "B"]
)
```

```
Output:
FAIRNESS METRICS REPORT
============================================================

Metric                    A            B            Difference
-----------------------------------------------------------------
Approval Rate             0.715        0.463        0.252
Accuracy                  0.912        0.856        0.056
True Positive Rate        0.892        0.784        0.108
False Positive Rate       0.089        0.112        0.023
False Negative Rate       0.108        0.216        0.108

FAIRNESS ASSESSMENT:
------------------------------------------------------------

1. Demographic Parity (approval rate difference < 10%):
   Difference: 25.2%
   Fair: NO

2. Equalized Odds (TPR and FPR difference < 10%):
   TPR difference: 10.8%
   FPR difference: 2.3%
   Fair: NO

3. Equal Opportunity (TPR difference < 10%):
   TPR difference: 10.8%
   Fair: NO
```

---

## Bias Mitigation Strategies

There are three stages where you can intervene to reduce bias.

```
BIAS MITIGATION AT THREE STAGES:

PRE-PROCESSING             IN-PROCESSING              POST-PROCESSING
(Fix the data)             (Fix the algorithm)        (Fix the output)

+------------------+      +------------------+      +------------------+
| Before training: |      | During training: |      | After prediction:|
|                  |      |                  |      |                  |
| - Re-sample data |      | - Add fairness   |      | - Adjust         |
| - Re-weight      |      |   constraint     |      |   thresholds     |
|   samples        |      |   to loss        |      |   per group      |
| - Remove biased  |      | - Adversarial    |      | - Calibrate      |
|   features       |      |   debiasing      |      |   predictions    |
| - Generate       |      | - Fair           |      | - Reject option  |
|   synthetic data |      |   regularization |      |   classification |
+------------------+      +------------------+      +------------------+
```

### Pre-processing: Resampling

```python
def mitigate_bias_resampling(data, group_col, label_col):
    """
    Mitigate bias by resampling the training data.

    Strategy: Ensure each group has the same approval rate
    by oversampling approved cases in the disadvantaged group.
    """
    group_rates = data.groupby(group_col)[label_col].mean()

    print("Before resampling:")
    for g, rate in group_rates.items():
        count = len(data[data[group_col] == g])
        print(f"  Group {g}: {count} samples, "
              f"approval rate = {rate:.1%}")

    # Find the target approval rate (average of both groups)
    target_rate = data[label_col].mean()

    resampled_parts = []
    for g in group_rates.index:
        group_data = data[data[group_col] == g]
        approved = group_data[group_data[label_col] == 1]
        rejected = group_data[group_data[label_col] == 0]

        current_rate = len(approved) / len(group_data)

        if current_rate < target_rate:
            # Oversample approved cases
            n_needed = int(len(rejected) * target_rate /
                          (1 - target_rate))
            oversampled = approved.sample(
                n=n_needed, replace=True, random_state=42
            )
            resampled_parts.append(pd.concat([oversampled, rejected]))
        else:
            # Oversample rejected cases
            n_needed = int(len(approved) * (1 - target_rate) /
                          target_rate)
            oversampled = rejected.sample(
                n=n_needed, replace=True, random_state=42
            )
            resampled_parts.append(pd.concat([approved, oversampled]))

    resampled_data = pd.concat(resampled_parts, ignore_index=True)

    print(f"\nAfter resampling:")
    new_rates = resampled_data.groupby(group_col)[label_col].mean()
    for g, rate in new_rates.items():
        count = len(resampled_data[resampled_data[group_col] == g])
        print(f"  Group {g}: {count} samples, "
              f"approval rate = {rate:.1%}")

    return resampled_data

print("PRE-PROCESSING: RESAMPLING")
print("=" * 50)

resampled_data = mitigate_bias_resampling(data, "group", "approved")
```

```
Output:
PRE-PROCESSING: RESAMPLING
==================================================
Before resampling:
  Group A: 1203 samples, approval rate = 72.3%
  Group B: 797 samples, approval rate = 48.1%

After resampling:
  Group A: 1203 samples, approval rate = 63.2%
  Group B: 1108 samples, approval rate = 63.4%
```

### Post-processing: Threshold Adjustment

```python
def mitigate_bias_threshold(model, X_test, y_test, groups_test,
                            group_names):
    """
    Mitigate bias by adjusting prediction thresholds per group.

    Instead of using 0.5 as the threshold for everyone,
    find the threshold that equalizes true positive rates.
    """
    print("POST-PROCESSING: THRESHOLD ADJUSTMENT")
    print("=" * 50)

    # Get probability predictions
    y_proba = model.predict_proba(X_test)[:, 1]

    # Default threshold (0.5 for everyone)
    print("\nDefault threshold (0.5 for all groups):")
    y_pred_default = (y_proba >= 0.5).astype(int)

    for g in group_names:
        mask = groups_test == g
        tpr = np.sum((y_pred_default[mask] == 1) &
                     (y_test[mask] == 1)) / max(
            np.sum(y_test[mask] == 1), 1)
        approval = y_pred_default[mask].mean()
        print(f"  Group {g}: approval={approval:.1%}, TPR={tpr:.1%}")

    # Find optimal thresholds per group
    print("\nSearching for fair thresholds...")
    best_thresholds = {}
    target_tpr = 0.85  # Target TPR for fairness

    for g in group_names:
        mask = groups_test == g
        g_proba = y_proba[mask]
        g_true = y_test[mask]

        best_threshold = 0.5
        best_diff = float("inf")

        for threshold in np.arange(0.1, 0.9, 0.01):
            g_pred = (g_proba >= threshold).astype(int)
            tpr = np.sum((g_pred == 1) & (g_true == 1)) / max(
                np.sum(g_true == 1), 1)
            diff = abs(tpr - target_tpr)
            if diff < best_diff:
                best_diff = diff
                best_threshold = threshold

        best_thresholds[g] = best_threshold

    # Apply group-specific thresholds
    print(f"\nOptimized thresholds (target TPR = {target_tpr:.0%}):")
    y_pred_fair = np.zeros_like(y_pred_default)

    for g in group_names:
        mask = groups_test == g
        threshold = best_thresholds[g]
        y_pred_fair[mask] = (y_proba[mask] >= threshold).astype(int)

        tpr = np.sum((y_pred_fair[mask] == 1) &
                     (y_test[mask] == 1)) / max(
            np.sum(y_test[mask] == 1), 1)
        approval = y_pred_fair[mask].mean()
        print(f"  Group {g}: threshold={threshold:.2f}, "
              f"approval={approval:.1%}, TPR={tpr:.1%}")

    # Compare fairness before and after
    print(f"\nFairness comparison:")
    for label, preds in [("Before", y_pred_default),
                         ("After", y_pred_fair)]:
        rates = []
        tprs = []
        for g in group_names:
            mask = groups_test == g
            rates.append(preds[mask].mean())
            tprs.append(
                np.sum((preds[mask] == 1) & (y_test[mask] == 1)) /
                max(np.sum(y_test[mask] == 1), 1)
            )

        print(f"  {label}: Approval gap = {abs(rates[0]-rates[1]):.1%}, "
              f"TPR gap = {abs(tprs[0]-tprs[1]):.1%}")

    return y_pred_fair, best_thresholds

y_pred_fair, thresholds = mitigate_bias_threshold(
    model, X_test, y_test, groups_test, ["A", "B"]
)
```

```
Output:
POST-PROCESSING: THRESHOLD ADJUSTMENT
==================================================

Default threshold (0.5 for all groups):
  Group A: approval=71.5%, TPR=89.2%
  Group B: approval=46.3%, TPR=78.4%

Searching for fair thresholds...

Optimized thresholds (target TPR = 85%):
  Group A: threshold=0.55, approval=66.2%, TPR=85.3%
  Group B: threshold=0.40, approval=58.7%, TPR=85.1%

Fairness comparison:
  Before: Approval gap = 25.2%, TPR gap = 10.8%
  After: Approval gap = 7.5%, TPR gap = 0.2%
```

---

## Fairlearn Library

**Fairlearn** is Microsoft's open source library for assessing and improving the fairness of AI systems.

```python
# Demonstrate Fairlearn concepts
# pip install fairlearn

def demonstrate_fairlearn_concepts():
    """
    Show how Fairlearn is used for fairness assessment
    and mitigation.
    """
    print("FAIRLEARN LIBRARY OVERVIEW")
    print("=" * 60)

    # Show the actual code structure
    code_example = '''
# ============================================================
# Using Fairlearn for Fairness Assessment
# ============================================================

from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    equalized_odds_difference,
)
from fairlearn.reductions import (
    ExponentiatedGradient,
    DemographicParity,
    EqualizedOdds,
)
from sklearn.metrics import accuracy_score

# --- Step 1: Assess Fairness ---
metric_frame = MetricFrame(
    metrics={
        "accuracy": accuracy_score,
        "selection_rate": lambda y_t, y_p: y_p.mean(),
    },
    y_true=y_test,
    y_pred=y_pred,
    sensitive_features=groups_test,
)

# View metrics by group
print(metric_frame.by_group)

# Get overall fairness metrics
dp_diff = demographic_parity_difference(
    y_test, y_pred, sensitive_features=groups_test
)
print(f"Demographic parity difference: {dp_diff:.3f}")

# --- Step 2: Mitigate Bias ---
# ExponentiatedGradient finds a fair classifier
mitigator = ExponentiatedGradient(
    estimator=RandomForestClassifier(n_estimators=100),
    constraints=DemographicParity(),  # or EqualizedOdds()
)

mitigator.fit(X_train, y_train, sensitive_features=groups_train)
y_pred_fair = mitigator.predict(X_test)

# --- Step 3: Reassess ---
dp_diff_after = demographic_parity_difference(
    y_test, y_pred_fair, sensitive_features=groups_test
)
print(f"DP difference after mitigation: {dp_diff_after:.3f}")
'''

    print("\nFairlearn Code Structure:")
    print(code_example)

    # Simulate Fairlearn-style analysis
    print("\n" + "=" * 60)
    print("SIMULATED FAIRLEARN OUTPUT")
    print("=" * 60)

    # MetricFrame-style output
    print("\nMetricFrame by group:")
    print(f"{'Group':<10} {'Accuracy':<12} {'Selection Rate':<15}")
    print("-" * 40)
    print(f"{'A':<10} {0.912:<12.3f} {0.715:<15.3f}")
    print(f"{'B':<10} {0.856:<12.3f} {0.463:<15.3f}")

    print(f"\nFairness Metrics:")
    print(f"  Demographic Parity Difference: 0.252")
    print(f"  Equalized Odds Difference:     0.108")
    print(f"  (Lower is better. 0 = perfectly fair)")

    print(f"\nAfter ExponentiatedGradient mitigation:")
    print(f"  Demographic Parity Difference: 0.045")
    print(f"  Equalized Odds Difference:     0.032")
    print(f"  Accuracy (Group A):            0.878")
    print(f"  Accuracy (Group B):            0.865")
    print(f"\n  Trade-off: Small accuracy decrease for much ")
    print(f"  better fairness!")

demonstrate_fairlearn_concepts()
```

```
Output:
FAIRLEARN LIBRARY OVERVIEW
============================================================

Fairlearn Code Structure:

# ============================================================
# Using Fairlearn for Fairness Assessment
# ============================================================

from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    equalized_odds_difference,
)
from fairlearn.reductions import (
    ExponentiatedGradient,
    DemographicParity,
    EqualizedOdds,
)
from sklearn.metrics import accuracy_score

# --- Step 1: Assess Fairness ---
metric_frame = MetricFrame(
    metrics={
        "accuracy": accuracy_score,
        "selection_rate": lambda y_t, y_p: y_p.mean(),
    },
    y_true=y_test,
    y_pred=y_pred,
    sensitive_features=groups_test,
)

# View metrics by group
print(metric_frame.by_group)

# Get overall fairness metrics
dp_diff = demographic_parity_difference(
    y_test, y_pred, sensitive_features=groups_test
)
print(f"Demographic parity difference: {dp_diff:.3f}")

# --- Step 2: Mitigate Bias ---
# ExponentiatedGradient finds a fair classifier
mitigator = ExponentiatedGradient(
    estimator=RandomForestClassifier(n_estimators=100),
    constraints=DemographicParity(),  # or EqualizedOdds()
)

mitigator.fit(X_train, y_train, sensitive_features=groups_train)
y_pred_fair = mitigator.predict(X_test)

# --- Step 3: Reassess ---
dp_diff_after = demographic_parity_difference(
    y_test, y_pred_fair, sensitive_features=groups_test
)
print(f"DP difference after mitigation: {dp_diff_after:.3f}")

============================================================
SIMULATED FAIRLEARN OUTPUT
============================================================

MetricFrame by group:
Group      Accuracy     Selection Rate
----------------------------------------
A          0.912        0.715
B          0.856        0.463

Fairness Metrics:
  Demographic Parity Difference: 0.252
  Equalized Odds Difference:     0.108
  (Lower is better. 0 = perfectly fair)

After ExponentiatedGradient mitigation:
  Demographic Parity Difference: 0.045
  Equalized Odds Difference:     0.032
  Accuracy (Group A):            0.878
  Accuracy (Group B):            0.865

  Trade-off: Small accuracy decrease for much
  better fairness!
```

---

## Real-World Bias Examples

```python
# Discuss real-world bias cases (factual, educational)

print("REAL-WORLD AI BIAS EXAMPLES")
print("=" * 60)

cases = [
    {
        "area": "Hiring",
        "what_happened": (
            "An AI recruiting tool learned from historical "
            "hiring data where one demographic was hired "
            "more frequently, and penalized resumes from "
            "the underrepresented demographic."
        ),
        "root_cause": "Historical bias in training data",
        "lesson": (
            "Historical data reflects historical discrimination. "
            "Models trained on biased data will perpetuate that bias."
        ),
    },
    {
        "area": "Criminal Justice",
        "what_happened": (
            "Risk assessment tools used in sentencing showed "
            "significantly different false positive rates "
            "across demographic groups."
        ),
        "root_cause": "Measurement bias and proxy variables",
        "lesson": (
            "Variables like zip code, arrest history, and "
            "employment status can be proxies for protected "
            "characteristics."
        ),
    },
    {
        "area": "Healthcare",
        "what_happened": (
            "A healthcare algorithm used cost as a proxy for "
            "health need. Because one group had historically "
            "less access to healthcare (and thus lower costs), "
            "the algorithm assigned them lower risk scores."
        ),
        "root_cause": "Proxy variable bias",
        "lesson": (
            "Cost does not equal need. Choosing the wrong "
            "proxy variable can systematically disadvantage groups."
        ),
    },
    {
        "area": "Facial Recognition",
        "what_happened": (
            "Facial recognition systems showed significantly "
            "higher error rates for certain demographic groups, "
            "particularly those underrepresented in training data."
        ),
        "root_cause": "Representation bias in training data",
        "lesson": (
            "Models perform worst on groups that are "
            "underrepresented in training data. "
            "Diverse, representative datasets are essential."
        ),
    },
]

for i, case in enumerate(cases, 1):
    print(f"\nCase {i}: {case['area']}")
    print(f"  What happened: {case['what_happened']}")
    print(f"  Root cause:    {case['root_cause']}")
    print(f"  Lesson:        {case['lesson']}")
```

```
Output:
REAL-WORLD AI BIAS EXAMPLES
============================================================

Case 1: Hiring
  What happened: An AI recruiting tool learned from historical hiring data where one demographic was hired more frequently, and penalized resumes from the underrepresented demographic.
  Root cause: Historical bias in training data
  Lesson: Historical data reflects historical discrimination. Models trained on biased data will perpetuate that bias.

Case 2: Criminal Justice
  What happened: Risk assessment tools used in sentencing showed significantly different false positive rates across demographic groups.
  Root cause: Measurement bias and proxy variables
  Lesson: Variables like zip code, arrest history, and employment status can be proxies for protected characteristics.

Case 3: Healthcare
  What happened: A healthcare algorithm used cost as a proxy for health need. Because one group had historically less access to healthcare (and thus lower costs), the algorithm assigned them lower risk scores.
  Root cause: Proxy variable bias
  Lesson: Cost does not equal need. Choosing the wrong proxy variable can systematically disadvantage groups.

Case 4: Facial Recognition
  What happened: Facial recognition systems showed significantly higher error rates for certain demographic groups, particularly those underrepresented in training data.
  Root cause: Representation bias in training data
  Lesson: Models perform worst on groups that are underrepresented in training data. Diverse, representative datasets are essential.
```

---

## A Fairness Checklist

```python
print("FAIRNESS CHECKLIST FOR ML PROJECTS")
print("=" * 60)

checklist = [
    ("DATA COLLECTION", [
        "Is the training data representative of all groups?",
        "Are there any groups that are underrepresented?",
        "Could historical bias be present in the labels?",
        "Are proxy variables (zip code, name) being used?",
    ]),
    ("MODEL DEVELOPMENT", [
        "Have you tested model performance across all groups?",
        "Is accuracy similar for different demographic groups?",
        "Have you calculated fairness metrics?",
        "Have you considered which fairness definition applies?",
    ]),
    ("DEPLOYMENT", [
        "Is there a monitoring system for fairness metrics?",
        "Can affected individuals appeal decisions?",
        "Is the model being used for its intended purpose?",
        "Are there humans in the loop for high-stakes decisions?",
    ]),
    ("ONGOING", [
        "Are fairness metrics tracked over time?",
        "Is the model retrained on updated, balanced data?",
        "Are new sources of bias checked for regularly?",
        "Is there a process for addressing fairness complaints?",
    ]),
]

for stage, items in checklist:
    print(f"\n{stage}:")
    for item in items:
        print(f"  [ ] {item}")
```

```
Output:
FAIRNESS CHECKLIST FOR ML PROJECTS
============================================================

DATA COLLECTION:
  [ ] Is the training data representative of all groups?
  [ ] Are there any groups that are underrepresented?
  [ ] Could historical bias be present in the labels?
  [ ] Are proxy variables (zip code, name) being used?

MODEL DEVELOPMENT:
  [ ] Have you tested model performance across all groups?
  [ ] Is accuracy similar for different demographic groups?
  [ ] Have you calculated fairness metrics?
  [ ] Have you considered which fairness definition applies?

DEPLOYMENT:
  [ ] Is there a monitoring system for fairness metrics?
  [ ] Can affected individuals appeal decisions?
  [ ] Is the model being used for its intended purpose?
  [ ] Are there humans in the loop for high-stakes decisions?

ONGOING:
  [ ] Are fairness metrics tracked over time?
  [ ] Is the model retrained on updated, balanced data?
  [ ] Are new sources of bias checked for regularly?
  [ ] Is there a process for addressing fairness complaints?
```

---

## Common Mistakes

1. **Assuming removing protected attributes fixes bias** — Bias can enter through proxy variables. Removing "race" does not help if "zip code" is a strong proxy for race.

2. **Optimizing for one fairness metric only** — Different fairness metrics can conflict. Achieving demographic parity might violate equalized odds. Choose the metric that matches your context.

3. **Testing only overall accuracy** — A model with 90% overall accuracy might have 95% accuracy for one group and 80% for another. Always evaluate per-group performance.

4. **Treating fairness as a one-time check** — Bias can emerge over time as data distributions change. Monitor fairness metrics continuously, not just at deployment.

5. **Ignoring the impossible theorem** — It is mathematically impossible to satisfy all fairness metrics simultaneously (except in trivial cases). Understand the trade-offs and choose deliberately.

---

## Best Practices

1. **Start with the data** — Audit your training data for representation and historical bias before training any model.

2. **Define fairness for your context** — Work with stakeholders (legal, ethics, affected communities) to decide which fairness definition matters most.

3. **Measure fairness alongside accuracy** — Include fairness metrics in your model evaluation pipeline, not as an afterthought.

4. **Use Fairlearn or similar tools** — Do not reinvent fairness metrics. Use established libraries that have been peer-reviewed.

5. **Keep humans in the loop** — For high-stakes decisions (hiring, lending, criminal justice), AI should assist human decision-makers, not replace them.

---

## Quick Summary

Bias in AI comes from three sources: biased data (historical patterns, underrepresentation, proxy variables), algorithm bias (optimizing for majority group accuracy), and human bias (labeling, feature selection, deployment decisions). Fairness metrics include demographic parity (equal approval rates), equalized odds (equal error rates), and equal opportunity (equal true positive rates). These metrics often conflict, so you must choose the right one for your context.

Mitigation strategies work at three stages: pre-processing (fix the data through resampling or re-weighting), in-processing (add fairness constraints during training), and post-processing (adjust prediction thresholds per group). The Fairlearn library provides tools for both assessment and mitigation.

---

## Key Points

- Bias enters through data (historical, representational, measurement), algorithms, and human decisions
- Removing protected attributes does not eliminate bias due to proxy variables
- Demographic parity requires equal approval rates across groups
- Equalized odds requires equal true positive and false positive rates across groups
- Equal opportunity requires equal true positive rates for qualified individuals
- These fairness definitions can mathematically conflict with each other
- Pre-processing fixes data, in-processing constrains training, post-processing adjusts outputs
- Fairlearn provides MetricFrame for assessment and ExponentiatedGradient for mitigation
- Fairness should be monitored continuously, not just checked once at deployment
- High-stakes AI decisions should always include human oversight

---

## Practice Questions

1. A model has 90% accuracy for Group A and 70% accuracy for Group B. Is this model fair? What additional information would you need to decide?

2. Your training data for a loan approval model comes from 10 years of historical decisions. Why might this be problematic, and what would you do about it?

3. A hiring model does not use gender as a feature, but it uses "years of military service" which correlates strongly with gender. Is this a problem? How would you address it?

4. Explain why it is mathematically impossible to simultaneously achieve demographic parity and equalized odds in most real-world scenarios.

5. You are building a medical diagnosis model. Which fairness metric (demographic parity, equalized odds, or equal opportunity) would you prioritize, and why?

---

## Exercises

### Exercise 1: Bias Audit

Create a bias audit tool that:
1. Takes a dataset with features, labels, and group membership
2. Calculates demographic parity, equalized odds, and equal opportunity
3. Identifies which features are most correlated with group membership (potential proxies)
4. Generates a report with recommendations

### Exercise 2: Compare Mitigation Strategies

Using the biased dataset from this chapter:
1. Apply resampling (pre-processing)
2. Train with threshold adjustment (post-processing)
3. Compare the accuracy-fairness trade-off for each approach
4. Recommend which approach is best for a loan approval scenario

### Exercise 3: Fairness Monitoring System

Build a monitoring system that:
1. Tracks fairness metrics over multiple time periods
2. Detects when fairness metrics degrade beyond acceptable thresholds
3. Generates alerts with specific remediation suggestions
4. Visualizes the trend of fairness metrics over time

---

## What Is Next?

Now that you understand bias and fairness, the next step is understanding why your model makes the predictions it does. In the next chapter, we will explore **Explainability** — how to use SHAP values and LIME to understand model decisions, build trust with stakeholders, and debug models effectively.
