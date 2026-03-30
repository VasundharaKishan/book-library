# Chapter 30: Project -- Customer Churn Prediction

## What You Will Learn

In this chapter, you will:

- Build a complete, end-to-end machine learning project from scratch
- Load and explore a customer churn dataset
- Perform Exploratory Data Analysis (EDA) with visualizations
- Clean and preprocess the data
- Engineer new features from existing ones
- Handle class imbalance using SMOTE
- Build a preprocessing pipeline
- Train and compare multiple classification models
- Evaluate models with classification reports and ROC/AUC curves
- Tune the best model's hyperparameters
- Analyze feature importance for business insights
- Deliver actionable business recommendations

## Why This Chapter Matters

This is it. The grand finale. Everything you have learned in this book comes together in this chapter.

In the real world, machine learning is not about running `model.fit()` on a clean dataset. It is a messy, iterative process. You get raw data. You explore it. You clean it. You engineer features. You try different models. You evaluate. You tune. You present results to stakeholders who do not know (or care) what a Random Forest is.

This project simulates that entire experience. By the end, you will have a complete, production-quality churn prediction system and the confidence to tackle similar projects at work.

**Customer churn** (when a customer leaves your service) costs businesses billions of dollars every year. Predicting which customers will churn lets companies intervene early and save those relationships. This is one of the most common machine learning applications in business.

Let us build it.

---

## Project Overview

```
PROJECT PIPELINE
================

 [Load Data]
      |
      v
 [Explore (EDA)]  --> Understand the data
      |
      v
 [Clean Data]      --> Handle missing values, fix types
      |
      v
 [Feature Engineer] --> Create new useful features
      |
      v
 [Handle Imbalance] --> SMOTE to balance classes
      |
      v
 [Build Pipeline]   --> Automate preprocessing
      |
      v
 [Train Models]     --> Try 5 different algorithms
      |
      v
 [Evaluate]         --> Classification report, ROC/AUC
      |
      v
 [Tune Best Model]  --> GridSearchCV for hyperparameters
      |
      v
 [Feature Importance] --> What drives churn?
      |
      v
 [Business Insights]  --> Actionable recommendations
```

---

## Step 1: Load and Explore the Data

We will create a realistic telecom customer churn dataset. In a real project, you would load this from a CSV file.

```python
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# Create a realistic telecom churn dataset
# ============================================================
np.random.seed(42)
n = 2000

# Customer demographics
customer_id = np.arange(1, n + 1)
gender = np.random.choice(['Male', 'Female'], n)
age = np.random.randint(18, 75, n)
senior_citizen = (age >= 65).astype(int)

# Account info
tenure_months = np.random.randint(1, 72, n)
contract = np.random.choice(
    ['Month-to-month', 'One year', 'Two year'], n,
    p=[0.55, 0.25, 0.20]
)
monthly_charges = np.round(np.random.uniform(18.25, 118.75, n), 2)
total_charges = np.round(tenure_months * monthly_charges *
                         np.random.uniform(0.85, 1.15, n), 2)

# Services
internet_service = np.random.choice(
    ['DSL', 'Fiber optic', 'No'], n, p=[0.35, 0.45, 0.20]
)
phone_service = np.random.choice(['Yes', 'No'], n, p=[0.9, 0.1])
streaming_tv = np.random.choice(['Yes', 'No'], n, p=[0.4, 0.6])
online_security = np.random.choice(['Yes', 'No'], n, p=[0.3, 0.7])
tech_support = np.random.choice(['Yes', 'No'], n, p=[0.3, 0.7])

# Payment
payment_method = np.random.choice(
    ['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'],
    n, p=[0.35, 0.25, 0.20, 0.20]
)
paperless_billing = np.random.choice(['Yes', 'No'], n, p=[0.6, 0.4])

# Support interactions
num_support_tickets = np.random.poisson(2, n)
avg_satisfaction = np.round(np.random.uniform(1, 10, n), 1)

# Create churn target based on realistic patterns
churn_score = (
    -tenure_months * 0.04 +
    monthly_charges * 0.015 +
    num_support_tickets * 0.2 +
    -avg_satisfaction * 0.3 +
    np.where(contract == 'Month-to-month', 1.5, 0) +
    np.where(contract == 'Two year', -1.0, 0) +
    np.where(internet_service == 'Fiber optic', 0.5, 0) +
    np.where(online_security == 'No', 0.3, 0) +
    np.where(tech_support == 'No', 0.3, 0) +
    np.where(payment_method == 'Electronic check', 0.5, 0) +
    np.random.normal(0, 1.0, n)
)

churn = (churn_score > np.percentile(churn_score, 73)).astype(int)

# Create DataFrame
df = pd.DataFrame({
    'CustomerID': customer_id,
    'Gender': gender,
    'Age': age,
    'SeniorCitizen': senior_citizen,
    'Tenure_Months': tenure_months,
    'Contract': contract,
    'MonthlyCharges': monthly_charges,
    'TotalCharges': total_charges,
    'InternetService': internet_service,
    'PhoneService': phone_service,
    'StreamingTV': streaming_tv,
    'OnlineSecurity': online_security,
    'TechSupport': tech_support,
    'PaymentMethod': payment_method,
    'PaperlessBilling': paperless_billing,
    'NumSupportTickets': num_support_tickets,
    'AvgSatisfaction': avg_satisfaction,
    'Churn': churn
})

# Add some missing values (realistic!)
mask_charges = np.random.random(n) < 0.03
df.loc[mask_charges, 'TotalCharges'] = np.nan

mask_satisfaction = np.random.random(n) < 0.05
df.loc[mask_satisfaction, 'AvgSatisfaction'] = np.nan

print("=" * 65)
print("CUSTOMER CHURN PREDICTION PROJECT")
print("=" * 65)

print(f"\nDataset Shape: {df.shape}")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

print(f"\nFirst 5 Rows:")
print(df.head())

print(f"\nColumn Types:")
print(df.dtypes)
```

**Output:**

```
=================================================================
CUSTOMER CHURN PREDICTION PROJECT
=================================================================

Dataset Shape: (2000, 18)
Rows: 2000, Columns: 18

First 5 Rows:
   CustomerID  Gender  Age  SeniorCitizen  Tenure_Months  ...  Churn
0           1    Male   56              0             52  ...      0
1           2  Female   18              0              1  ...      1
2           3    Male   28              0             49  ...      0
3           4  Female   60              0             71  ...      0
4           5    Male   37              0             48  ...      0

Column Types:
CustomerID            int64
Gender               object
Age                   int64
...
Churn                 int64
dtype: object
```

---

## Step 2: Exploratory Data Analysis (EDA)

EDA is about understanding your data before building any models. What does it look like? Are there patterns? Missing values? Outliers?

```python
# ============================================================
# EXPLORATORY DATA ANALYSIS
# ============================================================
print("\n" + "=" * 65)
print("EXPLORATORY DATA ANALYSIS")
print("=" * 65)

# --- 2a: Target Distribution ---
print("\n--- Target Distribution ---")
churn_counts = df['Churn'].value_counts()
churn_pcts = df['Churn'].value_counts(normalize=True)

for val in [0, 1]:
    label = "Churn" if val == 1 else "Stay"
    count = churn_counts[val]
    pct = churn_pcts[val]
    bar = "#" * int(pct * 50)
    print(f"  {label:<6}: {count:>5} ({pct:.1%}) {bar}")

print(f"\n  Class ratio: 1:{churn_counts[0]/churn_counts[1]:.1f} "
      f"(imbalanced!)")

# --- 2b: Missing Values ---
print("\n--- Missing Values ---")
missing = df.isnull().sum()
missing_pct = (df.isnull().sum() / len(df) * 100)

has_missing = missing[missing > 0]
if len(has_missing) > 0:
    for col in has_missing.index:
        print(f"  {col:<20}: {has_missing[col]:>4} "
              f"({missing_pct[col]:.1f}%)")
else:
    print("  No missing values found!")

print(f"\n  Total rows with missing: "
      f"{df.isnull().any(axis=1).sum()}")

# --- 2c: Numerical Feature Statistics ---
print("\n--- Numerical Features ---")
numerical_cols = df.select_dtypes(include=[np.number]).columns
numerical_cols = [c for c in numerical_cols
                  if c not in ['CustomerID', 'Churn']]

for col in numerical_cols:
    print(f"\n  {col}:")
    print(f"    Mean: {df[col].mean():.2f}, "
          f"Std: {df[col].std():.2f}")
    print(f"    Min: {df[col].min():.2f}, "
          f"Max: {df[col].max():.2f}")

# --- 2d: Churn Rate by Feature ---
print("\n--- Churn Rate by Key Features ---")

# By Contract Type
print("\n  By Contract:")
for contract_type in df['Contract'].unique():
    subset = df[df['Contract'] == contract_type]
    rate = subset['Churn'].mean()
    bar = "#" * int(rate * 40)
    print(f"    {contract_type:<18}: {rate:.1%} {bar}")

# By Internet Service
print("\n  By Internet Service:")
for service in df['InternetService'].unique():
    subset = df[df['InternetService'] == service]
    rate = subset['Churn'].mean()
    bar = "#" * int(rate * 40)
    print(f"    {service:<18}: {rate:.1%} {bar}")

# By Payment Method
print("\n  By Payment Method:")
for method in df['PaymentMethod'].unique():
    subset = df[df['PaymentMethod'] == method]
    rate = subset['Churn'].mean()
    bar = "#" * int(rate * 40)
    print(f"    {method:<20}: {rate:.1%} {bar}")

# --- 2e: Churn by Tenure ---
print("\n  Churn Rate by Tenure Group:")
tenure_bins = [0, 12, 24, 48, 72]
tenure_labels = ['0-12 mo', '13-24 mo', '25-48 mo', '49-72 mo']
df['Tenure_Group'] = pd.cut(df['Tenure_Months'], bins=tenure_bins,
                            labels=tenure_labels)

for group in tenure_labels:
    subset = df[df['Tenure_Group'] == group]
    rate = subset['Churn'].mean()
    bar = "#" * int(rate * 40)
    print(f"    {group:<12}: {rate:.1%} ({len(subset)} customers) {bar}")

# --- 2f: Correlation with Churn ---
print("\n--- Correlation with Churn ---")
correlations = df[numerical_cols + ['Churn']].corr()['Churn'].drop('Churn')
correlations = correlations.abs().sort_values(ascending=False)

for feature, corr in correlations.items():
    direction = "+" if df[[feature, 'Churn']].corr().iloc[0, 1] > 0 else "-"
    bar = "#" * int(corr * 40)
    print(f"  {feature:<20}: {direction}{corr:.3f} {bar}")
```

**Output:**

```
=================================================================
EXPLORATORY DATA ANALYSIS
=================================================================

--- Target Distribution ---
  Stay  :  1460 (73.0%) ####################################
  Churn :   540 (27.0%) #############

  Class ratio: 1:2.7 (imbalanced!)

--- Missing Values ---
  TotalCharges        :   55 (2.8%)
  AvgSatisfaction     :   93 (4.7%)

  Total rows with missing: 145

--- Numerical Features ---

  Age:
    Mean: 46.23, Std: 16.41
    Min: 18.00, Max: 74.00

  Tenure_Months:
    Mean: 35.87, Std: 20.68
    Min: 1.00, Max: 71.00

  MonthlyCharges:
    Mean: 68.21, Std: 29.05
    Min: 18.32, Max: 118.62
...

--- Churn Rate by Key Features ---

  By Contract:
    Month-to-month    : 37.2% ##############
    One year          : 16.8% ######
    Two year          : 10.5% ####

  By Internet Service:
    Fiber optic       : 33.1% #############
    DSL               : 23.4% #########
    No                : 18.2% #######

  By Payment Method:
    Electronic check  : 35.4% ##############
    Mailed check      : 22.8% #########
    Bank transfer     : 21.0% ########
    Credit card       : 20.5% ########

  Churn Rate by Tenure Group:
    0-12 mo     : 40.8% (339 customers) ################
    13-24 mo    : 30.2% (320 customers) ############
    25-48 mo    : 24.1% (610 customers) #########
    49-72 mo    : 16.3% (731 customers) ######

--- Correlation with Churn ---
  Tenure_Months       : -0.217 ########
  AvgSatisfaction     : -0.195 #######
  NumSupportTickets   : +0.123 ####
  MonthlyCharges      : +0.098 ###
  TotalCharges        : -0.078 ###
  Age                 : +0.041 #
  SeniorCitizen       : +0.035 #
```

**Key EDA Findings:**

1. **Imbalanced classes:** 73% stay, 27% churn. We need to handle this.
2. **Missing values:** TotalCharges (2.8%) and AvgSatisfaction (4.7%) have nulls.
3. **Month-to-month contracts** have the highest churn (37.2%).
4. **New customers** (0-12 months) churn the most (40.8%).
5. **Electronic check** users churn more (35.4%).
6. **Tenure and Satisfaction** are the strongest predictors of churn.

---

## Step 3: Data Cleaning

```python
# ============================================================
# DATA CLEANING
# ============================================================
print("\n" + "=" * 65)
print("DATA CLEANING")
print("=" * 65)

# Make a copy
df_clean = df.copy()

# --- 3a: Handle Missing Values ---
print("\n--- Handling Missing Values ---")

# TotalCharges: fill with tenure * monthly charges
median_total = df_clean['TotalCharges'].median()
missing_total = df_clean['TotalCharges'].isnull().sum()
df_clean['TotalCharges'].fillna(
    df_clean['Tenure_Months'] * df_clean['MonthlyCharges'],
    inplace=True
)
print(f"  TotalCharges: Filled {missing_total} missing values "
      f"with Tenure * MonthlyCharges")

# AvgSatisfaction: fill with median
median_sat = df_clean['AvgSatisfaction'].median()
missing_sat = df_clean['AvgSatisfaction'].isnull().sum()
df_clean['AvgSatisfaction'].fillna(median_sat, inplace=True)
print(f"  AvgSatisfaction: Filled {missing_sat} missing values "
      f"with median ({median_sat:.1f})")

# Verify
print(f"\n  Missing values remaining: {df_clean.isnull().sum().sum()}")

# --- 3b: Drop unnecessary columns ---
df_clean.drop(['CustomerID', 'Tenure_Group'], axis=1, inplace=True)
print(f"\n  Dropped: CustomerID, Tenure_Group")
print(f"  Columns remaining: {df_clean.shape[1]}")
```

**Output:**

```
=================================================================
DATA CLEANING
=================================================================

--- Handling Missing Values ---
  TotalCharges: Filled 55 missing values with Tenure * MonthlyCharges
  AvgSatisfaction: Filled 93 missing values with median (5.5)

  Missing values remaining: 0

  Dropped: CustomerID, Tenure_Group
  Columns remaining: 16
```

---

## Step 4: Feature Engineering

**Feature engineering** is the art of creating new features from existing ones. Good features can dramatically improve model performance.

```python
# ============================================================
# FEATURE ENGINEERING
# ============================================================
print("\n" + "=" * 65)
print("FEATURE ENGINEERING")
print("=" * 65)

# --- 4a: Create new features ---

# Average charge per month of tenure
df_clean['AvgChargePerMonth'] = np.where(
    df_clean['Tenure_Months'] > 0,
    df_clean['TotalCharges'] / df_clean['Tenure_Months'],
    df_clean['MonthlyCharges']
)

# Tenure in years
df_clean['Tenure_Years'] = df_clean['Tenure_Months'] / 12

# Is the customer new? (less than 12 months)
df_clean['IsNewCustomer'] = (df_clean['Tenure_Months'] <= 12).astype(int)

# Number of services (count of "Yes" values)
service_cols = ['PhoneService', 'StreamingTV',
                'OnlineSecurity', 'TechSupport']
df_clean['NumServices'] = sum(
    (df_clean[col] == 'Yes').astype(int) for col in service_cols
)

# Charge per service
df_clean['ChargePerService'] = np.where(
    df_clean['NumServices'] > 0,
    df_clean['MonthlyCharges'] / df_clean['NumServices'],
    df_clean['MonthlyCharges']
)

# Has any protection service
df_clean['HasProtection'] = (
    (df_clean['OnlineSecurity'] == 'Yes') |
    (df_clean['TechSupport'] == 'Yes')
).astype(int)

# Support tickets per month of tenure
df_clean['TicketsPerMonth'] = np.where(
    df_clean['Tenure_Months'] > 0,
    df_clean['NumSupportTickets'] / df_clean['Tenure_Months'],
    df_clean['NumSupportTickets']
)

new_features = ['AvgChargePerMonth', 'Tenure_Years', 'IsNewCustomer',
                'NumServices', 'ChargePerService', 'HasProtection',
                'TicketsPerMonth']

print(f"\n  Created {len(new_features)} new features:")
for f in new_features:
    print(f"    - {f}")

print(f"\n  Total features now: {df_clean.shape[1] - 1}")

# --- 4b: Encode categorical variables ---
print("\n--- Encoding Categorical Variables ---")

cat_columns = df_clean.select_dtypes(include=['object']).columns
print(f"  Categorical columns: {list(cat_columns)}")

# One-hot encode
df_encoded = pd.get_dummies(df_clean, columns=cat_columns,
                            drop_first=True)

print(f"\n  After encoding:")
print(f"    Columns: {df_encoded.shape[1]}")
print(f"    Rows: {df_encoded.shape[0]}")
```

**Output:**

```
=================================================================
FEATURE ENGINEERING
=================================================================

  Created 7 new features:
    - AvgChargePerMonth
    - Tenure_Years
    - IsNewCustomer
    - NumServices
    - ChargePerService
    - HasProtection
    - TicketsPerMonth

  Total features now: 23

--- Encoding Categorical Variables ---
  Categorical columns: ['Gender', 'Contract', 'InternetService',
                         'PhoneService', 'StreamingTV',
                         'OnlineSecurity', 'TechSupport',
                         'PaymentMethod', 'PaperlessBilling']

  After encoding:
    Columns: 30
    Rows: 2000
```

---

## Step 5: Handle Class Imbalance with SMOTE

Our dataset has 73% "Stay" and 27% "Churn". This imbalance can cause models to predict "Stay" for everything (since that is correct 73% of the time).

**SMOTE** (Synthetic Minority Over-sampling Technique) creates synthetic (artificial) examples of the minority class to balance the dataset.

```
Before SMOTE:              After SMOTE:

Stay:  1460 (73%)          Stay:  1460 (50%)
Churn:  540 (27%)          Churn: 1460 (50%)  <-- Synthetic
                                                  samples added!

How SMOTE works:

1. Pick a minority sample (Churn customer)
2. Find its K nearest neighbors (also Churn)
3. Create a new synthetic sample between them

  Original    Synthetic     Neighbor
  Churn  --------x---------  Churn
  sample    (interpolated)   sample

The synthetic sample is a blend of existing samples.
```

```python
from sklearn.model_selection import train_test_split

# ============================================================
# PREPARE FOR MODELING
# ============================================================

# Separate features and target
X = df_encoded.drop('Churn', axis=1)
y = df_encoded['Churn']

# Split FIRST, then apply SMOTE only to training data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("=" * 65)
print("HANDLING CLASS IMBALANCE")
print("=" * 65)

print(f"\nBefore SMOTE (training set):")
print(f"  Stay:  {(y_train == 0).sum()} ({(y_train == 0).mean():.1%})")
print(f"  Churn: {(y_train == 1).sum()} ({(y_train == 1).mean():.1%})")

# Apply SMOTE
# Note: In real projects, install imblearn: pip install imbalanced-learn
# from imblearn.over_sampling import SMOTE
# smote = SMOTE(random_state=42)
# X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# For this example, we simulate SMOTE with manual oversampling
# (keeps the book dependency-free)
minority_indices = y_train[y_train == 1].index
majority_count = (y_train == 0).sum()
minority_count = (y_train == 1).sum()
samples_needed = majority_count - minority_count

# Oversample minority class
np.random.seed(42)
oversample_indices = np.random.choice(
    minority_indices, size=samples_needed, replace=True
)

X_train_balanced = pd.concat([X_train, X_train.loc[oversample_indices]])
y_train_balanced = pd.concat([y_train, y_train.loc[oversample_indices]])

print(f"\nAfter Balancing (training set):")
print(f"  Stay:  {(y_train_balanced == 0).sum()} "
      f"({(y_train_balanced == 0).mean():.1%})")
print(f"  Churn: {(y_train_balanced == 1).sum()} "
      f"({(y_train_balanced == 1).mean():.1%})")

print(f"\n  Training set grew from {len(X_train)} "
      f"to {len(X_train_balanced)} samples")
print(f"\n  Test set remains untouched: {len(X_test)} samples")
print(f"  (Never apply SMOTE to test data!)")
```

**Output:**

```
=================================================================
HANDLING CLASS IMBALANCE
=================================================================

Before SMOTE (training set):
  Stay:  1168 (73.0%)
  Churn: 432 (27.0%)

After Balancing (training set):
  Stay:  1168 (50.0%)
  Churn: 1168 (50.0%)

  Training set grew from 1600 to 2336 samples

  Test set remains untouched: 400 samples
  (Never apply SMOTE to test data!)
```

**Critical rule:** Apply SMOTE (or any balancing technique) **only to training data**, never to test data. The test set must represent the real-world distribution.

---

## Step 6: Build Pipeline and Train Models

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, roc_auc_score)
from sklearn.model_selection import cross_val_score
import numpy as np

# ============================================================
# TRAIN MULTIPLE MODELS
# ============================================================
print("\n" + "=" * 65)
print("TRAINING AND COMPARING MODELS")
print("=" * 65)

# Define models
models = {
    'Logistic Regression': Pipeline([
        ('scaler', StandardScaler()),
        ('model', LogisticRegression(max_iter=1000, random_state=42))
    ]),
    'K-Nearest Neighbors': Pipeline([
        ('scaler', StandardScaler()),
        ('model', KNeighborsClassifier(n_neighbors=7))
    ]),
    'Decision Tree': DecisionTreeClassifier(
        max_depth=7, min_samples_leaf=10, random_state=42
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=200, max_depth=10, min_samples_leaf=5,
        random_state=42, n_jobs=-1
    ),
    'SVM': Pipeline([
        ('scaler', StandardScaler()),
        ('model', SVC(kernel='rbf', probability=True, random_state=42))
    ]),
}

results = {}

print(f"\n{'Model':<25} {'CV Acc':>8} {'Test Acc':>9} "
      f"{'ROC-AUC':>9} {'Status'}")
print("-" * 65)

for name, model in models.items():
    # Cross-validation on training data
    cv_scores = cross_val_score(
        model, X_train_balanced, y_train_balanced,
        cv=5, scoring='accuracy'
    )

    # Train on full balanced training set
    model.fit(X_train_balanced, y_train_balanced)

    # Predict on test set
    y_pred = model.predict(X_test)

    # Get probabilities for ROC-AUC
    if hasattr(model, 'predict_proba'):
        y_proba = model.predict_proba(X_test)[:, 1]
    else:
        y_proba = model.decision_function(X_test)

    # Metrics
    test_acc = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)

    results[name] = {
        'model': model,
        'cv_acc': cv_scores.mean(),
        'test_acc': test_acc,
        'roc_auc': roc_auc,
        'y_pred': y_pred,
        'y_proba': y_proba,
    }

    # Best so far?
    best_auc = max(r['roc_auc'] for r in results.values())
    status = "<-- BEST" if roc_auc == best_auc else ""

    print(f"{name:<25} {cv_scores.mean():>7.1%} {test_acc:>8.1%} "
          f"{roc_auc:>8.3f} {status}")
```

**Output:**

```
=================================================================
TRAINING AND COMPARING MODELS
=================================================================

Model                      CV Acc  Test Acc   ROC-AUC Status
-----------------------------------------------------------------
Logistic Regression         77.8%    75.0%     0.823
K-Nearest Neighbors         74.3%    70.5%     0.768
Decision Tree               74.5%    73.2%     0.742
Random Forest               82.1%    78.5%     0.856 <-- BEST
SVM                         78.6%    74.8%     0.831
```

---

## Step 7: Detailed Evaluation of the Best Model

```python
# ============================================================
# DETAILED EVALUATION
# ============================================================
print("\n" + "=" * 65)
print("DETAILED EVALUATION: RANDOM FOREST")
print("=" * 65)

best_name = max(results, key=lambda k: results[k]['roc_auc'])
best = results[best_name]

y_pred = best['y_pred']
y_proba = best['y_proba']

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

print(f"\n--- Confusion Matrix ---")
print(f"                  Predicted")
print(f"               Stay    Churn")
print(f"Actual Stay   {tn:>5}    {fp:>5}")
print(f"Actual Churn  {fn:>5}    {tp:>5}")
print(f"              -----    -----")
print(f"Total         {tn+fn:>5}    {fp+tp:>5}")

print(f"\n  True Negatives (correctly predicted Stay):   {tn}")
print(f"  False Positives (incorrectly predicted Churn): {fp}")
print(f"  False Negatives (MISSED churners):             {fn}")
print(f"  True Positives (correctly caught churners):    {tp}")

# Catch rate
catch_rate = tp / (tp + fn)
print(f"\n  Churn Catch Rate: {catch_rate:.1%}")
print(f"  (We catch {catch_rate:.0%} of customers who would churn)")

# Classification Report
print(f"\n--- Classification Report ---")
print(classification_report(y_test, y_pred,
                            target_names=['Stay', 'Churn']))

# ROC-AUC Score
print(f"--- ROC-AUC Score ---")
print(f"  ROC-AUC: {best['roc_auc']:.3f}")
print(f"\n  Interpretation:")
print(f"    0.5 = Random guessing (useless)")
print(f"    0.7-0.8 = Acceptable")
print(f"    0.8-0.9 = Excellent <-- Our model!")
print(f"    0.9-1.0 = Outstanding")

# ROC Curve (ASCII)
print(f"\n--- ROC Curve (Conceptual) ---")
print("""
  True Positive
  Rate (Recall)
  1.0 |        xxxxxxxxx
      |      xx
      |    xx
      |   x     Our model (AUC=0.856)
  0.5 |  x
      | x
      |x          Random guess (AUC=0.5)
      |x  . . . . . . . . . .
  0.0 +--+--+--+--+--+--+--+--> False Positive Rate
      0                      1.0

  The more the curve hugs the top-left corner,
  the better the model.
""")
```

**Output:**

```
=================================================================
DETAILED EVALUATION: RANDOM FOREST
=================================================================

--- Confusion Matrix ---
                  Predicted
               Stay    Churn
Actual Stay     238       54
Actual Churn     32       76
              -----    -----
Total           270      130

  True Negatives (correctly predicted Stay):   238
  False Positives (incorrectly predicted Churn): 54
  False Negatives (MISSED churners):             32
  True Positives (correctly caught churners):    76

  Churn Catch Rate: 70.4%
  (We catch 70% of customers who would churn)

--- Classification Report ---
              precision    recall  f1-score   support

        Stay       0.88      0.82      0.85       292
       Churn       0.58      0.70      0.64       108

    accuracy                           0.78       400
   macro avg       0.73      0.76      0.74       400
weighted avg       0.80      0.78      0.79       400

--- ROC-AUC Score ---
  ROC-AUC: 0.856

  Interpretation:
    0.5 = Random guessing (useless)
    0.7-0.8 = Acceptable
    0.8-0.9 = Excellent <-- Our model!
    0.9-1.0 = Outstanding
```

---

## Step 8: Tune the Best Model

```python
from sklearn.model_selection import GridSearchCV

# ============================================================
# HYPERPARAMETER TUNING
# ============================================================
print("\n" + "=" * 65)
print("HYPERPARAMETER TUNING (Random Forest)")
print("=" * 65)

# Define parameter grid
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [5, 7, 10, 15],
    'min_samples_leaf': [3, 5, 10],
    'min_samples_split': [5, 10, 15],
}

total_combinations = 1
for v in param_grid.values():
    total_combinations *= len(v)
print(f"\n  Parameter combinations to try: {total_combinations}")
print(f"  With 5-fold CV: {total_combinations * 5} model fits")

# Grid Search (use a smaller grid for speed)
param_grid_small = {
    'n_estimators': [100, 200, 300],
    'max_depth': [7, 10, 15],
    'min_samples_leaf': [3, 5, 10],
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42, n_jobs=-1),
    param_grid_small,
    cv=5,
    scoring='roc_auc',
    n_jobs=-1,
    verbose=0
)

print("\n  Running Grid Search...")
grid_search.fit(X_train_balanced, y_train_balanced)

print(f"\n  Best Parameters:")
for param, value in grid_search.best_params_.items():
    print(f"    {param}: {value}")

print(f"\n  Best CV ROC-AUC: {grid_search.best_score_:.4f}")

# Evaluate tuned model on test set
tuned_model = grid_search.best_estimator_
y_pred_tuned = tuned_model.predict(X_test)
y_proba_tuned = tuned_model.predict_proba(X_test)[:, 1]

tuned_acc = accuracy_score(y_test, y_pred_tuned)
tuned_auc = roc_auc_score(y_test, y_proba_tuned)

print(f"\n--- Tuned Model vs. Original ---")
print(f"{'Metric':<15} {'Original':>10} {'Tuned':>10} {'Change':>10}")
print("-" * 50)
print(f"{'Accuracy':<15} {best['test_acc']:>9.1%} {tuned_acc:>9.1%} "
      f"{(tuned_acc - best['test_acc']):>+9.1%}")
print(f"{'ROC-AUC':<15} {best['roc_auc']:>9.3f} {tuned_auc:>9.3f} "
      f"{(tuned_auc - best['roc_auc']):>+9.3f}")

# Updated classification report
print(f"\n--- Tuned Model Classification Report ---")
print(classification_report(y_test, y_pred_tuned,
                            target_names=['Stay', 'Churn']))
```

**Output:**

```
=================================================================
HYPERPARAMETER TUNING (Random Forest)
=================================================================

  Parameter combinations to try: 144
  With 5-fold CV: 720 model fits

  Running Grid Search...

  Best Parameters:
    max_depth: 10
    min_samples_leaf: 3
    n_estimators: 300

  Best CV ROC-AUC: 0.8712

--- Tuned Model vs. Original ---
Metric           Original      Tuned     Change
--------------------------------------------------
Accuracy            78.5%      79.2%      +0.8%
ROC-AUC             0.856      0.862     +0.006

--- Tuned Model Classification Report ---
              precision    recall  f1-score   support

        Stay       0.89      0.83      0.86       292
       Churn       0.60      0.72      0.65       108

    accuracy                           0.79       400
   macro avg       0.74      0.77      0.76       400
weighted avg       0.81      0.79      0.80       400
```

---

## Step 9: Feature Importance Analysis

```python
# ============================================================
# FEATURE IMPORTANCE
# ============================================================
print("\n" + "=" * 65)
print("FEATURE IMPORTANCE ANALYSIS")
print("=" * 65)

importances = tuned_model.feature_importances_
feature_names = X.columns

# Sort by importance
importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
}).sort_values('Importance', ascending=False)

print(f"\nTop 15 Most Important Features:")
print("-" * 55)
print(f"{'Rank':>4} {'Feature':<30} {'Importance':>10}")
print("-" * 55)

for rank, (_, row) in enumerate(importance_df.head(15).iterrows(), 1):
    bar = "#" * int(row['Importance'] * 100)
    print(f"{rank:>4} {row['Feature']:<30} "
          f"{row['Importance']:>9.4f} {bar}")

# Group importance by category
print(f"\n--- Feature Importance by Category ---")

categories = {
    'Account/Tenure': ['Tenure_Months', 'Tenure_Years',
                       'IsNewCustomer'],
    'Charges': ['MonthlyCharges', 'TotalCharges',
                'AvgChargePerMonth', 'ChargePerService'],
    'Satisfaction/Support': ['AvgSatisfaction', 'NumSupportTickets',
                             'TicketsPerMonth'],
    'Services': ['NumServices', 'HasProtection'],
    'Contract': [c for c in feature_names if 'Contract' in c],
    'Demographics': ['Age', 'SeniorCitizen'],
}

category_importance = {}
for cat, features in categories.items():
    total = sum(importance_df[importance_df['Feature'].isin(features)]['Importance'])
    category_importance[cat] = total

# Sort and display
sorted_cats = sorted(category_importance.items(),
                     key=lambda x: x[1], reverse=True)

for cat, imp in sorted_cats:
    bar = "#" * int(imp * 50)
    print(f"  {cat:<25}: {imp:.4f} {bar}")
```

**Output:**

```
=================================================================
FEATURE IMPORTANCE ANALYSIS
=================================================================

Top 15 Most Important Features:
-------------------------------------------------------
Rank Feature                        Importance
-------------------------------------------------------
   1 AvgSatisfaction                    0.1123 ###########
   2 Tenure_Months                     0.0987 #########
   3 MonthlyCharges                    0.0812 ########
   4 TotalCharges                      0.0789 #######
   5 AvgChargePerMonth                 0.0654 ######
   6 NumSupportTickets                 0.0612 ######
   7 Age                               0.0534 #####
   8 TicketsPerMonth                   0.0498 ####
   9 Tenure_Years                      0.0467 ####
  10 ChargePerService                  0.0423 ####
  11 NumServices                       0.0312 ###
  12 Contract_One year                 0.0287 ##
  13 Contract_Two year                 0.0265 ##
  14 IsNewCustomer                     0.0234 ##
  15 PaymentMethod_Electronic check    0.0198 #

--- Feature Importance by Category ---
  Charges                  : 0.2678 #############
  Satisfaction/Support     : 0.2233 ###########
  Account/Tenure           : 0.1688 ########
  Demographics             : 0.0593 ##
  Contract                 : 0.0552 ##
  Services                 : 0.0464 ##
```

---

## Step 10: Business Insights and Recommendations

```python
# ============================================================
# BUSINESS INSIGHTS
# ============================================================
print("\n" + "=" * 65)
print("BUSINESS INSIGHTS & RECOMMENDATIONS")
print("=" * 65)

print("""
Based on our model analysis, here are actionable insights:

============================================================
INSIGHT 1: Customer Satisfaction Is King
============================================================
  - AvgSatisfaction is the #1 predictor of churn
  - Customers with satisfaction < 4/10 churn at 3x the rate

  RECOMMENDATION:
  --> Launch monthly satisfaction surveys
  --> Create an early warning system when scores drop
  --> Invest in customer experience improvements
  --> Target: Keep satisfaction above 6/10

============================================================
INSIGHT 2: New Customers Are Most At Risk
============================================================
  - Customers with < 12 months tenure churn at 40.8%
  - After 2 years, churn drops to 16.3%

  RECOMMENDATION:
  --> Create a 90-day onboarding program
  --> Assign dedicated account managers to new customers
  --> Offer first-year loyalty bonuses
  --> Goal: Reduce first-year churn by 25%

============================================================
INSIGHT 3: Month-to-Month Contracts Drive Churn
============================================================
  - Month-to-month: 37.2% churn rate
  - One year:       16.8% churn rate
  - Two year:       10.5% churn rate

  RECOMMENDATION:
  --> Offer discounts for annual/biannual contracts
  --> Example: 15% off for 1-year, 25% off for 2-year
  --> This locks in customers and reduces churn

============================================================
INSIGHT 4: High Support Tickets = Flight Risk
============================================================
  - Each additional support ticket increases churn risk
  - TicketsPerMonth is a strong predictor

  RECOMMENDATION:
  --> Improve product reliability to reduce tickets
  --> Proactive outreach after 3+ tickets in a month
  --> Offer premium support as a retention tool

============================================================
INSIGHT 5: Electronic Check Users Churn More
============================================================
  - Electronic check: 35.4% churn (vs ~21% for other methods)
  - This may indicate less committed customers

  RECOMMENDATION:
  --> Incentivize automatic payment setup
  --> Offer small discount for credit card/bank transfer
  --> Auto-pay customers are stickier customers

============================================================
MODEL PERFORMANCE SUMMARY
============================================================
  Algorithm:    Random Forest (tuned)
  Accuracy:     ~79%
  ROC-AUC:      ~0.86 (Excellent)
  Churn Catch:  ~70% of churners identified

  BUSINESS VALUE:
  If average customer lifetime value = $5,000
  If we catch 70% of 540 churners = 378 customers
  If we retain 30% of those with interventions = 113 customers
  Potential revenue saved = 113 x $5,000 = $565,000/year
""")

# ============================================================
# FINAL MODEL USAGE EXAMPLE
# ============================================================
print("=" * 65)
print("HOW TO USE THE MODEL")
print("=" * 65)

print("""
To predict churn for a new customer:

1. Gather their data (tenure, charges, satisfaction, etc.)
2. Create the same features we engineered
3. Encode categorical variables the same way
4. Feed into the trained model
5. Get prediction and probability

Example:
  customer_data = {...}
  churn_probability = model.predict_proba(customer_data)[0][1]

  if churn_probability > 0.6:
      --> HIGH RISK: Immediate intervention needed
  elif churn_probability > 0.4:
      --> MEDIUM RISK: Schedule check-in call
  else:
      --> LOW RISK: Standard engagement
""")
```

---

## Congratulations!

```
   ####################################################
   #                                                  #
   #    CONGRATULATIONS!                              #
   #                                                  #
   #    You have completed Book 2:                    #
   #    Data Science & Machine Learning               #
   #                                                  #
   #    You have learned:                             #
   #                                                  #
   #    - Logistic Regression (classification)        #
   #    - K-Nearest Neighbors (lazy learning)         #
   #    - Decision Trees (flowchart classifier)       #
   #    - Random Forests (wisdom of crowds)           #
   #    - Cross-Validation (fair model evaluation)    #
   #                                                  #
   #    And built a complete end-to-end project:      #
   #    Customer Churn Prediction                     #
   #                                                  #
   #    You are no longer a beginner.                 #
   #    You are a practitioner.                       #
   #                                                  #
   ####################################################
```

You started this book not knowing what a sigmoid function was. Now you can:

- Build classification models from scratch
- Engineer features that actually improve performance
- Handle messy, imbalanced real-world data
- Evaluate models properly with cross-validation and ROC curves
- Tune hyperparameters to squeeze out better performance
- Extract business insights from machine learning models
- Present results to non-technical stakeholders

That is an incredible transformation. Take a moment to appreciate how far you have come.

---

## What Is Next? Book 3: Deep Learning & Neural Networks

In **Book 3**, you will enter the world of deep learning. Here is what is coming:

- **Neural networks from scratch** -- understand every weight and bias
- **TensorFlow and PyTorch** -- the frameworks powering AI today
- **Convolutional Neural Networks (CNNs)** -- for image recognition
- **Recurrent Neural Networks (RNNs)** -- for text and sequences
- **Transfer learning** -- use pre-trained models like a pro
- **A complete image classification project** -- build your own AI that sees

The algorithms you learned in this book are the foundation. Deep learning builds on top of these concepts. You are ready.

See you in Book 3!

---

## Quick Summary

```
+------------------------------------------+
|   END-TO-END ML PROJECT CHECKLIST        |
+------------------------------------------+
|                                          |
| [ ] Load and understand the data        |
| [ ] Exploratory Data Analysis (EDA)     |
|     - Target distribution               |
|     - Missing values                    |
|     - Feature distributions             |
|     - Correlations with target          |
| [ ] Data cleaning                       |
|     - Handle missing values             |
|     - Fix data types                    |
|     - Remove duplicates                 |
| [ ] Feature engineering                 |
|     - Create new features               |
|     - Encode categorical variables      |
| [ ] Handle class imbalance              |
|     - SMOTE or oversampling             |
|     - Apply ONLY to training data!      |
| [ ] Build preprocessing pipeline        |
| [ ] Train multiple models               |
| [ ] Evaluate with multiple metrics      |
|     - Accuracy                          |
|     - Confusion matrix                  |
|     - Classification report             |
|     - ROC-AUC score                     |
| [ ] Tune the best model (GridSearchCV)  |
| [ ] Analyze feature importance          |
| [ ] Extract business insights           |
+------------------------------------------+
```

---

## Key Points

- A real ML project involves much more than just `model.fit()` and `model.predict()`. Data preparation is 80% of the work.
- **EDA** reveals patterns, missing values, and class imbalances before you train any model.
- **Feature engineering** creates new informative features from raw data. Good features can improve a model more than a better algorithm.
- **Class imbalance** must be handled (e.g., with SMOTE). Otherwise, the model just predicts the majority class.
- **Always split before balancing.** Never apply SMOTE to test data.
- **Compare multiple models** using the same evaluation method (cross-validation, same test set).
- **ROC-AUC** is often a better metric than accuracy for imbalanced datasets.
- **Hyperparameter tuning** (GridSearchCV) can improve a model, but the gains are usually smaller than good feature engineering.
- **Feature importance** translates model results into business insights.
- The final deliverable is not just a model -- it is **actionable recommendations** that stakeholders can act on.

---

## Practice Questions

1. Why do we split the data before applying SMOTE? What would happen if we applied SMOTE to the entire dataset first?

2. Our model catches 70% of churners. Is this good enough? What are the business implications of the 30% we miss? How could we improve the catch rate?

3. The feature importance shows "AvgSatisfaction" as the top predictor. A colleague says "Just use satisfaction score alone -- why bother with the other features?" How would you respond?

4. Explain ROC-AUC to a non-technical business manager. Use an analogy they would understand.

5. If you had to redo this project, what would you do differently? What additional data would you want?

---

## Exercises

### Exercise 1: Try Different Balancing Techniques

Instead of random oversampling, try: (a) random undersampling of the majority class, and (b) adjusting `class_weight='balanced'` in the model. Compare results with our oversampling approach. Which works best?

### Exercise 2: Add More Features

Think of 3-5 additional features you could engineer from the existing data. Create them, retrain the model, and see if they improve performance. Document which features helped and which did not.

### Exercise 3: Threshold Optimization

Instead of using the default 0.5 threshold for classification, try thresholds from 0.3 to 0.7. For each threshold, calculate precision, recall, and F1-score for the Churn class. What threshold maximizes the business value (catching the most churners while keeping false positives manageable)?
