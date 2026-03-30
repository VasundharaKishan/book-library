# Chapter 11: Regularization — Teaching Your Model Self-Control

## What You Will Learn

In this chapter, you will learn:

- What overfitting is and why it is a problem
- How regularization prevents overfitting
- What Ridge Regression (L2) does and how it works
- What Lasso Regression (L1) does and how it works
- What Elastic Net is and when to use it
- How to choose the right amount of regularization (the alpha parameter)
- How to use Ridge, Lasso, and Elastic Net in scikit-learn
- How to compare regularized models against plain Linear Regression

## Why This Chapter Matters

Imagine a student who memorizes every single answer for an exam. They score 100% on the practice test. But when the real exam has slightly different questions, they fail badly. They memorized the answers instead of understanding the subject.

Machine learning models can do the exact same thing. They can memorize the training data perfectly but fail on new data. This problem is called **overfitting**. It is one of the most common and most dangerous problems in machine learning.

Regularization is the cure. It forces your model to keep things simple. Simple models generalize better. They work well on data they have never seen before.

Every professional data scientist uses regularization. After this chapter, you will too.

---

## 11.1 What Is Overfitting?

### The Memorization Problem

**Overfitting** means your model has learned the training data too well. It has memorized every detail, including the noise and random fluctuations. The model fits the training data perfectly but performs poorly on new, unseen data.

Think of it this way:

```
Memorizing (Overfitting)          Understanding (Good Fit)
========================          ========================

Student memorizes:                Student understands:
"Q1 answer is B"                  "Photosynthesis converts
"Q2 answer is D"                   sunlight into energy"
"Q3 answer is A"

Practice test: 100%               Practice test: 85%
Real exam:     40%                Real exam:     82%
```

The student who memorizes gets a perfect score on practice but fails the real exam. The student who understands gets a slightly lower practice score but does well on both.

### Overfitting in Machine Learning

Here is what overfitting looks like with data:

```
    Underfitting              Good Fit               Overfitting
    (Too Simple)              (Just Right)           (Too Complex)

    |    x                    |    x                  |    x
    |  x   x                 |  x   x                |  x / x
    | x      x               | x  /   x              | x/    \x
    |x        x              |x  /     x              |/  /\   \
    |          x              | /       x              |  /  \   \
    +------------>            +------------>           +------------>

    Misses the pattern        Captures the pattern    Captures noise too
    High training error       Low training error       Very low training error
    High test error           Low test error           HIGH test error
```

The underfitting model is too simple. It misses the pattern entirely.

The good fit model captures the real pattern in the data.

The overfitting model tries to pass through every single point. It captures the noise too. It will fail on new data.

### How to Spot Overfitting

The classic sign of overfitting:

```
Training score:  0.99  (nearly perfect)
Test score:      0.65  (much worse)
                  ^
                  |
           Big gap = Overfitting!
```

When there is a large gap between training performance and test performance, your model is overfitting.

Let us see this in code:

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split

# Create simple data with some noise
np.random.seed(42)
X = np.linspace(0, 10, 30).reshape(-1, 1)
y = 2 * X.ravel() + 1 + np.random.randn(30) * 2

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Model 1: Simple linear regression (good fit)
model_simple = LinearRegression()
model_simple.fit(X_train, y_train)
print("Simple Model (degree 1):")
print(f"  Training R2: {model_simple.score(X_train, y_train):.4f}")
print(f"  Test R2:     {model_simple.score(X_test, y_test):.4f}")

# Model 2: Very complex polynomial (overfitting)
poly = PolynomialFeatures(degree=15)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

model_complex = LinearRegression()
model_complex.fit(X_train_poly, y_train)
print("\nComplex Model (degree 15):")
print(f"  Training R2: {model_complex.score(X_train_poly, y_train):.4f}")
print(f"  Test R2:     {model_complex.score(X_test_poly, y_test):.4f}")
```

**Expected Output:**

```
Simple Model (degree 1):
  Training R2: 0.9281
  Test R2:     0.9450

Complex Model (degree 15):
  Training R2: 0.9994
  Test R2:     -2.8137
```

**Line-by-line explanation:**

- `np.random.seed(42)` — makes results reproducible every time you run the code
- `X = np.linspace(0, 10, 30).reshape(-1, 1)` — creates 30 evenly spaced points from 0 to 10
- `y = 2 * X.ravel() + 1 + np.random.randn(30) * 2` — creates target values with a simple linear pattern plus some random noise
- `PolynomialFeatures(degree=15)` — creates polynomial features up to degree 15, making the model very complex
- The simple model has similar training and test scores (good!)
- The complex model has a near-perfect training score (0.9994) but a negative test score (-2.8137). A negative R2 means the model is worse than just predicting the average. This is severe overfitting.

---

## 11.2 How Regularization Helps

### The Core Idea

Regularization adds a **penalty** to the model for being too complex. It is like telling the model: "You can learn the pattern, but keep it simple. Do not go overboard."

Think of it like a budget constraint:

```
Without Regularization:            With Regularization:
=====================              ====================

"Learn the data perfectly!          "Learn the data well,
 Use any coefficients               but keep your coefficients
 you want, no limits!"              small. Big coefficients
                                     cost you points!"

Result: Huge coefficients           Result: Small, controlled
         Wild predictions                    coefficients
         Overfitting                         Better generalization
```

### What Does "Penalize Complexity" Mean?

In linear regression, the model learns coefficients (weights) for each feature:

```
prediction = w1*feature1 + w2*feature2 + w3*feature3 + ... + bias
```

When a model overfits, these coefficients become very large. Regularization adds a penalty based on the size of these coefficients.

```
Without regularization:
  Goal: Minimize prediction errors only

With regularization:
  Goal: Minimize prediction errors + penalty for large coefficients

  Total Cost = Prediction Errors + alpha * Size of Coefficients
                                    ^^^^^
                                    This controls how much
                                    we penalize complexity
```

The **alpha** parameter controls how much we penalize. More on this later.

### The Seesaw Analogy

Think of regularization like balancing a seesaw:

```
                    alpha (regularization strength)
                           |
                           v
    Fitting data    ===============    Keeping it simple
    well                  /\
                         /  \
                     ====/====\====
                    /              \

    alpha too low:               alpha too high:
    Model fits too closely       Model is too simple
    (overfitting)                (underfitting)

    alpha just right:
    Good balance between
    fitting data and simplicity
```

---

## 11.3 Ridge Regression (L2 Regularization)

### What Ridge Does

**Ridge Regression** is Linear Regression with a penalty on the sum of squared coefficients. The technical name is **L2 regularization**.

```
Ridge cost = Prediction errors + alpha * (w1^2 + w2^2 + w3^2 + ...)
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                          Sum of squared coefficients
                                          (L2 penalty)
```

Ridge **shrinks** all coefficients toward zero. But it never makes them exactly zero. Every feature stays in the model, just with a smaller influence.

### The Weight Analogy

Imagine a seesaw with weights on it. Some weights are very heavy (large coefficients) and make the seesaw tip wildly.

```
Before Ridge (unregularized):

    Heavy weights = Large coefficients = Wild predictions

         [50kg]  [0.1kg]  [80kg]  [0.2kg]  [60kg]
          w1       w2       w3       w4       w5
    ================================================
                         /\
                      (tips wildly)

After Ridge (regularized):

    Weights are compressed = Smaller coefficients = Smoother predictions

         [8kg]   [0.1kg]   [10kg]  [0.1kg]   [7kg]
          w1       w2        w3       w4        w5
    ================================================
                         /\
                     (balanced!)
```

Ridge pulls all the large weights toward smaller values. It does not remove any weight entirely. It just makes them all more moderate.

### Ridge in scikit-learn

```python
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split

# Create data
np.random.seed(42)
X = np.linspace(0, 10, 30).reshape(-1, 1)
y = 2 * X.ravel() + 1 + np.random.randn(30) * 2

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Create polynomial features (degree 15 — normally overfits!)
poly = PolynomialFeatures(degree=15)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

# Plain Linear Regression (will overfit)
lr = LinearRegression()
lr.fit(X_train_poly, y_train)
print("Linear Regression (no regularization):")
print(f"  Training R2: {lr.score(X_train_poly, y_train):.4f}")
print(f"  Test R2:     {lr.score(X_test_poly, y_test):.4f}")

# Ridge Regression (with regularization)
ridge = Ridge(alpha=1.0)
ridge.fit(X_train_poly, y_train)
print("\nRidge Regression (alpha=1.0):")
print(f"  Training R2: {ridge.score(X_train_poly, y_train):.4f}")
print(f"  Test R2:     {ridge.score(X_test_poly, y_test):.4f}")
```

**Expected Output:**

```
Linear Regression (no regularization):
  Training R2: 0.9994
  Test R2:     -2.8137

Ridge Regression (alpha=1.0):
  Training R2: 0.9543
  Test R2:     0.9187
```

**Line-by-line explanation:**

- `Ridge(alpha=1.0)` — creates a Ridge model with regularization strength of 1.0. Higher alpha means more regularization (more penalty for large coefficients).
- The plain Linear Regression overfits badly (test R2 is -2.81).
- Ridge gives up a tiny bit of training accuracy (0.95 vs 0.99) but the test score jumps from -2.81 to 0.92. That is a massive improvement!

### Comparing Coefficients

Let us look at what Ridge does to the coefficients:

```python
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split

# Create data
np.random.seed(42)
X = np.linspace(0, 10, 30).reshape(-1, 1)
y = 2 * X.ravel() + 1 + np.random.randn(30) * 2

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

poly = PolynomialFeatures(degree=10)
X_train_poly = poly.fit_transform(X_train)

# Compare coefficients
lr = LinearRegression().fit(X_train_poly, y_train)
ridge = Ridge(alpha=10.0).fit(X_train_poly, y_train)

print("Feature        LinearReg Coef    Ridge Coef")
print("-" * 50)
for i in range(min(6, len(lr.coef_))):
    print(f"  x^{i:<12} {lr.coef_[i]:>12.4f}    {ridge.coef_[i]:>12.4f}")
```

**Expected Output:**

```
Feature        LinearReg Coef    Ridge Coef
--------------------------------------------------
  x^0            -0.0000          -0.0000
  x^1            20.3512           1.8741
  x^2           -25.8394           0.1023
  x^3            16.3907          -0.0412
  x^4            -5.9128           0.0053
  x^5             1.3551          -0.0003
```

Look at the difference! Linear Regression has huge coefficients (20.35, -25.84, 16.39). Ridge shrinks them dramatically (1.87, 0.10, -0.04). Smaller coefficients mean smoother, more stable predictions.

---

## 11.4 Lasso Regression (L1 Regularization)

### What Lasso Does

**Lasso** stands for "Least Absolute Shrinkage and Selection Operator." It uses a penalty on the sum of absolute values of coefficients. The technical name is **L1 regularization**.

```
Lasso cost = Prediction errors + alpha * (|w1| + |w2| + |w3| + ...)
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^
                                          Sum of absolute coefficients
                                          (L1 penalty)
```

The key difference from Ridge: Lasso can make coefficients exactly zero. When a coefficient becomes zero, that feature is completely removed from the model. This means Lasso performs **automatic feature selection**.

### Ridge vs Lasso — The Key Difference

```
Ridge (L2):                          Lasso (L1):
=========                            =========

Shrinks ALL coefficients             Can ZERO OUT coefficients
toward zero, but never               completely!
exactly zero.
                                     Some features are removed
All features stay in                 from the model entirely.
the model.

Before: [50, 0.1, 80, 0.2, 60]     Before: [50, 0.1, 80, 0.2, 60]
After:  [ 8, 0.05, 10, 0.1,  7]    After:  [12,  0,  15,  0,   9]
                                             ^^^  ^^      ^^
                                             kept zero    zero

Good when all features               Good when only some features
matter somewhat.                     actually matter.
```

### Lasso as Feature Selection

Think of Lasso like a talent show judge:

```
Lasso as a Talent Judge:

  Feature 1 (height):    "You are important. Stay." --> coef = 2.5
  Feature 2 (shoe size): "Irrelevant. You are out!" --> coef = 0.0
  Feature 3 (age):       "You matter. Stay."       --> coef = 1.8
  Feature 4 (hair color):"Not useful. You are out!" --> coef = 0.0
  Feature 5 (income):    "Very important. Stay."    --> coef = 3.1

  Lasso kept 3 features, removed 2.
  This is automatic feature selection!
```

### Lasso in scikit-learn

```python
import numpy as np
from sklearn.linear_model import Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split

# Create data
np.random.seed(42)
X = np.linspace(0, 10, 30).reshape(-1, 1)
y = 2 * X.ravel() + 1 + np.random.randn(30) * 2

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Polynomial features
poly = PolynomialFeatures(degree=15)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

# Lasso Regression
lasso = Lasso(alpha=0.1)
lasso.fit(X_train_poly, y_train)
print("Lasso Regression (alpha=0.1):")
print(f"  Training R2: {lasso.score(X_train_poly, y_train):.4f}")
print(f"  Test R2:     {lasso.score(X_test_poly, y_test):.4f}")

# Count non-zero coefficients
non_zero = np.sum(lasso.coef_ != 0)
total = len(lasso.coef_)
print(f"\n  Non-zero coefficients: {non_zero} out of {total}")
print(f"  Lasso removed {total - non_zero} features!")

# Show which coefficients are non-zero
print("\n  Coefficients:")
for i, coef in enumerate(lasso.coef_):
    status = "KEPT" if coef != 0 else "removed"
    print(f"    x^{i}: {coef:>10.4f}  ({status})")
```

**Expected Output:**

```
Lasso Regression (alpha=0.1):
  Training R2: 0.9329
  Test R2:     0.9405

  Non-zero coefficients: 2 out of 16
  Lasso removed 14 features!

  Coefficients:
    x^0:     0.0000  (removed)
    x^1:     1.8962  (KEPT)
    x^2:     0.0000  (removed)
    x^3:     0.0000  (removed)
    x^4:     0.0000  (removed)
    x^5:     0.0000  (removed)
    x^6:     0.0000  (removed)
    x^7:     0.0000  (removed)
    x^8:     0.0000  (removed)
    x^9:     0.0000  (removed)
    x^10:    0.0000  (removed)
    x^11:    0.0000  (removed)
    x^12:    0.0000  (removed)
    x^13:    0.0000  (removed)
    x^14:    0.0000  (removed)
    x^15:    0.0012  (KEPT)
```

**Line-by-line explanation:**

- `Lasso(alpha=0.1)` — creates a Lasso model. Alpha controls regularization strength.
- `np.sum(lasso.coef_ != 0)` — counts how many coefficients are not zero. These are the features Lasso kept.
- Out of 16 polynomial features, Lasso kept only 2! It figured out that most features are just noise and removed them.
- The test R2 (0.94) is excellent. Lasso gave us a simpler model that works just as well.

---

## 11.5 Elastic Net — The Best of Both Worlds

### What Elastic Net Does

**Elastic Net** combines Ridge and Lasso. It uses both L1 and L2 penalties together.

```
Elastic Net cost = Prediction errors
                   + alpha * l1_ratio * (|w1| + |w2| + ...)     # Lasso part
                   + alpha * (1 - l1_ratio) * (w1^2 + w2^2 + ...)  # Ridge part
```

The `l1_ratio` parameter controls the mix:

```
l1_ratio = 0.0  -->  Pure Ridge (only L2)
l1_ratio = 0.5  -->  Half Ridge, half Lasso
l1_ratio = 1.0  -->  Pure Lasso (only L1)

  Ridge <-------|----------|----------|-------> Lasso
       0.0     0.25      0.50      0.75      1.0
                      l1_ratio
```

### When to Use Elastic Net

```
Use Ridge when:
  - You think all features are somewhat useful
  - You want to shrink coefficients but keep all features

Use Lasso when:
  - You think only a few features matter
  - You want automatic feature selection
  - You have many features and want a simpler model

Use Elastic Net when:
  - You are not sure which is better
  - You have many correlated features
  - Lasso is being too aggressive (removing too many features)
  - You want some feature selection but also some shrinkage
```

### Elastic Net in scikit-learn

```python
import numpy as np
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split

# Create data
np.random.seed(42)
X = np.linspace(0, 10, 30).reshape(-1, 1)
y = 2 * X.ravel() + 1 + np.random.randn(30) * 2

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

poly = PolynomialFeatures(degree=15)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

# Elastic Net
elastic = ElasticNet(alpha=0.1, l1_ratio=0.5)
elastic.fit(X_train_poly, y_train)
print("Elastic Net (alpha=0.1, l1_ratio=0.5):")
print(f"  Training R2: {elastic.score(X_train_poly, y_train):.4f}")
print(f"  Test R2:     {elastic.score(X_test_poly, y_test):.4f}")

non_zero = np.sum(elastic.coef_ != 0)
total = len(elastic.coef_)
print(f"  Non-zero coefficients: {non_zero} out of {total}")
```

**Expected Output:**

```
Elastic Net (alpha=0.1, l1_ratio=0.5):
  Training R2: 0.9316
  Test R2:     0.9404
  Non-zero coefficients: 3 out of 16
```

**Line-by-line explanation:**

- `ElasticNet(alpha=0.1, l1_ratio=0.5)` — creates an Elastic Net model. `alpha=0.1` sets the overall regularization strength. `l1_ratio=0.5` means half Lasso penalty, half Ridge penalty.
- The result is between Ridge and Lasso: it removes some features (like Lasso) but is less aggressive about it.

---

## 11.6 The Alpha Parameter — Finding the Sweet Spot

### What Alpha Does

The **alpha** parameter controls how much regularization to apply. It is like a dial:

```
    alpha = 0                                    alpha = very large
    |                                            |
    v                                            v
    No penalty                                   Maximum penalty
    (same as plain                               (all coefficients
     Linear Regression)                           shrink to ~zero)

         Overfitting <---------|---------> Underfitting
                          Sweet spot
                        (best alpha)
```

### Effect of Different Alpha Values

```python
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split

# Create data
np.random.seed(42)
X = np.linspace(0, 10, 30).reshape(-1, 1)
y = 2 * X.ravel() + 1 + np.random.randn(30) * 2

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

poly = PolynomialFeatures(degree=15)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

# Try different alpha values
alphas = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]

print(f"{'Alpha':<10} {'Train R2':<12} {'Test R2':<12} {'Gap':<10}")
print("-" * 44)

for alpha in alphas:
    ridge = Ridge(alpha=alpha)
    ridge.fit(X_train_poly, y_train)
    train_score = ridge.score(X_train_poly, y_train)
    test_score = ridge.score(X_test_poly, y_test)
    gap = train_score - test_score
    print(f"{alpha:<10} {train_score:<12.4f} {test_score:<12.4f} {gap:<10.4f}")
```

**Expected Output:**

```
Alpha      Train R2     Test R2      Gap
--------------------------------------------
0.001      0.9987       0.5312       0.4675
0.01       0.9937       0.8654       0.1283
0.1        0.9721       0.9268       0.0453
1.0        0.9543       0.9187       0.0356
10.0       0.9418       0.9288       0.0130
100.0      0.9326       0.9394       -0.0068
1000.0     0.8694       0.8806       -0.0112
```

**What the output tells us:**

- `alpha=0.001`: Very low regularization. Training is great (0.9987), test is poor (0.53). Large gap = overfitting.
- `alpha=0.1 to 10.0`: Good range. Training and test scores are close. Small gap.
- `alpha=1000.0`: Too much regularization. Both scores drop. The model is too simple (underfitting).

### Using Cross-Validation to Choose Alpha

The best way to choose alpha is **cross-validation**. Scikit-learn provides `RidgeCV` and `LassoCV` that do this automatically.

```python
import numpy as np
from sklearn.linear_model import RidgeCV, LassoCV
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split

# Create data
np.random.seed(42)
X = np.linspace(0, 10, 30).reshape(-1, 1)
y = 2 * X.ravel() + 1 + np.random.randn(30) * 2

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

poly = PolynomialFeatures(degree=15)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

# RidgeCV automatically finds the best alpha
alphas_to_try = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
ridge_cv = RidgeCV(alphas=alphas_to_try, cv=5)
ridge_cv.fit(X_train_poly, y_train)

print("RidgeCV Results:")
print(f"  Best alpha: {ridge_cv.alpha_}")
print(f"  Training R2: {ridge_cv.score(X_train_poly, y_train):.4f}")
print(f"  Test R2:     {ridge_cv.score(X_test_poly, y_test):.4f}")

# LassoCV automatically finds the best alpha
lasso_cv = LassoCV(cv=5, random_state=42)
lasso_cv.fit(X_train_poly, y_train)

print("\nLassoCV Results:")
print(f"  Best alpha: {lasso_cv.alpha_:.4f}")
print(f"  Training R2: {lasso_cv.score(X_train_poly, y_train):.4f}")
print(f"  Test R2:     {lasso_cv.score(X_test_poly, y_test):.4f}")
```

**Expected Output:**

```
RidgeCV Results:
  Best alpha: 10.0
  Training R2: 0.9418
  Test R2:     0.9288

LassoCV Results:
  Best alpha: 0.1827
  Training R2: 0.9324
  Test R2:     0.9404
```

**Line-by-line explanation:**

- `RidgeCV(alphas=alphas_to_try, cv=5)` — tries each alpha value using 5-fold cross-validation and picks the best one. You give it a list of alphas to try.
- `ridge_cv.alpha_` — after fitting, this tells you which alpha won.
- `LassoCV(cv=5, random_state=42)` — automatically generates a range of alpha values and tests them. You do not need to provide the list yourself.
- `lasso_cv.alpha_` — the best alpha found by cross-validation.

---

## 11.7 Complete Comparison: Linear vs Ridge vs Lasso

Let us put it all together with a complete comparison:

```python
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split

# Create data with a known pattern
np.random.seed(42)
X = np.linspace(0, 10, 50).reshape(-1, 1)
y = 3 * X.ravel() + 2 + np.random.randn(50) * 3

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Add polynomial features to make overfitting possible
poly = PolynomialFeatures(degree=12)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

# Build four models
models = {
    "Linear Regression": LinearRegression(),
    "Ridge (alpha=1.0)": Ridge(alpha=1.0),
    "Lasso (alpha=0.1)": Lasso(alpha=0.1),
    "Elastic Net":       ElasticNet(alpha=0.1, l1_ratio=0.5),
}

print(f"{'Model':<22} {'Train R2':<10} {'Test R2':<10} {'Non-zero':<10}")
print("=" * 52)

for name, model in models.items():
    model.fit(X_train_poly, y_train)
    train_r2 = model.score(X_train_poly, y_train)
    test_r2 = model.score(X_test_poly, y_test)
    non_zero = np.sum(model.coef_ != 0)
    print(f"{name:<22} {train_r2:<10.4f} {test_r2:<10.4f} {non_zero:<10}")
```

**Expected Output:**

```
Model                  Train R2   Test R2    Non-zero
====================================================
Linear Regression      0.9978     -0.6231    13
Ridge (alpha=1.0)      0.9457     0.9031     13
Lasso (alpha=0.1)      0.9215     0.9221     2
Elastic Net            0.9202     0.9195     3
```

**What this tells us:**

```
Summary Table:

+---------------------+----------+---------+----------+
| Model               | Train R2 | Test R2 | Features |
+---------------------+----------+---------+----------+
| Linear Regression   |  0.9978  | -0.6231 |    13    |  <-- Overfits!
| Ridge               |  0.9457  |  0.9031 |    13    |  <-- All features, shrunk
| Lasso               |  0.9215  |  0.9221 |     2    |  <-- Only 2 features!
| Elastic Net         |  0.9202  |  0.9195 |     3    |  <-- 3 features
+---------------------+----------+---------+----------+

Winner: Lasso — simplest model, best test score!
```

- **Linear Regression** overfits terribly. Perfect training, terrible test.
- **Ridge** fixes overfitting by shrinking coefficients. Keeps all 13 features.
- **Lasso** fixes overfitting AND selects features. Keeps only 2 features!
- **Elastic Net** is a compromise. Keeps 3 features.

---

## 11.8 When to Use Which

```
Decision Guide:

Start with your problem
        |
        v
Do you have many features?
        |
   Yes  |  No
   |    |    |
   v    |    v
   |    |  Try Ridge first
   |    |  (simple, works well)
   v    |
Do you think many    |
features are useless?|
   |                 |
  Yes     No         |
   |       |         |
   v       v         |
  Lasso   Elastic    |
          Net        |
   |       |         |
   v       v         v
   Always use cross-validation
   to find the best alpha!
```

---

## Common Mistakes

1. **Forgetting to scale features before regularization.** Regularization penalizes large coefficients. If features have different scales, features with larger values will be penalized more unfairly. Always use StandardScaler or similar before Ridge/Lasso.

2. **Using alpha=0 and thinking it is regularized.** Alpha=0 means no regularization at all. It is the same as plain Linear Regression.

3. **Setting alpha too high.** Too much regularization makes the model too simple. It will underfit. Both training and test scores will be low.

4. **Not using cross-validation to choose alpha.** Guessing alpha is unreliable. Use RidgeCV or LassoCV to find the best value automatically.

5. **Confusing Ridge and Lasso.** Ridge shrinks coefficients but keeps all features. Lasso can remove features entirely. Pick the right one for your problem.

---

## Best Practices

1. **Always scale your features** before applying regularization. Use `StandardScaler` from scikit-learn.

2. **Start with RidgeCV or LassoCV.** Let cross-validation find the best alpha for you.

3. **Use Lasso when you want feature selection.** If you have many features and suspect most are useless, Lasso will identify the important ones.

4. **Use Elastic Net when Lasso is unstable.** If you have correlated features, Lasso may arbitrarily pick one and drop the other. Elastic Net handles this better.

5. **Compare models.** Try Linear Regression, Ridge, and Lasso on your data. Compare test scores to see which works best.

6. **Watch the train-test gap.** A large gap between training and test scores means overfitting. Increase alpha to add more regularization.

---

## Quick Summary

```
Regularization in One Picture:

  Problem:   Model memorizes training data (overfitting)
  Solution:  Add a penalty for complex models (regularization)

  Ridge (L2):  Shrinks all coefficients. Keeps all features.
  Lasso (L1):  Can zero out coefficients. Removes useless features.
  Elastic Net: Mix of Ridge and Lasso. Best of both worlds.

  alpha:  Controls how much to penalize.
          Low alpha  = Less penalty = Risk of overfitting
          High alpha = More penalty = Risk of underfitting
          Use cross-validation to find the best alpha!
```

---

## Key Points to Remember

1. **Overfitting** is when a model memorizes training data but fails on new data. The sign is a large gap between training and test scores.

2. **Regularization** adds a penalty for large coefficients, forcing the model to stay simple.

3. **Ridge (L2)** shrinks all coefficients toward zero but never to exactly zero. All features stay in the model.

4. **Lasso (L1)** can make coefficients exactly zero, effectively removing features. This is automatic feature selection.

5. **Elastic Net** combines Ridge and Lasso. The `l1_ratio` parameter controls the mix.

6. **Alpha** controls regularization strength. Use cross-validation (RidgeCV, LassoCV) to find the best value.

7. **Always scale features** before applying regularization.

---

## Practice Questions

### Question 1
Your model has a training R2 of 0.99 and a test R2 of 0.55. What is happening, and what should you do?

**Answer:** The model is overfitting. The large gap (0.99 - 0.55 = 0.44) between training and test scores is the classic sign. You should apply regularization (Ridge or Lasso) to penalize model complexity. You should also use cross-validation to find the best alpha value.

### Question 2
You have a dataset with 200 features, but you suspect only about 10 are actually useful. Which regularization method should you use and why?

**Answer:** Use Lasso (L1 regularization). Lasso can set coefficients to exactly zero, effectively removing useless features. Since you suspect most features are not useful, Lasso will perform automatic feature selection and identify the approximately 10 important features. You could also try Elastic Net if Lasso behaves unstably due to correlated features.

### Question 3
What happens if you set alpha to a very large value (like 1,000,000)?

**Answer:** The model will underfit. With an extremely large alpha, the penalty for having any non-zero coefficients is so high that all coefficients will be pushed to nearly zero. The model becomes too simple and cannot capture even the basic pattern in the data. Both training and test scores will be low.

### Question 4
Why is it important to scale features before applying regularization?

**Answer:** Regularization penalizes coefficients based on their size. If features have different scales (for example, age ranges from 0-100 and income from 0-1,000,000), the coefficient for income will naturally be much smaller. Regularization will penalize the age coefficient more, even if income is a more important feature. Scaling ensures all features are treated fairly by the regularization penalty.

### Question 5
What is the difference between RidgeCV and Ridge?

**Answer:** `Ridge` requires you to manually set the alpha parameter. You have to guess or try different values yourself. `RidgeCV` automatically tries multiple alpha values using cross-validation and picks the one that gives the best performance. Always prefer RidgeCV over Ridge to avoid guessing.

---

## Exercises

### Exercise 1: Ridge vs Lasso Comparison

Create a dataset with 5 features where only 2 actually affect the target. Train both Ridge and Lasso models. Compare their coefficients. Does Lasso correctly identify the 2 important features?

**Hint:** Use `np.random.randn(100, 5)` to create 5 features. Make the target depend on only features 0 and 3.

### Exercise 2: Alpha Exploration

Using the Boston-style housing data (or any regression dataset), create a plot of test R2 scores for Ridge regression with alpha values from 0.01 to 1000 (use `np.logspace(-2, 3, 50)` to generate alpha values). Which alpha gives the best test score?

**Hint:** Loop through each alpha value, train a Ridge model, and store the test score. Print the results in a table.

### Exercise 3: Elastic Net Tuning

Use ElasticNet with different combinations of alpha (0.01, 0.1, 1.0) and l1_ratio (0.1, 0.5, 0.9). Find the combination that gives the best test score on your data. What does the best l1_ratio tell you about whether Ridge or Lasso behavior is more appropriate for your data?

**Hint:** Use nested loops — one for alpha values and one for l1_ratio values.

---

## What Is Next?

In this chapter, you learned how to prevent overfitting using regularization. You saw that Ridge shrinks coefficients and Lasso removes them entirely. These techniques work with regression problems — predicting continuous numbers.

But what if you need to predict categories? What if the question is not "how much?" but "which class?" In the next chapter, you will learn **Logistic Regression** — a technique that turns regression into classification. Despite its name, Logistic Regression is actually a classification method. It predicts probabilities and assigns categories like spam/not-spam, yes/no, or buy/not-buy. Get ready to cross the bridge from regression to classification!
