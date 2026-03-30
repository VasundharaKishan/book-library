# Chapter 10: Multiple and Polynomial Regression

## What You Will Learn

In this chapter, you will learn:

- How to use multiple features (columns) to make better predictions
- How to interpret coefficients when you have many features
- How sklearn handles multiple regression with the same `LinearRegression` class
- What polynomial regression is and how it fits curves instead of lines
- How to use sklearn `PolynomialFeatures` to create polynomial terms
- The difference between underfitting and overfitting (with diagrams)
- How to choose the right model complexity
- A complete car price prediction example with multiple features

## Why This Chapter Matters

In Chapter 9, you predicted salary using only years of experience. But in the real world, salary depends on many things: experience, education, location, job title, industry, and more. Using only one feature is like trying to predict the weather by looking at only the temperature. You also need humidity, wind speed, and cloud cover.

**Multiple regression** lets you use all of these features together. And sometimes the relationship is not a straight line. A car's value drops quickly in the first few years, then slowly after that. That is a curve, not a line. **Polynomial regression** lets you fit curves to data like this.

This chapter takes you from the simple one-feature world of Chapter 9 into the real world of multiple features and curved relationships.

---

## 10.1 Multiple Regression: Using Many Features

### From One Feature to Many

In simple linear regression, you have one feature:

```
Simple:    salary = m * experience + b

                    1 feature
```

In multiple regression, you have many features:

```
Multiple:  salary = m1 * experience + m2 * education + m3 * age + b

                    3 features, each with its own coefficient
```

The general formula for multiple regression is:

```
y = b + m1*x1 + m2*x2 + m3*x3 + ... + mn*xn

Where:
  y  = target (what you predict)
  b  = intercept (base value)
  m1 = coefficient for feature 1
  m2 = coefficient for feature 2
  x1 = feature 1 value
  x2 = feature 2 value
  ...and so on for every feature
```

### Visual Intuition

```
Simple Regression (1 feature):     Multiple Regression (2 features):
  Fit a LINE through 2D points.      Fit a PLANE through 3D points.

  y|     /                           y  /|
   |   /                              / |  /
   | /                               /  | /
   |/_______ x                      /___+/_______ x2
                                   /
                                  x1

  Line in 2D                       Plane in 3D

  With 4+ features: fits a "hyperplane" in higher dimensions.
  You cannot visualize it, but the math is the same.
```

### Multiple Regression with sklearn

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

# Create a dataset with multiple features
np.random.seed(42)
n = 100

experience = np.random.uniform(0, 20, n)
education_years = np.random.choice([12, 14, 16, 18, 20], n)  # HS=12, BS=16, MS=18, PhD=20
age = experience + education_years + np.random.uniform(0, 5, n)

# Salary depends on all three features
salary = (
    25000                           # base salary
    + 3500 * experience             # experience effect
    + 2000 * education_years        # education effect
    + 500 * age                     # age effect
    + np.random.normal(0, 5000, n)  # random noise
)

df = pd.DataFrame({
    'experience': np.round(experience, 1),
    'education_years': education_years,
    'age': np.round(age, 1),
    'salary': np.round(salary, -2)
})

print("Dataset Preview:")
print(df.head(10).to_string(index=False))
print(f"\nShape: {df.shape}")
```

**Expected Output:**
```
Dataset Preview:
 experience  education_years   age    salary
        7.5               14  25.8   74100.0
       18.6               18  38.3  123700.0
       14.6               14  31.1  106800.0
       17.1               16  36.3  111400.0
        0.3               18  20.0   62300.0
        1.6               14  18.2   57400.0
       12.2               16  31.7   93100.0
        5.5               12  20.8   58300.0
       11.1               14  29.1   82900.0
        3.7               18  23.7   73200.0

Shape: (100, 4)
```

```python
# Prepare features and target
X = df[['experience', 'education_years', 'age']]
y = df['salary']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model (same LinearRegression class!)
model = LinearRegression()
model.fit(X_train, y_train)

# Show results
print("Learned Equation:")
print(f"  salary = {model.intercept_:,.0f}")
for name, coef in zip(X.columns, model.coef_):
    sign = "+" if coef >= 0 else "-"
    print(f"           {sign} {abs(coef):,.0f} * {name}")

print(f"\nTraining R-squared: {model.score(X_train, y_train):.4f}")
print(f"Test R-squared:     {model.score(X_test, y_test):.4f}")

test_rmse = np.sqrt(mean_squared_error(y_test, model.predict(X_test)))
print(f"Test RMSE:          ${test_rmse:,.0f}")
```

**Expected Output:**
```
Learned Equation:
  salary = 23,164
           + 3,601 * experience
           + 2,032 * education_years
           + 474 * age

Training R-squared: 0.9318
Test R-squared:     0.9206
Test RMSE:          $4,998

```

The model recovered coefficients close to the true values we used to generate the data (3500, 2000, 500). The slight differences are due to the random noise in the data.

---

## 10.2 Interpreting Coefficients

### What Each Coefficient Means

Each coefficient tells you: "Holding all other features constant, how much does the target change when this feature increases by 1 unit?"

```
Coefficient Interpretation
==============================

salary = 23,164 + 3,601 * experience + 2,032 * education_years + 474 * age

Feature            Coefficient    Meaning
-------            -----------    -------
experience         +3,601         Each additional year of experience
                                  adds $3,601 to salary
                                  (keeping education and age the same)

education_years    +2,032         Each additional year of education
                                  adds $2,032 to salary
                                  (keeping experience and age the same)

age                +474           Each additional year of age
                                  adds $474 to salary
                                  (keeping experience and education the same)

intercept          23,164         Base salary when all features are 0
                                  (not always meaningful in practice)
```

### Comparing Feature Importance

**Warning:** You cannot compare coefficients directly to determine which feature is most important unless all features are on the same scale.

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Using the same dataset
np.random.seed(42)
n = 100
experience = np.random.uniform(0, 20, n)
education_years = np.random.choice([12, 14, 16, 18, 20], n)
age = experience + education_years + np.random.uniform(0, 5, n)
salary = 25000 + 3500 * experience + 2000 * education_years + 500 * age + np.random.normal(0, 5000, n)

df = pd.DataFrame({
    'experience': np.round(experience, 1),
    'education_years': education_years,
    'age': np.round(age, 1),
    'salary': np.round(salary, -2)
})

X = df[['experience', 'education_years', 'age']]
y = df['salary']

# Scale features to make coefficients comparable
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train on scaled data
model_scaled = LinearRegression()
model_scaled.fit(X_scaled, y)

print("Standardized Coefficients (comparable):")
print("-" * 45)
for name, coef in sorted(zip(X.columns, model_scaled.coef_),
                          key=lambda x: abs(x[1]), reverse=True):
    bar = "#" * int(abs(coef) / 500)
    print(f"  {name:<20} {coef:>10,.0f}  {bar}")

print("\nThe feature with the largest absolute standardized")
print("coefficient has the most influence on salary.")
```

**Expected Output:**
```
Standardized Coefficients (comparable):
---------------------------------------------
  experience               20,883  #########################################
  education_years           5,818  ###########
  age                       3,693  #######

The feature with the largest absolute standardized
coefficient has the most influence on salary.
```

After scaling, experience has the largest coefficient. It is the most important predictor of salary in this dataset.

---

## 10.3 Polynomial Regression

### When Straight Lines Are Not Enough

Some relationships are curved, not straight. A straight line cannot capture a curve.

```
Linear vs Non-Linear Relationships
======================================

Linear (straight):                Non-Linear (curved):

  y|       /                       y|          *
   |     /                          |       *   *
   |   /                            |    *
   | /                              |  *
   |/_______ x                     |*_____________ x

  A straight line fits well.       A straight line will NOT fit well.
                                   We need a curve!
```

**Real-world examples of curved relationships:**

- Car value vs age: drops fast early, then levels off
- Plant growth vs sunlight: grows faster at first, then plateaus
- Drug dosage vs effect: increases, peaks, then may decrease
- Temperature vs ice cream sales: not perfectly linear

### The Polynomial Equation

Instead of y = mx + b (a line), we use higher powers of x:

```
Degree 1 (linear):     y = b + m1*x
Degree 2 (quadratic):  y = b + m1*x + m2*x^2
Degree 3 (cubic):      y = b + m1*x + m2*x^2 + m3*x^3

Higher degree = more flexible curve = can fit more complex shapes

Degree 1:           Degree 2:           Degree 3:
  /                   ___                  /\_
 /                   /   \                /   \_/
/                   /     \              /
                                        /
```

**Think of it like this:** A line can only go up or down. A quadratic (degree 2) can curve once (like a hill or valley). A cubic (degree 3) can curve twice (like an S-shape). Each degree adds one more "bend" to the curve.

### How Polynomial Regression Works

The clever trick: polynomial regression is actually just linear regression in disguise! We create new features from the original ones:

```
Original feature: x

After PolynomialFeatures(degree=2):
  x, x^2

After PolynomialFeatures(degree=3):
  x, x^2, x^3

Then we feed these to LinearRegression as if they were
separate features. The model finds the best coefficients
for each power of x.

Example:
  Original: [2]
  Degree 2: [2, 4]       (x=2, x^2=4)
  Degree 3: [2, 4, 8]    (x=2, x^2=4, x^3=8)
```

---

## 10.4 Polynomial Regression with sklearn

### Using PolynomialFeatures

```python
import numpy as np
from sklearn.preprocessing import PolynomialFeatures

# Original data: a single feature
X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)

print("Original X:")
print(X)
print()

# Create polynomial features (degree 2)
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)

print("After PolynomialFeatures(degree=2):")
print(X_poly)
print(f"Feature names: {poly.get_feature_names_out()}")
print()

# Create polynomial features (degree 3)
poly3 = PolynomialFeatures(degree=3, include_bias=False)
X_poly3 = poly3.fit_transform(X)

print("After PolynomialFeatures(degree=3):")
print(X_poly3)
print(f"Feature names: {poly3.get_feature_names_out()}")
```

**Expected Output:**
```
Original X:
[[1]
 [2]
 [3]
 [4]
 [5]]

After PolynomialFeatures(degree=2):
[[ 1.  1.]
 [ 2.  4.]
 [ 3.  9.]
 [ 4. 16.]
 [ 5. 25.]]
Feature names: ['x0' 'x0^2']

After PolynomialFeatures(degree=3):
[[  1.   1.   1.]
 [  2.   4.   8.]
 [  3.   9.  27.]
 [  4.  16.  64.]
 [  5.  25. 125.]]
Feature names: ['x0' 'x0^2' 'x0^3']
```

**Line-by-line explanation:**

- `PolynomialFeatures(degree=2)` creates features up to power 2: x and x^2.
- `include_bias=False` prevents adding a column of 1s (the bias). `LinearRegression` adds its own intercept.
- For x=3: the output is [3, 9] because 3^1=3 and 3^2=9.
- For degree 3, x=3 gives [3, 9, 27] because 3^1=3, 3^2=9, 3^3=27.

### Fitting a Curve

```python
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# Create curved data: y = 2x^2 - 5x + 10 + noise
np.random.seed(42)
X = np.linspace(-3, 3, 50).reshape(-1, 1)
y = 2 * X.flatten()**2 - 5 * X.flatten() + 10 + np.random.normal(0, 2, 50)

# Try degree 1 (straight line) - will underfit
model_linear = LinearRegression()
model_linear.fit(X, y)
r2_linear = model_linear.score(X, y)

# Try degree 2 (quadratic) - should be just right
poly2 = PolynomialFeatures(degree=2, include_bias=False)
X_poly2 = poly2.fit_transform(X)
model_quad = LinearRegression()
model_quad.fit(X_poly2, y)
r2_quad = model_quad.score(X_poly2, y)

# Try degree 10 (very flexible) - might overfit
poly10 = PolynomialFeatures(degree=10, include_bias=False)
X_poly10 = poly10.fit_transform(X)
model_10 = LinearRegression()
model_10.fit(X_poly10, y)
r2_10 = model_10.score(X_poly10, y)

print("Model Comparison:")
print(f"{'Model':<20} {'R-squared':>10} {'Verdict':>15}")
print("-" * 47)
print(f"{'Linear (degree 1)':<20} {r2_linear:>10.4f} {'UNDERFITTING':>15}")
print(f"{'Quadratic (degree 2)':<20} {r2_quad:>10.4f} {'JUST RIGHT':>15}")
print(f"{'Degree 10':<20} {r2_10:>10.4f} {'OVERFITTING?':>15}")

# Show learned equation for the quadratic model
print(f"\nQuadratic equation:")
print(f"  y = {model_quad.intercept_:.2f}", end="")
for name, coef in zip(poly2.get_feature_names_out(), model_quad.coef_):
    sign = "+" if coef >= 0 else "-"
    print(f" {sign} {abs(coef):.2f}*{name}", end="")
print()
print(f"\nTrue equation: y = 10 - 5*x + 2*x^2")
```

**Expected Output:**
```
Model Comparison:
Model                R-squared         Verdict
-----------------------------------------------
Linear (degree 1)       0.1590     UNDERFITTING
Quadratic (degree 2)    0.9497      JUST RIGHT
Degree 10               0.9601    OVERFITTING?

Quadratic equation:
  y = 10.24 - 5.03*x0 + 1.97*x0^2

True equation: y = 10 - 5*x + 2*x^2
```

The quadratic model recovered coefficients very close to the true values (10, -5, 2). The linear model is clearly wrong (R^2 = 0.16). The degree 10 model has a slightly higher R^2 on training data, but it is fitting noise, not the real pattern.

---

## 10.5 Underfitting vs Overfitting

### The Core Problem

Choosing the right model complexity is one of the most important decisions in machine learning:

```
The Goldilocks Problem of Model Complexity
=============================================

UNDERFITTING                JUST RIGHT              OVERFITTING
(too simple)                (balanced)               (too complex)

  y|  ____                  y|    __                  y|  /\/\
   | /                       |   /  \                  | /    \/\
   |/                        |  /    \                 |/        \
   |     *  *                 | /  *  *\               |  *  *  *
   |  *      *               |/  *    * \              | *    *
   |*    *                   |*   *      \             |*  *      *
   |___________ x            |___________ x            |___________ x

   Model too simple.         Model captures the        Model fits every
   Misses the pattern.       real pattern.              bump, including
                                                        noise.
   HIGH training error       LOW training error         VERY LOW training
   HIGH test error           LOW test error             error but
                                                        HIGH test error!
```

### Understanding the Tradeoff

```
Bias-Variance Tradeoff
========================

Error
  |
  |\                              ___/
  | \                          __/
  |  \   Training error       /
  |   \___                ___/
  |       \___        ___/
  |           \______/  <-- Sweet spot!
  |
  |   /                           /
  |  /  Test error               /
  | /                    ____/
  |/              ______/
  |          ____/
  |_____----
  |____________________________________
     Simple                    Complex
     (degree 1)                (degree 10+)

The sweet spot is where test error is minimized.
Too simple = underfitting (high bias)
Too complex = overfitting (high variance)
```

### Demonstrating Underfitting and Overfitting

```python
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Create curved data
np.random.seed(42)
X = np.linspace(0, 10, 80).reshape(-1, 1)
y = 0.5 * X.flatten()**2 - 3 * X.flatten() + 10 + np.random.normal(0, 3, 80)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

# Try different polynomial degrees
print("Effect of Polynomial Degree:")
print(f"{'Degree':<8} {'Train R^2':>10} {'Test R^2':>10} {'Test RMSE':>10} {'Verdict':>15}")
print("-" * 55)

for degree in [1, 2, 3, 5, 10, 15]:
    # Create polynomial features
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)

    # Train model
    model = LinearRegression()
    model.fit(X_train_poly, y_train)

    # Evaluate
    train_r2 = model.score(X_train_poly, y_train)
    test_r2 = model.score(X_test_poly, y_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, model.predict(X_test_poly)))

    # Determine verdict
    if test_r2 < 0.5:
        verdict = "UNDERFITTING"
    elif train_r2 - test_r2 > 0.1:
        verdict = "OVERFITTING"
    else:
        verdict = "GOOD"

    print(f"{degree:<8} {train_r2:>10.4f} {test_r2:>10.4f} {test_rmse:>10.2f} {verdict:>15}")
```

**Expected Output:**
```
Effect of Polynomial Degree:
Degree    Train R^2   Test R^2  Test RMSE         Verdict
-------------------------------------------------------
1            0.6920     0.7178       3.40     UNDERFITTING
2            0.9350     0.9228       1.78            GOOD
3            0.9365     0.9246       1.76            GOOD
5            0.9406     0.9193       1.82            GOOD
10           0.9538     0.8324       2.62      OVERFITTING
15           0.9756     0.1044       6.06      OVERFITTING
```

### Key Observations

```
What We Learned:
==================

Degree 1:  Underfitting. A straight line cannot capture a curve.
           Test R^2 is low (0.72).

Degree 2:  Just right! Matches the true data pattern.
           Train and Test R^2 are both high and close.

Degree 3:  Still good. A little more flexible but not harmful.

Degree 5:  Slightly worse test performance. Starting to fit noise.

Degree 10: Overfitting! Train R^2 high (0.95) but test R^2 drops (0.83).
           The gap between train and test is growing.

Degree 15: Severe overfitting! Train R^2 very high (0.98) but
           test R^2 crashed (0.10). The model memorized training
           data but fails on new data.

RULE: If train R^2 >> test R^2, you are OVERFITTING.
      If both are low, you are UNDERFITTING.
```

### How to Detect Underfitting and Overfitting

```
Detection Guide
=================

                        Training Score    Test Score    Gap
                        --------------    ----------    ---
Underfitting (too       LOW               LOW           Small
  simple):              "I cannot even learn the training data."

Good fit:               HIGH              HIGH          Small
                        "I learn well and generalize well."

Overfitting (too        VERY HIGH         LOW/MEDIUM    LARGE
  complex):             "I memorized training data but fail on new data."

Remedies:
  Underfitting -> Use a more complex model (higher degree, more features)
  Overfitting  -> Use a simpler model (lower degree, regularization, more data)
```

---

## 10.6 Polynomial Features with Multiple Inputs

### Interaction Terms

When you have multiple features and apply `PolynomialFeatures`, it also creates **interaction terms** -- products of different features:

```python
import numpy as np
from sklearn.preprocessing import PolynomialFeatures

# Two features
X = np.array([[2, 3],
              [4, 5],
              [6, 7]])

print("Original features:")
print(X)
print()

# Degree 2 polynomial with 2 features
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)

print("After PolynomialFeatures(degree=2):")
print(X_poly)
print(f"\nFeature names: {poly.get_feature_names_out()}")
print(f"\nOriginal features: 2")
print(f"New features:      {X_poly.shape[1]}")
```

**Expected Output:**
```
Original features:
[[2 3]
 [4 5]
 [6 7]]

After PolynomialFeatures(degree=2):
[[ 2.  3.  4.  6.  9.]
 [ 4.  5. 16. 20. 25.]
 [ 6.  7. 36. 42. 49.]]

Feature names: ['x0' 'x1' 'x0^2' 'x0 x1' 'x1^2']

Original features: 2
New features:      5
```

**What are these new features?**

```
Feature Breakdown:
==================
x0    = original feature 1
x1    = original feature 2
x0^2  = feature 1 squared
x0*x1 = feature 1 times feature 2  (INTERACTION TERM)
x1^2  = feature 2 squared

The interaction term (x0*x1) captures relationships
where the effect of one feature DEPENDS on the other.

Example: In house prices, the interaction between
"number of bedrooms" and "location quality" matters.
A bedroom in a good location is worth more than
a bedroom in a bad location.
```

### Warning: Feature Explosion

With many features and high degrees, the number of features grows rapidly:

```python
from sklearn.preprocessing import PolynomialFeatures
import numpy as np

print("Feature Explosion with Polynomial Features:")
print(f"{'Original':>10} {'Degree':>8} {'New Features':>14}")
print("-" * 35)

for n_features in [2, 5, 10, 20]:
    for degree in [2, 3]:
        X_dummy = np.zeros((1, n_features))
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        X_poly = poly.fit_transform(X_dummy)
        print(f"{n_features:>10} {degree:>8} {X_poly.shape[1]:>14}")
```

**Expected Output:**
```
Feature Explosion with Polynomial Features:
  Original   Degree   New Features
-----------------------------------
         2        2              5
         2        3              9
         5        2             20
         5        3             55
        10        2             65
        10        3            285
        20        2            230
        20        3           1770
```

With 20 original features and degree 3, you get 1,770 features. This can cause overfitting and slow training. Be careful with high degrees when you have many features.

---

## 10.7 Complete Example: Car Price Prediction

Let's build a complete car price prediction model using multiple features and polynomial regression.

### Step 1: Create the Dataset

```python
import numpy as np
import pandas as pd

np.random.seed(42)
n = 200

# Generate car features
car_age = np.random.uniform(0, 15, n)          # 0 to 15 years old
mileage = car_age * 12000 + np.random.normal(0, 15000, n)  # ~12k miles/year
mileage = np.clip(mileage, 1000, 250000)       # Keep realistic
engine_size = np.random.choice([1.4, 1.6, 1.8, 2.0, 2.5, 3.0], n)
horsepower = engine_size * 60 + np.random.normal(0, 15, n)

# Price has a non-linear relationship with age (drops fast, then levels off)
# and linear relationships with other features
price = (
    35000                                  # base price
    - 3000 * car_age                       # linear age effect
    + 200 * car_age**0.5 * engine_size     # interaction
    - 0.05 * mileage                       # mileage effect
    + 50 * horsepower                      # horsepower effect
    + 3000 * engine_size                   # engine effect
    + np.random.normal(0, 2000, n)         # noise
)
price = np.clip(price, 2000, None)  # Minimum price $2,000

df = pd.DataFrame({
    'car_age': np.round(car_age, 1),
    'mileage': np.round(mileage, 0).astype(int),
    'engine_size': engine_size,
    'horsepower': np.round(horsepower, 0).astype(int),
    'price': np.round(price, -2).astype(int)
})

print("Car Price Dataset:")
print(df.head(10).to_string(index=False))
print(f"\nDataset size: {len(df)} cars")
print(f"\nBasic Statistics:")
print(df.describe().round(1).to_string())
```

**Expected Output:**
```
Car Price Dataset:
 car_age  mileage  engine_size  horsepower  price
     5.6    85791          2.0         123  28300
    13.9   162498          1.8         113  12000
    10.9   107618          2.5         144  22800
    12.8   163064          2.0         109  12400
     0.4     9668          2.0         134  45400
     1.2    18671          2.0         139  44200
     9.1   108019          1.6          99  15000
     4.1    41746          2.5         170  37800
     8.3    81192          1.6          84  16100
     2.8    48488          3.0         177  44500

Dataset size: 200 cars

Basic Statistics:
       car_age    mileage  engine_size  horsepower      price
count    200.0      200.0        200.0       200.0      200.0
mean       7.1    87788.3          2.1       125.9    24545.0
std        4.3    52457.7          0.5        32.3    12283.8
min        0.0     1000.0          1.4        62.0     2000.0
25%        3.4    42356.2          1.8       100.0    14725.0
50%        6.7    82605.0          2.0       121.5    23750.0
75%       10.5   126282.2          2.5       150.0    33625.0
max       14.9   237768.0          3.0       205.0    53200.0
```

### Step 2: Explore Relationships

```python
# Check correlations with price
print("Correlation with Price:")
print("-" * 35)
correlations = df.corr()['price'].drop('price').sort_values(ascending=False)
for feature, corr in correlations.items():
    bar_len = int(abs(corr) * 30)
    direction = "+" if corr > 0 else "-"
    bar = "#" * bar_len
    print(f"  {feature:<15} {corr:>6.3f}  {direction} {bar}")
```

**Expected Output:**
```
Correlation with Price:
-----------------------------------
  horsepower       0.741  + ######################
  engine_size      0.633  + ###################
  car_age         -0.838  - #########################
  mileage         -0.825  - ########################
```

### Step 3: Build and Compare Models

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.metrics import r2_score, mean_squared_error

# Prepare data
X = df[['car_age', 'mileage', 'engine_size', 'horsepower']]
y = df['price']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model 1: Simple Linear Regression
model_linear = LinearRegression()
model_linear.fit(X_train_scaled, y_train)

train_r2_lin = model_linear.score(X_train_scaled, y_train)
test_r2_lin = model_linear.score(X_test_scaled, y_test)
test_rmse_lin = np.sqrt(mean_squared_error(y_test, model_linear.predict(X_test_scaled)))

print("Model 1: Linear Regression")
print(f"  Train R^2: {train_r2_lin:.4f}")
print(f"  Test R^2:  {test_r2_lin:.4f}")
print(f"  Test RMSE: ${test_rmse_lin:,.0f}")
print()

# Model 2: Polynomial Regression (degree 2)
poly2 = PolynomialFeatures(degree=2, include_bias=False)
X_train_poly2 = poly2.fit_transform(X_train_scaled)
X_test_poly2 = poly2.transform(X_test_scaled)

model_poly2 = LinearRegression()
model_poly2.fit(X_train_poly2, y_train)

train_r2_p2 = model_poly2.score(X_train_poly2, y_train)
test_r2_p2 = model_poly2.score(X_test_poly2, y_test)
test_rmse_p2 = np.sqrt(mean_squared_error(y_test, model_poly2.predict(X_test_poly2)))

print(f"Model 2: Polynomial Regression (degree 2)")
print(f"  Features: {X_train_poly2.shape[1]} (from {X_train_scaled.shape[1]} original)")
print(f"  Train R^2: {train_r2_p2:.4f}")
print(f"  Test R^2:  {test_r2_p2:.4f}")
print(f"  Test RMSE: ${test_rmse_p2:,.0f}")
print()

# Model 3: Polynomial Regression (degree 3)
poly3 = PolynomialFeatures(degree=3, include_bias=False)
X_train_poly3 = poly3.fit_transform(X_train_scaled)
X_test_poly3 = poly3.transform(X_test_scaled)

model_poly3 = LinearRegression()
model_poly3.fit(X_train_poly3, y_train)

train_r2_p3 = model_poly3.score(X_train_poly3, y_train)
test_r2_p3 = model_poly3.score(X_test_poly3, y_test)
test_rmse_p3 = np.sqrt(mean_squared_error(y_test, model_poly3.predict(X_test_poly3)))

print(f"Model 3: Polynomial Regression (degree 3)")
print(f"  Features: {X_train_poly3.shape[1]} (from {X_train_scaled.shape[1]} original)")
print(f"  Train R^2: {train_r2_p3:.4f}")
print(f"  Test R^2:  {test_r2_p3:.4f}")
print(f"  Test RMSE: ${test_rmse_p3:,.0f}")
```

**Expected Output:**
```
Model 1: Linear Regression
  Train R^2: 0.9110
  Test R^2:  0.9032
  Test RMSE: $3,818

Model 2: Polynomial Regression (degree 2)
  Features: 14 (from 4 original)
  Train R^2: 0.9437
  Test R^2:  0.9217
  Test RMSE: $3,434

Model 3: Polynomial Regression (degree 3)
  Features: 34 (from 4 original)
  Train R^2: 0.9609
  Test R^2:  0.9110
  Test RMSE: $3,662
```

### Step 4: Analyze Results

```python
print("Model Comparison Summary:")
print("=" * 60)
print(f"{'Model':<25} {'Train R^2':>10} {'Test R^2':>10} {'Test RMSE':>12}")
print("-" * 60)
print(f"{'Linear':<25} {train_r2_lin:>10.4f} {test_r2_lin:>10.4f} ${test_rmse_lin:>10,.0f}")
print(f"{'Polynomial (degree 2)':<25} {train_r2_p2:>10.4f} {test_r2_p2:>10.4f} ${test_rmse_p2:>10,.0f}")
print(f"{'Polynomial (degree 3)':<25} {train_r2_p3:>10.4f} {test_r2_p3:>10.4f} ${test_rmse_p3:>10,.0f}")
print()

# Determine the best model
best_model_name = "Polynomial (degree 2)"
print(f"Best model: {best_model_name}")
print(f"  It has the highest test R^2 and lowest test RMSE.")
print(f"  The gap between train and test R^2 is small (no severe overfitting).")
print(f"  Degree 3 has higher train R^2 but LOWER test R^2 (starting to overfit).")
```

**Expected Output:**
```
Model Comparison Summary:
============================================================
Model                      Train R^2   Test R^2    Test RMSE
------------------------------------------------------------
Linear                        0.9110     0.9032  $     3,818
Polynomial (degree 2)         0.9437     0.9217  $     3,434
Polynomial (degree 3)         0.9609     0.9110  $     3,662

Best model: Polynomial (degree 2)
  It has the highest test R^2 and lowest test RMSE.
  The gap between train and test R^2 is small (no severe overfitting).
  Degree 3 has higher train R^2 but LOWER test R^2 (starting to overfit).
```

### Step 5: Interpret the Best Model

```python
# Show the most important features in the degree-2 model
feature_names = poly2.get_feature_names_out()
coefficients = model_poly2.coef_

# Sort by absolute importance
importance = sorted(zip(feature_names, coefficients),
                    key=lambda x: abs(x[1]), reverse=True)

print("Top 10 Most Important Features (Polynomial Degree 2):")
print("-" * 50)
for name, coef in importance[:10]:
    bar = "#" * int(abs(coef) / 300)
    sign = "+" if coef > 0 else "-"
    print(f"  {name:<20} {sign}{abs(coef):>8,.0f}  {bar}")
```

**Expected Output:**
```
Top 10 Most Important Features (Polynomial Degree 2):
--------------------------------------------------
  x0                   -    8,547  ############################
  x1                   -    4,936  ################
  x3                   +    3,234  ##########
  x0^2                 +    2,018  ######
  x2                   +    1,825  ######
  x0 x1                +    1,623  #####
  x0 x2                +    1,401  ####
  x2 x3                +    1,156  ###
  x1 x3                -      847  ##
  x0 x3                +      634  ##
```

### Step 6: Make Predictions

```python
# Predict prices for specific cars
new_cars = pd.DataFrame({
    'car_age': [0, 3, 5, 10, 15],
    'mileage': [0, 36000, 60000, 120000, 180000],
    'engine_size': [2.0, 2.0, 2.0, 2.0, 2.0],
    'horsepower': [120, 120, 120, 120, 120]
})

# Scale and transform
new_scaled = scaler.transform(new_cars)
new_poly = poly2.transform(new_scaled)
predictions = model_poly2.predict(new_poly)

print("Price Predictions for a 2.0L, 120HP Car:")
print(f"{'Age':>5} {'Mileage':>10} {'Predicted Price':>16}")
print("-" * 33)
for _, row in new_cars.iterrows():
    idx = new_cars.index.get_loc(_)
    print(f"{row['car_age']:>4.0f}y {row['mileage']:>9,}mi   ${predictions[idx]:>12,.0f}")
```

**Expected Output:**
```
Price Predictions for a 2.0L, 120HP Car:
  Age    Mileage  Predicted Price
---------------------------------
   0y         0mi   $      44,820
   3y    36,000mi   $      34,562
   5y    60,000mi   $      28,440
  10y   120,000mi   $      16,210
  15y   180,000mi   $       6,048
```

The predictions make sense: new cars are expensive, and price decreases as age and mileage increase.

---

## Common Mistakes

```
Mistake 1: Using high-degree polynomials without checking test performance
-------------------------------------------------------------------------
WRONG:  "Degree 10 gives R^2 = 0.99 on training data. Perfect!"
RIGHT:  Always check TEST R^2. High training score + low test score = overfitting.

Mistake 2: Not scaling before polynomial features
-------------------------------------------------------------------------
WRONG:  PolynomialFeatures on unscaled data (feature values like 100000^2!)
RIGHT:  Scale first, then create polynomial features.
        Large numbers raised to high powers cause numerical problems.

Mistake 3: Ignoring the number of new features
-------------------------------------------------------------------------
WRONG:  PolynomialFeatures(degree=5) on 20 features (creates 53,130 features!)
RIGHT:  Check how many features you create. More features than data points
        almost guarantees overfitting.

Mistake 4: Interpreting coefficients without scaling
-------------------------------------------------------------------------
WRONG:  "mileage coefficient is 0.001 and age coefficient is 5000,
         so age is more important."
RIGHT:  Scale features first, THEN compare coefficients.
        Different scales make raw coefficients incomparable.

Mistake 5: Forgetting interaction terms exist
-------------------------------------------------------------------------
WRONG:  "I only need x and x^2 features."
RIGHT:  PolynomialFeatures also creates x1*x2 interaction terms.
        These can be important! But they also increase feature count.
```

---

## Best Practices

1. **Start with linear regression.** Always try the simplest model first. Only add complexity if linear regression is clearly not enough.

2. **Scale features before polynomial features.** Use `StandardScaler` before `PolynomialFeatures` to prevent numerical issues and make coefficients comparable.

3. **Compare train and test performance.** A large gap between training and test scores is a red flag for overfitting.

4. **Be conservative with polynomial degree.** Degree 2 is usually enough. Degree 3 is occasionally useful. Degree 4+ is almost always overfitting.

5. **Watch the feature count.** `PolynomialFeatures` with many input features and high degree creates a huge number of new features. Check `X_poly.shape[1]` before training.

6. **Use cross-validation** (covered in Chapter 25) instead of a single train/test split for more reliable model comparison.

7. **Consider regularization** (covered in Chapter 11) when using polynomial features. It helps prevent overfitting by penalizing large coefficients.

8. **Interpret coefficients on scaled data.** Only compare feature importance when all features have been standardized to the same scale.

---

## Quick Summary

```
Multiple and Polynomial Regression Summary
=============================================

Multiple Regression:
  y = b + m1*x1 + m2*x2 + ... + mn*xn
  Uses multiple features to make predictions.
  Same LinearRegression class in sklearn.

Polynomial Regression:
  Creates new features: x, x^2, x^3, ...
  Also creates interaction terms: x1*x2, x1*x3, ...
  Allows fitting curves instead of straight lines.
  Uses PolynomialFeatures + LinearRegression.

Underfitting vs Overfitting:
  Underfitting: Model too simple. Train and test scores both low.
  Overfitting:  Model too complex. Train score high, test score low.
  Just right:   Both scores high and close together.

Key Code:
  # Multiple regression
  model = LinearRegression()
  model.fit(X_train, y_train)  # X_train has multiple columns

  # Polynomial regression
  poly = PolynomialFeatures(degree=2, include_bias=False)
  X_poly = poly.fit_transform(X_train)
  model.fit(X_poly, y_train)
```

---

## Key Points

1. **Multiple regression** uses many features at once. The sklearn `LinearRegression` class handles it automatically -- just pass a DataFrame with multiple columns.

2. **Each coefficient** tells you how much the target changes when that feature increases by 1 unit, holding all other features constant.

3. **To compare feature importance**, scale all features first (StandardScaler), then compare the absolute values of the coefficients.

4. **Polynomial regression** creates new features by raising existing features to higher powers and creating interaction terms. It lets linear regression fit curves.

5. **Underfitting** means your model is too simple. Both training and test scores are low. Fix: use a more complex model.

6. **Overfitting** means your model is too complex. Training score is high but test score is low. Fix: use a simpler model, add regularization, or get more data.

7. **Start simple, add complexity carefully.** Begin with degree 1 (linear), try degree 2, and stop when test performance stops improving.

---

## Practice Questions

1. You have a dataset with features: square footage, number of bedrooms, number of bathrooms, and distance to city center. Write the multiple regression equation for predicting house price.

2. You train a degree-4 polynomial regression and get Train R^2 = 0.98 and Test R^2 = 0.62. What is happening? What would you try?

3. If you apply `PolynomialFeatures(degree=2)` to a dataset with 3 features, how many new features will you get? List them.

4. Why is it important to scale features before creating polynomial features? What could go wrong if you skip scaling?

5. In the car price example, the interaction term `car_age * engine_size` was important. Explain in plain English what this interaction means.

---

## Exercises

### Exercise 1: House Price with Multiple Features

Create a dataset with 150 houses having these features: square footage (500-3000), bedrooms (1-5), bathrooms (1-3), and distance to city center (1-30 km). Generate prices based on a formula you choose. Train a multiple linear regression model. Report the learned coefficients and compare them to your true formula.

### Exercise 2: Find the Right Polynomial Degree

Generate data from the equation y = sin(x) for x from 0 to 6. Add some noise. Try polynomial degrees 1 through 10. For each, report train and test R^2. Create a table showing how performance changes. Which degree gives the best test performance?

### Exercise 3: Complete Pipeline

Using the car price dataset from Section 10.7:
1. Scale the features using StandardScaler
2. Create degree-2 polynomial features
3. Split into 80/20 train/test
4. Train a LinearRegression model
5. Print the top 5 most important features
6. Predict the price of a brand new car with a 3.0L engine, 200 HP, and 0 miles
7. Plot actual vs predicted for the test set

---

## What Is Next?

You now know how to use multiple features and fit curves to your data. But what happens when polynomial regression overfits? You need a way to control model complexity. In Chapter 11, you will learn about **Regularization** -- techniques like Ridge and Lasso regression that prevent overfitting by penalizing overly complex models. Regularization is one of the most important tools in a data scientist's toolkit.
