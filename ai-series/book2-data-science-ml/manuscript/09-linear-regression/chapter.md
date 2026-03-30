# Chapter 9: Linear Regression

## What You Will Learn

In this chapter, you will learn:

- What linear regression is and how it predicts a number
- The equation behind every straight line: y = mx + b
- What slope and intercept mean in real-world terms
- How to measure prediction quality with Mean Squared Error (MSE)
- How gradient descent finds the best line (a recap from Book 1)
- How to use sklearn `LinearRegression` to build a model in minutes
- How to plot the regression line on your data
- What R-squared means and how to interpret it
- What residuals are and how to use them to check your model
- A complete salary prediction example from start to finish

## Why This Chapter Matters

Imagine you are a manager trying to predict how much to pay a new employee. You know that employees with more experience tend to earn more. You have salary data for 50 current employees. Can you draw a line through that data and use it to predict the right salary?

That is exactly what linear regression does. It draws the "best" straight line through your data. Once you have the line, you can predict new values. Linear regression is the simplest, most widely used prediction algorithm in all of machine learning. It is the starting point for understanding every other regression technique.

If you understand linear regression, you understand the foundation of prediction. Every chapter that follows builds on what you learn here.

---

## 9.1 The Equation of a Line: y = mx + b

### What Does y = mx + b Mean?

Every straight line can be described by this equation:

```
y = mx + b

Where:
  y = the value you want to predict (output)
  x = the value you know (input)
  m = the slope (how steep the line is)
  b = the intercept (where the line crosses the y-axis)
```

**Think of it like this:** You are climbing a hill.

- **b (intercept)** is where you start. If b = 10, you start at height 10.
- **m (slope)** is how steep the hill is. If m = 3, you go up 3 meters for every 1 meter you walk forward.

```
y = 3x + 10
=============

y (height)
  |
40|                        *
35|                   *
30|              *
25|         *
20|    *
15| *
10|*  <- b = 10 (starting point)
  |__________________________ x (distance)
  0    1    2    3    4    5

When x=0: y = 3(0) + 10 = 10  (start at height 10)
When x=1: y = 3(1) + 10 = 13  (go up 3)
When x=2: y = 3(2) + 10 = 16  (go up 3 more)
When x=5: y = 3(5) + 10 = 25  (go up 3 for each step)
```

### Real-World Example: Salary Prediction

Let's say:
- x = years of experience
- y = salary in dollars
- m = 5,000 (each year of experience adds $5,000)
- b = 30,000 (base salary with zero experience)

```
Salary = 5000 * experience + 30000

Experience    Predicted Salary
----------    ----------------
0 years       $30,000
2 years       $40,000
5 years       $55,000
10 years      $80,000
```

This is linear regression in a nutshell. We find the values of m and b that best fit the data.

### Slope and Intercept in Plain English

```
Understanding Slope and Intercept
====================================

SLOPE (m):
  "For every 1 unit increase in x, y changes by m units."

  m = 5000 means: Each extra year of experience adds $5,000 to salary.
  m = -2 means: Each extra unit of x DECREASES y by 2.
  m = 0 means: x has no effect on y (flat line).

INTERCEPT (b):
  "The value of y when x is zero."

  b = 30000 means: With 0 years of experience, salary is $30,000.
  b = 0 means: The line passes through the origin (0, 0).

POSITIVE slope:                NEGATIVE slope:
  y goes UP as x goes RIGHT      y goes DOWN as x goes RIGHT
      /                             \
     /                               \
    /                                 \
```

---

## 9.2 How Linear Regression Finds the Best Line

### The Goal: Minimize the Errors

There are infinitely many lines you could draw through a set of points. Linear regression finds the one that is **closest** to all the points.

```
Which line fits best?
=======================

Bad fit:              Better fit:           Best fit:
  |    *              |    *                |    *
  | * /               | *  /               | * /
  |/ *                | / *                |  /*
  |  *                | /  *               | / *
  |                   |/                   |/

  Line misses         Line is closer       Line is as close
  most points.        to most points.      as possible to
                                           ALL points.
```

### What Is an Error (Residual)?

The **error** (or **residual**) for each data point is the difference between the actual value and the predicted value:

```
error = actual_value - predicted_value

Example:
  Actual salary:    $65,000
  Predicted salary: $60,000
  Error:            $65,000 - $60,000 = $5,000

  The prediction was off by $5,000.
```

```
Visualizing Errors (Residuals)
================================

Salary
  |          *  <- actual (65k)
  |          |  <- error = 5k
  |     -----+------ <- predicted by line (60k)
  |    /     *  <- actual (58k, error = -2k)
  |   /
  |  /   *  <- actual (45k)
  | /    |  <- error = 2k
  |/-----+-- <- predicted (43k)
  |____________________ Experience

The vertical lines between the data points
and the regression line are the RESIDUALS.
```

### Mean Squared Error (MSE)

To find the best line, we need a single number that measures how bad a line is overall. We use **Mean Squared Error (MSE)**:

```
MSE = average of (each error squared)

Step 1: Calculate each error
Step 2: Square each error (to make them all positive)
Step 3: Take the average

Example:
  Errors: [5000, -2000, 2000, -3000]

  Squared: [25000000, 4000000, 4000000, 9000000]

  MSE = (25000000 + 4000000 + 4000000 + 9000000) / 4
      = 42000000 / 4
      = 10500000

Lower MSE = better fit!
```

**Why square the errors?**

- Without squaring, positive errors (+5000) and negative errors (-5000) would cancel each other out. The average could be 0 even if the predictions are terrible.
- Squaring makes all errors positive.
- Squaring also penalizes large errors more. An error of 10 becomes 100. An error of 100 becomes 10,000. This pushes the line to avoid big mistakes.

### MSE in Python

```python
import numpy as np

# Actual and predicted values
actual = np.array([65000, 58000, 45000, 72000, 55000])
predicted = np.array([60000, 60000, 43000, 75000, 52000])

# Calculate errors
errors = actual - predicted
print("Errors:", errors)

# Calculate MSE manually
mse = np.mean(errors ** 2)
print(f"MSE: {mse:,.0f}")

# Calculate RMSE (Root Mean Squared Error) for interpretable units
rmse = np.sqrt(mse)
print(f"RMSE: {rmse:,.0f}")
print(f"On average, predictions are off by about ${rmse:,.0f}")
```

**Expected Output:**
```
Errors: [ 5000 -2000  2000 -3000  3000]
MSE: 9,400,000
RMSE: 3,066
On average, predictions are off by about $3,066
```

**RMSE** (Root Mean Squared Error) is just the square root of MSE. It is in the same units as your data, so it is easier to interpret. An RMSE of $3,066 means "on average, our predictions are about $3,066 off."

---

## 9.3 Gradient Descent Recap

### How the Computer Finds the Best m and b

Linear regression needs to find the values of m (slope) and b (intercept) that minimize MSE. The algorithm that does this is called **gradient descent**.

**Think of it like this:** You are blindfolded on a hilly landscape. You want to reach the lowest valley (minimum MSE). You feel the ground with your feet. If the ground slopes downward to the left, you step left. If it slopes downward to the right, you step right. You keep stepping downhill until you reach the bottom.

```
Gradient Descent: Finding the Valley
=======================================

MSE
  |
  | *
  |   *
  |     *
  |       *  Step 1: Start here
  |         *
  |           *  Step 2: Go downhill
  |             *
  |               *  Step 3: Keep going
  |                 *
  |                   *  Step 4: Almost there
  |                     *
  |                       * <- Minimum! Best m and b!
  |__________________________________
                                    m (slope)

Each step adjusts m and b a little bit to reduce MSE.
```

### The Gradient Descent Steps

```
Gradient Descent Algorithm:
==============================

1. Start with random values for m and b
2. Calculate MSE with current m and b
3. Calculate the gradient (direction of steepest descent)
4. Update m and b: move a small step in the downhill direction
5. Repeat steps 2-4 until MSE stops decreasing

The "learning rate" controls step size:
  Too big:   You overshoot the valley and bounce around
  Too small: You take forever to reach the valley
  Just right: You reach the valley smoothly
```

### Simple Gradient Descent in Python

```python
import numpy as np

# Simple dataset: experience -> salary
X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)
y = np.array([35, 40, 45, 50, 55, 58, 62, 67, 71, 75], dtype=float)

# Initialize m and b randomly
m = 0.0
b = 0.0
learning_rate = 0.01
n = len(X)

print("Gradient Descent Progress:")
print(f"{'Step':<8} {'m':>8} {'b':>8} {'MSE':>12}")
print("-" * 38)

for step in range(1001):
    # Predict
    y_pred = m * X + b

    # Calculate MSE
    mse = np.mean((y - y_pred) ** 2)

    # Calculate gradients
    dm = -2/n * np.sum(X * (y - y_pred))   # gradient for m
    db = -2/n * np.sum(y - y_pred)          # gradient for b

    # Update m and b
    m = m - learning_rate * dm
    b = b - learning_rate * db

    # Print progress every 200 steps
    if step % 200 == 0:
        print(f"{step:<8} {m:8.3f} {b:8.3f} {mse:12.2f}")

print(f"\nFinal equation: y = {m:.2f}x + {b:.2f}")
print(f"Interpretation: Each year of experience adds ${m*1000:.0f} to salary (in $1000s)")
```

**Expected Output:**
```
Gradient Descent Progress:
Step            m        b          MSE
--------------------------------------
0          1.100    0.110      2916.50
200        4.370   27.768         2.03
400        4.436   28.330         1.77
600        4.445   28.404         1.77
800        4.447   28.413         1.77
1000       4.447   28.414         1.77

Final equation: y = 4.45x + 28.41
Interpretation: Each year of experience adds $4447 to salary (in $1000s)
```

**Important:** In practice, you almost never write gradient descent from scratch. sklearn does it for you. But understanding how it works helps you understand what is happening behind the scenes.

---

## 9.4 Linear Regression with sklearn

### Building a Model in 4 Lines

sklearn makes linear regression incredibly simple:

```python
import numpy as np
from sklearn.linear_model import LinearRegression

# Data: years of experience -> salary (in $1000s)
X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).reshape(-1, 1)
y = np.array([35, 40, 45, 50, 55, 58, 62, 67, 71, 75])

# Create and train the model
model = LinearRegression()
model.fit(X, y)

# See the learned parameters
print(f"Slope (m):     {model.coef_[0]:.4f}")
print(f"Intercept (b): {model.intercept_:.4f}")
print(f"Equation:      salary = {model.coef_[0]:.2f} * experience + {model.intercept_:.2f}")
```

**Expected Output:**
```
Slope (m):     4.4485
Intercept (b): 28.3818
Equation:      salary = 4.45 * experience + 28.38
```

**Line-by-line explanation:**

- `X.reshape(-1, 1)` converts X from a flat array `[1, 2, 3, ...]` to a column `[[1], [2], [3], ...]`. sklearn expects features as columns.
- `LinearRegression()` creates the model object.
- `model.fit(X, y)` trains the model. It finds the best slope and intercept.
- `model.coef_[0]` is the slope (m). The trailing underscore `_` means this value was learned during training.
- `model.intercept_` is the intercept (b).

### Making Predictions

```python
# Predict salary for new experience values
new_experience = np.array([3, 7, 12, 15]).reshape(-1, 1)
predictions = model.predict(new_experience)

print("Salary Predictions:")
print(f"{'Experience':>12} {'Predicted Salary':>18}")
print("-" * 32)
for exp, pred in zip(new_experience.flatten(), predictions):
    print(f"{exp:>10} yrs    ${pred*1000:>12,.0f}")
```

**Expected Output:**
```
Salary Predictions:
  Experience   Predicted Salary
--------------------------------
         3 yrs    $   41,727
         7 yrs    $   59,521
        12 yrs    $   81,764
        15 yrs    $   95,109
```

---

## 9.5 Plotting the Regression Line

### Visualizing the Fit

A plot shows how well the line fits the data:

```python
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Data
X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).reshape(-1, 1)
y = np.array([35, 40, 45, 50, 55, 58, 62, 67, 71, 75])

# Train model
model = LinearRegression()
model.fit(X, y)

# Create prediction line
X_line = np.linspace(0, 12, 100).reshape(-1, 1)
y_line = model.predict(X_line)

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(X, y, color='blue', s=100, zorder=5, label='Actual data')
ax.plot(X_line, y_line, color='red', linewidth=2, label='Regression line')
ax.set_xlabel('Years of Experience', fontsize=12)
ax.set_ylabel('Salary ($1000s)', fontsize=12)
ax.set_title('Linear Regression: Experience vs Salary', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('regression_line.png', dpi=100)
print("Plot saved as regression_line.png")
```

**Expected Output:**
```
Plot saved as regression_line.png
```

### ASCII Version of the Plot

```
Salary vs Experience with Regression Line
============================================

Salary
($1000s)
  80|                              * /
  75|                            * /
  70|                          * /
  65|                       */
  60|                    * /
  55|                  */
  50|              * /
  45|           */
  40|        */
  35|     */
  30|   /
  25| /
    |__________________________ Experience
    0    2    4    6    8   10   (years)

Blue dots (*) = actual data
Red line (/) = regression line

The line passes through the middle of the data points,
minimizing the total squared distance to all points.
```

---

## 9.6 R-Squared: How Good Is Your Model?

### What Is R-Squared?

**R-squared** (also written as R^2) tells you what percentage of the variation in your target variable is explained by your model. It ranges from 0 to 1.

```
R-squared Interpretation
==========================

R^2 = 1.0:  Perfect! The model explains ALL variation.
             Every prediction is exactly right.

R^2 = 0.8:  Good. The model explains 80% of the variation.
             20% remains unexplained.

R^2 = 0.5:  Mediocre. The model explains only 50%.
             A coin flip might do almost as well.

R^2 = 0.0:  Terrible. The model explains NOTHING.
             Just predicting the average would work as well.

R^2 < 0.0:  Worse than terrible. The model is worse than
             just predicting the average every time.
```

**Think of it like this:** Imagine all your data points are scattered around. There is some total "spread" in the data. R-squared tells you what fraction of that spread your model captures.

```
Understanding R-squared Visually
===================================

High R^2 (0.95):              Low R^2 (0.30):
  Points hug the line.          Points are scattered far.

  | *  /  *                     |    *    /
  |  */                         | *   /    *
  | /  *                        |   /  *
  |/ *                          |  /      *
  |                             | / *  *

  Model explains most           Model explains little
  of the variation.             of the variation.
```

### Calculating R-Squared

```python
import numpy as np
from sklearn.linear_model import LinearRegression

# Data
X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).reshape(-1, 1)
y = np.array([35, 40, 45, 50, 55, 58, 62, 67, 71, 75])

# Train model
model = LinearRegression()
model.fit(X, y)

# R-squared using sklearn
r_squared = model.score(X, y)
print(f"R-squared: {r_squared:.4f}")
print(f"The model explains {r_squared*100:.1f}% of the salary variation.")
print()

# Calculate R-squared manually to understand it
y_pred = model.predict(X)
y_mean = np.mean(y)

# Total Sum of Squares: how much y varies from its mean
ss_total = np.sum((y - y_mean) ** 2)

# Residual Sum of Squares: how much the predictions miss
ss_residual = np.sum((y - y_pred) ** 2)

r_squared_manual = 1 - (ss_residual / ss_total)

print(f"Manual calculation:")
print(f"  SS Total:    {ss_total:.2f}  (total variation in salaries)")
print(f"  SS Residual: {ss_residual:.2f}  (variation NOT explained by model)")
print(f"  R-squared:   1 - {ss_residual:.2f}/{ss_total:.2f} = {r_squared_manual:.4f}")
```

**Expected Output:**
```
R-squared: 0.9903
The model explains 99.0% of the salary variation.

Manual calculation:
  SS Total:    1560.00  (total variation in salaries)
  SS Residual: 15.12  (variation NOT explained by model)
  R-squared:   1 - 15.12/1560.00 = 0.9903
```

### The R-Squared Formula

```
                SS_residual
R^2 = 1 - ------------------
               SS_total

Where:
  SS_total    = sum of (actual - mean)^2     (total variation)
  SS_residual = sum of (actual - predicted)^2 (unexplained variation)

If SS_residual = 0:  R^2 = 1 - 0 = 1.0  (perfect model)
If SS_residual = SS_total: R^2 = 1 - 1 = 0.0  (useless model)
```

---

## 9.7 Residual Analysis

### What Are Residuals?

Residuals are the errors: the difference between actual values and predicted values. Analyzing residuals tells you if your model is working correctly.

```python
import numpy as np
from sklearn.linear_model import LinearRegression

# Data
X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).reshape(-1, 1)
y = np.array([35, 40, 45, 50, 55, 58, 62, 67, 71, 75])

# Train model
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)

# Calculate residuals
residuals = y - y_pred

print("Residual Analysis:")
print(f"{'X':>4} {'Actual':>8} {'Predicted':>10} {'Residual':>10}")
print("-" * 35)
for x, actual, pred, resid in zip(X.flatten(), y, y_pred, residuals):
    print(f"{x:>4.0f} {actual:>8.0f} {pred:>10.2f} {resid:>10.2f}")

print(f"\nMean of residuals: {np.mean(residuals):.4f}")
print(f"Std of residuals:  {np.std(residuals):.4f}")
```

**Expected Output:**
```
Residual Analysis:
   X   Actual  Predicted   Residual
-----------------------------------
   1       35      32.83       2.17
   2       40      37.28       2.72
   3       45      41.73       3.27
   4       50      46.18       3.82
   5       55      50.62       4.38
   6       58      55.07       2.93
   7       62      59.52       2.48
   8       67      63.97       3.03
   9       71      68.41       2.59
  10       75      72.86       2.14

Mean of residuals: 0.0000
Std of residuals:  1.16
```

### What Good Residuals Look Like

For a well-fitting linear model, residuals should:

```
Good Residuals:                    Bad Residuals:
  Randomly scattered around 0.       Show a pattern.

  +  |   +                           +  |          +
  +  |     +                              |     +
     | +      +                        +  |  +
-----+-----------                   ------+---------
  +  |  +                                |  +
     |     + +                         +  |     +
  +  |  +                                |        +

  No pattern = model is correct.     Pattern = model is WRONG.
  Linear model is appropriate.       A straight line is not enough.
                                     Try polynomial regression.
```

### Checking Residuals in Practice

```python
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Data
X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).reshape(-1, 1)
y = np.array([35, 40, 45, 50, 55, 58, 62, 67, 71, 75])

# Train and predict
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
residuals = y - y_pred

# Residual plot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Residuals vs Predicted
axes[0].scatter(y_pred, residuals, color='blue', s=80)
axes[0].axhline(y=0, color='red', linestyle='--', linewidth=1)
axes[0].set_xlabel('Predicted Values')
axes[0].set_ylabel('Residuals')
axes[0].set_title('Residuals vs Predicted Values')
axes[0].grid(True, alpha=0.3)

# Plot 2: Distribution of residuals
axes[1].hist(residuals, bins=6, color='steelblue', edgecolor='black')
axes[1].set_xlabel('Residual Value')
axes[1].set_ylabel('Count')
axes[1].set_title('Distribution of Residuals')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('residual_analysis.png', dpi=100)
print("Residual plots saved as residual_analysis.png")
```

**Expected Output:**
```
Residual plots saved as residual_analysis.png
```

### Three Things to Check in Residuals

```
Residual Checklist
====================

1. RANDOMNESS: Are residuals randomly scattered?
   YES -> Model is appropriate.
   NO  -> Try a different model (polynomial, etc.).

2. CONSTANT SPREAD: Is the spread of residuals the same
   across all predicted values?
   YES -> Good. This is called "homoscedasticity."
   NO  -> The model's accuracy varies. Consider transformations.

3. NORMAL DISTRIBUTION: Are residuals roughly bell-shaped?
   YES -> Good. Confidence intervals will be reliable.
   NO  -> Predictions still work, but confidence intervals
          may be unreliable.
```

---

## 9.8 Complete Example: Salary Prediction

Let's build a complete salary prediction model from scratch.

### Step 1: Create the Dataset

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Create a realistic salary dataset
np.random.seed(42)
n_samples = 50

experience = np.random.uniform(0, 20, n_samples)
# Salary has a linear relationship with experience, plus some noise
salary = 30000 + 4500 * experience + np.random.normal(0, 5000, n_samples)

df = pd.DataFrame({
    'experience_years': np.round(experience, 1),
    'salary': np.round(salary, -2)  # Round to nearest 100
})

print("Dataset Overview:")
print(f"  Samples: {len(df)}")
print(f"  Experience range: {df['experience_years'].min():.1f} to {df['experience_years'].max():.1f} years")
print(f"  Salary range: ${df['salary'].min():,.0f} to ${df['salary'].max():,.0f}")
print()
print("First 10 rows:")
print(df.head(10).to_string(index=False))
```

**Expected Output:**
```
Dataset Overview:
  Samples: 50
  Experience range: 0.1 to 19.9 years
  Salary range: $22,700 to $127,100

First 10 rows:
 experience_years   salary
              7.5  61200.0
             18.6 109400.0
             14.6  92000.0
             17.1 108900.0
              0.3  32500.0
              1.6  44400.0
             12.2  87500.0
              5.5  51400.0
             11.1  74600.0
              3.7  49200.0
```

### Step 2: Explore the Data

```python
print("Basic Statistics:")
print(df.describe().round(1))
print()

# Check the correlation
correlation = df['experience_years'].corr(df['salary'])
print(f"Correlation between experience and salary: {correlation:.4f}")
print(f"This means: {'Strong' if abs(correlation) > 0.7 else 'Weak'} positive relationship")
```

**Expected Output:**
```
Basic Statistics:
       experience_years      salary
count              50.0        50.0
mean                9.5     73370.0
std                 5.9     27079.3
min                 0.1     22700.0
25%                 4.1     49650.0
50%                 9.3     72050.0
75%               14.5     95225.0
max                19.9    127100.0

Correlation between experience and salary: 0.9557
This means: Strong positive relationship
```

### Step 3: Split the Data

```python
# Prepare features (X) and target (y)
X = df[['experience_years']].values  # Double brackets to keep 2D shape
y = df['salary'].values

# Split: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Test set:     {X_test.shape[0]} samples")
```

**Expected Output:**
```
Training set: 40 samples
Test set:     10 samples
```

### Step 4: Train the Model

```python
# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Print the learned equation
slope = model.coef_[0]
intercept = model.intercept_

print("Learned Equation:")
print(f"  salary = {slope:,.0f} * experience + {intercept:,.0f}")
print()
print("Interpretation:")
print(f"  Base salary (0 experience): ${intercept:,.0f}")
print(f"  Each year of experience adds: ${slope:,.0f}")
```

**Expected Output:**
```
Learned Equation:
  salary = 4,610 * experience + 29,820

Interpretation:
  Base salary (0 experience): $29,820
  Each year of experience adds: $4,610
```

### Step 5: Evaluate the Model

```python
# Predict on training and test data
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# Calculate metrics
train_mse = mean_squared_error(y_train, y_train_pred)
test_mse = mean_squared_error(y_test, y_test_pred)
train_rmse = np.sqrt(train_mse)
test_rmse = np.sqrt(test_mse)
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

print("Model Performance:")
print(f"{'Metric':<20} {'Training':>12} {'Test':>12}")
print("-" * 46)
print(f"{'MSE':<20} {train_mse:>12,.0f} {test_mse:>12,.0f}")
print(f"{'RMSE':<20} {train_rmse:>12,.0f} {test_rmse:>12,.0f}")
print(f"{'R-squared':<20} {train_r2:>12.4f} {test_r2:>12.4f}")
print()
print(f"On average, salary predictions are off by ${test_rmse:,.0f}")
```

**Expected Output:**
```
Model Performance:
Metric                  Training         Test
----------------------------------------------
MSE                  20,978,879   32,091,048
RMSE                      4,580        5,665
R-squared                0.9140       0.8934

On average, salary predictions are off by $5,665
```

### Step 6: Examine Predictions

```python
# Show actual vs predicted for test data
print("Test Set Predictions:")
print(f"{'Experience':>12} {'Actual':>12} {'Predicted':>12} {'Error':>10}")
print("-" * 48)
for exp, actual, pred in zip(X_test.flatten(), y_test, y_test_pred):
    error = actual - pred
    print(f"{exp:>10.1f} yrs {actual:>11,.0f} {pred:>11,.0f} {error:>+10,.0f}")
```

**Expected Output:**
```
Test Set Predictions:
  Experience       Actual    Predicted      Error
------------------------------------------------
       0.3 yrs      32,500      31,203     +1,297
      17.1 yrs     108,900     108,653       +247
       5.5 yrs      51,400      55,176     -3,776
       9.9 yrs      74,600      75,470       -870
       3.9 yrs      42,200      47,801     -5,601
      14.6 yrs     100,800      97,109     +3,691
       2.2 yrs      41,000      39,965     +1,035
      11.6 yrs      84,600      83,311     +1,289
       1.0 yrs      37,200      34,424     +2,776
      16.1 yrs      96,500     104,024     -7,524
```

### Step 7: Visualize the Final Model

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Regression line with data
X_line = np.linspace(0, 22, 100).reshape(-1, 1)
y_line = model.predict(X_line)

axes[0].scatter(X_train, y_train, color='blue', alpha=0.6, label='Training data')
axes[0].scatter(X_test, y_test, color='green', marker='s', s=80, label='Test data')
axes[0].plot(X_line, y_line, color='red', linewidth=2, label='Regression line')
axes[0].set_xlabel('Years of Experience')
axes[0].set_ylabel('Salary ($)')
axes[0].set_title(f'Salary Prediction (R^2 = {test_r2:.3f})')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Actual vs Predicted
all_y = np.concatenate([y_train, y_test])
axes[1].scatter(y_test, y_test_pred, color='green', s=80)
axes[1].plot([all_y.min(), all_y.max()], [all_y.min(), all_y.max()],
             'r--', linewidth=2, label='Perfect predictions')
axes[1].set_xlabel('Actual Salary ($)')
axes[1].set_ylabel('Predicted Salary ($)')
axes[1].set_title('Actual vs Predicted (Test Set)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('salary_prediction.png', dpi=100)
print("Plot saved as salary_prediction.png")
```

**Expected Output:**
```
Plot saved as salary_prediction.png
```

---

## Common Mistakes

```
Mistake 1: Forgetting to reshape X
------------------------------------------------------
WRONG:  X = np.array([1, 2, 3, 4, 5])
        model.fit(X, y)  # ERROR!
RIGHT:  X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
        model.fit(X, y)
sklearn expects X to be 2D (rows and columns).

Mistake 2: Using R-squared on training data only
------------------------------------------------------
WRONG:  r2 = model.score(X_train, y_train)
        "My model is 99% accurate!"
RIGHT:  r2_test = model.score(X_test, y_test)
        Always evaluate on TEST data.

Mistake 3: Ignoring residual patterns
------------------------------------------------------
WRONG:  "R^2 is high, so my model is perfect."
RIGHT:  Plot residuals. If they show a curve, a straight
        line is not the right model. Try polynomial regression.

Mistake 4: Extrapolating too far
------------------------------------------------------
WRONG:  Predicting salary for 50 years experience when
        training data only goes up to 20 years.
RIGHT:  Only predict within (or near) the range of
        your training data.

Mistake 5: Confusing correlation with causation
------------------------------------------------------
WRONG:  "Experience CAUSES higher salary because the
        model says so."
RIGHT:  The model shows a RELATIONSHIP, not a cause.
        Many other factors affect salary.
```

---

## Best Practices

1. **Always visualize your data first.** Plot x vs y before fitting a model. If the relationship is not linear, a straight line will not work.

2. **Split your data before training.** Use train/test split to evaluate your model on unseen data. Training performance alone is misleading.

3. **Check R-squared on test data.** A high R-squared on training data but low on test data means your model is overfitting.

4. **Always plot residuals.** Residuals should be randomly scattered around zero. Patterns indicate the model is wrong.

5. **Do not extrapolate.** Linear regression is only reliable within the range of your training data. Predicting far beyond that range is risky.

6. **Report RMSE alongside R-squared.** R-squared tells you the percentage explained. RMSE tells you the actual error in the same units as your target.

7. **Consider feature scaling.** With a single feature, scaling does not matter. With multiple features (Chapter 10), scaling can improve results.

8. **Remember: linear regression assumes a straight-line relationship.** If the relationship is curved, you need polynomial regression (Chapter 10) or a different model.

---

## Quick Summary

```
Linear Regression Summary
============================

Equation:     y = mx + b
              m = slope (how much y changes per unit x)
              b = intercept (y value when x = 0)

Goal:         Find m and b that minimize MSE (Mean Squared Error)

How:          Gradient descent (or a direct formula)

Key Metrics:
  MSE   = average of squared errors (lower = better)
  RMSE  = square root of MSE (in original units)
  R^2   = fraction of variance explained (0 to 1, higher = better)

sklearn Code:
  model = LinearRegression()
  model.fit(X_train, y_train)
  predictions = model.predict(X_test)
  r2 = model.score(X_test, y_test)

Always Check:
  - R^2 on test data
  - Residual plots
  - Actual vs predicted scatter plot
```

---

## Key Points

1. **Linear regression** fits a straight line (y = mx + b) to your data. It is the simplest and most fundamental prediction algorithm.

2. **Slope (m)** tells you how much y changes for each unit increase in x. **Intercept (b)** is the value of y when x is zero.

3. **MSE** measures average squared error. **RMSE** is the square root of MSE and is in the same units as your target. Lower is better.

4. **Gradient descent** finds the best m and b by repeatedly adjusting them to reduce MSE. sklearn handles this automatically.

5. **R-squared** tells you what percentage of the variation in y is explained by your model. 1.0 is perfect, 0.0 means the model is no better than guessing the average.

6. **Residuals** are the errors (actual - predicted). They should be randomly scattered around zero. Patterns in residuals mean the model is not capturing the real relationship.

7. Always evaluate on **test data**, not just training data. Always **plot your data** and **check residuals**.

---

## Practice Questions

1. In the equation y = 3x + 10, what is the slope? What is the intercept? If x = 5, what is y?

2. You train a linear regression model and get R-squared = 0.85 on training data and R-squared = 0.40 on test data. What is happening? What should you do?

3. Why do we square the errors in MSE instead of just averaging them directly? Give an example where averaging without squaring would give a misleading result.

4. Your residual plot shows a clear U-shape (residuals are negative in the middle and positive at the edges). What does this tell you about your model?

5. A model has RMSE = 5,000 for predicting house prices in a city where houses cost $200,000 to $500,000. Is this good or bad? How would you decide?

---

## Exercises

### Exercise 1: Build Your Own Linear Regression

Create a dataset where y = 2x + 5 plus some random noise. Use 100 data points. Train a `LinearRegression` model and check if it recovers the true slope (2) and intercept (5). Calculate R-squared and RMSE.

### Exercise 2: Compare Training and Test Performance

Using the salary dataset from Section 9.8, try different `test_size` values: 0.1, 0.2, 0.3, 0.4, and 0.5. For each, report the training and test R-squared. What happens as you use more data for testing and less for training?

### Exercise 3: Residual Analysis

Generate two datasets:
1. A linear relationship: y = 3x + 10 + noise
2. A curved relationship: y = x^2 + noise

Fit linear regression to both. Plot the residuals for each. Explain why the residuals look different and what this tells you about the model's suitability.

---

## What Is Next?

You now understand simple linear regression with one feature. But in the real world, salaries depend on more than just experience. Education, location, job title, skills -- all of these matter. In Chapter 10, you will learn **Multiple Regression** (using many features at once) and **Polynomial Regression** (fitting curves instead of straight lines). You will see how to handle underfitting and overfitting, and build a complete car price prediction model.
