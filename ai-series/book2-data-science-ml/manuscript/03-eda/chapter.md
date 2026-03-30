# Chapter 3: Exploratory Data Analysis (EDA)

## What You Will Learn

In this chapter, you will learn:

- What EDA is and why it matters
- How to check data shape, types, and missing values
- How to use describe() for statistical summaries
- How to create histograms and KDE plots for distributions
- How to use scatter plots and pair plots for relationships
- How to build correlation heatmaps
- How to detect outliers with box plots
- How to use groupby for analysis
- A complete EDA walkthrough on a real dataset

## Why This Chapter Matters

Imagine driving to a new city without looking at a map. You might get there eventually, but you will waste time, get lost, and miss important landmarks.

EDA is reading the map before you drive.

Before you build any ML model, you need to understand your data. What does it look like? Are there patterns? Are there problems? Are some columns related? Are there outliers that could mess up your model?

EDA answers all these questions. It is the most important step in any data science project. Skipping EDA is the number one reason beginners build bad models.

After this chapter, you will be able to look at any dataset and quickly understand its story.

---

## What Is EDA?

> **Exploratory Data Analysis (EDA):** The process of examining and visualizing a dataset to understand its structure, patterns, relationships, and problems before building a model.

EDA has two parts:

1. **Numerical analysis:** Using statistics (mean, median, counts) to summarize the data
2. **Visual analysis:** Using plots (histograms, scatter plots, heatmaps) to see patterns

```
+------------------------------------------------------------------+
|                 THE EDA PROCESS                                   |
|                                                                   |
|  Step 1: Check structure (shape, types, missing values)           |
|  Step 2: Statistical summary (describe, value_counts)             |
|  Step 3: Distributions (histograms, KDE plots)                    |
|  Step 4: Relationships (scatter plots, pair plots)                |
|  Step 5: Correlations (heatmap)                                   |
|  Step 6: Outliers (box plots)                                     |
|  Step 7: Group analysis (groupby)                                 |
+------------------------------------------------------------------+
```

Let us go through each step with code.

---

## Step 1: Check the Structure of Your Data

The first thing you do with any new dataset is check its structure. This tells you what you are working with.

```python
import pandas as pd
import numpy as np

# Create a sample dataset (simulating Titanic-like data)
np.random.seed(42)
n = 200

data = {
    'survived': np.random.choice([0, 1], n, p=[0.6, 0.4]),
    'pclass': np.random.choice([1, 2, 3], n, p=[0.2, 0.3, 0.5]),
    'sex': np.random.choice(['male', 'female'], n, p=[0.6, 0.4]),
    'age': np.random.normal(30, 12, n).round(1),
    'fare': np.random.exponential(30, n).round(2),
    'embarked': np.random.choice(['S', 'C', 'Q'], n, p=[0.7, 0.2, 0.1]),
    'siblings_spouses': np.random.choice([0, 1, 2, 3], n, p=[0.6, 0.2, 0.15, 0.05])
}

df = pd.DataFrame(data)

# Add some missing values (realistic)
df.loc[np.random.choice(n, 15, replace=False), 'age'] = np.nan
df.loc[np.random.choice(n, 5, replace=False), 'embarked'] = np.nan

# Check 1: Shape
print("=== SHAPE ===")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")
print()

# Check 2: First few rows
print("=== FIRST 5 ROWS ===")
print(df.head())
print()

# Check 3: Data types
print("=== DATA TYPES ===")
print(df.dtypes)
print()

# Check 4: Missing values
print("=== MISSING VALUES ===")
print(df.isnull().sum())
print()

# Check 5: Missing value percentages
print("=== MISSING VALUE PERCENTAGES ===")
missing_pct = (df.isnull().sum() / len(df) * 100).round(1)
print(missing_pct)
```

**Expected Output:**
```
=== SHAPE ===
Rows: 200
Columns: 7

=== FIRST 5 ROWS ===
   survived  pclass     sex   age   fare embarked  siblings_spouses
0         0       1  female  34.8  33.57        S                 0
1         1       3    male  32.1  22.19        S                 0
2         0       3    male  28.4   6.83        S                 2
3         0       3  female  42.0  27.75        S                 0
4         0       3    male  25.2  32.91        Q                 1

=== DATA TYPES ===
survived              int64
pclass                int64
sex                  object
age                 float64
fare                float64
embarked             object
siblings_spouses      int64
dtype: object

=== MISSING VALUES ===
survived             0
pclass               0
sex                  0
age                 15
fare                 0
embarked             5
siblings_spouses     0
dtype: int64

=== MISSING VALUE PERCENTAGES ===
survived            0.0
pclass              0.0
sex                 0.0
age                 7.5
fare                0.0
embarked            2.5
siblings_spouses    0.0
dtype: float64
```

**What we learned:**
- 200 rows, 7 columns
- Two text columns (`sex`, `embarked`) and five numeric columns
- `age` has 15 missing values (7.5%)
- `embarked` has 5 missing values (2.5%)
- Everything else is complete

---

## Step 2: Statistical Summary

```python
# Numeric columns summary
print("=== STATISTICAL SUMMARY (NUMERIC) ===")
print(df.describe())
print()

# Categorical columns summary
print("=== CATEGORICAL COLUMNS ===")
print("\nSex distribution:")
print(df['sex'].value_counts())
print()

print("Embarked distribution:")
print(df['embarked'].value_counts())
print()

print("Survived distribution:")
print(df['survived'].value_counts())
print(f"\nSurvival rate: {df['survived'].mean()*100:.1f}%")
```

**Expected Output:**
```
=== STATISTICAL SUMMARY (NUMERIC) ===
         survived      pclass         age        fare  siblings_spouses
count  200.000000  200.000000  185.000000  200.000000        200.000000
mean     0.395000    2.300000   30.165946   30.567600          0.650000
std      0.490010    0.793095   12.073521   30.186442          0.884138
min      0.000000    1.000000    1.100000    0.100000          0.000000
25%      0.000000    2.000000   22.300000    9.667500          0.000000
50%      0.000000    2.000000   29.900000   21.935000          0.000000
75%      1.000000    3.000000   37.950000   41.297500          1.000000
max      1.000000    3.000000   66.600000  173.750000          3.000000

=== CATEGORICAL COLUMNS ===

Sex distribution:
sex
male      121
female     79
Name: count, dtype: int64

Embarked distribution:
embarked
S    137
C     39
Q     19
Name: count, dtype: int64

Survived distribution:
survived
0    121
1     79
Name: count, dtype: int64

Survival rate: 39.5%
```

**What we learned:**
- Average age is about 30, ranging from 1 to 67
- Fares range widely (0.10 to 173.75), with a mean of 30.57
- 60% are male, 40% female
- Most embarked from port S (68.5%)
- About 39.5% survived

---

## Step 3: Distribution Plots

Distribution plots show how values are spread out. The two most common types are histograms and KDE plots.

> **Histogram:** A bar chart that groups values into bins and shows how many values fall in each bin. It shows the shape of the data distribution.

> **KDE (Kernel Density Estimation) plot:** A smooth curve that estimates the probability distribution. Think of it as a smoothed histogram.

```python
import matplotlib.pyplot as plt

# Create a figure with multiple subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Age distribution (histogram)
axes[0, 0].hist(df['age'].dropna(), bins=20, color='steelblue',
                edgecolor='black', alpha=0.7)
axes[0, 0].set_title('Age Distribution', fontsize=14)
axes[0, 0].set_xlabel('Age')
axes[0, 0].set_ylabel('Count')

# Plot 2: Fare distribution (histogram)
axes[0, 1].hist(df['fare'], bins=20, color='coral',
                edgecolor='black', alpha=0.7)
axes[0, 1].set_title('Fare Distribution', fontsize=14)
axes[0, 1].set_xlabel('Fare')
axes[0, 1].set_ylabel('Count')

# Plot 3: Passenger class distribution (bar chart)
class_counts = df['pclass'].value_counts().sort_index()
axes[1, 0].bar(class_counts.index, class_counts.values,
               color='seagreen', edgecolor='black', alpha=0.7)
axes[1, 0].set_title('Passenger Class Distribution', fontsize=14)
axes[1, 0].set_xlabel('Class')
axes[1, 0].set_ylabel('Count')
axes[1, 0].set_xticks([1, 2, 3])

# Plot 4: Survival count (bar chart)
survived_counts = df['survived'].value_counts()
axes[1, 1].bar(['Did Not Survive', 'Survived'],
               [survived_counts[0], survived_counts[1]],
               color=['salmon', 'lightgreen'],
               edgecolor='black', alpha=0.7)
axes[1, 1].set_title('Survival Distribution', fontsize=14)
axes[1, 1].set_ylabel('Count')

plt.tight_layout()
plt.savefig('distributions.png', dpi=100, bbox_inches='tight')
plt.show()
print("Plot saved as distributions.png")
```

**What the output looks like (described in ASCII):**

```
Age Distribution               Fare Distribution
     |                              |
  30 |   ___                     60 | __
  20 | _|   |___                 40 ||  |_
  10 ||         |___             20 ||    |___
   0 +----------+------>         0 +----------+------>
     0   20  40  60                 0  50  100 150
     (bell-shaped curve)           (right-skewed: most
                                    fares are low)

Passenger Class                Survival Count
     |                              |
 100 |          ___              120 | ___
  80 |     ___ |   |              80 ||   |  ___
  40 | ___|   ||   |              40 ||   | |   |
   0 +--+---+---+-->              0 +--+-----+-->
     1   2   3                     Not   Survived
     (most in 3rd class)          (more died than survived)
```

**Line-by-line explanation:**

- `fig, axes = plt.subplots(2, 2, figsize=(12, 10))` - Create a figure with 4 subplots arranged in a 2x2 grid. `figsize` sets the width and height in inches.
- `axes[0, 0]` - The top-left subplot. `[row, column]` selects which subplot to draw on.
- `.hist(df['age'].dropna(), bins=20)` - Create a histogram of the age column. `dropna()` removes missing values. `bins=20` splits the data into 20 groups.
- `alpha=0.7` - Make bars slightly transparent (0 = invisible, 1 = solid).
- `plt.tight_layout()` - Automatically adjust spacing so plots do not overlap.
- `plt.savefig(...)` - Save the plot as an image file.

### KDE Plots

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# KDE plot for age
df['age'].dropna().plot.kde(ax=axes[0], color='steelblue', linewidth=2)
axes[0].set_title('Age Distribution (KDE)', fontsize=14)
axes[0].set_xlabel('Age')

# Histogram + KDE together for fare
axes[1].hist(df['fare'], bins=25, density=True, color='coral',
             edgecolor='black', alpha=0.5, label='Histogram')
df['fare'].plot.kde(ax=axes[1], color='darkred', linewidth=2,
                     label='KDE')
axes[1].set_title('Fare Distribution (Histogram + KDE)', fontsize=14)
axes[1].set_xlabel('Fare')
axes[1].legend()

plt.tight_layout()
plt.savefig('kde_plots.png', dpi=100, bbox_inches='tight')
plt.show()
```

**What we learned from distributions:**
- Age follows roughly a bell shape (normal distribution) centered around 30
- Fare is right-skewed (most fares are low, with a long tail of expensive fares)
- Most passengers are in 3rd class
- More passengers did not survive than survived

---

## Step 4: Relationship Plots

Relationship plots show how two variables relate to each other.

### Scatter Plots

> **Scatter Plot:** A plot where each data point is a dot. The x-axis shows one variable. The y-axis shows another. Patterns in the dots reveal relationships.

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Scatter plot: Age vs Fare
colors = ['salmon' if s == 0 else 'lightgreen' for s in df['survived']]
axes[0].scatter(df['age'], df['fare'], c=colors, alpha=0.6, edgecolors='black', linewidth=0.5)
axes[0].set_title('Age vs Fare (colored by survival)', fontsize=14)
axes[0].set_xlabel('Age')
axes[0].set_ylabel('Fare')
# Manual legend
import matplotlib.patches as mpatches
red_patch = mpatches.Patch(color='salmon', label='Did not survive')
green_patch = mpatches.Patch(color='lightgreen', label='Survived')
axes[0].legend(handles=[red_patch, green_patch])

# Scatter plot: Age vs Fare by class
for pclass in [1, 2, 3]:
    subset = df[df['pclass'] == pclass]
    axes[1].scatter(subset['age'], subset['fare'],
                    alpha=0.6, label=f'Class {pclass}', edgecolors='black', linewidth=0.5)
axes[1].set_title('Age vs Fare (colored by class)', fontsize=14)
axes[1].set_xlabel('Age')
axes[1].set_ylabel('Fare')
axes[1].legend()

plt.tight_layout()
plt.savefig('scatter_plots.png', dpi=100, bbox_inches='tight')
plt.show()
```

**ASCII representation:**

```
Age vs Fare (by survival)       Age vs Fare (by class)
Fare                            Fare
 150|         o                  150|         *
    |      o                        |      *
 100|   o    o  o                100|   *    o  *
    |  ooo  oo oo                   |  ooo  ** oo
  50| ooooooooooooo               50| ooo***ooooo+
    |ooooooooooooooo                |++++***ooooo++
   0+-------------->              0+-------------->
    0  20  40  60                   0  20  40  60
    (o=died, o=survived)           (*=1st, o=2nd, +=3rd)
```

### Pair Plots

A pair plot shows scatter plots for every pair of variables at once. It is a powerful way to see all relationships at a glance.

```python
# Using the Iris dataset for a cleaner pair plot example
from sklearn.datasets import load_iris
import matplotlib.pyplot as plt

iris = load_iris()
iris_df = pd.DataFrame(iris.data, columns=iris.feature_names)
iris_df['species'] = iris.target

# Create a simplified pair plot manually
features = iris.feature_names
n_features = len(features)

fig, axes = plt.subplots(n_features, n_features, figsize=(14, 14))

colors = {0: 'red', 1: 'green', 2: 'blue'}
species_names = {0: 'setosa', 1: 'versicolor', 2: 'virginica'}

for i in range(n_features):
    for j in range(n_features):
        ax = axes[i, j]
        if i == j:
            # Diagonal: histogram
            for species in [0, 1, 2]:
                subset = iris_df[iris_df['species'] == species]
                ax.hist(subset[features[i]], bins=15, alpha=0.5,
                        color=colors[species])
        else:
            # Off-diagonal: scatter plot
            for species in [0, 1, 2]:
                subset = iris_df[iris_df['species'] == species]
                ax.scatter(subset[features[j]], subset[features[i]],
                          alpha=0.5, color=colors[species], s=10)

        if j == 0:
            ax.set_ylabel(features[i][:10], fontsize=8)
        if i == n_features - 1:
            ax.set_xlabel(features[j][:10], fontsize=8)

plt.suptitle('Iris Dataset - Pair Plot', fontsize=16, y=1.02)
plt.tight_layout()
plt.savefig('pair_plot.png', dpi=100, bbox_inches='tight')
plt.show()
print("Pair plot saved")
```

**What pair plots reveal:**
- Setosa (red) is clearly separated from the other two species
- Petal length and petal width are strongly related (they go up together)
- Versicolor and virginica overlap in some measurements but not others

---

## Step 5: Correlation Heatmap

Correlation measures how strongly two variables are related.

> **Correlation:** A number between -1 and +1 that measures the linear relationship between two variables. +1 means they go up together perfectly. -1 means one goes up while the other goes down. 0 means no linear relationship.

```
+------------------------------------------------------------------+
|              UNDERSTANDING CORRELATION                            |
|                                                                   |
|   +1.0  Perfect positive    As X goes up, Y goes up              |
|   +0.7  Strong positive     X and Y tend to go up together       |
|   +0.3  Weak positive       Slight tendency to go up together    |
|    0.0  No correlation      No linear relationship               |
|   -0.3  Weak negative       Slight tendency: one up, one down    |
|   -0.7  Strong negative     X goes up, Y tends to go down        |
|   -1.0  Perfect negative    As X goes up, Y goes down perfectly  |
+------------------------------------------------------------------+
```

### Building a Correlation Heatmap

```python
import matplotlib.pyplot as plt
import numpy as np

# Use the Iris dataset for a clean example
from sklearn.datasets import load_iris

iris = load_iris()
iris_df = pd.DataFrame(iris.data, columns=iris.feature_names)

# Calculate correlation matrix
corr_matrix = iris_df.corr()

print("=== CORRELATION MATRIX ===")
print(corr_matrix.round(2))
print()

# Create heatmap
fig, ax = plt.subplots(figsize=(8, 6))

# Display the correlation matrix as an image
im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)

# Add colorbar
plt.colorbar(im, ax=ax, label='Correlation')

# Add labels
ax.set_xticks(range(len(corr_matrix.columns)))
ax.set_yticks(range(len(corr_matrix.columns)))
ax.set_xticklabels([c[:12] for c in corr_matrix.columns], rotation=45, ha='right')
ax.set_yticklabels([c[:12] for c in corr_matrix.columns])

# Add correlation values as text
for i in range(len(corr_matrix)):
    for j in range(len(corr_matrix)):
        text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                       ha='center', va='center', fontsize=10,
                       color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black')

ax.set_title('Iris Dataset - Correlation Heatmap', fontsize=14, pad=20)
plt.tight_layout()
plt.savefig('correlation_heatmap.png', dpi=100, bbox_inches='tight')
plt.show()
```

**Expected Correlation Matrix Output:**
```
=== CORRELATION MATRIX ===
                   sepal length  sepal width  petal length  petal width
sepal length (cm)          1.00        -0.12          0.87         0.82
sepal width (cm)          -0.12         1.00         -0.43        -0.37
petal length (cm)          0.87        -0.43          1.00         0.96
petal width (cm)           0.82        -0.37          0.96         1.00
```

**ASCII representation of the heatmap:**

```
              sepal_l  sepal_w  petal_l  petal_w
sepal_l      [ 1.00]  [-0.12]  [ 0.87]  [ 0.82]
sepal_w      [-0.12]  [ 1.00]  [-0.43]  [-0.37]
petal_l      [ 0.87]  [-0.43]  [ 1.00]  [ 0.96]
petal_w      [ 0.82]  [-0.37]  [ 0.96]  [ 1.00]

Color:  Dark Red = strong positive (+1)
        White    = no correlation (0)
        Dark Blue = strong negative (-1)
```

**What we learned:**
- Petal length and petal width are very strongly correlated (0.96). When one is big, the other is big too.
- Sepal length correlates well with petal measurements (0.87, 0.82).
- Sepal width has a weak negative correlation with petal measurements. Wider sepals tend to come with shorter petals.

---

## Step 6: Box Plots for Outlier Detection

> **Box Plot:** A plot that shows the distribution of data using five numbers: minimum, 25th percentile (Q1), median (50th percentile), 75th percentile (Q3), and maximum. Points outside the "whiskers" are outliers.

> **Outlier:** A data point that is very different from the rest. It could be a measurement error, or a genuinely unusual value.

```
+------------------------------------------------------------------+
|              ANATOMY OF A BOX PLOT                                |
|                                                                   |
|         o          <-- Outlier (above Q3 + 1.5*IQR)              |
|         |                                                         |
|     +---+---+      <-- Maximum (within whiskers)                 |
|     |       |                                                     |
|     |   +   |      <-- Q3 (75th percentile)                      |
|     |   |   |                                                     |
|     |---+---|      <-- Median (50th percentile)                  |
|     |   |   |                                                     |
|     |   +   |      <-- Q1 (25th percentile)                      |
|     |       |                                                     |
|     +---+---+      <-- Minimum (within whiskers)                 |
|         |                                                         |
|         o          <-- Outlier (below Q1 - 1.5*IQR)              |
|                                                                   |
|   IQR = Q3 - Q1 (the height of the box)                         |
+------------------------------------------------------------------+
```

### Creating Box Plots

```python
import matplotlib.pyplot as plt

# Use our passenger dataset
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Box plot 1: Age
axes[0].boxplot(df['age'].dropna(), vert=True)
axes[0].set_title('Age Distribution', fontsize=14)
axes[0].set_ylabel('Age')

# Box plot 2: Fare
axes[1].boxplot(df['fare'], vert=True)
axes[1].set_title('Fare Distribution', fontsize=14)
axes[1].set_ylabel('Fare')

# Box plot 3: Fare by passenger class
data_by_class = [df[df['pclass'] == c]['fare'] for c in [1, 2, 3]]
axes[2].boxplot(data_by_class, labels=['1st', '2nd', '3rd'])
axes[2].set_title('Fare by Class', fontsize=14)
axes[2].set_ylabel('Fare')

plt.tight_layout()
plt.savefig('box_plots.png', dpi=100, bbox_inches='tight')
plt.show()

# Detect outliers numerically using IQR method
print("=== OUTLIER DETECTION (IQR Method) ===")
for col in ['age', 'fare']:
    data = df[col].dropna()
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = data[(data < lower_bound) | (data > upper_bound)]
    print(f"\n{col}:")
    print(f"  Q1={Q1:.1f}, Q3={Q3:.1f}, IQR={IQR:.1f}")
    print(f"  Lower bound: {lower_bound:.1f}")
    print(f"  Upper bound: {upper_bound:.1f}")
    print(f"  Number of outliers: {len(outliers)}")
    if len(outliers) > 0:
        print(f"  Outlier values: {sorted(outliers.values)[:5]}...")
```

**Expected Output:**
```
=== OUTLIER DETECTION (IQR Method) ===

age:
  Q1=22.3, Q3=38.0, IQR=15.6
  Lower bound: -1.1
  Upper bound: 61.4
  Number of outliers: 3
  Outlier values: [62.1, 64.3, 66.6]...

fare:
  Q1=9.7, Q3=41.3, IQR=31.6
  Lower bound: -37.7
  Upper bound: 88.7
  Number of outliers: 12
  Outlier values: [89.2, 91.5, 95.1, 101.3, 115.8]...
```

**Line-by-line explanation:**

- `Q1 = data.quantile(0.25)` - The 25th percentile. 25% of values are below this.
- `Q3 = data.quantile(0.75)` - The 75th percentile. 75% of values are below this.
- `IQR = Q3 - Q1` - The Interquartile Range. This is the spread of the middle 50% of data.
- `lower_bound = Q1 - 1.5 * IQR` - Anything below this is an outlier.
- `upper_bound = Q3 + 1.5 * IQR` - Anything above this is an outlier.
- The `1.5 * IQR` rule is a standard statistical method for detecting outliers.

---

## Step 7: Groupby Analysis

Groupby lets you split data into groups and calculate statistics for each group. It is incredibly useful for comparing categories.

> **Groupby:** Split your data into groups based on a column, then apply a calculation (mean, count, sum) to each group separately.

```python
import pandas as pd

# Survival rate by sex
print("=== SURVIVAL RATE BY SEX ===")
survival_by_sex = df.groupby('sex')['survived'].mean()
print(survival_by_sex.round(3))
print()

# Survival rate by class
print("=== SURVIVAL RATE BY CLASS ===")
survival_by_class = df.groupby('pclass')['survived'].mean()
print(survival_by_class.round(3))
print()

# Average fare by class
print("=== AVERAGE FARE BY CLASS ===")
fare_by_class = df.groupby('pclass')['fare'].mean()
print(fare_by_class.round(2))
print()

# Multiple statistics at once
print("=== AGE STATISTICS BY CLASS ===")
age_stats = df.groupby('pclass')['age'].agg(['count', 'mean', 'min', 'max'])
print(age_stats.round(1))
print()

# Survival by sex AND class
print("=== SURVIVAL RATE BY SEX AND CLASS ===")
survival_by_both = df.groupby(['sex', 'pclass'])['survived'].mean()
print(survival_by_both.round(3))
```

**Expected Output:**
```
=== SURVIVAL RATE BY SEX ===
sex
female    0.443
male      0.364
Name: survived, dtype: float64

=== SURVIVAL RATE BY CLASS ===
pclass
1    0.474
2    0.356
3    0.383
Name: survived, dtype: float64

=== AVERAGE FARE BY CLASS ===
pclass
1    36.14
2    25.69
3    30.43
Name: fare, dtype: float64

=== AGE STATISTICS BY CLASS ===
        count  mean   min   max
pclass
1          36  31.6   6.3  55.2
2          56  30.1   1.1  59.9
3          93  29.7   3.4  66.6

=== SURVIVAL RATE BY SEX AND CLASS ===
sex     pclass
female  1         0.562
        2         0.367
        3         0.434
male    1         0.407
        2         0.349
        3         0.344
Name: survived, dtype: float64
```

**Line-by-line explanation:**

- `df.groupby('sex')['survived'].mean()` - Split data by sex, then calculate the average survival rate for each group. Since survived is 0 or 1, the mean gives us the survival percentage.
- `df.groupby('pclass')['fare'].mean()` - Split by class, calculate average fare per class.
- `.agg(['count', 'mean', 'min', 'max'])` - Apply multiple functions at once. `agg` stands for aggregate.
- `df.groupby(['sex', 'pclass'])` - Group by two columns at once. Creates subgroups.

---

## Complete EDA Walkthrough: Iris Dataset

Let us put everything together in a complete EDA on the Iris dataset.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

# ============================================
# STEP 1: LOAD AND CHECK STRUCTURE
# ============================================
print("=" * 60)
print("STEP 1: LOAD AND CHECK STRUCTURE")
print("=" * 60)

iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['species'] = iris.target
df['species_name'] = df['species'].map(
    {0: 'setosa', 1: 'versicolor', 2: 'virginica'}
)

print(f"Shape: {df.shape}")
print(f"\nFirst 5 rows:")
print(df.head())
print(f"\nData types:")
print(df.dtypes)
print(f"\nMissing values:")
print(df.isnull().sum())

# ============================================
# STEP 2: STATISTICAL SUMMARY
# ============================================
print("\n" + "=" * 60)
print("STEP 2: STATISTICAL SUMMARY")
print("=" * 60)

print("\nNumeric summary:")
print(df.describe().round(2))
print("\nSpecies distribution:")
print(df['species_name'].value_counts())

# ============================================
# STEP 3: DISTRIBUTIONS
# ============================================
print("\n" + "=" * 60)
print("STEP 3: DISTRIBUTIONS")
print("=" * 60)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
features = iris.feature_names

for idx, (ax, feature) in enumerate(zip(axes.flat, features)):
    for species in [0, 1, 2]:
        subset = df[df['species'] == species]
        ax.hist(subset[feature], bins=15, alpha=0.5,
                label=iris.target_names[species])
    ax.set_title(feature, fontsize=12)
    ax.set_xlabel('Value')
    ax.set_ylabel('Count')
    ax.legend()

plt.suptitle('Feature Distributions by Species', fontsize=16)
plt.tight_layout()
plt.savefig('iris_distributions.png', dpi=100, bbox_inches='tight')
plt.show()
print("Distribution plots saved")

# ============================================
# STEP 4: RELATIONSHIPS
# ============================================
print("\n" + "=" * 60)
print("STEP 4: RELATIONSHIPS")
print("=" * 60)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
colors = {0: 'red', 1: 'green', 2: 'blue'}

# Scatter: Sepal length vs Sepal width
for species in [0, 1, 2]:
    subset = df[df['species'] == species]
    axes[0].scatter(subset['sepal length (cm)'],
                    subset['sepal width (cm)'],
                    c=colors[species],
                    label=iris.target_names[species],
                    alpha=0.6)
axes[0].set_title('Sepal: Length vs Width')
axes[0].set_xlabel('Sepal Length (cm)')
axes[0].set_ylabel('Sepal Width (cm)')
axes[0].legend()

# Scatter: Petal length vs Petal width
for species in [0, 1, 2]:
    subset = df[df['species'] == species]
    axes[1].scatter(subset['petal length (cm)'],
                    subset['petal width (cm)'],
                    c=colors[species],
                    label=iris.target_names[species],
                    alpha=0.6)
axes[1].set_title('Petal: Length vs Width')
axes[1].set_xlabel('Petal Length (cm)')
axes[1].set_ylabel('Petal Width (cm)')
axes[1].legend()

plt.tight_layout()
plt.savefig('iris_scatter.png', dpi=100, bbox_inches='tight')
plt.show()
print("Scatter plots saved")

# ============================================
# STEP 5: CORRELATIONS
# ============================================
print("\n" + "=" * 60)
print("STEP 5: CORRELATIONS")
print("=" * 60)

numeric_df = df[iris.feature_names]
corr = numeric_df.corr()
print("\nCorrelation Matrix:")
print(corr.round(2))

# ============================================
# STEP 6: BOX PLOTS
# ============================================
print("\n" + "=" * 60)
print("STEP 6: BOX PLOTS FOR OUTLIERS")
print("=" * 60)

fig, axes = plt.subplots(1, 4, figsize=(16, 5))

for idx, feature in enumerate(iris.feature_names):
    data_by_species = [df[df['species'] == s][feature] for s in [0, 1, 2]]
    axes[idx].boxplot(data_by_species,
                      labels=['setosa', 'vers.', 'virg.'])
    axes[idx].set_title(feature[:15], fontsize=10)
    axes[idx].set_ylabel('cm')

plt.suptitle('Box Plots by Species', fontsize=14)
plt.tight_layout()
plt.savefig('iris_boxplots.png', dpi=100, bbox_inches='tight')
plt.show()
print("Box plots saved")

# ============================================
# STEP 7: GROUPBY ANALYSIS
# ============================================
print("\n" + "=" * 60)
print("STEP 7: GROUPBY ANALYSIS")
print("=" * 60)

print("\nAverage measurements by species:")
group_stats = df.groupby('species_name')[iris.feature_names].mean()
print(group_stats.round(2))

print("\n=== EDA COMPLETE ===")
print("\nKey Findings:")
print("1. Dataset has 150 flowers, 4 features, 3 species (50 each)")
print("2. No missing values")
print("3. Setosa is clearly different from the other two species")
print("4. Petal length and petal width are highly correlated (0.96)")
print("5. Petal measurements are the best for distinguishing species")
print("6. Very few outliers in this clean dataset")
```

**Expected Output (key parts):**
```
============================================================
STEP 1: LOAD AND CHECK STRUCTURE
============================================================
Shape: (150, 6)

First 5 rows:
   sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)  species species_name
0                5.1               3.5                1.4               0.2        0       setosa
1                4.9               3.0                1.4               0.2        0       setosa
2                4.7               3.2                1.3               0.2        0       setosa
...

Missing values:
sepal length (cm)    0
sepal width (cm)     0
petal length (cm)    0
petal width (cm)     0
species              0
species_name         0
dtype: int64

...

Average measurements by species:
              sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)
species_name
setosa                     5.01              3.43               1.46              0.25
versicolor                 5.94              2.77               4.26              1.33
virginica                  6.59              2.97               5.55              2.03

=== EDA COMPLETE ===

Key Findings:
1. Dataset has 150 flowers, 4 features, 3 species (50 each)
2. No missing values
3. Setosa is clearly different from the other two species
4. Petal length and petal width are highly correlated (0.96)
5. Petal measurements are the best for distinguishing species
6. Very few outliers in this clean dataset
```

---

## Common Mistakes

1. **Skipping EDA entirely.** Jumping straight to modeling is the most common beginner mistake. You miss patterns, problems, and insights that could save you hours.

2. **Not checking for missing values.** Missing values can silently break your model or produce garbage results. Always check first.

3. **Ignoring outliers.** One extreme outlier can dramatically shift your model's results. Always look at box plots and check for unusual values.

4. **Making too many plots.** EDA is about insight, not art. Focus on plots that answer questions. A simple histogram is often more useful than a fancy 3D chart.

5. **Confusing correlation with causation.** Just because two variables are correlated does not mean one causes the other. Ice cream sales and drowning are both high in summer, but ice cream does not cause drowning.

6. **Not looking at data by groups.** Averages can hide important differences between groups. Always use groupby to compare subsets.

---

## Best Practices

1. **Follow a checklist.** Go through the EDA steps in order: structure, statistics, distributions, relationships, correlations, outliers, groups.

2. **Write down findings.** As you explore, write notes about what you discover. These findings guide your model building.

3. **Use simple plots.** Histograms, scatter plots, box plots, and bar charts cover 90% of EDA needs. Master these before learning fancier visualizations.

4. **Check distributions.** Many ML algorithms work best with normally distributed data. If your data is skewed, you may need to transform it.

5. **Look at correlations.** Highly correlated features may be redundant. Weak correlations with the target may mean a feature is not useful.

6. **Always visualize by groups.** If you have categories (species, class, gender), compare distributions across groups.

---

## Quick Summary

Exploratory Data Analysis (EDA) is the process of understanding your data before building a model. It involves checking the structure (shape, types, missing values), computing statistics (mean, median, distribution), visualizing patterns (histograms, scatter plots, heatmaps), detecting outliers (box plots, IQR method), and comparing groups (groupby). EDA reveals the story in your data and guides every decision you make in the modeling process. Never skip it.

---

## Key Points to Remember

- **EDA** = understanding your data before modeling. It is like reading a map before driving.
- Always check **shape**, **dtypes**, and **missing values** first.
- **describe()** gives you mean, median, min, max, and quartiles in one command.
- **Histograms** show the distribution (shape) of a single variable.
- **Scatter plots** show the relationship between two variables.
- **Correlation** ranges from -1 to +1. Close to +1 or -1 means a strong relationship.
- **Heatmaps** visualize the entire correlation matrix at once.
- **Box plots** show the spread of data and highlight outliers.
- **Outliers** are data points far from the rest. Use the IQR method to detect them.
- **Groupby** lets you compare statistics across categories.
- Correlation does NOT equal causation.
- Write down your findings as you go.

---

## Practice Questions

### Question 1
You run `df.describe()` and notice that the `count` for one column is 450 while all other columns show 500. What does this tell you?

**Answer:** That column has **50 missing values** (500 - 450 = 50). The `count` in `describe()` shows the number of non-missing values. If it is lower than the total number of rows, there are missing values in that column.

### Question 2
You see a correlation of 0.95 between "temperature" and "ice cream sales." Does this mean higher temperatures cause more ice cream sales?

**Answer:** **Not necessarily.** A high correlation means the two variables move together, but **correlation does not prove causation**. There could be a third factor (like summer vacation) that causes both. In this case, it is reasonable that temperature does influence ice cream sales, but the correlation alone does not prove it.

### Question 3
You create a box plot and see several dots above the upper whisker. What are these dots?

**Answer:** These dots are **outliers** -- data points that fall above Q3 + 1.5 * IQR. They are unusually large values compared to the rest of the data. They could be measurement errors, data entry mistakes, or genuinely extreme values. You need to investigate each outlier to decide what to do with it.

### Question 4
You have a dataset with columns: age, income, gender, and purchased (yes/no). Which EDA plots would you create?

**Answer:**
1. **Histograms** for age and income (to see distributions)
2. **Bar chart** for gender and purchased (to see counts)
3. **Box plots** for age and income by purchased status (do buyers differ from non-buyers?)
4. **Scatter plot** for age vs income, colored by purchased
5. **Groupby** analysis: average income and age for buyers vs non-buyers, and by gender

### Question 5
What is the IQR, and how is it used to detect outliers?

**Answer:** **IQR (Interquartile Range)** = Q3 - Q1. It is the range of the middle 50% of data. To detect outliers: calculate the lower bound (Q1 - 1.5 * IQR) and upper bound (Q3 + 1.5 * IQR). Any value below the lower bound or above the upper bound is considered an outlier. This is a standard statistical method and the same method used by box plots.

---

## Exercises

### Exercise 1: EDA on the Wine Dataset

Load the Wine dataset from scikit-learn (`load_wine`). Perform a complete EDA:

1. Check shape, dtypes, and missing values
2. Run describe() and interpret the results
3. Create histograms for at least 4 features
4. Create a correlation heatmap
5. Create box plots for 3 features, grouped by wine class
6. Use groupby to find the average of each feature per class
7. Write a summary of your key findings

### Exercise 2: Outlier Investigation

Using the passenger dataset created in this chapter (or your own), write code to:

1. Detect outliers in the `fare` column using the IQR method
2. Count how many outliers there are
3. Create a box plot showing fares with and without outliers
4. Calculate the mean fare with and without outliers. How much does removing outliers change the mean?

### Exercise 3: Groupby Deep Dive

Using the passenger dataset, answer these questions using groupby:

1. What is the average age for each passenger class?
2. What is the survival rate for males vs females?
3. Which combination of sex and class has the highest survival rate?
4. What is the average fare for survivors vs non-survivors?

---

## What Is Next?

Now you can explore and understand your data. But real-world data is messy. It has missing values, duplicates, wrong data types, and outliers.

In Chapter 4, you will learn Data Cleaning. You will fix missing values, remove duplicates, correct data types, handle outliers, and clean messy strings. Remember: "garbage in, garbage out." Clean data is the foundation of every good model.
