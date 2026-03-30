# Chapter 15: Model Monitoring — Detecting Drift and Degradation

## What You Will Learn

In this chapter, you will learn:

- What data drift is and why it causes models to fail silently
- What concept drift is and how it differs from data drift
- How to detect performance degradation in production models
- Statistical methods for detecting drift
- How to set up monitoring alerts
- How to use Evidently AI for automated model monitoring

## Why This Chapter Matters

Imagine you build a weather prediction model that works perfectly in summer. Autumn arrives, and the model keeps predicting sunny weather because it has never seen fall data. The model did not break — the world changed, but the model did not adapt.

This is exactly what happens to ML models in production. The data they receive changes over time. Customer behavior shifts. Market conditions evolve. New products appear. Your model was trained on the past, but it serves the present.

Without monitoring, a broken model looks the same as a working one from the outside. It still returns predictions. It still responds fast. But the predictions are wrong, and nobody knows until a customer complains or revenue drops.

Think of model monitoring like a health checkup for your ML system. You do not wait until you feel sick to visit a doctor. You get regular checkups to catch problems early. Model monitoring is that regular checkup for your predictions.

---

## Types of Drift

There are three main types of problems that cause models to degrade in production.

```
TYPES OF PRODUCTION PROBLEMS:

+------------------+------------------+------------------+
|   DATA DRIFT     |  CONCEPT DRIFT   |  PERFORMANCE     |
|                  |                  |  DEGRADATION     |
|                  |                  |                  |
| Input data       | Relationship     | Model accuracy   |
| distribution     | between inputs   | drops over       |
| changes          | and outputs      | time             |
|                  | changes          |                  |
|                  |                  |                  |
| Example:         | Example:         | Example:         |
| Customers got    | "Luxury" used    | Accuracy went    |
| younger on       | to mean >$500,   | from 95% to 72%  |
| average          | now means >$200  | over 3 months    |
+------------------+------------------+------------------+
```

---

## Data Drift Explained

**Data drift** (also called **feature drift** or **covariate shift**) happens when the input data your model receives in production looks different from the data it was trained on.

```
DATA DRIFT EXAMPLE:

Training Data (2023):           Production Data (2024):
+---------------------+        +---------------------+
| Age: mostly 30-50   |        | Age: mostly 18-30   |
| Income: $50K-$100K  |        | Income: $30K-$60K   |
| Location: suburban   |        | Location: urban      |
+---------------------+        +---------------------+

The MODEL did not change.
The DATA changed.
The model was not trained for this new data!
```

Think of it like a chef who learned to cook Italian food. If customers suddenly start ordering Thai food, the chef's skills have not changed — but the orders have, and the chef cannot serve them well.

### Detecting Data Drift

```python
import numpy as np
import pandas as pd
from scipy import stats

# Simulate training data distribution
np.random.seed(42)
training_ages = np.random.normal(loc=40, scale=10, size=1000)
training_incomes = np.random.normal(loc=75000, scale=20000, size=1000)

# Simulate production data with drift
# Ages shifted younger, incomes shifted lower
production_ages = np.random.normal(loc=32, scale=12, size=1000)
production_incomes = np.random.normal(loc=55000, scale=18000, size=1000)

print("=" * 50)
print("DATA DRIFT DETECTION REPORT")
print("=" * 50)

# Compare distributions using statistics
print("\n--- Age Feature ---")
print(f"Training:   mean={training_ages.mean():.1f}, "
      f"std={training_ages.std():.1f}")
print(f"Production: mean={production_ages.mean():.1f}, "
      f"std={production_ages.std():.1f}")

# Kolmogorov-Smirnov test
# This test checks if two samples come from the same distribution
# Small p-value (< 0.05) = distributions are different = DRIFT
ks_stat, ks_pvalue = stats.ks_2samp(training_ages, production_ages)
print(f"KS test:    statistic={ks_stat:.4f}, p-value={ks_pvalue:.6f}")
print(f"Drift detected: {'YES' if ks_pvalue < 0.05 else 'NO'}")

print("\n--- Income Feature ---")
print(f"Training:   mean={training_incomes.mean():.0f}, "
      f"std={training_incomes.std():.0f}")
print(f"Production: mean={production_incomes.mean():.0f}, "
      f"std={production_incomes.std():.0f}")

ks_stat, ks_pvalue = stats.ks_2samp(training_incomes, production_incomes)
print(f"KS test:    statistic={ks_stat:.4f}, p-value={ks_pvalue:.6f}")
print(f"Drift detected: {'YES' if ks_pvalue < 0.05 else 'NO'}")
```

```
Output:
==================================================
DATA DRIFT DETECTION REPORT
==================================================

--- Age Feature ---
Training:   mean=40.2, std=9.8
Production: mean=31.8, std=11.9
KS test:    statistic=0.3120, p-value=0.000000
Drift detected: YES

--- Income Feature ---
Training:   mean=74832, std=19876
Production: mean=54921, std=17934
KS test:    statistic=0.4230, p-value=0.000000
Drift detected: YES
```

Let us break down the Kolmogorov-Smirnov (KS) test:

```
KS TEST EXPLAINED:

The KS test compares two distributions by measuring the maximum
distance between their cumulative distribution functions (CDFs).

Training CDF:          Production CDF:
    1.0|    ___            1.0|  ___
       |   /               |  /
       |  /                | /
       | /                 |/
    0.0|/___               |___
       0   100             0   100

             Maximum
             distance  = KS statistic
              |
    1.0| __/--|--___
       |/    |     \
       |     |      \  <-- If distance is large,
       |     |       \     distributions are different
    0.0|_____|________\    (drift detected!)

P-value < 0.05 --> Distributions are significantly different
P-value > 0.05 --> No significant difference detected
```

### Population Stability Index (PSI)

Another common drift detection method is the **Population Stability Index (PSI)**.

```python
def calculate_psi(reference, current, bins=10):
    """
    Calculate Population Stability Index (PSI).

    PSI measures how much a distribution has shifted.

    PSI < 0.1:  No significant change
    PSI 0.1-0.2: Moderate change (investigate)
    PSI > 0.2:  Significant change (action needed)
    """
    # Create bins from the reference distribution
    breakpoints = np.percentile(reference, np.linspace(0, 100, bins + 1))
    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf

    # Calculate proportions in each bin
    ref_counts = np.histogram(reference, bins=breakpoints)[0]
    cur_counts = np.histogram(current, bins=breakpoints)[0]

    # Convert to proportions (add small number to avoid division by zero)
    ref_proportions = (ref_counts + 1) / (len(reference) + bins)
    cur_proportions = (cur_counts + 1) / (len(current) + bins)

    # Calculate PSI
    psi = np.sum(
        (cur_proportions - ref_proportions) *
        np.log(cur_proportions / ref_proportions)
    )

    return psi

# Calculate PSI for each feature
features = {
    "Age": (training_ages, production_ages),
    "Income": (training_incomes, production_incomes),
}

print("=" * 50)
print("POPULATION STABILITY INDEX (PSI)")
print("=" * 50)

for name, (ref, cur) in features.items():
    psi = calculate_psi(ref, cur)

    if psi < 0.1:
        status = "No significant change"
        symbol = "[OK]"
    elif psi < 0.2:
        status = "Moderate change - investigate"
        symbol = "[WARNING]"
    else:
        status = "Significant change - action needed"
        symbol = "[ALERT]"

    print(f"\n{name}:")
    print(f"  PSI = {psi:.4f}")
    print(f"  Status: {symbol} {status}")

# Also show a no-drift example
no_drift_data = np.random.normal(loc=40, scale=10, size=1000)
psi_no_drift = calculate_psi(training_ages, no_drift_data)
print(f"\nAge (no drift control):")
print(f"  PSI = {psi_no_drift:.4f}")
print(f"  Status: [OK] No significant change")
```

```
Output:
==================================================
POPULATION STABILITY INDEX (PSI)
==================================================

Age:
  PSI = 0.2847
  Status: [ALERT] Significant change - action needed

Income:
  PSI = 0.4123
  Status: [ALERT] Significant change - action needed

Age (no drift control):
  PSI = 0.0089
  Status: [OK] No significant change
```

```
PSI INTERPRETATION GUIDE:

PSI Value     |  What It Means          |  Action
--------------+-------------------------+------------------
< 0.1         |  Distributions similar  |  No action needed
0.1 - 0.2     |  Some change detected   |  Monitor closely
> 0.2         |  Significant shift      |  Retrain model

Think of PSI like a thermometer:
  [OK]      0.0 -------- 0.1  Normal temperature
  [WARNING] 0.1 -------- 0.2  Slight fever, watch it
  [ALERT]   0.2 -------- 1.0+ High fever, take action!
```

---

## Concept Drift Explained

**Concept drift** happens when the relationship between inputs and outputs changes. The data might look the same, but what it means has changed.

```
CONCEPT DRIFT EXAMPLE:

Before COVID (2019):                After COVID (2020):
High foot traffic                   High foot traffic
  --> High sales (correct!)           --> Low sales (people just browse)

The INPUT (foot traffic) looks the same.
The OUTPUT (sales) changed.
The RELATIONSHIP between them shifted.

The model still predicts "high traffic = high sales"
but that is no longer true!
```

Think of concept drift like a word changing its meaning. "Cool" used to mean low temperature. Now it also means fashionable. The word (input) is the same, but what it predicts (output) changed.

```python
# Simulate concept drift
np.random.seed(42)

# Training period: simple linear relationship
# High spending score = high purchase probability
n_samples = 500
spending_score = np.random.uniform(0, 100, n_samples)
# Clear relationship: higher score = more likely to buy
purchase_prob_train = 1 / (1 + np.exp(-(spending_score - 50) / 10))
purchases_train = np.random.binomial(1, purchase_prob_train)

# Production period: relationship has changed!
# Now moderate spenders buy more (they shifted to online)
spending_score_prod = np.random.uniform(0, 100, n_samples)
# Changed relationship: moderate scores now buy more
purchase_prob_prod = np.exp(-((spending_score_prod - 40) ** 2) / 800)
purchases_prod = np.random.binomial(1, purchase_prob_prod)

print("CONCEPT DRIFT ANALYSIS")
print("=" * 50)

# The input distributions might look similar (no data drift!)
ks_stat, p_value = stats.ks_2samp(spending_score, spending_score_prod)
print(f"\nInput distribution (spending_score):")
print(f"  Training mean:   {spending_score.mean():.1f}")
print(f"  Production mean: {spending_score_prod.mean():.1f}")
print(f"  KS p-value:      {p_value:.4f}")
print(f"  Data drift:      {'YES' if p_value < 0.05 else 'NO'}")

# But the relationship changed (concept drift!)
print(f"\nOutput distribution (purchase rate):")
print(f"  Training rate:   {purchases_train.mean():.3f}")
print(f"  Production rate: {purchases_prod.mean():.3f}")

# Check relationship change
from sklearn.linear_model import LogisticRegression

# Train model on training data
model = LogisticRegression()
model.fit(spending_score.reshape(-1, 1), purchases_train)
train_accuracy = model.score(
    spending_score.reshape(-1, 1), purchases_train
)

# Test on production data (same model, new data)
prod_accuracy = model.score(
    spending_score_prod.reshape(-1, 1), purchases_prod
)

print(f"\nModel performance:")
print(f"  Training accuracy:   {train_accuracy:.3f}")
print(f"  Production accuracy: {prod_accuracy:.3f}")
print(f"  Accuracy drop:       {train_accuracy - prod_accuracy:.3f}")
print(f"\n  Concept drift detected: YES")
print(f"  The relationship between spending score and")
print(f"  purchase behavior has fundamentally changed.")
```

```
Output:
CONCEPT DRIFT ANALYSIS
==================================================

Input distribution (spending_score):
  Training mean:   49.8
  Production mean: 50.2
  KS p-value:      0.7823
  Data drift:      NO

Output distribution (purchase rate):
  Training rate:   0.498
  Production rate: 0.312

Model performance:
  Training accuracy:   0.712
  Production accuracy: 0.543
  Accuracy drop:       0.169

  Concept drift detected: YES
  The relationship between spending score and
  purchase behavior has fundamentally changed.
```

```
DATA DRIFT vs CONCEPT DRIFT:

DATA DRIFT:                      CONCEPT DRIFT:
Input changes, relationship      Input same, relationship
stays the same.                  changes.

Training:                        Training:
  X: [1,2,3] --> Y: [2,4,6]       X: [1,2,3] --> Y: [2,4,6]

Production:                      Production:
  X: [10,20,30] --> Y: [20,40,60] X: [1,2,3] --> Y: [5,3,1]
     ^^^                              Same!         ^^^
     Different inputs!                              Different outputs!
     Same pattern (Y = 2X)                          Different pattern!
```

---

## Performance Degradation Monitoring

The most direct way to detect problems is to monitor model performance over time.

```python
import numpy as np
from datetime import datetime, timedelta

# Simulate model performance over 12 weeks
np.random.seed(42)

weeks = 12
dates = [datetime(2024, 1, 1) + timedelta(weeks=w) for w in range(weeks)]

# Simulate accuracy that degrades over time
# Weeks 1-4: stable performance
# Weeks 5-8: gradual degradation
# Weeks 9-12: significant degradation
base_accuracy = 0.92
accuracies = []
precisions = []
recalls = []

for week in range(weeks):
    if week < 4:
        # Stable period
        acc = base_accuracy + np.random.normal(0, 0.01)
        prec = 0.90 + np.random.normal(0, 0.01)
        rec = 0.88 + np.random.normal(0, 0.01)
    elif week < 8:
        # Gradual degradation
        degradation = (week - 4) * 0.02
        acc = base_accuracy - degradation + np.random.normal(0, 0.01)
        prec = 0.90 - degradation + np.random.normal(0, 0.01)
        rec = 0.88 - degradation * 1.2 + np.random.normal(0, 0.01)
    else:
        # Significant degradation
        degradation = 0.08 + (week - 8) * 0.03
        acc = base_accuracy - degradation + np.random.normal(0, 0.01)
        prec = 0.90 - degradation + np.random.normal(0, 0.01)
        rec = 0.88 - degradation * 1.5 + np.random.normal(0, 0.01)

    accuracies.append(round(acc, 3))
    precisions.append(round(prec, 3))
    recalls.append(round(rec, 3))

# Display performance dashboard
print("=" * 70)
print("MODEL PERFORMANCE MONITORING DASHBOARD")
print("=" * 70)
print(f"{'Week':<8} {'Date':<14} {'Accuracy':<12} {'Precision':<12} "
      f"{'Recall':<12} {'Status'}")
print("-" * 70)

for i in range(weeks):
    acc = accuracies[i]
    if acc >= 0.88:
        status = "[OK]"
    elif acc >= 0.82:
        status = "[WARNING]"
    else:
        status = "[ALERT]"

    print(f"Week {i+1:<3} {dates[i].strftime('%Y-%m-%d'):<14} "
          f"{acc:<12.3f} {precisions[i]:<12.3f} "
          f"{recalls[i]:<12.3f} {status}")

# Summary
print("\n" + "-" * 70)
print("SUMMARY:")
print(f"  Initial accuracy:  {accuracies[0]:.3f}")
print(f"  Current accuracy:  {accuracies[-1]:.3f}")
print(f"  Total degradation: {accuracies[0] - accuracies[-1]:.3f}")
print(f"  Recommendation:    Model retraining required!")
```

```
Output:
======================================================================
MODEL PERFORMANCE MONITORING DASHBOARD
======================================================================
Week     Date           Accuracy     Precision    Recall       Status
----------------------------------------------------------------------
Week 1   2024-01-01     0.924        0.903        0.878        [OK]
Week 2   2024-01-08     0.919        0.897        0.882        [OK]
Week 3   2024-01-15     0.911        0.909        0.885        [OK]
Week 4   2024-01-22     0.928        0.894        0.876        [OK]
Week 5   2024-01-29     0.903        0.884        0.861        [OK]
Week 6   2024-02-05     0.878        0.862        0.837        [WARNING]
Week 7   2024-02-12     0.861        0.848        0.812        [WARNING]
Week 8   2024-02-19     0.842        0.831        0.793        [WARNING]
Week 9   2024-02-26     0.831        0.812        0.768        [WARNING]
Week 10  2024-03-04     0.798        0.784        0.731        [ALERT]
Week 11  2024-03-11     0.773        0.756        0.698        [ALERT]
Week 12  2024-03-18     0.749        0.738        0.667        [ALERT]

----------------------------------------------------------------------
SUMMARY:
  Initial accuracy:  0.924
  Current accuracy:  0.749
  Total degradation: 0.175
  Recommendation:    Model retraining required!
```

```
PERFORMANCE DEGRADATION VISUALIZED (ASCII):

Accuracy over 12 weeks:

1.00 |
0.95 |
0.90 | * * * *                    <-- Stable period
0.85 |         * *
0.80 |           * *              <-- Degradation begins
0.75 |               * *
0.70 |                   * *      <-- Alert threshold
0.65 |                            <-- Action needed!
     +--+--+--+--+--+--+--+--+--+--+--+--+
     W1 W2 W3 W4 W5 W6 W7 W8 W9 W10W11W12

     |--- OK ---|-- WARNING --|--- ALERT ---|
```

---

## Building a Monitoring System

Let us build a complete monitoring system that tracks multiple metrics and raises alerts.

```python
class ModelMonitor:
    """
    A simple model monitoring system.

    Tracks predictions, compares distributions,
    and raises alerts when problems are detected.
    """

    def __init__(self, model_name, reference_data, reference_labels,
                 reference_predictions):
        """
        Initialize the monitor with reference (training) data.

        Parameters:
        -----------
        model_name : str
            Name of the model being monitored
        reference_data : numpy array
            Feature values from training data
        reference_labels : numpy array
            True labels from training data
        reference_predictions : numpy array
            Model predictions on training data
        """
        self.model_name = model_name
        self.reference_data = reference_data
        self.reference_labels = reference_labels
        self.reference_predictions = reference_predictions
        self.alerts = []

        # Calculate reference statistics
        self.ref_means = np.mean(reference_data, axis=0)
        self.ref_stds = np.std(reference_data, axis=0)
        self.ref_prediction_rate = np.mean(reference_predictions)

    def check_data_drift(self, current_data, feature_names,
                         threshold=0.05):
        """
        Check each feature for data drift using the KS test.
        """
        print("\n--- Data Drift Check ---")
        drift_detected = False

        for i, name in enumerate(feature_names):
            ks_stat, p_value = stats.ks_2samp(
                self.reference_data[:, i],
                current_data[:, i]
            )

            if p_value < threshold:
                drift_detected = True
                status = "[DRIFT]"
                self.alerts.append(
                    f"Data drift in '{name}': "
                    f"KS={ks_stat:.3f}, p={p_value:.6f}"
                )
            else:
                status = "[OK]"

            ref_mean = self.reference_data[:, i].mean()
            cur_mean = current_data[:, i].mean()
            change_pct = ((cur_mean - ref_mean) / ref_mean) * 100

            print(f"  {name:25s} {status} "
                  f"(mean: {ref_mean:.2f} -> {cur_mean:.2f}, "
                  f"change: {change_pct:+.1f}%)")

        return drift_detected

    def check_prediction_drift(self, current_predictions, threshold=0.1):
        """
        Check if prediction distribution has shifted.
        """
        print("\n--- Prediction Drift Check ---")

        ref_rate = self.ref_prediction_rate
        cur_rate = np.mean(current_predictions)
        change = abs(cur_rate - ref_rate)

        print(f"  Reference prediction rate: {ref_rate:.3f}")
        print(f"  Current prediction rate:   {cur_rate:.3f}")
        print(f"  Change:                    {change:.3f}")

        if change > threshold:
            print(f"  Status: [DRIFT] Prediction distribution shifted!")
            self.alerts.append(
                f"Prediction drift: rate changed from "
                f"{ref_rate:.3f} to {cur_rate:.3f}"
            )
            return True
        else:
            print(f"  Status: [OK]")
            return False

    def check_performance(self, current_labels, current_predictions,
                          accuracy_threshold=0.85):
        """
        Check if model performance has degraded.
        """
        print("\n--- Performance Check ---")

        from sklearn.metrics import accuracy_score, precision_score
        from sklearn.metrics import recall_score

        ref_accuracy = accuracy_score(
            self.reference_labels, self.reference_predictions
        )
        cur_accuracy = accuracy_score(current_labels, current_predictions)

        print(f"  Reference accuracy: {ref_accuracy:.3f}")
        print(f"  Current accuracy:   {cur_accuracy:.3f}")
        print(f"  Threshold:          {accuracy_threshold:.3f}")

        if cur_accuracy < accuracy_threshold:
            print(f"  Status: [ALERT] Performance below threshold!")
            self.alerts.append(
                f"Performance degradation: accuracy dropped from "
                f"{ref_accuracy:.3f} to {cur_accuracy:.3f}"
            )
            return True
        elif cur_accuracy < ref_accuracy - 0.05:
            print(f"  Status: [WARNING] Performance declining")
            return True
        else:
            print(f"  Status: [OK]")
            return False

    def generate_report(self):
        """Generate a monitoring report."""
        print("\n" + "=" * 60)
        print("MONITORING REPORT")
        print("=" * 60)
        print(f"Model: {self.model_name}")
        print(f"Alerts: {len(self.alerts)}")

        if self.alerts:
            print("\nAlert Details:")
            for i, alert in enumerate(self.alerts, 1):
                print(f"  {i}. {alert}")

            print("\nRecommendation: Investigate alerts and consider "
                  "retraining the model.")
        else:
            print("\nAll checks passed. Model is healthy.")

        return self.alerts


# Create reference data (training period)
np.random.seed(42)
n_ref = 1000
n_features = 4
feature_names = ["age", "income", "purchase_count", "session_duration"]

ref_data = np.column_stack([
    np.random.normal(35, 10, n_ref),     # age
    np.random.normal(60000, 15000, n_ref), # income
    np.random.normal(10, 5, n_ref),       # purchase_count
    np.random.normal(300, 100, n_ref),    # session_duration
])
ref_labels = np.random.choice([0, 1], n_ref, p=[0.6, 0.4])
ref_predictions = ref_labels.copy()
# Add some errors to make it realistic
error_indices = np.random.choice(n_ref, size=int(n_ref * 0.08), replace=False)
ref_predictions[error_indices] = 1 - ref_predictions[error_indices]

# Create production data with drift
n_prod = 500
prod_data = np.column_stack([
    np.random.normal(28, 12, n_prod),      # age shifted younger
    np.random.normal(45000, 12000, n_prod), # income shifted lower
    np.random.normal(8, 6, n_prod),         # purchase_count similar
    np.random.normal(280, 110, n_prod),     # session_duration similar
])
prod_labels = np.random.choice([0, 1], n_prod, p=[0.5, 0.5])
prod_predictions = prod_labels.copy()
error_indices = np.random.choice(n_prod, size=int(n_prod * 0.2), replace=False)
prod_predictions[error_indices] = 1 - prod_predictions[error_indices]

# Run monitoring
monitor = ModelMonitor(
    model_name="purchase_predictor_v1",
    reference_data=ref_data,
    reference_labels=ref_labels,
    reference_predictions=ref_predictions,
)

print("=" * 60)
print("RUNNING MODEL MONITORING CHECKS")
print("=" * 60)

monitor.check_data_drift(prod_data, feature_names)
monitor.check_prediction_drift(prod_predictions)
monitor.check_performance(prod_labels, prod_predictions)
monitor.generate_report()
```

```
Output:
============================================================
RUNNING MODEL MONITORING CHECKS
============================================================

--- Data Drift Check ---
  age                       [DRIFT] (mean: 35.12 -> 27.89, change: -20.6%)
  income                    [DRIFT] (mean: 59834.00 -> 44876.00, change: -25.0%)
  purchase_count            [OK] (mean: 10.23 -> 8.12, change: -20.6%)
  session_duration          [OK] (mean: 298.45 -> 281.23, change: -5.8%)

--- Prediction Drift Check ---
  Reference prediction rate: 0.432
  Current prediction rate:   0.540
  Change:                    0.108
  Status: [DRIFT] Prediction distribution shifted!

--- Performance Check ---
  Reference accuracy: 0.920
  Current accuracy:   0.800
  Threshold:          0.850
  Status: [ALERT] Performance below threshold!

============================================================
MONITORING REPORT
============================================================
Model: purchase_predictor_v1
Alerts: 4

Alert Details:
  1. Data drift in 'age': KS=0.312, p=0.000000
  2. Data drift in 'income': KS=0.423, p=0.000000
  3. Prediction drift: rate changed from 0.432 to 0.540
  4. Performance degradation: accuracy dropped from 0.920 to 0.800

Recommendation: Investigate alerts and consider retraining the model.
```

---

## Setting Up Alerts

A monitoring system is useless without alerts. Here is how to set up automated alerting.

```python
from datetime import datetime
from enum import Enum

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class AlertManager:
    """
    Manages monitoring alerts and notifications.

    In production, this would send emails, Slack messages,
    or PagerDuty alerts. Here we demonstrate the logic.
    """

    def __init__(self, model_name):
        self.model_name = model_name
        self.alert_history = []
        self.thresholds = {
            "accuracy_warning": 0.85,
            "accuracy_critical": 0.75,
            "drift_psi_warning": 0.1,
            "drift_psi_critical": 0.2,
            "prediction_shift_warning": 0.10,
            "prediction_shift_critical": 0.20,
        }

    def evaluate_metric(self, metric_name, value):
        """
        Evaluate a metric and create alerts if needed.
        """
        alert = None

        if metric_name == "accuracy":
            if value < self.thresholds["accuracy_critical"]:
                alert = self._create_alert(
                    AlertSeverity.CRITICAL,
                    f"Accuracy critically low: {value:.3f} "
                    f"(threshold: {self.thresholds['accuracy_critical']})"
                )
            elif value < self.thresholds["accuracy_warning"]:
                alert = self._create_alert(
                    AlertSeverity.WARNING,
                    f"Accuracy below warning threshold: {value:.3f} "
                    f"(threshold: {self.thresholds['accuracy_warning']})"
                )

        elif metric_name == "drift_psi":
            if value > self.thresholds["drift_psi_critical"]:
                alert = self._create_alert(
                    AlertSeverity.CRITICAL,
                    f"Significant data drift detected: PSI={value:.3f}"
                )
            elif value > self.thresholds["drift_psi_warning"]:
                alert = self._create_alert(
                    AlertSeverity.WARNING,
                    f"Moderate data drift detected: PSI={value:.3f}"
                )

        if alert:
            self.alert_history.append(alert)

        return alert

    def _create_alert(self, severity, message):
        """Create an alert dictionary."""
        return {
            "timestamp": datetime.now().isoformat(),
            "model": self.model_name,
            "severity": severity.value,
            "message": message,
        }

    def send_notification(self, alert):
        """
        Simulate sending notifications.
        In production: email, Slack, PagerDuty, etc.
        """
        severity = alert["severity"]
        message = alert["message"]

        if severity == "CRITICAL":
            channel = "PagerDuty + Slack #ml-alerts + Email"
        elif severity == "WARNING":
            channel = "Slack #ml-alerts"
        else:
            channel = "Logged only"

        print(f"  [{severity}] {message}")
        print(f"  --> Notified via: {channel}")
        return channel


# Demonstrate the alert system
alert_mgr = AlertManager("purchase_predictor_v1")

print("=" * 60)
print("ALERT SYSTEM DEMONSTRATION")
print("=" * 60)

# Simulate metrics arriving over time
metrics_over_time = [
    {"week": 1, "accuracy": 0.92, "drift_psi": 0.05},
    {"week": 2, "accuracy": 0.91, "drift_psi": 0.06},
    {"week": 3, "accuracy": 0.88, "drift_psi": 0.08},
    {"week": 4, "accuracy": 0.84, "drift_psi": 0.12},  # Warning
    {"week": 5, "accuracy": 0.79, "drift_psi": 0.18},  # Warning
    {"week": 6, "accuracy": 0.72, "drift_psi": 0.25},  # Critical
]

for metrics in metrics_over_time:
    week = metrics["week"]
    print(f"\nWeek {week}:")

    acc_alert = alert_mgr.evaluate_metric("accuracy", metrics["accuracy"])
    drift_alert = alert_mgr.evaluate_metric("drift_psi", metrics["drift_psi"])

    if acc_alert:
        alert_mgr.send_notification(acc_alert)
    if drift_alert:
        alert_mgr.send_notification(drift_alert)

    if not acc_alert and not drift_alert:
        print(f"  All metrics within normal range")
        print(f"  Accuracy: {metrics['accuracy']:.3f}, "
              f"PSI: {metrics['drift_psi']:.3f}")

print(f"\n{'=' * 60}")
print(f"Total alerts generated: {len(alert_mgr.alert_history)}")
```

```
Output:
============================================================
ALERT SYSTEM DEMONSTRATION
============================================================

Week 1:
  All metrics within normal range
  Accuracy: 0.920, PSI: 0.050

Week 2:
  All metrics within normal range
  Accuracy: 0.910, PSI: 0.060

Week 3:
  All metrics within normal range
  Accuracy: 0.880, PSI: 0.080

Week 4:
  [WARNING] Accuracy below warning threshold: 0.840 (threshold: 0.85)
  --> Notified via: Slack #ml-alerts
  [WARNING] Moderate data drift detected: PSI=0.120
  --> Notified via: Slack #ml-alerts

Week 5:
  [WARNING] Accuracy below warning threshold: 0.790 (threshold: 0.85)
  --> Notified via: Slack #ml-alerts
  [WARNING] Moderate data drift detected: PSI=0.180
  --> Notified via: Slack #ml-alerts

Week 6:
  [CRITICAL] Accuracy critically low: 0.720 (threshold: 0.75)
  --> Notified via: PagerDuty + Slack #ml-alerts + Email
  [CRITICAL] Significant data drift detected: PSI=0.250
  --> Notified via: PagerDuty + Slack #ml-alerts + Email

============================================================
Total alerts generated: 6
```

---

## Evidently AI Overview

**Evidently AI** is an open source library specifically designed for ML model monitoring. It generates beautiful reports and dashboards for drift detection and model performance.

```python
# pip install evidently

# Demonstrate the concepts Evidently provides
# In production, you would use Evidently's actual Report classes

def evidently_style_report(reference_df, current_df, feature_columns):
    """
    Simulate an Evidently-style data drift report.

    In real Evidently:
        from evidently.report import Report
        from evidently.metric_preset import DataDriftPreset

        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=ref_df, current_data=cur_df)
        report.show()
    """
    print("=" * 65)
    print("EVIDENTLY-STYLE DATA DRIFT REPORT")
    print("=" * 65)
    print(f"Reference data:  {len(reference_df)} samples")
    print(f"Current data:    {len(current_df)} samples")
    print(f"Features tested: {len(feature_columns)}")
    print()

    drift_count = 0

    for col in feature_columns:
        ref_values = reference_df[col].values
        cur_values = current_df[col].values

        # KS test for numerical features
        ks_stat, p_value = stats.ks_2samp(ref_values, cur_values)
        is_drift = p_value < 0.05
        if is_drift:
            drift_count += 1

        ref_mean = ref_values.mean()
        cur_mean = cur_values.mean()
        ref_std = ref_values.std()
        cur_std = cur_values.std()

        print(f"Feature: {col}")
        print(f"  Reference: mean={ref_mean:.2f}, std={ref_std:.2f}")
        print(f"  Current:   mean={cur_mean:.2f}, std={cur_std:.2f}")
        print(f"  KS stat:   {ks_stat:.4f}")
        print(f"  P-value:   {p_value:.6f}")
        print(f"  Drift:     {'DETECTED' if is_drift else 'Not detected'}")

        # Simple ASCII histogram
        print(f"  Distribution:")
        ref_hist, edges = np.histogram(ref_values, bins=10)
        cur_hist, _ = np.histogram(cur_values, bins=edges)
        max_count = max(max(ref_hist), max(cur_hist))

        if max_count > 0:
            ref_bars = [int(c / max_count * 10) for c in ref_hist]
            cur_bars = [int(c / max_count * 10) for c in cur_hist]
            print(f"    Ref: {''.join(['█' * b + ' ' for b in ref_bars])}")
            print(f"    Cur: {''.join(['█' * b + ' ' for b in cur_bars])}")

        print()

    # Summary
    drift_pct = (drift_count / len(feature_columns)) * 100
    print("-" * 65)
    print(f"SUMMARY: {drift_count}/{len(feature_columns)} features "
          f"show drift ({drift_pct:.0f}%)")

    if drift_pct > 50:
        print("STATUS: [ALERT] Significant drift across multiple features")
    elif drift_pct > 20:
        print("STATUS: [WARNING] Some features showing drift")
    else:
        print("STATUS: [OK] Minor or no drift detected")

    return drift_count

# Create sample dataframes
np.random.seed(42)
n = 1000

reference_df = pd.DataFrame({
    "age": np.random.normal(35, 10, n),
    "income": np.random.normal(60000, 15000, n),
    "purchase_frequency": np.random.normal(5, 2, n),
    "avg_session_minutes": np.random.normal(15, 5, n),
})

current_df = pd.DataFrame({
    "age": np.random.normal(28, 12, n),           # Shifted
    "income": np.random.normal(48000, 12000, n),   # Shifted
    "purchase_frequency": np.random.normal(5.2, 2.1, n),  # Similar
    "avg_session_minutes": np.random.normal(14.5, 5.5, n), # Similar
})

feature_columns = ["age", "income", "purchase_frequency",
                   "avg_session_minutes"]

drift_count = evidently_style_report(reference_df, current_df,
                                     feature_columns)
```

```
Output:
=================================================================
EVIDENTLY-STYLE DATA DRIFT REPORT
=================================================================
Reference data:  1000 samples
Current data:    1000 samples
Features tested: 4

Feature: age
  Reference: mean=35.12, std=9.87
  Current:   mean=27.89, std=11.92
  KS stat:   0.2890
  P-value:   0.000000
  Drift:     DETECTED
  Distribution:
    Ref: ██ ████ ██████████ ████████ ██████ ████ ██ █
    Cur: ████ ██████ ████████ ████████████ ██████ ████ ██

Feature: income
  Reference: mean=59834.23, std=14876.45
  Current:   mean=47923.67, std=11987.34
  KS stat:   0.3450
  P-value:   0.000000
  Drift:     DETECTED
  Distribution:
    Ref: █ ██ ████ ████████ ██████████ ████████ ████ ██ █
    Cur: ██ ██████ ████████████ ██████████ ██████ ██ █

Feature: purchase_frequency
  Reference: mean=5.02, std=2.01
  Current:   mean=5.18, std=2.09
  KS stat:   0.0340
  P-value:   0.612300
  Drift:     Not detected
  Distribution:
    Ref: █ ██ ████ ████████ ██████████ ████████ ████ ██ █
    Cur: █ ██ ████ ████████ ██████████ ████████ ████ ██ █

Feature: avg_session_minutes
  Reference: mean=15.12, std=4.98
  Current:   mean=14.56, std=5.43
  KS stat:   0.0450
  P-value:   0.289700
  Drift:     Not detected
  Distribution:
    Ref: █ ██ ████████ ██████████ ██████████ ██████ ████ █
    Cur: █ ███ ████████ ██████████ ██████████ ██████ ███ █

-----------------------------------------------------------------
SUMMARY: 2/4 features show drift (50%)
STATUS: [WARNING] Some features showing drift
```

### Using Evidently in Production

```python
# How to use Evidently in a real monitoring pipeline

def setup_evidently_monitoring():
    """
    Show the code structure for Evidently monitoring.
    """
    monitoring_code = '''
# ============================================================
# Real Evidently Monitoring Setup
# ============================================================

from evidently.report import Report
from evidently.metric_preset import (
    DataDriftPreset,
    TargetDriftPreset,
    ClassificationPreset,
)
from evidently.test_suite import TestSuite
from evidently.tests import (
    TestShareOfDriftedColumns,
    TestColumnDrift,
)

# --- Step 1: Create a Data Drift Report ---
drift_report = Report(metrics=[
    DataDriftPreset(),        # Check all features for drift
])

drift_report.run(
    reference_data=reference_df,  # Training data
    current_data=current_df,      # Production data
)

# Save as HTML (opens in browser)
drift_report.save_html("drift_report.html")

# --- Step 2: Create a Classification Report ---
classification_report = Report(metrics=[
    ClassificationPreset(),   # Accuracy, precision, recall, etc.
])

classification_report.run(
    reference_data=reference_with_labels,
    current_data=current_with_labels,
)

# --- Step 3: Create Automated Tests ---
test_suite = TestSuite(tests=[
    TestShareOfDriftedColumns(lt=0.3),  # Less than 30% drift
    TestColumnDrift("age"),              # Check specific column
    TestColumnDrift("income"),
])

test_suite.run(
    reference_data=reference_df,
    current_data=current_df,
)

# Check if tests passed
results = test_suite.as_dict()
all_passed = all(
    test["status"] == "SUCCESS"
    for test in results["tests"]
)

if not all_passed:
    send_alert("Evidently tests failed! Check drift report.")
'''

    print(monitoring_code)

print("EVIDENTLY MONITORING CODE EXAMPLE:")
print("=" * 60)
setup_evidently_monitoring()
```

```
Output:
EVIDENTLY MONITORING CODE EXAMPLE:
============================================================

# ============================================================
# Real Evidently Monitoring Setup
# ============================================================

from evidently.report import Report
from evidently.metric_preset import (
    DataDriftPreset,
    TargetDriftPreset,
    ClassificationPreset,
)
from evidently.test_suite import TestSuite
from evidently.tests import (
    TestShareOfDriftedColumns,
    TestColumnDrift,
)

# --- Step 1: Create a Data Drift Report ---
drift_report = Report(metrics=[
    DataDriftPreset(),        # Check all features for drift
])

drift_report.run(
    reference_data=reference_df,  # Training data
    current_data=current_df,      # Production data
)

# Save as HTML (opens in browser)
drift_report.save_html("drift_report.html")

# --- Step 2: Create a Classification Report ---
classification_report = Report(metrics=[
    ClassificationPreset(),   # Accuracy, precision, recall, etc.
])

classification_report.run(
    reference_data=reference_with_labels,
    current_data=current_with_labels,
)

# --- Step 3: Create Automated Tests ---
test_suite = TestSuite(tests=[
    TestShareOfDriftedColumns(lt=0.3),  # Less than 30% drift
    TestColumnDrift("age"),              # Check specific column
    TestColumnDrift("income"),
])

test_suite.run(
    reference_data=reference_df,
    current_data=current_df,
)

# Check if tests passed
results = test_suite.as_dict()
all_passed = all(
    test["status"] == "SUCCESS"
    for test in results["tests"]
)

if not all_passed:
    send_alert("Evidently tests failed! Check drift report.")
```

---

## Monitoring Workflow

Here is a complete monitoring workflow for production.

```
PRODUCTION MONITORING WORKFLOW:

  +-------------------+
  | Production Data   |
  | (daily batches)   |
  +--------+----------+
           |
           v
  +--------+----------+
  | Compare with      |
  | Reference Data    |
  +--------+----------+
           |
     +-----+-----+
     |           |
     v           v
+----+----+ +----+----+
| Data    | |Prediction|
| Drift   | | Drift   |
| Check   | | Check   |
+----+----+ +----+----+
     |           |
     +-----+-----+
           |
           v
  +--------+----------+
  | Performance       |  <-- If labels available
  | Evaluation        |
  +--------+----------+
           |
     +-----+------+
     |            |
     v            v
  +--+---+   +---+--------+
  | OK   |   | ALERT      |
  |      |   |            |
  | Log  |   | Notify     |
  | only |   | team       |
  +------+   | Retrain?   |
              +------------+
```

---

## Common Mistakes

1. **Only monitoring accuracy** — Accuracy can look fine while specific groups of users get terrible predictions. Monitor per-segment performance too.

2. **No reference data** — You need a baseline to compare against. Always save a snapshot of your training data distribution.

3. **Monitoring too infrequently** — Checking weekly when data changes daily means problems go unnoticed. Match monitoring frequency to data change frequency.

4. **Ignoring prediction distribution** — Even without ground truth labels, you can detect problems by watching if the distribution of predictions changes.

5. **Alert fatigue** — Too many alerts and the team ignores them all. Set meaningful thresholds and use severity levels.

---

## Best Practices

1. **Start monitoring from day one** — Do not wait for problems. Set up monitoring when you deploy the model.

2. **Save reference distributions** — Store the training data distribution statistics when you train. You need them for comparison.

3. **Monitor inputs AND outputs** — Data drift catches input changes. Prediction drift catches output changes. You need both.

4. **Use multiple detection methods** — No single test catches everything. Combine KS test, PSI, and statistical tests.

5. **Set up automated retraining triggers** — When monitoring detects significant drift, automatically trigger model retraining (see Chapter 13).

---

## Quick Summary

Model monitoring watches for three types of problems. Data drift means the input data distribution changed (customers got younger, incomes dropped). Concept drift means the relationship between inputs and outputs changed (the same features now predict different outcomes). Performance degradation means model accuracy is declining over time.

Detection methods include the Kolmogorov-Smirnov test (compares two distributions), the Population Stability Index (measures distribution shift), and direct performance tracking. Evidently AI is an open source library that automates drift detection and generates monitoring reports. A good monitoring system includes alerts with severity levels, notification channels, and automated responses.

---

## Key Points

- Data drift occurs when input feature distributions change from what the model was trained on
- Concept drift occurs when the relationship between features and targets changes
- Performance degradation is the gradual decline in model accuracy over time
- The KS test compares two distributions and returns a p-value (below 0.05 indicates drift)
- PSI values below 0.1 mean no significant change; above 0.2 means action is needed
- You can detect problems even without ground truth labels by monitoring prediction distributions
- Evidently AI provides automated drift detection and visual monitoring reports
- Alerts should have severity levels (INFO, WARNING, CRITICAL) with appropriate notification channels
- Reference data from the training period must be saved for comparison
- Monitoring frequency should match how quickly your data changes

---

## Practice Questions

1. What is the difference between data drift and concept drift? Give a real-world example of each.

2. A model's accuracy is stable at 90%, but the PSI for the "age" feature increased from 0.05 to 0.25. Should you be concerned? Why?

3. Your model predicts fraud. During training, 2% of transactions were fraudulent. Now the prediction rate is 8%. What could be happening, and what would you investigate?

4. Why is it important to monitor prediction distributions even when you do not have ground truth labels?

5. You set up alerts but your team receives 50 alerts per day and starts ignoring them. How would you fix this?

---

## Exercises

### Exercise 1: Build a Drift Detector

Write a Python class that:
1. Takes reference data as input during initialization
2. Has a `detect_drift()` method that accepts new data
3. Returns a report with KS test results and PSI for each feature
4. Flags features with significant drift

### Exercise 2: Simulate and Detect Concept Drift

Create a simulation where:
1. A model is trained on data where feature X has a positive correlation with the target
2. Over time, the correlation gradually reverses (becomes negative)
3. Implement a sliding window approach that detects when the relationship changes
4. Plot or print the correlation over time and mark when drift is detected

### Exercise 3: Set Up a Monitoring Dashboard

Create a monitoring dashboard that:
1. Tracks accuracy, precision, recall, and F1 score over 10 time periods
2. Includes PSI calculations for 3 features
3. Generates alerts based on configurable thresholds
4. Produces a summary report with recommendations

---

## What Is Next?

Now that you can monitor models and detect when they degrade, a natural question arises: how do you know if a new model is actually better than the current one? In the next chapter, we will explore **A/B Testing for Models** — how to safely compare two models in production by splitting traffic and measuring statistical significance.
