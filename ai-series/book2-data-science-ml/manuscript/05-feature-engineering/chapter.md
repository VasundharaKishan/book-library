# Chapter 5: Feature Engineering

## What You Will Learn

In this chapter, you will learn:

- What features are and why they matter
- How to create new features from existing ones
- How to extract useful information from dates
- How to bin continuous variables into groups
- How to create interaction features
- How to extract features from text
- How to apply log transformation for skewed data
- How to select the most important features

## Why This Chapter Matters

Imagine two chefs have the same ingredients. One chef makes a simple sandwich. The other chef combines those same ingredients into a gourmet meal. The difference is not the ingredients. It is how they are used.

Feature engineering is the same idea for machine learning. You take your raw data (the ingredients) and transform it into features (the meal) that help your model learn better.

A good feature can improve your model more than choosing a better algorithm. Data scientists often say:

> "Better features beat better algorithms."

This chapter teaches you the most common and effective feature engineering techniques. By the end, you will know how to create features that make your models significantly better.

---

## What Are Features?

> **Feature:** A column in your dataset that the model uses to make predictions. Features are the input variables. They are what the model "sees" and learns from.

Think of features as the questions on a job application form. Each question (column) gives the employer (model) information to make a hiring decision (prediction).

```
+------------------------------------------------------------------+
|              RAW DATA vs FEATURES                                 |
|                                                                   |
|   Raw Data:                                                       |
|   name="Alice", birthdate="1995-03-15", height_cm=165,           |
|   weight_kg=60                                                    |
|                                                                   |
|   Possible Features:                                              |
|   age=29, bmi=22.0, height_m=1.65, is_adult=True,               |
|   birth_month=3, birth_year=1995, birth_quarter=1                |
|                                                                   |
|   From 4 raw columns, we created 7 features!                     |
+------------------------------------------------------------------+
```

The key insight: your model only knows what you tell it. If you have a `birthdate` column but do not calculate `age`, the model cannot use age as a factor. Feature engineering is about giving your model the right information in the right form.

---

## Creating New Features from Existing Ones

The simplest form of feature engineering is combining existing columns to create new ones.

### Example: BMI from Height and Weight

```python
import pandas as pd
import numpy as np

# Sample health data
data = {
    'name': ['Alice', 'Bob', 'Carol', 'Dave', 'Eve'],
    'height_cm': [165, 180, 155, 175, 160],
    'weight_kg': [60, 85, 50, 90, 55],
    'age': [28, 35, 42, 31, 25]
}
df = pd.DataFrame(data)

# Create BMI feature
# BMI = weight_kg / (height_m ** 2)
df['height_m'] = df['height_cm'] / 100
df['bmi'] = (df['weight_kg'] / (df['height_m'] ** 2)).round(1)

# Create BMI category
def bmi_category(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'

df['bmi_category'] = df['bmi'].apply(bmi_category)

print("Health data with new features:")
print(df)
```

**Expected Output:**
```
Health data with new features:
    name  height_cm  weight_kg  age  height_m   bmi bmi_category
0  Alice        165         60   28      1.65  22.0       Normal
1    Bob        180         85   35      1.80  26.2   Overweight
2  Carol        155         50   42      1.55  20.8       Normal
3   Dave        175         90   31      1.75  29.4   Overweight
4    Eve        160         55   25      1.60  21.5       Normal
```

**Line-by-line explanation:**

- `df['height_m'] = df['height_cm'] / 100` - Convert centimeters to meters. This is needed for the BMI formula.
- `df['bmi'] = (df['weight_kg'] / (df['height_m'] ** 2)).round(1)` - Calculate BMI using the standard formula. `** 2` means "squared." `.round(1)` rounds to one decimal place.
- `df['bmi'].apply(bmi_category)` - Apply the `bmi_category` function to each BMI value. `apply()` runs a function on each row.

### Example: Total and Average from Multiple Columns

```python
# Student exam scores
data = {
    'student': ['Alice', 'Bob', 'Carol', 'Dave'],
    'math': [85, 92, 78, 95],
    'science': [90, 88, 82, 91],
    'english': [78, 85, 90, 88]
}
df = pd.DataFrame(data)

# New features
df['total_score'] = df['math'] + df['science'] + df['english']
df['average_score'] = df[['math', 'science', 'english']].mean(axis=1).round(1)
df['best_subject'] = df[['math', 'science', 'english']].idxmax(axis=1)
df['score_range'] = df[['math', 'science', 'english']].max(axis=1) - \
                    df[['math', 'science', 'english']].min(axis=1)

print("Student scores with new features:")
print(df)
```

**Expected Output:**
```
Student scores with new features:
  student  math  science  english  total_score  average_score best_subject  score_range
0   Alice    85       90       78          253           84.3      science           12
1     Bob    92       88       85          265           88.3         math            7
2   Carol    78       82       90          250           83.3      english           12
3    Dave    95       91       88          274           91.3         math            7
```

**Line-by-line explanation:**

- `df[['math', 'science', 'english']].mean(axis=1)` - Calculate the mean across columns (axis=1) for each row. `axis=0` would calculate down each column.
- `.idxmax(axis=1)` - Returns the column name with the highest value for each row.
- `score_range` - The difference between the best and worst score. A high range means the student is uneven across subjects.

---

## Extracting Features from Dates

Dates contain rich information. A single date column can be split into many useful features.

```python
import pandas as pd

# Sample order data
data = {
    'order_id': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
    'order_date': [
        '2024-01-15', '2024-02-14', '2024-03-20',
        '2024-06-15', '2024-07-04', '2024-11-29',
        '2024-12-25', '2024-09-02'
    ],
    'amount': [150, 200, 75, 300, 50, 500, 250, 180]
}
df = pd.DataFrame(data)

# Convert to datetime
df['order_date'] = pd.to_datetime(df['order_date'])

# Extract date features
df['year'] = df['order_date'].dt.year
df['month'] = df['order_date'].dt.month
df['day'] = df['order_date'].dt.day
df['day_of_week'] = df['order_date'].dt.dayofweek  # 0=Mon, 6=Sun
df['day_name'] = df['order_date'].dt.day_name()
df['quarter'] = df['order_date'].dt.quarter
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df['month_name'] = df['order_date'].dt.month_name()

# Is it a holiday season? (Nov-Dec)
df['is_holiday_season'] = df['month'].isin([11, 12]).astype(int)

print("Date features extracted:")
print(df[['order_date', 'year', 'month', 'day_name',
          'quarter', 'is_weekend', 'is_holiday_season']])
```

**Expected Output:**
```
Date features extracted:
  order_date  year  month    day_name  quarter  is_weekend  is_holiday_season
0 2024-01-15  2024      1      Monday        1           0                  0
1 2024-02-14  2024      2   Wednesday        1           0                  0
2 2024-03-20  2024      3   Wednesday        1           0                  0
3 2024-06-15  2024      6    Saturday        2           1                  0
4 2024-07-04  2024      7    Thursday        3           0                  0
5 2024-11-29  2024     11      Friday        4           0                  1
6 2024-12-25  2024     12   Wednesday        4           0                  1
7 2024-09-02  2024      9      Monday        3           0                  0
```

**Line-by-line explanation:**

- `.dt.year`, `.dt.month`, `.dt.day` - Extract year, month, and day as integers.
- `.dt.dayofweek` - Returns 0 for Monday through 6 for Sunday.
- `.dt.day_name()` - Returns the full name of the day ("Monday", "Tuesday", etc.).
- `.dt.quarter` - Returns the quarter (1-4). Q1 = Jan-Mar, Q2 = Apr-Jun, etc.
- `.isin([5, 6])` - Returns True if the value is 5 (Saturday) or 6 (Sunday).
- `.astype(int)` - Converts True/False to 1/0. Many ML algorithms prefer numbers.

### Calculating Time Differences

```python
# How many days since the order?
reference_date = pd.to_datetime('2025-01-01')
df['days_ago'] = (reference_date - df['order_date']).dt.days

print("\nDays since order:")
print(df[['order_date', 'days_ago']])
```

**Expected Output:**
```
Days since order:
  order_date  days_ago
0 2024-01-15       352
1 2024-02-14       322
2 2024-03-20       287
3 2024-06-15       200
4 2024-07-04       181
5 2024-11-29       33
6 2024-12-25       7
7 2024-09-02       121
```

```
+------------------------------------------------------------------+
|        USEFUL DATE FEATURES                                       |
|                                                                   |
|   Feature           What It Captures                              |
|   ----------------------------------------------------------------|
|   year              Long-term trends                              |
|   month             Seasonal patterns                             |
|   day_of_week       Weekly patterns (Mon=busy, Sun=slow)          |
|   is_weekend        Weekend vs weekday behavior                   |
|   quarter           Quarterly business cycles                     |
|   hour              Time-of-day patterns (if time available)      |
|   is_holiday        Holiday effects on sales/traffic              |
|   days_since_X      Recency (how recent is the event?)            |
+------------------------------------------------------------------+
```

---

## Binning Continuous Variables

Binning (also called bucketing or discretization) converts a continuous number into categories. This can help models find patterns that depend on ranges rather than exact values.

> **Binning:** Grouping continuous values into discrete categories. For example, converting exact ages (23, 37, 54) into age groups ("Young", "Middle", "Senior").

```python
import pandas as pd
import numpy as np

# Sample customer data
np.random.seed(42)
data = {
    'customer_id': range(1, 11),
    'age': [22, 35, 28, 45, 19, 55, 33, 67, 41, 29],
    'income': [25000, 55000, 38000, 72000, 18000,
               95000, 48000, 120000, 65000, 42000]
}
df = pd.DataFrame(data)

# Method 1: Equal-width bins with pd.cut()
df['age_group'] = pd.cut(df['age'],
                          bins=[0, 25, 35, 50, 100],
                          labels=['Young', 'Adult', 'Middle', 'Senior'])

# Method 2: Equal-frequency bins with pd.qcut()
df['income_quartile'] = pd.qcut(df['income'],
                                 q=4,
                                 labels=['Low', 'Medium', 'High', 'Very High'])

print("Data with binned features:")
print(df)
print()

# See the distribution of bins
print("Age group counts:")
print(df['age_group'].value_counts().sort_index())
print()
print("Income quartile counts:")
print(df['income_quartile'].value_counts().sort_index())
```

**Expected Output:**
```
Data with binned features:
   customer_id  age  income age_group income_quartile
0            1   22   25000     Young             Low
1            2   35   55000     Adult            High
2            3   28   38000     Adult          Medium
3            4   45   72000    Middle       Very High
4            5   19   18000     Young             Low
5            6   55   95000    Senior       Very High
6            7   33   48000     Adult          Medium
7            8   67  120000    Senior       Very High
8            9   41   65000    Middle            High
9           10   29   42000     Adult          Medium

Age group counts:
age_group
Young     2
Adult     4
Middle    2
Senior    2
Name: count, dtype: int64

Income quartile counts:
income_quartile
Low          2
Medium       3
High         2
Very High    3
Name: count, dtype: int64
```

**Line-by-line explanation:**

- `pd.cut(df['age'], bins=[0, 25, 35, 50, 100], labels=[...])` - Split ages into custom bins. Ages 0-25 become "Young", 26-35 become "Adult", etc. You define the bin edges.
- `pd.qcut(df['income'], q=4, labels=[...])` - Split income into 4 equal-frequency groups. Each group has roughly the same number of data points. `q=4` means quartiles (4 groups).

**When to use cut vs qcut:**

```
+------------------------------------------------------------------+
|   pd.cut()  (Equal-Width)     pd.qcut()  (Equal-Frequency)       |
|                                                                   |
|   Bins have equal range        Bins have equal count              |
|   Example: 0-25, 25-50,       Example: each bin has              |
|   50-75, 75-100                ~25% of the data                   |
|                                                                   |
|   Use when ranges matter       Use when you want balanced         |
|   (age groups, price           groups regardless of               |
|   tiers)                       the actual values                  |
+------------------------------------------------------------------+
```

---

## Interaction Features

Interaction features combine two or more features to capture relationships that neither feature captures alone.

> **Interaction Feature:** A new feature created by combining two or more existing features (usually by multiplication). It captures the combined effect of those features.

```python
import pandas as pd

# Real estate data
data = {
    'property': ['A', 'B', 'C', 'D', 'E'],
    'length_m': [10, 15, 8, 20, 12],
    'width_m': [8, 10, 6, 12, 9],
    'floors': [1, 2, 1, 3, 2],
    'bedrooms': [2, 4, 1, 6, 3],
    'bathrooms': [1, 2, 1, 3, 2],
    'age_years': [5, 20, 2, 35, 10],
    'price': [200000, 450000, 120000, 800000, 300000]
}
df = pd.DataFrame(data)

# Interaction features
df['area_sqm'] = df['length_m'] * df['width_m']
df['total_area'] = df['area_sqm'] * df['floors']
df['bed_bath_ratio'] = (df['bedrooms'] / df['bathrooms']).round(2)
df['price_per_sqm'] = (df['price'] / df['total_area']).round(0)
df['rooms_per_floor'] = ((df['bedrooms'] + df['bathrooms']) / df['floors']).round(1)

print("Properties with interaction features:")
print(df[['property', 'area_sqm', 'total_area', 'bed_bath_ratio',
          'price_per_sqm', 'rooms_per_floor']])
```

**Expected Output:**
```
Properties with interaction features:
  property  area_sqm  total_area  bed_bath_ratio  price_per_sqm  rooms_per_floor
0        A        80          80            2.00         2500.0              3.0
1        B       150         300            2.00         1500.0              3.0
2        C        48          48            1.00         2500.0              2.0
3        D       240         720            2.00         1111.0              3.0
4        E       108         216            1.50         1389.0              2.5
```

**Why interaction features matter:**

A model might not figure out that `area = length * width` on its own. By creating the `area` feature explicitly, you give the model a more useful signal. The model can now see that a 10x8 property (80 sqm) and a 20x4 property (80 sqm) have the same area, even though their length and width are very different.

---

## Text-Based Features

Text columns often contain useful information that models cannot use directly. You need to extract numeric features from text.

```python
import pandas as pd

# Product review data
data = {
    'review_id': [1, 2, 3, 4, 5],
    'review_text': [
        'Great product! Works perfectly. Highly recommend!',
        'Terrible quality. Broke after one day. Waste of money.',
        'OK product. Nothing special but does the job.',
        'AMAZING!!! Best purchase ever! Love love love it!!!!',
        'Not bad. Decent quality for the price.'
    ],
    'rating': [5, 1, 3, 5, 3]
}
df = pd.DataFrame(data)

# Text features
df['word_count'] = df['review_text'].str.split().str.len()
df['char_count'] = df['review_text'].str.len()
df['avg_word_length'] = (df['char_count'] / df['word_count']).round(1)
df['exclamation_count'] = df['review_text'].str.count('!')
df['question_count'] = df['review_text'].str.count(r'\?')
df['uppercase_count'] = df['review_text'].str.count(r'[A-Z]')
df['has_great'] = df['review_text'].str.lower().str.contains('great').astype(int)
df['has_terrible'] = df['review_text'].str.lower().str.contains('terrible').astype(int)
df['has_love'] = df['review_text'].str.lower().str.contains('love').astype(int)

print("Text features extracted:")
print(df[['review_text', 'word_count', 'exclamation_count',
          'uppercase_count', 'has_great', 'has_terrible']].to_string())
```

**Expected Output:**
```
Text features extracted:
                                           review_text  word_count  exclamation_count  uppercase_count  has_great  has_terrible
0    Great product! Works perfectly. Highly recommend!           7                  2                3          1             0
1  Terrible quality. Broke after one day. Waste of ...           9                  0                2          0             1
2       OK product. Nothing special but does the job.           8                  0                2          0             0
3  AMAZING!!! Best purchase ever! Love love love it...           8                  5                9          0             0
4              Not bad. Decent quality for the price.           7                  0                2          0             0
```

**Line-by-line explanation:**

- `.str.split().str.len()` - Split text into words, then count how many words. `split()` breaks on spaces. `len()` counts the pieces.
- `.str.len()` - Count the total number of characters (including spaces and punctuation).
- `.str.count('!')` - Count how many exclamation marks appear. More exclamation marks often means stronger emotion.
- `.str.count(r'[A-Z]')` - Count uppercase letters using a regex pattern. `[A-Z]` matches any uppercase letter.
- `.str.contains('great')` - Returns True if the word "great" appears anywhere in the text.
- `.astype(int)` - Convert True/False to 1/0 for the model.

### Creating Keyword Features

```python
# Check for positive and negative keywords
positive_words = ['great', 'amazing', 'love', 'excellent', 'best', 'perfect']
negative_words = ['terrible', 'worst', 'hate', 'awful', 'broke', 'waste']

def count_keywords(text, keywords):
    text_lower = text.lower()
    return sum(1 for word in keywords if word in text_lower)

df['positive_count'] = df['review_text'].apply(
    lambda x: count_keywords(x, positive_words)
)
df['negative_count'] = df['review_text'].apply(
    lambda x: count_keywords(x, negative_words)
)
df['sentiment_score'] = df['positive_count'] - df['negative_count']

print("\nSentiment features:")
print(df[['review_text', 'positive_count', 'negative_count',
          'sentiment_score', 'rating']].to_string())
```

**Expected Output:**
```
Sentiment features:
                                           review_text  positive_count  negative_count  sentiment_score  rating
0    Great product! Works perfectly. Highly recommend!               2               0                2       5
1  Terrible quality. Broke after one day. Waste of ...               0               3               -3       1
2       OK product. Nothing special but does the job.               0               0                0       3
3  AMAZING!!! Best purchase ever! Love love love it...               3               0                3       5
4              Not bad. Decent quality for the price.               0               0                0       3
```

Notice how `sentiment_score` aligns well with the actual `rating`. Positive reviews have positive scores. Negative reviews have negative scores.

---

## Log Transformation for Skewed Data

Some data is heavily skewed. For example, income data: most people earn moderate amounts, but a few earn millions. This skew can hurt model performance.

> **Skewed Data:** Data that is not symmetric. Right-skewed data has a long tail to the right (most values are low, a few are very high). Left-skewed data has a long tail to the left.

> **Log Transformation:** Applying the natural logarithm to values. This compresses large values and spreads out small values, making skewed data more symmetric.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Simulated income data (right-skewed)
np.random.seed(42)
incomes = np.random.exponential(scale=50000, size=1000)

df = pd.DataFrame({'income': incomes})

# Apply log transformation
df['income_log'] = np.log1p(df['income'])  # log1p = log(1 + x)

# Compare statistics
print("=== ORIGINAL INCOME ===")
print(f"Mean:   ${df['income'].mean():,.0f}")
print(f"Median: ${df['income'].median():,.0f}")
print(f"Std:    ${df['income'].std():,.0f}")
print(f"Min:    ${df['income'].min():,.0f}")
print(f"Max:    ${df['income'].max():,.0f}")
print(f"Skewness: {df['income'].skew():.2f}")

print()
print("=== LOG-TRANSFORMED INCOME ===")
print(f"Mean:   {df['income_log'].mean():.2f}")
print(f"Median: {df['income_log'].median():.2f}")
print(f"Std:    {df['income_log'].std():.2f}")
print(f"Min:    {df['income_log'].min():.2f}")
print(f"Max:    {df['income_log'].max():.2f}")
print(f"Skewness: {df['income_log'].skew():.2f}")
```

**Expected Output:**
```
=== ORIGINAL INCOME ===
Mean:   $49,379
Median: $33,858
Std:    $49,831
Min:    $117
Max:    $369,163
Skewness: 2.04

=== LOG-TRANSFORMED INCOME ===
Mean:   10.49
Median: 10.43
Std:    1.05
Min:    4.77
Max:    12.82
Skewness: -0.15
```

```python
# Visualize the difference
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(df['income'], bins=50, color='steelblue',
             edgecolor='black', alpha=0.7)
axes[0].set_title('Original Income (Skewed)', fontsize=14)
axes[0].set_xlabel('Income ($)')
axes[0].set_ylabel('Count')

axes[1].hist(df['income_log'], bins=50, color='coral',
             edgecolor='black', alpha=0.7)
axes[1].set_title('Log-Transformed Income (More Symmetric)', fontsize=14)
axes[1].set_xlabel('Log(Income)')
axes[1].set_ylabel('Count')

plt.tight_layout()
plt.savefig('log_transform.png', dpi=100, bbox_inches='tight')
plt.show()
```

**ASCII representation:**

```
Original (Skewed)                Log-Transformed (Symmetric)
Count                            Count
  |                                |        ___
  |___                             |      _|   |_
  |   |__                          |    _|       |_
  |      |____                     |  _|           |_
  |           |________            | |               |___
  +----------------------->       +----------------------->
  $0    $100K   $300K              4    8    10    12
  (Long tail to the right)        (More bell-shaped)
```

**Line-by-line explanation:**

- `np.log1p(df['income'])` - Applies `log(1 + x)`. We use `log1p` instead of `log` because `log(0)` is undefined. Adding 1 avoids this problem.
- **Skewness** measures asymmetry. A skewness of 0 means perfectly symmetric. Above 1 or below -1 means heavily skewed. The original income has skewness of 2.04 (heavily right-skewed). After log transformation, it drops to about -0.15 (nearly symmetric).

**When to use log transformation:**
- When data is right-skewed (long tail to the right)
- Common for: income, prices, population, website traffic, word frequencies
- Do NOT use when data has zero or negative values (use `log1p` for zeros)

---

## Feature Selection Basics

Not all features are useful. Some are irrelevant. Some are redundant. Too many features can actually hurt your model (this is called the "curse of dimensionality").

> **Feature Selection:** The process of choosing the most important features and removing the rest. Fewer, better features often lead to better models.

### Method 1: Correlation with Target

Features that strongly correlate with the target are likely useful. Features with no correlation are likely noise.

```python
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris

# Load iris dataset
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['species'] = iris.target

# Calculate correlation with target
correlations = df.corr()['species'].drop('species')
correlations_abs = correlations.abs().sort_values(ascending=False)

print("=== CORRELATION WITH TARGET (species) ===")
print("(Higher absolute value = more useful feature)")
print()
for feature, corr in correlations_abs.items():
    bar = '#' * int(corr * 40)
    print(f"  {feature:<25} {corr:.3f}  {bar}")
```

**Expected Output:**
```
=== CORRELATION WITH TARGET (species) ===
(Higher absolute value = more useful feature)

  petal length (cm)         0.949  #####################################
  petal width (cm)          0.956  ######################################
  sepal length (cm)         0.783  ###############################
  sepal width (cm)          0.427  #################
```

Petal measurements are much more useful for predicting species than sepal measurements.

### Method 2: Variance Threshold

Features with very low variance (almost the same value for every row) carry little information.

```python
from sklearn.feature_selection import VarianceThreshold
import pandas as pd
import numpy as np

# Create sample data with a useless feature
np.random.seed(42)
data = {
    'useful_1': np.random.randn(100),
    'useful_2': np.random.randn(100) * 5,
    'useful_3': np.random.randn(100) * 10,
    'almost_constant': np.ones(100) + np.random.randn(100) * 0.001,
    'constant': np.ones(100)
}
df = pd.DataFrame(data)

print("=== VARIANCE OF EACH FEATURE ===")
for col in df.columns:
    print(f"  {col:<20} variance = {df[col].var():.6f}")
print()

# Remove features with variance below threshold
selector = VarianceThreshold(threshold=0.01)
X_selected = selector.fit_transform(df)
selected_features = df.columns[selector.get_support()]

print(f"Features before: {len(df.columns)}")
print(f"Features after:  {len(selected_features)}")
print(f"Kept: {list(selected_features)}")
print(f"Removed: {list(df.columns[~selector.get_support()])}")
```

**Expected Output:**
```
=== VARIANCE OF EACH FEATURE ===
  useful_1             0.974003
  useful_2             26.363861
  useful_3             95.457697
  almost_constant      0.000001
  constant             0.000000

Features before: 5
Features after:  3
Kept: ['useful_1', 'useful_2', 'useful_3']
Removed: ['almost_constant', 'constant']
```

**Line-by-line explanation:**

- `VarianceThreshold(threshold=0.01)` - Create a selector that removes features with variance below 0.01.
- `.fit_transform(df)` - Fit the selector to the data and return only the selected features.
- `.get_support()` - Returns a boolean array: True for kept features, False for removed ones.
- The `constant` feature (all 1s) has zero variance and is useless. The `almost_constant` feature barely changes and is also removed.

### Complete Feature Selection Example

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import pandas as pd

# Load data
iris = load_iris()
X = pd.DataFrame(iris.data, columns=iris.feature_names)
y = iris.target

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train with ALL features
model_all = DecisionTreeClassifier(random_state=42)
model_all.fit(X_train, y_train)
acc_all = accuracy_score(y_test, model_all.predict(X_test))

# Train with only petal features (the most correlated ones)
petal_features = ['petal length (cm)', 'petal width (cm)']
model_petal = DecisionTreeClassifier(random_state=42)
model_petal.fit(X_train[petal_features], y_train)
acc_petal = accuracy_score(y_test, model_petal.predict(X_test[petal_features]))

# Train with only sepal features (less correlated)
sepal_features = ['sepal length (cm)', 'sepal width (cm)']
model_sepal = DecisionTreeClassifier(random_state=42)
model_sepal.fit(X_train[sepal_features], y_train)
acc_sepal = accuracy_score(y_test, model_sepal.predict(X_test[sepal_features]))

print("=== FEATURE SELECTION COMPARISON ===")
print(f"All 4 features:     {acc_all*100:.1f}% accuracy")
print(f"Petal only (2):     {acc_petal*100:.1f}% accuracy")
print(f"Sepal only (2):     {acc_sepal*100:.1f}% accuracy")
print()
print("Fewer but better features can match or beat using all features!")
```

**Expected Output:**
```
=== FEATURE SELECTION COMPARISON ===
All 4 features:     100.0% accuracy
Petal only (2):     100.0% accuracy
Sepal only (2):      73.3% accuracy

Fewer but better features can match or beat using all features!
```

This shows that the two petal features alone are just as good as using all four features. The sepal features alone are much worse. Feature selection helps you find the features that actually matter.

---

## Putting It All Together: Complete Feature Engineering Pipeline

```python
import pandas as pd
import numpy as np

# Sample e-commerce data
data = {
    'customer_id': range(1, 9),
    'name': ['Alice', 'Bob', 'Carol', 'Dave',
             'Eve', 'Frank', 'Grace', 'Heidi'],
    'birth_date': ['1990-05-15', '1985-11-22', '1978-03-08',
                   '1995-07-30', '2000-01-12', '1982-09-05',
                   '1993-12-20', '1975-06-18'],
    'signup_date': ['2020-01-10', '2019-06-15', '2021-03-22',
                    '2022-01-05', '2023-06-01', '2018-11-30',
                    '2021-09-15', '2020-07-20'],
    'total_purchases': [15, 52, 8, 3, 1, 89, 22, 45],
    'total_spent': [450, 2600, 320, 150, 50, 5500, 1100, 2800],
    'last_review': [
        'Love this store! Great products.',
        'OK service. Nothing special.',
        'Amazing deals! Will buy again!',
        'Not great. Slow shipping.',
        'First purchase. Seems fine.',
        'Best online store! 5 stars!',
        'Good quality. Fair prices.',
        'Excellent customer service!'
    ]
}

df = pd.DataFrame(data)

print("=== ORIGINAL DATA ===")
print(df)
print(f"\nOriginal columns: {list(df.columns)}")
print(f"Original shape: {df.shape}")

# ============================================
# FEATURE ENGINEERING
# ============================================

# 1. Date features
df['birth_date'] = pd.to_datetime(df['birth_date'])
df['signup_date'] = pd.to_datetime(df['signup_date'])

reference = pd.to_datetime('2025-01-01')
df['age'] = ((reference - df['birth_date']).dt.days / 365.25).astype(int)
df['days_as_customer'] = (reference - df['signup_date']).dt.days
df['signup_month'] = df['signup_date'].dt.month
df['signup_quarter'] = df['signup_date'].dt.quarter

# 2. Computed features
df['avg_order_value'] = (df['total_spent'] / df['total_purchases']).round(2)
df['purchases_per_month'] = (
    df['total_purchases'] / (df['days_as_customer'] / 30)
).round(2)

# 3. Binning
df['age_group'] = pd.cut(df['age'], bins=[0, 30, 45, 100],
                          labels=['Young', 'Middle', 'Senior'])
df['spending_tier'] = pd.qcut(df['total_spent'], q=3,
                               labels=['Low', 'Medium', 'High'])

# 4. Text features from review
df['review_word_count'] = df['last_review'].str.split().str.len()
df['review_exclamations'] = df['last_review'].str.count('!')

positive_words = ['love', 'great', 'amazing', 'best', 'excellent', 'good']
df['positive_words'] = df['last_review'].apply(
    lambda x: sum(1 for w in positive_words if w in x.lower())
)

# 5. Log transformation (total_spent is likely skewed)
df['log_total_spent'] = np.log1p(df['total_spent']).round(2)

# ============================================
# RESULTS
# ============================================

# Select only the engineered features
new_features = ['age', 'days_as_customer', 'signup_quarter',
                'avg_order_value', 'purchases_per_month',
                'age_group', 'spending_tier',
                'review_word_count', 'review_exclamations',
                'positive_words', 'log_total_spent']

print(f"\n=== ENGINEERED FEATURES ===")
print(f"New features created: {len(new_features)}")
print(f"New shape: {df.shape}")
print()
print(df[['name'] + new_features].to_string())
```

**Expected Output:**
```
=== ORIGINAL DATA ===
   customer_id   name  birth_date signup_date  total_purchases  total_spent                       last_review
0            1  Alice  1990-05-15  2020-01-10               15          450  Love this store! Great products.
1            2    Bob  1985-11-22  2019-06-15               52         2600   OK service. Nothing special.
...

Original columns: ['customer_id', 'name', 'birth_date', 'signup_date', 'total_purchases', 'total_spent', 'last_review']
Original shape: (8, 7)

=== ENGINEERED FEATURES ===
New features created: 11
New shape: (8, 18)

    name  age  days_as_customer  signup_quarter  avg_order_value  purchases_per_month age_group spending_tier  review_word_count  review_exclamations  positive_words  log_total_spent
0  Alice   34              1817               1            30.00             0.25        Middle        Low                  6                    1               2             6.11
1    Bob   39              2026               2            50.00             0.77        Middle       High                  4                    0               0             7.86
2  Carol   46              1380               1            40.00             0.17        Senior     Medium                  5                    2               1             5.77
3   Dave   29              1092               1            50.00             0.08         Young        Low                  4                    0               1             5.02
4    Eve   24               579               2            50.00             0.05         Young        Low                  4                    0               0             3.93
5  Frank   42              2224               4            61.80             1.20        Middle       High                  5                    1               1             8.61
6  Grace   31              1204               3            50.00             0.55        Middle     Medium                  4                    0               1             7.00
7  Heidi   49              1626               3            62.22             0.83        Senior       High                  3                    1               1             7.94
```

We started with 7 raw columns and created 11 new features. The model now has much more information to work with.

---

## Common Mistakes

1. **Creating features after splitting data.** Always split data into train/test first, then engineer features. If you use test data to compute means or bins, you introduce data leakage (the model indirectly "sees" the test data during training).

2. **Over-engineering.** Creating hundreds of features is tempting but counterproductive. Most will be noise. Start with a few well-thought-out features and add more only if needed.

3. **Forgetting to handle new categories.** If you bin ages into groups, what happens when a new data point has an age outside your bin ranges? Always plan for edge cases.

4. **Using raw dates as features.** A date like "2024-03-15" is meaningless to a model. Always extract components (year, month, day of week) or calculate differences (days since event).

5. **Not checking for data leakage.** If a feature is directly derived from the target, the model will cheat. For example, using "total profit" to predict "total revenue" is circular.

6. **Ignoring domain knowledge.** The best features often come from understanding the domain. A doctor knows that BMI matters for health predictions. A real estate agent knows that location matters for prices. Talk to domain experts.

---

## Best Practices

1. **Start with domain knowledge.** Think about what factors logically affect your target. What would a human expert consider important?

2. **Create features before selecting them.** First, brainstorm and create many potential features. Then, use correlation and variance to select the best ones.

3. **Test feature impact.** Train your model with and without each new feature. If a feature does not improve performance, remove it.

4. **Use log transformation for skewed numeric features.** Check the skewness. If it is above 1 or below -1, consider a log transformation.

5. **Keep track of your features.** Document what each feature means, how it was created, and why. This helps with debugging and collaboration.

6. **Look at feature importance after training.** Many models (like Decision Trees and Random Forests) can tell you which features were most useful. Use this feedback to refine your features.

---

## Quick Summary

Feature engineering transforms raw data into features that help your model make better predictions. Key techniques include: creating new features by combining existing columns (BMI from height and weight), extracting information from dates (year, month, day of week, is weekend), binning continuous values into categories (age groups), creating interaction features (area from length and width), extracting features from text (word count, keyword presence), applying log transformation for skewed data, and selecting the best features using correlation and variance threshold. Good features often matter more than choosing the right algorithm.

---

## Key Points to Remember

- **Features** are the columns your model learns from. Better features = better models.
- **Create new features** by combining existing columns (e.g., BMI = weight / height^2).
- **Date features** to extract: year, month, day, day_of_week, is_weekend, quarter, days_since.
- **Binning** converts numbers to categories. Use `pd.cut()` for custom bins, `pd.qcut()` for equal-frequency bins.
- **Interaction features** combine columns (e.g., area = length * width).
- **Text features:** word_count, char_count, exclamation_count, keyword presence.
- **Log transformation** (`np.log1p`) makes skewed data more symmetric.
- **Feature selection:** remove features with low variance or low correlation with the target.
- **Domain knowledge** is your best tool for creating features.
- Always **engineer features after splitting** data to avoid data leakage.
- Fewer, better features often beat many mediocre ones.

---

## Practice Questions

### Question 1
You have a dataset with a `birth_date` column and a `purchase_date` column. What features could you create from these?

**Answer:** You could create: **age** at time of purchase (purchase_date - birth_date), **birth_month** and **birth_year**, **purchase_month** and **purchase_day_of_week**, **is_weekend** purchase, **quarter** of purchase, **is_birthday_month** (does birth_month equal purchase_month?), **days_since_birthday** (how recent was their last birthday when they purchased?). Each of these could reveal patterns in buying behavior.

### Question 2
When should you use `pd.cut()` vs `pd.qcut()`?

**Answer:** Use `pd.cut()` when you want bins with **equal width** (e.g., age groups 0-25, 25-50, 50-75). Each bin covers the same range but may have different numbers of data points. Use `pd.qcut()` when you want bins with **equal frequency** (e.g., each bin has 25% of the data). This is useful when you want balanced groups regardless of the actual value range.

### Question 3
Your income data has a skewness of 3.5. What should you do?

**Answer:** Apply a **log transformation** using `np.log1p(income)`. A skewness of 3.5 is heavily right-skewed, meaning most values are low but a few are very high. The log transformation compresses the large values and spreads out the small values, making the distribution more symmetric. Many ML algorithms perform better with symmetric data.

### Question 4
You created a feature called `profit` to predict `revenue`. Your model gets 99% accuracy. Should you be suspicious? Why?

**Answer:** **Yes, be very suspicious.** This is likely **data leakage**. If profit is derived from revenue (e.g., profit = revenue - costs), then the feature essentially contains the answer. The model is cheating, not learning. In production, you would not have the profit before knowing the revenue. Remove this feature and retrain.

### Question 5
Why is feature engineering often more important than algorithm selection?

**Answer:** Because the **features determine what information is available** to the model. Even the best algorithm cannot learn patterns that are not in the data. A simple algorithm with great features often outperforms a complex algorithm with poor features. Feature engineering gives the model the right information in the right form, making it easier to find patterns.

---

## Exercises

### Exercise 1: Date Feature Engineering

Create a dataset of 20 random dates over the past 3 years. For each date, extract: year, month, day, day_of_week, day_name, quarter, is_weekend, is_month_start, is_month_end, and days_until_new_year. Then create a bar chart showing the distribution of orders by day of week.

### Exercise 2: Feature Engineering for House Prices

Given this dataset, create at least 6 new features:

```python
houses = pd.DataFrame({
    'length_ft': [30, 45, 25, 60, 35],
    'width_ft': [20, 30, 18, 40, 25],
    'floors': [1, 2, 1, 3, 2],
    'bedrooms': [2, 4, 1, 5, 3],
    'bathrooms': [1, 2, 1, 3, 2],
    'year_built': [1990, 2005, 1975, 2020, 2010],
    'lot_size_sqft': [5000, 8000, 3500, 12000, 6000],
    'price': [200000, 450000, 150000, 800000, 350000]
})
```

Ideas: area, total_living_area, price_per_sqft, house_age, bed_bath_ratio, lot_coverage_ratio. Train a model with and without your new features and compare accuracy.

### Exercise 3: Text Feature Challenge

Create a dataset of 10 product descriptions (e.g., from an imaginary online store). Extract at least 8 text-based features including: word_count, sentence_count, average_word_length, uppercase_ratio, has_discount_keyword, price_mentioned, exclamation_count, and question_count. Then analyze which text features correlate with a "quality_score" you assign.

---

## What Is Next?

Congratulations! You have completed the data preparation chapters of this book. You now know how to:

- Understand what machine learning is (Chapter 1)
- Collect and load data (Chapter 2)
- Explore and visualize data (Chapter 3)
- Clean messy data (Chapter 4)
- Engineer powerful features (Chapter 5)

In the upcoming chapters, you will put all of this knowledge to work by building actual machine learning models. You will learn specific algorithms like Linear Regression, Decision Trees, and Random Forests. You will train, test, and evaluate models. And you will see how the quality of your data preparation directly impacts model performance.

The hard work you have done in these first five chapters is the foundation. Everything that follows builds on it. Data preparation is 80% of the work in data science -- and you have just mastered it.
