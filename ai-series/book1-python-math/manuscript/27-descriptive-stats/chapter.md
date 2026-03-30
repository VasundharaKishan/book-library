# Chapter 27: Descriptive Statistics — Summarizing Data with Numbers

## What You Will Learn

- Measures of center: mean, median, and mode
- When to use each measure of center
- Measures of spread: range, variance, and standard deviation
- Quartiles and the interquartile range (IQR)
- Box plots for visualizing spread
- Skewness — what lopsided data looks like
- Computing all stats with NumPy and Pandas
- Using `.describe()` in Pandas for instant summaries
- Visualizing data with histograms and box plots
- Working with a real dataset example

## Why This Chapter Matters

You have data. Maybe thousands or millions of numbers. You cannot look at every single one. You need a way to **summarize** all that data into a few meaningful numbers.

That is what descriptive statistics does. It answers questions like:
- What is the "typical" value? (measures of center)
- How spread out are the values? (measures of spread)
- Is the data symmetric or lopsided? (skewness)

In machine learning, you will use these tools constantly. Before you train any model, you need to understand your data. Descriptive statistics is how you do it.

---

## 27.1 Measures of Center — Finding the "Typical" Value

### Mean (Average)

The **mean** is what most people think of as the "average." Add all the values and divide by how many there are.

```
MEAN = Sum of all values / Number of values

Example: Test scores = [85, 90, 78, 92, 88]

Mean = (85 + 90 + 78 + 92 + 88) / 5
     = 433 / 5
     = 86.6
```

**Real-life analogy:** If you split a pizza bill equally among friends, each person pays the mean amount.

### Computing the Mean with Python

```python
import numpy as np

scores = np.array([85, 90, 78, 92, 88])

# Three ways to compute the mean
mean1 = np.mean(scores)
mean2 = scores.mean()
mean3 = np.sum(scores) / len(scores)

print(f"np.mean():     {mean1}")
print(f"scores.mean(): {mean2}")
print(f"Manual:        {mean3}")
```

**Expected output:**
```
np.mean():     86.6
scores.mean(): 86.6
Manual:        86.6
```

**Line-by-line explanation:**
- `np.mean(scores)` — NumPy's built-in mean function
- `scores.mean()` — calling mean as a method on the array
- `np.sum(scores) / len(scores)` — doing it manually: sum divided by count
- All three give the same answer

### Median (Middle Value)

The **median** is the middle value when you sort the data.

```
FINDING THE MEDIAN

Step 1: Sort the data
  [78, 85, 88, 90, 92]
         ^
Step 2: Pick the middle value
  Median = 88

If even number of values:
  [78, 85, 88, 90, 92, 95]
          ^^
  Median = (88 + 90) / 2 = 89
```

**Real-life analogy:** If you line up 5 people by height, the median is the height of the person in the middle.

**Why use median instead of mean?** The median is not affected by extreme values (outliers).

```
WHY MEDIAN MATTERS

Salaries at a small company:
  $40K, $45K, $50K, $55K, $1,000K (the CEO)

  Mean:   $238K    <-- Misleading! Most people earn much less.
  Median: $50K     <-- Better representation of a "typical" salary.

The CEO's salary pulls the mean way up,
but the median stays in the middle.
```

### Computing the Median with Python

```python
import numpy as np

salaries = np.array([40000, 45000, 50000, 55000, 1000000])

print(f"Mean:   ${np.mean(salaries):,.0f}")
print(f"Median: ${np.median(salaries):,.0f}")
```

**Expected output:**
```
Mean:   $238,000
Median: $50,000
```

### Mode (Most Common Value)

The **mode** is the value that appears most often.

**Real-life analogy:** The most popular shoe size in a store.

```python
from scipy import stats
import numpy as np

shoe_sizes = np.array([8, 9, 9, 10, 10, 10, 11, 11, 12])

mode_result = stats.mode(shoe_sizes, keepdims=True)
print(f"Mode: {mode_result.mode[0]}")
print(f"Count: {mode_result.count[0]}")
print(f"Mean: {np.mean(shoe_sizes):.1f}")
print(f"Median: {np.median(shoe_sizes):.1f}")
```

**Expected output:**
```
Mode: 10
Count: 3
Mean: 10.0
Median: 10.0
```

**Line-by-line explanation:**
- `stats.mode()` — finds the most frequently occurring value
- `mode_result.mode[0]` — the value that appears most often (10)
- `mode_result.count[0]` — how many times it appears (3 times)

### When to Use Each

```
CHOOSING THE RIGHT MEASURE OF CENTER

+----------+-------------------+---------------------------+
| Measure  | Best For          | Watch Out For             |
+----------+-------------------+---------------------------+
| Mean     | Symmetric data    | Pulled by outliers        |
|          | No extreme values |                           |
+----------+-------------------+---------------------------+
| Median   | Skewed data       | Ignores actual values     |
|          | Data with outliers| (only cares about order)  |
+----------+-------------------+---------------------------+
| Mode     | Categorical data  | May not exist             |
|          | Most popular item | May have multiple modes   |
+----------+-------------------+---------------------------+

RULE OF THUMB:
  Symmetric data  -->  Use mean
  Skewed data     -->  Use median
  Categories      -->  Use mode
```

---

## 27.2 Measures of Spread — How Spread Out Is the Data?

Two classes can have the same average score but very different spreads:

```
SAME MEAN, DIFFERENT SPREAD

Class A: [85, 86, 87, 88, 89]   Mean = 87, but scores are tight
Class B: [60, 75, 87, 99, 114]  Mean = 87, but scores are spread out

Class A: |    ****    |
Class B: |*   *  *  * *|
         60         114

The mean alone does not tell the full story.
You need measures of SPREAD.
```

### Range

The simplest measure of spread. Just the difference between the largest and smallest values.

```python
import numpy as np

class_a = np.array([85, 86, 87, 88, 89])
class_b = np.array([60, 75, 87, 99, 114])

print(f"Class A — Mean: {np.mean(class_a)}, Range: {np.ptp(class_a)}")
print(f"Class B — Mean: {np.mean(class_b)}, Range: {np.ptp(class_b)}")
```

**Expected output:**
```
Class A — Mean: 87.0, Range: 4
Class B — Mean: 87.0, Range: 54
```

**Line-by-line explanation:**
- `np.ptp()` — "peak to peak" — calculates max minus min (the range)
- Same mean (87), but Class B has a much larger range (54 vs 4)

### Variance

Variance measures how far each value is from the mean, on average.

```
COMPUTING VARIANCE (step by step)

Data: [2, 4, 4, 4, 5, 5, 7, 9]
Mean: 5.0

Step 1: Subtract the mean from each value
  2-5 = -3,  4-5 = -1,  4-5 = -1,  4-5 = -1
  5-5 =  0,  5-5 =  0,  7-5 =  2,  9-5 =  4

Step 2: Square each difference
  9, 1, 1, 1, 0, 0, 4, 16

Step 3: Find the mean of the squared differences
  (9+1+1+1+0+0+4+16) / 8 = 32/8 = 4.0

Variance = 4.0
```

### Standard Deviation

The standard deviation is the **square root of the variance**. It brings the units back to the original scale.

```
Standard Deviation = sqrt(Variance)
                   = sqrt(4.0)
                   = 2.0
```

**Real-life analogy:** If test scores have a mean of 80 and a standard deviation of 5, most students scored between 75 and 85.

### Computing Variance and Standard Deviation with Python

```python
import numpy as np

data = np.array([2, 4, 4, 4, 5, 5, 7, 9])

# Step by step
mean = np.mean(data)
differences = data - mean
squared_diff = differences ** 2
variance_manual = np.mean(squared_diff)
std_manual = np.sqrt(variance_manual)

print("--- Step by Step ---")
print(f"Data: {data}")
print(f"Mean: {mean}")
print(f"Differences from mean: {differences}")
print(f"Squared differences: {squared_diff}")
print(f"Variance (manual): {variance_manual}")
print(f"Std Dev (manual): {std_manual}")

print("\n--- Using NumPy ---")
print(f"Variance: {np.var(data)}")
print(f"Std Dev: {np.std(data)}")
```

**Expected output:**
```
--- Step by Step ---
Data: [2 4 4 4 5 5 7 9]
Mean: 5.0
Differences from mean: [-3. -1. -1. -1.  0.  0.  2.  4.]
Squared differences: [9. 1. 1. 1. 0. 0. 4. 16.]
Variance (manual): 4.0
Std Dev (manual): 2.0

--- Using NumPy ---
Variance: 4.0
Std Dev: 2.0
```

---

## 27.3 Quartiles and IQR

Quartiles divide your sorted data into four equal parts.

```
QUARTILES

Sorted data: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]

                Q1        Q2        Q3
                |         |         |
  [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]
   |___25%___|___25%___|___25%___|___25%___|

  Q1 (25th percentile) = 5     <-- 25% of data is below this
  Q2 (50th percentile) = 11    <-- This is the median!
  Q3 (75th percentile) = 17    <-- 75% of data is below this

  IQR = Q3 - Q1 = 17 - 5 = 12  <-- The "middle 50%" spread
```

The **Interquartile Range (IQR)** is the range of the middle 50% of data. It is more robust than the full range because it ignores outliers.

### Computing Quartiles with Python

```python
import numpy as np

data = np.array([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])

q1 = np.percentile(data, 25)
q2 = np.percentile(data, 50)  # This is the median
q3 = np.percentile(data, 75)
iqr = q3 - q1

print(f"Q1 (25th percentile): {q1}")
print(f"Q2 (50th percentile): {q2}  (median)")
print(f"Q3 (75th percentile): {q3}")
print(f"IQR (Q3 - Q1): {iqr}")
print(f"Min: {np.min(data)}")
print(f"Max: {np.max(data)}")
```

**Expected output:**
```
Q1 (25th percentile): 5.0
Q2 (50th percentile): 11.0  (median)
Q3 (75th percentile): 17.0
IQR (Q3 - Q1): 12.0
Min: 1
Max: 21
```

---

## 27.4 Box Plots — Visualizing the Spread

A box plot shows all five summary numbers in one picture: min, Q1, median, Q3, max.

```
BOX PLOT ANATOMY

                          Outlier
                            o
    |-----[=========|=========]-----|
   Min    Q1      Median     Q3    Max
          |____IQR____|

  The box = middle 50% of data (Q1 to Q3)
  The line in the box = median
  The whiskers = extend to min/max (or 1.5*IQR)
  Dots beyond whiskers = outliers
```

### Creating Box Plots with Python

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Create three datasets with different spreads
class_a = np.random.normal(loc=75, scale=5, size=100)   # tight scores
class_b = np.random.normal(loc=75, scale=15, size=100)  # spread out
class_c = np.append(np.random.normal(75, 8, 95), [20, 25, 130, 135, 140])  # with outliers

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Box plots side by side
axes[0].boxplot([class_a, class_b, class_c],
                labels=['Class A\n(tight)', 'Class B\n(spread)', 'Class C\n(outliers)'])
axes[0].set_title('Box Plots: Comparing Three Classes')
axes[0].set_ylabel('Score')
axes[0].grid(True, alpha=0.3)

# Histograms for comparison
axes[1].hist(class_a, bins=20, alpha=0.5, label='Class A (tight)', color='blue')
axes[1].hist(class_b, bins=20, alpha=0.5, label='Class B (spread)', color='red')
axes[1].hist(class_c, bins=20, alpha=0.5, label='Class C (outliers)', color='green')
axes[1].set_title('Histograms: Same Three Classes')
axes[1].set_xlabel('Score')
axes[1].set_ylabel('Count')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('boxplots_vs_histograms.png', dpi=100)
plt.show()
```

**Line-by-line explanation:**
- `np.random.normal(loc=75, scale=5, size=100)` — 100 scores with mean 75, tight spread (std=5)
- `np.random.normal(loc=75, scale=15, size=100)` — same mean, but much wider spread (std=15)
- `np.append(...)` — Class C has outliers (scores of 20, 25, 130, 135, 140)
- `axes[0].boxplot(...)` — creates box plots; outliers appear as dots beyond the whiskers

---

## 27.5 Skewness — Lopsided Data

Not all data is symmetric. Sometimes data leans to one side. This is called **skewness**.

```
TYPES OF SKEWNESS

Left-skewed (negative)    Symmetric (zero)      Right-skewed (positive)
       ___                    ___                      ___
     _/   |                  / \                     |   \_
   _/     |                 /   \                    |     \_
  /       |                /     \                   |       \
 /________|               /       \                  |________\

  Long tail              No tail                  Long tail
  to the LEFT            (balanced)               to the RIGHT

  Example:               Example:                Example:
  Age at retirement      Heights                  Income
  Easy test scores       IQ scores                House prices
```

When data is skewed:
- Right-skewed: mean > median (mean gets pulled toward the tail)
- Left-skewed: mean < median
- Symmetric: mean is approximately equal to median

### Computing Skewness with Python

```python
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

np.random.seed(42)

# Create three distributions
symmetric = np.random.normal(50, 10, 10000)       # symmetric
right_skewed = np.random.exponential(10, 10000)    # right-skewed
left_skewed = 100 - np.random.exponential(10, 10000)  # left-skewed

# Compute skewness
print("--- Skewness Values ---")
print(f"Symmetric:    {stats.skew(symmetric):.3f}   (close to 0)")
print(f"Right-skewed: {stats.skew(right_skewed):.3f}  (positive)")
print(f"Left-skewed:  {stats.skew(left_skewed):.3f} (negative)")

print("\n--- Mean vs Median ---")
print(f"Symmetric    — Mean: {np.mean(symmetric):.1f}, Median: {np.median(symmetric):.1f}")
print(f"Right-skewed — Mean: {np.mean(right_skewed):.1f}, Median: {np.median(right_skewed):.1f}")
print(f"Left-skewed  — Mean: {np.mean(left_skewed):.1f}, Median: {np.median(left_skewed):.1f}")

# Plot all three
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].hist(left_skewed, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
axes[0].set_title(f'Left-Skewed\nskew={stats.skew(left_skewed):.2f}')
axes[0].axvline(np.mean(left_skewed), color='red', linestyle='--', label='Mean')
axes[0].axvline(np.median(left_skewed), color='green', linestyle='--', label='Median')
axes[0].legend()

axes[1].hist(symmetric, bins=50, color='salmon', edgecolor='black', alpha=0.7)
axes[1].set_title(f'Symmetric\nskew={stats.skew(symmetric):.2f}')
axes[1].axvline(np.mean(symmetric), color='red', linestyle='--', label='Mean')
axes[1].axvline(np.median(symmetric), color='green', linestyle='--', label='Median')
axes[1].legend()

axes[2].hist(right_skewed, bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
axes[2].set_title(f'Right-Skewed\nskew={stats.skew(right_skewed):.2f}')
axes[2].axvline(np.mean(right_skewed), color='red', linestyle='--', label='Mean')
axes[2].axvline(np.median(right_skewed), color='green', linestyle='--', label='Median')
axes[2].legend()

for ax in axes:
    ax.set_xlabel('Value')
    ax.set_ylabel('Count')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('skewness_comparison.png', dpi=100)
plt.show()
```

**Expected output:**
```
--- Skewness Values ---
Symmetric:    0.003   (close to 0)
Right-skewed: 1.985  (positive)
Left-skewed:  -1.985 (negative)

--- Mean vs Median ---
Symmetric    — Mean: 50.0, Median: 50.0
Right-skewed — Mean: 10.0, Median: 6.9
Left-skewed  — Mean: 90.0, Median: 93.1
```

---

## 27.6 Computing All Stats with Pandas — The `.describe()` Method

Pandas has a magic method called `.describe()` that computes everything at once.

```python
import pandas as pd
import numpy as np

np.random.seed(42)

# Create a dataset of student exam scores
data = {
    'Math':    np.random.normal(72, 12, 200).round(1),
    'Science': np.random.normal(78, 8, 200).round(1),
    'English': np.random.normal(68, 15, 200).round(1)
}

df = pd.DataFrame(data)

# The magic .describe() method
print(df.describe().round(2))
```

**Expected output:**
```
         Math  Science  English
count  200.00   200.00   200.00
mean    72.03    78.26    67.64
std     11.63     7.83    14.80
min     38.30    56.60    24.80
25%     64.15    73.18    57.83
50%     71.95    78.15    67.55
75%     79.90    83.15    77.80
max    104.00    99.50   106.00
```

**Line-by-line explanation:**
- `count` — number of non-missing values
- `mean` — the average
- `std` — the standard deviation
- `min` — the smallest value
- `25%` — Q1 (first quartile)
- `50%` — the median (Q2)
- `75%` — Q3 (third quartile)
- `max` — the largest value

### Adding More Statistics

```python
import pandas as pd
import numpy as np
from scipy import stats

np.random.seed(42)

data = np.random.normal(72, 12, 200).round(1)
df = pd.DataFrame({'Math': data})

print("--- Complete Statistics ---")
print(f"Count:    {len(df)}")
print(f"Mean:     {df['Math'].mean():.2f}")
print(f"Median:   {df['Math'].median():.2f}")
print(f"Mode:     {df['Math'].mode().values[0]}")
print(f"Std Dev:  {df['Math'].std():.2f}")
print(f"Variance: {df['Math'].var():.2f}")
print(f"Range:    {df['Math'].max() - df['Math'].min():.2f}")
print(f"IQR:      {df['Math'].quantile(0.75) - df['Math'].quantile(0.25):.2f}")
print(f"Skewness: {df['Math'].skew():.3f}")
print(f"Kurtosis: {df['Math'].kurtosis():.3f}")
```

**Expected output:**
```
--- Complete Statistics ---
Count:    200
Mean:     72.03
Median:   71.95
Mode:     62.8
Std Dev:  11.66
Variance: 135.96
Range:    65.70
IQR:      15.75
Skewness: 0.054
Kurtosis: -0.048
```

---

## 27.7 Real Dataset Example — Analyzing Employee Data

Let us put everything together with a realistic dataset.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Create a realistic employee dataset
n = 500
departments = np.random.choice(['Engineering', 'Marketing', 'Sales', 'HR'], n,
                                p=[0.35, 0.25, 0.25, 0.15])
base_salaries = {
    'Engineering': (95000, 20000),
    'Marketing': (72000, 15000),
    'Sales': (65000, 18000),
    'HR': (68000, 12000)
}

salaries = []
for dept in departments:
    mean, std = base_salaries[dept]
    salaries.append(max(35000, np.random.normal(mean, std)))

experience = np.random.exponential(5, n).round(1)
experience = np.clip(experience, 0.5, 30)

df = pd.DataFrame({
    'Department': departments,
    'Salary': np.array(salaries).round(0),
    'Experience_Years': experience
})

# Overall summary
print("=== EMPLOYEE DATASET SUMMARY ===")
print(f"Total employees: {len(df)}")
print()
print(df.describe().round(2))

# Statistics by department
print("\n=== SALARY BY DEPARTMENT ===")
dept_stats = df.groupby('Department')['Salary'].agg(['mean', 'median', 'std', 'count'])
print(dept_stats.round(0))

# Detect skewness
print(f"\n=== SKEWNESS ===")
print(f"Salary skewness: {df['Salary'].skew():.3f}")
print(f"Experience skewness: {df['Experience_Years'].skew():.3f}")

if df['Salary'].skew() > 0.5:
    print("Salary is right-skewed (some high earners pull the mean up)")
    print(f"  Mean salary:   ${df['Salary'].mean():,.0f}")
    print(f"  Median salary: ${df['Salary'].median():,.0f}")
    print("  --> Use MEDIAN for 'typical' salary")
```

**Expected output:**
```
=== EMPLOYEE DATASET SUMMARY ===
Total employees: 500

          Salary  Experience_Years
count     500.00            500.00
mean    78844.00              4.94
std     20912.00              4.40
min     35000.00              0.50
25%     64178.00              1.80
50%     76498.00              3.60
75%     93536.00              6.70
max    149498.00             27.50

=== SALARY BY DEPARTMENT ===
               mean  median      std  count
Department
Engineering   95185   94675  19671.0    173
HR            67543   67276  11637.0     79
Marketing     72155   72217  14620.0    115
Sales         65216   65192  17558.0    133

=== SKEWNESS ===
Salary skewness: 0.307
Experience skewness: 1.523
```

### Visualizing the Employee Data

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Salary histogram
axes[0, 0].hist(df['Salary'], bins=30, edgecolor='black', alpha=0.7, color='skyblue')
axes[0, 0].axvline(df['Salary'].mean(), color='red', linestyle='--', label=f"Mean: ${df['Salary'].mean():,.0f}")
axes[0, 0].axvline(df['Salary'].median(), color='green', linestyle='--', label=f"Median: ${df['Salary'].median():,.0f}")
axes[0, 0].set_title('Salary Distribution')
axes[0, 0].set_xlabel('Salary ($)')
axes[0, 0].legend()

# 2. Box plot by department
dept_data = [df[df['Department']==d]['Salary'] for d in ['Engineering','Marketing','Sales','HR']]
axes[0, 1].boxplot(dept_data, labels=['Eng', 'Mkt', 'Sales', 'HR'])
axes[0, 1].set_title('Salary by Department')
axes[0, 1].set_ylabel('Salary ($)')

# 3. Experience histogram
axes[1, 0].hist(df['Experience_Years'], bins=30, edgecolor='black', alpha=0.7, color='salmon')
axes[1, 0].set_title('Experience Distribution (Right-Skewed)')
axes[1, 0].set_xlabel('Years of Experience')

# 4. Experience box plot
axes[1, 1].boxplot(df['Experience_Years'], vert=True)
axes[1, 1].set_title('Experience Box Plot')
axes[1, 1].set_ylabel('Years')

for ax in axes.flat:
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('employee_data_analysis.png', dpi=100)
plt.show()
```

---

## Common Mistakes

1. **Using the mean for skewed data.** When data has outliers or is skewed, the median is a better measure of center.

2. **Confusing variance and standard deviation.** Variance is in squared units. Standard deviation is the square root of variance, bringing it back to original units.

3. **Ignoring the shape of data.** Always plot a histogram or box plot before computing statistics. Numbers alone can be misleading.

4. **Forgetting `ddof=1` for sample statistics.** NumPy defaults to population variance (`ddof=0`). Pandas defaults to sample variance (`ddof=1`). Be aware of the difference when comparing results.

5. **Reporting statistics without context.** Saying "the standard deviation is 5" means nothing without knowing the scale. A std of 5 is small for salaries but huge for GPAs.

---

## Best Practices

1. **Always start with `.describe()`** to get a quick overview of your data.

2. **Plot before you compute.** A histogram shows the shape. A box plot shows outliers. Look at both.

3. **Report both mean and median** for skewed data, so readers can judge for themselves.

4. **Use the IQR** instead of the range when outliers are present. It gives a more honest picture of spread.

5. **Check skewness** before choosing your analysis method. Many ML algorithms assume symmetric data.

---

## Quick Summary

```
CHAPTER 27 SUMMARY

MEASURES OF CENTER:
  Mean   = sum / count         (sensitive to outliers)
  Median = middle value        (robust to outliers)
  Mode   = most frequent value (for categories)

MEASURES OF SPREAD:
  Range    = max - min                    (simplest)
  Variance = mean of squared differences  (in squared units)
  Std Dev  = sqrt(variance)               (in original units)
  IQR      = Q3 - Q1                      (robust to outliers)

SKEWNESS:
  Right-skewed: long tail to the right, mean > median
  Left-skewed:  long tail to the left,  mean < median
  Symmetric:    mean ≈ median, skewness ≈ 0

PYTHON TOOLS:
  np.mean(), np.median(), np.std(), np.var()
  np.percentile(data, [25, 50, 75])
  df.describe()  — all stats at once!
  stats.mode(), stats.skew()
```

---

## Key Points to Remember

1. The **mean** is the average. It is pulled by outliers.
2. The **median** is the middle value. It is robust to outliers.
3. The **mode** is the most frequent value. Best for categorical data.
4. **Variance** measures spread in squared units. **Standard deviation** is its square root.
5. **Quartiles** divide data into four equal parts. The **IQR** is Q3 minus Q1.
6. **Box plots** show the five-number summary (min, Q1, median, Q3, max) and outliers.
7. **Skewness** tells you if data is lopsided. Right-skewed means a long tail to the right.
8. Pandas `.describe()` gives you count, mean, std, min, Q1, median, Q3, and max in one call.

---

## Practice Questions

1. A dataset of house prices has a mean of $450,000 and a median of $320,000. Is this data right-skewed or left-skewed? Which measure better represents a "typical" house price?

2. Two datasets have the same mean of 50. Dataset A has a standard deviation of 2 and Dataset B has a standard deviation of 15. Describe how these datasets look different.

3. What is the IQR of this dataset: [10, 20, 30, 40, 50, 60, 70, 80, 90]? What does the IQR tell you?

4. Explain why you might prefer the median over the mean when analyzing income data in a country.

5. You run `df.describe()` and see that the 25th percentile is 40 and the 75th percentile is 60. What is the IQR? What does this tell you about where most of the data lies?

---

## Exercises

### Exercise 1: Analyze Test Scores

Create a dataset of 300 test scores from a normal distribution (mean=70, std=12). Compute all descriptive statistics and create both a histogram and a box plot.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)

# Generate test scores
scores = np.random.normal(loc=70, scale=12, size=300).round(1)
scores = np.clip(scores, 0, 100)  # Keep scores between 0 and 100

df = pd.DataFrame({'Score': scores})

# Print all statistics
print("=== Test Score Statistics ===")
print(df.describe().round(2))
print(f"\nSkewness: {df['Score'].skew():.3f}")
print(f"IQR: {df['Score'].quantile(0.75) - df['Score'].quantile(0.25):.2f}")

# Create visualizations
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].hist(scores, bins=25, edgecolor='black', alpha=0.7, color='skyblue')
axes[0].axvline(np.mean(scores), color='red', linestyle='--', label=f'Mean: {np.mean(scores):.1f}')
axes[0].axvline(np.median(scores), color='green', linestyle='--', label=f'Median: {np.median(scores):.1f}')
axes[0].set_title('Test Score Distribution')
axes[0].set_xlabel('Score')
axes[0].set_ylabel('Count')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].boxplot(scores, vert=True)
axes[1].set_title('Test Score Box Plot')
axes[1].set_ylabel('Score')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('test_scores_analysis.png', dpi=100)
plt.show()
```

### Exercise 2: Compare Two Groups

Create two groups: "Before Training" (mean=60, std=10) and "After Training" (mean=75, std=8). Compare their statistics and visualize with side-by-side box plots.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.random.seed(42)

before = np.random.normal(60, 10, 150).round(1)
after = np.random.normal(75, 8, 150).round(1)

df = pd.DataFrame({'Before Training': before, 'After Training': after})

print("=== Comparison ===")
print(df.describe().round(2))
print(f"\nImprovement in mean: {np.mean(after) - np.mean(before):.2f} points")
print(f"Spread reduced (std): {np.std(before):.2f} -> {np.std(after):.2f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].boxplot([before, after], labels=['Before', 'After'])
axes[0].set_title('Before vs After Training')
axes[0].set_ylabel('Score')
axes[0].grid(True, alpha=0.3)

axes[1].hist(before, bins=20, alpha=0.5, label='Before', color='red')
axes[1].hist(after, bins=20, alpha=0.5, label='After', color='green')
axes[1].set_title('Score Distribution Comparison')
axes[1].set_xlabel('Score')
axes[1].set_ylabel('Count')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('before_after_comparison.png', dpi=100)
plt.show()
```

### Exercise 3: Detect and Handle Outliers

Create data with outliers. Use the IQR method to identify them. Show the data before and after removing outliers.

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Normal data with some outliers added
normal_data = np.random.normal(50, 10, 200)
outliers = np.array([120, 130, -30, -40, 150])
data_with_outliers = np.concatenate([normal_data, outliers])

# IQR method to detect outliers
q1 = np.percentile(data_with_outliers, 25)
q3 = np.percentile(data_with_outliers, 75)
iqr = q3 - q1
lower_fence = q1 - 1.5 * iqr
upper_fence = q3 + 1.5 * iqr

outlier_mask = (data_with_outliers < lower_fence) | (data_with_outliers > upper_fence)
clean_data = data_with_outliers[~outlier_mask]

print(f"Original data points: {len(data_with_outliers)}")
print(f"Outliers found: {np.sum(outlier_mask)}")
print(f"Clean data points: {len(clean_data)}")
print(f"Outlier values: {data_with_outliers[outlier_mask].round(1)}")
print(f"\nBefore removing outliers:")
print(f"  Mean: {np.mean(data_with_outliers):.2f}, Std: {np.std(data_with_outliers):.2f}")
print(f"After removing outliers:")
print(f"  Mean: {np.mean(clean_data):.2f}, Std: {np.std(clean_data):.2f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].boxplot(data_with_outliers)
axes[0].set_title(f'With Outliers (n={len(data_with_outliers)})')
axes[0].set_ylabel('Value')

axes[1].boxplot(clean_data)
axes[1].set_title(f'After Removing Outliers (n={len(clean_data)})')
axes[1].set_ylabel('Value')

for ax in axes:
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outlier_detection.png', dpi=100)
plt.show()
```

---

## What Is Next?

You can now summarize any dataset with numbers and pictures. But descriptive statistics only tells you about the data you **have**. What about the data you do **not** have?

In the next chapter, you will learn **inferential statistics** — the art of drawing conclusions about a whole population from just a sample. You will learn about confidence intervals, hypothesis testing, and p-values. These are the tools scientists use to decide if a result is real or just luck.
