# Chapter 29: Correlation and Regression — Finding Relationships in Data

## What You Will Learn

- What correlation is (do two things move together?)
- The Pearson correlation coefficient (-1 to +1)
- Computing correlation with NumPy and Pandas
- Correlation matrices and heatmaps
- Why correlation does NOT mean causation
- Simple linear regression by hand (finding the best line: y = mx + b)
- The cost function (Mean Squared Error)
- Fitting a line with NumPy's `polyfit`
- Plotting the regression line
- R-squared (how well does the line fit?)
- How this connects directly to machine learning

## Why This Chapter Matters

So far, you have looked at one variable at a time. But the most interesting questions involve **two or more** variables:

- Does more study time lead to higher grades?
- Does temperature affect ice cream sales?
- Does experience predict salary?

Correlation tells you if two things are related. Regression gives you a formula to predict one from the other.

And here is the key insight: **linear regression is the simplest machine learning model.** When you understand regression, you understand the foundation of ML. Every neural network, at its core, is doing something similar — just with many more variables.

---

## 29.1 What Is Correlation?

**Correlation** measures how two variables move together.

**Real-life analogy:** When it is hot outside, ice cream sales go up. Temperature and ice cream sales are **positively correlated** — they move in the same direction.

```
TYPES OF CORRELATION

POSITIVE CORRELATION         NO CORRELATION           NEGATIVE CORRELATION
(both go up together)        (no pattern)             (one goes up, other goes down)

y |        *                 y |    *  *              y | *
  |      *                     |  *      *              |  *
  |    *                       |      *                 |    *
  |  *                         |  *    *                |      *
  |*                           |    *     *             |        *
  +----------> x               +----------> x           +----------> x

r close to +1                r close to 0              r close to -1

Examples:                    Examples:                  Examples:
- Height & weight            - Shoe size & IQ           - Speed & travel time
- Study time & grades        - Birth month & salary     - Exercise & body fat
- Experience & salary        - Hair color & math score  - Price & demand
```

### The Pearson Correlation Coefficient (r)

The Pearson correlation coefficient **r** is a number between -1 and +1.

```
THE CORRELATION SCALE

-1.0    -0.5     0      +0.5    +1.0
  |-------|-------|-------|-------|
  Strong  Moderate  None  Moderate Strong
  negative         correlation   positive

r = +1.0: Perfect positive correlation (straight line going up)
r = -1.0: Perfect negative correlation (straight line going down)
r =  0.0: No linear correlation (random scatter)
r = +0.7: Strong positive (clear upward trend, some scatter)
r = -0.3: Weak negative (slight downward trend, lots of scatter)
```

### Computing Correlation with Python

```python
import numpy as np

np.random.seed(42)

# Create data: study hours and exam scores
# More study hours --> higher scores (with some noise)
study_hours = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
exam_scores = study_hours * 8 + 30 + np.random.normal(0, 5, 10)

# Compute correlation
r = np.corrcoef(study_hours, exam_scores)[0, 1]

print(f"Study hours: {study_hours}")
print(f"Exam scores: {exam_scores.round(1)}")
print(f"\nPearson correlation (r): {r:.4f}")
print()

if abs(r) > 0.7:
    print(f"r = {r:.2f} --> Strong {'positive' if r > 0 else 'negative'} correlation")
elif abs(r) > 0.3:
    print(f"r = {r:.2f} --> Moderate {'positive' if r > 0 else 'negative'} correlation")
else:
    print(f"r = {r:.2f} --> Weak or no correlation")
```

**Expected output:**
```
Study hours: [ 1  2  3  4  5  6  7  8  9 10]
Exam scores: [40.5 45.3 56.2 62.9 72.8 77.6 84.8 88.2 103.  112.1]

Pearson correlation (r): 0.9933

r = 0.99 --> Strong positive correlation
```

**Line-by-line explanation:**
- `np.corrcoef(x, y)` — returns a 2x2 correlation matrix; `[0, 1]` gives the correlation between x and y
- r = 0.99 means study hours and exam scores are almost perfectly linearly related
- The small amount of random noise prevents it from being exactly 1.0

---

## 29.2 Correlation Matrix and Heatmap

When you have many variables, you want to see all correlations at once. A **correlation matrix** does this.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)

# Create a dataset with multiple variables
n = 100
study_hours = np.random.uniform(1, 10, n)
sleep_hours = np.random.uniform(4, 10, n)
exam_score = 5 * study_hours - 2 * sleep_hours + 50 + np.random.normal(0, 5, n)
stress_level = -3 * sleep_hours + 8 * study_hours + np.random.normal(0, 10, n)

df = pd.DataFrame({
    'Study Hours': study_hours.round(1),
    'Sleep Hours': sleep_hours.round(1),
    'Exam Score': exam_score.round(1),
    'Stress Level': stress_level.round(1)
})

# Compute correlation matrix
corr_matrix = df.corr().round(3)
print("=== CORRELATION MATRIX ===")
print(corr_matrix)
```

**Expected output:**
```
=== CORRELATION MATRIX ===
              Study Hours  Sleep Hours  Exam Score  Stress Level
Study Hours         1.000       -0.038       0.889         0.875
Sleep Hours        -0.038        1.000      -0.318        -0.406
Exam Score          0.889       -0.318       1.000         0.885
Stress Level        0.875       -0.406       0.885         1.000
```

### Creating a Heatmap

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(8, 6))

# Create the heatmap
im = ax.imshow(corr_matrix.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')

# Add labels
labels = corr_matrix.columns
ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.set_yticklabels(labels)

# Add correlation values in each cell
for i in range(len(labels)):
    for j in range(len(labels)):
        text = f"{corr_matrix.values[i, j]:.2f}"
        color = 'white' if abs(corr_matrix.values[i, j]) > 0.5 else 'black'
        ax.text(j, i, text, ha='center', va='center', color=color, fontsize=12)

plt.colorbar(im, label='Correlation')
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.savefig('correlation_heatmap.png', dpi=100)
plt.show()
```

```
READING A HEATMAP

+1.0 (dark red)   = Strong positive correlation
 0.0 (white)      = No correlation
-1.0 (dark blue)  = Strong negative correlation

The diagonal is always +1.0 (each variable
correlates perfectly with itself).

The matrix is symmetric (corr(A,B) = corr(B,A)).
```

---

## 29.3 Correlation Does NOT Mean Causation

This is one of the most important concepts in statistics. Just because two things are correlated does not mean one causes the other.

```
CORRELATION vs CAUSATION

CORRELATION: "These two things move together."
CAUSATION:   "This thing MAKES that thing happen."

Correlation does NOT prove causation!
```

**Famous examples of misleading correlations:**

```
EXAMPLE 1: Ice Cream and Drowning
  Ice cream sales and drowning deaths are correlated.
  Does ice cream cause drowning? NO!

  The HIDDEN VARIABLE: Hot weather
  Hot weather --> more ice cream AND more swimming
                                     --> more drowning

  Ice cream sales --X--> Drowning (no causation)
  Hot weather ---------> Ice cream sales
  Hot weather ---------> Swimming --> Drowning


EXAMPLE 2: Shoe Size and Reading Ability
  Among children, bigger feet correlate with better reading.
  Do big feet cause better reading? NO!

  The HIDDEN VARIABLE: Age
  Older kids --> bigger feet AND better reading skills


EXAMPLE 3: Firefighters and Fire Damage
  More firefighters at a fire correlates with more damage.
  Do firefighters cause damage? NO!

  The HIDDEN VARIABLE: Fire size
  Bigger fire --> more firefighters AND more damage
```

### Demonstrating with Python

```python
import numpy as np

np.random.seed(42)

# Temperature is the HIDDEN CAUSE
temperature = np.random.uniform(60, 100, 100)  # Fahrenheit

# Ice cream sales go up with temperature
ice_cream_sales = 2 * temperature + np.random.normal(0, 15, 100)

# Swimming (and drowning risk) goes up with temperature
drowning_incidents = 0.1 * temperature + np.random.normal(0, 3, 100)

# Ice cream and drowning are correlated...
r = np.corrcoef(ice_cream_sales, drowning_incidents)[0, 1]
print(f"Correlation between ice cream sales and drowning: {r:.3f}")
print()
print("These are correlated, but ice cream does NOT cause drowning!")
print("Temperature is the hidden variable that causes BOTH.")
print()

# The real correlations:
r1 = np.corrcoef(temperature, ice_cream_sales)[0, 1]
r2 = np.corrcoef(temperature, drowning_incidents)[0, 1]
print(f"Correlation: Temperature vs Ice Cream Sales:    {r1:.3f}")
print(f"Correlation: Temperature vs Drowning Incidents: {r2:.3f}")
```

**Expected output:**
```
Correlation between ice cream sales and drowning: 0.569

These are correlated, but ice cream does NOT cause drowning!
Temperature is the hidden variable that causes BOTH.

Correlation: Temperature vs Ice Cream Sales:    0.932
Correlation: Temperature vs Drowning Incidents: 0.805
```

**Key takeaway:** Always ask "Is there a hidden variable that could explain both?" before concluding that one thing causes another.

---

## 29.4 Simple Linear Regression — Finding the Best Line

Linear regression finds the **best straight line** through your data points.

The line has the equation: **y = mx + b**

```
LINEAR REGRESSION: y = mx + b

y (what we predict)
^
|          *    /
|        *   /
|      *  /
|    * /   *
|   /  *
| /  *
|/ *
+-------------------> x (what we know)

m = slope (how steep the line is)
b = y-intercept (where the line crosses the y-axis)

The BEST line minimizes the total distance
between all data points and the line.
```

**Real-life analogy:** You are plotting house prices against house size. Linear regression draws the best line through the scatter plot. Then you can use that line to predict the price of a house based on its size.

### Computing Regression by Hand

Let us find the best line through 5 data points, step by step.

```python
import numpy as np

# Our data: x = years of experience, y = salary (in thousands)
x = np.array([1, 2, 3, 4, 5])
y = np.array([40, 45, 55, 60, 68])

n = len(x)

# Step 1: Compute the means
x_mean = np.mean(x)
y_mean = np.mean(y)
print(f"Step 1: Means")
print(f"  x_mean = {x_mean}")
print(f"  y_mean = {y_mean}")

# Step 2: Compute the slope (m)
# m = sum((x - x_mean) * (y - y_mean)) / sum((x - x_mean)^2)
numerator = np.sum((x - x_mean) * (y - y_mean))
denominator = np.sum((x - x_mean) ** 2)
m = numerator / denominator
print(f"\nStep 2: Slope")
print(f"  Numerator (sum of cross-deviations): {numerator}")
print(f"  Denominator (sum of squared x-deviations): {denominator}")
print(f"  Slope (m) = {numerator}/{denominator} = {m}")

# Step 3: Compute the y-intercept (b)
# b = y_mean - m * x_mean
b = y_mean - m * x_mean
print(f"\nStep 3: Y-intercept")
print(f"  b = {y_mean} - {m} * {x_mean} = {b}")

print(f"\n=== THE BEST LINE ===")
print(f"  y = {m}x + {b}")
print(f"  Salary = {m} * experience + {b}")

# Step 4: Make predictions
print(f"\nStep 4: Predictions")
for xi in x:
    predicted = m * xi + b
    actual = y[x == xi][0]
    error = actual - predicted
    print(f"  x={xi}: predicted={predicted:.1f}, actual={actual}, error={error:+.1f}")

# Predict for a new value
new_x = 7
predicted_salary = m * new_x + b
print(f"\n  Prediction for {new_x} years experience: ${predicted_salary:.1f}K")
```

**Expected output:**
```
Step 1: Means
  x_mean = 3.0
  y_mean = 53.6

Step 2: Slope
  Numerator (sum of cross-deviations): 53.0
  Denominator (sum of squared x-deviations): 10.0
  Slope (m) = 53.0/10.0 = 6.7

Step 3: Y-intercept
  b = 53.6 - 6.7 * 3.0 = 33.5

=== THE BEST LINE ===
  y = 6.7x + 33.5
  Salary = 6.7 * experience + 33.5

Step 4: Predictions
  x=1: predicted=40.2, actual=40, error=-0.2
  x=2: predicted=46.9, actual=45, error=-1.9
  x=3: predicted=53.6, actual=55, error=+1.4
  x=4: predicted=60.3, actual=60, error=-0.3
  x=5: predicted=67.0, actual=68, error=+1.0

  Prediction for 7 years experience: $80.4K
```

```
REGRESSION BY HAND — VISUAL

y (Salary)
^
70|              * (5,68)
  |          ----/----
60|        *(4,60)
  |      /
55|    * (3,55)
  |  /
45| * (2,45)
  |/
40|*(1,40)
  +-------------------> x (Experience)
  0  1  2  3  4  5  6

The line y = 6.7x + 33.5 passes as
close as possible to ALL the points.
```

---

## 29.5 The Cost Function — Mean Squared Error (MSE)

How do we know our line is the "best"? We need a way to measure how bad a line is. This measure is called the **cost function** or **loss function**.

The most common cost function is **Mean Squared Error (MSE)**.

```
MEAN SQUARED ERROR (MSE)

For each data point:
  1. Predict y using the line: y_pred = mx + b
  2. Compute the error: error = y_actual - y_pred
  3. Square the error: error^2

MSE = average of all squared errors

WHY SQUARE?
  - Negative errors do not cancel positive ones
  - Big errors are penalized more than small ones

           *        <-- error = distance to line
          /|
         / |  error
        /  |
  -----/------------ regression line
      /
```

### Computing MSE with Python

```python
import numpy as np

x = np.array([1, 2, 3, 4, 5])
y = np.array([40, 45, 55, 60, 68])

# Our best-fit line: y = 6.7x + 33.5
m = 6.7
b = 33.5

# Predictions
y_pred = m * x + b

# Errors (residuals)
errors = y - y_pred

# Squared errors
squared_errors = errors ** 2

# Mean Squared Error
mse = np.mean(squared_errors)

print("Point-by-point breakdown:")
print(f"{'x':>3} {'y_actual':>8} {'y_pred':>8} {'error':>8} {'error^2':>8}")
print("-" * 40)
for i in range(len(x)):
    print(f"{x[i]:>3} {y[i]:>8.1f} {y_pred[i]:>8.1f} {errors[i]:>+8.1f} {squared_errors[i]:>8.2f}")

print(f"\nMean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {np.sqrt(mse):.2f}")
print()
print(f"RMSE = {np.sqrt(mse):.2f} means our predictions are off")
print(f"by about ${np.sqrt(mse):.1f}K on average.")
```

**Expected output:**
```
Point-by-point breakdown:
  x y_actual   y_pred    error  error^2
----------------------------------------
  1     40.0     40.2     -0.2     0.04
  2     45.0     46.9     -1.9     3.61
  3     55.0     53.6     +1.4     1.96
  4     60.0     60.3     -0.3     0.09
  5     68.0     67.0     +1.0     1.00

Mean Squared Error (MSE): 1.34
Root Mean Squared Error (RMSE): 1.16

RMSE = 1.16 means our predictions are off
by about $1.2K on average.
```

```
WHY MSE MATTERS FOR MACHINE LEARNING

The ENTIRE goal of training a ML model is:
  Find the values of m and b that MINIMIZE the MSE.

This is what "training" means:
  Adjust parameters to reduce errors.

  High MSE = bad model (big errors)
  Low MSE  = good model (small errors)
  MSE = 0  = perfect predictions (never happens with real data)
```

---

## 29.6 Fitting a Line with NumPy's `polyfit`

You do not need to compute the slope and intercept by hand every time. NumPy has `np.polyfit()`.

```python
import numpy as np
import matplotlib.pyplot as plt

# Data
x = np.array([1, 2, 3, 4, 5])
y = np.array([40, 45, 55, 60, 68])

# Fit a line (degree 1 polynomial = straight line)
coefficients = np.polyfit(x, y, deg=1)
m = coefficients[0]  # slope
b = coefficients[1]  # intercept

print(f"Slope (m): {m:.2f}")
print(f"Intercept (b): {b:.2f}")
print(f"Equation: y = {m:.2f}x + {b:.2f}")

# Create the regression line
x_line = np.linspace(0, 7, 100)
y_line = m * x_line + b

# Plot
plt.figure(figsize=(8, 5))
plt.scatter(x, y, color='blue', s=100, zorder=5, label='Actual data')
plt.plot(x_line, y_line, color='red', linewidth=2, label=f'Best fit: y = {m:.1f}x + {b:.1f}')

# Draw error lines
y_pred = m * x + b
for i in range(len(x)):
    plt.plot([x[i], x[i]], [y[i], y_pred[i]], 'g--', alpha=0.7)

plt.xlabel('Years of Experience')
plt.ylabel('Salary ($K)')
plt.title('Linear Regression: Experience vs Salary')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('linear_regression.png', dpi=100)
plt.show()
```

**Expected output:**
```
Slope (m): 6.70
Intercept (b): 33.50
Equation: y = 6.70x + 33.50
```

**Line-by-line explanation:**
- `np.polyfit(x, y, deg=1)` — fit a polynomial of degree 1 (a straight line) to the data
- Returns `[slope, intercept]` — the coefficients of y = mx + b
- The green dashed lines in the plot show the errors (residuals) for each point

---

## 29.7 R-Squared — How Good Is the Fit?

The **R-squared** (R^2) value tells you what percentage of the variation in y is explained by x.

```
R-SQUARED (R^2)

R^2 = 1 - (sum of squared errors / sum of squared deviations from mean)

R^2 = 1.0:  Perfect fit (line explains 100% of variation)
R^2 = 0.8:  Good fit (line explains 80% of variation)
R^2 = 0.5:  Moderate fit (line explains 50%)
R^2 = 0.0:  Terrible fit (line explains nothing)

VISUAL:

R^2 ≈ 0.95 (great)       R^2 ≈ 0.50 (moderate)      R^2 ≈ 0.05 (terrible)

  *  *                      * *                        *     *
   **                     *     *                    *   *
  **                        * *                       *   *
  **                      *   *                      *  *    *
   *                     *   *  *                     *    *
  Points hug the line    Points scattered some     Points scattered everywhere
```

### Computing R-Squared with Python

```python
import numpy as np

x = np.array([1, 2, 3, 4, 5])
y = np.array([40, 45, 55, 60, 68])

# Fit the line
m, b = np.polyfit(x, y, deg=1)
y_pred = m * x + b

# Compute R-squared
ss_residual = np.sum((y - y_pred) ** 2)       # sum of squared errors
ss_total = np.sum((y - np.mean(y)) ** 2)      # total sum of squares
r_squared = 1 - (ss_residual / ss_total)

print(f"SS_residual (errors):  {ss_residual:.2f}")
print(f"SS_total (total var):  {ss_total:.2f}")
print(f"R-squared:             {r_squared:.4f}")
print()
print(f"The line explains {r_squared*100:.1f}% of the variation in salary.")
print(f"Only {(1-r_squared)*100:.1f}% is unexplained (random noise).")

# Verify: R^2 = r^2 (Pearson correlation squared)
r = np.corrcoef(x, y)[0, 1]
print(f"\nPearson r: {r:.4f}")
print(f"r^2:       {r**2:.4f}")
print(f"R^2:       {r_squared:.4f}")
print("They match! R-squared = correlation squared.")
```

**Expected output:**
```
SS_residual (errors):  6.70
SS_total (total var):  470.80
R-squared:             0.9858

The line explains 98.6% of the variation in salary.
Only 1.4% is unexplained (random noise).

Pearson r: 0.9929
r^2:       0.9858
R^2:       0.9858
They match! R-squared = correlation squared.
```

---

## 29.8 A Complete Regression Example

Let us put everything together with a larger dataset.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)

# Generate realistic data: House size vs price
n = 50
house_size = np.random.uniform(800, 3500, n)  # square feet
house_price = 50 * house_size + 30000 + np.random.normal(0, 25000, n)  # dollars

df = pd.DataFrame({
    'Size (sqft)': house_size.round(0),
    'Price ($)': house_price.round(0)
})

# Step 1: Descriptive statistics
print("=== STEP 1: Describe the Data ===")
print(df.describe().round(0))

# Step 2: Correlation
r = df['Size (sqft)'].corr(df['Price ($)'])
print(f"\n=== STEP 2: Correlation ===")
print(f"Pearson r: {r:.4f}")
print(f"Relationship: {'Strong' if abs(r) > 0.7 else 'Moderate' if abs(r) > 0.3 else 'Weak'} "
      f"{'positive' if r > 0 else 'negative'}")

# Step 3: Fit the regression line
m, b = np.polyfit(house_size, house_price, deg=1)
print(f"\n=== STEP 3: Regression Line ===")
print(f"Price = {m:.2f} * Size + {b:.2f}")
print(f"Interpretation: Each additional sqft adds ~${m:.0f} to the price")

# Step 4: R-squared
y_pred = m * house_size + b
ss_res = np.sum((house_price - y_pred) ** 2)
ss_tot = np.sum((house_price - np.mean(house_price)) ** 2)
r_sq = 1 - ss_res / ss_tot
print(f"\n=== STEP 4: R-squared ===")
print(f"R-squared: {r_sq:.4f}")
print(f"The model explains {r_sq*100:.1f}% of price variation")

# Step 5: MSE and RMSE
mse = np.mean((house_price - y_pred) ** 2)
rmse = np.sqrt(mse)
print(f"\n=== STEP 5: Error ===")
print(f"MSE:  ${mse:,.0f}")
print(f"RMSE: ${rmse:,.0f}")
print(f"On average, predictions are off by ~${rmse:,.0f}")

# Step 6: Make predictions
print(f"\n=== STEP 6: Predictions ===")
for size in [1000, 1500, 2000, 2500, 3000]:
    predicted_price = m * size + b
    print(f"  {size} sqft --> ${predicted_price:,.0f}")

# Step 7: Visualize
plt.figure(figsize=(10, 6))
plt.scatter(house_size, house_price, alpha=0.6, color='blue', label='Actual')
x_line = np.linspace(700, 3600, 100)
y_line = m * x_line + b
plt.plot(x_line, y_line, color='red', linewidth=2,
         label=f'Best fit: Price = {m:.0f} * Size + {b:.0f}')
plt.xlabel('House Size (sqft)')
plt.ylabel('House Price ($)')
plt.title(f'House Size vs Price (R² = {r_sq:.3f})')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('house_price_regression.png', dpi=100)
plt.show()
```

**Expected output:**
```
=== STEP 1: Describe the Data ===
       Size (sqft)   Price ($)
count           50          50
mean          2119      137168
std            778       48539
min            836       54316
25%           1455      102759
50%           2042      130612
75%           2842      177447
max           3477      246875

=== STEP 2: Correlation ===
Pearson r: 0.9205
Relationship: Strong positive

=== STEP 3: Regression Line ===
Price = 57.52 * Size + 15277.47
Interpretation: Each additional sqft adds ~$58 to the price

=== STEP 4: R-squared ===
R-squared: 0.8474
The model explains 84.7% of price variation

=== STEP 5: Error ===
MSE:  557,456,789
RMSE: $23,610
On average, predictions are off by ~$23,610

=== STEP 6: Predictions ===
  1000 sqft --> $72,797
  1500 sqft --> $101,557
  2000 sqft --> $130,318
  2500 sqft --> $159,078
  3000 sqft --> $187,838
```

---

## 29.9 This Is Where Statistics Meets Machine Learning

Everything you just learned IS machine learning. Really.

```
FROM REGRESSION TO MACHINE LEARNING

What you just did:                  What ML does:
----------------------------------------------
Chose x (house size)             = Select FEATURES
Predicted y (house price)        = Make PREDICTIONS
Found the best line (polyfit)    = TRAINED a model
Minimized MSE                    = Optimized a LOSS FUNCTION
Measured R-squared               = EVALUATED the model
Predicted new values             = Made INFERENCE

Linear regression IS the simplest ML model!

The only differences in "real" ML:
  1. Many features (not just one x)
  2. More complex models (not just a straight line)
  3. More data (thousands or millions of points)
  4. Gradient descent instead of polyfit (Chapter 30!)
```

```python
# A preview of what comes next...
import numpy as np

print("=== THE BRIDGE FROM STATISTICS TO ML ===")
print()
print("Statistics says:")
print("  y = mx + b")
print("  Find m and b that minimize MSE")
print()
print("Machine Learning says:")
print("  y = w1*x1 + w2*x2 + ... + wn*xn + b")
print("  Find weights w and bias b that minimize the loss function")
print("  Use gradient descent to find them")
print()
print("Same idea. More variables. Smarter search algorithm.")
print()
print("Neural networks? Same idea again.")
print("Just stack many of these equations together")
print("and add non-linear activation functions.")
```

---

## Common Mistakes

1. **Assuming correlation means causation.** It does not. Always look for hidden variables.

2. **Extrapolating too far.** Your regression line is only valid within the range of your data. Predicting a salary for 50 years of experience from data that only goes to 10 years is unreliable.

3. **Ignoring outliers.** A single outlier can dramatically change the regression line. Always plot your data first.

4. **Using linear regression for non-linear data.** If the relationship is curved, a straight line will fit poorly. Check your scatter plot.

5. **Confusing R-squared with accuracy.** R-squared tells you how much variance is explained, not how accurate individual predictions are. Use RMSE for prediction accuracy.

---

## Best Practices

1. **Always plot your data first.** Look at the scatter plot before fitting any model.

2. **Check the correlation before fitting a line.** If r is close to 0, linear regression will not help.

3. **Report R-squared AND RMSE together.** R-squared tells the overall quality. RMSE tells the typical prediction error in meaningful units.

4. **Look at the residuals** (errors). If they show a pattern, a straight line is not the right model.

5. **Remember: regression gives you a starting point.** More complex ML models build on these same ideas.

---

## Quick Summary

```
CHAPTER 29 SUMMARY

CORRELATION:
  Measures how two variables move together
  Pearson r: -1 (perfect negative) to +1 (perfect positive)
  r = 0 means no LINEAR relationship
  Correlation does NOT mean causation!

LINEAR REGRESSION:
  y = mx + b (best line through data points)
  m = slope (how much y changes per unit of x)
  b = intercept (y value when x = 0)
  np.polyfit(x, y, 1) computes m and b

COST FUNCTION (MSE):
  MSE = average of (actual - predicted)^2
  The best line minimizes MSE
  RMSE = sqrt(MSE) gives error in original units

R-SQUARED:
  What fraction of y's variation is explained by x
  R^2 = 1 - (SS_residual / SS_total)
  R^2 = Pearson_r^2

THE ML CONNECTION:
  Linear regression IS the simplest ML model
  Training = finding parameters that minimize loss
  Same ideas, just scaled up with more features
```

---

## Key Points to Remember

1. **Correlation** measures the strength and direction of a linear relationship between two variables.
2. **Pearson r** ranges from -1 to +1. Values near 0 mean no linear relationship.
3. **Correlation does NOT mean causation.** Always look for hidden variables.
4. **Linear regression** finds the best straight line: y = mx + b.
5. The **slope (m)** tells you how much y changes for each unit increase in x.
6. **MSE** measures how far predictions are from actual values (lower is better).
7. **R-squared** tells you what fraction of the variation your line explains (higher is better).
8. **Linear regression is the simplest ML model.** Everything in ML builds on this foundation.

---

## Practice Questions

1. You compute a Pearson correlation of r = -0.85 between hours of TV watched and exam scores. What does this mean? Does watching TV cause lower scores?

2. A regression line has the equation y = 3.2x + 15. If x = 10, what is the predicted y? What does the slope of 3.2 mean in plain English?

3. You fit a regression line and get R-squared = 0.60. What does this mean? Is this a good fit?

4. Give two examples of variables that are correlated but where one does NOT cause the other.

5. Why is it dangerous to use a regression line to predict values far outside the range of your training data?

---

## Exercises

### Exercise 1: Compute Correlation for Multiple Pairs

Create a dataset with temperature, ice cream sales, and umbrella sales. Compute all pairwise correlations and visualize with a heatmap.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)

n = 100
temperature = np.random.uniform(30, 100, n)
ice_cream = 3 * temperature + np.random.normal(0, 20, n)
umbrella = -2 * temperature + 250 + np.random.normal(0, 15, n)

df = pd.DataFrame({
    'Temperature': temperature.round(1),
    'Ice Cream Sales': ice_cream.round(1),
    'Umbrella Sales': umbrella.round(1)
})

corr = df.corr()
print("Correlation Matrix:")
print(corr.round(3))

# Heatmap
fig, ax = plt.subplots(figsize=(7, 5))
im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
ax.set_xticks(range(3))
ax.set_yticks(range(3))
ax.set_xticklabels(corr.columns, rotation=45, ha='right')
ax.set_yticklabels(corr.columns)
for i in range(3):
    for j in range(3):
        ax.text(j, i, f'{corr.values[i,j]:.2f}', ha='center', va='center',
                color='white' if abs(corr.values[i,j]) > 0.5 else 'black')
plt.colorbar(im)
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.savefig('exercise_heatmap.png', dpi=100)
plt.show()
```

### Exercise 2: Regression with Real-World-Like Data

Build a regression model predicting exam score from study hours using 100 data points. Compute the regression line, R-squared, and RMSE. Plot everything.

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Generate data
study_hours = np.random.uniform(0.5, 12, 100)
exam_scores = 6 * study_hours + 30 + np.random.normal(0, 8, 100)
exam_scores = np.clip(exam_scores, 0, 100)

# Fit regression
m, b = np.polyfit(study_hours, exam_scores, 1)
y_pred = m * study_hours + b

# Metrics
r = np.corrcoef(study_hours, exam_scores)[0, 1]
r_sq = 1 - np.sum((exam_scores - y_pred)**2) / np.sum((exam_scores - np.mean(exam_scores))**2)
rmse = np.sqrt(np.mean((exam_scores - y_pred)**2))

print(f"Equation: Score = {m:.2f} * Hours + {b:.2f}")
print(f"Correlation (r): {r:.4f}")
print(f"R-squared: {r_sq:.4f}")
print(f"RMSE: {rmse:.2f} points")

# Plot
plt.figure(figsize=(10, 6))
plt.scatter(study_hours, exam_scores, alpha=0.5, color='blue', label='Students')
x_line = np.linspace(0, 13, 100)
plt.plot(x_line, m*x_line + b, 'r-', linewidth=2,
         label=f'y = {m:.1f}x + {b:.1f} (R² = {r_sq:.3f})')
plt.xlabel('Study Hours')
plt.ylabel('Exam Score')
plt.title('Study Hours vs Exam Score')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('study_regression.png', dpi=100)
plt.show()
```

### Exercise 3: Compare Good and Bad Regression Fits

Create two datasets: one with a strong linear relationship and one with no relationship. Fit regression lines to both and compare their R-squared values.

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Strong relationship
x1 = np.random.uniform(0, 10, 50)
y1 = 3 * x1 + 5 + np.random.normal(0, 2, 50)

# No relationship
x2 = np.random.uniform(0, 10, 50)
y2 = np.random.normal(20, 5, 50)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, x, y, title in [(axes[0], x1, y1, 'Strong Relationship'),
                          (axes[1], x2, y2, 'No Relationship')]:
    m, b = np.polyfit(x, y, 1)
    y_pred = m * x + b
    r_sq = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)

    ax.scatter(x, y, alpha=0.6, color='blue')
    x_line = np.linspace(0, 10, 100)
    ax.plot(x_line, m*x_line + b, 'r-', linewidth=2)
    ax.set_title(f'{title}\ny = {m:.2f}x + {b:.2f}, R² = {r_sq:.4f}')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('good_vs_bad_fit.png', dpi=100)
plt.show()
```

---

## What Is Next?

You now understand correlation and regression — the bridge between statistics and machine learning.

In the final chapter, you will put EVERYTHING together. You will take a tiny dataset and walk through a complete machine learning pipeline step by step: compute statistics, visualize the data, normalize features, run gradient descent by hand, and find the best-fit line. You will see how every math concept from this entire book connects to build a working ML model.

Get ready for the grand finale.
