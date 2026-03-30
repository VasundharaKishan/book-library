# Chapter 27: Scikit-Learn Pipelines

## What You Will Learn

In this chapter, you will learn:

- Why writing preprocessing and modeling as separate steps is risky
- What a Pipeline is and how it chains steps together
- How to build a Pipeline with StandardScaler and LogisticRegression
- How to use ColumnTransformer for mixed data types (numbers + categories)
- Why Pipelines prevent data leakage automatically
- How to combine Pipelines with GridSearchCV for tuning
- How to name, access, and inspect pipeline components
- How to save and load pipelines with joblib
- A complete real-world example with mixed data types

## Why This Chapter Matters

Imagine you are baking a cake. You need to:
1. Mix the dry ingredients
2. Mix the wet ingredients
3. Combine them
4. Pour into a pan
5. Bake

Now imagine you do step 1 on Monday, step 2 on Wednesday, and forget which bowl you used. You accidentally use the wrong measurements. The cake is ruined.

This is exactly what happens in machine learning when you write preprocessing and model training as separate, disconnected steps. You scale the training data one way. You forget to scale the test data. Or you accidentally fit the scaler on the test data (data leakage!).

**Pipelines** solve this problem. A Pipeline is like a recipe card that lists every step in order. When you call `fit`, it does all steps in order. When you call `predict`, it does all steps in order. Nothing gets forgotten. Nothing gets mixed up.

Pipelines are one of the most important tools in scikit-learn. Professional data scientists use them in almost every project.

---

## The Problem: Messy, Error-Prone Code

Let us look at what code looks like WITHOUT pipelines:

```python
# WITHOUT a Pipeline (error-prone)
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Step 1: Scale the data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Fit AND transform on train
X_test_scaled = scaler.transform(X_test)          # Only transform on test

# Step 2: Train the model
model = LogisticRegression(random_state=42)
model.fit(X_train_scaled, y_train)

# Step 3: Evaluate
score = model.score(X_test_scaled, y_test)
print(f"Accuracy: {score:.4f}")
```

This works, but there are several problems:

```
PROBLEMS WITH SEPARATE STEPS:

1. Easy to forget a step
   - What if you forget to scale the test data?
   - What if you add a new preprocessing step later?

2. Easy to cause DATA LEAKAGE
   - What if you accidentally do:
     scaler.fit_transform(X_test)   <-- BIG MISTAKE!
     (This fits on test data, leaking information)

3. Hard to use with cross-validation
   - In each fold, you need to fit the scaler on the
     training fold and transform the validation fold.
   - This is tedious and error-prone.

4. Hard to save and deploy
   - You need to save the scaler AND the model separately.
   - And remember to apply them in the right order.
```

---

## What a Pipeline Is

A **Pipeline** is a chain of steps that are executed in order. Each step (except the last) is a **transformer** (something that transforms data). The last step is usually an **estimator** (a model that makes predictions).

```
Pipeline: Chain of Steps
========================

Step 1          Step 2          Step 3
(Transform)     (Transform)     (Predict)

+-----------+   +-----------+   +-----------+
| Standard  |-->| Feature   |-->| Logistic  |
| Scaler    |   | Selection |   | Regression|
+-----------+   +-----------+   +-----------+

     |               |               |
  Scale data    Select best      Train model /
                features         Make predictions

When you call pipeline.fit(X_train, y_train):
  - Step 1: fit_transform on X_train
  - Step 2: fit_transform on result
  - Step 3: fit on result

When you call pipeline.predict(X_test):
  - Step 1: transform on X_test  (NOT fit_transform!)
  - Step 2: transform on result  (NOT fit_transform!)
  - Step 3: predict on result
```

The key insight: when you call `fit` on a Pipeline, it calls `fit_transform` on each step (except the last, which only gets `fit`). When you call `predict`, it calls `transform` on each step (except the last, which gets `predict`). This means the scaler is fitted only on training data and the test data is only transformed, never fitted. Data leakage is prevented automatically.

---

## Your First Pipeline

Let us rewrite the messy code from before using a Pipeline:

```python
# WITH a Pipeline (clean and safe)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create the pipeline: scale, then classify
pipeline = Pipeline([
    ('scaler', StandardScaler()),              # Step 1: Scale features
    ('classifier', LogisticRegression(random_state=42))  # Step 2: Classify
])

# Fit the entire pipeline (scales + trains in one call)
pipeline.fit(X_train, y_train)

# Evaluate (scales + predicts in one call)
score = pipeline.score(X_test, y_test)
print(f"Accuracy: {score:.4f}")
```

**Expected Output:**

```
Accuracy: 1.0000
```

### Line-by-Line Explanation

```python
from sklearn.pipeline import Pipeline
```
We import `Pipeline` from scikit-learn. This is the class that chains steps together.

```python
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42))
])
```
We create a Pipeline with a list of tuples. Each tuple has two parts:
- **A name** (string): You choose this. It is used to identify and access the step later.
- **An estimator or transformer**: The actual scikit-learn object.

The steps are executed in order: first `scaler`, then `classifier`.

```python
pipeline.fit(X_train, y_train)
```
This single call does two things:
1. Fits the StandardScaler on `X_train` and transforms `X_train`.
2. Fits the LogisticRegression on the scaled `X_train` with `y_train`.

```python
score = pipeline.score(X_test, y_test)
```
This single call does two things:
1. Transforms `X_test` using the already-fitted StandardScaler (NOT fit_transform!).
2. Scores using the LogisticRegression model.

### Before and After Comparison

```
WITHOUT Pipeline:                WITH Pipeline:
================                 ==============

scaler = StandardScaler()        pipeline = Pipeline([
X_train_s = scaler.fit_transform(    ('scaler', StandardScaler()),
    X_train)                         ('clf', LogisticRegression())
X_test_s = scaler.transform(     ])
    X_test)
model = LogisticRegression()     pipeline.fit(X_train, y_train)
model.fit(X_train_s, y_train)    score = pipeline.score(X_test, y_test)
score = model.score(
    X_test_s, y_test)

6 lines, error-prone             3 lines, safe
```

### The `make_pipeline` Shortcut

If you do not want to name your steps, use `make_pipeline`. It automatically names them based on the class name (in lowercase):

```python
from sklearn.pipeline import make_pipeline

# Equivalent to the Pipeline above, but names are auto-generated
pipeline = make_pipeline(
    StandardScaler(),
    LogisticRegression(random_state=42)
)

# Auto-generated names: 'standardscaler', 'logisticregression'
pipeline.fit(X_train, y_train)
print(f"Accuracy: {pipeline.score(X_test, y_test):.4f}")
```

**Expected Output:**

```
Accuracy: 1.0000
```

---

## ColumnTransformer: Different Preprocessing for Different Columns

Real-world data has different types of columns:

- **Numeric columns** (age, salary, temperature): Need scaling
- **Categorical columns** (color, city, gender): Need encoding

You cannot scale a category like "red" or "blue". And you usually do not encode a number like 25.5. You need different preprocessing for different columns.

**ColumnTransformer** solves this. It applies different transformers to different columns.

```
ColumnTransformer: Route Columns to Different Preprocessors
============================================================

Input Data:
+-----+--------+---------+-------+
| age | salary | city    | color |
+-----+--------+---------+-------+
| 25  | 50000  | NYC     | red   |
| 30  | 60000  | London  | blue  |
| 35  | 70000  | Tokyo   | red   |
+-----+--------+---------+-------+

         |                    |
   Numeric columns      Categorical columns
   (age, salary)        (city, color)
         |                    |
    +-----------+        +-----------+
    | Standard  |        | OneHot    |
    | Scaler    |        | Encoder   |
    +-----------+        +-----------+
         |                    |
    Scaled values        Encoded values
         |                    |
         +--------+-----------+
                  |
          Combined output
          (all columns together)
```

### ColumnTransformer Example

```python
# ColumnTransformer: Different preprocessing for different columns
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Create sample data with mixed types
data = pd.DataFrame({
    'age': [25, 30, 35, 40, 45],
    'salary': [50000, 60000, 70000, 80000, 90000],
    'city': ['NYC', 'London', 'Tokyo', 'NYC', 'London'],
    'color': ['red', 'blue', 'red', 'green', 'blue']
})

print("Original Data:")
print(data)
print()

# Define which columns get which treatment
numeric_features = ['age', 'salary']
categorical_features = ['city', 'color']

# Create the ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),          # Scale numbers
        ('cat', OneHotEncoder(drop='first'), categorical_features)  # Encode categories
    ]
)

# Fit and transform
result = preprocessor.fit_transform(data)
print("Transformed Data:")
print(result)
print(f"\nShape: {result.shape}")
```

**Expected Output:**

```
Original Data:
   age  salary    city  color
0   25   50000     NYC    red
1   30   60000  London   blue
2   35   70000   Tokyo    red
3   40   80000     NYC  green
4   45   90000  London   blue

Transformed Data:
[[-1.41421356 -1.41421356  0.          1.          0.          1.        ]
 [-0.70710678 -0.70710678  1.          0.          0.          0.        ]
 [ 0.          0.          0.          0.          1.          0.        ]
 [ 0.70710678  0.70710678  0.          1.          0.          0.        ]
 [ 1.41421356  1.41421356  1.          0.          0.          0.        ]]

Shape: (5, 6)
```

### Line-by-Line Explanation

```python
from sklearn.compose import ColumnTransformer
```
We import ColumnTransformer from `sklearn.compose`. This is the tool that routes columns to different preprocessors.

```python
numeric_features = ['age', 'salary']
categorical_features = ['city', 'color']
```
We define which columns are numeric and which are categorical. We use column names (strings) because our data is a pandas DataFrame. You can also use column indices (integers) if you have a NumPy array.

```python
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(drop='first'), categorical_features)
    ]
)
```
We create the ColumnTransformer with a list of tuples. Each tuple has three parts:
- **Name** (string): A label for this transformer (e.g., 'num', 'cat').
- **Transformer**: The scikit-learn transformer to apply.
- **Columns**: Which columns to apply it to.

`drop='first'` in OneHotEncoder drops the first category to avoid the **dummy variable trap**. (The dummy variable trap is when having all dummy columns creates redundant information. If city is not NYC and not Tokyo, it must be London.)

The output combines the scaled numeric columns and the encoded categorical columns into one array.

---

## Complete Pipeline: ColumnTransformer + Model

Now let us combine a ColumnTransformer with a model into a complete Pipeline:

```python
# Complete Pipeline: Preprocessing + Model
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Create a synthetic dataset with mixed types
np.random.seed(42)
n = 200

data = pd.DataFrame({
    'age': np.random.randint(18, 70, n),
    'income': np.random.randint(20000, 120000, n),
    'education': np.random.choice(['high_school', 'bachelors', 'masters', 'phd'], n),
    'employment': np.random.choice(['employed', 'self_employed', 'unemployed'], n),
    'purchased': np.random.choice([0, 1], n)  # Target
})

print("Sample Data:")
print(data.head())
print(f"\nShape: {data.shape}")
print()

# Separate features and target
X = data.drop('purchased', axis=1)
y = data['purchased']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Define column types
numeric_features = ['age', 'income']
categorical_features = ['education', 'employment']

# Step 1: Create the preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'),
         categorical_features)
    ]
)

# Step 2: Create the full pipeline
full_pipeline = Pipeline([
    ('preprocessor', preprocessor),                     # Preprocess
    ('classifier', LogisticRegression(random_state=42))  # Classify
])

# Step 3: Fit and evaluate
full_pipeline.fit(X_train, y_train)
score = full_pipeline.score(X_test, y_test)
print(f"Accuracy: {score:.4f}")

# Make predictions on new data (the pipeline handles everything)
new_data = pd.DataFrame({
    'age': [28, 55],
    'income': [45000, 95000],
    'education': ['bachelors', 'phd'],
    'employment': ['employed', 'self_employed']
})

predictions = full_pipeline.predict(new_data)
print(f"\nPredictions for new data: {predictions}")
```

**Expected Output:**

```
Sample Data:
   age  income     education    employment  purchased
0   69   62291  high_school      employed          0
1   64   41967     bachelors  self_employed          1
2   21   26431       masters      employed          0
3   47   94541       masters      employed          0
4   30   83798  high_school    unemployed          0

Shape: (200, 5)

Accuracy: 0.4750

Predictions for new data: [1 0]
```

(Note: The accuracy is low because this is random synthetic data. In a real project with meaningful data, it would be much higher.)

### The Flow of Data Through the Pipeline

```
pipeline.fit(X_train, y_train):
================================

X_train (DataFrame)
    |
    v
+---ColumnTransformer---+
|  age, income           | --> StandardScaler.fit_transform()
|  education, employment | --> OneHotEncoder.fit_transform()
|  (combine outputs)     |
+------------------------+
    |
    v
X_train_preprocessed (array)
    |
    v
LogisticRegression.fit(X_train_preprocessed, y_train)


pipeline.predict(X_test):
==========================

X_test (DataFrame)
    |
    v
+---ColumnTransformer---+
|  age, income           | --> StandardScaler.transform()     (NOT fit!)
|  education, employment | --> OneHotEncoder.transform()      (NOT fit!)
|  (combine outputs)     |
+------------------------+
    |
    v
X_test_preprocessed (array)
    |
    v
LogisticRegression.predict(X_test_preprocessed)
    |
    v
Predictions
```

---

## Why Pipelines Prevent Data Leakage

**Data leakage** happens when information from the test set "leaks" into the training process. This makes your model appear better than it really is.

The most common form of data leakage in preprocessing:

```
DATA LEAKAGE (BAD):
====================

# You fit the scaler on ALL data (train + test)
scaler.fit(X)                    # <-- LEAKAGE! Test info leaks in
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# The scaler now "knows" about test data statistics
# (mean, standard deviation of test data)
# This gives an unfair advantage.


NO DATA LEAKAGE (GOOD - Pipeline does this automatically):
==========================================================

# Pipeline fits the scaler ONLY on training data
pipeline.fit(X_train, y_train)
# Internally:
#   scaler.fit_transform(X_train)     <-- Only train data!
#   model.fit(scaled_X_train, y_train)

# Pipeline transforms test data with the train-fitted scaler
pipeline.predict(X_test)
# Internally:
#   scaler.transform(X_test)           <-- Only transform, NOT fit!
#   model.predict(scaled_X_test)
```

### Why This Matters in Cross-Validation

Pipelines are especially important with cross-validation:

```
Cross-Validation WITHOUT Pipeline (LEAKY):
==========================================

scaler.fit(X_train)                 # Fits on ALL training data
X_train_scaled = scaler.transform(X_train)
cross_val_score(model, X_train_scaled, y_train, cv=5)
# Problem: In each fold, the validation fold was used
# to fit the scaler (because we scaled ALL of X_train first)


Cross-Validation WITH Pipeline (SAFE):
=======================================

cross_val_score(pipeline, X_train, y_train, cv=5)
# In each fold, the pipeline:
#   1. Fits scaler on ONLY the training fold
#   2. Transforms the validation fold
#   3. Trains model on training fold
#   4. Evaluates on validation fold
# No leakage! Each fold is properly isolated.
```

---

## Using Pipelines with GridSearchCV

One of the most powerful features of Pipelines is that you can tune the entire pipeline with GridSearchCV. You can tune both preprocessing parameters AND model parameters at the same time.

The trick is in how you name the parameters. You use double underscores (`__`) to specify which step's parameter you want to tune:

```
step_name__parameter_name

Examples:
  'classifier__C'              --> C parameter of the 'classifier' step
  'preprocessor__num__with_mean' --> with_mean of the 'num' transformer
                                    inside the 'preprocessor' step
```

```python
# Tuning the entire pipeline with GridSearchCV
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.datasets import load_iris

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42))
])

# Define parameter grid
# Use double underscore: step_name__param_name
param_grid = {
    'scaler__with_mean': [True, False],      # Scaler parameter
    'classifier__C': [0.01, 0.1, 1.0, 10.0],  # Model parameter
    'classifier__penalty': ['l1', 'l2'],       # Model parameter
    'classifier__solver': ['liblinear']        # Required for l1 penalty
}

# GridSearch on the entire pipeline
grid_search = GridSearchCV(
    pipeline,
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

print(f"Best Parameters: {grid_search.best_params_}")
print(f"Best CV Score: {grid_search.best_score_:.4f}")
print(f"Test Score: {grid_search.score(X_test, y_test):.4f}")
```

**Expected Output:**

```
Best Parameters: {'classifier__C': 10.0, 'classifier__penalty': 'l1',
                  'classifier__solver': 'liblinear', 'scaler__with_mean': True}
Best CV Score: 0.9750
Test Score: 1.0000
```

### How the Parameter Names Work

```
Pipeline Steps:
  Step 1: 'scaler'     --> StandardScaler
  Step 2: 'classifier' --> LogisticRegression

Parameter Grid:
  'scaler__with_mean'       = StandardScaler(with_mean=?)
  'classifier__C'           = LogisticRegression(C=?)
  'classifier__penalty'     = LogisticRegression(penalty=?)

The double underscore (__) says:
  "Go to this step and set this parameter"

It is like an address:
  Building__RoomNumber
  scaler__with_mean
```

---

## Naming Steps and Accessing Components

You can access individual steps in a pipeline by name or by index:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Create pipeline with named steps
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42))
])

# Fit the pipeline
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
pipeline.fit(X, y)

# Access steps by name
print("Scaler step:", pipeline.named_steps['scaler'])
print("Classifier step:", pipeline.named_steps['classifier'])

# Access steps by index
print("\nFirst step:", pipeline[0])     # StandardScaler
print("Last step:", pipeline[-1])       # LogisticRegression

# Get the scaler's learned parameters
scaler = pipeline.named_steps['scaler']
print(f"\nScaler mean (first 3 features): {scaler.mean_[:3]}")
print(f"Scaler std  (first 3 features): {scaler.scale_[:3]}")

# Get the classifier's learned parameters
classifier = pipeline.named_steps['classifier']
print(f"\nModel coefficients shape: {classifier.coef_.shape}")
print(f"Model classes: {classifier.classes_}")
```

**Expected Output:**

```
Scaler step: StandardScaler()
Classifier step: LogisticRegression(random_state=42)

First step: StandardScaler()
Last step: LogisticRegression(random_state=42)

Scaler mean (first 3 features): [5.84333333 3.05733333 3.758     ]
Scaler std  (first 3 features): [0.82530129 0.43441097 1.75940407]

Model coefficients shape: (3, 4)
Model classes: [0 1 2]
```

---

## Saving and Loading Pipelines with joblib

One of the best things about Pipelines is that you save ONE object and get everything: all preprocessing steps AND the model. No need to save them separately.

**joblib** is a library for saving Python objects to disk. It is especially good at saving scikit-learn models and pipelines.

```python
# Saving and Loading Pipelines
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Create and train a pipeline
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42))
])
pipeline.fit(X_train, y_train)

print(f"Original accuracy: {pipeline.score(X_test, y_test):.4f}")

# ===================
# SAVE the pipeline
# ===================
joblib.dump(pipeline, 'my_pipeline.joblib')
print("Pipeline saved to 'my_pipeline.joblib'")

# ===================
# LOAD the pipeline
# ===================
loaded_pipeline = joblib.load('my_pipeline.joblib')
print(f"Loaded accuracy: {loaded_pipeline.score(X_test, y_test):.4f}")

# The loaded pipeline works exactly like the original
predictions = loaded_pipeline.predict(X_test)
print(f"Predictions (first 5): {predictions[:5]}")
```

**Expected Output:**

```
Original accuracy: 1.0000
Pipeline saved to 'my_pipeline.joblib'
Loaded accuracy: 1.0000
Predictions (first 5): [1 0 2 1 1]
```

### Why Save with joblib (Not pickle)?

```
joblib vs pickle:
=================

joblib:
  + Optimized for large NumPy arrays (common in ML)
  + Faster for large models
  + Compressed file sizes
  + Standard in scikit-learn community

pickle:
  + Built into Python (no extra install)
  + Works for any Python object
  - Slower for large numerical data
  - Larger file sizes
```

### What Gets Saved?

When you save a Pipeline, EVERYTHING is saved:

```
Saved Pipeline Contains:
========================

1. The StandardScaler:
   - Learned mean values
   - Learned standard deviation values

2. The LogisticRegression:
   - Learned coefficients (weights)
   - Learned intercept (bias)

3. The Pipeline structure:
   - Step names
   - Step order
   - All hyperparameters

Everything needed to transform new data
and make predictions. One file. No mess.
```

---

## Complete Example: Full Pipeline for Mixed Data

Let us build a complete, real-world pipeline that handles numeric features, categorical features, and trains a model. This is the kind of pipeline you would build in a real project.

```python
# Complete Pipeline Example: Mixed Data Types
# ============================================
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
import joblib
import warnings
warnings.filterwarnings('ignore')

# ================================
# Step 1: Create a Realistic Dataset
# ================================
np.random.seed(42)
n = 500

# Simulate employee data (predict if they will leave the company)
data = pd.DataFrame({
    'age': np.random.randint(22, 65, n),
    'years_experience': np.random.randint(0, 30, n),
    'salary': np.random.randint(30000, 150000, n),
    'satisfaction_score': np.random.uniform(1.0, 5.0, n).round(1),
    'department': np.random.choice(
        ['Sales', 'Engineering', 'Marketing', 'HR', 'Finance'], n
    ),
    'education_level': np.random.choice(
        ['high_school', 'bachelors', 'masters', 'phd'], n
    ),
    'remote_work': np.random.choice(['yes', 'no'], n)
})

# Create target (left the company = 1, stayed = 0)
# People with low satisfaction and low salary are more likely to leave
leave_probability = (
    (5.0 - data['satisfaction_score']) / 5.0 * 0.3 +
    (150000 - data['salary']) / 150000 * 0.3 +
    np.random.uniform(0, 0.4, n)
)
data['left_company'] = (leave_probability > 0.55).astype(int)

# Add some missing values (realistic!)
missing_indices = np.random.choice(n, 20, replace=False)
data.loc[missing_indices[:10], 'salary'] = np.nan
data.loc[missing_indices[10:], 'satisfaction_score'] = np.nan

print("Dataset Preview:")
print(data.head(10))
print(f"\nShape: {data.shape}")
print(f"Missing values:\n{data.isnull().sum()}")
print(f"\nTarget distribution:\n{data['left_company'].value_counts()}")
print()

# ================================
# Step 2: Define Features and Target
# ================================
X = data.drop('left_company', axis=1)
y = data['left_company']

# Define column types
numeric_features = ['age', 'years_experience', 'salary', 'satisfaction_score']
categorical_features = ['department', 'education_level', 'remote_work']

# ================================
# Step 3: Build the Preprocessing Pipeline
# ================================

# Numeric pipeline: impute missing values, then scale
numeric_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),   # Fill missing with median
    ('scaler', StandardScaler())                      # Scale to mean=0, std=1
])

# Categorical pipeline: impute missing, then one-hot encode
categorical_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),  # Fill with most common
    ('encoder', OneHotEncoder(drop='first', handle_unknown='ignore'))
])

# Combine both pipelines with ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_pipeline, numeric_features),
        ('cat', categorical_pipeline, categorical_features)
    ]
)

# ================================
# Step 4: Build the Full Pipeline
# ================================
full_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))
])

# Print the pipeline structure
print("Pipeline Structure:")
print(full_pipeline)
print()

# ================================
# Step 5: Split and Evaluate
# ================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Cross-validation (pipeline handles everything!)
cv_scores = cross_val_score(full_pipeline, X_train, y_train, cv=5, scoring='accuracy')
print(f"Cross-Validation Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# ================================
# Step 6: Hyperparameter Tuning
# ================================
param_grid = {
    'preprocessor__num__imputer__strategy': ['mean', 'median'],
    'classifier__n_estimators': [100, 200],
    'classifier__max_depth': [5, 10, None],
    'classifier__min_samples_split': [2, 5]
}

grid_search = GridSearchCV(
    full_pipeline,
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=0
)

grid_search.fit(X_train, y_train)

print(f"\nBest Parameters: {grid_search.best_params_}")
print(f"Best CV Score: {grid_search.best_score_:.4f}")
print(f"Test Score: {grid_search.score(X_test, y_test):.4f}")

# ================================
# Step 7: Save the Best Pipeline
# ================================
best_pipeline = grid_search.best_estimator_

joblib.dump(best_pipeline, 'best_employee_pipeline.joblib')
print("\nBest pipeline saved to 'best_employee_pipeline.joblib'")

# ================================
# Step 8: Use on New Data
# ================================
# Simulate new employee data
new_employees = pd.DataFrame({
    'age': [28, 45, 55],
    'years_experience': [3, 15, 25],
    'salary': [45000, 85000, 110000],
    'satisfaction_score': [2.5, 4.2, 3.8],
    'department': ['Engineering', 'Sales', 'Finance'],
    'education_level': ['bachelors', 'masters', 'phd'],
    'remote_work': ['yes', 'no', 'yes']
})

# The pipeline handles everything automatically
predictions = best_pipeline.predict(new_employees)
probabilities = best_pipeline.predict_proba(new_employees)

print("\nPredictions for New Employees:")
for i, (_, emp) in enumerate(new_employees.iterrows()):
    status = "WILL LEAVE" if predictions[i] == 1 else "WILL STAY"
    prob = probabilities[i][1]  # Probability of leaving
    print(f"  Employee {i+1} (age={emp['age']}, dept={emp['department']}): "
          f"{status} (probability: {prob:.2f})")
```

**Expected Output:**

```
Dataset Preview:
   age  years_experience    salary  satisfaction_score  department education_level remote_work  left_company
0   69              28   62291.0                2.8       Sales       bachelors          no             1
1   64              15   41967.0                3.7  Engineering         masters         yes             1
2   21              22   26431.0                4.3   Marketing       bachelors          no             1
3   47              17   94541.0                1.6          HR         masters         yes             0
4   30               5   83798.0                4.7       Sales     high_school          no             0
5   62               5   46373.0                3.0     Finance       bachelors          no             1
6   56               0  120937.0                2.5  Engineering             phd         yes             0
7   61              14   42224.0                4.5   Marketing     high_school         yes             1
8   33              20   95545.0                1.3       Sales       bachelors          no             0
9   36               4   87519.0                3.3          HR         masters          no             0

Shape: (500, 8)
Missing values:
age                  0
years_experience     0
salary              10
satisfaction_score   10
department           0
education_level      0
remote_work          0
left_company         0
dtype: int64

Target distribution:
left_company
0    276
1    224
Name: count, dtype: int64

Pipeline Structure:
Pipeline(steps=[('preprocessor',
                 ColumnTransformer(transformers=[('num',
                                                  Pipeline(steps=[('imputer',
                                                                   SimpleImputer(strategy='median')),
                                                                  ('scaler',
                                                                   StandardScaler())]),
                                                  ['age', 'years_experience',
                                                   'salary',
                                                   'satisfaction_score']),
                                                 ('cat',
                                                  Pipeline(steps=[('imputer',
                                                                   SimpleImputer(strategy='most_frequent')),
                                                                  ('encoder',
                                                                   OneHotEncoder(drop='first',
                                                                                 handle_unknown='ignore'))]),
                                                  ['department',
                                                   'education_level',
                                                   'remote_work'])])),
                ('classifier', RandomForestClassifier(random_state=42))])

Cross-Validation Accuracy: 0.6650 (+/- 0.0307)

Best Parameters: {'classifier__max_depth': 10, 'classifier__min_samples_split': 5,
                  'classifier__n_estimators': 200,
                  'preprocessor__num__imputer__strategy': 'median'}
Best CV Score: 0.6725
Test Score: 0.6800

Best pipeline saved to 'best_employee_pipeline.joblib'

Predictions for New Employees:
  Employee 1 (age=28, dept=Engineering): WILL LEAVE (probability: 0.62)
  Employee 2 (age=45, dept=Sales): WILL STAY (probability: 0.25)
  Employee 3 (age=55, dept=Finance): WILL STAY (probability: 0.38)
```

### The Complete Pipeline Diagram

```
Full Pipeline Architecture:
============================

Input: Raw DataFrame with mixed types and missing values
    |
    v
+-------ColumnTransformer ('preprocessor')---------+
|                                                    |
|  Numeric Pipeline ('num'):      Cat Pipeline ('cat'):|
|  +------------------+          +------------------+|
|  | SimpleImputer    |          | SimpleImputer    ||
|  | (fill NaN with   |          | (fill NaN with   ||
|  |  median)         |          |  most frequent)  ||
|  +--------+---------+          +--------+---------+|
|           |                             |          |
|  +--------+---------+          +--------+---------+|
|  | StandardScaler   |          | OneHotEncoder    ||
|  | (mean=0, std=1)  |          | (create dummies) ||
|  +--------+---------+          +--------+---------+|
|           |                             |          |
+-----------|-----------------------------|-----------+
            |                             |
            +---------- Combine ----------+
                          |
                          v
              +-----------------------+
              | RandomForestClassifier|
              | ('classifier')        |
              +-----------------------+
                          |
                          v
                    Predictions
```

---

## Common Mistakes

**Mistake 1: Fitting the scaler on all data before splitting.**
```python
# WRONG:
scaler.fit(X)  # This sees test data!
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# RIGHT: Use a Pipeline. It handles this automatically.
pipeline.fit(X_train, y_train)
```

**Mistake 2: Wrong parameter names in GridSearchCV.**
```python
# WRONG: Missing the step name
param_grid = {'C': [0.1, 1.0]}  # Error! Which step is 'C' for?

# RIGHT: Use step_name__parameter_name
param_grid = {'classifier__C': [0.1, 1.0]}
```

**Mistake 3: Forgetting `handle_unknown='ignore'` in OneHotEncoder.**
If the test data has a category not seen during training, OneHotEncoder will raise an error. Use `handle_unknown='ignore'` to handle this gracefully.

**Mistake 4: Applying the wrong transformer to the wrong columns.**
Scaling categorical data or encoding numeric data will produce nonsense results. Always check that your `numeric_features` and `categorical_features` lists are correct.

**Mistake 5: Not using `drop='first'` in OneHotEncoder.**
Without `drop='first'`, you create perfectly correlated columns (the dummy variable trap). This can confuse some models, especially linear models.

---

## Best Practices

1. **Always use Pipelines in production code.** They prevent data leakage and make code cleaner.

2. **Name your steps clearly.** Use descriptive names like `'scaler'`, `'encoder'`, `'classifier'` instead of `'step1'`, `'step2'`.

3. **Use `make_pipeline` for simple cases.** When you do not need custom names, `make_pipeline` is shorter.

4. **Handle missing values inside the pipeline.** Use `SimpleImputer` as the first step so missing values are handled automatically for new data too.

5. **Use `handle_unknown='ignore'` in OneHotEncoder.** This prevents errors when new data has unseen categories.

6. **Save the entire pipeline.** Never save just the model. The preprocessing steps are just as important.

7. **Use ColumnTransformer for mixed data types.** Do not try to scale everything or encode everything. Match the preprocessing to the data type.

8. **Combine with GridSearchCV for tuning.** You can tune preprocessing and model parameters together.

---

## Quick Summary

- **Pipelines** chain preprocessing and modeling steps into one object.
- They prevent **data leakage** by automatically handling fit/transform correctly.
- **ColumnTransformer** applies different preprocessing to different column types.
- You can tune entire pipelines with **GridSearchCV** using double-underscore notation.
- **Save one file** (with joblib) and get everything: preprocessing + model.
- Pipelines make your code cleaner, safer, and more reproducible.

---

## Key Points to Remember

1. A Pipeline chains steps: each step transforms data, the last step predicts.
2. `pipeline.fit()` calls `fit_transform` on each step (except the last).
3. `pipeline.predict()` calls `transform` on each step (except the last).
4. ColumnTransformer routes different columns to different transformers.
5. Use double underscore (`__`) notation for parameter names: `step__param`.
6. Pipelines prevent data leakage automatically.
7. `make_pipeline` auto-names steps from the class name.
8. `joblib.dump()` saves the entire pipeline to disk.
9. `joblib.load()` loads it back, ready to use.
10. Always include `handle_unknown='ignore'` in OneHotEncoder for safety.

---

## Practice Questions

### Question 1
What is the main advantage of using a Pipeline over writing separate preprocessing and modeling steps?

**Answer:** The main advantage is that Pipelines prevent data leakage. When you call `fit` on a Pipeline, it ensures that preprocessing steps (like scaling) are fitted only on training data. When you call `predict` or `transform`, it only transforms (never fits) on new data. This is done automatically, eliminating the risk of accidentally fitting preprocessors on test data.

### Question 2
How do you specify hyperparameters for individual steps when using GridSearchCV with a Pipeline?

**Answer:** You use double-underscore notation: `step_name__parameter_name`. For example, if your pipeline has a step named `'classifier'` that is a LogisticRegression, you would write `'classifier__C': [0.1, 1.0, 10.0]` in the parameter grid. For nested steps (like a transformer inside a ColumnTransformer), you chain the names: `'preprocessor__num__scaler__with_mean': [True, False]`.

### Question 3
What is a ColumnTransformer and when would you use it?

**Answer:** A ColumnTransformer applies different transformers to different columns of your data. You use it when your dataset has mixed data types. For example, numeric columns need scaling (StandardScaler) while categorical columns need encoding (OneHotEncoder). The ColumnTransformer routes each group of columns to the appropriate transformer and combines the results.

### Question 4
Why should you use `handle_unknown='ignore'` when using OneHotEncoder in a pipeline?

**Answer:** When you deploy a model to production, new data might contain categories that were not present in the training data. Without `handle_unknown='ignore'`, the OneHotEncoder would raise an error when it encounters an unknown category. With `handle_unknown='ignore'`, it simply creates a row of zeros for that category, allowing the pipeline to continue working.

### Question 5
How do you save and load a complete pipeline?

**Answer:** Use `joblib.dump(pipeline, 'filename.joblib')` to save and `joblib.load('filename.joblib')` to load. This saves everything: all preprocessing steps (with their learned parameters like means and standard deviations), the trained model (with its learned weights), and the pipeline structure. One file contains everything needed to transform new data and make predictions.

---

## Exercises

### Exercise 1: Build a Simple Pipeline

Create a pipeline with three steps: SimpleImputer (strategy='mean'), StandardScaler, and SVM classifier (SVC). Use the Iris dataset. Split into train/test, fit the pipeline, and print the accuracy. Compare with training without a pipeline.

### Exercise 2: Mixed Data Pipeline with Tuning

Using the tips dataset from seaborn (or create a synthetic restaurant dataset with columns: bill_amount, tip_percentage, party_size, day_of_week, meal_type), build a pipeline with ColumnTransformer that scales numeric columns and encodes categorical columns. Use GridSearchCV to tune both the imputer strategy and the classifier parameters. Print the best parameters and test score.

### Exercise 3: Pipeline Comparison

Build three different pipelines, each using the same ColumnTransformer for preprocessing but different classifiers: LogisticRegression, RandomForestClassifier, and GradientBoostingClassifier. Use cross-validation to compare them. Print a comparison table showing each model's mean CV score and standard deviation. Save the best pipeline to disk.

---

## What Is Next?

You now know how to build clean, safe, and reproducible machine learning workflows with Pipelines. But there is a common problem that Pipelines alone cannot solve: **imbalanced data**.

In the next chapter, you will learn what happens when one class vastly outnumbers another (like 99% normal transactions and 1% fraud). Your model might get 99% accuracy by simply predicting "normal" every time! You will learn strategies to handle this: class weights, SMOTE, undersampling, and choosing the right metrics. These techniques are essential for real-world problems like fraud detection, disease diagnosis, and spam filtering.
