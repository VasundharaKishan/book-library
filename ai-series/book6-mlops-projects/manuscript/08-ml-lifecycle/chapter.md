# Chapter 8: The ML Lifecycle

## What You Will Learn

In this chapter, you will learn:

- What the ML lifecycle is and why it matters
- Each stage of the lifecycle: data collection, preparation, training, evaluation, deployment, monitoring, and retraining
- How these stages connect to form a continuous loop
- What happens at each stage and what can go wrong
- How to think about ML as an ongoing process, not a one-time project

## Why This Chapter Matters

Imagine you open a restaurant. You do not just cook one meal and declare success. You constantly buy fresh ingredients, try new recipes, check customer feedback, update the menu, and train new staff. Running a restaurant is a cycle, not a one-time event.

ML works the same way. Training a model is just one step in a much larger process. Data changes. User behavior shifts. The world evolves. A model that was great six months ago might be making bad predictions today. Understanding the full ML lifecycle helps you build systems that stay healthy over time.

---

## The Full ML Lifecycle

```
+------------------------------------------------------------------+
|                    The ML Lifecycle                                |
|                                                                    |
|     +------------------+                                          |
|     | 1. Data          |                                          |
|     |    Collection    |                                          |
|     +--------+---------+                                          |
|              |                                                    |
|              v                                                    |
|     +--------+---------+                                          |
|     | 2. Data          |                                          |
|     |    Preparation   |                                          |
|     +--------+---------+                                          |
|              |                                                    |
|              v                                                    |
|     +--------+---------+                                          |
|     | 3. Model         |                                          |
|     |    Training      |                                          |
|     +--------+---------+                                          |
|              |                                                    |
|              v                                                    |
|     +--------+---------+                                          |
|     | 4. Model         |                                          |
|     |    Evaluation    |                                          |
|     +--------+---------+                                          |
|              |                                                    |
|              v                                                    |
|     +--------+---------+                                          |
|     | 5. Model         |                                          |
|     |    Deployment    |                                          |
|     +--------+---------+                                          |
|              |                                                    |
|              v                                                    |
|     +--------+---------+                                          |
|     | 6. Monitoring    |------> Problem detected?                 |
|     |                  |              |                            |
|     +--------+---------+              | Yes                       |
|              |                        v                           |
|              |               +--------+---------+                 |
|              |               | 7. Retraining    |                 |
|              |               +--------+---------+                 |
|              |                        |                           |
|              +<----- Back to Step 2 --+                           |
|                                                                    |
|  This is a LOOP, not a straight line!                             |
+------------------------------------------------------------------+
```

---

## Stage 1: Data Collection

Data collection is gathering the raw information your model will learn from. It is like collecting ingredients before cooking.

```
+--------------------------------------------------+
|  Data Collection Sources                          |
|                                                   |
|  Databases        -> Customer records, orders    |
|  APIs             -> Weather data, stock prices  |
|  User Interactions-> Clicks, searches, ratings   |
|  Sensors          -> IoT devices, cameras        |
|  Web Scraping     -> Product prices, reviews     |
|  Manual Labeling  -> Annotated images, text      |
|  Public Datasets  -> Kaggle, government data     |
+--------------------------------------------------+
```

### Key Questions

```python
"""
data_collection_checklist.py - Questions to ask about your data.

Before collecting data, answer these questions to
make sure you are collecting the right data.
"""

checklist = {
    "What problem are we solving?": {
        "example": "Predicting customer churn",
        "why": "Defines what data you need",
    },
    "What data do we already have?": {
        "example": "Customer purchase history, support tickets",
        "why": "Avoid collecting what you already have",
    },
    "What data do we still need?": {
        "example": "Customer satisfaction surveys, competitor pricing",
        "why": "Identify gaps in your data",
    },
    "How fresh does the data need to be?": {
        "example": "Last 12 months of transactions",
        "why": "Old data may not reflect current patterns",
    },
    "How much data do we need?": {
        "example": "At least 10,000 labeled examples",
        "why": "Too little data leads to poor models",
    },
    "Are there privacy or legal concerns?": {
        "example": "GDPR compliance for EU customers",
        "why": "Violations can result in fines and lawsuits",
    },
    "Is the data representative?": {
        "example": "Includes all customer segments, not just active ones",
        "why": "Biased data leads to biased models",
    },
}

print("Data Collection Checklist")
print("=" * 55)
for question, details in checklist.items():
    print(f"\n  Q: {question}")
    print(f"     Example: {details['example']}")
    print(f"     Why it matters: {details['why']}")
```

```
Output:
Data Collection Checklist
=======================================================

  Q: What problem are we solving?
     Example: Predicting customer churn
     Why it matters: Defines what data you need

  Q: What data do we already have?
     Example: Customer purchase history, support tickets
     Why it matters: Avoid collecting what you already have

  Q: What data do we still need?
     Example: Customer satisfaction surveys, competitor pricing
     Why it matters: Identify gaps in your data

  Q: How fresh does the data need to be?
     Example: Last 12 months of transactions
     Why it matters: Old data may not reflect current patterns

  Q: How much data do we need?
     Example: At least 10,000 labeled examples
     Why it matters: Too little data leads to poor models

  Q: Are there privacy or legal concerns?
     Example: GDPR compliance for EU customers
     Why it matters: Violations can result in fines and lawsuits

  Q: Is the data representative?
     Example: Includes all customer segments, not just active ones
     Why it matters: Biased data leads to biased models
```

---

## Stage 2: Data Preparation

Raw data is like raw ingredients. You cannot just throw them in a pan. You need to wash, chop, and measure them first. Data preparation transforms raw data into a format your model can learn from.

```
+--------------------------------------------------+
|  Data Preparation Steps                           |
|                                                   |
|  Raw Data                                        |
|    |                                              |
|    +--> Clean (fix errors, handle missing values)|
|    |                                              |
|    +--> Transform (scale, encode, normalize)     |
|    |                                              |
|    +--> Feature Engineering (create new features)|
|    |                                              |
|    +--> Split (train / validation / test)        |
|    |                                              |
|    v                                              |
|  Prepared Data (ready for training)              |
+--------------------------------------------------+
```

```python
"""
data_preparation.py - The data preparation stage.

This shows the typical steps in data preparation
with explanations of what each step does and why.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging

logger = logging.getLogger(__name__)


def prepare_data(df, target_column):
    """
    Complete data preparation pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        Raw data.
    target_column : str
        Name of the column we want to predict.

    Returns
    -------
    dict
        Prepared data and metadata.
    """
    logger.info(f"Starting data preparation: {len(df)} rows")
    steps_completed = []

    # Step 1: Handle missing values
    missing_before = df.isnull().sum().sum()
    if missing_before > 0:
        # Fill numeric columns with the median (middle value)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

        # Fill text columns with the most common value
        text_cols = df.select_dtypes(include=["object"]).columns
        for col in text_cols:
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)

        logger.info(f"Filled {missing_before} missing values")
        steps_completed.append("missing_values")

    # Step 2: Remove duplicates
    dupes = df.duplicated().sum()
    if dupes > 0:
        df = df.drop_duplicates()
        logger.info(f"Removed {dupes} duplicate rows")
        steps_completed.append("duplicates_removed")

    # Step 3: Encode categorical variables
    label_encoders = {}
    text_cols = df.select_dtypes(include=["object"]).columns
    text_cols = [c for c in text_cols if c != target_column]

    for col in text_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
        logger.info(f"Encoded column: {col}")
    steps_completed.append("encoding")

    # Step 4: Split features and target
    X = df.drop(target_column, axis=1)
    y = df[target_column]

    # Step 5: Split into train/validation/test sets
    # First split: 80% train+val, 20% test
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    # Second split: 75% train, 25% validation (of the 80%)
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=0.25, random_state=42
    )

    logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    steps_completed.append("split")

    # Step 6: Scale numeric features
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns,
        index=X_train.index,
    )
    X_val_scaled = pd.DataFrame(
        scaler.transform(X_val),
        columns=X_val.columns,
        index=X_val.index,
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns,
        index=X_test.index,
    )
    steps_completed.append("scaling")

    logger.info(f"Preparation complete. Steps: {steps_completed}")

    return {
        "X_train": X_train_scaled,
        "X_val": X_val_scaled,
        "X_test": X_test_scaled,
        "y_train": y_train,
        "y_val": y_val,
        "y_test": y_test,
        "scaler": scaler,
        "label_encoders": label_encoders,
        "steps": steps_completed,
    }
```

---

## Stage 3: Model Training

Training is where the model learns patterns from the data. It is like a student studying for an exam: they look at many examples and learn the rules.

```
+--------------------------------------------------+
|  Model Training                                   |
|                                                   |
|  Training Data -----> Algorithm -----> Model      |
|  (Examples)           (Learning)       (Knowledge)|
|                                                   |
|  The algorithm looks at thousands of examples    |
|  and figures out the patterns.                   |
|                                                   |
|  Input: age=25, income=30k -> churned=Yes        |
|  Input: age=45, income=90k -> churned=No         |
|  ...                                              |
|  (After seeing enough examples, the model learns)|
+--------------------------------------------------+
```

### Training Considerations

```python
"""
training_stage.py - Model training considerations.

This shows the key decisions you make during training.
"""

training_decisions = {
    "Model Selection": {
        "question": "Which algorithm should I use?",
        "options": [
            "Logistic Regression - Simple, interpretable",
            "Random Forest - Good default, handles many data types",
            "Gradient Boosting (XGBoost) - Often best accuracy",
            "Neural Network - Best for images, text, complex patterns",
        ],
        "tip": "Start simple. Try logistic regression first. "
               "Only use complex models if simple ones are not good enough.",
    },
    "Hyperparameter Tuning": {
        "question": "How do I configure the model?",
        "options": [
            "Grid Search - Try all combinations (slow but thorough)",
            "Random Search - Try random combinations (faster)",
            "Bayesian Optimization - Smart search (efficient)",
        ],
        "tip": "Random search with 50-100 trials is a good starting point.",
    },
    "Training Data Size": {
        "question": "How much data should I use?",
        "options": [
            "More data usually = better model",
            "Learning curves show when more data stops helping",
            "Start with all available data, reduce only if too slow",
        ],
        "tip": "Plot a learning curve to see if more data would help.",
    },
}

for topic, info in training_decisions.items():
    print(f"\n{topic}")
    print(f"  Question: {info['question']}")
    print(f"  Options:")
    for opt in info["options"]:
        print(f"    - {opt}")
    print(f"  Tip: {info['tip']}")
```

```
Output:

Model Selection
  Question: Which algorithm should I use?
  Options:
    - Logistic Regression - Simple, interpretable
    - Random Forest - Good default, handles many data types
    - Gradient Boosting (XGBoost) - Often best accuracy
    - Neural Network - Best for images, text, complex patterns
  Tip: Start simple. Try logistic regression first. Only use complex models if simple ones are not good enough.

Hyperparameter Tuning
  Question: How do I configure the model?
  Options:
    - Grid Search - Try all combinations (slow but thorough)
    - Random Search - Try random combinations (faster)
    - Bayesian Optimization - Smart search (efficient)
  Tip: Random search with 50-100 trials is a good starting point.

Training Data Size
  Question: How much data should I use?
  Options:
    - More data usually = better model
    - Learning curves show when more data stops helping
    - Start with all available data, reduce only if too slow
  Tip: Plot a learning curve to see if more data would help.
```

---

## Stage 4: Model Evaluation

Evaluation answers: "Is this model good enough?" You never trust a student's claim that they studied well. You give them an exam. Similarly, you test your model on data it has never seen before.

```
+--------------------------------------------------+
|  Evaluation: Three Types of Data                 |
|                                                   |
|  Training Data  -> Model learns from this        |
|  (60%)            Like studying from a textbook  |
|                                                   |
|  Validation Data -> Tune hyperparameters         |
|  (20%)             Like practice exams            |
|                                                   |
|  Test Data      -> Final evaluation              |
|  (20%)            Like the real exam              |
|                     (ONLY look at this once!)     |
+--------------------------------------------------+
```

```python
"""
evaluation_stage.py - Model evaluation metrics and checks.
"""

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
import numpy as np


def comprehensive_evaluation(model, X_test, y_test):
    """
    Run a comprehensive model evaluation.

    Returns metrics and checks for common problems.
    """
    predictions = model.predict(X_test)

    # Basic metrics
    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, average="weighted"),
        "recall": recall_score(y_test, predictions, average="weighted"),
        "f1": f1_score(y_test, predictions, average="weighted"),
    }

    # Confusion matrix
    cm = confusion_matrix(y_test, predictions)

    # Checks
    checks = []

    # Check 1: Is accuracy much better than random guessing?
    baseline_accuracy = max(
        np.mean(y_test == 0), np.mean(y_test == 1)
    )
    if metrics["accuracy"] > baseline_accuracy + 0.05:
        checks.append(("Better than baseline", "PASS"))
    else:
        checks.append(("Better than baseline", "FAIL"))

    # Check 2: Is the model not overfitting?
    train_accuracy = model.score(X_test, y_test)
    # In practice, compare with training accuracy too

    # Check 3: Are precision and recall balanced?
    if abs(metrics["precision"] - metrics["recall"]) < 0.1:
        checks.append(("Balanced precision/recall", "PASS"))
    else:
        checks.append(("Balanced precision/recall", "WARNING"))

    # Print results
    print("Model Evaluation Report")
    print("=" * 40)
    for name, value in metrics.items():
        print(f"  {name:>12}: {value:.4f}")

    print(f"\n  Confusion Matrix:")
    print(f"  {cm}")

    print(f"\n  Quality Checks:")
    for check_name, status in checks:
        print(f"  [{status:>7}] {check_name}")

    return metrics, checks
```

---

## Stage 5: Model Deployment

Deployment is putting your model into production so real users or systems can use it. We covered this in detail in Chapters 3-5.

```
+--------------------------------------------------+
|  Deployment Options                               |
|                                                   |
|  REST API (FastAPI)  -> Chapter 3                |
|  Docker Container    -> Chapter 4                |
|  Cloud Service       -> Chapter 5                |
|  Web Demo            -> Chapter 6                |
|  Batch Job           -> Chapter 7                |
|                                                   |
|  Key Questions:                                  |
|  - How fast must predictions be?                 |
|  - How many users will there be?                 |
|  - How often will the model be updated?          |
+--------------------------------------------------+
```

---

## Stage 6: Monitoring

Monitoring is watching your model after deployment. Even the best model can degrade over time. This is like checking the temperature of food in a restaurant throughout the day.

```
+--------------------------------------------------+
|  What to Monitor                                  |
|                                                   |
|  1. Model Performance                            |
|     - Accuracy over time                         |
|     - Prediction distribution changes            |
|                                                   |
|  2. Data Quality                                 |
|     - Missing values in incoming data            |
|     - Feature distributions shifting             |
|     - New categories appearing                   |
|                                                   |
|  3. System Health                                |
|     - Response time (latency)                    |
|     - Error rate                                 |
|     - Memory usage                               |
|     - Request volume                             |
|                                                   |
|  4. Business Metrics                             |
|     - Are predictions leading to good outcomes?  |
|     - Customer satisfaction                      |
|     - Revenue impact                             |
+--------------------------------------------------+
```

### Data Drift Detection

Data drift happens when the incoming data changes from what the model was trained on. Like a weather model trained on summer data trying to predict winter weather.

```python
"""
drift_detection.py - Simple data drift monitoring.

Data drift means the incoming data looks different from
the training data. When this happens, the model's
predictions may become unreliable.
"""

import numpy as np
from scipy import stats


def check_drift(
    training_data,
    production_data,
    feature_names,
    threshold=0.05,
):
    """
    Check for data drift between training and production data.

    Uses the Kolmogorov-Smirnov test to compare distributions.
    This test answers: "Do these two sets of numbers come
    from the same distribution?"

    Parameters
    ----------
    training_data : np.ndarray
        Features from the training set.
    production_data : np.ndarray
        Features from recent production data.
    feature_names : list
        Names of the features.
    threshold : float
        P-value threshold. Below this means significant drift.

    Returns
    -------
    dict
        Drift detection results.
    """
    results = {}
    drift_detected = False

    print("Data Drift Report")
    print("=" * 55)

    for i, name in enumerate(feature_names):
        train_col = training_data[:, i]
        prod_col = production_data[:, i]

        # Kolmogorov-Smirnov test
        # Returns: statistic (how different) and p-value
        # Low p-value = distributions are different
        ks_stat, p_value = stats.ks_2samp(train_col, prod_col)

        drifted = p_value < threshold
        status = "DRIFT!" if drifted else "OK"

        if drifted:
            drift_detected = True

        results[name] = {
            "ks_statistic": round(ks_stat, 4),
            "p_value": round(p_value, 4),
            "drifted": drifted,
        }

        print(
            f"  {name:>20}: KS={ks_stat:.4f}, "
            f"p={p_value:.4f} [{status}]"
        )

    print("=" * 55)
    if drift_detected:
        print("  WARNING: Data drift detected! Consider retraining.")
    else:
        print("  All features within expected range.")

    return results, drift_detected


# Example: Detect drift
np.random.seed(42)

# Training data distribution
training = np.random.normal(
    loc=[30, 50000, 700, 5],       # means
    scale=[10, 20000, 50, 3],      # standard deviations
    size=(1000, 4),
)

# Production data with drift in income (mean shifted)
production = np.random.normal(
    loc=[30, 70000, 700, 5],       # income shifted from 50k to 70k
    scale=[10, 20000, 50, 3],
    size=(500, 4),
)

features = ["age", "income", "credit_score", "employment_years"]
results, has_drift = check_drift(training, production, features)
```

```
Output:
Data Drift Report
=======================================================
                  age: KS=0.0420, p=0.7234 [OK]
               income: KS=0.3856, p=0.0000 [DRIFT!]
         credit_score: KS=0.0380, p=0.8012 [OK]
     employment_years: KS=0.0410, p=0.7456 [OK]
=======================================================
  WARNING: Data drift detected! Consider retraining.
```

---

## Stage 7: Retraining

When monitoring reveals problems (drift, declining accuracy, new patterns), it is time to retrain the model. This brings us back to Stage 2, creating the lifecycle loop.

```
+--------------------------------------------------+
|  When to Retrain?                                 |
|                                                   |
|  Trigger               Action                    |
|  -------               ------                    |
|  Data drift detected   Retrain with new data     |
|  Accuracy drops        Investigate + retrain     |
|  New features added    Retrain to use them       |
|  Scheduled (monthly)   Regular refresh           |
|  Business changes      Update labels/features    |
+--------------------------------------------------+
```

---

## The Lifecycle in Practice

```python
"""
lifecycle_overview.py - Overview of the complete ML lifecycle.
"""

lifecycle_stages = [
    {
        "stage": "1. Data Collection",
        "duration": "Days to weeks",
        "key_activity": "Gather and store raw data",
        "output": "Raw dataset",
        "common_problem": "Not enough data or biased data",
    },
    {
        "stage": "2. Data Preparation",
        "duration": "Days to weeks",
        "key_activity": "Clean, transform, split data",
        "output": "Train/val/test datasets",
        "common_problem": "Data leakage between splits",
    },
    {
        "stage": "3. Model Training",
        "duration": "Hours to days",
        "key_activity": "Train and tune models",
        "output": "Trained model file",
        "common_problem": "Overfitting to training data",
    },
    {
        "stage": "4. Model Evaluation",
        "duration": "Hours",
        "key_activity": "Test model on held-out data",
        "output": "Performance metrics",
        "common_problem": "Using wrong metrics for the problem",
    },
    {
        "stage": "5. Model Deployment",
        "duration": "Hours to days",
        "key_activity": "Put model in production",
        "output": "Running API or service",
        "common_problem": "Works in dev, breaks in production",
    },
    {
        "stage": "6. Monitoring",
        "duration": "Ongoing",
        "key_activity": "Watch model performance",
        "output": "Alerts and dashboards",
        "common_problem": "Not monitoring at all",
    },
    {
        "stage": "7. Retraining",
        "duration": "Hours to days",
        "key_activity": "Update model with new data",
        "output": "New model version",
        "common_problem": "No automated pipeline",
    },
]

print("The ML Lifecycle")
print("=" * 65)
for stage in lifecycle_stages:
    print(f"\n{stage['stage']}")
    print(f"  Duration:        {stage['duration']}")
    print(f"  Key Activity:    {stage['key_activity']}")
    print(f"  Output:          {stage['output']}")
    print(f"  Common Problem:  {stage['common_problem']}")
```

```
Output:
The ML Lifecycle
=================================================================

1. Data Collection
  Duration:        Days to weeks
  Key Activity:    Gather and store raw data
  Output:          Raw dataset
  Common Problem:  Not enough data or biased data

2. Data Preparation
  Duration:        Days to weeks
  Key Activity:    Clean, transform, split data
  Output:          Train/val/test datasets
  Common Problem:  Data leakage between splits

3. Model Training
  Duration:        Hours to days
  Key Activity:    Train and tune models
  Output:          Trained model file
  Common Problem:  Overfitting to training data

4. Model Evaluation
  Duration:        Hours
  Key Activity:    Test model on held-out data
  Output:          Performance metrics
  Common Problem:  Using wrong metrics for the problem

5. Model Deployment
  Duration:        Hours to days
  Key Activity:    Put model in production
  Output:          Running API or service
  Common Problem:  Works in dev, breaks in production

6. Monitoring
  Duration:        Ongoing
  Key Activity:    Watch model performance
  Output:          Alerts and dashboards
  Common Problem:  Not monitoring at all

7. Retraining
  Duration:        Hours to days
  Key Activity:    Update model with new data
  Output:          New model version
  Common Problem:  No automated pipeline
```

---

## Common Mistakes

1. **Treating ML as a one-time project.** ML is a continuous process. Models degrade over time and need regular attention.

2. **Skipping monitoring.** Without monitoring, you do not know when your model starts making bad predictions.

3. **Data leakage.** Using test data during training or preparation gives overly optimistic results that do not hold in production.

4. **Ignoring data drift.** The world changes. Data distributions shift. Models trained on old patterns make poor predictions on new patterns.

5. **No retraining plan.** Every model needs a plan for when and how it will be retrained.

---

## Best Practices

1. **Document every stage.** Record what data was used, what decisions were made, and what results were achieved.

2. **Automate the pipeline.** Manual steps are error-prone and slow. Automate as much as possible.

3. **Monitor from day one.** Set up monitoring before deployment, not after problems appear.

4. **Version everything.** Version your data, code, models, and configurations.

5. **Plan for failure.** Have a rollback plan. If the new model is worse, you should be able to quickly revert to the previous version.

---

## Quick Summary

The ML lifecycle is a continuous loop of seven stages: data collection, data preparation, model training, model evaluation, model deployment, monitoring, and retraining. Each stage has its own challenges and best practices. Understanding this full picture is essential for building ML systems that stay healthy and effective over time.

---

## Key Points

- ML is a lifecycle, not a one-time project
- The seven stages form a continuous loop
- Data preparation typically takes the most time (60-80% of a project)
- Monitoring is essential to detect when a model starts degrading
- Data drift is a common reason models lose accuracy over time
- Every model needs a retraining strategy
- Version everything: data, code, models, and configs

---

## Practice Questions

1. Why is the ML lifecycle a loop rather than a straight line?

2. What is data drift and how can you detect it?

3. Why is it important to keep training, validation, and test sets completely separate?

4. Which stage of the ML lifecycle typically takes the most time and effort?

5. What are three signals that tell you a model needs to be retrained?

---

## Exercises

### Exercise 1: Lifecycle Diagram

Draw your own ML lifecycle diagram for a specific use case (such as email spam detection). Include at least one detail specific to your use case at each stage.

### Exercise 2: Drift Monitor

Implement a simple drift monitoring system that:
- Stores the distribution of training features
- Accepts new data batches
- Compares distributions and raises an alert if drift is detected
- Logs drift events with timestamps

### Exercise 3: Retraining Decision

You have a model in production. Write a decision framework that answers:
- When should you retrain? (What triggers retraining?)
- How often should you retrain? (Schedule vs triggered)
- How do you validate the new model before deploying it?
- What do you do if the new model is worse than the current one?

---

## What Is Next?

Now that you understand the full ML lifecycle, the next chapters dive deeper into the tools that support it. In Chapter 9, we will learn about experiment tracking with MLflow, which helps you organize and compare your training experiments. No more guessing which parameters gave the best results!
