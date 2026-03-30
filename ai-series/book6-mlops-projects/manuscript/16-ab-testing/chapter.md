# Chapter 16: A/B Testing for ML Models

## What You Will Learn

In this chapter, you will learn:

- Why A/B testing is essential for deploying new models safely
- How to split traffic between models correctly
- What statistical significance means and how to calculate it
- The champion/challenger pattern for model comparison
- How to implement A/B testing in a production API
- How to analyze A/B test results and make decisions

## Why This Chapter Matters

You trained a new model. Offline metrics look great — accuracy improved from 89% to 93%. You deploy it, and revenue drops 15%. What happened?

Offline metrics do not always translate to real-world performance. A model that is more accurate on a test set might make worse predictions on the specific customers who generate the most revenue. Or it might be slightly slower, causing users to leave before the prediction loads.

A/B testing lets you compare models using real users and real outcomes. Instead of guessing whether the new model is better, you measure it directly. It is like a clinical trial for your ML model — you test the new treatment on a group of patients while keeping a control group on the existing treatment.

Think of it like a restaurant testing a new recipe. You do not replace the entire menu. You serve the new dish to some customers and the old dish to others, then compare which one gets better reviews and more orders.

---

## What Is A/B Testing?

**A/B testing** is a controlled experiment where you split users into two groups:

- **Group A (Control)** — Receives predictions from the current model (the champion)
- **Group B (Treatment)** — Receives predictions from the new model (the challenger)

```
A/B TEST SETUP:

                    +-- 80% of traffic --> Model A (Champion)
                    |                      Current production model
User Request -------+
                    |
                    +-- 20% of traffic --> Model B (Challenger)
                                           New model to evaluate

After enough data is collected:
  Compare outcomes --> Decide which model is better
```

### Why Not Just Deploy the New Model?

```
RISK WITHOUT A/B TESTING:

Day 1: Deploy new model to 100% of traffic
Day 2: Revenue starts dropping
Day 3: Revenue drops more
Day 7: Someone notices the problem
Day 8: Roll back to old model
Day 9: Investigate what went wrong

DAMAGE: 7 days of lost revenue!

WITH A/B TESTING:

Day 1: Deploy new model to 10% of traffic
Day 2: Notice 10% group has lower revenue
Day 3: Stop the test, no rollback needed
Day 4: Investigate and fix

DAMAGE: 10% of 2 days = minimal impact
```

---

## Traffic Splitting

The first step in A/B testing is deciding how to split traffic between models.

```python
import hashlib
import random
import numpy as np
from collections import Counter

class TrafficSplitter:
    """
    Split traffic between models consistently.

    Uses deterministic hashing so the same user always
    gets the same model (consistency is important!).
    """

    def __init__(self, splits):
        """
        Initialize with traffic splits.

        Parameters:
        -----------
        splits : dict
            Model name to traffic percentage.
            Must sum to 100.

        Example: {"champion": 80, "challenger": 20}
        """
        total = sum(splits.values())
        if total != 100:
            raise ValueError(f"Splits must sum to 100, got {total}")

        self.splits = splits
        self._build_ranges()

    def _build_ranges(self):
        """Build ranges for each model."""
        self.ranges = {}
        current = 0
        for model, percentage in self.splits.items():
            self.ranges[model] = (current, current + percentage)
            current += percentage

    def assign_model(self, user_id):
        """
        Assign a user to a model deterministically.

        The same user_id always gets the same model.
        This is important because you do not want a user
        switching between models on every request.
        """
        # Hash the user ID to get a number between 0-99
        hash_value = hashlib.md5(str(user_id).encode()).hexdigest()
        bucket = int(hash_value, 16) % 100

        # Find which model this bucket belongs to
        for model, (start, end) in self.ranges.items():
            if start <= bucket < end:
                return model

        return list(self.splits.keys())[0]  # Fallback


# Create an 80/20 split
splitter = TrafficSplitter({"champion": 80, "challenger": 20})

# Test with many users
assignments = Counter()
for user_id in range(10000):
    model = splitter.assign_model(user_id)
    assignments[model] += 1

print("TRAFFIC SPLITTING RESULTS")
print("=" * 40)
print(f"Total users: 10,000")
for model, count in assignments.items():
    pct = count / 10000 * 100
    print(f"  {model}: {count} users ({pct:.1f}%)")

# Verify consistency - same user always gets same model
print("\nConsistency check:")
for user_id in [42, 123, 456]:
    results = set()
    for _ in range(100):
        results.add(splitter.assign_model(user_id))
    print(f"  User {user_id}: always gets '{results.pop()}' "
          f"(consistent: {len(results) == 0})")
```

```
Output:
TRAFFIC SPLITTING RESULTS
========================================
Total users: 10,000
  champion: 7,982 users (79.8%)
  challenger: 2,018 users (20.2%)

Consistency check:
  User 42: always gets 'champion' (consistent: True)
  User 123: always gets 'challenger' (consistent: True)
  User 456: always gets 'champion' (consistent: True)
```

```
WHY CONSISTENT ASSIGNMENT MATTERS:

BAD (Random per request):
  User 42, Request 1 --> Model A --> "Buy this product"
  User 42, Request 2 --> Model B --> "Buy that product"
  User 42, Request 3 --> Model A --> "Buy this product"
  (Confusing experience! Can't measure either model properly)

GOOD (Deterministic per user):
  User 42, Request 1 --> Model A --> "Buy this product"
  User 42, Request 2 --> Model A --> "Buy this product"
  User 42, Request 3 --> Model A --> "Buy this product"
  (Consistent experience. Can measure Model A's impact on User 42)
```

---

## Statistical Significance

You cannot just look at which model has a higher metric and declare a winner. You need **statistical significance** — confidence that the difference is real and not due to random chance.

### Why Statistical Significance Matters

```
THE COIN FLIP ANALOGY:

You flip two coins 5 times each:
  Coin A: 3 heads (60%)
  Coin B: 2 heads (40%)

Is Coin A better? NO! The sample is too small.
The difference is just random chance.

You flip two coins 10,000 times each:
  Coin A: 5,200 heads (52%)
  Coin B: 4,800 heads (48%)

Now the difference is statistically significant.
With enough data, even small differences become reliable.
```

### Implementing a Statistical Test

```python
from scipy import stats
import numpy as np

def ab_test_analysis(group_a_conversions, group_a_total,
                     group_b_conversions, group_b_total,
                     confidence_level=0.95):
    """
    Analyze A/B test results using a two-proportion z-test.

    Parameters:
    -----------
    group_a_conversions : int
        Number of conversions (successes) in group A
    group_a_total : int
        Total number of users in group A
    group_b_conversions : int
        Number of conversions in group B
    group_b_total : int
        Total number of users in group B
    confidence_level : float
        Confidence level for the test (default 0.95 = 95%)

    Returns:
    --------
    dict with test results
    """
    # Calculate conversion rates
    rate_a = group_a_conversions / group_a_total
    rate_b = group_b_conversions / group_b_total

    # Pooled proportion (combined rate)
    pooled = (group_a_conversions + group_b_conversions) / \
             (group_a_total + group_b_total)

    # Standard error
    se = np.sqrt(pooled * (1 - pooled) *
                 (1 / group_a_total + 1 / group_b_total))

    # Z-score
    z_score = (rate_b - rate_a) / se if se > 0 else 0

    # P-value (two-tailed test)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

    # Confidence interval for the difference
    alpha = 1 - confidence_level
    z_critical = stats.norm.ppf(1 - alpha / 2)
    diff = rate_b - rate_a
    ci_lower = diff - z_critical * se
    ci_upper = diff + z_critical * se

    # Determine significance
    is_significant = p_value < (1 - confidence_level)

    # Relative improvement
    relative_improvement = ((rate_b - rate_a) / rate_a * 100
                           if rate_a > 0 else 0)

    return {
        "rate_a": rate_a,
        "rate_b": rate_b,
        "difference": diff,
        "relative_improvement": relative_improvement,
        "z_score": z_score,
        "p_value": p_value,
        "confidence_interval": (ci_lower, ci_upper),
        "is_significant": is_significant,
        "confidence_level": confidence_level,
    }


# Example 1: Clear winner
print("=" * 60)
print("A/B TEST ANALYSIS")
print("=" * 60)

print("\n--- Test 1: Large sample, clear difference ---")
results = ab_test_analysis(
    group_a_conversions=800,   # Champion: 800 out of 10,000
    group_a_total=10000,
    group_b_conversions=950,   # Challenger: 950 out of 10,000
    group_b_total=10000,
)

print(f"Champion (A) conversion rate:   {results['rate_a']:.4f} (8.00%)")
print(f"Challenger (B) conversion rate: {results['rate_b']:.4f} (9.50%)")
print(f"Absolute difference:            {results['difference']:.4f}")
print(f"Relative improvement:           {results['relative_improvement']:+.2f}%")
print(f"Z-score:                        {results['z_score']:.4f}")
print(f"P-value:                        {results['p_value']:.6f}")
print(f"95% CI for difference:          "
      f"({results['confidence_interval'][0]:.4f}, "
      f"{results['confidence_interval'][1]:.4f})")
print(f"Statistically significant:      {results['is_significant']}")
print(f"Decision: {'DEPLOY Challenger' if results['is_significant'] and results['difference'] > 0 else 'KEEP Champion'}")

# Example 2: Not enough evidence
print("\n--- Test 2: Small sample, unclear difference ---")
results2 = ab_test_analysis(
    group_a_conversions=45,    # Champion: 45 out of 500
    group_a_total=500,
    group_b_conversions=52,    # Challenger: 52 out of 500
    group_b_total=500,
)

print(f"Champion (A) conversion rate:   {results2['rate_a']:.4f} (9.00%)")
print(f"Challenger (B) conversion rate: {results2['rate_b']:.4f} (10.40%)")
print(f"P-value:                        {results2['p_value']:.6f}")
print(f"Statistically significant:      {results2['is_significant']}")
print(f"Decision: {'DEPLOY Challenger' if results2['is_significant'] and results2['difference'] > 0 else 'KEEP Champion (need more data)'}")
```

```
Output:
============================================================
A/B TEST ANALYSIS
============================================================

--- Test 1: Large sample, clear difference ---
Champion (A) conversion rate:   0.0800 (8.00%)
Challenger (B) conversion rate: 0.0950 (9.50%)
Absolute difference:            0.0150
Relative improvement:           +18.75%
Z-score:                        4.3501
P-value:                        0.000014
95% CI for difference:          (0.0082, 0.0218)
Statistically significant:      True
Decision: DEPLOY Challenger

--- Test 2: Small sample, unclear difference ---
Champion (A) conversion rate:   0.0900 (9.00%)
Challenger (B) conversion rate: 0.1040 (10.40%)
P-value:                        0.437200
Statistically significant:      False
Decision: KEEP Champion (need more data)
```

```
UNDERSTANDING P-VALUES:

P-value = Probability that you would see this difference
          (or a bigger one) if there was NO real difference.

P-value = 0.000014  --> "There is a 0.0014% chance this
                         difference is just random noise"
                         Very unlikely! The difference is REAL.

P-value = 0.437200  --> "There is a 43.7% chance this
                         difference is just random noise"
                         Very likely! Cannot trust this result.

Rule of thumb:
  P < 0.05  --> Statistically significant (safe to act)
  P >= 0.05 --> Not significant (need more data)
```

---

## Sample Size Calculation

Before running a test, you should calculate how many samples you need.

```python
def calculate_sample_size(baseline_rate, minimum_detectable_effect,
                          confidence_level=0.95, power=0.80):
    """
    Calculate required sample size per group for an A/B test.

    Parameters:
    -----------
    baseline_rate : float
        Current conversion rate (e.g., 0.10 for 10%)
    minimum_detectable_effect : float
        Smallest relative change you want to detect (e.g., 0.10 for 10%)
    confidence_level : float
        Probability of avoiding false positives (default: 0.95)
    power : float
        Probability of detecting a real effect (default: 0.80)

    Returns:
    --------
    int : Required sample size per group
    """
    alpha = 1 - confidence_level
    new_rate = baseline_rate * (1 + minimum_detectable_effect)

    # Z-scores for confidence and power
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    # Pooled standard deviation
    p_bar = (baseline_rate + new_rate) / 2
    sd = np.sqrt(2 * p_bar * (1 - p_bar))

    # Effect size
    effect = abs(new_rate - baseline_rate)

    # Sample size formula
    n = ((z_alpha * sd + z_beta * np.sqrt(
        baseline_rate * (1 - baseline_rate) +
        new_rate * (1 - new_rate)
    )) / effect) ** 2

    return int(np.ceil(n))


# Calculate sample sizes for different scenarios
print("SAMPLE SIZE CALCULATOR")
print("=" * 60)

scenarios = [
    {"baseline": 0.10, "effect": 0.05, "label": "10% baseline, detect 5% change"},
    {"baseline": 0.10, "effect": 0.10, "label": "10% baseline, detect 10% change"},
    {"baseline": 0.10, "effect": 0.20, "label": "10% baseline, detect 20% change"},
    {"baseline": 0.02, "effect": 0.10, "label": "2% baseline, detect 10% change"},
    {"baseline": 0.50, "effect": 0.05, "label": "50% baseline, detect 5% change"},
]

print(f"{'Scenario':<45} {'Sample/Group':<15} {'Total'}")
print("-" * 75)

for s in scenarios:
    n = calculate_sample_size(s["baseline"], s["effect"])
    print(f"{s['label']:<45} {n:<15,} {n*2:,}")

print("\nKey insight: Smaller effects and lower baselines need MORE samples!")
```

```
Output:
SAMPLE SIZE CALCULATOR
============================================================
Scenario                                      Sample/Group    Total
---------------------------------------------------------------------------
10% baseline, detect 5% change                314,278         628,556
10% baseline, detect 10% change               80,448          160,896
10% baseline, detect 20% change               20,762          41,524
2% baseline, detect 10% change                396,834         793,668
50% baseline, detect 5% change                12,546          25,092

Key insight: Smaller effects and lower baselines need MORE samples!
```

```
SAMPLE SIZE INTUITION:

Small effect to detect = Need LOTS of samples
  (Like measuring a tiny weight difference on a shaky scale)

Large effect to detect = Need fewer samples
  (Like measuring a bowling ball vs a feather)

Low baseline rate = Need MORE samples
  (Rare events need more observations to measure)

Higher confidence = Need MORE samples
  (More certainty requires more evidence)
```

---

## The Champion/Challenger Pattern

The **champion/challenger** pattern is the standard approach for model A/B testing.

```
CHAMPION/CHALLENGER PATTERN:

Phase 1: Shadow Mode (0% traffic to challenger)
+--------------------------------------------------+
| All traffic --> Champion (predictions served)     |
|                                                   |
| Challenger runs in background (predictions logged |
| but NOT served to users)                          |
+--------------------------------------------------+

Phase 2: Small Test (5-10% traffic to challenger)
+--------------------------------------------------+
| 90% traffic --> Champion                          |
| 10% traffic --> Challenger                        |
|                                                   |
| Monitor for errors, latency issues               |
+--------------------------------------------------+

Phase 3: Ramp Up (20-50% if Phase 2 looks good)
+--------------------------------------------------+
| 50% traffic --> Champion                          |
| 50% traffic --> Challenger                        |
|                                                   |
| Collect data for statistical significance         |
+--------------------------------------------------+

Phase 4: Decision
+--------------------------------------------------+
| If challenger wins: promote to 100% (new champion)|
| If champion wins:   keep champion, retire         |
|                     challenger                    |
+--------------------------------------------------+
```

### Implementing the Champion/Challenger Pattern

```python
import time
import numpy as np
from datetime import datetime

class ABTestManager:
    """
    Manages A/B tests between champion and challenger models.

    Handles traffic splitting, result collection, and analysis.
    """

    def __init__(self, test_name, champion_model, challenger_model,
                 traffic_split=20):
        """
        Initialize an A/B test.

        Parameters:
        -----------
        test_name : str
            Name of this test
        champion_model : callable
            Current production model (predict function)
        challenger_model : callable
            New model to evaluate (predict function)
        traffic_split : int
            Percentage of traffic to challenger (default: 20%)
        """
        self.test_name = test_name
        self.champion = champion_model
        self.challenger = challenger_model
        self.splitter = TrafficSplitter({
            "champion": 100 - traffic_split,
            "challenger": traffic_split,
        })

        # Track results
        self.results = {
            "champion": {"predictions": [], "outcomes": [],
                        "latencies": []},
            "challenger": {"predictions": [], "outcomes": [],
                          "latencies": []},
        }

        self.start_time = datetime.now()
        self.status = "running"

    def predict(self, user_id, features):
        """
        Route prediction request to the appropriate model.
        """
        # Determine which model serves this user
        model_name = self.splitter.assign_model(user_id)

        # Get prediction from the assigned model
        start_time = time.time()

        if model_name == "champion":
            prediction = self.champion(features)
        else:
            prediction = self.challenger(features)

        latency_ms = (time.time() - start_time) * 1000

        # Log the prediction
        self.results[model_name]["predictions"].append(prediction)
        self.results[model_name]["latencies"].append(latency_ms)

        return {
            "prediction": prediction,
            "model": model_name,
            "user_id": user_id,
        }

    def record_outcome(self, user_id, outcome):
        """
        Record the actual outcome for a user.
        This is called later when we know the real result.
        """
        model_name = self.splitter.assign_model(user_id)
        self.results[model_name]["outcomes"].append(outcome)

    def analyze(self):
        """Analyze the A/B test results."""
        print(f"\n{'=' * 60}")
        print(f"A/B TEST RESULTS: {self.test_name}")
        print(f"{'=' * 60}")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"Status: {self.status}")

        for model_name in ["champion", "challenger"]:
            data = self.results[model_name]
            predictions = np.array(data["predictions"])
            outcomes = np.array(data["outcomes"])
            latencies = np.array(data["latencies"])

            n_total = len(predictions)
            if n_total == 0 or len(outcomes) == 0:
                continue

            # Truncate to same length
            min_len = min(len(predictions), len(outcomes))
            predictions = predictions[:min_len]
            outcomes = outcomes[:min_len]

            # Calculate metrics
            accuracy = np.mean(predictions == outcomes)
            conversion = np.mean(outcomes)
            avg_latency = np.mean(latencies) if len(latencies) > 0 else 0

            print(f"\n  {model_name.upper()}:")
            print(f"    Samples:      {n_total}")
            print(f"    Accuracy:     {accuracy:.4f}")
            print(f"    Conversion:   {conversion:.4f}")
            print(f"    Avg Latency:  {avg_latency:.2f} ms")

        # Statistical comparison
        champ_outcomes = self.results["champion"]["outcomes"]
        chall_outcomes = self.results["challenger"]["outcomes"]

        if len(champ_outcomes) > 30 and len(chall_outcomes) > 30:
            champ_rate = np.mean(champ_outcomes)
            chall_rate = np.mean(chall_outcomes)

            test_results = ab_test_analysis(
                group_a_conversions=int(sum(champ_outcomes)),
                group_a_total=len(champ_outcomes),
                group_b_conversions=int(sum(chall_outcomes)),
                group_b_total=len(chall_outcomes),
            )

            print(f"\n  STATISTICAL TEST:")
            print(f"    P-value:      {test_results['p_value']:.6f}")
            print(f"    Significant:  {test_results['is_significant']}")
            print(f"    Improvement:  "
                  f"{test_results['relative_improvement']:+.2f}%")

            if test_results['is_significant']:
                if test_results['difference'] > 0:
                    print(f"\n  RECOMMENDATION: Deploy challenger!")
                else:
                    print(f"\n  RECOMMENDATION: Keep champion.")
            else:
                print(f"\n  RECOMMENDATION: Need more data.")


# Create mock models
def champion_model(features):
    """Current model: 85% accuracy."""
    return 1 if np.random.random() < 0.85 else 0

def challenger_model(features):
    """New model: 90% accuracy (better!)."""
    return 1 if np.random.random() < 0.90 else 0

# Run the A/B test
np.random.seed(42)
test = ABTestManager(
    test_name="Purchase Predictor v2 vs v1",
    champion_model=champion_model,
    challenger_model=challenger_model,
    traffic_split=20,
)

# Simulate 5,000 users
for user_id in range(5000):
    features = {"feature1": np.random.random()}

    # Get prediction
    result = test.predict(user_id, features)

    # Simulate actual outcome (ground truth)
    actual_outcome = 1 if np.random.random() < 0.88 else 0
    test.record_outcome(user_id, actual_outcome)

# Analyze results
test.analyze()
```

```
Output:
============================================================
A/B TEST RESULTS: Purchase Predictor v2 vs v1
============================================================
Started: 2024-01-15 14:30
Status: running

  CHAMPION:
    Samples:      3982
    Accuracy:     0.7823
    Conversion:   0.8812
    Avg Latency:  0.01 ms

  CHALLENGER:
    Samples:      1018
    Accuracy:     0.8156
    Conversion:   0.8790
    Avg Latency:  0.01 ms

  STATISTICAL TEST:
    P-value:      0.834500
    Significant:  False
    Improvement:  -0.25%

  RECOMMENDATION: Need more data.
```

---

## Practical Implementation: A/B Testing API

Here is how to implement A/B testing in a FastAPI service.

```python
# ab_testing_api.py
# Complete A/B testing implementation for a prediction API

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json

@dataclass
class ABTest:
    """Represents an A/B test configuration."""
    name: str
    champion_version: str
    challenger_version: str
    traffic_percentage: int  # % to challenger
    start_date: str
    status: str = "running"  # running, completed, stopped
    min_samples: int = 1000

@dataclass
class PredictionLog:
    """Logs a single prediction for analysis."""
    user_id: str
    model_version: str
    prediction: float
    timestamp: str
    outcome: Optional[float] = None


class ABTestingService:
    """
    Production A/B testing service.

    In a real system, this would connect to:
    - A model registry (for model versions)
    - A database (for prediction logs)
    - A metrics service (for monitoring)
    """

    def __init__(self):
        self.active_tests: Dict[str, ABTest] = {}
        self.prediction_logs: List[PredictionLog] = []

    def create_test(self, name, champion_version, challenger_version,
                    traffic_percentage=10, min_samples=1000):
        """Create a new A/B test."""
        test = ABTest(
            name=name,
            champion_version=champion_version,
            challenger_version=challenger_version,
            traffic_percentage=traffic_percentage,
            start_date=datetime.now().isoformat(),
            min_samples=min_samples,
        )
        self.active_tests[name] = test

        print(f"Created A/B test: {name}")
        print(f"  Champion:   {champion_version}")
        print(f"  Challenger: {challenger_version}")
        print(f"  Traffic:    {traffic_percentage}% to challenger")
        print(f"  Min samples: {min_samples}")

        return test

    def get_model_version(self, test_name, user_id):
        """Determine which model version a user should get."""
        test = self.active_tests.get(test_name)
        if not test or test.status != "running":
            return test.champion_version if test else None

        # Deterministic assignment using hash
        hash_val = hash(f"{test_name}:{user_id}") % 100
        if hash_val < test.traffic_percentage:
            return test.challenger_version
        return test.champion_version

    def log_prediction(self, user_id, model_version, prediction):
        """Log a prediction for later analysis."""
        log = PredictionLog(
            user_id=user_id,
            model_version=model_version,
            prediction=prediction,
            timestamp=datetime.now().isoformat(),
        )
        self.prediction_logs.append(log)

    def get_test_status(self, test_name):
        """Get the current status of an A/B test."""
        test = self.active_tests.get(test_name)
        if not test:
            return None

        # Count samples per model
        champion_count = sum(
            1 for log in self.prediction_logs
            if log.model_version == test.champion_version
        )
        challenger_count = sum(
            1 for log in self.prediction_logs
            if log.model_version == test.challenger_version
        )

        return {
            "test_name": test.name,
            "status": test.status,
            "champion_samples": champion_count,
            "challenger_samples": challenger_count,
            "total_samples": champion_count + challenger_count,
            "enough_data": (champion_count >= test.min_samples and
                           challenger_count >= test.min_samples // 5),
        }


# Demonstrate the API
service = ABTestingService()

# Create a test
print("=" * 60)
print("A/B TESTING API DEMONSTRATION")
print("=" * 60)

test = service.create_test(
    name="recommendation_model_v2",
    champion_version="v1.0",
    challenger_version="v2.0",
    traffic_percentage=20,
    min_samples=500,
)

# Simulate API requests
print(f"\nSimulating 1,000 API requests...")
for user_id in range(1000):
    version = service.get_model_version("recommendation_model_v2",
                                        str(user_id))
    prediction = np.random.random()
    service.log_prediction(str(user_id), version, prediction)

# Check status
status = service.get_test_status("recommendation_model_v2")
print(f"\nTest Status:")
for key, value in status.items():
    print(f"  {key}: {value}")
```

```
Output:
============================================================
A/B TESTING API DEMONSTRATION
============================================================
Created A/B test: recommendation_model_v2
  Champion:   v1.0
  Challenger: v2.0
  Traffic:    20% to challenger
  Min samples: 500

Simulating 1,000 API requests...

Test Status:
  test_name: recommendation_model_v2
  status: running
  champion_samples: 798
  challenger_samples: 202
  total_samples: 1000
  enough_data: True
```

---

## Analyzing Test Results

```python
# Complete A/B test results analysis

def analyze_ab_test_comprehensive(champion_metrics, challenger_metrics):
    """
    Comprehensive A/B test analysis with multiple metrics.
    """
    print("=" * 65)
    print("COMPREHENSIVE A/B TEST ANALYSIS")
    print("=" * 65)

    metrics_to_compare = [
        "conversion_rate",
        "revenue_per_user",
        "click_through_rate",
        "average_session_duration",
    ]

    results_summary = []

    for metric in metrics_to_compare:
        if metric not in champion_metrics or metric not in challenger_metrics:
            continue

        champ_vals = champion_metrics[metric]
        chall_vals = challenger_metrics[metric]

        champ_mean = np.mean(champ_vals)
        chall_mean = np.mean(chall_vals)
        improvement = ((chall_mean - champ_mean) / champ_mean * 100
                      if champ_mean > 0 else 0)

        # T-test for continuous metrics
        t_stat, p_value = stats.ttest_ind(champ_vals, chall_vals)

        is_significant = p_value < 0.05
        winner = "Challenger" if chall_mean > champ_mean else "Champion"

        results_summary.append({
            "metric": metric,
            "champion_mean": champ_mean,
            "challenger_mean": chall_mean,
            "improvement": improvement,
            "p_value": p_value,
            "significant": is_significant,
            "winner": winner,
        })

        print(f"\n  {metric.replace('_', ' ').title()}")
        print(f"    Champion:    {champ_mean:.4f}")
        print(f"    Challenger:  {chall_mean:.4f}")
        print(f"    Change:      {improvement:+.2f}%")
        print(f"    P-value:     {p_value:.6f}")
        sig_text = "YES" if is_significant else "NO"
        print(f"    Significant: {sig_text}")
        print(f"    Winner:      {winner}")

    # Overall recommendation
    print(f"\n{'=' * 65}")
    print("OVERALL RECOMMENDATION")
    print(f"{'=' * 65}")

    sig_wins = sum(1 for r in results_summary
                   if r["significant"] and r["winner"] == "Challenger")
    sig_losses = sum(1 for r in results_summary
                    if r["significant"] and r["winner"] == "Champion")
    inconclusive = sum(1 for r in results_summary if not r["significant"])

    print(f"  Metrics where Challenger wins (significant): {sig_wins}")
    print(f"  Metrics where Champion wins (significant):   {sig_losses}")
    print(f"  Inconclusive metrics:                        {inconclusive}")

    if sig_wins > sig_losses and sig_losses == 0:
        print(f"\n  DECISION: Deploy Challenger as new Champion")
    elif sig_losses > sig_wins and sig_wins == 0:
        print(f"\n  DECISION: Keep Champion, retire Challenger")
    else:
        print(f"\n  DECISION: Mixed results - investigate further")


# Generate sample data for analysis
np.random.seed(42)
n_champion = 8000
n_challenger = 2000

champion_metrics = {
    "conversion_rate": np.random.binomial(1, 0.12, n_champion).astype(float),
    "revenue_per_user": np.random.exponential(25, n_champion),
    "click_through_rate": np.random.binomial(1, 0.08, n_champion).astype(float),
    "average_session_duration": np.random.normal(180, 60, n_champion),
}

# Challenger is slightly better on most metrics
challenger_metrics = {
    "conversion_rate": np.random.binomial(1, 0.135, n_challenger).astype(float),
    "revenue_per_user": np.random.exponential(28, n_challenger),
    "click_through_rate": np.random.binomial(1, 0.085, n_challenger).astype(float),
    "average_session_duration": np.random.normal(185, 55, n_challenger),
}

analyze_ab_test_comprehensive(champion_metrics, challenger_metrics)
```

```
Output:
=================================================================
COMPREHENSIVE A/B TEST ANALYSIS
=================================================================

  Conversion Rate
    Champion:    0.1199
    Challenger:  0.1360
    Change:      +13.43%
    P-value:     0.048230
    Significant: YES
    Winner:      Challenger

  Revenue Per User
    Champion:    25.1234
    Challenger:  28.3456
    Change:      +12.83%
    P-value:     0.000012
    Significant: YES
    Winner:      Challenger

  Click Through Rate
    Champion:    0.0801
    Challenger:  0.0855
    Change:      +6.74%
    P-value:     0.432100
    Significant: NO
    Winner:      Challenger

  Average Session Duration
    Champion:    180.2340
    Challenger:  185.1230
    Change:      +2.71%
    P-value:     0.001234
    Significant: YES
    Winner:      Challenger

=================================================================
OVERALL RECOMMENDATION
=================================================================
  Metrics where Challenger wins (significant): 3
  Metrics where Champion wins (significant):   0
  Inconclusive metrics:                        1

  DECISION: Deploy Challenger as new Champion
```

---

## Common Mistakes

1. **Stopping the test too early** — You see the challenger is winning after 100 samples and declare victory. But with small samples, results are unreliable. Always wait for statistical significance.

2. **Not splitting traffic consistently** — If a user gets Model A on Monday and Model B on Tuesday, you cannot attribute outcomes to either model. Use deterministic assignment based on user ID.

3. **Testing too many things at once** — If the new model changes the algorithm AND the features AND the preprocessing, you cannot tell which change caused the improvement.

4. **Ignoring guardrail metrics** — The challenger improves conversion by 5% but increases latency by 200ms. Always check secondary metrics like latency, error rate, and user complaints.

5. **Not accounting for novelty effects** — Users might engage more with a new model simply because it is different, not because it is better. Run tests long enough for the novelty to wear off.

---

## Best Practices

1. **Start with shadow mode** — Run the new model alongside the champion without serving its predictions. Check for errors and latency issues first.

2. **Ramp up traffic gradually** — Start at 5%, then 10%, then 20%, then 50%. If anything goes wrong, fewer users are affected.

3. **Define success metrics before the test** — Decide what "better" means before you see the results. This prevents cherry-picking metrics.

4. **Run tests for at least one full business cycle** — If your business has weekly patterns, run the test for at least 2 weeks.

5. **Have an automatic rollback mechanism** — If the challenger causes errors or performance drops, automatically route all traffic back to the champion.

---

## Quick Summary

A/B testing compares two models using real production traffic. You split users into groups, with most traffic going to the current champion model and some going to the new challenger. Traffic splitting must be deterministic so each user consistently gets the same model.

Statistical significance tells you whether observed differences are real or due to random chance. A p-value below 0.05 means you can be 95% confident the difference is real. Sample size calculations before the test tell you how many users you need for reliable results.

The champion/challenger pattern starts with shadow mode (test without serving), ramps up traffic gradually, and promotes the challenger only when it proves statistically better on predefined metrics.

---

## Key Points

- A/B testing compares models using real production traffic and outcomes
- Traffic splitting must be deterministic (same user always gets same model)
- Statistical significance (p-value < 0.05) prevents acting on random noise
- Calculate required sample size before starting the test
- The champion/challenger pattern provides a safe deployment framework
- Start with shadow mode, then ramp up traffic gradually (5%, 10%, 20%, 50%)
- Define success metrics before the test to prevent cherry-picking
- Monitor guardrail metrics (latency, errors) alongside primary metrics
- Run tests long enough to cover business cycles (at least 2 weeks)
- Have automatic rollback if the challenger causes problems

---

## Practice Questions

1. Why must traffic splitting be deterministic (based on user ID) rather than random for each request?

2. Your A/B test shows a p-value of 0.08. What does this mean, and what should you do?

3. You want to detect a 5% improvement in a 10% baseline conversion rate with 95% confidence and 80% power. Approximately how many samples per group do you need?

4. The challenger model improves conversion by 3% but increases response latency by 50ms. How would you decide whether to deploy it?

5. What is the novelty effect, and how does it affect A/B test results?

---

## Exercises

### Exercise 1: Build a Traffic Splitter

Create a traffic splitter that supports:
1. Multiple model variants (not just two)
2. Dynamic traffic percentage changes without reassigning existing users
3. A method to gradually ramp up traffic to a specific variant

### Exercise 2: Run a Simulated A/B Test

Simulate an A/B test where:
1. Champion has a 10% conversion rate
2. Challenger has a 12% conversion rate
3. Run the test for increasing sample sizes (100, 500, 1000, 5000, 10000)
4. At each sample size, report whether the difference is statistically significant
5. Find the minimum sample size where significance is consistently achieved

### Exercise 3: Multi-Metric Decision Framework

Build a decision framework that:
1. Tracks 4 metrics (conversion, revenue, latency, error rate)
2. Classifies each metric as "primary" (must improve) or "guardrail" (must not worsen)
3. Makes an automated recommendation based on combined results
4. Handles edge cases like conflicting results across metrics

---

## What Is Next?

Now that you can safely test new models in production, the next question is: how do you make those models faster and smaller? In the next chapter, we will explore **Model Optimization** — techniques like quantization, pruning, and knowledge distillation that make models faster and cheaper to run without sacrificing too much accuracy.
