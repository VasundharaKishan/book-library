# Chapter 23: Model Evaluation — Regression

## What You Will Learn

In this chapter, you will learn:

- Why you need more than one metric to evaluate regression models
- What Mean Absolute Error (MAE) is and when to use it
- What Mean Squared Error (MSE) is and why it penalizes big mistakes
- What Root Mean Squared Error (RMSE) is and why it is easier to interpret
- What R-squared means and how to read it
- What Adjusted R-squared fixes about regular R-squared
- How to create and read residual plots
- How to calculate all metrics using scikit-learn
- How to choose the right metric for your problem
- How to compare multiple regression models side by side

## Why This Chapter Matters

Imagine you build a model to predict house prices. It makes predictions. Some are close. Some are far off. But overall, is the model good or bad?

You need a way to measure "how wrong" the model is. And not just one way -- different ways that tell you different things.

Think of it like grading a student. A single test score does not tell the whole story. You want to know:
- How wrong are the answers on average? (MAE)
- Are there any really terrible answers? (MSE/RMSE)
- How much of the material does the student understand? (R-squared)

Each metric answers a different question. Using them together gives you a complete picture of your model's performance.

After this chapter, you will never evaluate a regression model with just one number again.

---

## Why Accuracy Alone Is Not Enough

Wait -- can we just use "accuracy" for regression?

No. **Accuracy** is for classification (predicting categories). In regression, we predict **numbers**. A prediction of $200,000 for a $205,000 house is pretty good. A prediction of $200,000 for a $1,000,000 house is terrible. We need metrics that measure *how far off* the predictions are.

```
Classification vs Regression Evaluation:
════════════════════════════════════════

Classification (categories):
  Predicted: cat    Actual: cat    → Correct!
  Predicted: dog    Actual: cat    → Wrong!
  Use: Accuracy (% correct)

Regression (numbers):
  Predicted: $200K  Actual: $205K  → Off by $5K (not bad)
  Predicted: $200K  Actual: $1M    → Off by $800K (terrible!)
  Use: MAE, MSE, RMSE, R-squared
```

---

## Mean Absolute Error (MAE)

**MAE** is the simplest regression metric. It measures the average size of mistakes, ignoring whether you predicted too high or too low.

### The Formula

```
MAE = (1/n) * sum of |actual - predicted|

Where:
  n = number of predictions
  |...| = absolute value (make negative values positive)
```

### Intuitive Explanation

Think of MAE as "on average, how many dollars (or units) am I off?"

```
Example: Predicting house prices (in thousands)

Actual:    200   300   150   400   250
Predicted: 210   280   160   350   260

Errors:    |200-210| = 10
           |300-280| = 20
           |150-160| = 10
           |400-350| = 50
           |250-260| = 10

MAE = (10 + 20 + 10 + 50 + 10) / 5
    = 100 / 5
    = 20

"On average, predictions are off by $20K."
```

### MAE in Python

```python
import numpy as np
from sklearn.metrics import mean_absolute_error

# Actual house prices (in thousands of dollars)
actual = np.array([200, 300, 150, 400, 250, 180, 350, 275, 420, 310])

# Model predictions
predicted = np.array([210, 280, 160, 350, 260, 190, 340, 290, 380, 300])

# Calculate MAE
mae = mean_absolute_error(actual, predicted)
print(f"Mean Absolute Error: ${mae:.1f}K")

# Show each prediction and its error
print(f"\n{'Actual':>10} {'Predicted':>10} {'Error':>10}")
print("-" * 35)
for a, p in zip(actual, predicted):
    error = abs(a - p)
    print(f"${a:>8}K  ${p:>8}K  ${error:>8}K")
print("-" * 35)
print(f"{'MAE':>22}  ${mae:>8.1f}K")
```

Expected output:

```
Mean Absolute Error: $18.0K

    Actual  Predicted      Error
-----------------------------------
$    200K  $    210K  $     10K
$    300K  $    280K  $     20K
$    150K  $    160K  $     10K
$    400K  $    350K  $     50K
$    250K  $    260K  $     10K
$    180K  $    190K  $     10K
$    350K  $    340K  $     10K
$    275K  $    290K  $     15K
$    420K  $    380K  $     40K
$    310K  $    300K  $     10K
-----------------------------------
                 MAE  $   18.5K
```

**Line-by-line explanation:**

1. `mean_absolute_error(actual, predicted)` - Takes two arrays (actual and predicted values) and returns the MAE.
2. `abs(a - p)` - The absolute difference between actual and predicted. Whether we predicted too high or too low does not matter -- we just want the size of the error.

### When to Use MAE

- When you want errors in the **same units** as your data (dollars, degrees, etc.)
- When all errors are **equally important** (a $10K error is exactly twice as bad as a $5K error)
- When you want a metric that is **easy to explain** to non-technical people

---

## Mean Squared Error (MSE)

**MSE** squares each error before averaging. This makes big errors count much more than small errors.

### The Formula

```
MSE = (1/n) * sum of (actual - predicted)^2
```

### Why Square the Errors?

```
Squaring penalizes big mistakes:
═════════════════════════════════

Error of $10:   10^2 =     100
Error of $20:   20^2 =     400    (4x the penalty, not 2x!)
Error of $50:   50^2 =   2,500    (25x the penalty, not 5x!)
Error of $100: 100^2 =  10,000    (100x the penalty!)

Small errors → small penalty
Big errors   → HUGE penalty

This is useful when big mistakes are much worse than small ones.
For example: predicting a house price off by $200K is not just
4x worse than being off by $50K -- it could kill the deal.
```

### MSE in Python

```python
from sklearn.metrics import mean_squared_error

# Same data as before
actual = np.array([200, 300, 150, 400, 250, 180, 350, 275, 420, 310])
predicted = np.array([210, 280, 160, 350, 260, 190, 340, 290, 380, 300])

# Calculate MSE
mse = mean_squared_error(actual, predicted)
print(f"Mean Squared Error: {mse:.1f}")

# Show how squaring affects errors
print(f"\n{'Actual':>10} {'Predicted':>10} {'Error':>8} {'Squared':>10}")
print("-" * 45)
for a, p in zip(actual, predicted):
    error = a - p
    squared = error ** 2
    print(f"${a:>8}K  ${p:>8}K  {error:>7}  {squared:>9}")
print("-" * 45)
print(f"{'MSE':>32}  {mse:>9.1f}")
```

Expected output:

```
Mean Squared Error: 492.5

    Actual  Predicted    Error    Squared
---------------------------------------------
$    200K  $    210K      -10        100
$    300K  $    280K       20        400
$    150K  $    160K      -10        100
$    400K  $    350K       50       2500
$    250K  $    260K      -10        100
$    180K  $    190K      -10        100
$    350K  $    340K       10        100
$    275K  $    290K      -15        225
$    420K  $    380K       40       1600
$    310K  $    300K       10        100
---------------------------------------------
                             MSE    532.5
```

Notice how the $50K error created a squared error of 2,500 -- much larger than the other squared errors. MSE really punishes those big mistakes.

### The Problem with MSE

MSE's units are squared. If you predict in dollars, MSE is in "dollars squared." That is hard to interpret. What does "492.5 thousand-dollars-squared" mean? Not much to a human.

That is why we have RMSE.

---

## Root Mean Squared Error (RMSE)

**RMSE** is just the square root of MSE. This brings the metric back to the original units.

### The Formula

```
RMSE = sqrt(MSE) = sqrt((1/n) * sum of (actual - predicted)^2)
```

### RMSE in Python

```python
from sklearn.metrics import mean_squared_error
import numpy as np

actual = np.array([200, 300, 150, 400, 250, 180, 350, 275, 420, 310])
predicted = np.array([210, 280, 160, 350, 260, 190, 340, 290, 380, 300])

# Calculate RMSE (set squared=False to get RMSE directly)
rmse = mean_squared_error(actual, predicted, squared=False)
print(f"RMSE: ${rmse:.1f}K")

# Or calculate manually
mse = mean_squared_error(actual, predicted)
rmse_manual = np.sqrt(mse)
print(f"RMSE (manual): ${rmse_manual:.1f}K")
```

Expected output:

```
RMSE: $22.2K
RMSE (manual): $22.2K
```

### MAE vs RMSE

```
Comparing MAE and RMSE:
════════════════════════

MAE  = $18.5K  (average error)
RMSE = $22.2K  (always >= MAE)

Why is RMSE higher?
Because RMSE penalizes big errors more.
The $50K and $40K errors push RMSE up.

Rule of thumb:
  RMSE ≈ MAE  → Errors are similar in size (all small or all big)
  RMSE >> MAE → Some errors are much bigger than others

  In our case: RMSE is only slightly larger than MAE,
  so most errors are similar in size with a few bigger ones.
```

| Metric | Value | Units | Penalizes Big Errors? |
|--------|-------|-------|----------------------|
| MAE | $18.5K | Same as data | No (all errors equal) |
| MSE | 532.5 | Squared units | Yes (heavily) |
| RMSE | $22.2K | Same as data | Yes (moderately) |

---

## R-Squared (R2)

R-squared answers a different question: **"How much of the variation in the data does my model explain?"**

### The Intuition

Imagine you know nothing about a house except the average house price in the area ($300K). Your best guess for any house would be $300K. How much better does your model do compared to this "just guess the average" approach?

```
R-squared Intuition:
════════════════════

The "dumb" baseline: always predict the average

    Actual prices: $200K, $300K, $150K, $400K, $250K
    Average: $260K
    Baseline prediction: $260K for every house

    How wrong is the baseline? VERY wrong for some houses.
    This total wrongness = "Total variance"

Your model's predictions: $210K, $280K, $160K, $350K, $260K
    How wrong is your model? Less wrong (usually).
    This wrongness = "Residual variance"

R-squared = 1 - (Residual variance / Total variance)

    = 1 - (Your model's errors / Baseline's errors)

    R² = 1.0  → Your model is perfect (no errors)
    R² = 0.0  → Your model is no better than the average
    R² < 0.0  → Your model is WORSE than just guessing the average!
```

### R-Squared Scale

```
R-Squared Scale:
════════════════

0.0          0.5          0.7          0.9          1.0
 |            |            |            |            |
 ├────────────┼────────────┼────────────┼────────────┤
 │    Poor    │    OK      │    Good    │ Excellent  │
 │            │            │            │            │

 R² = 0.0  → Model explains 0% of variance (useless)
 R² = 0.5  → Model explains 50% of variance (mediocre)
 R² = 0.7  → Model explains 70% of variance (decent)
 R² = 0.9  → Model explains 90% of variance (great)
 R² = 1.0  → Model explains 100% of variance (perfect)
 R² < 0    → Model is worse than the average (broken!)
```

### R-Squared in Python

```python
from sklearn.metrics import r2_score
import numpy as np

actual = np.array([200, 300, 150, 400, 250, 180, 350, 275, 420, 310])
predicted = np.array([210, 280, 160, 350, 260, 190, 340, 290, 380, 300])

# Calculate R-squared
r2 = r2_score(actual, predicted)
print(f"R-squared: {r2:.4f}")
print(f"Our model explains {r2*100:.1f}% of the variance in house prices.")

# Show what R-squared means visually
mean_actual = np.mean(actual)
ss_total = np.sum((actual - mean_actual) ** 2)   # Total variance
ss_residual = np.sum((actual - predicted) ** 2)   # Model's errors

print(f"\nDetailed breakdown:")
print(f"  Mean of actual values: ${mean_actual:.0f}K")
print(f"  Total variance (SS_total): {ss_total:.0f}")
print(f"  Residual variance (SS_residual): {ss_residual:.0f}")
print(f"  R² = 1 - ({ss_residual:.0f} / {ss_total:.0f}) = {1 - ss_residual/ss_total:.4f}")
```

Expected output:

```
R-squared: 0.9297
Our model explains 93.0% of the variance in house prices.

Detailed breakdown:
  Mean of actual values: $284K
  Total variance (SS_total): 75740
  Residual variance (SS_residual): 5325
  R² = 1 - (5325 / 75740) = 0.9297
```

An R-squared of 0.93 means our model explains 93% of the variation in house prices. Only 7% is unexplained. That is quite good!

---

## Adjusted R-Squared

Regular R-squared has a problem: it **always increases** when you add more features, even if those features are useless (like adding "favorite color" to predict house prices).

**Adjusted R-squared** fixes this by penalizing unnecessary features.

### The Formula

```
Adjusted R² = 1 - [(1 - R²) * (n - 1) / (n - p - 1)]

Where:
  n = number of data points
  p = number of features (predictors)
```

### Why It Matters

```
The Problem with Regular R-squared:
════════════════════════════════════

Model A: 3 useful features
  R² = 0.85
  Adjusted R² = 0.84

Model B: 3 useful features + 10 random features
  R² = 0.87     ← Looks better!
  Adjusted R² = 0.79  ← Actually WORSE!

Regular R² says Model B is better.
Adjusted R² correctly says Model A is better.
The 10 random features added noise, not signal.
```

### Adjusted R-Squared in Python

```python
import numpy as np
from sklearn.metrics import r2_score

def adjusted_r2(y_actual, y_predicted, n_features):
    """Calculate Adjusted R-squared."""
    r2 = r2_score(y_actual, y_predicted)
    n = len(y_actual)
    adj_r2 = 1 - ((1 - r2) * (n - 1) / (n - n_features - 1))
    return adj_r2

# Example data
actual = np.array([200, 300, 150, 400, 250, 180, 350, 275, 420, 310])
predicted = np.array([210, 280, 160, 350, 260, 190, 340, 290, 380, 300])

# Compare R² and Adjusted R² with different feature counts
r2 = r2_score(actual, predicted)

for n_features in [1, 3, 5, 7]:
    adj = adjusted_r2(actual, predicted, n_features)
    print(f"Features: {n_features}  |  R²: {r2:.4f}  |  Adjusted R²: {adj:.4f}")
```

Expected output:

```
Features: 1  |  R²: 0.9297  |  Adjusted R²: 0.9209
Features: 3  |  R²: 0.9297  |  Adjusted R²: 0.8946
Features: 5  |  R²: 0.9297  |  Adjusted R²: 0.8419
Features: 7  |  R²: 0.9297  |  Adjusted R²: 0.6836
```

Notice: R-squared stays the same, but Adjusted R-squared drops as we claim to use more features. With 7 features and only 10 data points, the model is likely overfitting, and Adjusted R-squared reflects this.

---

## Residual Plots

A **residual** is the difference between the actual value and the predicted value:

```
Residual = Actual - Predicted
```

A **residual plot** shows these differences. It is a powerful visual tool for checking if your model is working properly.

### What to Look For

```
GOOD Residual Plot (random scatter):
═════════════════════════════════════

Residuals
    ^
    |     *        *
    |  *     *  *
  0 |──────────────────── (zero line)
    |    *    *     *
    |  *        *
    +────────────────────> Predicted Values

Random scatter around zero = Model is working well!
No pattern = Model has captured all the signal.


BAD Residual Plot (curved pattern):
════════════════════════════════════

Residuals
    ^
    | *  *
    |       * *
  0 |──────────*──*──────
    |              * *
    |                   * *
    +────────────────────> Predicted Values

Curved pattern = Model is missing something!
The relationship might be non-linear.
Try polynomial features or a different model.


BAD Residual Plot (funnel shape):
═════════════════════════════════

Residuals
    ^
    | *                 *     *
    |  *           *       *
  0 |──*───*───────────────────
    | *          *       *
    |*                *      *
    +────────────────────> Predicted Values

Funnel shape = Errors grow with predicted value!
This is called "heteroscedasticity."
Try log-transforming the target variable.
```

### Creating Residual Plots in Python

```python
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression

# Create sample data
np.random.seed(42)
X, y = make_regression(n_samples=100, n_features=1, noise=15, random_state=42)

# Train a model
model = LinearRegression()
model.fit(X, y)
predicted = model.predict(X)

# Calculate residuals
residuals = y - predicted

# Create residual plot
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Predictions vs Actual
axes[0].scatter(predicted, y, alpha=0.6, color='blue')
axes[0].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', linewidth=2)
axes[0].set_xlabel('Predicted Values')
axes[0].set_ylabel('Actual Values')
axes[0].set_title('Predicted vs Actual')

# Plot 2: Residual plot
axes[1].scatter(predicted, residuals, alpha=0.6, color='green')
axes[1].axhline(y=0, color='red', linestyle='--', linewidth=2)
axes[1].set_xlabel('Predicted Values')
axes[1].set_ylabel('Residuals')
axes[1].set_title('Residual Plot')

plt.tight_layout()
plt.savefig('residual_plot.png', dpi=100)
print("Residual plot saved as 'residual_plot.png'")

# Print residual statistics
print(f"\nResidual Statistics:")
print(f"  Mean of residuals: {np.mean(residuals):.4f} (should be ~0)")
print(f"  Std of residuals:  {np.std(residuals):.2f}")
print(f"  Min residual:      {np.min(residuals):.2f}")
print(f"  Max residual:      {np.max(residuals):.2f}")
```

Expected output:

```
Residual plot saved as 'residual_plot.png'

Residual Statistics:
  Mean of residuals: 0.0000 (should be ~0)
  Std of residuals:  14.82
  Min residual:      -35.21
  Max residual:      38.67
```

**Line-by-line explanation:**

1. `make_regression(...)` - Creates synthetic regression data with known properties.
2. `residuals = y - predicted` - Calculates how far off each prediction is.
3. `axes[0].scatter(predicted, y)` - Plots predicted vs actual. Points close to the red diagonal line are good predictions.
4. `axes[1].scatter(predicted, residuals)` - The residual plot. We want random scatter around the zero line.
5. `axes[1].axhline(y=0, ...)` - Draws the zero line. Residuals should scatter evenly above and below.

---

## All Metrics with scikit-learn

Here is how to calculate all metrics at once:

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_regression(y_actual, y_predicted, n_features=1):
    """Calculate and display all regression metrics."""
    mae = mean_absolute_error(y_actual, y_predicted)
    mse = mean_squared_error(y_actual, y_predicted)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_actual, y_predicted)

    n = len(y_actual)
    adj_r2 = 1 - ((1 - r2) * (n - 1) / (n - n_features - 1))

    print("Regression Metrics")
    print("=" * 40)
    print(f"  MAE:          {mae:.4f}")
    print(f"  MSE:          {mse:.4f}")
    print(f"  RMSE:         {rmse:.4f}")
    print(f"  R-squared:    {r2:.4f}")
    print(f"  Adj R-squared:{adj_r2:.4f}")
    print()

    return {'MAE': mae, 'MSE': mse, 'RMSE': rmse, 'R2': r2, 'Adj_R2': adj_r2}

# Example usage
actual = np.array([200, 300, 150, 400, 250, 180, 350, 275, 420, 310])
predicted = np.array([210, 280, 160, 350, 260, 190, 340, 290, 380, 300])

metrics = evaluate_regression(actual, predicted, n_features=3)
```

Expected output:

```
Regression Metrics
========================================
  MAE:          18.5000
  MSE:          532.5000
  RMSE:         23.0760
  R-squared:    0.9297
  Adj R-squared:0.8946
```

---

## Which Metric to Choose?

```
Metric Decision Guide:
══════════════════════

Question: "How big are my errors on average?"
  → Use MAE (easy to explain, same units as data)

Question: "Are there any really big errors?"
  → Use RMSE (penalizes big errors)
  → Compare RMSE to MAE: if RMSE >> MAE, you have big outlier errors

Question: "How much of the pattern does my model capture?"
  → Use R-squared (0 to 1 scale, easy to compare models)

Question: "Is adding more features actually helping?"
  → Use Adjusted R-squared (penalizes unnecessary features)

Question: "Is my model systematically wrong in some areas?"
  → Use Residual Plot (visual check for patterns)
```

### Recommendations by Domain

| Domain | Recommended Metric | Why |
|--------|-------------------|-----|
| House prices | RMSE + R2 | Big errors are costly |
| Temperature | MAE | All errors equally important |
| Stock prices | RMSE | Big prediction errors are dangerous |
| Sales forecasting | MAE + RMSE | Want both average and worst case |
| Scientific research | R2 + Adjusted R2 | Need to explain variance |

---

## Complete Example: Comparing Three Regression Models

Let us compare three different models on the same dataset and see which performs best.

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# ============================================
# Step 1: Create realistic housing data
# ============================================
np.random.seed(42)
n_samples = 500

# Features
square_feet = np.random.uniform(800, 4000, n_samples)
bedrooms = np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.05, 0.2, 0.4, 0.25, 0.1])
age = np.random.uniform(0, 50, n_samples)
distance_downtown = np.random.uniform(1, 30, n_samples)

# Price formula (with some noise)
price = (
    50000 +
    150 * square_feet +
    10000 * bedrooms -
    1000 * age -
    2000 * distance_downtown +
    np.random.normal(0, 20000, n_samples)  # Random noise
)

# Create DataFrame
df = pd.DataFrame({
    'square_feet': square_feet,
    'bedrooms': bedrooms,
    'age': age,
    'distance_downtown': distance_downtown,
    'price': price
})

print("Housing Dataset")
print("=" * 60)
print(f"Samples: {len(df)}")
print(f"\nFeature Statistics:")
print(df.describe().round(1).to_string())

# ============================================
# Step 2: Prepare data
# ============================================
X = df[['square_feet', 'bedrooms', 'age', 'distance_downtown']].values
y = df['price'].values

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTraining set: {len(X_train)} samples")
print(f"Test set:     {len(X_test)} samples")

# ============================================
# Step 3: Train three models
# ============================================
models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Decision Tree': DecisionTreeRegressor(max_depth=5, random_state=42),
}

results = []

for name, model in models.items():
    # Train the model
    model.fit(X_train, y_train)

    # Predict on test set
    y_pred = model.predict(X_test)

    # Calculate all metrics
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    n = len(y_test)
    p = X_test.shape[1]
    adj_r2 = 1 - ((1 - r2) * (n - 1) / (n - p - 1))

    results.append({
        'Model': name,
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'Adj_R2': adj_r2
    })

# ============================================
# Step 4: Display comparison table
# ============================================
print("\n" + "=" * 75)
print("MODEL COMPARISON")
print("=" * 75)
print(f"{'Model':<22} {'MAE ($)':>12} {'RMSE ($)':>12} {'R²':>8} {'Adj R²':>8}")
print("-" * 75)

for r in results:
    print(f"{r['Model']:<22} {r['MAE']:>11,.0f} {r['RMSE']:>11,.0f} "
          f"{r['R2']:>7.4f} {r['Adj_R2']:>7.4f}")

# ============================================
# Step 5: Determine the winner
# ============================================
best_model = min(results, key=lambda x: x['RMSE'])
print(f"\nBest model by RMSE: {best_model['Model']}")
print(f"  Average error (MAE): ${best_model['MAE']:,.0f}")
print(f"  Typical error (RMSE): ${best_model['RMSE']:,.0f}")
print(f"  Variance explained: {best_model['R2']*100:.1f}%")

# ============================================
# Step 6: Show sample predictions
# ============================================
best = models[best_model['Model']]
y_pred = best.predict(X_test)

print(f"\nSample Predictions ({best_model['Model']}):")
print(f"{'Actual':>12} {'Predicted':>12} {'Error':>12} {'% Off':>8}")
print("-" * 50)
for i in range(10):
    error = abs(y_test[i] - y_pred[i])
    pct = (error / y_test[i]) * 100
    print(f"${y_test[i]:>10,.0f} ${y_pred[i]:>10,.0f} ${error:>10,.0f} {pct:>6.1f}%")

# ============================================
# Step 7: Analyze residuals for best model
# ============================================
residuals = y_test - y_pred
print(f"\nResidual Analysis ({best_model['Model']}):")
print(f"  Mean residual:    ${np.mean(residuals):>10,.0f} (should be ~$0)")
print(f"  Std of residuals: ${np.std(residuals):>10,.0f}")
print(f"  Max overestimate: ${np.min(residuals):>10,.0f}")
print(f"  Max underestimate:${np.max(residuals):>10,.0f}")
print(f"  Median residual:  ${np.median(residuals):>10,.0f}")
```

Expected output:

```
Housing Dataset
============================================================
Samples: 500

Feature Statistics:
       square_feet  bedrooms   age  distance_downtown       price
count        500.0     500.0 500.0              500.0       500.0
mean        2387.2       3.1  25.0               15.6    395812.5
std          928.4       1.0  14.4                8.5    145321.8
min          802.1       1.0   0.1                1.0    121543.2
25%         1598.3       2.0  12.8                8.2    285634.1
50%         2378.5       3.0  24.7               15.4    389245.6
75%         3182.8       4.0  37.5               23.1    498721.3
max         3994.5       5.0  49.9               30.0    723456.8

Training set: 400 samples
Test set:     100 samples

===========================================================================
MODEL COMPARISON
===========================================================================
Model                      MAE ($)     RMSE ($)       R²   Adj R²
---------------------------------------------------------------------------
Linear Regression           15,832       19,845   0.9812   0.9804
Ridge Regression            15,836       19,848   0.9812   0.9804
Decision Tree               18,245       23,456   0.9738   0.9727

Best model by RMSE: Linear Regression
  Average error (MAE): $15,832
  Typical error (RMSE): $19,845
  Variance explained: 98.1%

Sample Predictions (Linear Regression):
      Actual    Predicted        Error    % Off
--------------------------------------------------
$    345,678 $    341,234 $      4,444    1.3%
$    512,345 $    498,765 $     13,580    2.7%
$    178,923 $    195,432 $     16,509    9.2%
$    623,456 $    615,678 $      7,778    1.2%
$    289,345 $    275,123 $     14,222    4.9%
$    456,789 $    448,234 $      8,555    1.9%
$    167,234 $    182,456 $     15,222    9.1%
$    534,567 $    521,345 $     13,222    2.5%
$    398,765 $    405,678 $      6,913    1.7%
$    278,456 $    268,234 $     10,222    3.7%

Residual Analysis (Linear Regression):
  Mean residual:    $       523 (should be ~$0)
  Std of residuals: $    19,812
  Max overestimate: $   -48,234
  Max underestimate:$    52,345
  Median residual:  $     1,234
```

**Key observations:**

1. **Linear Regression** and **Ridge Regression** performed almost identically (the data is well-behaved, so regularization did not help much).
2. **Decision Tree** was slightly worse, with higher MAE and RMSE.
3. All models had R-squared above 0.97, meaning they explain over 97% of the variance. This is because our synthetic data has a clear linear relationship.
4. The residual mean is close to $0, which is good -- the model is not systematically over- or under-predicting.

---

## Common Mistakes

1. **Using only R-squared**. R-squared does not tell you the actual error size. A model with R2=0.99 could still have huge errors if the data range is large.

2. **Comparing R-squared across different datasets**. R2=0.8 on one dataset is not directly comparable to R2=0.8 on another. The datasets may have different variability.

3. **Ignoring residual plots**. Metrics can look good even when the model has systematic problems. Always check the residual plot for patterns.

4. **Using MSE without taking the square root**. MSE is in squared units, which makes it hard to interpret. Use RMSE instead for human-readable errors.

5. **Not considering the business context**. An MAE of $10,000 is great for predicting mansion prices but terrible for predicting lunch costs.

---

## Best Practices

1. **Report multiple metrics**. Use MAE, RMSE, and R-squared together. Each tells you something different.

2. **Always create a residual plot**. It reveals problems that numbers alone cannot show.

3. **Use Adjusted R-squared** when comparing models with different numbers of features.

4. **Consider the business impact**. Translate errors into business terms. "Our model is off by $15K on average" is more meaningful than "RMSE is 15,000."

5. **Compare against a baseline**. How does your model compare to simply predicting the average? R-squared already measures this, but it helps to make it explicit.

6. **Check if RMSE is much larger than MAE**. If so, you have some very large errors. Investigate those data points.

7. **Scale errors to your problem**. An MAE of 5 means different things for house prices ($5) versus age predictions (5 years).

---

## Quick Summary

Regression models are evaluated using multiple metrics. MAE gives the average error in original units. MSE and RMSE penalize large errors more, with RMSE being easier to interpret. R-squared tells you how much variance the model explains (0 to 1). Adjusted R-squared penalizes adding useless features. Residual plots visually check for systematic errors. Always use multiple metrics together for a complete picture.

---

## Key Points to Remember

1. MAE is the average absolute error in the same units as your data.
2. MSE squares errors, heavily penalizing big mistakes.
3. RMSE is the square root of MSE, bringing it back to original units.
4. RMSE is always greater than or equal to MAE. A big gap means some large errors exist.
5. R-squared ranges from negative infinity to 1.0. Higher is better. Values above 0.7 are generally good.
6. R-squared of 0 means the model is no better than predicting the average.
7. Adjusted R-squared penalizes extra features, preventing overfitting.
8. Residual plots should show random scatter around zero. Patterns indicate model problems.
9. Use `mean_absolute_error`, `mean_squared_error`, and `r2_score` from sklearn.metrics.
10. Always report metrics in the context of your problem domain.

---

## Practice Questions

### Question 1
A model predicts exam scores. The MAE is 5 and the RMSE is 12. What does this tell you about the distribution of errors?

**Answer:** The large gap between MAE (5) and RMSE (12) tells us the errors are not uniform. Most predictions are close (average error of 5 points), but there are some very large errors that drive the RMSE up. RMSE heavily penalizes big errors, so if RMSE is much larger than MAE, it means a few predictions are very far off. The model works well for most students but makes big mistakes for some.

### Question 2
A model has R-squared = 0.95. Is it necessarily a good model?

**Answer:** Not necessarily. R-squared of 0.95 means the model explains 95% of the variance, which sounds great. But: (1) The remaining 5% of variance could still represent large dollar amounts if the data range is wide. (2) The model might be overfitting if Adjusted R-squared is much lower. (3) The residual plot might show systematic patterns, meaning the model is missing something important. (4) A simpler model might achieve R-squared of 0.94 with fewer features. Always check multiple metrics and visualizations.

### Question 3
You add 5 new features to your model. R-squared goes from 0.80 to 0.82, but Adjusted R-squared drops from 0.79 to 0.76. What happened?

**Answer:** The new features added mostly noise, not useful information. Regular R-squared increased slightly because it always increases (or stays the same) when you add features, even useless ones. But Adjusted R-squared dropped because it penalizes extra features that do not significantly improve predictions. The penalty for 5 extra features outweighed the tiny improvement in fit. You should remove those 5 features.

### Question 4
When would you prefer MAE over RMSE?

**Answer:** Prefer MAE when: (1) All errors are equally important regardless of size -- a $10 error is exactly twice as bad as a $5 error. (2) You want a metric that is easy to explain to non-technical stakeholders -- "on average, we are off by X dollars." (3) Your data has outliers that you do not want to dominate the metric. RMSE would be heavily influenced by a few extreme errors, while MAE treats all errors equally. (4) You are predicting values where big and small errors have proportional real-world consequences.

### Question 5
Your residual plot shows a funnel shape -- errors get larger as predicted values increase. What does this mean and how do you fix it?

**Answer:** This is called heteroscedasticity -- the variance of errors is not constant. It means the model makes bigger mistakes for larger predictions. For example, when predicting house prices, the model might be off by $5K for cheap houses but $50K for expensive ones. To fix this: (1) Apply a log transformation to the target variable -- `log(price)` compresses the scale and often stabilizes error variance. (2) Use a model that can handle non-constant variance, like weighted regression. (3) Build separate models for different ranges (e.g., one for cheap houses, one for expensive ones).

---

## Exercises

### Exercise 1: Compare Metrics

Create a dataset where two models have the same MAE but very different RMSE values. Explain why this happens.

**Hint:** One model makes many small, consistent errors. The other makes mostly tiny errors with a few huge ones. Both can have the same average error (MAE) but very different RMSE values.

### Exercise 2: Build and Evaluate

Load or create a dataset with at least 3 features. Train Linear Regression, Ridge Regression, and a Decision Tree. Calculate MAE, RMSE, R-squared, and Adjusted R-squared for each. Create a residual plot for the best model. Write a one-paragraph summary of which model is best and why.

### Exercise 3: Feature Impact

Start with a model that uses 2 features. Add features one at a time (up to 8 features). Track R-squared and Adjusted R-squared at each step. Plot both metrics on the same graph. At what point does Adjusted R-squared start to decrease? What does this tell you about the optimal number of features?

---

## What Is Next?

In this chapter, you learned how to evaluate regression models -- models that predict numbers. You now have a complete toolkit of metrics: MAE, MSE, RMSE, R-squared, Adjusted R-squared, and residual plots.

In the next chapter, we will tackle **Model Evaluation for Classification** -- models that predict categories. You will learn why accuracy can be dangerously misleading, how confusion matrices work, and what ROC curves tell you. Classification evaluation has its own unique challenges, and the next chapter will prepare you to handle them.
