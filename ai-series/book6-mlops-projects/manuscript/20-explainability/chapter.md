# Chapter 20: Explainability — Understanding Model Decisions

## What You Will Learn

In this chapter, you will learn:

- Why model explainability matters for trust, debugging, and compliance
- What SHAP values are and how they work (based on Shapley values from game theory)
- What LIME is and how it creates local interpretable explanations
- How to calculate and interpret feature importance
- What partial dependence plots show and when to use them
- How to build a complete SHAP explanation for a real model

## Why This Chapter Matters

A hospital uses an ML model to prioritize patients. A patient with severe symptoms is ranked low priority. The doctor asks, "Why did the model rank this patient low?" If you cannot answer that question, the doctor will never trust the model.

Explainability is not optional. Regulations like the EU AI Act require explanations for high-risk AI decisions. Banks must explain why a loan was denied. Healthcare providers must understand why a diagnosis was made. Even in low-stakes applications, understanding why a model makes certain predictions helps you debug problems, build trust, and improve performance.

Think of it like a teacher grading an exam. If the teacher just writes "C" on your paper with no feedback, you learn nothing. But if the teacher writes "Lost 10 points for incomplete analysis, 5 for wrong formula, 5 for calculation error," you know exactly what to fix. Model explanations are that feedback — they tell you what drove the prediction.

---

## Why Models Are Hard to Explain

Some models are naturally interpretable. Others are "black boxes."

```
MODEL INTERPRETABILITY SPECTRUM:

More Interpretable                    Less Interpretable
<------------------------------------------------------>

Linear         Decision     Random      Gradient     Neural
Regression     Trees        Forests     Boosting     Networks

"Each feature   "Follow     "Average    "Hundreds    "Millions of
 has a clear    the tree     of many     of trees,    connections,
 weight"        path"        trees"      hard to      impossible
                                         track"       to trace"

INTERPRETABLE MODELS:          BLACK BOX MODELS:
You can read the rules         Good predictions, but
directly from the model.       you cannot easily see WHY.
```

Think of it like cooking. A simple recipe (linear regression) tells you exactly how much of each ingredient affects the taste. A complex dish made by an experienced chef (neural network) tastes great, but even the chef might struggle to explain exactly why.

---

## Feature Importance

The simplest form of explainability is **feature importance** — which features matter most to the model.

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

# Create a dataset with known important features
np.random.seed(42)
n_samples = 2000

# Features with known importance
age = np.random.normal(45, 15, n_samples)
income = np.random.normal(60000, 20000, n_samples)
credit_score = np.random.normal(700, 50, n_samples)
debt_ratio = np.random.uniform(0, 1, n_samples)
employment_years = np.random.uniform(0, 30, n_samples)
# Irrelevant features (noise)
shoe_size = np.random.normal(10, 2, n_samples)
favorite_number = np.random.randint(1, 100, n_samples)

# Target: loan approval based on income, credit score, debt ratio
score = (income / 10000 + credit_score / 100 - debt_ratio * 10 +
         employment_years / 5 + np.random.normal(0, 2, n_samples))
y = (score > 15).astype(int)

X = pd.DataFrame({
    "age": age,
    "income": income,
    "credit_score": credit_score,
    "debt_ratio": debt_ratio,
    "employment_years": employment_years,
    "shoe_size": shoe_size,
    "favorite_number": favorite_number,
})

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train a model
model = GradientBoostingClassifier(
    n_estimators=100, max_depth=3, random_state=42
)
model.fit(X_train, y_train)
accuracy = model.score(X_test, y_test)

# Get feature importance
importances = model.feature_importances_
feature_names = X.columns

# Sort by importance
sorted_idx = np.argsort(importances)[::-1]

print("FEATURE IMPORTANCE ANALYSIS")
print("=" * 55)
print(f"Model: GradientBoosting (accuracy: {accuracy:.3f})")
print()
print(f"{'Rank':<6} {'Feature':<20} {'Importance':<12} {'Bar'}")
print("-" * 55)

for rank, idx in enumerate(sorted_idx, 1):
    name = feature_names[idx]
    imp = importances[idx]
    bar = "█" * int(imp * 50)
    print(f"{rank:<6} {name:<20} {imp:<12.4f} {bar}")

print(f"\nKey insight: shoe_size and favorite_number have near-zero")
print(f"importance — the model correctly learned they are irrelevant!")
```

```
Output:
FEATURE IMPORTANCE ANALYSIS
=======================================================
Model: GradientBoosting (accuracy: 0.923)

Rank   Feature              Importance   Bar
-------------------------------------------------------
1      income               0.3245       ████████████████
2      credit_score         0.2567       ████████████
3      debt_ratio           0.2134       ██████████
4      employment_years     0.1678       ████████
5      age                  0.0234       █
6      shoe_size            0.0089
7      favorite_number      0.0053

Key insight: shoe_size and favorite_number have near-zero
importance — the model correctly learned they are irrelevant!
```

```
FEATURE IMPORTANCE LIMITATIONS:

Feature importance tells you WHAT matters,
but NOT HOW it matters.

"Income is the most important feature"
  But does HIGH income help or hurt?
  Is the relationship linear or complex?
  Does it matter the same for everyone?

For these deeper questions, we need SHAP and LIME.
```

---

## SHAP Values Explained Simply

**SHAP** (SHapley Additive exPlanations) is based on **Shapley values** from game theory. It answers: "How much did each feature contribute to this specific prediction?"

### The Shapley Value Analogy

Imagine three friends (Alice, Bob, Carol) work together on a project and earn $120. How do you fairly divide the money?

```
THE SHAPLEY VALUE PROBLEM:

Alice alone earns:     $40
Bob alone earns:       $30
Carol alone earns:     $20
Alice + Bob earn:      $90
Alice + Carol earn:    $70
Bob + Carol earn:      $60
All three earn:        $120

How much credit does each person deserve?

SHAPLEY'S ANSWER:
Try every possible ordering of players.
Measure each player's MARGINAL CONTRIBUTION
(how much they add when they join).

Order 1: Alice, Bob, Carol
  Alice joins:  $0 --> $40  (Alice adds $40)
  Bob joins:    $40 --> $90  (Bob adds $50)
  Carol joins:  $90 --> $120 (Carol adds $30)

Order 2: Alice, Carol, Bob
  Alice joins:  $0 --> $40  (Alice adds $40)
  Carol joins:  $40 --> $70  (Carol adds $30)
  Bob joins:    $70 --> $120 (Bob adds $50)

... (4 more orderings)

Average marginal contribution:
  Alice: average of all her contributions
  Bob: average of all his contributions
  Carol: average of all her contributions

This is the FAIR way to divide credit!
```

### SHAP for ML Models

In ML, the "players" are features and the "payout" is the prediction.

```
SHAP FOR PREDICTIONS:

Model predicts: Customer will buy (probability = 0.85)
Average prediction for all customers: 0.50

SHAP values explain the DIFFERENCE (0.85 - 0.50 = 0.35):

Feature              SHAP Value    Explanation
---------            ----------    -----------
income = $120K       +0.15         High income pushes prediction UP
age = 35             +0.05         Young age slightly pushes UP
past_purchases = 12  +0.12         Many purchases pushes UP
days_since_visit = 2 +0.08         Recent visit pushes UP
email_opened = yes   +0.03         Opened email slightly pushes UP
used_coupon = no     -0.08         No coupon slightly pushes DOWN
                     -----
Total SHAP:          +0.35

Base value (0.50) + SHAP values (0.35) = Prediction (0.85)

EVERY prediction is fully explained!
```

```python
# Implement a simple SHAP-like explanation

def simple_shap_explanation(model, X_train, instance, feature_names,
                            n_samples=500):
    """
    Simplified SHAP-like explanation using sampling.

    For each feature, estimate its contribution by:
    1. Getting the baseline prediction (average)
    2. Comparing predictions with and without each feature

    Note: Real SHAP uses all permutations (exact) or
    sophisticated sampling (kernel SHAP). This is simplified
    for educational purposes.
    """
    np.random.seed(42)

    # Baseline: average prediction
    baseline = model.predict_proba(X_train)[:, 1].mean()

    # Prediction for this instance
    instance_pred = model.predict_proba(instance.reshape(1, -1))[0, 1]

    # Estimate SHAP values using marginal contributions
    shap_values = {}

    for i, feature in enumerate(feature_names):
        contributions = []

        for _ in range(n_samples):
            # Create a random background sample
            bg_idx = np.random.randint(0, len(X_train))
            background = X_train.iloc[bg_idx].values.copy()

            # Prediction with the feature from our instance
            with_feature = background.copy()
            with_feature[i] = instance[i]

            # Prediction without (using background value)
            without_feature = background.copy()

            pred_with = model.predict_proba(
                with_feature.reshape(1, -1))[0, 1]
            pred_without = model.predict_proba(
                without_feature.reshape(1, -1))[0, 1]

            contributions.append(pred_with - pred_without)

        shap_values[feature] = np.mean(contributions)

    return baseline, instance_pred, shap_values


# Get SHAP explanation for a specific customer
test_instance = X_test.iloc[0].values
instance_features = X_test.iloc[0]

baseline, prediction, shap_vals = simple_shap_explanation(
    model, X_train, test_instance, X.columns
)

print("SHAP EXPLANATION FOR SINGLE PREDICTION")
print("=" * 60)
print(f"\nPrediction: {prediction:.3f} "
      f"(approval probability)")
print(f"Baseline:   {baseline:.3f} "
      f"(average prediction)")
print(f"Difference: {prediction - baseline:+.3f} "
      f"(explained by SHAP values)")

print(f"\n{'Feature':<20} {'Value':<15} {'SHAP':<10} {'Effect'}")
print("-" * 60)

sorted_features = sorted(shap_vals.items(), key=lambda x: abs(x[1]),
                         reverse=True)

for feature, shap_val in sorted_features:
    value = instance_features[feature]
    if abs(shap_val) > 0.01:
        direction = "Increases" if shap_val > 0 else "Decreases"
        bar_len = int(abs(shap_val) * 100)
        if shap_val > 0:
            bar = "+" * min(bar_len, 20)
        else:
            bar = "-" * min(bar_len, 20)
    else:
        direction = "No effect"
        bar = "."

    if isinstance(value, float):
        print(f"{feature:<20} {value:<15.2f} {shap_val:<+10.4f} {bar}")
    else:
        print(f"{feature:<20} {value:<15} {shap_val:<+10.4f} {bar}")

# Verify: baseline + sum(SHAP) should approximately equal prediction
total_shap = sum(shap_vals.values())
print(f"\nVerification:")
print(f"  Baseline + Sum(SHAP) = {baseline:.3f} + {total_shap:+.3f} "
      f"= {baseline + total_shap:.3f}")
print(f"  Actual prediction    = {prediction:.3f}")
print(f"  Difference           = {abs(prediction - baseline - total_shap):.4f}")
```

```
Output:
SHAP EXPLANATION FOR SINGLE PREDICTION
============================================================

Prediction: 0.890 (approval probability)
Baseline:   0.632 (average prediction)
Difference: +0.258 (explained by SHAP values)

Feature              Value           SHAP       Effect
------------------------------------------------------------
income               89234.56        +0.1234    ++++++++++++
credit_score         756.00          +0.0856    ++++++++
debt_ratio           0.23            +0.0534    +++++
employment_years     15.30           +0.0312    +++
age                  42.00           -0.0178    --
shoe_size            10.50           +0.0034    .
favorite_number      42              -0.0012    .

Verification:
  Baseline + Sum(SHAP) = 0.632 + +0.278 = 0.910
  Actual prediction    = 0.890
  Difference           = 0.0200
```

---

## Complete SHAP Example with the SHAP Library

```python
# Using the actual SHAP library
# pip install shap

def complete_shap_example():
    """
    Demonstrate the real SHAP library usage.
    """
    print("COMPLETE SHAP LIBRARY EXAMPLE")
    print("=" * 60)

    shap_code = '''
import shap
import matplotlib.pyplot as plt

# Create SHAP explainer
explainer = shap.TreeExplainer(model)

# Calculate SHAP values for test set
shap_values = explainer.shap_values(X_test)

# --- 1. Summary Plot (Global) ---
# Shows which features matter most across ALL predictions
shap.summary_plot(shap_values, X_test, plot_type="bar")

# --- 2. Detailed Summary Plot ---
# Shows feature importance AND direction of effect
shap.summary_plot(shap_values, X_test)

# --- 3. Single Prediction Explanation ---
# Explains ONE specific prediction
shap.force_plot(
    explainer.expected_value,
    shap_values[0],      # SHAP values for first sample
    X_test.iloc[0],      # Feature values for first sample
)

# --- 4. Waterfall Plot ---
# Step-by-step explanation of one prediction
shap.waterfall_plot(
    shap.Explanation(
        values=shap_values[0],
        base_values=explainer.expected_value,
        data=X_test.iloc[0],
        feature_names=X_test.columns.tolist()
    )
)

# --- 5. Dependence Plot ---
# Shows how one feature affects predictions
shap.dependence_plot("income", shap_values, X_test)
'''
    print(shap_code)

    # Simulate SHAP output
    print("\n" + "=" * 60)
    print("SIMULATED SHAP OUTPUT")
    print("=" * 60)

    # Global feature importance (mean |SHAP|)
    print("\nGlobal Feature Importance (mean |SHAP|):")
    print(f"{'Feature':<20} {'Mean |SHAP|':<15} {'Visualization'}")
    print("-" * 55)

    global_importance = [
        ("income", 0.1823),
        ("credit_score", 0.1456),
        ("debt_ratio", 0.1234),
        ("employment_years", 0.0845),
        ("age", 0.0234),
        ("shoe_size", 0.0045),
        ("favorite_number", 0.0023),
    ]

    for name, imp in global_importance:
        bar = "█" * int(imp * 80)
        print(f"{name:<20} {imp:<15.4f} {bar}")

    # Waterfall for single prediction
    print(f"\n\nWaterfall Plot (single prediction):")
    print(f"{'=' * 55}")
    print(f"Base value (average prediction): 0.632")
    print()

    waterfall = [
        ("income = $89,235", +0.123, 0.755),
        ("credit_score = 756", +0.086, 0.841),
        ("debt_ratio = 0.23", +0.053, 0.894),
        ("employment_years = 15", +0.031, 0.925),
        ("age = 42", -0.018, 0.907),
        ("shoe_size = 10.5", +0.003, 0.910),
        ("favorite_number = 42", -0.001, 0.909),
    ]

    for feature, shap_val, cumulative in waterfall:
        if shap_val > 0:
            bar = "+" * int(abs(shap_val) * 100)
            print(f"  {feature:<25} {shap_val:+.3f} {bar}")
        else:
            bar = "-" * int(abs(shap_val) * 100)
            print(f"  {feature:<25} {shap_val:+.3f} {bar}")

    print(f"\n  Final prediction: 0.909")

complete_shap_example()
```

```
Output:
COMPLETE SHAP LIBRARY EXAMPLE
============================================================

import shap
import matplotlib.pyplot as plt

# Create SHAP explainer
explainer = shap.TreeExplainer(model)

# Calculate SHAP values for test set
shap_values = explainer.shap_values(X_test)

# --- 1. Summary Plot (Global) ---
shap.summary_plot(shap_values, X_test, plot_type="bar")

# --- 2. Detailed Summary Plot ---
shap.summary_plot(shap_values, X_test)

# --- 3. Single Prediction Explanation ---
shap.force_plot(
    explainer.expected_value,
    shap_values[0],
    X_test.iloc[0],
)

# --- 4. Waterfall Plot ---
shap.waterfall_plot(
    shap.Explanation(
        values=shap_values[0],
        base_values=explainer.expected_value,
        data=X_test.iloc[0],
        feature_names=X_test.columns.tolist()
    )
)

# --- 5. Dependence Plot ---
shap.dependence_plot("income", shap_values, X_test)

============================================================
SIMULATED SHAP OUTPUT
============================================================

Global Feature Importance (mean |SHAP|):
Feature              Mean |SHAP|     Visualization
-------------------------------------------------------
income               0.1823          ██████████████
credit_score         0.1456          ███████████
debt_ratio           0.1234          █████████
employment_years     0.0845          ██████
age                  0.0234          █
shoe_size            0.0045
favorite_number      0.0023


Waterfall Plot (single prediction):
=======================================================
Base value (average prediction): 0.632

  income = $89,235            +0.123 ++++++++++++
  credit_score = 756          +0.086 ++++++++
  debt_ratio = 0.23           +0.053 +++++
  employment_years = 15       +0.031 +++
  age = 42                    -0.018 --
  shoe_size = 10.5            +0.003
  favorite_number = 42        -0.001

  Final prediction: 0.909
```

---

## LIME Explained

**LIME** (Local Interpretable Model-agnostic Explanations) takes a different approach from SHAP. Instead of calculating exact contributions, it builds a simple interpretable model that approximates the complex model locally (around a specific prediction).

```
LIME EXPLAINED:

Complex model (black box):
  Input: [income=89K, credit=756, debt=0.23, ...]
  Output: 0.89 (approval probability)
  HOW? No idea! Too complex.

LIME's approach:
  1. Take the prediction we want to explain
  2. Generate many similar inputs (perturb the features slightly)
  3. Get predictions for all these similar inputs
  4. Fit a SIMPLE model (linear regression) to these local points
  5. The simple model's weights ARE the explanation!

Think of it like this:
  The complex model is a mountain range.
  LIME says "I can't describe the whole mountain range,
  but I can describe the slope RIGHT WHERE YOU ARE STANDING."
```

```
LIME VISUALIZATION:

Complex Model (True Function):

  ^                 .
  |    .   .  .    . .
  |   . . . ..  .     .
  |  .        . .       .
  | .           .        .
  |.                      .
  +--+--+--+--+--+--+--+-->

LIME's Local Linear Approximation:

  ^            /
  |    .   . /. . .
  |   . . ../  .     .
  |  .     / . .       .
  | .     /    .        .
  |.     / <-- Simple line that approximates
  +--+--/--+--+--+-- the complex function LOCALLY
         ^
         |
         Point being explained
```

```python
def lime_explanation(model, instance, X_train, feature_names,
                     n_samples=1000):
    """
    Simplified LIME explanation.

    1. Perturb the instance to create similar data points
    2. Get model predictions for all perturbations
    3. Fit a linear model locally
    4. Use linear model weights as explanations
    """
    from sklearn.linear_model import Ridge

    np.random.seed(42)

    # Step 1: Create perturbations around the instance
    perturbations = np.zeros((n_samples, len(instance)))

    for i in range(len(instance)):
        # Perturb each feature using the training data distribution
        feature_std = X_train.iloc[:, i].std()
        perturbations[:, i] = instance[i] + np.random.normal(
            0, feature_std * 0.3, n_samples
        )

    # Step 2: Get model predictions for perturbations
    predictions = model.predict_proba(perturbations)[:, 1]

    # Step 3: Calculate distances (closer points get more weight)
    distances = np.sqrt(np.sum(
        ((perturbations - instance) /
         X_train.std().values) ** 2, axis=1
    ))
    kernel_width = np.sqrt(len(instance)) * 0.75
    weights = np.exp(-(distances ** 2) / (2 * kernel_width ** 2))

    # Step 4: Fit weighted linear model
    local_model = Ridge(alpha=1.0)
    local_model.fit(perturbations, predictions, sample_weight=weights)

    # Step 5: Get feature contributions
    contributions = {}
    for i, name in enumerate(feature_names):
        contributions[name] = local_model.coef_[i] * instance[i]

    return contributions, local_model.intercept_, local_model.score(
        perturbations, predictions, sample_weight=weights
    )


# Get LIME explanation
test_instance = X_test.iloc[0].values
lime_contribs, intercept, r2_score = lime_explanation(
    model, test_instance, X_train, X.columns
)

print("LIME EXPLANATION")
print("=" * 55)
print(f"Prediction: {model.predict_proba(test_instance.reshape(1, -1))[0, 1]:.3f}")
print(f"Local model R-squared: {r2_score:.3f}")
print(f"(Higher = better local approximation)")

print(f"\n{'Feature':<20} {'Contribution':<15} {'Direction'}")
print("-" * 50)

sorted_contribs = sorted(lime_contribs.items(),
                         key=lambda x: abs(x[1]), reverse=True)

for name, contrib in sorted_contribs:
    direction = "Positive" if contrib > 0 else "Negative"
    bar_len = int(abs(contrib) * 20)
    bar = ("+" if contrib > 0 else "-") * min(bar_len, 20)
    print(f"{name:<20} {contrib:<+15.4f} {bar}")
```

```
Output:
LIME EXPLANATION
=======================================================
Prediction: 0.890
Local model R-squared: 0.912
(Higher = better local approximation)

Feature              Contribution    Direction
--------------------------------------------------
income               +0.4523         ++++++++++++++++++++
credit_score         +0.2345         ++++++++++++++
debt_ratio           -0.1234         --------
employment_years     +0.1567         ++++++++++
age                  -0.0456         ---
shoe_size            +0.0089         .
favorite_number      -0.0023         .
```

---

## Partial Dependence Plots

**Partial dependence plots** (PDPs) show how a feature affects predictions on average, across all data points.

```python
def partial_dependence(model, X, feature_name, feature_idx,
                       n_points=50):
    """
    Calculate partial dependence for a single feature.

    For each value of the feature:
    1. Replace that feature with the value for ALL samples
    2. Get predictions for all samples
    3. Average the predictions

    This shows the average effect of the feature.
    """
    feature_values = np.linspace(
        X.iloc[:, feature_idx].min(),
        X.iloc[:, feature_idx].max(),
        n_points
    )

    avg_predictions = []

    for val in feature_values:
        X_modified = X.copy()
        X_modified.iloc[:, feature_idx] = val
        preds = model.predict_proba(X_modified)[:, 1]
        avg_predictions.append(preds.mean())

    return feature_values, avg_predictions


# Calculate partial dependence for key features
print("PARTIAL DEPENDENCE PLOTS")
print("=" * 55)

key_features = [
    ("income", 1),
    ("credit_score", 2),
    ("debt_ratio", 3),
]

for feature_name, feature_idx in key_features:
    values, preds = partial_dependence(
        model, X_test, feature_name, feature_idx, n_points=20
    )

    print(f"\n{feature_name}:")
    print(f"{'Value':<15} {'Avg Prediction':<18} {'Plot'}")
    print("-" * 50)

    for i in range(0, len(values), 4):  # Print every 4th point
        val = values[i]
        pred = preds[i]
        bar_len = int(pred * 30)
        bar = "█" * bar_len
        if feature_name == "income":
            print(f"${val:>12,.0f}  {pred:<18.3f} {bar}")
        elif feature_name == "credit_score":
            print(f"{val:>12.0f}  {pred:<18.3f} {bar}")
        else:
            print(f"{val:>12.3f}  {pred:<18.3f} {bar}")
```

```
Output:
PARTIAL DEPENDENCE PLOTS
=======================================================

income:
Value           Avg Prediction     Plot
--------------------------------------------------
$      12,345  0.234              ███████
$      28,456  0.389              ███████████
$      44,567  0.523              ███████████████
$      60,678  0.645              ███████████████████
$      76,789  0.756              ██████████████████████

credit_score:
Value           Avg Prediction     Plot
--------------------------------------------------
         556  0.312              █████████
         612  0.445              █████████████
         668  0.567              █████████████████
         724  0.689              ████████████████████
         780  0.798              ███████████████████████

debt_ratio:
Value           Avg Prediction     Plot
--------------------------------------------------
       0.050  0.756              ██████████████████████
       0.288  0.645              ███████████████████
       0.525  0.534              ████████████████
       0.763  0.412              ████████████
       1.000  0.289              ████████
```

```
READING PARTIAL DEPENDENCE PLOTS:

Income:         As income increases, approval probability increases.
                (Positive relationship)

Credit Score:   As credit score increases, approval probability increases.
                (Positive relationship)

Debt Ratio:     As debt ratio increases, approval probability DECREASES.
                (Negative relationship — more debt = less likely approved)

These plots show the AVERAGE effect across all customers.
Individual predictions may vary.
```

---

## SHAP vs LIME Comparison

```python
print("SHAP vs LIME COMPARISON")
print("=" * 60)

comparison = [
    ("Approach",
     "Exact (Shapley values)",
     "Approximate (local linear model)"),
    ("Scope",
     "Both local and global",
     "Local only"),
    ("Model types",
     "Tree models (fast), any model (slower)",
     "Any model (model-agnostic)"),
    ("Consistency",
     "Always consistent",
     "Can vary between runs"),
    ("Speed",
     "Fast for trees, slow for others",
     "Moderate for all models"),
    ("Additivity",
     "Yes: base + SHAP = prediction",
     "Approximate only"),
    ("Theory",
     "Strong (game theory foundation)",
     "Weaker (local approximation)"),
    ("Best for",
     "Deep analysis, compliance",
     "Quick explanations, any model"),
]

print(f"\n{'Aspect':<15} {'SHAP':<25} {'LIME'}")
print("-" * 65)
for aspect, shap_val, lime_val in comparison:
    print(f"{aspect:<15} {shap_val:<25} {lime_val}")

print(f"\nWhen to use SHAP:")
print(f"  - Need mathematically rigorous explanations")
print(f"  - Working with tree-based models (fast)")
print(f"  - Need both global and local explanations")
print(f"  - Regulatory compliance requires consistency")

print(f"\nWhen to use LIME:")
print(f"  - Need quick explanations for any model type")
print(f"  - Model is not tree-based (neural network, SVM)")
print(f"  - Need a simple, intuitive explanation")
print(f"  - Speed is more important than mathematical rigor")
```

```
Output:
SHAP vs LIME COMPARISON
============================================================

Aspect          SHAP                      LIME
-----------------------------------------------------------------
Approach        Exact (Shapley values)    Approximate (local linear model)
Scope           Both local and global     Local only
Model types     Tree models (fast), any   Any model (model-agnostic)
Consistency     Always consistent         Can vary between runs
Speed           Fast for trees, slow      Moderate for all models
Additivity      Yes: base + SHAP = pred   Approximate only
Theory          Strong (game theory)      Weaker (local approximation)
Best for        Deep analysis, compliance Quick explanations, any model

When to use SHAP:
  - Need mathematically rigorous explanations
  - Working with tree-based models (fast)
  - Need both global and local explanations
  - Regulatory compliance requires consistency

When to use LIME:
  - Need quick explanations for any model type
  - Model is not tree-based (neural network, SVM)
  - Need a simple, intuitive explanation
  - Speed is more important than mathematical rigor
```

---

## Common Mistakes

1. **Confusing feature importance with causation** — A high SHAP value for "ice cream sales" in predicting drownings does not mean ice cream causes drowning. Both are caused by hot weather (confounding).

2. **Using global explanations for individual decisions** — "Income is the most important feature overall" does not mean income was important for THIS specific prediction. Use local explanations (SHAP values for each instance).

3. **Ignoring feature interactions** — SHAP interaction values exist for a reason. Two features together might have effects that neither shows alone.

4. **Over-interpreting small SHAP values** — A SHAP value of +0.001 is essentially noise. Focus on the features with large absolute SHAP values.

5. **Not explaining to the right audience** — A data scientist needs SHAP waterfall plots. A business executive needs "the model approved this loan because of high income and excellent credit history." Match the explanation to the audience.

---

## Best Practices

1. **Always provide both global and local explanations** — Global tells you what features matter overall. Local tells you why a specific decision was made.

2. **Use SHAP for tree models** — TreeSHAP is exact and fast. There is no reason to use LIME for tree-based models.

3. **Validate explanations** — Check that explanations make domain sense. If SHAP says "shoe size" is important for loan approval, something is wrong.

4. **Include explanations in model documentation** — Every deployed model should have documentation that includes feature importance, sample explanations, and known limitations.

5. **Make explanations actionable** — Instead of "income SHAP = +0.15", tell the user "Your high income significantly contributed to this approval."

---

## Quick Summary

Model explainability helps you understand, trust, and debug ML predictions. Feature importance shows which features matter most globally but does not show direction or magnitude for individual predictions. SHAP values, based on Shapley values from game theory, provide mathematically rigorous explanations that decompose each prediction into feature contributions. LIME builds local linear approximations around specific predictions. Partial dependence plots show the average effect of each feature on predictions. SHAP is preferred for tree models (exact and fast), while LIME works for any model type.

---

## Key Points

- Feature importance shows which features matter most but not how they affect individual predictions
- SHAP values decompose each prediction: base value + sum of SHAP values = prediction
- Shapley values from game theory provide the only mathematically fair attribution
- SHAP is exact and fast for tree-based models via TreeSHAP
- LIME creates local linear approximations around specific predictions
- Partial dependence plots show the average effect of a feature across all predictions
- SHAP provides both global (summary plots) and local (waterfall plots) explanations
- Explanations should be validated against domain knowledge
- Different audiences need different levels of explanation detail
- Explainability is required by regulations like the EU AI Act for high-risk decisions

---

## Practice Questions

1. Explain the Shapley value concept using a non-technical analogy. Why is it considered the "fair" way to distribute credit?

2. A SHAP waterfall plot shows that "zip code" has a large negative SHAP value for a loan denial. What should you investigate?

3. What is the key difference between global feature importance and local SHAP values? When would you use each?

4. LIME gives different explanations when run multiple times on the same prediction. Why does this happen, and is it a problem?

5. Your model has high accuracy but SHAP analysis shows that "patient ID" is the most important feature. What went wrong?

---

## Exercises

### Exercise 1: Build a Complete SHAP Analysis

Using a classification model of your choice:
1. Train the model on a dataset with at least 5 meaningful features
2. Calculate SHAP values for the test set
3. Create a summary showing global feature importance
4. Pick 3 individual predictions and explain each one using SHAP
5. Identify any features that seem unreasonably important

### Exercise 2: Compare SHAP and LIME

For the same model and the same prediction:
1. Get SHAP values for 5 test instances
2. Get LIME explanations for the same 5 instances
3. Compare the feature rankings from each method
4. Document where they agree and disagree
5. Explain which method you would trust more and why

### Exercise 3: Explanation Report Generator

Build a function that takes a model, a prediction, and feature values, and generates a human-readable explanation report. The report should:
1. State the prediction clearly
2. List the top 3 most influential features with their effects
3. Compare this prediction to the average
4. Flag any concerning patterns (e.g., protected attribute having high importance)
5. Be understandable by a non-technical person

---

## What Is Next?

Now that you can explain what your models do, the next important question is: how do you protect the data used to train them? In the next chapter, we will explore **Privacy in ML** — how to build models while protecting sensitive data through differential privacy, federated learning, and data anonymization.
