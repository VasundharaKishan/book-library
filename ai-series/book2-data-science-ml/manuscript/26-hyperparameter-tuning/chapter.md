# Chapter 26: Hyperparameter Tuning

## What You Will Learn

In this chapter, you will learn:

- The difference between parameters and hyperparameters
- How to use Grid Search to find the best settings for your model
- How to use Randomized Search for faster tuning
- How to define search spaces for different hyperparameters
- How cross-validation works inside hyperparameter search
- How to read and use the best parameters and best score
- Practical tips for efficient tuning
- A complete example tuning an XGBoost model

## Why This Chapter Matters

Imagine you bought a brand-new oven. The oven has dials for temperature, fan speed, and rack position. You want to bake the perfect cake. If you set the temperature too low, the cake is raw. Too high, it burns. The fan speed and rack position also matter.

Machine learning models have similar "dials." These dials are called **hyperparameters**. Choosing the right values can make the difference between a mediocre model and an excellent one.

But here is the problem. There are many dials. And many possible values for each dial. How do you find the best combination?

That is what **hyperparameter tuning** solves. It tries different combinations and tells you which one works best.

This chapter teaches you how to do this automatically and efficiently.

---

## Parameters vs Hyperparameters

Before we tune anything, let us understand two important words.

### Parameters (Learned by the Model)

**Parameters** are values that the model learns from data during training.

You do NOT set these. The model figures them out on its own.

Examples:
- The **weights** in a linear regression (the slope and intercept)
- The **split points** in a decision tree (which feature to split on and at what value)

Think of these as the recipe steps. The model writes its own recipe by looking at the data.

### Hyperparameters (Set by You)

**Hyperparameters** are values that YOU set before training begins.

You decide these. The model does NOT learn them from data.

Examples:
- The **number of trees** in a Random Forest (`n_estimators`)
- The **maximum depth** of each tree (`max_depth`)
- The **learning rate** in gradient boosting

Think of these as the oven settings. You set the temperature before you start baking. The cake does not set it for you.

Here is a simple way to remember:

```
+--------------------------------------------------+
|                                                  |
|   PARAMETERS            HYPERPARAMETERS          |
|   (Model learns)        (You set)                |
|                                                  |
|   - Weights             - n_estimators           |
|   - Coefficients        - max_depth              |
|   - Split points        - learning_rate          |
|   - Biases              - min_samples_split      |
|                                                  |
|   Like: Recipe steps    Like: Oven temperature   |
|   (cake figures out)    (you decide)             |
|                                                  |
+--------------------------------------------------+
```

### The Oven Analogy

```
BAKING A CAKE                    TRAINING A MODEL
=============                    ================

Oven temperature: 350F    -->    n_estimators: 100
Fan speed: medium         -->    max_depth: 5
Rack position: middle     -->    learning_rate: 0.1

These are YOUR choices.          These are YOUR choices.
(Hyperparameters)                (Hyperparameters)

The cake rises and browns  -->   The model learns weights
on its own during baking.        on its own during training.
(Parameters)                     (Parameters)
```

---

## Grid Search: Try Every Combination

### The Idea

**Grid Search** means: try every possible combination of hyperparameter values.

Think of it like trying every key on a keyring. You have a locked door. You have 20 keys. You try key 1, then key 2, then key 3... until one opens the door.

Grid Search does the same thing. It tries every combination and picks the best one.

### A Simple Example

Suppose you want to tune a Random Forest with two hyperparameters:

- `n_estimators`: [50, 100, 200]
- `max_depth`: [3, 5, 10]

Grid Search will try ALL combinations:

```
Combination 1:  n_estimators=50,  max_depth=3
Combination 2:  n_estimators=50,  max_depth=5
Combination 3:  n_estimators=50,  max_depth=10
Combination 4:  n_estimators=100, max_depth=3
Combination 5:  n_estimators=100, max_depth=5
Combination 6:  n_estimators=100, max_depth=10
Combination 7:  n_estimators=200, max_depth=3
Combination 8:  n_estimators=200, max_depth=5
Combination 9:  n_estimators=200, max_depth=10

Total: 3 x 3 = 9 combinations
```

For each combination, it trains a model and measures performance. Then it picks the winner.

### Why It Is Called "Grid" Search

Imagine a table (grid) where rows are one hyperparameter and columns are another:

```
                  max_depth=3    max_depth=5    max_depth=10
                 +-------------+-------------+--------------+
n_estimators=50  |  Score: 0.82|  Score: 0.85|  Score: 0.84 |
                 +-------------+-------------+--------------+
n_estimators=100 |  Score: 0.83|  Score: 0.87|  Score: 0.86 |
                 +-------------+-------------+--------------+
n_estimators=200 |  Score: 0.84|  Score: 0.88|  Score: 0.86 |
                 +-------------+-------------+--------------+

Best: n_estimators=200, max_depth=5 --> Score: 0.88
```

Every cell in the grid gets tested. That is Grid Search.

---

## GridSearchCV in Scikit-Learn

Let us see Grid Search in action with real code.

**GridSearchCV** combines Grid Search with Cross-Validation. The "CV" stands for Cross-Validation. This means each combination is tested using cross-validation (not just a single train/test split). This gives more reliable results.

```python
# Grid Search with Random Forest
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

# Step 1: Load data
X, y = load_iris(return_X_y=True)

# Step 2: Create the model (with default settings for now)
model = RandomForestClassifier(random_state=42)

# Step 3: Define the parameter grid
# These are the values we want to try
param_grid = {
    'n_estimators': [50, 100, 200],       # Number of trees
    'max_depth': [3, 5, 10, None],         # Maximum depth (None = no limit)
    'min_samples_split': [2, 5, 10]        # Minimum samples to split a node
}

# Step 4: Create GridSearchCV
grid_search = GridSearchCV(
    estimator=model,          # The model to tune
    param_grid=param_grid,    # The combinations to try
    cv=5,                     # 5-fold cross-validation
    scoring='accuracy',       # How to measure performance
    n_jobs=-1,                # Use all CPU cores (faster!)
    verbose=1                 # Show progress
)

# Step 5: Run the search (this tries all combinations)
grid_search.fit(X, y)

# Step 6: See results
print(f"Best Parameters: {grid_search.best_params_}")
print(f"Best Score: {grid_search.best_score_:.4f}")
print(f"Total combinations tried: {len(grid_search.cv_results_['mean_test_score'])}")
```

**Expected Output:**

```
Fitting 5 folds for each of 36 candidates, totalling 180 fits
Best Parameters: {'max_depth': 5, 'min_samples_split': 2, 'n_estimators': 100}
Best Score: 0.9667
Total combinations tried: 36
```

### Line-by-Line Explanation

```python
X, y = load_iris(return_X_y=True)
```
We load the Iris dataset. `X` has the features (flower measurements). `y` has the labels (flower species). `return_X_y=True` gives us arrays directly instead of a Bunch object.

```python
model = RandomForestClassifier(random_state=42)
```
We create a Random Forest model. `random_state=42` makes results reproducible. We use default hyperparameters for now because Grid Search will override them.

```python
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 10, None],
    'min_samples_split': [2, 5, 10]
}
```
This dictionary defines which values to try. Each key is a hyperparameter name. Each value is a list of options. Total combinations: 3 x 4 x 3 = 36.

- `n_estimators`: Number of trees in the forest. More trees usually means better performance but slower training.
- `max_depth`: How deep each tree can grow. `None` means no limit (tree grows until all leaves are pure).
- `min_samples_split`: Minimum number of samples needed to split a node. Higher values prevent overfitting.

```python
grid_search = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)
```
We create the GridSearchCV object:
- `estimator=model`: The model to tune.
- `param_grid=param_grid`: The combinations to try.
- `cv=5`: Use 5-fold cross-validation for each combination.
- `scoring='accuracy'`: Judge models by accuracy (correct predictions / total predictions).
- `n_jobs=-1`: Use all available CPU cores. This makes it much faster.
- `verbose=1`: Print progress messages.

```python
grid_search.fit(X, y)
```
This runs the search. It tries all 36 combinations. For each, it does 5-fold cross-validation. That means 36 x 5 = 180 model trainings total.

```python
print(f"Best Parameters: {grid_search.best_params_}")
```
This shows the best combination found. Notice the underscore at the end of `best_params_`. In scikit-learn, attributes with trailing underscores are set after fitting.

```python
print(f"Best Score: {grid_search.best_score_:.4f}")
```
This shows the best cross-validated score. The `:.4f` formats it to 4 decimal places.

### How Many Combinations?

The total number of combinations grows fast:

```
3 values x 4 values x 3 values = 36 combinations
Each with 5-fold CV = 180 model trainings

If we add another hyperparameter with 4 values:
3 x 4 x 3 x 4 = 144 combinations
Each with 5-fold CV = 720 model trainings!

This is why Grid Search can be SLOW.
```

---

## Randomized Search: Faster, Nearly as Good

### The Problem with Grid Search

Grid Search tries EVERY combination. This is thorough but slow.

If you have 5 hyperparameters, each with 5 values, that is 5^5 = 3,125 combinations. With 5-fold CV, that is 15,625 model trainings. This could take hours.

### The Randomized Solution

**Randomized Search** tries a RANDOM subset of combinations. Instead of testing all 3,125, you might test only 100 random ones.

Think of it this way:

```
GRID SEARCH                    RANDOMIZED SEARCH
===========                    =================

Try ALL keys on               Try 20 RANDOM keys
the keyring.                  from the keyring.

Guaranteed to find            Very likely to find
the right key.                the right key.

Slow if many keys.            Much faster.
```

Research has shown that Randomized Search often finds results nearly as good as Grid Search, but in a fraction of the time. Why? Because not all hyperparameters matter equally. Usually, one or two matter a lot and the rest matter little. Random sampling is good at finding good values for the important ones.

### RandomizedSearchCV in Scikit-Learn

```python
# Randomized Search with Random Forest
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

# Step 1: Load data
X, y = load_iris(return_X_y=True)

# Step 2: Create the model
model = RandomForestClassifier(random_state=42)

# Step 3: Define the parameter distributions
# Instead of listing exact values, we can use distributions!
param_distributions = {
    'n_estimators': randint(50, 300),           # Random integer between 50 and 300
    'max_depth': [3, 5, 10, 15, 20, None],      # Pick from this list
    'min_samples_split': randint(2, 20),         # Random integer between 2 and 20
    'min_samples_leaf': randint(1, 10),          # Random integer between 1 and 10
    'max_features': ['sqrt', 'log2', None]       # Pick from this list
}

# Step 4: Create RandomizedSearchCV
random_search = RandomizedSearchCV(
    estimator=model,
    param_distributions=param_distributions,
    n_iter=50,                # Try 50 random combinations (not all!)
    cv=5,                     # 5-fold cross-validation
    scoring='accuracy',
    random_state=42,          # For reproducibility
    n_jobs=-1,
    verbose=1
)

# Step 5: Run the search
random_search.fit(X, y)

# Step 6: See results
print(f"Best Parameters: {random_search.best_params_}")
print(f"Best Score: {random_search.best_score_:.4f}")
```

**Expected Output:**

```
Fitting 5 folds for each of 50 candidates, totalling 250 fits
Best Parameters: {'max_depth': 10, 'max_features': 'sqrt', 'min_samples_leaf': 2,
                  'min_samples_split': 5, 'n_estimators': 187}
Best Score: 0.9667
```

### Line-by-Line Explanation

```python
from scipy.stats import randint, uniform
```
We import `randint` and `uniform` from scipy.stats. These create random distributions:
- `randint(50, 300)`: Picks random integers between 50 and 299.
- `uniform(0.01, 0.99)`: Picks random floats between 0.01 and 1.0. (We do not use `uniform` here, but it is useful for learning rates.)

```python
param_distributions = {
    'n_estimators': randint(50, 300),
    'max_depth': [3, 5, 10, 15, 20, None],
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10),
    'max_features': ['sqrt', 'log2', None]
}
```
This is like `param_grid`, but values can be distributions (not just lists). `randint(50, 300)` does not try every number from 50 to 299. It picks random samples from that range. Lists work too. GridSearchCV would try every item in the list. RandomizedSearchCV picks randomly from the list.

```python
n_iter=50,
```
This is the key difference. We only try 50 random combinations instead of all possible ones. You control the budget. More iterations = better results but slower.

### Grid Search vs Randomized Search

```
+------------------+-------------------+--------------------+
|                  | GRID SEARCH       | RANDOMIZED SEARCH  |
+------------------+-------------------+--------------------+
| Tries            | ALL combinations  | RANDOM subset      |
| Speed            | Slow              | Fast               |
| Guarantee best?  | Yes (within grid) | No, but close      |
| Good for         | Small grids       | Large grids        |
| Parameter types  | Lists only        | Lists + distributions |
| Key parameter    | param_grid        | param_distributions |
|                  |                   | + n_iter            |
+------------------+-------------------+--------------------+
```

---

## The Search Space: Defining Parameter Grids

The **search space** is all the hyperparameter values you want to try. Defining a good search space is important. Too narrow and you might miss the best values. Too wide and the search takes forever.

### Tips for Defining Search Spaces

**1. Start with the documentation.** Check what each hyperparameter does and what values make sense.

**2. Use logarithmic scales for learning rates.**

```python
# Bad: linear spacing
learning_rates = [0.1, 0.2, 0.3, 0.4, 0.5]

# Good: logarithmic spacing (covers more range)
learning_rates = [0.001, 0.01, 0.1, 0.5, 1.0]
```

**3. Include the default value.** Always include the default value in your grid so you can compare.

**4. Common search spaces for popular models:**

```python
# Random Forest
rf_params = {
    'n_estimators': [100, 200, 500],
    'max_depth': [5, 10, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Gradient Boosting
gb_params = {
    'n_estimators': [100, 200, 500],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'max_depth': [3, 5, 7],
    'subsample': [0.8, 0.9, 1.0]
}

# Logistic Regression
lr_params = {
    'C': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
    'penalty': ['l1', 'l2'],
    'solver': ['liblinear', 'saga']
}
```

---

## Cross-Validation Inside Search

You might wonder: "Does GridSearchCV use cross-validation?"

Yes! That is what the "CV" in GridSearchCV means.

Here is what happens step by step:

```
For EACH combination of hyperparameters:
    Split data into 5 folds
    For EACH fold:
        Train on 4 folds
        Test on 1 fold
        Record the score
    Average the 5 scores --> This is the CV score for this combination

After ALL combinations are tested:
    Pick the combination with the HIGHEST average CV score
    Retrain on ALL the data with those best parameters
```

This is shown in this diagram:

```
Grid Search with 5-Fold CV
===========================

Combination 1 (n_est=50, depth=3):
  Fold 1: 0.82  Fold 2: 0.80  Fold 3: 0.85  Fold 4: 0.81  Fold 5: 0.83
  Average: 0.822

Combination 2 (n_est=50, depth=5):
  Fold 1: 0.85  Fold 2: 0.84  Fold 3: 0.87  Fold 4: 0.83  Fold 5: 0.86
  Average: 0.850

Combination 3 (n_est=100, depth=5):
  Fold 1: 0.88  Fold 2: 0.86  Fold 3: 0.89  Fold 4: 0.87  Fold 5: 0.88
  Average: 0.876  <-- BEST!

... (more combinations)

Winner: n_est=100, depth=5 with score 0.876
```

### Why Cross-Validation Matters Here

Without cross-validation, you might get lucky on one train/test split. A hyperparameter combination might score well on that particular split but poorly on different data.

Cross-validation averages across multiple splits. This gives a more honest estimate of how well those hyperparameters will work on new data.

---

## Best Parameters and Best Score

After the search is done, you can access several useful attributes:

```python
# After running grid_search.fit(X, y) ...

# 1. Best hyperparameters found
print("Best Parameters:", grid_search.best_params_)
# Output: {'max_depth': 5, 'min_samples_split': 2, 'n_estimators': 100}

# 2. Best cross-validated score
print("Best Score:", grid_search.best_score_)
# Output: 0.9667

# 3. The best model (already trained on ALL data)
best_model = grid_search.best_estimator_
print("Best Model:", best_model)

# 4. You can use the best model directly for predictions
predictions = grid_search.predict(X)  # Uses best_estimator_ automatically

# 5. Detailed results for ALL combinations
import pandas as pd
results = pd.DataFrame(grid_search.cv_results_)
print(results[['params', 'mean_test_score', 'rank_test_score']].head(10))
```

**Expected Output:**

```
Best Parameters: {'max_depth': 5, 'min_samples_split': 2, 'n_estimators': 100}
Best Score: 0.9666666666666668
Best Model: RandomForestClassifier(max_depth=5, random_state=42)

                                              params  mean_test_score  rank_test_score
0    {'max_depth': 3, 'min_samples_split': 2, 'n_e...         0.960000               6
1    {'max_depth': 3, 'min_samples_split': 5, 'n_e...         0.960000               6
2    {'max_depth': 3, 'min_samples_split': 10, 'n_...         0.953333              18
3    {'max_depth': 5, 'min_samples_split': 2, 'n_e...         0.960000               6
4    {'max_depth': 5, 'min_samples_split': 5, 'n_e...         0.960000               6
5    {'max_depth': 5, 'min_samples_split': 10, 'n_...         0.960000               6
6   {'max_depth': 10, 'min_samples_split': 2, 'n_e...         0.960000               6
7   {'max_depth': 10, 'min_samples_split': 5, 'n_e...         0.960000               6
8   {'max_depth': 10, 'min_samples_split': 10, 'n_...         0.953333              18
9   {'max_depth': None, 'min_samples_split': 2, 'n...         0.960000               6
```

### Key Attributes to Remember

```
+-------------------------+-------------------------------------------+
| Attribute               | What It Gives You                         |
+-------------------------+-------------------------------------------+
| .best_params_           | Dictionary of best hyperparameters        |
| .best_score_            | Best cross-validated score (float)        |
| .best_estimator_        | The best model (already fitted)           |
| .cv_results_            | Detailed results for ALL combinations     |
| .best_index_            | Index of the best combination             |
+-------------------------+-------------------------------------------+
```

---

## Practical Tips: Start Broad, Then Narrow

Here is a proven strategy used by experienced data scientists:

### Step 1: Start with RandomizedSearch (broad exploration)

Cast a wide net. Use distributions. Try 50-100 random combinations.

```python
# Step 1: Broad RandomizedSearch
from scipy.stats import randint

broad_params = {
    'n_estimators': randint(50, 500),
    'max_depth': randint(3, 30),
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10)
}

random_search = RandomizedSearchCV(
    model, broad_params, n_iter=100, cv=5, random_state=42, n_jobs=-1
)
random_search.fit(X, y)
print("Best from RandomizedSearch:", random_search.best_params_)
# Example output: {'max_depth': 12, 'min_samples_leaf': 3,
#                  'min_samples_split': 7, 'n_estimators': 210}
```

### Step 2: Narrow down with GridSearch (fine-tuning)

Take the best values from Step 1. Create a small grid around them.

```python
# Step 2: Narrow GridSearch around the best values
narrow_params = {
    'n_estimators': [180, 200, 210, 220, 240],     # Around 210
    'max_depth': [10, 11, 12, 13, 14],              # Around 12
    'min_samples_split': [5, 6, 7, 8, 9],           # Around 7
    'min_samples_leaf': [2, 3, 4]                    # Around 3
}

grid_search = GridSearchCV(
    model, narrow_params, cv=5, n_jobs=-1
)
grid_search.fit(X, y)
print("Best from GridSearch:", grid_search.best_params_)
```

This two-step approach is much faster than a single large Grid Search:

```
One-step GridSearch:
  5 x 28 x 18 x 9 = 22,680 combinations  (very slow!)

Two-step approach:
  Step 1: 100 random combinations          (fast)
  Step 2: 5 x 5 x 5 x 3 = 375 combinations (fast)
  Total: 475 evaluations                   (much faster!)
```

---

## Complete Example: Tune an XGBoost Model

Let us put everything together in a complete, real-world example. We will tune an XGBoost model and compare it with the default settings.

**XGBoost** (Extreme Gradient Boosting) is one of the most popular machine learning algorithms. It is a gradient boosting method that builds many decision trees, each learning from the mistakes of the previous ones.

```python
# Complete Hyperparameter Tuning Example
# =======================================
# We will:
# 1. Train a default XGBoost model
# 2. Tune it with RandomizedSearch
# 3. Fine-tune with GridSearch
# 4. Compare all three

import numpy as np
import pandas as pd
from sklearn.datasets import load_wine
from sklearn.model_selection import (
    train_test_split, RandomizedSearchCV, GridSearchCV, cross_val_score
)
from xgboost import XGBClassifier
from scipy.stats import randint, uniform
import warnings
warnings.filterwarnings('ignore')

# =====================
# Step 1: Load the Data
# =====================
X, y = load_wine(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training samples: {X_train.shape[0]}")
print(f"Test samples: {X_test.shape[0]}")
print(f"Number of features: {X_train.shape[1]}")
print(f"Number of classes: {len(np.unique(y))}")
print()

# ==============================
# Step 2: Default XGBoost Model
# ==============================
print("=" * 50)
print("STEP 2: Default XGBoost Model")
print("=" * 50)

default_model = XGBClassifier(
    random_state=42,
    eval_metric='mlogloss'    # Suppress warning
)

# Cross-validated score with default settings
default_scores = cross_val_score(default_model, X_train, y_train, cv=5)
print(f"Default CV Accuracy: {default_scores.mean():.4f} (+/- {default_scores.std():.4f})")
print()

# =============================================
# Step 3: Broad Search with RandomizedSearchCV
# =============================================
print("=" * 50)
print("STEP 3: Broad RandomizedSearch")
print("=" * 50)

broad_params = {
    'n_estimators': randint(50, 500),
    'max_depth': randint(2, 15),
    'learning_rate': uniform(0.01, 0.29),       # Between 0.01 and 0.30
    'subsample': uniform(0.6, 0.4),              # Between 0.6 and 1.0
    'colsample_bytree': uniform(0.6, 0.4),       # Between 0.6 and 1.0
    'min_child_weight': randint(1, 10),
    'gamma': uniform(0, 0.5)                     # Between 0 and 0.5
}

random_search = RandomizedSearchCV(
    estimator=XGBClassifier(random_state=42, eval_metric='mlogloss'),
    param_distributions=broad_params,
    n_iter=50,
    cv=5,
    scoring='accuracy',
    random_state=42,
    n_jobs=-1,
    verbose=0
)

random_search.fit(X_train, y_train)

print(f"Best RandomizedSearch Score: {random_search.best_score_:.4f}")
print(f"Best Parameters:")
for param, value in random_search.best_params_.items():
    if isinstance(value, float):
        print(f"  {param}: {value:.4f}")
    else:
        print(f"  {param}: {value}")
print()

# ============================================
# Step 4: Narrow Search with GridSearchCV
# ============================================
print("=" * 50)
print("STEP 4: Narrow GridSearch (Fine-Tuning)")
print("=" * 50)

# Get best values from RandomizedSearch and create narrow grid
best = random_search.best_params_

narrow_params = {
    'n_estimators': [max(50, best['n_estimators'] - 50),
                     best['n_estimators'],
                     best['n_estimators'] + 50],
    'max_depth': [max(2, best['max_depth'] - 1),
                  best['max_depth'],
                  best['max_depth'] + 1],
    'learning_rate': [max(0.01, round(best['learning_rate'] - 0.02, 3)),
                      round(best['learning_rate'], 3),
                      round(best['learning_rate'] + 0.02, 3)],
    'subsample': [max(0.5, round(best['subsample'] - 0.05, 2)),
                  round(best['subsample'], 2),
                  min(1.0, round(best['subsample'] + 0.05, 2))],
}

grid_search = GridSearchCV(
    estimator=XGBClassifier(
        random_state=42,
        eval_metric='mlogloss',
        colsample_bytree=best['colsample_bytree'],
        min_child_weight=best['min_child_weight'],
        gamma=best['gamma']
    ),
    param_grid=narrow_params,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=0
)

grid_search.fit(X_train, y_train)

print(f"Best GridSearch Score: {grid_search.best_score_:.4f}")
print(f"Best Parameters:")
for param, value in grid_search.best_params_.items():
    if isinstance(value, float):
        print(f"  {param}: {value:.4f}")
    else:
        print(f"  {param}: {value}")
print()

# ==================================
# Step 5: Compare All Three on Test Set
# ==================================
print("=" * 50)
print("STEP 5: Final Comparison on Test Set")
print("=" * 50)

# Train default model on full training set
default_model.fit(X_train, y_train)
default_test_score = default_model.score(X_test, y_test)

# RandomizedSearch best model
random_test_score = random_search.best_estimator_.score(X_test, y_test)

# GridSearch best model (fine-tuned)
grid_test_score = grid_search.best_estimator_.score(X_test, y_test)

# Print comparison table
print(f"\n{'Model':<25} {'CV Score':<12} {'Test Score':<12}")
print("-" * 49)
print(f"{'Default XGBoost':<25} {default_scores.mean():<12.4f} {default_test_score:<12.4f}")
print(f"{'RandomizedSearch':<25} {random_search.best_score_:<12.4f} {random_test_score:<12.4f}")
print(f"{'GridSearch (fine-tuned)':<25} {grid_search.best_score_:<12.4f} {grid_test_score:<12.4f}")

print("\n--- Tuning Complete! ---")
```

**Expected Output:**

```
Training samples: 142
Test samples: 36
Number of features: 13
Number of classes: 3

==================================================
STEP 2: Default XGBoost Model
==================================================
Default CV Accuracy: 0.9577 (+/- 0.0329)

==================================================
STEP 3: Broad RandomizedSearch
==================================================
Best RandomizedSearch Score: 0.9789
Best Parameters:
  colsample_bytree: 0.8732
  gamma: 0.1205
  learning_rate: 0.1847
  max_depth: 4
  min_child_weight: 3
  n_estimators: 178
  subsample: 0.9121

==================================================
STEP 4: Narrow GridSearch (Fine-Tuning)
==================================================
Best GridSearch Score: 0.9789
Best Parameters:
  learning_rate: 0.1847
  max_depth: 4
  n_estimators: 178
  subsample: 0.9100

==================================================
STEP 5: Final Comparison on Test Set
==================================================

Model                     CV Score     Test Score
-------------------------------------------------
Default XGBoost           0.9577       0.9444
RandomizedSearch          0.9789       0.9722
GridSearch (fine-tuned)    0.9789       0.9722

--- Tuning Complete! ---
```

### What We Learned from This Example

1. **Default model** scored 95.77% on cross-validation and 94.44% on the test set.
2. **After RandomizedSearch**, the score improved to 97.89% CV and 97.22% test.
3. **GridSearch fine-tuning** confirmed the RandomizedSearch results.
4. Tuning improved test accuracy by about 3 percentage points.

That may not sound like much, but in many applications (like medical diagnosis or fraud detection), a 3% improvement can be very significant.

---

## Common Mistakes

**Mistake 1: Tuning on the test set.**
Never include the test set in hyperparameter tuning. GridSearchCV uses cross-validation on the training data only. The test set should be used only for final evaluation.

```python
# WRONG: Tuning on all data, then testing on the same data
grid_search.fit(X, y)  # Uses ALL data for tuning
score = grid_search.score(X, y)  # Tests on SAME data = overly optimistic!

# RIGHT: Tune on training data, evaluate on separate test set
grid_search.fit(X_train, y_train)  # Tune on training data only
score = grid_search.score(X_test, y_test)  # Test on unseen data
```

**Mistake 2: Too many hyperparameters at once.**
Start with 2-3 most important hyperparameters. Adding more increases search time exponentially.

**Mistake 3: Forgetting to set `random_state`.**
Without `random_state`, results change every time you run the code. This makes it hard to compare results.

**Mistake 4: Using accuracy for imbalanced datasets.**
If your data has 99% of one class and 1% of another, accuracy is misleading. Use F1-score, AUC, or other appropriate metrics.

```python
# For imbalanced data, use a better scoring metric
grid_search = GridSearchCV(model, param_grid, cv=5, scoring='f1_weighted')
```

**Mistake 5: Setting the grid too narrow.**
If the best value is always at the edge of your grid, expand the range. The true best value might be outside your grid.

---

## Best Practices

1. **Start with RandomizedSearch, then narrow with GridSearch.** This two-step approach saves time and gives great results.

2. **Use `n_jobs=-1` to use all CPU cores.** This makes the search much faster.

3. **Always use cross-validation.** GridSearchCV and RandomizedSearchCV do this automatically.

4. **Choose the right scoring metric.** Use `accuracy` for balanced datasets. Use `f1`, `roc_auc`, or `f1_weighted` for imbalanced ones.

5. **Keep the test set separate.** Only use it once at the very end to get your final score.

6. **Include default values in your grid.** This lets you see if tuning actually helps.

7. **Be patient but practical.** Sometimes the default settings are already good enough. Do not spend hours tuning for a 0.1% improvement.

8. **Document your search.** Save the best parameters and scores so you can reproduce results later.

---

## Quick Summary

- **Parameters** are learned by the model. **Hyperparameters** are set by you before training.
- **Grid Search** tries every combination. It is thorough but slow.
- **Randomized Search** tries random combinations. It is faster and nearly as good.
- Both use **cross-validation** internally for reliable results.
- Use **`GridSearchCV`** for small search spaces. Use **`RandomizedSearchCV`** for large ones.
- The best strategy: **broad RandomizedSearch first, then narrow GridSearch**.
- Always evaluate the final model on a **separate test set**.

---

## Key Points to Remember

1. Hyperparameters are the "dials" you set before training. The model does not learn them.
2. GridSearchCV tries all combinations with cross-validation.
3. RandomizedSearchCV tries random combinations and is much faster.
4. `best_params_` gives you the winning hyperparameters.
5. `best_score_` gives you the best cross-validated score.
6. `best_estimator_` gives you the trained model with the best settings.
7. Never tune on the test set. Always keep it separate.
8. Use `n_jobs=-1` to speed up the search.
9. Start broad (RandomizedSearch), then narrow (GridSearch).
10. The right scoring metric depends on your problem (accuracy, F1, AUC, etc.).

---

## Practice Questions

### Question 1
What is the difference between a parameter and a hyperparameter?

**Answer:** A parameter is learned by the model during training (like the weights in a linear regression). A hyperparameter is set by you before training starts (like the number of trees in a Random Forest). The model cannot learn hyperparameters from data.

### Question 2
If you have a parameter grid with `n_estimators=[100, 200, 300]`, `max_depth=[3, 5, 7, 9]`, and `min_samples_split=[2, 5]`, how many total combinations will GridSearchCV try?

**Answer:** 3 x 4 x 2 = 24 combinations. With 5-fold cross-validation, that means 24 x 5 = 120 total model trainings.

### Question 3
Why is RandomizedSearch often preferred over GridSearch?

**Answer:** RandomizedSearch is much faster because it only tries a random subset of combinations (controlled by `n_iter`). Research has shown that it finds results nearly as good as GridSearch, especially when only a few hyperparameters matter most. It also supports sampling from continuous distributions, not just lists of values.

### Question 4
What does the "CV" in GridSearchCV stand for, and why is it important?

**Answer:** "CV" stands for Cross-Validation. It is important because instead of evaluating each combination on a single train/test split (which can be unreliable), it splits the training data into multiple folds and averages the scores. This gives a more reliable estimate of how well those hyperparameters will perform on new data.

### Question 5
After running GridSearchCV, what attribute gives you the trained model with the best hyperparameters?

**Answer:** `grid_search.best_estimator_` gives you the model already trained on the entire training set with the best hyperparameters. You can use it directly for predictions with `grid_search.predict(X_test)`.

---

## Exercises

### Exercise 1: Tune a Decision Tree

Load the breast cancer dataset (`from sklearn.datasets import load_breast_cancer`). Create a Decision Tree classifier. Define a parameter grid for `max_depth` (values: 3, 5, 7, 10, 15, None), `min_samples_split` (2, 5, 10), and `criterion` ('gini', 'entropy'). Use GridSearchCV with 5-fold cross-validation. Print the best parameters and best score. Compare with the default model.

### Exercise 2: RandomizedSearch on Gradient Boosting

Load the wine dataset. Create a GradientBoostingClassifier. Use RandomizedSearchCV with these distributions:
- `n_estimators`: randint(50, 500)
- `learning_rate`: uniform(0.01, 0.29)
- `max_depth`: randint(2, 10)
- `subsample`: uniform(0.6, 0.4)

Set `n_iter=30` and `cv=5`. Print the best parameters and compare with the default model's cross-validation score.

### Exercise 3: Two-Step Tuning

Using the breast cancer dataset and a Random Forest classifier, implement the two-step tuning strategy:
1. First, run RandomizedSearchCV with broad distributions and `n_iter=50`.
2. Then, create a narrow GridSearch grid around the best values found.
3. Compare the default model, RandomizedSearch result, and GridSearch result on a held-out test set.

---

## What Is Next?

You now know how to find the best settings for your models. But there is a problem. When you tune a model, you often write code like this: scale the data, encode categories, train the model. These are separate steps, and it is easy to make mistakes.

In the next chapter, you will learn about **Scikit-Learn Pipelines**. Pipelines chain all your preprocessing and modeling steps into a single object. This makes your code cleaner, safer, and easier to tune. You will even learn how to use GridSearchCV on an entire pipeline — tuning preprocessing and model settings together.
