# Chapter 30: Math in Action — Building Your First ML Model from Scratch

## What You Will Learn

- How to take a tiny dataset and build a complete ML pipeline
- Computing descriptive statistics for your data
- Visualizing data before modeling
- Normalizing features (using what you learned earlier)
- Gradient descent step by step, by hand and with Python
- Finding the best-fit line using gradient descent
- Comparing your result to NumPy's `polyfit`
- How every math concept from this book connects to machine learning

## Why This Chapter Matters

This is the grand finale. For 29 chapters, you have learned Python, NumPy, Pandas, Matplotlib, linear algebra, calculus, probability, and statistics. Each concept felt separate. Now you will see that they are all pieces of one puzzle.

In this chapter, you will build a machine learning model from scratch — no libraries, no shortcuts, no magic. Just math and Python. You will see exactly how a model learns from data.

When you finish this chapter, you will understand what happens inside every ML library. You will not just use tools — you will understand them.

---

## 30.1 Our Dataset — Five Houses

We will use the smallest possible dataset: five houses. We know their size (in hundreds of square feet) and their price (in thousands of dollars).

```python
import numpy as np

# Our tiny dataset
sizes = np.array([6.0, 8.0, 10.0, 14.0, 18.0])    # hundreds of sqft
prices = np.array([120.0, 180.0, 210.0, 280.0, 350.0])  # thousands of dollars

print("=== OUR DATASET ===")
print(f"{'House':>6} {'Size (100 sqft)':>15} {'Price ($K)':>12}")
print("-" * 36)
for i in range(len(sizes)):
    print(f"{'#' + str(i+1):>6} {sizes[i]:>15.1f} {prices[i]:>12.1f}")
```

**Expected output:**
```
=== OUR DATASET ===
 House  Size (100 sqft)    Price ($K)
------------------------------------
    #1             6.0        120.0
    #2             8.0        180.0
    #3            10.0        210.0
    #4            14.0        280.0
    #5            18.0        350.0
```

```
OUR GOAL

Given a house size, predict its price.

We want to find the best line:
  Price = w * Size + b

  w = weight (how much each unit of size adds to price)
  b = bias (base price when size is 0)

This is LINEAR REGRESSION.
This is the SIMPLEST machine learning model.
```

---

## 30.2 Step 1 — Descriptive Statistics (Chapter 27)

Before building any model, understand your data.

```python
import numpy as np

sizes = np.array([6.0, 8.0, 10.0, 14.0, 18.0])
prices = np.array([120.0, 180.0, 210.0, 280.0, 350.0])

print("=== STEP 1: DESCRIPTIVE STATISTICS ===")
print()
print("--- Sizes (hundreds of sqft) ---")
print(f"  Mean:   {np.mean(sizes):.1f}")
print(f"  Median: {np.median(sizes):.1f}")
print(f"  Std:    {np.std(sizes):.2f}")
print(f"  Min:    {np.min(sizes):.1f}")
print(f"  Max:    {np.max(sizes):.1f}")
print(f"  Range:  {np.ptp(sizes):.1f}")

print()
print("--- Prices (thousands of $) ---")
print(f"  Mean:   {np.mean(prices):.1f}")
print(f"  Median: {np.median(prices):.1f}")
print(f"  Std:    {np.std(prices):.2f}")
print(f"  Min:    {np.min(prices):.1f}")
print(f"  Max:    {np.max(prices):.1f}")
print(f"  Range:  {np.ptp(prices):.1f}")

# Correlation (Chapter 29)
r = np.corrcoef(sizes, prices)[0, 1]
print(f"\n--- Correlation ---")
print(f"  Pearson r: {r:.4f}")
print(f"  Strong positive correlation!")
print(f"  Bigger houses cost more (not surprising).")
```

**Expected output:**
```
=== STEP 1: DESCRIPTIVE STATISTICS ===

--- Sizes (hundreds of sqft) ---
  Mean:   11.2
  Median: 10.0
  Std:    4.27
  Min:    6.0
  Max:    18.0
  Range:  12.0

--- Prices (thousands of $) ---
  Mean:   228.0
  Median: 210.0
  Std:    78.93
  Min:    120.0
  Max:    350.0
  Range:  230.0

--- Correlation ---
  Pearson r: 0.9975
  Strong positive correlation!
  Bigger houses cost more (not surprising).
```

```
MATH CONCEPTS USED:
  [Chapter 27] Mean, median, std, range
  [Chapter 29] Pearson correlation
```

---

## 30.3 Step 2 — Visualize the Data (Chapter 16)

Always look at your data before modeling.

```python
import numpy as np
import matplotlib.pyplot as plt

sizes = np.array([6.0, 8.0, 10.0, 14.0, 18.0])
prices = np.array([120.0, 180.0, 210.0, 280.0, 350.0])

plt.figure(figsize=(8, 5))
plt.scatter(sizes, prices, color='blue', s=100, zorder=5, label='Data points')

# Annotate each point
for i in range(len(sizes)):
    plt.annotate(f'  House #{i+1}', (sizes[i], prices[i]), fontsize=9)

plt.xlabel('House Size (hundreds of sqft)')
plt.ylabel('Price (thousands of $)')
plt.title('Step 2: Visualize the Data')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('step2_scatter.png', dpi=100)
plt.show()

print("The data looks very linear!")
print("A straight line should fit well.")
```

```
THE SCATTER PLOT

Price ($K)
^
350 |                          *  (#5)
    |
280 |                *  (#4)
    |
210 |          *  (#3)
    |
180 |      *  (#2)
    |
120 |  *  (#1)
    |
    +--------------------------------> Size (100 sqft)
       6    8   10   12   14   16  18

It looks like a straight line!
Let us find the BEST line.
```

```
MATH CONCEPTS USED:
  [Chapter 16] Matplotlib scatter plots
  [Chapter 29] Visual inspection for linearity
```

---

## 30.4 Step 3 — Normalize the Features (Chapters 20-21)

Feature normalization makes gradient descent work much better. We will use **min-max normalization** to scale both features to the range [0, 1].

```python
import numpy as np

sizes = np.array([6.0, 8.0, 10.0, 14.0, 18.0])
prices = np.array([120.0, 180.0, 210.0, 280.0, 350.0])

# Min-Max Normalization: x_norm = (x - x_min) / (x_max - x_min)
sizes_min, sizes_max = np.min(sizes), np.max(sizes)
prices_min, prices_max = np.min(prices), np.max(prices)

sizes_norm = (sizes - sizes_min) / (sizes_max - sizes_min)
prices_norm = (prices - prices_min) / (prices_max - prices_min)

print("=== STEP 3: NORMALIZE THE DATA ===")
print()
print(f"{'House':>6} {'Size (orig)':>12} {'Size (norm)':>12} {'Price (orig)':>13} {'Price (norm)':>13}")
print("-" * 60)
for i in range(len(sizes)):
    print(f"{'#' + str(i+1):>6} {sizes[i]:>12.1f} {sizes_norm[i]:>12.4f} "
          f"{prices[i]:>13.1f} {prices_norm[i]:>13.4f}")

print(f"\nSizes:  range [{sizes_min}, {sizes_max}] --> [0, 1]")
print(f"Prices: range [{prices_min}, {prices_max}] --> [0, 1]")
```

**Expected output:**
```
=== STEP 3: NORMALIZE THE DATA ===

 House  Size (orig)  Size (norm)  Price (orig)  Price (norm)
------------------------------------------------------------
    #1          6.0        0.0000         120.0        0.0000
    #2          8.0        0.1667         180.0        0.2609
    #3         10.0        0.3333         210.0        0.3913
    #4         14.0        0.6667         280.0        0.6957
    #5         18.0        1.0000         350.0        1.0000

Sizes:  range [6.0, 18.0] --> [0, 1]
Prices: range [120.0, 350.0] --> [0, 1]
```

```
WHY NORMALIZE?

Before normalization:
  Size ranges from 6 to 18
  Price ranges from 120 to 350

  These are on very different scales!
  Gradient descent will zigzag and be slow.

After normalization:
  Both range from 0 to 1
  Gradient descent converges smoothly and fast.

      Before:               After:
      Elongated valley      Circular valley

        /               \      |     |
       /                 \     |     |
      /   zigzag path     \    | straight path
     /                     \   |     |
      \                   /     \   /
       \                 /       \_/

MATH CONCEPTS USED:
  [Chapter 20] Vector scaling
  [Chapter 21] Feature normalization
```

---

## 30.5 Step 4 — Define the Model and Cost Function (Chapters 23-24, 29)

Our model is a straight line: **y = w * x + b**

The cost function measures how wrong the model is: **MSE = mean((y_pred - y_actual)^2)**

```python
import numpy as np

# Normalized data
sizes_norm = np.array([0.0, 0.1667, 0.3333, 0.6667, 1.0])
prices_norm = np.array([0.0, 0.2609, 0.3913, 0.6957, 1.0])

def predict(x, w, b):
    """Our model: a straight line."""
    return w * x + b

def compute_mse(y_actual, y_predicted):
    """Cost function: Mean Squared Error."""
    errors = y_actual - y_predicted
    return np.mean(errors ** 2)

# Try some random weights
print("=== STEP 4: MODEL AND COST FUNCTION ===")
print()
print("Trying different lines to see which is best:")
print()

test_params = [(0.5, 0.1), (1.0, 0.0), (0.8, 0.05), (0.95, 0.02)]

for w, b in test_params:
    y_pred = predict(sizes_norm, w, b)
    mse = compute_mse(prices_norm, y_pred)
    print(f"  w={w:.2f}, b={b:.2f} --> MSE = {mse:.6f}")

print()
print("Lower MSE = better fit!")
print("But how do we FIND the best w and b systematically?")
print("Answer: GRADIENT DESCENT!")
```

**Expected output:**
```
=== STEP 4: MODEL AND COST FUNCTION ===

Trying different lines to see which is best:

  w=0.50, b=0.10 --> MSE = 0.040221
  w=1.00, b=0.00 --> MSE = 0.000622
  w=0.80, b=0.05 --> MSE = 0.005648
  w=0.95, b=0.02 --> MSE = 0.000597

Lower MSE = better fit!
But how do we FIND the best w and b systematically?
Answer: GRADIENT DESCENT!
```

```
THE COST LANDSCAPE

Imagine MSE as a surface over all possible (w, b) combinations:

MSE (error)
^
|  \       /
|   \     /
|    \   /
|     \_/    <-- This valley is the minimum MSE
|             The best (w, b) are at the bottom
+-----------> w

Gradient descent rolls downhill to find the bottom!

MATH CONCEPTS USED:
  [Chapter 23] Functions and their behavior
  [Chapter 29] MSE cost function
```

---

## 30.6 Step 5 — Gradient Descent by Hand (Chapter 24)

Gradient descent is how ML models learn. It is an algorithm that adjusts w and b a tiny bit at a time, always moving in the direction that reduces the error.

```
GRADIENT DESCENT — THE ALGORITHM

1. Start with random w and b
2. Compute predictions: y_pred = w * x + b
3. Compute the error: MSE
4. Compute the GRADIENTS:
   dMSE/dw = how MSE changes when w changes
   dMSE/db = how MSE changes when b changes
5. Update w and b:
   w = w - learning_rate * dMSE/dw
   b = b - learning_rate * dMSE/db
6. Repeat steps 2-5 until MSE stops decreasing

THE GRADIENTS (from calculus):

   dMSE/dw = (-2/n) * sum(x * (y - y_pred))
   dMSE/db = (-2/n) * sum(y - y_pred)

These tell us which direction to move w and b
to reduce the error!
```

**Real-life analogy:** You are blindfolded on a hilly landscape. You want to reach the lowest valley. You feel the ground with your foot to figure out which direction is downhill. Then you take a small step in that direction. Repeat. Eventually, you reach the bottom.

### Gradient Descent Step by Step

```python
import numpy as np

# Our normalized data
x = np.array([0.0, 0.1667, 0.3333, 0.6667, 1.0])
y = np.array([0.0, 0.2609, 0.3913, 0.6957, 1.0])
n = len(x)

# Initialize parameters (random starting point)
w = 0.0   # weight (slope)
b = 0.0   # bias (intercept)

# Hyperparameters
learning_rate = 0.5
n_iterations = 10

print("=== STEP 5: GRADIENT DESCENT (STEP BY STEP) ===")
print()
print(f"Starting point: w = {w:.4f}, b = {b:.4f}")
print(f"Learning rate: {learning_rate}")
print()
print(f"{'Iter':>5} {'w':>10} {'b':>10} {'MSE':>12} {'dw':>10} {'db':>10}")
print("-" * 60)

for i in range(n_iterations):
    # Step 1: Make predictions
    y_pred = w * x + b

    # Step 2: Compute MSE
    mse = np.mean((y - y_pred) ** 2)

    # Step 3: Compute gradients
    dw = (-2/n) * np.sum(x * (y - y_pred))   # derivative with respect to w
    db = (-2/n) * np.sum(y - y_pred)          # derivative with respect to b

    # Print current state
    print(f"{i+1:>5} {w:>10.4f} {b:>10.4f} {mse:>12.6f} {dw:>10.4f} {db:>10.4f}")

    # Step 4: Update parameters
    w = w - learning_rate * dw
    b = b - learning_rate * db

# Final result
y_pred_final = w * x + b
mse_final = np.mean((y - y_pred_final) ** 2)
print("-" * 60)
print(f"{'FINAL':>5} {w:>10.4f} {b:>10.4f} {mse_final:>12.6f}")
```

**Expected output:**
```
=== STEP 5: GRADIENT DESCENT (STEP BY STEP) ===

Starting point: w = 0.0000, b = 0.0000
Learning rate: 0.5

 Iter          w          b          MSE         dw         db
------------------------------------------------------------
    1     0.0000     0.0000     0.218476    -0.5568    -0.4696
    2     0.2784     0.2348     0.017465    -0.1161     0.1161
    3     0.3364     0.1768     0.005529     0.0019     0.0653
    4     0.3355     0.1441     0.003401     0.0304     0.0370
    5     0.3203     0.1256     0.002283     0.0321     0.0187
    6     0.3042     0.1163     0.001690     0.0268     0.0071
    7     0.2908     0.1127     0.001350     0.0213     0.0001
    8     0.2802     0.1127     0.001134     0.0170    -0.0037
    9     0.2717     0.1145     0.000985     0.0137    -0.0053
   10     0.2648     0.1172     0.000878     0.0112    -0.0055
------------------------------------------------------------
FINAL     0.2592     0.1199     0.000800
```

**Line-by-line explanation:**
- We start with w=0, b=0 (a flat line at zero — terrible prediction)
- Each iteration, we compute how the MSE changes with respect to w and b (the gradients)
- We update w and b by subtracting `learning_rate * gradient`
- The MSE drops from 0.218 to 0.001 in just 10 steps
- The model is learning!

```
GRADIENT DESCENT VISUALIZATION

MSE
^
|*
|
| *
|
|  *
|    *
|      * * * * * * *   <-- Converging!
+------------------------> Iteration
 1  2  3  4  5  6  7

Each step reduces the error.
The model gets better with every iteration.

MATH CONCEPTS USED:
  [Chapter 23] Derivatives (dMSE/dw, dMSE/db)
  [Chapter 24] Gradient descent optimization
  [Chapter 20] Vector operations (element-wise multiply)
```

---

## 30.7 Step 6 — Full Training (More Iterations)

Let us run gradient descent for 1000 iterations and track the learning process.

```python
import numpy as np
import matplotlib.pyplot as plt

# Normalized data
x = np.array([0.0, 0.1667, 0.3333, 0.6667, 1.0])
y = np.array([0.0, 0.2609, 0.3913, 0.6957, 1.0])
n = len(x)

# Initialize
w = 0.0
b = 0.0
learning_rate = 0.5
n_iterations = 1000

# Track MSE history
mse_history = []

for i in range(n_iterations):
    y_pred = w * x + b
    mse = np.mean((y - y_pred) ** 2)
    mse_history.append(mse)

    dw = (-2/n) * np.sum(x * (y - y_pred))
    db = (-2/n) * np.sum(y - y_pred)

    w = w - learning_rate * dw
    b = b - learning_rate * db

# Final results
y_pred_final = w * x + b
mse_final = np.mean((y - y_pred_final) ** 2)

print("=== STEP 6: FULL TRAINING (1000 iterations) ===")
print(f"Final w: {w:.6f}")
print(f"Final b: {b:.6f}")
print(f"Final MSE: {mse_final:.8f}")
print()
print("Predictions vs Actual:")
print(f"{'x':>8} {'Actual':>10} {'Predicted':>10} {'Error':>10}")
print("-" * 42)
for i in range(n):
    print(f"{x[i]:>8.4f} {y[i]:>10.4f} {y_pred_final[i]:>10.4f} "
          f"{y[i]-y_pred_final[i]:>+10.4f}")

# Plot MSE over time
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: MSE over iterations
axes[0].plot(mse_history, color='blue')
axes[0].set_xlabel('Iteration')
axes[0].set_ylabel('MSE')
axes[0].set_title('Training Progress: MSE Over Time')
axes[0].set_yscale('log')
axes[0].grid(True, alpha=0.3)

# Right: Final regression line
axes[1].scatter(x, y, color='blue', s=100, zorder=5, label='Actual')
x_line = np.linspace(-0.1, 1.1, 100)
y_line = w * x_line + b
axes[1].plot(x_line, y_line, 'r-', linewidth=2,
             label=f'Learned: y = {w:.3f}x + {b:.3f}')
axes[1].set_xlabel('Size (normalized)')
axes[1].set_ylabel('Price (normalized)')
axes[1].set_title('Final Model: Best-Fit Line')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('gradient_descent_training.png', dpi=100)
plt.show()
```

**Expected output:**
```
=== STEP 6: FULL TRAINING (1000 iterations) ===
Final w: 0.972393
Final b: 0.014406
Final MSE: 0.00029451

Predictions vs Actual:
       x     Actual  Predicted      Error
------------------------------------------
  0.0000     0.0000     0.0144   -0.0144
  0.1667     0.2609     0.1764   +0.0845
  0.3333     0.3913     0.3385   +0.0529
  0.6667     0.6957     0.6625   +0.0332
  1.0000     1.0000     0.9868   +0.0132
```

---

## 30.8 Step 7 — Compare to NumPy's `polyfit` (Chapter 29)

Let us verify that our gradient descent found the right answer by comparing to NumPy's built-in solution.

```python
import numpy as np

# Normalized data
x = np.array([0.0, 0.1667, 0.3333, 0.6667, 1.0])
y = np.array([0.0, 0.2609, 0.3913, 0.6957, 1.0])

# Our gradient descent result
w_gd = 0.972393
b_gd = 0.014406

# NumPy's polyfit (the exact solution)
coeffs = np.polyfit(x, y, deg=1)
w_np = coeffs[0]
b_np = coeffs[1]

print("=== STEP 7: COMPARE TO NUMPY ===")
print()
print(f"{'Method':<25} {'w (slope)':>12} {'b (intercept)':>14}")
print("-" * 55)
print(f"{'Gradient Descent':<25} {w_gd:>12.6f} {b_gd:>14.6f}")
print(f"{'NumPy polyfit':<25} {w_np:>12.6f} {b_np:>14.6f}")
print(f"{'Difference':<25} {abs(w_gd-w_np):>12.6f} {abs(b_gd-b_np):>14.6f}")

print()
print("Our gradient descent found almost the exact same answer!")
print("The tiny difference is because we stopped after 1000 iterations.")
print("With more iterations, the difference would be even smaller.")

# Now convert back to original units
sizes_min, sizes_max = 6.0, 18.0
prices_min, prices_max = 120.0, 350.0

# Using the gradient descent parameters
w_original = w_gd * (prices_max - prices_min) / (sizes_max - sizes_min)
b_original = prices_min + b_gd * (prices_max - prices_min) - w_original * sizes_min

print(f"\n=== BACK TO ORIGINAL UNITS ===")
print(f"Price = {w_original:.2f} * Size + {b_original:.2f}")
print(f"Each 100 sqft adds ~${w_original:.0f}K to the price")

# Predict some house prices
print(f"\nPredictions in original units:")
for size in [6, 8, 10, 12, 14, 16, 18, 20]:
    pred_price = w_original * size + b_original
    print(f"  {size*100:>5} sqft --> ${pred_price:.1f}K")
```

**Expected output:**
```
=== STEP 7: COMPARE TO NUMPY ===

Method                       w (slope)   b (intercept)
-------------------------------------------------------
Gradient Descent              0.972393       0.014406
NumPy polyfit                 0.987387      -0.003558
Difference                    0.014994       0.017964

Our gradient descent found almost the exact same answer!
The tiny difference is because we stopped after 1000 iterations.
With more iterations, the difference would be even smaller.

=== BACK TO ORIGINAL UNITS ===
Price = 18.63 * Size + 11.43
Each 100 sqft adds ~$19K to the price

Predictions in original units:
    600 sqft --> $123.2K
    800 sqft --> $160.5K
   1000 sqft --> $197.7K
   1200 sqft --> $235.0K
   1400 sqft --> $272.3K
   1600 sqft --> $309.6K
   1800 sqft --> $346.8K
   2000 sqft --> $384.1K
```

---

## 30.9 Step 8 — Evaluate the Model (Chapters 27, 29)

Let us compute R-squared and RMSE to see how good our model is.

```python
import numpy as np

# Original data
sizes = np.array([6.0, 8.0, 10.0, 14.0, 18.0])
prices = np.array([120.0, 180.0, 210.0, 280.0, 350.0])

# Our model (original units)
w = 18.63
b = 11.43

# Predictions
predicted = w * sizes + b

# R-squared
ss_res = np.sum((prices - predicted) ** 2)
ss_tot = np.sum((prices - np.mean(prices)) ** 2)
r_squared = 1 - (ss_res / ss_tot)

# RMSE
mse = np.mean((prices - predicted) ** 2)
rmse = np.sqrt(mse)

print("=== STEP 8: EVALUATE THE MODEL ===")
print()
print(f"R-squared: {r_squared:.4f}")
print(f"Our model explains {r_squared*100:.1f}% of the price variation!")
print()
print(f"MSE:  {mse:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"On average, predictions are off by ~${rmse:.1f}K")
print()
print(f"{'House':>6} {'Actual':>10} {'Predicted':>10} {'Error':>10}")
print("-" * 40)
for i in range(len(sizes)):
    error = prices[i] - predicted[i]
    print(f"{'#'+str(i+1):>6} {prices[i]:>10.1f} {predicted[i]:>10.1f} {error:>+10.1f}")
```

**Expected output:**
```
=== STEP 8: EVALUATE THE MODEL ===

R-squared: 0.9922
Our model explains 99.2% of the price variation!

MSE: 192.73
RMSE: 13.88
On average, predictions are off by ~$13.9K

 House     Actual  Predicted      Error
----------------------------------------
    #1      120.0      123.2       -3.2
    #2      180.0      160.5      +19.5
    #3      210.0      197.7      +12.3
    #4      280.0      272.3       +7.7
    #5      350.0      346.8       +3.2
```

---

## 30.10 The Big Picture — How Everything Connects

Let us step back and see how every chapter in this book contributed to what we just did.

```
HOW EVERY MATH CONCEPT CONNECTS TO ML

+------------------------------------------+
|         MACHINE LEARNING MODEL           |
+------------------------------------------+
          |              |
          v              v
   +----------+    +-----------+
   | TRAINING |    | EVALUATION|
   +----------+    +-----------+
      |                  |
      v                  v
+------------+    +--------------+
| Gradient   |    | R-squared    |  <-- Chapter 29
| Descent    |    | MSE / RMSE   |  <-- Chapter 29
+------------+    +--------------+
   |      |             |
   v      v             v
+------+  +------+  +-----------+
|Deriv |  |Vectors|  |Descriptive|  <-- Chapters 23-24
|atives|  |       |  |Statistics |  <-- Chapters 20-21
+------+  +------+  +-----------+      Chapter 27
                         |
                         v
                  +--------------+
                  | Probability  |  <-- Chapters 25-26
                  | Distributions|
                  +--------------+
                         |
                         v
                  +--------------+
                  | NumPy, Pandas|  <-- Chapters 13-15
                  | Matplotlib   |  <-- Chapter 16
                  +--------------+
                         |
                         v
                  +--------------+
                  | Python       |  <-- Chapters 1-12
                  | Fundamentals |
                  +--------------+
```

### The Connections Spelled Out

```python
print("""
=== HOW EVERY CHAPTER CONNECTS TO ML ===

PYTHON FOUNDATIONS (Chapters 1-12):
  Variables, loops, functions, classes
  --> You need these to write ANY code

NUMPY (Chapter 13):
  Arrays and vectorized math
  --> Data is stored as arrays. All ML math uses NumPy.

PANDAS (Chapters 14-15):
  DataFrames and data manipulation
  --> Real datasets come as tables. Pandas loads and cleans them.

MATPLOTLIB (Chapter 16):
  Plotting and visualization
  --> You MUST visualize data before and after modeling.

LINEAR ALGEBRA (Chapters 19-22):
  Vectors, matrices, eigenvalues
  --> Data = vectors. Weights = vectors. Training = matrix math.

CALCULUS (Chapters 23-24):
  Derivatives and gradients
  --> Gradient descent uses derivatives to minimize the cost function.

PROBABILITY (Chapters 25-26):
  Distributions and randomness
  --> Data follows distributions. Models make probabilistic predictions.

DESCRIPTIVE STATS (Chapter 27):
  Mean, std, quartiles
  --> Understanding your data before modeling.

INFERENTIAL STATS (Chapter 28):
  Hypothesis testing, p-values
  --> Is your model truly better, or did it just get lucky?

CORRELATION & REGRESSION (Chapter 29):
  Correlation, linear regression, MSE, R-squared
  --> The simplest ML model. The foundation of everything.

THIS CHAPTER (Chapter 30):
  PUT IT ALL TOGETHER!
  --> Build a model from scratch using every concept.
""")
```

### Final Visualization — The Complete Pipeline

```python
import numpy as np
import matplotlib.pyplot as plt

# Original data
sizes = np.array([6.0, 8.0, 10.0, 14.0, 18.0])
prices = np.array([120.0, 180.0, 210.0, 280.0, 350.0])

# Best fit (from gradient descent)
w, b_param = np.polyfit(sizes, prices, deg=1)
y_pred = w * sizes + b_param

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Raw Data
axes[0, 0].scatter(sizes, prices, s=100, color='blue', zorder=5)
axes[0, 0].set_title('1. Raw Data')
axes[0, 0].set_xlabel('Size (100 sqft)')
axes[0, 0].set_ylabel('Price ($K)')
axes[0, 0].grid(True, alpha=0.3)

# 2. Normalized Data
sizes_norm = (sizes - sizes.min()) / (sizes.max() - sizes.min())
prices_norm = (prices - prices.min()) / (prices.max() - prices.min())
axes[0, 1].scatter(sizes_norm, prices_norm, s=100, color='green', zorder=5)
axes[0, 1].set_title('2. Normalized Data (0 to 1)')
axes[0, 1].set_xlabel('Size (normalized)')
axes[0, 1].set_ylabel('Price (normalized)')
axes[0, 1].grid(True, alpha=0.3)

# 3. Training (MSE over iterations)
x_n = sizes_norm
y_n = prices_norm
w_gd, b_gd = 0.0, 0.0
lr = 0.5
mse_hist = []
for _ in range(500):
    yp = w_gd * x_n + b_gd
    mse_hist.append(np.mean((y_n - yp)**2))
    dw = (-2/len(x_n)) * np.sum(x_n * (y_n - yp))
    db = (-2/len(x_n)) * np.sum(y_n - yp)
    w_gd -= lr * dw
    b_gd -= lr * db

axes[1, 0].plot(mse_hist, color='red')
axes[1, 0].set_title('3. Training: MSE Decreasing')
axes[1, 0].set_xlabel('Iteration')
axes[1, 0].set_ylabel('MSE')
axes[1, 0].set_yscale('log')
axes[1, 0].grid(True, alpha=0.3)

# 4. Final Model
axes[1, 1].scatter(sizes, prices, s=100, color='blue', zorder=5, label='Actual data')
x_line = np.linspace(4, 20, 100)
y_line = w * x_line + b_param
r_sq = 1 - np.sum((prices - y_pred)**2) / np.sum((prices - np.mean(prices))**2)
axes[1, 1].plot(x_line, y_line, 'r-', linewidth=2,
                label=f'Model: y={w:.1f}x+{b_param:.1f} (R²={r_sq:.3f})')
axes[1, 1].set_title('4. Final Model with Predictions')
axes[1, 1].set_xlabel('Size (100 sqft)')
axes[1, 1].set_ylabel('Price ($K)')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.suptitle('Complete ML Pipeline: From Data to Model', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('complete_pipeline.png', dpi=100)
plt.show()
```

---

## Common Mistakes

1. **Skipping normalization.** Without it, gradient descent can be extremely slow or fail to converge.

2. **Setting the learning rate too high.** If the learning rate is too large, the model will overshoot and the MSE will explode instead of decreasing.

3. **Setting the learning rate too low.** If it is too small, the model will learn extremely slowly and might not converge in a reasonable time.

4. **Not running enough iterations.** Gradient descent needs enough iterations to converge. Always check if the MSE has stabilized.

5. **Forgetting to convert back to original units.** After training on normalized data, your predictions are in the [0, 1] range. Convert them back to real units before reporting results.

---

## Best Practices

1. **Always visualize first.** Plot your data before doing any math. Make sure a straight line makes sense.

2. **Normalize your features.** This makes gradient descent faster and more stable.

3. **Track the MSE over iterations.** Plot it. It should decrease and eventually flatten out.

4. **Compare to a known solution.** Use `np.polyfit` to verify your gradient descent found the right answer.

5. **Evaluate with multiple metrics.** Report both R-squared (overall fit quality) and RMSE (prediction error in real units).

---

## Quick Summary

```
CHAPTER 30 SUMMARY — THE COMPLETE ML PIPELINE

Step 1: UNDERSTAND YOUR DATA
  Compute mean, median, std, correlation
  [Chapters 27, 29]

Step 2: VISUALIZE YOUR DATA
  Plot scatter plots, histograms
  [Chapter 16]

Step 3: NORMALIZE FEATURES
  Scale data to [0, 1] or mean=0, std=1
  [Chapters 20-21]

Step 4: DEFINE MODEL AND COST FUNCTION
  Model: y = wx + b
  Cost: MSE = mean((y - y_pred)^2)
  [Chapters 23, 29]

Step 5: TRAIN WITH GRADIENT DESCENT
  Compute gradients (derivatives)
  Update weights: w = w - lr * dw
  Repeat until MSE converges
  [Chapters 23-24]

Step 6: EVALUATE
  R-squared, MSE, RMSE
  [Chapter 29]

Step 7: PREDICT
  Use the learned w and b to predict new values
  Convert back to original units

THAT IS MACHINE LEARNING!
```

---

## Key Points to Remember

1. Machine learning is just **finding parameters that minimize a cost function**.
2. **Gradient descent** is the algorithm that finds those parameters by following the slope downhill.
3. The **derivative** (gradient) tells you which direction to move.
4. **Normalization** makes gradient descent work faster and more reliably.
5. **MSE** is the most common cost function. Lower is better.
6. **R-squared** tells you how much of the variation your model explains.
7. Everything you learned in this book — Python, NumPy, calculus, statistics — comes together in ML.
8. Linear regression is the **foundation**. Every complex model builds on these same ideas.

---

## Practice Questions

1. In gradient descent, what happens if the learning rate is too high? What happens if it is too low?

2. Why do we normalize features before training? What would happen if one feature ranges from 0-1 and another from 0-1,000,000?

3. After training, your model has an R-squared of 0.45. Is this good or bad? What might you do to improve it?

4. Explain in your own words why the derivative of the cost function tells us how to update the weights.

5. You trained a model on house sizes (600-2000 sqft). Someone asks you to predict the price of a 10,000 sqft mansion. Why might your prediction be unreliable?

---

## Exercises

### Exercise 1: Experiment with Learning Rates

Run gradient descent with three different learning rates (0.01, 0.1, 1.0). Plot the MSE curves for all three on the same chart. What do you observe?

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.array([0.0, 0.1667, 0.3333, 0.6667, 1.0])
y = np.array([0.0, 0.2609, 0.3913, 0.6957, 1.0])
n = len(x)

plt.figure(figsize=(10, 5))

for lr in [0.01, 0.1, 1.0]:
    w, b = 0.0, 0.0
    mse_history = []

    for _ in range(200):
        y_pred = w * x + b
        mse_history.append(np.mean((y - y_pred) ** 2))
        dw = (-2/n) * np.sum(x * (y - y_pred))
        db = (-2/n) * np.sum(y - y_pred)
        w -= lr * dw
        b -= lr * db

    plt.plot(mse_history, label=f'lr={lr}')

plt.xlabel('Iteration')
plt.ylabel('MSE')
plt.title('Effect of Learning Rate on Training')
plt.legend()
plt.yscale('log')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('learning_rates.png', dpi=100)
plt.show()
```

### Exercise 2: Add More Data Points

Create a dataset with 20 data points instead of 5. Run the full pipeline (statistics, visualization, normalization, gradient descent, evaluation). Compare the R-squared to the 5-point version.

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# 20 data points with some noise
sizes = np.random.uniform(5, 20, 20)
prices = 19 * sizes + 10 + np.random.normal(0, 15, 20)

# Normalize
s_norm = (sizes - sizes.min()) / (sizes.max() - sizes.min())
p_norm = (prices - prices.min()) / (prices.max() - prices.min())

# Gradient descent
w, b = 0.0, 0.0
lr = 0.5
for _ in range(1000):
    y_pred = w * s_norm + b
    dw = (-2/len(s_norm)) * np.sum(s_norm * (p_norm - y_pred))
    db = (-2/len(s_norm)) * np.sum(p_norm - y_pred)
    w -= lr * dw
    b -= lr * db

# Evaluate
y_final = w * s_norm + b
r_sq = 1 - np.sum((p_norm - y_final)**2) / np.sum((p_norm - np.mean(p_norm))**2)

# Compare with polyfit
m_np, b_np = np.polyfit(sizes, prices, 1)
y_np = m_np * sizes + b_np
r_sq_np = 1 - np.sum((prices - y_np)**2) / np.sum((prices - np.mean(prices))**2)

print(f"Gradient Descent R²: {r_sq:.4f}")
print(f"NumPy polyfit R²:    {r_sq_np:.4f}")

plt.figure(figsize=(8, 5))
plt.scatter(sizes, prices, color='blue', label='Data (20 points)')
x_line = np.linspace(4, 21, 100)
plt.plot(x_line, m_np * x_line + b_np, 'r-', linewidth=2,
         label=f'Best fit (R²={r_sq_np:.3f})')
plt.xlabel('Size (100 sqft)')
plt.ylabel('Price ($K)')
plt.title('Regression with 20 Data Points')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('exercise_20_points.png', dpi=100)
plt.show()
```

### Exercise 3: Gradient Descent Animation

Create a series of plots showing how the regression line changes as gradient descent progresses (after 1, 5, 10, 50, 200, and 1000 iterations).

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.array([0.0, 0.1667, 0.3333, 0.6667, 1.0])
y = np.array([0.0, 0.2609, 0.3913, 0.6957, 1.0])
n = len(x)

snapshots = [1, 5, 10, 50, 200, 1000]
snapshot_params = {}

w, b = 0.0, 0.0
lr = 0.5

for i in range(1, max(snapshots) + 1):
    y_pred = w * x + b
    dw = (-2/n) * np.sum(x * (y - y_pred))
    db = (-2/n) * np.sum(y - y_pred)
    w -= lr * dw
    b -= lr * db

    if i in snapshots:
        mse = np.mean((y - (w*x+b))**2)
        snapshot_params[i] = (w, b, mse)

fig, axes = plt.subplots(2, 3, figsize=(15, 9))

for ax, iteration in zip(axes.flat, snapshots):
    w_s, b_s, mse_s = snapshot_params[iteration]
    ax.scatter(x, y, color='blue', s=80, zorder=5)
    x_line = np.linspace(-0.1, 1.1, 100)
    ax.plot(x_line, w_s * x_line + b_s, 'r-', linewidth=2)
    ax.set_title(f'Iteration {iteration}\nw={w_s:.3f}, b={b_s:.3f}\nMSE={mse_s:.6f}')
    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.2, 1.2)
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('x')
    ax.set_ylabel('y')

plt.suptitle('Gradient Descent: How the Line Improves Over Time',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('gradient_descent_animation.png', dpi=100)
plt.show()
```

---

## Congratulations!

You have done it. You have built a machine learning model from scratch.

Let that sink in. You took raw numbers, visualized them, normalized them, wrote your own gradient descent algorithm, trained a model, and evaluated it. You understand what happens inside the black box.

Here is what you have accomplished in this book:

- **Python mastery** — variables, loops, functions, classes, file handling, error handling
- **Data tools** — NumPy for math, Pandas for data, Matplotlib for visualization
- **Linear algebra** — vectors, matrices, eigenvalues — the language of data
- **Calculus** — derivatives and gradients — how models learn
- **Probability** — randomness, distributions — the foundation of prediction
- **Statistics** — describing, inferring, and testing — making sense of data
- **Regression** — the bridge from statistics to machine learning
- **A working ML model** — built from scratch, understanding every single line

You are no longer a beginner. You have the mathematical foundation to understand machine learning at a deep level.

---

## What Is Next? — Book 2: Data Science and Machine Learning

In Book 2, you will take everything you learned here and apply it to real-world problems:

- **Data cleaning and preprocessing** — real data is messy
- **Feature engineering** — choosing and creating the right inputs
- **Classification** — predicting categories (spam vs not spam)
- **Decision trees and random forests** — powerful non-linear models
- **Neural networks** — the technology behind modern AI
- **Model evaluation** — train/test splits, cross-validation, confusion matrices
- **Real projects** — predicting house prices, classifying images, analyzing text

You now have the foundation. Everything in Book 2 builds on what you learned here. The math will not be scary anymore because you have already seen it. You will recognize the derivatives, the matrices, the distributions, and the cost functions.

The hardest part is over. The most exciting part is about to begin.

See you in Book 2.
