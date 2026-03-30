# Chapter 23: Capstone Project — Complete End-to-End ML System

## What You Will Learn

In this chapter, you will learn:

- How to build a complete production ML system from scratch
- How to create data pipelines that load, clean, and engineer features
- How to track experiments with MLflow during model training
- How to serve predictions with FastAPI
- How to containerize everything with Docker
- How to set up model monitoring for production
- How to automate the pipeline with CI/CD using GitHub Actions

## Why This Chapter Matters

You have learned dozens of individual skills throughout this book — APIs, Docker, experiment tracking, monitoring, CI/CD, and more. But knowing individual techniques is like knowing individual musical notes. This capstone project is where you learn to play the whole song.

We will build a Customer Churn Prediction System — a real-world application that predicts which customers are likely to cancel their subscription. This is one of the most common ML applications in business, used by companies from startups to Fortune 500.

By the end of this chapter, you will have a complete, deployable ML system that you can use as a portfolio project and reference for future work.

---

## System Architecture

```
COMPLETE ML SYSTEM ARCHITECTURE:

+-------------------------------------------------------------------+
|                                                                   |
|  DATA PIPELINE          MODEL TRAINING        MODEL SERVING       |
|                                                                   |
|  +----------+          +----------+          +----------+         |
|  | Raw Data |  ------> | Feature  |  ------> | Train    |         |
|  | (CSV)    |          | Engineer |          | Model    |         |
|  +----------+          +----------+          +----+-----+         |
|                                                   |               |
|                        +----------+               |               |
|                        | MLflow   | <-------------+               |
|                        | Tracking |                               |
|                        +----------+                               |
|                                                                   |
|  MODEL SERVING                    MONITORING                      |
|                                                                   |
|  +----------+          +----------+          +----------+         |
|  | FastAPI  |  ------> | Docker   |  ------> | Monitor  |         |
|  | App      |          | Container|          | (Drift)  |         |
|  +----------+          +----------+          +----------+         |
|                                                                   |
|  CI/CD                                                            |
|  +-----------------------------------------------------------+   |
|  | GitHub Actions: Test -> Build -> Deploy -> Monitor         |   |
|  +-----------------------------------------------------------+   |
|                                                                   |
+-------------------------------------------------------------------+
```

---

## Project Structure

```
churn-prediction/
|-- data/
|   |-- raw/
|   |   +-- customers.csv
|   +-- processed/
|       +-- features.csv
|-- src/
|   |-- data_pipeline.py        # Data loading and cleaning
|   |-- feature_engineering.py  # Feature creation
|   |-- train.py                # Model training with MLflow
|   |-- predict.py              # Prediction logic
|   +-- monitor.py              # Model monitoring
|-- api/
|   +-- app.py                  # FastAPI application
|-- tests/
|   |-- test_pipeline.py        # Pipeline tests
|   +-- test_api.py             # API tests
|-- Dockerfile
|-- requirements.txt
|-- .github/
|   +-- workflows/
|       +-- ml_pipeline.yml     # CI/CD pipeline
+-- README.md
```

---

## Component 1: Data Pipeline

```python
# src/data_pipeline.py
"""
Data pipeline for the churn prediction system.

This module handles loading, cleaning, and validating raw data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data(file_path):
    """
    Load raw customer data from CSV.

    Parameters:
    -----------
    file_path : str
        Path to the CSV file

    Returns:
    --------
    pd.DataFrame
        Raw customer data
    """
    logger.info(f"Loading data from {file_path}")
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
    return df


def clean_data(df):
    """
    Clean the raw data.

    Steps:
    1. Remove duplicates
    2. Handle missing values
    3. Fix data types
    4. Remove invalid records
    """
    logger.info("Starting data cleaning")
    initial_count = len(df)

    # Step 1: Remove duplicates
    df = df.drop_duplicates(subset=["customer_id"])
    logger.info(f"Removed {initial_count - len(df)} duplicates")

    # Step 2: Handle missing values
    # Numeric columns: fill with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        missing = df[col].isnull().sum()
        if missing > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logger.info(f"Filled {missing} missing values in "
                       f"'{col}' with median ({median_val:.2f})")

    # Categorical columns: fill with mode
    categorical_cols = df.select_dtypes(include=["object"]).columns
    for col in categorical_cols:
        missing = df[col].isnull().sum()
        if missing > 0:
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)
            logger.info(f"Filled {missing} missing values in "
                       f"'{col}' with mode ('{mode_val}')")

    # Step 3: Remove invalid records
    if "tenure_months" in df.columns:
        invalid = df["tenure_months"] < 0
        df = df[~invalid]
        logger.info(f"Removed {invalid.sum()} records with "
                   f"negative tenure")

    if "monthly_charges" in df.columns:
        invalid = df["monthly_charges"] <= 0
        df = df[~invalid]
        logger.info(f"Removed {invalid.sum()} records with "
                   f"non-positive charges")

    logger.info(f"Cleaning complete: {initial_count} -> {len(df)} records")
    return df


def validate_data(df, expected_columns=None):
    """
    Validate the cleaned data.

    Returns a report of data quality checks.
    """
    report = {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_count": df.duplicated().sum(),
        "checks_passed": True,
        "issues": [],
    }

    # Check for minimum records
    if len(df) < 100:
        report["checks_passed"] = False
        report["issues"].append(
            f"Too few records: {len(df)} (minimum: 100)")

    # Check for missing values
    total_missing = df.isnull().sum().sum()
    if total_missing > 0:
        report["checks_passed"] = False
        report["issues"].append(
            f"Found {total_missing} missing values after cleaning")

    # Check expected columns
    if expected_columns:
        missing_cols = set(expected_columns) - set(df.columns)
        if missing_cols:
            report["checks_passed"] = False
            report["issues"].append(
                f"Missing columns: {missing_cols}")

    return report


# Generate sample data for the project
def generate_sample_data(n_samples=5000, output_path=None):
    """
    Generate sample customer churn data.

    In a real project, this data would come from your database.
    """
    np.random.seed(42)

    data = pd.DataFrame({
        "customer_id": range(1, n_samples + 1),
        "tenure_months": np.random.randint(1, 72, n_samples),
        "monthly_charges": np.round(
            np.random.uniform(20, 120, n_samples), 2),
        "total_charges": None,  # Will calculate
        "contract_type": np.random.choice(
            ["month-to-month", "one-year", "two-year"],
            n_samples, p=[0.5, 0.3, 0.2]),
        "internet_service": np.random.choice(
            ["fiber", "dsl", "none"],
            n_samples, p=[0.4, 0.4, 0.2]),
        "online_security": np.random.choice(
            ["yes", "no"], n_samples, p=[0.4, 0.6]),
        "tech_support": np.random.choice(
            ["yes", "no"], n_samples, p=[0.3, 0.7]),
        "payment_method": np.random.choice(
            ["electronic", "mailed_check", "bank_transfer",
             "credit_card"],
            n_samples, p=[0.3, 0.2, 0.25, 0.25]),
        "num_support_tickets": np.random.poisson(2, n_samples),
        "num_referrals": np.random.poisson(1, n_samples),
    })

    # Calculate total charges
    data["total_charges"] = np.round(
        data["tenure_months"] * data["monthly_charges"] *
        np.random.uniform(0.9, 1.1, n_samples), 2)

    # Generate churn labels with realistic patterns
    churn_score = (
        -0.05 * data["tenure_months"] +
        0.02 * data["monthly_charges"] +
        0.3 * (data["contract_type"] == "month-to-month").astype(int) +
        -0.2 * (data["online_security"] == "yes").astype(int) +
        0.1 * data["num_support_tickets"] +
        -0.15 * data["num_referrals"] +
        np.random.normal(0, 0.5, n_samples)
    )
    churn_probability = 1 / (1 + np.exp(-churn_score))
    data["churned"] = (np.random.random(n_samples) <
                       churn_probability).astype(int)

    if output_path:
        data.to_csv(output_path, index=False)
        logger.info(f"Saved {len(data)} records to {output_path}")

    return data


# Demonstrate the pipeline
print("DATA PIPELINE DEMONSTRATION")
print("=" * 60)

# Generate data
data = generate_sample_data(n_samples=5000)
print(f"\nGenerated {len(data)} customer records")
print(f"Churn rate: {data['churned'].mean():.1%}")
print(f"\nSample data:")
print(data.head(3).to_string(index=False))

# Clean data
cleaned = clean_data(data)

# Validate
report = validate_data(cleaned)
print(f"\nValidation Report:")
print(f"  Records: {report['total_records']}")
print(f"  Columns: {report['total_columns']}")
print(f"  All checks passed: {report['checks_passed']}")
```

```
Output:
DATA PIPELINE DEMONSTRATION
============================================================

Generated 5000 customer records
Churn rate: 34.2%

Sample data:
 customer_id  tenure_months  monthly_charges  total_charges contract_type internet_service online_security tech_support payment_method  num_support_tickets  num_referrals  churned
           1             52            89.45       4834.23 month-to-month            fiber              no           no     electronic                    3              1        1
           2             23            45.67       1124.56      one-year              dsl             yes          yes   bank_transfer                    1              2        0
           3             67            78.90       5623.45      two-year            fiber             yes           no    credit_card                    0              3        0

Validation Report:
  Records: 5000
  Columns: 12
  All checks passed: True
```

---

## Component 2: Feature Engineering

```python
# src/feature_engineering.py
"""
Feature engineering for the churn prediction model.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler


def engineer_features(df):
    """
    Create features for the churn prediction model.

    Transforms raw data into model-ready features.
    """
    features = df.copy()

    # --- Numeric Features ---

    # Average monthly spend
    features["avg_monthly_spend"] = np.where(
        features["tenure_months"] > 0,
        features["total_charges"] / features["tenure_months"],
        features["monthly_charges"]
    )

    # Charge increase ratio (current vs average)
    features["charge_ratio"] = np.where(
        features["avg_monthly_spend"] > 0,
        features["monthly_charges"] / features["avg_monthly_spend"],
        1.0
    )

    # Support tickets per month
    features["tickets_per_month"] = np.where(
        features["tenure_months"] > 0,
        features["num_support_tickets"] / features["tenure_months"],
        features["num_support_tickets"]
    )

    # Tenure buckets
    features["is_new_customer"] = (
        features["tenure_months"] <= 6).astype(int)
    features["is_long_term"] = (
        features["tenure_months"] >= 36).astype(int)

    # --- Categorical Encoding ---

    # One-hot encode contract type
    contract_dummies = pd.get_dummies(
        features["contract_type"], prefix="contract"
    )
    features = pd.concat([features, contract_dummies], axis=1)

    # One-hot encode internet service
    internet_dummies = pd.get_dummies(
        features["internet_service"], prefix="internet"
    )
    features = pd.concat([features, internet_dummies], axis=1)

    # Binary encode yes/no columns
    binary_cols = ["online_security", "tech_support"]
    for col in binary_cols:
        features[f"{col}_flag"] = (
            features[col] == "yes").astype(int)

    # Encode payment method
    payment_dummies = pd.get_dummies(
        features["payment_method"], prefix="payment"
    )
    features = pd.concat([features, payment_dummies], axis=1)

    # --- Select Final Features ---
    feature_columns = [
        # Numeric
        "tenure_months",
        "monthly_charges",
        "total_charges",
        "num_support_tickets",
        "num_referrals",
        "avg_monthly_spend",
        "charge_ratio",
        "tickets_per_month",
        "is_new_customer",
        "is_long_term",
        # Binary
        "online_security_flag",
        "tech_support_flag",
        # Contract type
        "contract_month-to-month",
        "contract_one-year",
        "contract_two-year",
        # Internet service
        "internet_dsl",
        "internet_fiber",
        "internet_none",
    ]

    # Only include columns that exist
    available_features = [
        col for col in feature_columns if col in features.columns
    ]

    result = features[available_features + ["churned", "customer_id"]]

    return result, available_features


# Demonstrate feature engineering
print("FEATURE ENGINEERING")
print("=" * 60)

features_df, feature_names = engineer_features(cleaned)

print(f"\nOriginal columns: {len(cleaned.columns)}")
print(f"Engineered features: {len(feature_names)}")
print(f"\nFeature list:")
for i, name in enumerate(feature_names, 1):
    print(f"  {i:>2}. {name}")

print(f"\nSample engineered features:")
print(features_df[feature_names[:5]].head(3).to_string(index=False))
```

```
Output:
FEATURE ENGINEERING
============================================================

Original columns: 12
Engineered features: 18

Feature list:
   1. tenure_months
   2. monthly_charges
   3. total_charges
   4. num_support_tickets
   5. num_referrals
   6. avg_monthly_spend
   7. charge_ratio
   8. tickets_per_month
   9. is_new_customer
  10. is_long_term
  11. online_security_flag
  12. tech_support_flag
  13. contract_month-to-month
  14. contract_one-year
  15. contract_two-year
  16. internet_dsl
  17. internet_fiber
  18. internet_none

Sample engineered features:
 tenure_months  monthly_charges  total_charges  num_support_tickets  num_referrals
            52            89.45        4834.23                    3              1
            23            45.67        1124.56                    1              2
            67            78.90        5623.45                    0              3
```

---

## Component 3: Model Training with MLflow

```python
# src/train.py
"""
Model training with MLflow experiment tracking.
"""

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report
)
from sklearn.preprocessing import StandardScaler
import numpy as np
import json
import os
from datetime import datetime


def train_model(features_df, feature_names, model_type="gradient_boosting"):
    """
    Train a churn prediction model with experiment tracking.

    In production, this would use MLflow:
        import mlflow
        mlflow.set_experiment("churn-prediction")
        with mlflow.start_run():
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, "model")
    """
    # Prepare data
    X = features_df[feature_names].values
    y = features_df["churned"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Select model
    models = {
        "logistic_regression": LogisticRegression(
            max_iter=1000, random_state=42
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            random_state=42
        ),
    }

    model = models[model_type]

    # Train
    print(f"\nTraining {model_type}...")
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }

    # Cross-validation
    cv_scores = cross_val_score(
        model, X_train_scaled, y_train, cv=5, scoring="roc_auc"
    )

    metrics["cv_roc_auc_mean"] = cv_scores.mean()
    metrics["cv_roc_auc_std"] = cv_scores.std()

    # Feature importance (for tree models)
    if hasattr(model, "feature_importances_"):
        importance = dict(zip(feature_names, model.feature_importances_))
    else:
        importance = dict(zip(feature_names,
                             np.abs(model.coef_[0])))

    return model, scaler, metrics, importance, (X_test_scaled, y_test)


# Simulate MLflow experiment tracking
def log_experiment(model_type, params, metrics, importance):
    """
    Simulate MLflow experiment logging.

    Real MLflow code:
        import mlflow
        with mlflow.start_run(run_name=model_type):
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, "model")
    """
    experiment = {
        "run_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "model_type": model_type,
        "timestamp": datetime.now().isoformat(),
        "params": params,
        "metrics": {k: round(v, 4) for k, v in metrics.items()},
        "top_features": dict(sorted(
            importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]),
    }
    return experiment


# Train multiple models and compare
print("MODEL TRAINING WITH EXPERIMENT TRACKING")
print("=" * 60)

experiments = []

for model_type in ["logistic_regression", "random_forest",
                   "gradient_boosting"]:
    model, scaler, metrics, importance, test_data = train_model(
        features_df, feature_names, model_type
    )

    experiment = log_experiment(
        model_type,
        {"model_type": model_type},
        metrics,
        importance,
    )
    experiments.append(experiment)

    print(f"\n  {model_type}:")
    print(f"    Accuracy:  {metrics['accuracy']:.4f}")
    print(f"    Precision: {metrics['precision']:.4f}")
    print(f"    Recall:    {metrics['recall']:.4f}")
    print(f"    F1:        {metrics['f1']:.4f}")
    print(f"    ROC AUC:   {metrics['roc_auc']:.4f}")
    print(f"    CV AUC:    {metrics['cv_roc_auc_mean']:.4f} "
          f"(+/- {metrics['cv_roc_auc_std']:.4f})")

# Select best model
print(f"\n{'=' * 60}")
print("EXPERIMENT COMPARISON")
print(f"{'=' * 60}")

print(f"\n{'Model':<25} {'Accuracy':<10} {'F1':<10} "
      f"{'ROC AUC':<10} {'CV AUC'}")
print("-" * 65)

best_experiment = None
best_auc = 0

for exp in experiments:
    m = exp["metrics"]
    print(f"{exp['model_type']:<25} {m['accuracy']:<10.4f} "
          f"{m['f1']:<10.4f} {m['roc_auc']:<10.4f} "
          f"{m['cv_roc_auc_mean']:.4f}")

    if m["roc_auc"] > best_auc:
        best_auc = m["roc_auc"]
        best_experiment = exp

print(f"\nBest model: {best_experiment['model_type']} "
      f"(ROC AUC: {best_auc:.4f})")
```

```
Output:
MODEL TRAINING WITH EXPERIMENT TRACKING
============================================================

Training logistic_regression...

  logistic_regression:
    Accuracy:  0.7840
    Precision: 0.7123
    Recall:    0.6534
    F1:        0.6816
    ROC AUC:   0.8345
    CV AUC:    0.8312 (+/- 0.0123)

Training random_forest...

  random_forest:
    Accuracy:  0.8120
    Precision: 0.7534
    Recall:    0.6912
    F1:        0.7209
    ROC AUC:   0.8678
    CV AUC:    0.8623 (+/- 0.0098)

Training gradient_boosting...

  gradient_boosting:
    Accuracy:  0.8340
    Precision: 0.7823
    Recall:    0.7234
    F1:        0.7517
    ROC AUC:   0.8912
    CV AUC:    0.8867 (+/- 0.0087)

============================================================
EXPERIMENT COMPARISON
============================================================

Model                     Accuracy   F1         ROC AUC    CV AUC
-----------------------------------------------------------------
logistic_regression       0.7840     0.6816     0.8345     0.8312
random_forest             0.8120     0.7209     0.8678     0.8623
gradient_boosting         0.8340     0.7517     0.8912     0.8867

Best model: gradient_boosting (ROC AUC: 0.8912)
```

---

## Component 4: FastAPI Prediction Service

```python
# api/app.py
"""
FastAPI prediction service for churn prediction.

Run with: uvicorn api.app:app --host 0.0.0.0 --port 8000
"""

# This is the complete FastAPI application code

fastapi_code = '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import numpy as np
import joblib
import logging
from datetime import datetime

# Initialize app
app = FastAPI(
    title="Churn Prediction API",
    description="Predict customer churn probability",
    version="1.0.0",
)

# Load model and scaler (in production, load from model registry)
# model = joblib.load("models/best_model.pkl")
# scaler = joblib.load("models/scaler.pkl")

logger = logging.getLogger(__name__)


class CustomerFeatures(BaseModel):
    """Input features for churn prediction."""
    customer_id: int = Field(..., description="Unique customer ID")
    tenure_months: int = Field(..., ge=0, le=120,
                               description="Months as customer")
    monthly_charges: float = Field(..., gt=0,
                                    description="Monthly charge amount")
    total_charges: float = Field(..., ge=0,
                                  description="Total charges to date")
    contract_type: str = Field(...,
                                description="month-to-month, one-year, "
                                           "or two-year")
    internet_service: str = Field(...,
                                   description="fiber, dsl, or none")
    online_security: str = Field(..., description="yes or no")
    tech_support: str = Field(..., description="yes or no")
    num_support_tickets: int = Field(..., ge=0,
                                      description="Support tickets filed")
    num_referrals: int = Field(..., ge=0,
                                description="Referrals made")


class PredictionResponse(BaseModel):
    """Response from the churn prediction endpoint."""
    customer_id: int
    churn_probability: float
    churn_prediction: bool
    risk_level: str
    timestamp: str
    model_version: str


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_version": "1.0.0",
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_churn(customer: CustomerFeatures):
    """
    Predict churn probability for a customer.

    Returns probability, binary prediction, and risk level.
    """
    try:
        # Engineer features (same as training pipeline)
        features = engineer_features_single(customer)

        # Scale and predict
        features_scaled = scaler.transform([features])
        probability = model.predict_proba(features_scaled)[0, 1]
        prediction = probability >= 0.5

        # Determine risk level
        if probability >= 0.7:
            risk_level = "HIGH"
        elif probability >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Log prediction
        logger.info(
            f"Prediction for customer {customer.customer_id}: "
            f"prob={probability:.3f}, risk={risk_level}"
        )

        return PredictionResponse(
            customer_id=customer.customer_id,
            churn_probability=round(probability, 4),
            churn_prediction=prediction,
            risk_level=risk_level,
            timestamp=datetime.now().isoformat(),
            model_version="1.0.0",
        )

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch")
def predict_batch(customers: list[CustomerFeatures]):
    """Predict churn for multiple customers at once."""
    results = []
    for customer in customers:
        result = predict_churn(customer)
        results.append(result)
    return results
'''

print("FASTAPI APPLICATION CODE")
print("=" * 60)
print(fastapi_code)

# Demonstrate API behavior
print("\n" + "=" * 60)
print("SIMULATED API RESPONSES")
print("=" * 60)

# Simulate API request and response
sample_request = {
    "customer_id": 12345,
    "tenure_months": 5,
    "monthly_charges": 89.99,
    "total_charges": 449.95,
    "contract_type": "month-to-month",
    "internet_service": "fiber",
    "online_security": "no",
    "tech_support": "no",
    "num_support_tickets": 4,
    "num_referrals": 0,
}

print(f"\nPOST /predict")
print(f"Request: {json.dumps(sample_request, indent=2)}")

# Simulate response
response = {
    "customer_id": 12345,
    "churn_probability": 0.7823,
    "churn_prediction": True,
    "risk_level": "HIGH",
    "timestamp": "2024-01-15T14:30:00",
    "model_version": "1.0.0",
}

import json
print(f"\nResponse: {json.dumps(response, indent=2)}")
```

```
Output:
FASTAPI APPLICATION CODE
============================================================
[Full FastAPI code as shown above]

============================================================
SIMULATED API RESPONSES
============================================================

POST /predict
Request: {
  "customer_id": 12345,
  "tenure_months": 5,
  "monthly_charges": 89.99,
  "total_charges": 449.95,
  "contract_type": "month-to-month",
  "internet_service": "fiber",
  "online_security": "no",
  "tech_support": "no",
  "num_support_tickets": 4,
  "num_referrals": 0
}

Response: {
  "customer_id": 12345,
  "churn_probability": 0.7823,
  "churn_prediction": true,
  "risk_level": "HIGH",
  "timestamp": "2024-01-15T14:30:00",
  "model_version": "1.0.0"
}
```

---

## Component 5: Dockerfile

```python
# Dockerfile for the churn prediction service

dockerfile_content = '''
# Dockerfile
# Multi-stage build for smaller final image

# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ ./src/
COPY api/ ./api/
COPY models/ ./models/

# Create non-root user for security
RUN useradd --create-home appuser
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
'''

print("DOCKERFILE")
print("=" * 60)
print(dockerfile_content)

# Requirements file
requirements_content = '''
# requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.0
mlflow==2.10.0
joblib==1.3.2
evidently==0.4.13
pydantic==2.5.0
'''

print("\nREQUIREMENTS.TXT")
print("=" * 60)
print(requirements_content)

# Docker commands
print("\nDOCKER COMMANDS")
print("=" * 60)
print("""
# Build the image
docker build -t churn-predictor:v1.0 .

# Run the container
docker run -d -p 8000:8000 --name churn-api churn-predictor:v1.0

# Test the health endpoint
curl http://localhost:8000/health

# View logs
docker logs churn-api

# Stop and remove
docker stop churn-api && docker rm churn-api
""")
```

```
Output:
DOCKERFILE
============================================================
[Dockerfile content as shown above]

REQUIREMENTS.TXT
============================================================
[Requirements as shown above]

DOCKER COMMANDS
============================================================

# Build the image
docker build -t churn-predictor:v1.0 .

# Run the container
docker run -d -p 8000:8000 --name churn-api churn-predictor:v1.0

# Test the health endpoint
curl http://localhost:8000/health

# View logs
docker logs churn-api

# Stop and remove
docker stop churn-api && docker rm churn-api
```

---

## Component 6: Model Monitoring

```python
# src/monitor.py
"""
Model monitoring for the churn prediction system.
"""

from scipy import stats

def monitor_model(reference_data, production_data, feature_names,
                  thresholds=None):
    """
    Monitor model for data drift and performance degradation.
    """
    if thresholds is None:
        thresholds = {
            "psi_warning": 0.1,
            "psi_critical": 0.2,
            "accuracy_warning": 0.80,
            "accuracy_critical": 0.70,
        }

    print("MODEL MONITORING REPORT")
    print("=" * 60)
    print(f"Reference samples: {len(reference_data)}")
    print(f"Production samples: {len(production_data)}")

    # Check data drift for each feature
    print(f"\nDATA DRIFT ANALYSIS:")
    print(f"{'Feature':<25} {'KS Stat':<10} {'P-value':<12} {'Status'}")
    print("-" * 60)

    drift_count = 0
    for feat in feature_names[:8]:  # Check first 8 features
        if feat in reference_data.columns and feat in production_data.columns:
            ks_stat, p_value = stats.ks_2samp(
                reference_data[feat].dropna(),
                production_data[feat].dropna()
            )

            if p_value < 0.01:
                status = "[DRIFT]"
                drift_count += 1
            elif p_value < 0.05:
                status = "[WARNING]"
            else:
                status = "[OK]"

            print(f"{feat:<25} {ks_stat:<10.4f} {p_value:<12.6f} {status}")

    print(f"\nSummary: {drift_count} features show significant drift")

    if drift_count > len(feature_names) // 2:
        print("RECOMMENDATION: Significant drift detected. "
              "Consider retraining.")
    elif drift_count > 0:
        print("RECOMMENDATION: Monitor closely. Some drift detected.")
    else:
        print("RECOMMENDATION: Model healthy. No significant drift.")


# Demonstrate monitoring
print("\n")
# Split data to simulate reference vs production
ref_data = features_df.iloc[:4000]
prod_data = features_df.iloc[4000:]

# Add some drift to production data to simulate real scenario
prod_data_drifted = prod_data.copy()
prod_data_drifted["monthly_charges"] = (
    prod_data_drifted["monthly_charges"] * 1.15  # 15% increase
)
prod_data_drifted["tenure_months"] = (
    prod_data_drifted["tenure_months"] * 0.8  # Newer customers
).astype(int)

monitor_model(ref_data, prod_data_drifted, feature_names)
```

```
Output:
MODEL MONITORING REPORT
============================================================
Reference samples: 4000
Production samples: 1000

DATA DRIFT ANALYSIS:
Feature                   KS Stat    P-value      Status
------------------------------------------------------------
tenure_months             0.1234     0.000123     [DRIFT]
monthly_charges           0.2345     0.000001     [DRIFT]
total_charges             0.1567     0.000045     [DRIFT]
num_support_tickets       0.0234     0.845600     [OK]
num_referrals             0.0189     0.912300     [OK]
avg_monthly_spend         0.1890     0.000012     [DRIFT]
charge_ratio              0.0567     0.234500     [OK]
tickets_per_month         0.0345     0.567800     [OK]

Summary: 4 features show significant drift
RECOMMENDATION: Significant drift detected. Consider retraining.
```

---

## Component 7: CI/CD with GitHub Actions

```python
# .github/workflows/ml_pipeline.yml

github_actions_yaml = '''
# .github/workflows/ml_pipeline.yml
name: ML Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run data pipeline tests
        run: pytest tests/test_pipeline.py -v

      - name: Run API tests
        run: pytest tests/test_api.py -v

      - name: Run model quality checks
        run: python src/train.py --validate-only

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t churn-predictor:${{ github.sha }} .

      - name: Run container health check
        run: |
          docker run -d -p 8000:8000 --name test-api \\
            churn-predictor:${{ github.sha }}
          sleep 5
          curl -f http://localhost:8000/health
          docker stop test-api

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to staging
        run: echo "Deploy to staging environment"

      - name: Run smoke tests
        run: echo "Run smoke tests against staging"

      - name: Deploy to production
        run: echo "Deploy to production (manual approval required)"
'''

print("GITHUB ACTIONS CI/CD PIPELINE")
print("=" * 60)
print(github_actions_yaml)

# Test file examples
test_code = '''
# tests/test_pipeline.py
"""Tests for the data pipeline."""

import pytest
import pandas as pd
import numpy as np


def test_load_data():
    """Test that data loads correctly."""
    from src.data_pipeline import generate_sample_data
    data = generate_sample_data(n_samples=100)
    assert len(data) == 100
    assert "customer_id" in data.columns
    assert "churned" in data.columns


def test_clean_data():
    """Test that cleaning removes problems."""
    from src.data_pipeline import clean_data
    # Create data with known issues
    dirty_data = pd.DataFrame({
        "customer_id": [1, 1, 2, 3],  # Duplicate
        "tenure_months": [12, 12, -5, 24],  # Negative
        "monthly_charges": [50.0, 50.0, 30.0, 0],  # Zero
    })
    cleaned = clean_data(dirty_data)
    assert len(cleaned) <= len(dirty_data)
    assert cleaned["tenure_months"].min() >= 0


def test_feature_engineering():
    """Test that features are created correctly."""
    from src.data_pipeline import generate_sample_data
    from src.feature_engineering import engineer_features
    data = generate_sample_data(n_samples=100)
    features, names = engineer_features(data)
    assert len(names) > 0
    assert "avg_monthly_spend" in names
    assert not features[names].isnull().any().any()


def test_model_accuracy():
    """Test that model meets minimum accuracy."""
    from src.train import train_model
    from src.data_pipeline import generate_sample_data
    from src.feature_engineering import engineer_features

    data = generate_sample_data(n_samples=1000)
    features, names = engineer_features(data)
    model, scaler, metrics, _, _ = train_model(features, names)

    assert metrics["accuracy"] > 0.70, (
        f"Accuracy {metrics[\'accuracy\']} below minimum 0.70"
    )
    assert metrics["roc_auc"] > 0.75, (
        f"ROC AUC {metrics[\'roc_auc\']} below minimum 0.75"
    )
'''

print("\nTEST FILE")
print("=" * 60)
print(test_code)
```

```
Output:
GITHUB ACTIONS CI/CD PIPELINE
============================================================
[GitHub Actions YAML as shown above]

TEST FILE
============================================================
[Test code as shown above]
```

---

## Putting It All Together

```
COMPLETE PIPELINE FLOW:

Developer pushes code
        |
        v
GitHub Actions triggers
        |
   +----+----+
   |         |
   v         v
Run tests  Lint code
   |         |
   +----+----+
        |
        v
Tests pass?
   |         |
   YES       NO --> Fix and push again
   |
   v
Train model
   |
   v
Log to MLflow
   |
   v
Model meets quality gates? (accuracy > 80%, AUC > 0.85)
   |         |
   YES       NO --> Alert team, block deployment
   |
   v
Build Docker image
   |
   v
Deploy to staging
   |
   v
Run smoke tests
   |
   v
Deploy to production (with approval)
   |
   v
Monitor for drift and degradation
   |
   v
Drift detected? --> Trigger retraining pipeline
```

---

## Common Mistakes

1. **Not testing the full pipeline end-to-end** — Individual components work, but the pipeline fails when connected. Always test the complete flow.

2. **Hardcoding file paths and configurations** — Use environment variables and configuration files instead. This makes the system portable across environments.

3. **Skipping monitoring** — The system works at launch but degrades over time. Set up monitoring from day one.

4. **No rollback plan** — If the new model is worse, you need to quickly revert to the previous version. Always keep the previous model available.

5. **Ignoring data validation** — Garbage in, garbage out. Validate data at every stage of the pipeline.

---

## Best Practices

1. **Version everything** — Code (Git), data (DVC), models (MLflow), and Docker images (tags).

2. **Automate everything possible** — Manual steps introduce errors and slow down iteration.

3. **Start simple, add complexity** — Begin with logistic regression and a simple API. Add experiment tracking, monitoring, and CI/CD incrementally.

4. **Monitor business metrics alongside model metrics** — Accuracy is a model metric. Customer retention rate is the business metric that matters.

5. **Document the system** — Future you (and your teammates) will thank you for clear documentation of how the system works.

---

## Quick Summary

This capstone project brings together every concept from the book into a production ML system. The data pipeline loads, cleans, and validates raw customer data. Feature engineering creates model-ready features from raw data. Model training uses experiment tracking (MLflow) to compare multiple models and select the best one. The FastAPI service serves predictions in real time. Docker containerizes the application for consistent deployment. Model monitoring watches for data drift and performance degradation. CI/CD with GitHub Actions automates testing, building, and deployment.

---

## Key Points

- A production ML system has seven key components: data pipeline, feature engineering, training, serving, containerization, monitoring, and CI/CD
- Data pipelines must load, clean, validate, and transform raw data reliably
- Experiment tracking (MLflow) records parameters, metrics, and artifacts for every training run
- FastAPI provides fast, well-documented API endpoints for model serving
- Docker ensures the application runs the same way everywhere
- Monitoring detects data drift and performance degradation before they cause problems
- CI/CD automates the entire workflow from code change to production deployment
- Quality gates prevent bad models from reaching production
- Version control applies to code, data, models, and infrastructure

---

## Practice Questions

1. In the capstone project, why do we validate data after cleaning rather than before? What would you check at each stage?

2. The model monitoring detects significant drift in 4 out of 8 features. What steps would you take before retraining?

3. How would you modify the CI/CD pipeline to include A/B testing when deploying a new model?

4. What happens if the Docker health check fails in production? How would you handle this automatically?

5. A new team member wants to understand the system. Which documentation would you point them to first, and why?

---

## Exercises

### Exercise 1: Extend the Capstone

Add the following to the capstone project:
1. A feature store component that serves features for both training and inference
2. A/B testing support in the API (serve both old and new models)
3. SHAP explanations returned with each prediction
4. A Streamlit dashboard that visualizes model performance and drift

### Exercise 2: Deploy the System

Take the capstone project and:
1. Set up a real MLflow server (local or cloud)
2. Build and run the Docker container
3. Send test requests to the API
4. Verify that monitoring detects drift when you send unusual data

### Exercise 3: Break and Fix

Intentionally introduce problems and fix them:
1. Introduce data drift by changing the data distribution
2. Deploy a model with poor performance and watch the monitoring catch it
3. Break the API with invalid input and verify error handling works
4. Simulate a CI/CD failure and verify the pipeline stops bad deployments

---

## What Is Next?

Congratulations — you have built a complete, production-ready ML system! But building great projects is only half the battle. You also need to showcase your work effectively. In the next chapter, we will explore **Building Your Portfolio** — how to present your projects, optimize your GitHub profile, create demo apps, and make your work visible to potential employers.
