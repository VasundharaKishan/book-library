# Chapter 11: The Model Registry

## What You Will Learn

In this chapter, you will learn:

- What a model registry is and why you need one
- How to use the MLflow Model Registry
- How to manage model stages: staging, production, and archived
- How to implement a model promotion workflow
- How to load production models from the registry

## Why This Chapter Matters

Imagine a pharmaceutical company. They do not just create medicines and give them directly to patients. Each medicine goes through a rigorous process: lab testing, clinical trials, regulatory approval, and finally production. At each stage, the medicine is carefully tracked.

ML models need a similar process. You do not want someone to accidentally deploy an untested model to production. A model registry is the system that tracks every model version, which stage it is in, who approved it, and when it was promoted. It is the quality control system for your models.

---

## What Is a Model Registry?

A model registry is a centralized store for managing ML models throughout their lifecycle. Think of it as a library catalog for your models.

```
+--------------------------------------------------+
|  Model Registry                                  |
|                                                   |
|  +-----------+     +-----------+     +-----------+|
|  |  Staging  | --> |Production | --> | Archived  ||
|  |           |     |           |     |           ||
|  | Testing   |     | Live!     |     | Retired   ||
|  | Validation|     | Serving   |     | Kept for  ||
|  | Review    |     | users     |     | reference ||
|  +-----------+     +-----------+     +-----------+|
|                                                   |
|  Each model version has:                         |
|  - A unique version number                       |
|  - The person who registered it                  |
|  - When it was created                           |
|  - Its current stage                             |
|  - Description and tags                          |
+--------------------------------------------------+
```

### Without vs With a Model Registry

```
+--------------------------------------------------+
|  Without Registry           With Registry         |
|                                                   |
|  model_v1.pkl              CreditRisk Model      |
|  model_v2.pkl              Version 1: Archived   |
|  model_v2_fixed.pkl        Version 2: Archived   |
|  model_FINAL.pkl           Version 3: Staging    |
|  model_FINAL_v2.pkl        Version 4: Production |
|  WHICH ONE IS IN PROD??                          |
|                              Clear and organized! |
+--------------------------------------------------+
```

---

## MLflow Model Registry

MLflow includes a built-in model registry. Let us see how to use it.

### Registering a Model

```python
"""
register_model.py - Register models in MLflow Model Registry.

The registry provides a central place to manage model
versions and their lifecycle stages.
"""

import mlflow
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Create and train a model
X, y = make_classification(
    n_samples=1000, n_features=10,
    n_classes=2, random_state=42,
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42,
)

mlflow.set_experiment("model_registry_demo")

# Train and register the model
with mlflow.start_run(run_name="rf_v1") as run:
    # Train
    model = RandomForestClassifier(
        n_estimators=100, random_state=42
    )
    model.fit(X_train, y_train)

    # Log metrics
    accuracy = accuracy_score(y_test, model.predict(X_test))
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_param("n_estimators", 100)

    # Log and register the model
    # registered_model_name creates an entry in the registry
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="CreditRiskModel",
    )

    print(f"Model registered as 'CreditRiskModel'")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Run ID: {run.info.run_id}")
```

```
Output:
Model registered as 'CreditRiskModel'
Accuracy: 0.9350
Run ID: a1b2c3d4567890
Successfully registered model 'CreditRiskModel'.
Created version '1' of model 'CreditRiskModel'.
```

### Registering Multiple Versions

```python
"""
register_multiple.py - Register multiple model versions.

Each time you register a model with the same name,
MLflow creates a new version automatically.
"""

import mlflow
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
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

mlflow.set_experiment("model_registry_demo")

# Version 1: Random Forest with 50 trees
with mlflow.start_run(run_name="rf_50_trees"):
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("n_estimators", 50)

    mlflow.sklearn.log_model(
        model, "model",
        registered_model_name="CreditRiskModel",
    )
    print(f"Version 1 - RF(50): accuracy={accuracy:.4f}")

# Version 2: Random Forest with 200 trees
with mlflow.start_run(run_name="rf_200_trees"):
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("n_estimators", 200)

    mlflow.sklearn.log_model(
        model, "model",
        registered_model_name="CreditRiskModel",
    )
    print(f"Version 2 - RF(200): accuracy={accuracy:.4f}")

# Version 3: Gradient Boosting
with mlflow.start_run(run_name="gradient_boosting"):
    model = GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.1, random_state=42
    )
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_param("model_type", "GradientBoosting")
    mlflow.log_param("n_estimators", 100)

    mlflow.sklearn.log_model(
        model, "model",
        registered_model_name="CreditRiskModel",
    )
    print(f"Version 3 - GB: accuracy={accuracy:.4f}")
```

```
Output:
Version 1 - RF(50): accuracy=0.9250
Created version '1' of model 'CreditRiskModel'.
Version 2 - RF(200): accuracy=0.9400
Created version '2' of model 'CreditRiskModel'.
Version 3 - GB: accuracy=0.9450
Created version '3' of model 'CreditRiskModel'.
```

---

## Model Stages

The MLflow Model Registry supports lifecycle stages that represent where a model is in the promotion process:

```
+--------------------------------------------------+
|  Model Lifecycle Stages                           |
|                                                   |
|  None -------> Staging -------> Production        |
|  (just           |                 |              |
|   registered)    |                 |              |
|                  |                 |              |
|                  +----> Archived <-+              |
|                                                   |
|  None:       Just registered, not evaluated yet  |
|  Staging:    Being tested and validated          |
|  Production: Live, serving real users            |
|  Archived:   Retired, kept for reference         |
+--------------------------------------------------+
```

### Managing Model Stages

```python
"""
manage_stages.py - Promote models through lifecycle stages.

This shows how to move models between stages using
the MLflow client API.
"""

from mlflow.tracking import MlflowClient

# Create a client to interact with the registry
client = MlflowClient()

model_name = "CreditRiskModel"

# List all versions of the model
print(f"All versions of '{model_name}':")
print("=" * 60)

for version in client.search_model_versions(f"name='{model_name}'"):
    print(
        f"  Version {version.version}: "
        f"Stage={version.current_stage}, "
        f"Status={version.status}"
    )

# Promote version 3 to Staging
# (In MLflow 2.x, use set_registered_model_alias instead)
client.transition_model_version_stage(
    name=model_name,
    version="3",
    stage="Staging",
)
print(f"\nVersion 3 promoted to Staging")

# After testing in staging, promote to Production
client.transition_model_version_stage(
    name=model_name,
    version="3",
    stage="Production",
)
print(f"Version 3 promoted to Production")

# Archive the old production model
client.transition_model_version_stage(
    name=model_name,
    version="1",
    stage="Archived",
)
print(f"Version 1 archived")

# Add descriptions for documentation
client.update_model_version(
    name=model_name,
    version="3",
    description="GradientBoosting model with 94.5% accuracy. "
                "Promoted to production on 2024-01-15.",
)

# List updated stages
print(f"\nUpdated stages:")
print("=" * 60)
for version in client.search_model_versions(f"name='{model_name}'"):
    print(
        f"  Version {version.version}: "
        f"Stage={version.current_stage}"
    )
```

```
Output:
All versions of 'CreditRiskModel':
============================================================
  Version 1: Stage=None, Status=READY
  Version 2: Stage=None, Status=READY
  Version 3: Stage=None, Status=READY

Version 3 promoted to Staging
Version 3 promoted to Production
Version 1 archived

Updated stages:
============================================================
  Version 1: Stage=Archived
  Version 2: Stage=None
  Version 3: Stage=Production
```

---

## Loading Models from the Registry

The beauty of the registry is that your serving code does not need to know specific file paths. It just asks for "the production model."

```python
"""
load_from_registry.py - Load models by stage from the registry.

Your API code can load "the production model" without
knowing which specific version or file path to use.
When you promote a new version, the API automatically
picks it up.
"""

import mlflow

model_name = "CreditRiskModel"

# Load the production model
# This always loads whatever version is currently in Production
production_model = mlflow.pyfunc.load_model(
    f"models:/{model_name}/Production"
)
print("Production model loaded!")

# Load the staging model (for testing)
try:
    staging_model = mlflow.pyfunc.load_model(
        f"models:/{model_name}/Staging"
    )
    print("Staging model loaded!")
except Exception:
    print("No model in Staging stage")

# Load a specific version
specific_model = mlflow.pyfunc.load_model(
    f"models:/{model_name}/2"
)
print("Version 2 loaded!")

# Use the model for predictions
import numpy as np
sample_input = np.array([[30, 50000, 720, 5, 1, 0, 1, 0, 1, 0]])

prediction = production_model.predict(sample_input)
print(f"\nProduction model prediction: {prediction}")
```

```
Output:
Production model loaded!
No model in Staging stage
Version 2 loaded!

Production model prediction: [0]
```

---

## Model Promotion Workflow

Here is a complete workflow for promoting models safely:

```python
"""
promotion_workflow.py - A complete model promotion workflow.

This workflow ensures models are properly validated
before reaching production.
"""

from mlflow.tracking import MlflowClient
import mlflow
import numpy as np
from sklearn.metrics import accuracy_score


def promote_model(
    model_name,
    version,
    test_data,
    test_labels,
    min_accuracy=0.90,
):
    """
    Safely promote a model through stages.

    Steps:
    1. Load the candidate model
    2. Run validation tests
    3. Compare with current production model
    4. If better, promote to staging then production
    5. Archive the old production model

    Parameters
    ----------
    model_name : str
        Name of the registered model.
    version : str
        Version number to promote.
    test_data : np.ndarray
        Test features for validation.
    test_labels : np.ndarray
        True labels for validation.
    min_accuracy : float
        Minimum accuracy required for production.

    Returns
    -------
    bool
        True if promotion was successful.
    """
    client = MlflowClient()

    print(f"Model Promotion Workflow")
    print(f"Model: {model_name}, Version: {version}")
    print("=" * 50)

    # Step 1: Load the candidate model
    print("\n[Step 1] Loading candidate model...")
    candidate = mlflow.pyfunc.load_model(
        f"models:/{model_name}/{version}"
    )

    # Step 2: Validate the candidate
    print("[Step 2] Validating candidate...")
    candidate_preds = candidate.predict(test_data)
    candidate_accuracy = accuracy_score(test_labels, candidate_preds)
    print(f"  Candidate accuracy: {candidate_accuracy:.4f}")

    # Check minimum accuracy
    if candidate_accuracy < min_accuracy:
        print(f"  FAIL: Below minimum accuracy ({min_accuracy})")
        return False
    print(f"  PASS: Above minimum accuracy ({min_accuracy})")

    # Step 3: Compare with current production model
    print("[Step 3] Comparing with production model...")
    try:
        production = mlflow.pyfunc.load_model(
            f"models:/{model_name}/Production"
        )
        prod_preds = production.predict(test_data)
        prod_accuracy = accuracy_score(test_labels, prod_preds)
        print(f"  Production accuracy: {prod_accuracy:.4f}")

        if candidate_accuracy <= prod_accuracy:
            print(f"  FAIL: Not better than production model")
            return False
        print(f"  PASS: Better than production model!")

        improvement = candidate_accuracy - prod_accuracy
        print(f"  Improvement: +{improvement:.4f}")

        # Find current production version to archive later
        prod_versions = client.search_model_versions(
            f"name='{model_name}'"
        )
        old_prod_version = None
        for v in prod_versions:
            if v.current_stage == "Production":
                old_prod_version = v.version
                break

    except Exception:
        print("  No current production model found")
        old_prod_version = None
        prod_accuracy = 0

    # Step 4: Promote to staging
    print("[Step 4] Promoting to staging...")
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage="Staging",
    )
    print(f"  Version {version} moved to Staging")

    # Step 5: Promote to production
    print("[Step 5] Promoting to production...")
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage="Production",
    )
    print(f"  Version {version} moved to Production")

    # Step 6: Archive old production model
    if old_prod_version:
        print(f"[Step 6] Archiving old version {old_prod_version}...")
        client.transition_model_version_stage(
            name=model_name,
            version=old_prod_version,
            stage="Archived",
        )
        print(f"  Version {old_prod_version} archived")

    # Step 7: Add description
    client.update_model_version(
        name=model_name,
        version=version,
        description=(
            f"Promoted to production. "
            f"Accuracy: {candidate_accuracy:.4f}. "
            f"Improvement over previous: "
            f"+{candidate_accuracy - prod_accuracy:.4f}"
        ),
    )

    print("\n" + "=" * 50)
    print("Promotion SUCCESSFUL!")
    print(f"  New production model: Version {version}")
    print(f"  Accuracy: {candidate_accuracy:.4f}")

    return True


# Example usage
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=1000, n_features=10,
    n_classes=2, random_state=42,
)
_, X_test, _, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42,
)

success = promote_model(
    model_name="CreditRiskModel",
    version="3",
    test_data=X_test,
    test_labels=y_test,
    min_accuracy=0.90,
)
```

```
Output:
Model Promotion Workflow
Model: CreditRiskModel, Version: 3
==================================================

[Step 1] Loading candidate model...
[Step 2] Validating candidate...
  Candidate accuracy: 0.9450
  PASS: Above minimum accuracy (0.9)
[Step 3] Comparing with production model...
  No current production model found
[Step 4] Promoting to staging...
  Version 3 moved to Staging
[Step 5] Promoting to production...
  Version 3 moved to Production

==================================================
Promotion SUCCESSFUL!
  New production model: Version 3
  Accuracy: 0.9450
```

---

## Common Mistakes

1. **Deploying models without validation.** Always test a model in staging before promoting to production.

2. **Not archiving old models.** Keep old versions archived for reference. You might need to roll back.

3. **No rollback plan.** If the new production model has issues, you need to quickly revert to the previous version.

4. **Skipping the staging stage.** Going directly from development to production is risky. Always test in staging first.

5. **Not documenting model versions.** Add descriptions to each version explaining what changed and why it was promoted.

---

## Best Practices

1. **Follow a strict promotion workflow.** None -> Staging -> Production. Never skip stages.

2. **Automate validation.** Run automated tests before any promotion.

3. **Compare before promoting.** The new model should be better than the current production model on key metrics.

4. **Keep a rollback plan.** If the new model causes problems, you should be able to quickly revert to the previous production version.

5. **Document every version.** Record why each model was created, what data it used, and why it was promoted or archived.

---

## Quick Summary

A model registry is a centralized system for managing ML model versions and their lifecycle stages. MLflow's Model Registry lets you register models, promote them through stages (None, Staging, Production, Archived), and load the production model without knowing specific file paths. A proper promotion workflow includes validation, comparison with the current production model, and archiving of old versions.

---

## Key Points

- A model registry tracks model versions and their lifecycle stages
- MLflow supports four stages: None, Staging, Production, Archived
- Models should be validated in Staging before promoting to Production
- Loading models by stage (e.g., "Production") decouples serving from specific versions
- Always compare a candidate with the current production model before promoting
- Keep old versions archived for potential rollback

---

## Practice Questions

1. What are the four lifecycle stages in the MLflow Model Registry?

2. Why should you never promote a model directly from development to production?

3. How does loading a model by stage (e.g., `models:/ModelName/Production`) help in production systems?

4. What should you do with the old production model when promoting a new one?

5. What validation checks should you perform before promoting a model to production?

---

## Exercises

### Exercise 1: Register and Manage

Register three different model versions in MLflow. Practice promoting one to staging, then to production, and archiving an old version.

### Exercise 2: Automated Promotion

Write a function that:
- Takes a model version and test data
- Runs at least three validation checks (accuracy, precision, recall)
- Only promotes if ALL checks pass
- Logs the promotion decision with reasons

### Exercise 3: Rollback System

Implement a rollback function that:
- Takes a model name as input
- Finds the most recently archived version
- Promotes it back to production
- Archives the current production model
- Logs all changes

---

## What Is Next?

You now have a system for managing model versions. But how do you ensure models are automatically tested and deployed when code changes? In Chapter 12, we will learn about CI/CD (Continuous Integration and Continuous Deployment) for ML, using GitHub Actions to automate testing, training, and deployment.
