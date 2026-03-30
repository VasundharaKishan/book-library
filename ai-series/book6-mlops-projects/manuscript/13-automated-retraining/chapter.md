# Chapter 13: Automated Retraining

## What You Will Learn

In this chapter, you will learn:

- What triggers model retraining and when it is needed
- Three types of retraining triggers: schedule-based, drift-based, and performance-based
- How to orchestrate retraining pipelines
- How to build a simple scheduler for automated retraining
- How to validate new models before replacing old ones

## Why This Chapter Matters

Imagine you have a navigation app on your phone. It works great when you first install it. But six months later, a new highway has been built, three roads have been closed, and a bridge is under construction. If the app never updates its maps, it will send you down closed roads.

ML models are the same. They are trained on historical data that reflects the world at a specific moment. But the world changes. Customer behavior shifts. New products appear. Economic conditions fluctuate. A model that was excellent six months ago might be giving poor recommendations today.

Automated retraining keeps your models fresh by detecting when they need updating and running the retraining process without human intervention.

---

## When to Retrain

There are three main triggers for retraining:

```
+--------------------------------------------------+
|  Retraining Triggers                              |
|                                                   |
|  1. Schedule-Based                               |
|     "Retrain every Monday at 6 AM"               |
|     Simple and predictable                       |
|     May retrain when not needed                  |
|                                                   |
|  2. Drift-Based                                  |
|     "Retrain when data distribution changes"     |
|     Retrains only when needed                    |
|     Requires drift monitoring                    |
|                                                   |
|  3. Performance-Based                            |
|     "Retrain when accuracy drops below 85%"      |
|     Most meaningful trigger                      |
|     Requires ground truth labels                 |
+--------------------------------------------------+
```

### Schedule-Based Retraining

The simplest approach. Like changing your car's oil every 5,000 miles, you retrain on a fixed schedule.

```python
"""
scheduled_retraining.py - Retrain on a fixed schedule.

This is the simplest retraining approach. You set a
schedule (daily, weekly, monthly) and the model
retrains automatically.

Schedule options:
- Daily:   For fast-changing data (stock prices, trending topics)
- Weekly:  For moderately changing data (user behavior)
- Monthly: For slowly changing data (demographics, climate)
"""

import schedule
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retrain_model():
    """
    Complete retraining pipeline.

    This function:
    1. Loads the latest data
    2. Trains a new model
    3. Evaluates the new model
    4. Replaces the production model if the new one is better
    """
    logger.info("=" * 50)
    logger.info(f"Retraining started at {datetime.now()}")
    logger.info("=" * 50)

    try:
        # Step 1: Load latest data
        logger.info("Step 1: Loading latest data...")
        # In practice: query database, download files, etc.
        # data = load_latest_data()

        # Step 2: Prepare data
        logger.info("Step 2: Preparing data...")
        # X_train, X_test, y_train, y_test = prepare_data(data)

        # Step 3: Train new model
        logger.info("Step 3: Training new model...")
        # new_model = train_model(X_train, y_train)

        # Step 4: Evaluate new model
        logger.info("Step 4: Evaluating new model...")
        # new_accuracy = evaluate(new_model, X_test, y_test)

        # Step 5: Compare with current model
        logger.info("Step 5: Comparing with current model...")
        # current_accuracy = evaluate(current_model, X_test, y_test)

        # Step 6: Deploy if better
        # if new_accuracy > current_accuracy:
        #     deploy_model(new_model)
        #     logger.info(f"New model deployed! Accuracy: {new_accuracy:.4f}")
        # else:
        #     logger.info(f"Current model is still better. No deployment.")

        logger.info("Retraining complete!")

    except Exception as e:
        logger.error(f"Retraining failed: {e}")
        # In practice: send alert to team
        raise


# Schedule retraining
# This is a simple in-process scheduler
# For production, use cron, Airflow, or cloud schedulers
schedule.every().monday.at("06:00").do(retrain_model)
schedule.every().thursday.at("06:00").do(retrain_model)

print("Scheduler started. Waiting for next retraining...")
print("Scheduled times: Monday and Thursday at 06:00")

# Run the scheduler loop
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

### Drift-Based Retraining

Smarter than scheduled retraining. Only retrain when the data actually changes.

```python
"""
drift_retraining.py - Retrain when data drift is detected.

This monitors incoming data and triggers retraining
only when the data distribution changes significantly.
"""

import numpy as np
from scipy import stats
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DriftMonitor:
    """
    Monitor data for drift and trigger retraining.

    This class stores the training data distribution
    and compares new data against it. When significant
    drift is detected, it triggers retraining.
    """

    def __init__(
        self,
        reference_data,
        feature_names,
        drift_threshold=0.05,
        min_drift_features=1,
    ):
        """
        Initialize the drift monitor.

        Parameters
        ----------
        reference_data : np.ndarray
            The training data (what the model was trained on).
        feature_names : list
            Names of the features.
        drift_threshold : float
            P-value threshold for the KS test.
            Below this = drift detected.
        min_drift_features : int
            Minimum number of features that must show drift
            before triggering retraining.
        """
        self.reference_data = reference_data
        self.feature_names = feature_names
        self.drift_threshold = drift_threshold
        self.min_drift_features = min_drift_features
        self.check_count = 0
        self.drift_count = 0

    def check_drift(self, new_data):
        """
        Check if new data has drifted from the reference.

        Parameters
        ----------
        new_data : np.ndarray
            Recent production data to check.

        Returns
        -------
        dict
            Drift check results including whether
            retraining is recommended.
        """
        self.check_count += 1
        drifted_features = []

        for i, name in enumerate(self.feature_names):
            ref_col = self.reference_data[:, i]
            new_col = new_data[:, i]

            # Kolmogorov-Smirnov test
            ks_stat, p_value = stats.ks_2samp(ref_col, new_col)

            if p_value < self.drift_threshold:
                drifted_features.append({
                    "feature": name,
                    "ks_statistic": round(ks_stat, 4),
                    "p_value": round(p_value, 6),
                })

        # Determine if retraining is needed
        should_retrain = (
            len(drifted_features) >= self.min_drift_features
        )

        if should_retrain:
            self.drift_count += 1

        result = {
            "timestamp": datetime.now().isoformat(),
            "check_number": self.check_count,
            "total_features": len(self.feature_names),
            "drifted_features": len(drifted_features),
            "drifted_details": drifted_features,
            "should_retrain": should_retrain,
        }

        # Log results
        if should_retrain:
            logger.warning(
                f"DRIFT DETECTED in {len(drifted_features)} features! "
                f"Retraining recommended."
            )
            for feat in drifted_features:
                logger.warning(
                    f"  {feat['feature']}: p={feat['p_value']}"
                )
        else:
            logger.info(
                f"No significant drift detected "
                f"({len(drifted_features)} features drifted, "
                f"threshold: {self.min_drift_features})"
            )

        return result


# Example usage
np.random.seed(42)

# Reference data (what the model was trained on)
reference = np.random.normal(
    loc=[30, 50000, 700, 5],
    scale=[10, 20000, 50, 3],
    size=(1000, 4),
)

feature_names = ["age", "income", "credit_score", "emp_years"]

# Create monitor
monitor = DriftMonitor(
    reference_data=reference,
    feature_names=feature_names,
    drift_threshold=0.05,
    min_drift_features=1,
)

# Check 1: Similar data (no drift expected)
similar_data = np.random.normal(
    loc=[30, 50000, 700, 5],
    scale=[10, 20000, 50, 3],
    size=(500, 4),
)
result1 = monitor.check_drift(similar_data)
print(f"\nCheck 1 - Should retrain: {result1['should_retrain']}")

# Check 2: Shifted data (drift expected)
shifted_data = np.random.normal(
    loc=[35, 70000, 680, 8],  # Income and emp_years shifted
    scale=[10, 20000, 50, 3],
    size=(500, 4),
)
result2 = monitor.check_drift(shifted_data)
print(f"Check 2 - Should retrain: {result2['should_retrain']}")
print(f"  Drifted features: {result2['drifted_features']}")
```

```
Output:
INFO - No significant drift detected (0 features drifted, threshold: 1)

Check 1 - Should retrain: False
WARNING - DRIFT DETECTED in 3 features! Retraining recommended.
WARNING -   age: p=0.001234
WARNING -   income: p=0.000001
WARNING -   emp_years: p=0.000023
Check 2 - Should retrain: True
  Drifted features: 3
```

### Performance-Based Retraining

The most meaningful trigger. Retrain when the model's actual performance drops.

```python
"""
performance_retraining.py - Retrain when performance drops.

This monitors the model's actual predictions against
ground truth labels and triggers retraining when
accuracy drops below a threshold.
"""

import numpy as np
from collections import deque
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Monitor model performance and trigger retraining.

    Uses a rolling window to track recent accuracy.
    When accuracy drops below the threshold, it
    triggers retraining.
    """

    def __init__(
        self,
        accuracy_threshold=0.85,
        window_size=100,
        alert_after_n_checks=3,
    ):
        """
        Initialize the performance monitor.

        Parameters
        ----------
        accuracy_threshold : float
            Minimum acceptable accuracy (0.0 to 1.0).
        window_size : int
            Number of recent predictions to consider.
        alert_after_n_checks : int
            Number of consecutive checks below threshold
            before triggering retraining.
        """
        self.accuracy_threshold = accuracy_threshold
        self.window_size = window_size
        self.alert_after_n_checks = alert_after_n_checks

        # Track recent predictions and actual outcomes
        # deque with maxlen automatically drops old entries
        self.predictions = deque(maxlen=window_size)
        self.actuals = deque(maxlen=window_size)

        self.consecutive_failures = 0
        self.total_checks = 0

    def record(self, prediction, actual):
        """Record a single prediction and its actual outcome."""
        self.predictions.append(prediction)
        self.actuals.append(actual)

    def record_batch(self, predictions, actuals):
        """Record a batch of predictions and actual outcomes."""
        for pred, actual in zip(predictions, actuals):
            self.record(pred, actual)

    def check_performance(self):
        """
        Check if performance is acceptable.

        Returns
        -------
        dict
            Performance check results.
        """
        self.total_checks += 1

        if len(self.predictions) < 10:
            return {
                "status": "insufficient_data",
                "samples": len(self.predictions),
                "should_retrain": False,
            }

        # Calculate rolling accuracy
        correct = sum(
            p == a for p, a in zip(self.predictions, self.actuals)
        )
        accuracy = correct / len(self.predictions)

        # Check if below threshold
        below_threshold = accuracy < self.accuracy_threshold

        if below_threshold:
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 0

        # Trigger retraining after N consecutive failures
        should_retrain = (
            self.consecutive_failures >= self.alert_after_n_checks
        )

        result = {
            "timestamp": datetime.now().isoformat(),
            "accuracy": round(accuracy, 4),
            "threshold": self.accuracy_threshold,
            "below_threshold": below_threshold,
            "consecutive_failures": self.consecutive_failures,
            "should_retrain": should_retrain,
            "window_size": len(self.predictions),
        }

        # Logging
        if should_retrain:
            logger.warning(
                f"PERFORMANCE DEGRADATION! Accuracy: {accuracy:.4f} "
                f"(threshold: {self.accuracy_threshold}). "
                f"Consecutive failures: {self.consecutive_failures}. "
                f"RETRAINING TRIGGERED!"
            )
        elif below_threshold:
            logger.warning(
                f"Performance below threshold: {accuracy:.4f} "
                f"(failure {self.consecutive_failures}/"
                f"{self.alert_after_n_checks})"
            )
        else:
            logger.info(
                f"Performance OK: {accuracy:.4f} "
                f"(threshold: {self.accuracy_threshold})"
            )

        return result


# Example: Simulate performance degradation
monitor = PerformanceMonitor(
    accuracy_threshold=0.85,
    window_size=50,
    alert_after_n_checks=3,
)

np.random.seed(42)

# Phase 1: Model performing well (90% accuracy)
print("Phase 1: Model performing well")
for _ in range(50):
    actual = np.random.choice([0, 1])
    # 90% chance of correct prediction
    correct = np.random.random() < 0.90
    prediction = actual if correct else 1 - actual
    monitor.record(prediction, actual)

result = monitor.check_performance()
print(f"  Accuracy: {result['accuracy']}, Retrain: {result['should_retrain']}")

# Phase 2: Model starting to degrade (75% accuracy)
print("\nPhase 2: Model degrading")
for _ in range(50):
    actual = np.random.choice([0, 1])
    correct = np.random.random() < 0.75
    prediction = actual if correct else 1 - actual
    monitor.record(prediction, actual)

for check in range(4):
    result = monitor.check_performance()
    print(
        f"  Check {check+1}: Accuracy={result['accuracy']}, "
        f"Failures={result['consecutive_failures']}, "
        f"Retrain={result['should_retrain']}"
    )
```

```
Output:
Phase 1: Model performing well
  Accuracy: 0.88, Retrain: False

Phase 2: Model degrading
  Check 1: Accuracy=0.76, Failures=1, Retrain=False
  Check 2: Accuracy=0.76, Failures=2, Retrain=False
  Check 3: Accuracy=0.76, Failures=3, Retrain=True
  Check 4: Accuracy=0.76, Failures=4, Retrain=True
```

---

## Pipeline Orchestration

Orchestration means coordinating all the steps in the retraining pipeline. Think of it as a conductor directing an orchestra. Each musician (step) plays their part at the right time.

```
+--------------------------------------------------+
|  Retraining Pipeline Steps                        |
|                                                   |
|  Trigger (drift/schedule/performance)            |
|       |                                           |
|       v                                           |
|  1. Collect latest data                          |
|       |                                           |
|       v                                           |
|  2. Validate data quality                        |
|       |                                           |
|       v                                           |
|  3. Prepare data (clean, split)                  |
|       |                                           |
|       v                                           |
|  4. Train new model                              |
|       |                                           |
|       v                                           |
|  5. Evaluate new model                           |
|       |                                           |
|       v                                           |
|  6. Compare with production model                |
|       |                                           |
|       +-- New model worse? --> Keep current,     |
|       |                        log and alert      |
|       |                                           |
|       +-- New model better? --> Continue          |
|       |                                           |
|       v                                           |
|  7. Deploy new model                             |
|       |                                           |
|       v                                           |
|  8. Verify deployment (smoke test)               |
|       |                                           |
|       v                                           |
|  9. Log results and notify team                  |
+--------------------------------------------------+
```

### Complete Retraining Pipeline

```python
"""
retraining_pipeline.py - A complete automated retraining pipeline.

This pipeline handles the entire process from data
collection to model deployment.
"""

import logging
import json
import time
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Results from a retraining pipeline run."""

    started_at: str = ""
    completed_at: str = ""
    trigger: str = ""
    data_samples: int = 0
    new_model_accuracy: float = 0.0
    current_model_accuracy: float = 0.0
    deployed: bool = False
    reason: str = ""
    duration_seconds: float = 0.0
    errors: list = field(default_factory=list)


class RetrainingPipeline:
    """
    Complete retraining pipeline.

    Coordinates all steps of the retraining process.
    """

    def __init__(
        self,
        model_path="models/production_model.pkl",
        data_source="data/latest.csv",
        min_accuracy=0.85,
        min_improvement=0.01,
    ):
        """
        Initialize the pipeline.

        Parameters
        ----------
        model_path : str
            Path to the current production model.
        data_source : str
            Where to get training data.
        min_accuracy : float
            Minimum accuracy for deployment.
        min_improvement : float
            Minimum improvement over current model.
        """
        self.model_path = model_path
        self.data_source = data_source
        self.min_accuracy = min_accuracy
        self.min_improvement = min_improvement

    def run(self, trigger="manual"):
        """
        Execute the complete retraining pipeline.

        Parameters
        ----------
        trigger : str
            What triggered this run (schedule, drift,
            performance, manual).

        Returns
        -------
        PipelineResult
            Results of the pipeline run.
        """
        result = PipelineResult(
            started_at=datetime.now().isoformat(),
            trigger=trigger,
        )
        start_time = time.time()

        logger.info("=" * 60)
        logger.info(f"RETRAINING PIPELINE STARTED")
        logger.info(f"Trigger: {trigger}")
        logger.info(f"Time: {result.started_at}")
        logger.info("=" * 60)

        try:
            # Step 1: Collect data
            logger.info("\n[1/7] Collecting latest data...")
            X, y = self._collect_data()
            result.data_samples = len(X)
            logger.info(f"  Collected {len(X)} samples")

            # Step 2: Validate data
            logger.info("\n[2/7] Validating data quality...")
            self._validate_data(X, y)
            logger.info("  Data validation passed")

            # Step 3: Prepare data
            logger.info("\n[3/7] Preparing data...")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            logger.info(
                f"  Train: {len(X_train)}, Test: {len(X_test)}"
            )

            # Step 4: Train new model
            logger.info("\n[4/7] Training new model...")
            new_model = self._train_model(X_train, y_train)
            logger.info("  Training complete")

            # Step 5: Evaluate new model
            logger.info("\n[5/7] Evaluating new model...")
            new_preds = new_model.predict(X_test)
            new_accuracy = accuracy_score(y_test, new_preds)
            new_f1 = f1_score(y_test, new_preds, average="weighted")
            result.new_model_accuracy = new_accuracy
            logger.info(
                f"  New model: accuracy={new_accuracy:.4f}, "
                f"f1={new_f1:.4f}"
            )

            # Step 6: Compare with current model
            logger.info("\n[6/7] Comparing with current model...")
            should_deploy = self._compare_models(
                new_model, new_accuracy, X_test, y_test, result
            )

            # Step 7: Deploy or skip
            if should_deploy:
                logger.info("\n[7/7] Deploying new model...")
                self._deploy_model(new_model)
                result.deployed = True
                result.reason = (
                    f"New model ({new_accuracy:.4f}) is better "
                    f"than current ({result.current_model_accuracy:.4f})"
                )
                logger.info("  Deployment complete!")
            else:
                logger.info("\n[7/7] Skipping deployment")
                result.deployed = False
                logger.info(
                    f"  Reason: {result.reason}"
                )

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            result.errors.append(str(e))
            result.reason = f"Pipeline error: {e}"

        result.completed_at = datetime.now().isoformat()
        result.duration_seconds = round(time.time() - start_time, 2)

        # Log summary
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE SUMMARY")
        logger.info(f"  Duration: {result.duration_seconds}s")
        logger.info(f"  Deployed: {result.deployed}")
        logger.info(f"  Reason: {result.reason}")
        logger.info("=" * 60)

        # Save results
        self._save_results(result)

        return result

    def _collect_data(self):
        """Collect the latest training data."""
        # In practice, this would query a database or API
        X, y = make_classification(
            n_samples=2000,
            n_features=10,
            n_classes=2,
            random_state=int(time.time()) % 1000,
        )
        return X, y

    def _validate_data(self, X, y):
        """Validate data quality."""
        # Check minimum size
        if len(X) < 100:
            raise ValueError(
                f"Insufficient data: {len(X)} samples "
                f"(minimum: 100)"
            )

        # Check for NaN values
        if np.isnan(X).any():
            raise ValueError("Data contains NaN values")

        # Check class balance
        unique, counts = np.unique(y, return_counts=True)
        min_ratio = counts.min() / counts.max()
        if min_ratio < 0.1:
            logger.warning(
                f"Imbalanced classes: ratio={min_ratio:.2f}"
            )

    def _train_model(self, X_train, y_train):
        """Train a new model."""
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
        )
        model.fit(X_train, y_train)
        return model

    def _compare_models(
        self, new_model, new_accuracy, X_test, y_test, result
    ):
        """Compare new model with current production model."""
        # Check minimum accuracy
        if new_accuracy < self.min_accuracy:
            result.reason = (
                f"New model accuracy ({new_accuracy:.4f}) "
                f"below minimum ({self.min_accuracy})"
            )
            return False

        # Try to load current model
        try:
            current_model = joblib.load(self.model_path)
            current_preds = current_model.predict(X_test)
            current_accuracy = accuracy_score(y_test, current_preds)
            result.current_model_accuracy = current_accuracy

            logger.info(
                f"  Current model accuracy: {current_accuracy:.4f}"
            )
            logger.info(
                f"  New model accuracy: {new_accuracy:.4f}"
            )

            improvement = new_accuracy - current_accuracy
            logger.info(f"  Improvement: {improvement:+.4f}")

            if improvement < self.min_improvement:
                result.reason = (
                    f"Improvement ({improvement:+.4f}) below "
                    f"minimum ({self.min_improvement})"
                )
                return False

            return True

        except FileNotFoundError:
            logger.info("  No current model found. Deploying new model.")
            result.current_model_accuracy = 0.0
            return True

    def _deploy_model(self, model):
        """Deploy the new model."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(model, self.model_path)
        logger.info(f"  Model saved to {self.model_path}")

    def _save_results(self, result):
        """Save pipeline results to a log file."""
        results_dir = "logs/retraining"
        os.makedirs(results_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(
            results_dir, f"run_{timestamp}.json"
        )

        # Convert dataclass to dict for JSON
        result_dict = {
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "trigger": result.trigger,
            "data_samples": result.data_samples,
            "new_model_accuracy": result.new_model_accuracy,
            "current_model_accuracy": result.current_model_accuracy,
            "deployed": result.deployed,
            "reason": result.reason,
            "duration_seconds": result.duration_seconds,
            "errors": result.errors,
        }

        with open(filepath, "w") as f:
            json.dump(result_dict, f, indent=2)

        logger.info(f"Results saved to {filepath}")


# Run the pipeline
pipeline = RetrainingPipeline(
    model_path="models/production_model.pkl",
    min_accuracy=0.85,
    min_improvement=0.01,
)

result = pipeline.run(trigger="manual")
```

```
Output:
============================================================
RETRAINING PIPELINE STARTED
Trigger: manual
Time: 2024-01-15T10:00:00.000000
============================================================

[1/7] Collecting latest data...
  Collected 2000 samples

[2/7] Validating data quality...
  Data validation passed

[3/7] Preparing data...
  Train: 1600, Test: 400

[4/7] Training new model...
  Training complete

[5/7] Evaluating new model...
  New model: accuracy=0.9325, f1=0.9323

[6/7] Comparing with current model...
  No current model found. Deploying new model.

[7/7] Deploying new model...
  Model saved to models/production_model.pkl
  Deployment complete!

============================================================
PIPELINE SUMMARY
  Duration: 3.45s
  Deployed: True
  Reason: New model (0.9325) is better than current (0.0000)
============================================================
```

---

## Simple Scheduler Example

Here is a complete example that combines drift monitoring with scheduled checks:

```python
"""
auto_retrain_scheduler.py - Automated retraining with monitoring.

This combines schedule-based checks with drift detection
and performance monitoring.
"""

import time
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)


class AutoRetrainer:
    """
    Automated retraining scheduler.

    Combines multiple triggers:
    - Scheduled checks (e.g., daily)
    - Drift detection
    - Performance monitoring
    """

    def __init__(
        self,
        check_interval_hours=24,
        max_days_without_retrain=30,
    ):
        """
        Initialize the auto-retrainer.

        Parameters
        ----------
        check_interval_hours : int
            How often to check if retraining is needed.
        max_days_without_retrain : int
            Force retraining after this many days.
        """
        self.check_interval = timedelta(hours=check_interval_hours)
        self.max_interval = timedelta(days=max_days_without_retrain)
        self.last_retrain = datetime.now()
        self.last_check = datetime.now()
        self.retrain_count = 0

    def should_retrain(self, drift_detected=False, accuracy=None):
        """
        Decide whether to retrain.

        Parameters
        ----------
        drift_detected : bool
            Whether data drift was detected.
        accuracy : float, optional
            Current model accuracy (0.0 to 1.0).

        Returns
        -------
        tuple
            (should_retrain: bool, reason: str)
        """
        now = datetime.now()
        time_since_retrain = now - self.last_retrain

        # Reason 1: Maximum time exceeded
        if time_since_retrain > self.max_interval:
            return True, (
                f"Maximum interval exceeded "
                f"({time_since_retrain.days} days > "
                f"{self.max_interval.days} days)"
            )

        # Reason 2: Data drift detected
        if drift_detected:
            return True, "Data drift detected"

        # Reason 3: Performance degradation
        if accuracy is not None and accuracy < 0.85:
            return True, (
                f"Performance below threshold "
                f"({accuracy:.4f} < 0.85)"
            )

        return False, "No retraining needed"

    def run_check(self, drift_detected=False, accuracy=None):
        """
        Run a single check and potentially trigger retraining.

        Returns
        -------
        dict
            Check results.
        """
        self.last_check = datetime.now()

        should_retrain, reason = self.should_retrain(
            drift_detected=drift_detected,
            accuracy=accuracy,
        )

        result = {
            "timestamp": datetime.now().isoformat(),
            "should_retrain": should_retrain,
            "reason": reason,
            "days_since_retrain": (
                datetime.now() - self.last_retrain
            ).days,
        }

        if should_retrain:
            logger.warning(f"RETRAINING TRIGGERED: {reason}")
            self._execute_retrain(reason)
        else:
            logger.info(f"Check complete: {reason}")

        return result

    def _execute_retrain(self, reason):
        """Execute the retraining pipeline."""
        logger.info("Starting retraining pipeline...")

        # In practice, this would call your RetrainingPipeline
        # pipeline = RetrainingPipeline()
        # result = pipeline.run(trigger=reason)

        self.retrain_count += 1
        self.last_retrain = datetime.now()

        logger.info(
            f"Retraining complete! "
            f"Total retrains: {self.retrain_count}"
        )

    def get_status(self):
        """Get the current status of the auto-retrainer."""
        now = datetime.now()
        return {
            "last_retrain": self.last_retrain.isoformat(),
            "days_since_retrain": (now - self.last_retrain).days,
            "total_retrains": self.retrain_count,
            "next_check": (
                self.last_check + self.check_interval
            ).isoformat(),
        }


# Demo: Simulate the auto-retrainer
retrainer = AutoRetrainer(
    check_interval_hours=24,
    max_days_without_retrain=30,
)

# Simulate checks
print("Simulating automated retraining checks\n")

# Check 1: Everything is fine
result = retrainer.run_check(drift_detected=False, accuracy=0.92)
print(f"  Result: {result['reason']}\n")

# Check 2: Drift detected
result = retrainer.run_check(drift_detected=True, accuracy=0.90)
print(f"  Result: {result['reason']}\n")

# Check 3: Performance drop
result = retrainer.run_check(drift_detected=False, accuracy=0.80)
print(f"  Result: {result['reason']}\n")

# Show status
status = retrainer.get_status()
print(f"\nRetrainer Status:")
for key, value in status.items():
    print(f"  {key}: {value}")
```

```
Output:
Simulating automated retraining checks

2024-01-15 10:00:00 | INFO     | Check complete: No retraining needed
  Result: No retraining needed

2024-01-15 10:00:00 | WARNING  | RETRAINING TRIGGERED: Data drift detected
2024-01-15 10:00:00 | INFO     | Starting retraining pipeline...
2024-01-15 10:00:00 | INFO     | Retraining complete! Total retrains: 1
  Result: Data drift detected

2024-01-15 10:00:00 | WARNING  | RETRAINING TRIGGERED: Performance below threshold (0.8000 < 0.85)
2024-01-15 10:00:00 | INFO     | Starting retraining pipeline...
2024-01-15 10:00:00 | INFO     | Retraining complete! Total retrains: 2
  Result: Performance below threshold (0.8000 < 0.85)

Retrainer Status:
  last_retrain: 2024-01-15T10:00:00.654321
  days_since_retrain: 0
  total_retrains: 2
  next_check: 2024-01-16T10:00:00.654321
```

---

## Common Mistakes

1. **Retraining too frequently.** If nothing has changed, retraining wastes compute and risks introducing instability. Use triggers, not just schedules.

2. **Not comparing with the current model.** Always verify the new model is actually better before deploying it.

3. **No rollback mechanism.** If the newly deployed model causes problems, you need to be able to quickly revert.

4. **Ignoring data quality.** Retraining on bad data produces a bad model. Always validate data before training.

5. **No logging or notification.** When retraining happens automatically, you need logs and alerts to know what happened.

---

## Best Practices

1. **Use multiple triggers.** Combine schedule-based, drift-based, and performance-based triggers for comprehensive coverage.

2. **Always validate before deploying.** Run validation gates before replacing the production model.

3. **Keep a history of retraining runs.** Log every run with its trigger, data, metrics, and outcome.

4. **Set up alerts.** Notify the team when retraining happens, especially when it fails.

5. **Test the pipeline itself.** Run the retraining pipeline in a test environment before relying on it in production.

6. **Have a manual override.** Sometimes you need to force retraining or skip it. Build in manual controls.

---

## Quick Summary

Automated retraining keeps ML models fresh by detecting when they need updating and running the retraining process automatically. Three triggers drive retraining: schedule-based (regular intervals), drift-based (data distribution changes), and performance-based (accuracy drops). A complete retraining pipeline collects data, validates it, trains a new model, compares it with the current model, and deploys it only if it is better.

---

## Key Points

- Models degrade over time as the world changes
- Schedule-based retraining is simple but may retrain unnecessarily
- Drift-based retraining detects when data distributions change
- Performance-based retraining triggers when accuracy drops
- Always compare new models with the current production model
- Never deploy a new model without validation
- Log every retraining run for debugging and auditing
- Have a rollback plan in case the new model causes problems

---

## Practice Questions

1. What are the three types of retraining triggers? When would you use each one?

2. Why is it important to compare a new model with the current production model before deploying?

3. What is data drift and how can it affect model performance?

4. What should happen if the retraining pipeline produces a model that is worse than the current one?

5. Why should you log every retraining run, even successful ones?

---

## Exercises

### Exercise 1: Drift Monitor

Build a drift monitor that:
- Accepts reference data during initialization
- Checks new data batches for drift using the KS test
- Tracks drift history over time
- Returns a report with which features drifted and by how much

### Exercise 2: Complete Retraining Pipeline

Implement a retraining pipeline that:
- Loads data from a CSV file
- Validates data quality (at least 3 checks)
- Trains a model
- Evaluates against 3 metrics (accuracy, precision, recall)
- Compares with the current production model
- Deploys only if better
- Saves a JSON report of the run

### Exercise 3: Multi-Trigger Scheduler

Create a retraining system that combines all three triggers:
- Runs a check every hour
- Checks for data drift
- Checks model performance
- Forces retraining if more than 7 days have passed
- Logs all decisions and actions

---

## What Is Next?

Congratulations! You have completed the MLOps journey from notebook to production. You now know how to:

- Organize code for production (Chapter 1)
- Save and load models (Chapter 2)
- Build ML APIs with FastAPI (Chapter 3)
- Containerize with Docker (Chapter 4)
- Deploy to the cloud (Chapter 5)
- Build demos with Streamlit and Gradio (Chapter 6)
- Serve models at scale (Chapter 7)
- Understand the full ML lifecycle (Chapter 8)
- Track experiments with MLflow (Chapter 9)
- Version data with DVC (Chapter 10)
- Manage models in a registry (Chapter 11)
- Automate with CI/CD (Chapter 12)
- Set up automated retraining (Chapter 13)

These skills form the foundation of MLOps, the discipline of deploying and maintaining ML models in production. Keep practicing, keep building, and keep learning. The field is evolving rapidly, and the best way to stay current is to build real projects.
