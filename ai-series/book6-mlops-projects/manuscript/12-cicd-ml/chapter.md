# Chapter 12: CI/CD for Machine Learning

## What You Will Learn

In this chapter, you will learn:

- What CI/CD means and why ML projects need it
- How to use GitHub Actions for automated testing
- How to create automated training pipelines
- How to implement model validation gates that prevent bad models from reaching production

## Why This Chapter Matters

Imagine you run a bakery with 10 bakers. Each baker makes cakes independently. One day, a baker uses salt instead of sugar, but nobody catches the mistake until customers complain. The next day, another baker changes the recipe without telling anyone.

CI/CD prevents this chaos. CI (Continuous Integration) means every change is automatically tested. CD (Continuous Deployment) means tested changes are automatically deployed. In ML, this means every code change is tested, every model is validated, and only good models make it to production.

---

## What Is CI/CD?

```
+--------------------------------------------------+
|  CI/CD Explained                                  |
|                                                   |
|  CI = Continuous Integration                     |
|  "Every code change is automatically tested"     |
|                                                   |
|  Developer pushes code                           |
|       |                                           |
|       v                                           |
|  Automated tests run                             |
|       |                                           |
|       +-- Tests pass?  --> Merge allowed         |
|       |                                           |
|       +-- Tests fail?  --> Fix before merging    |
|                                                   |
|  CD = Continuous Deployment                      |
|  "Tested code is automatically deployed"         |
|                                                   |
|  Tests pass                                      |
|       |                                           |
|       v                                           |
|  Automatically deploy to production              |
+--------------------------------------------------+
```

### CI/CD for ML Is Special

ML CI/CD has extra challenges compared to regular software:

```
+--------------------------------------------------+
|  Regular Software CI/CD    ML CI/CD               |
|                                                   |
|  Test code                 Test code              |
|  Deploy code               Test data quality      |
|                             Test model performance |
|                             Validate predictions   |
|                             Deploy model + code    |
|                             Monitor model health   |
+--------------------------------------------------+
```

---

## GitHub Actions Basics

GitHub Actions is a CI/CD service built into GitHub. When you push code, it automatically runs tasks you define in a YAML file.

```
+--------------------------------------------------+
|  How GitHub Actions Works                         |
|                                                   |
|  1. You push code to GitHub                      |
|  2. GitHub reads .github/workflows/*.yml files   |
|  3. GitHub creates a virtual machine             |
|  4. The VM runs your defined steps               |
|  5. Results are shown on GitHub                  |
|                                                   |
|  It is like having a robot assistant that         |
|  checks your work every time you submit it.      |
+--------------------------------------------------+
```

### Your First GitHub Action

```yaml
# .github/workflows/test.yml
# This file tells GitHub Actions what to do

name: Run Tests  # Name shown in the GitHub UI

# When should this run?
on:
  push:
    branches: [main]      # On push to main branch
  pull_request:
    branches: [main]      # On pull requests to main

# What should it do?
jobs:
  test:
    runs-on: ubuntu-latest  # Use a Linux virtual machine

    steps:
      # Step 1: Get the code
      - name: Checkout code
        uses: actions/checkout@v4

      # Step 2: Set up Python
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      # Step 3: Install dependencies
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest

      # Step 4: Run tests
      - name: Run tests
        run: pytest tests/ -v
```

**Line-by-line explanation:**

```yaml
name: Run Tests
```

This is the name of the workflow. It appears in the GitHub Actions tab.

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

This defines when the workflow runs. It triggers on pushes to main and on pull requests targeting main.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
```

Jobs are the actual work. `runs-on: ubuntu-latest` means GitHub creates a fresh Ubuntu Linux machine for each run.

```yaml
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
```

Steps are individual tasks within a job. `actions/checkout@v4` is a pre-built action that downloads your code into the virtual machine.

---

## CI/CD Pipeline for ML Projects

### Testing Data Quality

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  # Job 1: Test code quality
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest flake8

      - name: Lint code
        run: flake8 src/ --max-line-length 100

      - name: Run unit tests
        run: pytest tests/ -v

  # Job 2: Validate data
  data-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Validate data quality
        run: python scripts/validate_data.py

  # Job 3: Train and evaluate model
  train-model:
    runs-on: ubuntu-latest
    needs: [code-quality, data-validation]  # Wait for previous jobs
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Train model
        run: python scripts/train.py --config config.yaml

      - name: Evaluate model
        run: python scripts/evaluate.py

      - name: Check model quality gates
        run: python scripts/check_gates.py
```

### Data Validation Script

```python
"""
scripts/validate_data.py - Validate data quality in CI/CD.

This script runs as part of the CI/CD pipeline to
ensure the data meets quality standards before training.
"""

import pandas as pd
import sys
import json


def validate_data(data_path, rules_path=None):
    """
    Validate a dataset against quality rules.

    Parameters
    ----------
    data_path : str
        Path to the dataset CSV.
    rules_path : str, optional
        Path to validation rules JSON.

    Returns
    -------
    tuple
        (passed: bool, report: dict)
    """
    print(f"Validating data: {data_path}")
    print("=" * 50)

    df = pd.read_csv(data_path)
    checks = []

    # Check 1: File is not empty
    if len(df) > 0:
        checks.append(("Not empty", True, f"{len(df)} rows"))
    else:
        checks.append(("Not empty", False, "File is empty!"))

    # Check 2: Required columns exist
    required_columns = ["age", "income", "credit_score", "target"]
    missing = [c for c in required_columns if c not in df.columns]
    if not missing:
        checks.append(("Required columns", True, "All present"))
    else:
        checks.append(("Required columns", False, f"Missing: {missing}"))

    # Check 3: No excessive missing values (max 5%)
    max_missing_pct = 0.05
    missing_pct = df.isnull().mean()
    worst_column = missing_pct.max()
    if worst_column <= max_missing_pct:
        checks.append((
            "Missing values",
            True,
            f"Max: {worst_column:.1%}",
        ))
    else:
        checks.append((
            "Missing values",
            False,
            f"Max: {worst_column:.1%} (limit: {max_missing_pct:.0%})",
        ))

    # Check 4: No duplicate rows (max 1%)
    dupe_pct = df.duplicated().mean()
    if dupe_pct <= 0.01:
        checks.append(("Duplicates", True, f"{dupe_pct:.2%}"))
    else:
        checks.append(("Duplicates", False, f"{dupe_pct:.2%} (limit: 1%)"))

    # Check 5: Target column has expected values
    if "target" in df.columns:
        unique_targets = df["target"].nunique()
        if unique_targets >= 2:
            checks.append((
                "Target classes",
                True,
                f"{unique_targets} classes",
            ))
        else:
            checks.append((
                "Target classes",
                False,
                f"Only {unique_targets} class(es)!",
            ))

    # Check 6: Minimum dataset size
    min_size = 100
    if len(df) >= min_size:
        checks.append(("Minimum size", True, f"{len(df)} >= {min_size}"))
    else:
        checks.append(("Minimum size", False, f"{len(df)} < {min_size}"))

    # Print results
    all_passed = True
    for name, passed, detail in checks:
        status = "PASS" if passed else "FAIL"
        symbol = "[+]" if passed else "[-]"
        print(f"  {symbol} {name}: {status} ({detail})")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("All data validation checks PASSED")
    else:
        print("Data validation FAILED")

    return all_passed


if __name__ == "__main__":
    data_path = "data/training_data.csv"
    passed = validate_data(data_path)

    if not passed:
        print("\nExiting with error code 1")
        sys.exit(1)  # Non-zero exit code = CI/CD failure
```

```
Output (all checks pass):
Validating data: data/training_data.csv
==================================================
  [+] Not empty: PASS (1000 rows)
  [+] Required columns: PASS (All present)
  [+] Missing values: PASS (Max: 1.2%)
  [+] Duplicates: PASS (0.30%)
  [+] Target classes: PASS (2 classes)
  [+] Minimum size: PASS (1000 >= 100)
==================================================
All data validation checks PASSED
```

---

## Model Validation Gates

A validation gate is a check that must pass before a model can be deployed. It is like a quality control checkpoint in a factory.

```
+--------------------------------------------------+
|  Model Validation Gates                           |
|                                                   |
|  Gate 1: Minimum accuracy (e.g., > 0.85)        |
|  Gate 2: Better than current production model    |
|  Gate 3: No performance regression on key groups |
|  Gate 4: Prediction latency under threshold      |
|  Gate 5: Model size within limits                |
|                                                   |
|  ALL gates must pass for deployment!             |
+--------------------------------------------------+
```

```python
"""
scripts/check_gates.py - Model validation gates for CI/CD.

This script checks if a trained model meets all quality
requirements before it can be deployed.
"""

import joblib
import json
import sys
import time
import os
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split


def check_model_gates(model_path, test_data_path=None):
    """
    Run all validation gates on a trained model.

    Parameters
    ----------
    model_path : str
        Path to the trained model file.
    test_data_path : str, optional
        Path to test data. If None, uses synthetic data.

    Returns
    -------
    tuple
        (all_passed: bool, results: list)
    """
    print("Model Validation Gates")
    print("=" * 55)

    gates = []

    # Load model
    model = joblib.load(model_path)

    # Load or create test data
    if test_data_path:
        import pandas as pd
        df = pd.read_csv(test_data_path)
        X_test = df.drop("target", axis=1).values
        y_test = df["target"].values
    else:
        X, y = make_classification(
            n_samples=1000, n_features=10,
            n_classes=2, random_state=42,
        )
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42,
        )

    predictions = model.predict(X_test)

    # Gate 1: Minimum accuracy
    accuracy = accuracy_score(y_test, predictions)
    min_accuracy = float(os.getenv("MIN_ACCURACY", "0.85"))
    gate1_passed = accuracy >= min_accuracy
    gates.append({
        "gate": "Minimum Accuracy",
        "passed": gate1_passed,
        "value": f"{accuracy:.4f}",
        "threshold": f">= {min_accuracy}",
    })

    # Gate 2: Minimum F1 score
    f1 = f1_score(y_test, predictions, average="weighted")
    min_f1 = 0.80
    gate2_passed = f1 >= min_f1
    gates.append({
        "gate": "Minimum F1 Score",
        "passed": gate2_passed,
        "value": f"{f1:.4f}",
        "threshold": f">= {min_f1}",
    })

    # Gate 3: Prediction latency
    # Time how long predictions take
    start = time.time()
    for _ in range(100):
        model.predict(X_test[:1])
    avg_latency_ms = (time.time() - start) / 100 * 1000

    max_latency_ms = 50.0
    gate3_passed = avg_latency_ms <= max_latency_ms
    gates.append({
        "gate": "Prediction Latency",
        "passed": gate3_passed,
        "value": f"{avg_latency_ms:.2f} ms",
        "threshold": f"<= {max_latency_ms} ms",
    })

    # Gate 4: Model file size
    model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
    max_size_mb = 500.0
    gate4_passed = model_size_mb <= max_size_mb
    gates.append({
        "gate": "Model File Size",
        "passed": gate4_passed,
        "value": f"{model_size_mb:.1f} MB",
        "threshold": f"<= {max_size_mb} MB",
    })

    # Gate 5: No class with zero predictions
    unique_preds = set(predictions)
    all_classes_predicted = len(unique_preds) >= 2
    gates.append({
        "gate": "All Classes Predicted",
        "passed": all_classes_predicted,
        "value": f"{len(unique_preds)} classes",
        "threshold": ">= 2 classes",
    })

    # Print results
    all_passed = True
    for gate in gates:
        status = "PASS" if gate["passed"] else "FAIL"
        symbol = "[+]" if gate["passed"] else "[-]"
        print(
            f"  {symbol} {gate['gate']:<25} "
            f"{status:>4} | "
            f"Value: {gate['value']:<15} "
            f"Threshold: {gate['threshold']}"
        )
        if not gate["passed"]:
            all_passed = False

    print("=" * 55)
    if all_passed:
        print("ALL GATES PASSED - Model approved for deployment!")
    else:
        print("GATES FAILED - Model NOT approved for deployment.")

    # Save results as JSON (for CI/CD reporting)
    results = {
        "all_passed": all_passed,
        "gates": gates,
        "model_path": model_path,
    }
    with open("gate_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return all_passed, gates


if __name__ == "__main__":
    model_path = os.getenv(
        "MODEL_PATH", "models/trained_model.pkl"
    )
    passed, _ = check_model_gates(model_path)

    if not passed:
        sys.exit(1)
```

```
Output:
Model Validation Gates
=======================================================
  [+] Minimum Accuracy          PASS | Value: 0.9350          Threshold: >= 0.85
  [+] Minimum F1 Score          PASS | Value: 0.9348          Threshold: >= 0.8
  [+] Prediction Latency        PASS | Value: 2.34 ms         Threshold: <= 50.0 ms
  [+] Model File Size           PASS | Value: 12.5 MB         Threshold: <= 500.0 MB
  [+] All Classes Predicted     PASS | Value: 2 classes       Threshold: >= 2 classes
=======================================================
ALL GATES PASSED - Model approved for deployment!
```

---

## Automated Training Pipeline

```yaml
# .github/workflows/train-and-deploy.yml
name: Train and Deploy Model

on:
  # Run weekly on Mondays at 6 AM UTC
  schedule:
    - cron: "0 6 * * 1"

  # Also allow manual triggering
  workflow_dispatch:
    inputs:
      force_deploy:
        description: "Force deployment even if model is not better"
        required: false
        default: "false"

jobs:
  train:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Validate data
        run: python scripts/validate_data.py

      - name: Train model
        run: python scripts/train.py --config config.yaml
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}

      - name: Run validation gates
        run: python scripts/check_gates.py
        env:
          MODEL_PATH: models/trained_model.pkl
          MIN_ACCURACY: "0.85"

      - name: Upload model artifact
        uses: actions/upload-artifact@v4
        with:
          name: trained-model
          path: |
            models/trained_model.pkl
            gate_results.json

  deploy:
    runs-on: ubuntu-latest
    needs: train  # Only runs after train succeeds
    if: github.ref == 'refs/heads/main'  # Only deploy from main

    steps:
      - uses: actions/checkout@v4

      - name: Download model artifact
        uses: actions/download-artifact@v4
        with:
          name: trained-model

      - name: Deploy to production
        run: |
          echo "Deploying model to production..."
          # In practice, this would:
          # - Push Docker image to registry
          # - Update the running service
          # - Register model in MLflow registry
          echo "Deployment complete!"
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

---

## Complete CI/CD Flow

```
+------------------------------------------------------------------+
|  ML CI/CD Pipeline                                                |
|                                                                    |
|  Developer pushes code to GitHub                                  |
|       |                                                            |
|       v                                                            |
|  [Code Quality]   Run linter and unit tests                      |
|       |                                                            |
|       +-- Fail? --> Developer must fix and push again             |
|       |                                                            |
|       v  Pass                                                     |
|  [Data Validation] Check data quality                            |
|       |                                                            |
|       +-- Fail? --> Alert: data issue                             |
|       |                                                            |
|       v  Pass                                                     |
|  [Model Training]  Train the model                               |
|       |                                                            |
|       v                                                            |
|  [Validation Gates] Check accuracy, latency, size                |
|       |                                                            |
|       +-- Fail? --> Alert: model does not meet standards          |
|       |                                                            |
|       v  Pass                                                     |
|  [Deploy]          Push to production                            |
|       |                                                            |
|       v                                                            |
|  [Monitor]         Watch model performance                       |
+------------------------------------------------------------------+
```

---

## Common Mistakes

1. **No tests at all.** Even basic tests catch many bugs before they reach production.

2. **Testing only code, not data or models.** ML CI/CD must validate data quality and model performance, not just code.

3. **Hard-coding secrets in YAML files.** Use GitHub Secrets for API keys, tokens, and passwords. Never put them in code.

4. **No validation gates.** Without gates, a terrible model can be deployed automatically.

5. **Deploying from any branch.** Only deploy from the main branch. Use pull requests for code review.

---

## Best Practices

1. **Test at multiple levels.** Test code (unit tests), data (validation), and models (performance gates).

2. **Use GitHub Secrets for sensitive values.** Never commit API keys, passwords, or tokens to your repository.

3. **Make gates configurable.** Use environment variables for thresholds so you can adjust them without changing code.

4. **Run tests on pull requests.** Catch problems before code is merged, not after.

5. **Save artifacts.** Upload trained models and test results as GitHub Actions artifacts for later review.

6. **Use scheduled workflows.** Retrain models on a schedule (weekly, monthly) to keep them fresh.

---

## Quick Summary

CI/CD for ML automates testing, training, and deployment. GitHub Actions runs workflows automatically when code changes. Data validation checks ensure data quality. Model validation gates ensure model quality. Together, they create a pipeline where only tested code and validated models reach production.

---

## Key Points

- CI ensures every code change is automatically tested
- CD automates deployment of tested changes
- ML CI/CD adds data validation and model validation gates
- GitHub Actions workflows are defined in YAML files
- Validation gates prevent bad models from reaching production
- Use GitHub Secrets for sensitive configuration
- Schedule automatic retraining to keep models fresh

---

## Practice Questions

1. What is the difference between CI and CD?

2. Why does ML CI/CD need more than just code testing?

3. What is a validation gate? Give three examples of gates for an ML model.

4. Why should you use GitHub Secrets instead of putting API keys directly in your workflow file?

5. How does the `needs` keyword work in GitHub Actions?

---

## Exercises

### Exercise 1: Basic CI Pipeline

Create a GitHub Actions workflow that:
- Triggers on pull requests
- Installs Python dependencies
- Runs pytest
- Checks code style with flake8

### Exercise 2: Model Quality Gates

Write a Python script with at least 5 validation gates:
- Minimum accuracy
- Minimum F1 score
- Maximum prediction latency
- Maximum model file size
- Balanced predictions across classes

The script should exit with code 1 if any gate fails.

### Exercise 3: Full ML Pipeline

Design a complete CI/CD pipeline (as a GitHub Actions YAML file) that:
- Validates data quality
- Trains a model
- Runs validation gates
- Deploys only if all checks pass
- Sends a notification on failure

---

## What Is Next?

CI/CD automates the process of testing and deploying models. But what triggers retraining in the first place? In Chapter 13, we will learn about automated retraining: how to detect when a model needs updating and how to orchestrate the retraining process automatically.
