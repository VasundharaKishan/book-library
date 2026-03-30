# Chapter 9: Experiment Tracking with MLflow

## What You Will Learn

In this chapter, you will learn:

- Why tracking experiments is essential for ML projects
- How to install and set up MLflow
- How to log parameters, metrics, and artifacts
- How to compare different experiment runs
- How to use the MLflow UI to visualize results
- An overview of Weights & Biases as an alternative

## Why This Chapter Matters

Imagine you are a scientist testing different medications. You try dozens of combinations: different doses, different ingredients, different schedules. After three weeks, you find a combination that works great. But you cannot remember exactly what it was. You scribbled notes on random papers, some of which you threw away.

This happens all the time in ML. You try different model types, different parameters, different data preprocessing steps. After many experiments, you find something that works, but you cannot reproduce it because you forgot to write down the details.

Experiment tracking solves this problem. It automatically records everything about every experiment so you can always go back and see exactly what you did.

---

## The Problem Without Tracking

```
+--------------------------------------------------+
|  Without Experiment Tracking                      |
|                                                   |
|  "Was it 100 trees or 200 trees?"                |
|  "Did I use StandardScaler or MinMaxScaler?"     |
|  "Which version of the data gave 95% accuracy?"  |
|  "What was the learning rate for the best model?"|
|                                                   |
|  Common "solutions" that do not work:            |
|  - model_final.pkl                               |
|  - model_final_v2.pkl                            |
|  - model_final_v2_ACTUALLY_FINAL.pkl             |
|  - model_best_DO_NOT_DELETE.pkl                  |
+--------------------------------------------------+
```

```
+--------------------------------------------------+
|  With Experiment Tracking                         |
|                                                   |
|  Run #1: RF, 100 trees, StandardScaler -> 0.89   |
|  Run #2: RF, 200 trees, StandardScaler -> 0.91   |
|  Run #3: XGBoost, lr=0.1, StandardScaler -> 0.93 |
|  Run #4: XGBoost, lr=0.05, MinMaxScaler -> 0.94  |
|                                                   |
|  Every run recorded with:                        |
|  - Parameters used                               |
|  - Metrics achieved                              |
|  - Model files saved                             |
|  - Code version                                  |
|  - Timestamp                                     |
+--------------------------------------------------+
```

---

## What Is MLflow?

MLflow is an open-source platform for managing the ML lifecycle. It has four main components:

```
+--------------------------------------------------+
|  MLflow Components                                |
|                                                   |
|  1. Tracking    -> Record experiments             |
|  2. Projects    -> Package ML code                |
|  3. Models      -> Manage model versions          |
|  4. Registry    -> Store and serve models         |
|                                                   |
|  In this chapter, we focus on Tracking.          |
|  Chapter 11 covers the Model Registry.           |
+--------------------------------------------------+
```

### Installing MLflow

```bash
pip install mlflow
```

---

## Getting Started with MLflow Tracking

### Your First Tracked Experiment

```python
"""
first_tracking.py - Your first MLflow experiment.

Run with: python first_tracking.py

After running, start the MLflow UI with:
    mlflow ui

Then visit http://localhost:5000 to see your results.
"""

import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

# Create sample data
X, y = make_classification(
    n_samples=1000,
    n_features=10,
    n_classes=2,
    random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Set the experiment name
# All runs with this name are grouped together
mlflow.set_experiment("credit_risk_model")

# Start an MLflow run
# Everything inside this 'with' block is tracked
with mlflow.start_run(run_name="random_forest_baseline"):

    # Define parameters
    n_estimators = 100
    max_depth = 10
    random_state = 42

    # Log parameters
    # Parameters are the inputs to your experiment
    # (settings, hyperparameters, choices you made)
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param("random_state", random_state)
    mlflow.log_param("test_size", 0.2)

    # Train model
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
    )
    model.fit(X_train, y_train)

    # Make predictions
    predictions = model.predict(X_test)

    # Calculate metrics
    accuracy = accuracy_score(y_test, predictions)
    f1 = f1_score(y_test, predictions, average="weighted")

    # Log metrics
    # Metrics are the outputs / results of your experiment
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("train_samples", len(X_train))
    mlflow.log_metric("test_samples", len(X_test))

    # Log the model itself
    # This saves the model as an artifact
    mlflow.sklearn.log_model(model, "model")

    print(f"Run completed!")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  F1 Score: {f1:.4f}")
    print(f"  Run ID: {mlflow.active_run().info.run_id}")
```

```
Output:
Run completed!
  Accuracy: 0.9350
  F1 Score: 0.9348
  Run ID: a1b2c3d4e5f6789012345678
```

**Line-by-line explanation:**

```python
mlflow.set_experiment("credit_risk_model")
```

This creates (or selects) an experiment. Think of an experiment as a folder where all related runs are stored. All runs for your credit risk model go in this folder.

```python
with mlflow.start_run(run_name="random_forest_baseline"):
```

This starts a new run within the experiment. Each run is one attempt (one set of parameters, one training session). The `run_name` is a human-readable label. The `with` block ensures the run is properly closed when done.

```python
mlflow.log_param("n_estimators", n_estimators)
```

This records a parameter. Parameters are the settings you chose for this run. They are searchable and comparable across runs.

```python
mlflow.log_metric("accuracy", accuracy)
```

This records a metric. Metrics are the results you measured. You can plot metrics over time and compare them across runs.

```python
mlflow.sklearn.log_model(model, "model")
```

This saves the actual model file as an artifact. Artifacts are any files associated with the run (models, plots, data samples).

---

## Running Multiple Experiments

The real power of tracking comes from running many experiments and comparing them:

```python
"""
multiple_experiments.py - Run and compare multiple experiments.

This script tries different model configurations and
logs everything to MLflow for comparison.
"""

import mlflow
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Create data
X, y = make_classification(
    n_samples=1000, n_features=10,
    n_classes=2, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42,
)

mlflow.set_experiment("model_comparison")

# Define experiments to run
experiments = [
    {
        "name": "logistic_regression",
        "model": LogisticRegression(max_iter=1000),
        "params": {"model_type": "LogisticRegression", "max_iter": 1000},
    },
    {
        "name": "random_forest_50",
        "model": RandomForestClassifier(n_estimators=50, random_state=42),
        "params": {"model_type": "RandomForest", "n_estimators": 50},
    },
    {
        "name": "random_forest_200",
        "model": RandomForestClassifier(n_estimators=200, random_state=42),
        "params": {"model_type": "RandomForest", "n_estimators": 200},
    },
    {
        "name": "gradient_boosting",
        "model": GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, random_state=42
        ),
        "params": {
            "model_type": "GradientBoosting",
            "n_estimators": 100,
            "learning_rate": 0.1,
        },
    },
]

# Run each experiment
results = []

for exp in experiments:
    with mlflow.start_run(run_name=exp["name"]):
        # Log parameters
        for key, value in exp["params"].items():
            mlflow.log_param(key, value)

        # Train
        model = exp["model"]
        model.fit(X_train, y_train)

        # Evaluate
        predictions = model.predict(X_test)
        metrics = {
            "accuracy": accuracy_score(y_test, predictions),
            "f1_score": f1_score(y_test, predictions, average="weighted"),
            "precision": precision_score(y_test, predictions, average="weighted"),
            "recall": recall_score(y_test, predictions, average="weighted"),
        }

        # Log metrics
        for key, value in metrics.items():
            mlflow.log_metric(key, value)

        # Log model
        mlflow.sklearn.log_model(model, "model")

        results.append({
            "name": exp["name"],
            **metrics,
        })

        print(f"  {exp['name']}: accuracy={metrics['accuracy']:.4f}")

# Print comparison
print("\n" + "=" * 60)
print(f"{'Model':<25} {'Accuracy':>10} {'F1':>10} {'Precision':>10}")
print("-" * 60)
for r in sorted(results, key=lambda x: x["accuracy"], reverse=True):
    print(
        f"{r['name']:<25} {r['accuracy']:>10.4f} "
        f"{r['f1_score']:>10.4f} {r['precision']:>10.4f}"
    )
```

```
Output:
  logistic_regression: accuracy=0.9100
  random_forest_50: accuracy=0.9250
  random_forest_200: accuracy=0.9400
  gradient_boosting: accuracy=0.9450

============================================================
Model                       Accuracy         F1  Precision
------------------------------------------------------------
gradient_boosting              0.9450     0.9449     0.9455
random_forest_200              0.9400     0.9398     0.9405
random_forest_50               0.9250     0.9248     0.9260
logistic_regression            0.9100     0.9098     0.9110
```

---

## Logging Artifacts

Artifacts are files associated with a run, like plots, data samples, or configuration files:

```python
"""
log_artifacts.py - Log files and plots to MLflow.

Artifacts are any files you want to associate with
a run: charts, config files, sample predictions, etc.
"""

import mlflow
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import json
import os

# Setup
X, y = make_classification(
    n_samples=1000, n_features=10,
    n_classes=2, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42,
)

mlflow.set_experiment("artifact_demo")

with mlflow.start_run(run_name="with_artifacts"):
    # Train model
    model = RandomForestClassifier(
        n_estimators=100, random_state=42
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    # Log basic metrics
    from sklearn.metrics import accuracy_score
    mlflow.log_metric("accuracy", accuracy_score(y_test, predictions))

    # Artifact 1: Confusion matrix plot
    cm = confusion_matrix(y_test, predictions)
    fig, ax = plt.subplots(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(ax=ax)
    ax.set_title("Confusion Matrix")

    # Save plot to file, then log as artifact
    plot_path = "confusion_matrix.png"
    fig.savefig(plot_path)
    plt.close()
    mlflow.log_artifact(plot_path)
    os.remove(plot_path)  # Clean up local file

    # Artifact 2: Feature importance plot
    importances = model.feature_importances_
    fig, ax = plt.subplots(figsize=(10, 6))
    feature_names = [f"feature_{i}" for i in range(len(importances))]
    ax.barh(feature_names, importances)
    ax.set_xlabel("Importance")
    ax.set_title("Feature Importances")

    plot_path = "feature_importance.png"
    fig.savefig(plot_path, bbox_inches="tight")
    plt.close()
    mlflow.log_artifact(plot_path)
    os.remove(plot_path)

    # Artifact 3: Model configuration JSON
    config = {
        "model_type": "RandomForestClassifier",
        "n_estimators": 100,
        "random_state": 42,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "features": feature_names,
    }
    config_path = "model_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    mlflow.log_artifact(config_path)
    os.remove(config_path)

    # Artifact 4: Sample predictions
    import pandas as pd
    sample_df = pd.DataFrame({
        "actual": y_test[:20],
        "predicted": predictions[:20],
        "correct": y_test[:20] == predictions[:20],
    })
    sample_path = "sample_predictions.csv"
    sample_df.to_csv(sample_path, index=False)
    mlflow.log_artifact(sample_path)
    os.remove(sample_path)

    print("All artifacts logged!")
    print("Run 'mlflow ui' and check the Artifacts tab")
```

```
Output:
All artifacts logged!
Run 'mlflow ui' and check the Artifacts tab
```

---

## Using the MLflow UI

The MLflow UI is a web interface where you can browse and compare your experiments.

```bash
# Start the MLflow UI
mlflow ui
# Visit http://localhost:5000
```

```
+--------------------------------------------------+
|  MLflow UI Features                               |
|                                                   |
|  Experiments List                                |
|  +---------------------------------------------+|
|  | credit_risk_model (4 runs)                   ||
|  | model_comparison  (4 runs)                   ||
|  | artifact_demo     (1 run)                    ||
|  +---------------------------------------------+|
|                                                   |
|  Run Details                                     |
|  +---------------------------------------------+|
|  | Parameters  | Metrics    | Artifacts          ||
|  | n_trees=100 | acc=0.935  | model/              ||
|  | depth=10    | f1=0.934   | confusion_matrix.png||
|  | seed=42     | prec=0.936 | feature_importance.png|
|  +---------------------------------------------+|
|                                                   |
|  Compare Runs                                    |
|  +---------------------------------------------+|
|  | Select multiple runs and compare side by side||
|  | See parameter vs metric charts               ||
|  | Identify the best configuration              ||
|  +---------------------------------------------+|
+--------------------------------------------------+
```

### Querying Runs Programmatically

```python
"""
query_runs.py - Search and compare MLflow runs in code.

You do not always need the UI. You can query runs
programmatically to find the best model or compare results.
"""

import mlflow

# Set the experiment
mlflow.set_experiment("model_comparison")

# Get all runs from the experiment
experiment = mlflow.get_experiment_by_name("model_comparison")

if experiment:
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.accuracy DESC"],  # Sort by accuracy
    )

    print("All runs (sorted by accuracy):")
    print("=" * 70)

    for _, run in runs.iterrows():
        print(
            f"  Run: {run['tags.mlflow.runName']:<25} "
            f"Accuracy: {run['metrics.accuracy']:.4f} "
            f"F1: {run['metrics.f1_score']:.4f}"
        )

    # Find the best run
    best_run = runs.iloc[0]
    print(f"\nBest run: {best_run['tags.mlflow.runName']}")
    print(f"  Accuracy: {best_run['metrics.accuracy']:.4f}")
    print(f"  Run ID: {best_run['run_id']}")

    # Load the best model
    best_model_uri = f"runs:/{best_run['run_id']}/model"
    print(f"  Model URI: {best_model_uri}")
    # best_model = mlflow.sklearn.load_model(best_model_uri)
```

```
Output:
All runs (sorted by accuracy):
======================================================================
  Run: gradient_boosting        Accuracy: 0.9450 F1: 0.9449
  Run: random_forest_200        Accuracy: 0.9400 F1: 0.9398
  Run: random_forest_50         Accuracy: 0.9250 F1: 0.9248
  Run: logistic_regression      Accuracy: 0.9100 F1: 0.9098

Best run: gradient_boosting
  Accuracy: 0.9450
  Run ID: a1b2c3d4e5f6789012345678
  Model URI: runs:/a1b2c3d4e5f6789012345678/model
```

---

## Weights & Biases Overview

Weights & Biases (W&B or wandb) is a popular alternative to MLflow, especially for deep learning projects. It is a cloud-based service with a beautiful UI.

```
+--------------------------------------------------+
|  MLflow vs Weights & Biases                       |
|                                                   |
|  MLflow                    W&B                   |
|  - Open source             - Freemium service    |
|  - Self-hosted             - Cloud-hosted        |
|  - Works offline           - Needs internet      |
|  - General ML              - Deep learning focus |
|  - Free forever            - Free for personal   |
|  - Setup required          - Quick to start      |
+--------------------------------------------------+
```

### Quick W&B Example

```python
"""
wandb_example.py - Basic Weights & Biases usage.

Install: pip install wandb
Setup: wandb login (get API key from wandb.ai)

This shows the basic W&B API for comparison with MLflow.
"""

import wandb
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Create data
X, y = make_classification(
    n_samples=1000, n_features=10,
    n_classes=2, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42,
)

# Initialize W&B run
# This creates a new run on the W&B servers
run = wandb.init(
    project="credit-risk-model",
    name="random_forest_baseline",
    config={
        "model_type": "RandomForest",
        "n_estimators": 100,
        "max_depth": 10,
    },
)

# Train model
model = RandomForestClassifier(
    n_estimators=wandb.config.n_estimators,
    max_depth=wandb.config.max_depth,
    random_state=42,
)
model.fit(X_train, y_train)

# Evaluate and log metrics
accuracy = accuracy_score(y_test, model.predict(X_test))
wandb.log({
    "accuracy": accuracy,
    "train_samples": len(X_train),
    "test_samples": len(X_test),
})

print(f"Accuracy: {accuracy:.4f}")
print(f"View results at: {run.get_url()}")

# Finish the run
wandb.finish()
```

```
Output:
Accuracy: 0.9350
View results at: https://wandb.ai/your-username/credit-risk-model/runs/abc123
```

---

## Common Mistakes

1. **Not tracking experiments at all.** Even simple experiments should be logged. You will thank yourself later.

2. **Logging too little.** Log everything: parameters, metrics, data versions, code versions, and artifacts.

3. **Not using experiment names.** Group related runs under the same experiment name for easy comparison.

4. **Forgetting to log the model.** Metrics tell you how good a model was, but without the saved model, you cannot use it.

5. **Only looking at one metric.** A model with 99% accuracy might have terrible recall for rare classes. Log multiple metrics.

---

## Best Practices

1. **Track every experiment from the start.** Even during exploration. You never know which run will turn out to be the best.

2. **Use descriptive run names.** Names like "rf_200trees_scaled" are more useful than "run_47."

3. **Log artifacts.** Save confusion matrices, feature importance plots, and sample predictions alongside your metrics.

4. **Compare runs systematically.** Use the UI or programmatic queries to find the best model, not memory.

5. **Set up experiment naming conventions.** Consistent naming makes it easy to find and compare runs.

---

## Quick Summary

Experiment tracking with MLflow eliminates the guesswork from ML development. You log parameters (what you tried), metrics (what happened), and artifacts (supporting files) for every experiment. The MLflow UI lets you compare runs visually. Weights & Biases is a cloud-based alternative. The key principle is: if you did not log it, it did not happen.

---

## Key Points

- MLflow tracks parameters, metrics, and artifacts for each experiment run
- Use mlflow.set_experiment() to group related runs
- Use mlflow.start_run() to start tracking a new experiment
- Log parameters with mlflow.log_param() and metrics with mlflow.log_metric()
- Save models with mlflow.sklearn.log_model() (or the appropriate framework)
- The MLflow UI lets you compare runs visually
- Weights & Biases is a popular cloud-based alternative

---

## Practice Questions

1. What is the difference between a parameter and a metric in MLflow?

2. Why should you use `with mlflow.start_run()` instead of manually starting and stopping runs?

3. What are artifacts in MLflow? Give three examples of useful artifacts to log.

4. How would you find the best model from 50 different runs using MLflow?

5. When would you choose Weights & Biases over MLflow?

---

## Exercises

### Exercise 1: Track a Hyperparameter Search

Use MLflow to track a grid search over these parameters:
- n_estimators: [50, 100, 200]
- max_depth: [5, 10, 20]
- min_samples_split: [2, 5, 10]

Log all 27 combinations and find the best one using the MLflow UI.

### Exercise 2: Custom Artifacts

Create an MLflow run that logs:
- A confusion matrix as a PNG image
- A CSV file with the top 10 most important features
- A JSON file with the model configuration
- The trained model itself

### Exercise 3: Experiment Comparison Script

Write a Python script that:
- Queries all runs from an experiment
- Creates a summary table with the top 5 runs by accuracy
- Generates a bar chart comparing metrics across runs
- Saves the chart as an artifact in a new summary run

---

## What Is Next?

Experiment tracking tells you what happened during training. But what about the data itself? In Chapter 10, we will learn about data versioning with DVC. Just as git tracks code changes, DVC tracks data changes, ensuring you can always reproduce an experiment with the exact data that was used.
