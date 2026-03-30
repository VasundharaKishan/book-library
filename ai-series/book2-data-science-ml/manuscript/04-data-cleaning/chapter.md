# Chapter 4: Data Cleaning

## What You Will Learn

In this chapter, you will learn:

- Why clean data is essential for good models
- How to find missing values in your data
- How to handle missing values (drop, fill with mean/median/mode, forward/backward fill)
- How to find and remove duplicate rows
- How to fix incorrect data types
- How to detect and handle outliers using IQR and Z-score methods
- How to clean messy strings
- A complete before-and-after cleaning example

## Why This Chapter Matters

There is a famous saying in data science:

> "Garbage in, garbage out."

It means this: if you feed bad data to a machine learning model, you will get bad results. No matter how smart the algorithm is.

Think of it like baking a cake. You can have the best recipe in the world (the algorithm). But if you use spoiled eggs, rancid butter, and stale flour (bad data), the cake will be terrible.

Real-world data is almost always messy. It has missing values, duplicate entries, wrong data types, and outliers. Data cleaning fixes these problems.

Data scientists spend about 80% of their time cleaning data and only 20% building models. That tells you how important this chapter is.

---

## Setting Up: Our Messy Dataset

Let us create a realistically messy dataset that we will clean throughout this chapter.

```python
import pandas as pd
import numpy as np

# Create a messy dataset
data = {
    'Name': ['Alice', 'Bob', 'Carol', 'Dave', 'Eve', 'Frank',
             'Grace', 'alice', 'Bob', 'Heidi', None, 'Ivan'],
    'Age': [25, 30, np.nan, 28, 35, 150, 22, 25, 30, -5, 40, 33],
    'Salary': ['50000', '60000', '55000', 'unknown', '70000',
               '80000', '45000', '50000', '60000', '65000',
               '72000', np.nan],
    'Department': ['Sales', 'Engineering', 'Sales', 'Marketing',
                   'Engineering', 'Sales', ' Marketing ',
                   'SALES', 'Engineering', 'sales', 'HR', 'Engineering'],
    'Hire_Date': ['2020-01-15', '2019-06-20', '2021-03-10',
                  '2020/07/25', 'Jan 5, 2022', '2018-11-30',
                  '2023-02-14', '2020-01-15', '2019-06-20',
                  '2021-09-01', '2020-05-15', '2022-08-10'],
    'Email': ['alice@co.com', 'BOB@Co.Com', 'carol@co.com',
              'dave@co.com', 'eve@co.com', 'frank@co.com',
              'grace@co.com', 'alice@co.com', 'BOB@Co.Com',
              'heidi@co.com', 'kate@co.com', 'ivan@co.com']
}

df = pd.DataFrame(data)

print("=== OUR MESSY DATASET ===")
print(df)
print(f"\nShape: {df.shape}")
print(f"\nData types:\n{df.dtypes}")
```

**Expected Output:**
```
=== OUR MESSY DATASET ===
     Name  Age   Salary    Department     Hire_Date         Email
0   Alice   25    50000         Sales    2020-01-15   alice@co.com
1     Bob   30    60000   Engineering    2019-06-20    BOB@Co.Com
2   Carol  NaN    55000         Sales    2021-03-10   carol@co.com
3    Dave   28  unknown     Marketing    2020/07/25    dave@co.com
4     Eve   35    70000   Engineering   Jan 5, 2022    eve@co.com
5   Frank  150    80000         Sales    2018-11-30   frank@co.com
6   Grace   22    45000    Marketing     2023-02-14   grace@co.com
7   alice   25    50000         SALES    2020-01-15   alice@co.com
8     Bob   30    60000   Engineering    2019-06-20    BOB@Co.Com
9   Heidi   -5    65000         sales    2021-09-01   heidi@co.com
10   None   40    72000            HR    2020-05-15    kate@co.com
11   Ivan   33      NaN   Engineering    2022-08-10   ivan@co.com

Shape: (12, 6)

Data types:
Name          object
Age          float64
Salary        object
Department    object
Hire_Date     object
Email         object
dtype: object
```

**Problems in this dataset:**

```
+------------------------------------------------------------------+
|              PROBLEMS IN OUR MESSY DATA                           |
|                                                                   |
|  1. Missing values: Age (row 2), Salary (row 11), Name (row 10) |
|  2. Invalid values: Age=150 (row 5), Age=-5 (row 9)             |
|  3. Wrong data type: Salary is text, not numbers                 |
|  4. Invalid text: Salary="unknown" (row 3)                       |
|  5. Duplicates: Rows 0&7 (Alice), Rows 1&8 (Bob)                |
|  6. Inconsistent text: "Sales", "SALES", "sales"                |
|  7. Extra spaces: " Marketing " has leading/trailing spaces      |
|  8. Inconsistent dates: Different formats across rows            |
|  9. Inconsistent case: "alice" vs "Alice", "BOB@Co.Com"          |
+------------------------------------------------------------------+
```

---

## Finding Missing Values

The first step in cleaning is finding what is missing.

```python
import pandas as pd
import numpy as np

# Check for missing values
print("=== MISSING VALUES ===")
print(df.isnull().sum())
print()

# Missing value percentages
print("=== MISSING VALUE PERCENTAGES ===")
missing_pct = (df.isnull().sum() / len(df) * 100).round(1)
print(missing_pct)
print()

# See which rows have missing values
print("=== ROWS WITH MISSING VALUES ===")
missing_rows = df[df.isnull().any(axis=1)]
print(missing_rows)
```

**Expected Output:**
```
=== MISSING VALUES ===
Name          1
Age           1
Salary        1
Department    0
Hire_Date     0
Email         0
dtype: int64

=== MISSING VALUE PERCENTAGES ===
Name          8.3
Age           8.3
Salary        8.3
Department    0.0
Hire_Date     0.0
Email         0.0
dtype: float64

=== ROWS WITH MISSING VALUES ===
     Name  Age Salary Department   Hire_Date        Email
2   Carol  NaN  55000      Sales  2021-03-10  carol@co.com
10   None   40  72000         HR  2020-05-15   kate@co.com
11   Ivan   33    NaN Engineering  2022-08-10  ivan@co.com
```

**Line-by-line explanation:**

- `df.isnull()` - Returns a DataFrame of True/False. True where a value is missing (NaN or None).
- `.sum()` - Counts the True values (missing values) in each column.
- `df.isnull().any(axis=1)` - Returns True for any row that has at least one missing value. `axis=1` means "check across columns for each row."

---

## Handling Missing Values

There are several strategies for dealing with missing values:

```
+------------------------------------------------------------------+
|         STRATEGIES FOR MISSING VALUES                             |
|                                                                   |
|  Strategy            When to Use                                  |
|  ---------------------------------------------------------------- |
|  Drop rows           Very few missing rows (<5%)                  |
|  Drop column          Column has too many missing values (>50%)   |
|  Fill with mean       Numeric column, roughly symmetric           |
|  Fill with median     Numeric column, has outliers                |
|  Fill with mode       Categorical column (most common value)      |
|  Forward fill         Time series data (use previous value)       |
|  Backward fill        Time series data (use next value)           |
+------------------------------------------------------------------+
```

### Strategy 1: Drop Rows with Missing Values

```python
# Make a copy so we do not change the original
df_dropped = df.copy()

print("Before dropping:", df_dropped.shape)

# Drop all rows with ANY missing value
df_dropped_all = df.dropna()
print("After dropping all missing:", df_dropped_all.shape)

# Drop rows where a SPECIFIC column is missing
df_dropped_age = df.dropna(subset=['Age'])
print("After dropping missing Age:", df_dropped_age.shape)
```

**Expected Output:**
```
Before dropping: (12, 6)
After dropping all missing: (9, 6)
After dropping missing Age: (11, 6)
```

**When to drop rows:** Only when you have plenty of data and very few rows are missing values. If you drop too many rows, you lose important information.

### Strategy 2: Fill with Mean, Median, or Mode

```python
df_filled = df.copy()

# Fill missing Age with the median
# (median is better than mean when there are outliers)
median_age = df_filled['Age'].median()
print(f"Median age: {median_age}")
df_filled['Age'] = df_filled['Age'].fillna(median_age)

print("\nAge column after filling with median:")
print(df_filled['Age'].values)
```

**Expected Output:**
```
Median age: 29.0

Age column after filling with median:
[ 25.  30.  29.  28.  35. 150.  22.  25.  30.  -5.  40.  33.]
```

**Line-by-line explanation:**

- `df['Age'].median()` - Calculate the middle value of the Age column, ignoring NaN.
- `.fillna(median_age)` - Replace all NaN values with the median. The original non-missing values stay the same.

### Strategy 3: Fill Categorical Values with Mode

```python
df_filled2 = df.copy()

# Fill missing Name with "Unknown"
df_filled2['Name'] = df_filled2['Name'].fillna('Unknown')

print("Name column after filling:")
print(df_filled2['Name'].values)
```

**Expected Output:**
```
Name column after filling:
['Alice' 'Bob' 'Carol' 'Dave' 'Eve' 'Frank' 'Grace' 'alice' 'Bob'
 'Heidi' 'Unknown' 'Ivan']
```

### Strategy 4: Forward Fill and Backward Fill

These are useful for time series data where the previous or next value is a good estimate.

```python
# Example: temperature readings with gaps
temps = pd.Series([72, 74, np.nan, np.nan, 78, 80, np.nan, 82])
print("Original:       ", temps.values)
print("Forward fill:   ", temps.ffill().values)
print("Backward fill:  ", temps.bfill().values)
```

**Expected Output:**
```
Original:        [72. 74. nan nan 78. 80. nan 82.]
Forward fill:    [72. 74. 74. 74. 78. 80. 80. 82.]
Backward fill:   [72. 74. 78. 78. 78. 80. 82. 82.]
```

**Explanation:**
- `ffill()` (forward fill) - Fills each NaN with the last non-missing value before it. The temperature stays at 74 until we get a new reading.
- `bfill()` (backward fill) - Fills each NaN with the next non-missing value after it. The temperature jumps to 78 before we measure it.

---

## Finding and Removing Duplicates

Duplicate rows waste resources and can bias your model. A model trained on duplicate data gives too much weight to those repeated rows.

```python
# Check for duplicates
print("=== DUPLICATE CHECK ===")
print(f"Total rows: {len(df)}")
print(f"Duplicate rows: {df.duplicated().sum()}")
print()

# See the duplicate rows
print("Duplicate rows:")
print(df[df.duplicated(keep=False)])
print()

# Check duplicates based on specific columns
print("Duplicates based on Name + Email:")
dupes = df.duplicated(subset=['Name', 'Email'], keep=False)
print(df[dupes])
```

**Expected Output:**
```
=== DUPLICATE CHECK ===
Total rows: 12
Duplicate rows: 0

Duplicate rows:
Empty DataFrame

Duplicates based on Name + Email:
    Name  Age Salary   Department   Hire_Date       Email
1    Bob   30  60000  Engineering  2019-06-20  BOB@Co.Com
8    Bob   30  60000  Engineering  2019-06-20  BOB@Co.Com
```

Note: Rows 0 and 7 (Alice/alice) are not exact duplicates because the name capitalization differs. We will fix that in the string cleaning section.

```python
# Remove duplicates
df_no_dupes = df.drop_duplicates()
print(f"Before: {len(df)} rows")
print(f"After removing exact duplicates: {len(df_no_dupes)} rows")

# Remove duplicates based on specific columns
df_no_dupes2 = df.drop_duplicates(subset=['Name', 'Email'], keep='first')
print(f"After removing dupes by Name+Email: {len(df_no_dupes2)} rows")
```

**Expected Output:**
```
Before: 12 rows
After removing exact duplicates: 11 rows
After removing dupes by Name+Email: 11 rows
```

**Line-by-line explanation:**

- `df.duplicated()` - Returns True for rows that are exact copies of a previous row.
- `df.duplicated(keep=False)` - Shows ALL duplicate rows (including the first occurrence).
- `df.drop_duplicates()` - Remove duplicate rows, keeping the first occurrence.
- `keep='first'` - Keep the first occurrence and drop later ones. Use `keep='last'` to keep the last occurrence.
- `subset=['Name', 'Email']` - Only check these columns when looking for duplicates.

---

## Fixing Data Types

Sometimes columns have the wrong data type. Salary might be stored as text instead of numbers. Dates might be stored as plain strings instead of datetime objects.

### Converting Text to Numbers

```python
df_types = df.copy()

# Check current type of Salary
print("Salary dtype:", df_types['Salary'].dtype)
print("Salary values:", df_types['Salary'].values)
print()

# Problem: "unknown" is in the Salary column
# Step 1: Replace non-numeric text with NaN
df_types['Salary'] = pd.to_numeric(df_types['Salary'], errors='coerce')

print("After to_numeric:")
print("Salary dtype:", df_types['Salary'].dtype)
print("Salary values:", df_types['Salary'].values)
print()

# Step 2: Fill the NaN salary with the median
median_salary = df_types['Salary'].median()
print(f"Median salary: {median_salary}")
df_types['Salary'] = df_types['Salary'].fillna(median_salary)

print("\nFinal Salary values:", df_types['Salary'].values)
```

**Expected Output:**
```
Salary dtype: object
Salary values: ['50000' '60000' '55000' 'unknown' '70000' '80000' '45000'
                '50000' '60000' '65000' '72000' nan]

After to_numeric:
Salary dtype: float64
Salary values: [50000. 60000. 55000.   nan 70000. 80000. 45000. 50000.
                60000. 65000. 72000.   nan]

Median salary: 60000.0

Final Salary values: [50000. 60000. 55000. 60000. 70000. 80000. 45000.
                      50000. 60000. 65000. 72000. 60000.]
```

**Line-by-line explanation:**

- `pd.to_numeric(df_types['Salary'], errors='coerce')` - Try to convert each value to a number. `errors='coerce'` means: if a value cannot be converted (like "unknown"), replace it with NaN instead of throwing an error.
- After conversion, Salary is now `float64` (a number type) instead of `object` (text type).

### Converting Strings to Dates

```python
df_dates = df.copy()

print("Hire_Date dtype:", df_dates['Hire_Date'].dtype)
print("Sample values:", df_dates['Hire_Date'].values[:5])
print()

# Convert to datetime
# Pandas is smart enough to handle multiple date formats
df_dates['Hire_Date'] = pd.to_datetime(df_dates['Hire_Date'])

print("After conversion:")
print("Hire_Date dtype:", df_dates['Hire_Date'].dtype)
print("Sample values:")
print(df_dates['Hire_Date'].head())
print()

# Now we can extract parts of the date
df_dates['Hire_Year'] = df_dates['Hire_Date'].dt.year
df_dates['Hire_Month'] = df_dates['Hire_Date'].dt.month

print("Year and Month extracted:")
print(df_dates[['Hire_Date', 'Hire_Year', 'Hire_Month']].head())
```

**Expected Output:**
```
Hire_Date dtype: object
Sample values: ['2020-01-15' '2019-06-20' '2021-03-10' '2020/07/25'
                'Jan 5, 2022']

After conversion:
Hire_Date dtype: datetime64[ns]
Sample values:
0   2020-01-15
1   2019-06-20
2   2021-03-10
3   2020-07-25
4   2022-01-05
Name: Hire_Date, dtype: datetime64[ns]

Year and Month extracted:
   Hire_Date  Hire_Year  Hire_Month
0 2020-01-15       2020           1
1 2019-06-20       2019           6
2 2021-03-10       2021           3
3 2020-07-25       2020           7
4 2022-01-05       2022           1
```

**Line-by-line explanation:**

- `pd.to_datetime(df_dates['Hire_Date'])` - Convert text dates to datetime objects. Pandas automatically detects different formats ("2020-01-15", "2020/07/25", "Jan 5, 2022").
- `.dt.year` - Extract the year from a datetime column. The `.dt` accessor gives you access to date components.
- `.dt.month` - Extract the month (1-12).

---

## Handling Outliers

Outliers are extreme values that differ significantly from the rest of the data. They can distort your model's results.

### Method 1: IQR Method

```python
df_outliers = df.copy()
# First fix the Age column to be numeric
df_outliers['Age'] = pd.to_numeric(df_outliers['Age'], errors='coerce')

print("Age values:", sorted(df_outliers['Age'].dropna().values))
print()

# IQR method
Q1 = df_outliers['Age'].quantile(0.25)
Q3 = df_outliers['Age'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print(f"Q1: {Q1}")
print(f"Q3: {Q3}")
print(f"IQR: {IQR}")
print(f"Lower bound: {lower_bound}")
print(f"Upper bound: {upper_bound}")
print()

# Find outliers
outliers = df_outliers[
    (df_outliers['Age'] < lower_bound) |
    (df_outliers['Age'] > upper_bound)
]
print(f"Outliers found: {len(outliers)}")
print(outliers[['Name', 'Age']])
print()

# Option 1: Remove outliers
df_no_outliers = df_outliers[
    (df_outliers['Age'] >= lower_bound) &
    (df_outliers['Age'] <= upper_bound)
]
print(f"Rows before: {len(df_outliers)}")
print(f"Rows after removing outliers: {len(df_no_outliers)}")
print()

# Option 2: Cap outliers (clip to bounds)
df_capped = df_outliers.copy()
df_capped['Age'] = df_capped['Age'].clip(lower=lower_bound, upper=upper_bound)
print("After capping:")
print("Age values:", sorted(df_capped['Age'].dropna().values))
```

**Expected Output:**
```
Age values: [-5.0, 22.0, 25.0, 25.0, 28.0, 30.0, 30.0, 33.0, 35.0, 40.0, 150.0]

Q1: 25.0
Q3: 33.5
IQR: 8.5
Lower bound: 12.25
Upper bound: 46.25

Outliers found: 2
    Name    Age
5  Frank  150.0
9  Heidi   -5.0

Rows before: 12
Rows after removing outliers: 10

After capping:
Age values: [12.25, 22.0, 25.0, 25.0, 28.0, 29.0, 30.0, 30.0, 33.0, 35.0, 40.0, 46.25]
```

### Method 2: Z-Score Method

> **Z-Score:** How many standard deviations a value is from the mean. A Z-score of 0 means the value equals the mean. A Z-score of 3 means the value is 3 standard deviations above the mean.

```python
from scipy import stats
import numpy as np

df_zscore = df.copy()
df_zscore['Age'] = pd.to_numeric(df_zscore['Age'], errors='coerce')

# Calculate Z-scores
age_values = df_zscore['Age'].dropna()
z_scores = np.abs(stats.zscore(age_values))

print("Z-scores for each age:")
for age, z in zip(age_values.values, z_scores):
    flag = " <-- OUTLIER" if z > 2 else ""
    print(f"  Age {age:>6.1f} -> Z-score: {z:.2f}{flag}")
print()

# Remove rows where Z-score > 2 (or 3 for less aggressive)
threshold = 2
mask = np.abs(stats.zscore(df_zscore['Age'].fillna(df_zscore['Age'].median()))) < threshold
df_z_clean = df_zscore[mask]
print(f"Rows before: {len(df_zscore)}")
print(f"Rows after Z-score filtering (threshold={threshold}): {len(df_z_clean)}")
```

**Expected Output:**
```
Z-scores for each age:
  Age   25.0 -> Z-score: 0.28
  Age   30.0 -> Z-score: 0.14
  Age   28.0 -> Z-score: 0.20
  Age   35.0 -> Z-score: 0.03
  Age  150.0 -> Z-score: 2.96 <-- OUTLIER
  Age   22.0 -> Z-score: 0.37
  Age   25.0 -> Z-score: 0.28
  Age   30.0 -> Z-score: 0.14
  Age   -5.0 -> Z-score: 1.06
  Age   40.0 -> Z-score: 0.10
  Age   33.0 -> Z-score: 0.08

Rows before: 12
Rows after Z-score filtering (threshold=2): 11
```

```
+------------------------------------------------------------------+
|         IQR vs Z-SCORE: WHEN TO USE WHICH                         |
|                                                                   |
|  IQR Method                    Z-Score Method                     |
|  - Does not assume normal      - Assumes roughly normal           |
|    distribution                  distribution                     |
|  - Based on quartiles          - Based on mean and                |
|  - More robust to extreme       standard deviation                |
|    values                      - Sensitive to extreme values      |
|  - Common threshold: 1.5*IQR  - Common threshold: 2 or 3         |
|  - Good general-purpose        - Good for normally                |
|    method                       distributed data                  |
+------------------------------------------------------------------+
```

---

## String Cleaning

Messy strings are one of the most common data problems. Inconsistent capitalization, extra spaces, and formatting differences can cause the same value to be treated as different categories.

```python
df_strings = df.copy()

print("=== BEFORE STRING CLEANING ===")
print("Department values:")
print(df_strings['Department'].value_counts())
print()

# Problem: "Sales", "SALES", "sales", " Marketing " are treated as different

# Step 1: Strip whitespace (remove leading/trailing spaces)
df_strings['Department'] = df_strings['Department'].str.strip()

print("After strip():")
print(df_strings['Department'].value_counts())
print()

# Step 2: Convert to consistent case (lowercase)
df_strings['Department'] = df_strings['Department'].str.lower()

print("After lower():")
print(df_strings['Department'].value_counts())
print()

# Step 3: Standardize to title case for display
df_strings['Department'] = df_strings['Department'].str.title()

print("After title():")
print(df_strings['Department'].value_counts())
```

**Expected Output:**
```
=== BEFORE STRING CLEANING ===
Department values:
Department
Sales           3
Engineering     3
 Marketing      1
Marketing       1
SALES           1
sales           1
HR              1
marketing       1
Name: count, dtype: int64

After strip():
Department
Sales          3
Engineering    3
Marketing      2
SALES          1
sales          1
HR             1
Name: count, dtype: int64

After lower():
Department
sales          4
engineering    3
marketing      2
hr             1
Name: count, dtype: int64

After title():
Department
Sales          4
Engineering    3
Marketing      2
Hr             1
Name: count, dtype: int64
```

### Cleaning Emails and Names

```python
df_strings2 = df.copy()

# Clean emails: lowercase and strip
df_strings2['Email'] = df_strings2['Email'].str.lower().str.strip()

print("Emails after cleaning:")
print(df_strings2['Email'].values)
print()

# Clean names: title case, strip, handle None
df_strings2['Name'] = df_strings2['Name'].fillna('Unknown')
df_strings2['Name'] = df_strings2['Name'].str.strip().str.title()

print("Names after cleaning:")
print(df_strings2['Name'].values)
```

**Expected Output:**
```
Emails after cleaning:
['alice@co.com' 'bob@co.com' 'carol@co.com' 'dave@co.com' 'eve@co.com'
 'frank@co.com' 'grace@co.com' 'alice@co.com' 'bob@co.com' 'heidi@co.com'
 'kate@co.com' 'ivan@co.com']

Names after cleaning:
['Alice' 'Bob' 'Carol' 'Dave' 'Eve' 'Frank' 'Grace' 'Alice' 'Bob' 'Heidi'
 'Unknown' 'Ivan']
```

### Using str.replace() for Pattern Cleaning

```python
# Example: cleaning phone numbers
phones = pd.Series([
    '(555) 123-4567',
    '555.123.4567',
    '555-123-4567',
    '5551234567',
    '+1 555 123 4567'
])

print("Before cleaning:")
print(phones.values)

# Remove all non-digit characters
phones_clean = phones.str.replace(r'\D', '', regex=True)

print("\nAfter removing non-digits:")
print(phones_clean.values)

# Keep last 10 digits (remove country code)
phones_clean = phones_clean.str[-10:]

print("\nFinal (last 10 digits):")
print(phones_clean.values)
```

**Expected Output:**
```
Before cleaning:
['(555) 123-4567' '555.123.4567' '555-123-4567' '5551234567'
 '+1 555 123 4567']

After removing non-digits:
['5551234567' '5551234567' '5551234567' '5551234567' '15551234567']

Final (last 10 digits):
['5551234567' '5551234567' '5551234567' '5551234567' '5551234567']
```

**Line-by-line explanation:**

- `.str.replace(r'\D', '', regex=True)` - Replace any character that is NOT a digit (`\D` in regex) with nothing (empty string). This removes parentheses, dashes, dots, spaces, and plus signs.
- `.str[-10:]` - Take only the last 10 characters. This removes a leading country code like "1".

---

## Complete Before/After Cleaning Example

Let us clean our entire messy dataset from start to finish.

```python
import pandas as pd
import numpy as np

# ============================================
# CREATE THE MESSY DATASET
# ============================================
data = {
    'Name': ['Alice', 'Bob', 'Carol', 'Dave', 'Eve', 'Frank',
             'Grace', 'alice', 'Bob', 'Heidi', None, 'Ivan'],
    'Age': [25, 30, np.nan, 28, 35, 150, 22, 25, 30, -5, 40, 33],
    'Salary': ['50000', '60000', '55000', 'unknown', '70000',
               '80000', '45000', '50000', '60000', '65000',
               '72000', np.nan],
    'Department': ['Sales', 'Engineering', 'Sales', 'Marketing',
                   'Engineering', 'Sales', ' Marketing ',
                   'SALES', 'Engineering', 'sales', 'HR',
                   'Engineering'],
    'Hire_Date': ['2020-01-15', '2019-06-20', '2021-03-10',
                  '2020/07/25', 'Jan 5, 2022', '2018-11-30',
                  '2023-02-14', '2020-01-15', '2019-06-20',
                  '2021-09-01', '2020-05-15', '2022-08-10'],
    'Email': ['alice@co.com', 'BOB@Co.Com', 'carol@co.com',
              'dave@co.com', 'eve@co.com', 'frank@co.com',
              'grace@co.com', 'alice@co.com', 'BOB@Co.Com',
              'heidi@co.com', 'kate@co.com', 'ivan@co.com']
}

df_raw = pd.DataFrame(data)

print("=" * 60)
print("BEFORE CLEANING")
print("=" * 60)
print(f"Shape: {df_raw.shape}")
print(f"Missing values:\n{df_raw.isnull().sum()}")
print(f"Duplicates: {df_raw.duplicated().sum()}")
print(f"\n{df_raw}")

# ============================================
# STEP 1: Clean strings first
# ============================================
df_clean = df_raw.copy()

# Clean Name
df_clean['Name'] = df_clean['Name'].fillna('Unknown')
df_clean['Name'] = df_clean['Name'].str.strip().str.title()

# Clean Department
df_clean['Department'] = df_clean['Department'].str.strip().str.title()

# Clean Email
df_clean['Email'] = df_clean['Email'].str.lower().str.strip()

print("\nStep 1 done: Strings cleaned")

# ============================================
# STEP 2: Remove duplicates
# ============================================
before_count = len(df_clean)
df_clean = df_clean.drop_duplicates(subset=['Name', 'Email'], keep='first')
after_count = len(df_clean)
print(f"Step 2 done: Removed {before_count - after_count} duplicates")

# ============================================
# STEP 3: Fix data types
# ============================================
# Convert Salary to numeric
df_clean['Salary'] = pd.to_numeric(df_clean['Salary'], errors='coerce')

# Convert Hire_Date to datetime
df_clean['Hire_Date'] = pd.to_datetime(df_clean['Hire_Date'])

print("Step 3 done: Data types fixed")

# ============================================
# STEP 4: Handle missing values
# ============================================
# Fill missing Age with median
median_age = df_clean['Age'].median()
df_clean['Age'] = df_clean['Age'].fillna(median_age)

# Fill missing Salary with median
median_salary = df_clean['Salary'].median()
df_clean['Salary'] = df_clean['Salary'].fillna(median_salary)

print(f"Step 4 done: Missing values filled (Age median={median_age}, Salary median={median_salary})")

# ============================================
# STEP 5: Handle outliers
# ============================================
# Cap Age to reasonable range
df_clean['Age'] = df_clean['Age'].clip(lower=0, upper=100)

print("Step 5 done: Outliers capped")

# ============================================
# FINAL RESULT
# ============================================
print("\n" + "=" * 60)
print("AFTER CLEANING")
print("=" * 60)
print(f"Shape: {df_clean.shape}")
print(f"Missing values:\n{df_clean.isnull().sum()}")
print(f"Duplicates: {df_clean.duplicated().sum()}")
print(f"\nData types:\n{df_clean.dtypes}")
print(f"\n{df_clean}")
print()

# Quick validation
print("=== VALIDATION ===")
print(f"Age range: {df_clean['Age'].min()} to {df_clean['Age'].max()}")
print(f"Salary range: {df_clean['Salary'].min()} to {df_clean['Salary'].max()}")
print(f"Departments: {sorted(df_clean['Department'].unique())}")
print(f"Date range: {df_clean['Hire_Date'].min()} to {df_clean['Hire_Date'].max()}")
```

**Expected Output:**
```
============================================================
BEFORE CLEANING
============================================================
Shape: (12, 6)
Missing values:
Name          1
Age           1
Salary        1
Department    0
Hire_Date     0
Email         0
dtype: int64
Duplicates: 0

     Name  Age   Salary    Department     Hire_Date         Email
0   Alice   25    50000         Sales    2020-01-15   alice@co.com
1     Bob   30    60000   Engineering    2019-06-20    BOB@Co.Com
...

Step 1 done: Strings cleaned
Step 2 done: Removed 2 duplicates
Step 3 done: Data types fixed
Step 4 done: Missing values filled (Age median=30.0, Salary median=62500.0)
Step 5 done: Outliers capped

============================================================
AFTER CLEANING
============================================================
Shape: (10, 6)
Missing values:
Name          0
Age           0
Salary        0
Department    0
Hire_Date     0
Email         0
dtype: int64
Duplicates: 0

Data types:
Name                  object
Age                  float64
Salary               float64
Department            object
Hire_Date     datetime64[ns]
Email                 object
dtype: object

      Name   Age    Salary   Department  Hire_Date         Email
0    Alice  25.0   50000.0        Sales 2020-01-15  alice@co.com
2    Carol  30.0   55000.0        Sales 2021-03-10  carol@co.com
3     Dave  28.0   62500.0    Marketing 2020-07-25   dave@co.com
4      Eve  35.0   70000.0  Engineering 2022-01-05   eve@co.com
5    Frank 100.0   80000.0        Sales 2018-11-30  frank@co.com
6    Grace  22.0   45000.0    Marketing 2023-02-14  grace@co.com
9    Heidi   0.0   65000.0        Sales 2021-09-01  heidi@co.com
10 Unknown  40.0   72000.0           Hr 2020-05-15   kate@co.com
11    Ivan  33.0   62500.0  Engineering 2022-08-10   ivan@co.com

=== VALIDATION ===
Age range: 0.0 to 100.0
Salary range: 45000.0 to 80000.0
Departments: ['Engineering', 'Hr', 'Marketing', 'Sales']
Date range: 2018-11-30 to 2023-02-14
```

---

## Common Mistakes

1. **Cleaning data without making a copy first.** Always use `df_clean = df.copy()` before making changes. This preserves your original data in case you make a mistake.

2. **Filling missing values with the mean when outliers exist.** The mean is sensitive to outliers. If you have ages like [20, 25, 30, 200], the mean is 68.75. The median (27.5) is much more representative. Use the median when outliers exist.

3. **Dropping too many rows.** If 30% of your data has missing values, dropping all those rows loses too much information. Consider filling instead.

4. **Not cleaning strings before removing duplicates.** "Sales" and "SALES" look different to the computer. Clean strings first, then check for duplicates.

5. **Blindly removing outliers.** An outlier might be a real, important data point. A 150-year-old person is clearly an error. But a $10 million house in a housing dataset might be real. Always investigate before removing.

6. **Not validating after cleaning.** After cleaning, always check your data. Run describe(), check for remaining missing values, verify data types, and spot-check values.

---

## Best Practices

1. **Make a copy before cleaning.** Always work on a copy: `df_clean = df.copy()`.

2. **Follow a consistent order.** Clean strings first, then remove duplicates, fix data types, handle missing values, and finally address outliers.

3. **Document every step.** Write comments explaining what you changed and why. Your future self will thank you.

4. **Check data after each step.** After each cleaning step, print the shape, missing values, or a sample to verify your changes worked correctly.

5. **Use median over mean for filling.** Median is more robust to outliers than mean. Use it as your default for numeric columns.

6. **Keep a record of what you removed.** If you drop rows or change values, log how many and why. This helps with transparency and debugging.

---

## Quick Summary

Data cleaning is the process of fixing errors and inconsistencies in your data. The main tasks are: finding and handling missing values (drop, fill with mean/median/mode, or forward/backward fill), removing duplicate rows, fixing data types (text to numbers, text to dates), handling outliers (IQR method, Z-score, or capping), and cleaning strings (strip, lower, replace). Always clean data before building a model because bad data produces bad models. Follow a consistent cleaning order and validate your data after each step.

---

## Key Points to Remember

- **"Garbage in, garbage out"** -- clean data is essential for good models.
- Use `isnull().sum()` to find missing values.
- **Drop rows** only when very few are missing. Otherwise, **fill** with mean, median, or mode.
- **Median** is better than mean when outliers exist.
- `pd.to_numeric(col, errors='coerce')` converts text to numbers, replacing failures with NaN.
- `pd.to_datetime(col)` converts text to datetime objects.
- Always **clean strings first** (strip, lower), then check for duplicates.
- `drop_duplicates()` removes duplicate rows. Use `subset` to check specific columns.
- **IQR method**: outliers are below Q1 - 1.5*IQR or above Q3 + 1.5*IQR.
- **Z-score method**: outliers have a Z-score above 2 or 3.
- Use `.clip()` to cap outliers instead of removing them.
- Always **make a copy** before cleaning: `df_clean = df.copy()`.
- **Validate** your cleaned data: check shape, missing values, data types, and value ranges.

---

## Practice Questions

### Question 1
You have a column with 40% missing values. Should you drop those rows or fill them? Why?

**Answer:** You should **fill** them, not drop them. Dropping 40% of your data would lose too much information and significantly reduce your dataset. Fill numeric columns with the **median** (robust to outliers) and categorical columns with the **mode** (most common value) or a placeholder like "Unknown."

### Question 2
What is the difference between `errors='coerce'` and `errors='raise'` in `pd.to_numeric()`?

**Answer:** `errors='coerce'` replaces values that cannot be converted to numbers with NaN (silently handles errors). `errors='raise'` throws an error and stops the program if any value cannot be converted. Use `coerce` when you expect some bad values and want to handle them later. Use `raise` when all values should be numeric and you want to be alerted to problems.

### Question 3
Why should you clean strings before checking for duplicates?

**Answer:** Because the computer treats different capitalizations and spacing as different values. "Sales", "SALES", "sales", and " Sales " are all considered different strings. If you check for duplicates before cleaning, you will miss duplicates that differ only in capitalization or spacing. Clean strings first (strip whitespace, standardize case), then check for duplicates.

### Question 4
You have ages: [22, 25, 28, 30, 35, 40, 200]. Using the IQR method, is 200 an outlier?

**Answer:** Yes. Q1 = 25, Q3 = 40, IQR = 15. Upper bound = 40 + 1.5 * 15 = 62.5. Since 200 > 62.5, it is an outlier. Lower bound = 25 - 1.5 * 15 = 2.5. No values are below 2.5, so there are no lower outliers.

### Question 5
What is the difference between forward fill and backward fill? When would you use each?

**Answer:** **Forward fill (ffill)** fills missing values with the last known value before the gap. **Backward fill (bfill)** fills missing values with the next known value after the gap. Use forward fill when the previous value is the best estimate (e.g., a stock price that has not changed). Use backward fill when the next value is more relevant (e.g., filling in a schedule where the next event is known).

---

## Exercises

### Exercise 1: Clean a Messy Dataset

Create the following messy dataset and clean it completely:

```python
messy_data = {
    'product': ['Widget', 'widget', 'Gadget', 'GADGET', 'Doohickey',
                'Widget', None, 'Gadget'],
    'price': ['10.99', '10.99', '24.50', 'free', '5.00',
              '10.99', '15.00', '24.50'],
    'quantity': [100, 100, np.nan, 50, -10, 100, 75, 50],
    'category': ['electronics', 'Electronics', ' tools',
                 'Tools', 'misc', 'electronics', 'TOOLS', 'tools']
}
```

Your tasks:
1. Clean all strings (strip, standardize case)
2. Fix the price column (convert to numeric, handle "free")
3. Handle missing values
4. Fix the invalid quantity (-10)
5. Remove duplicates
6. Print before and after

### Exercise 2: Outlier Investigation

Create a dataset with 100 normally distributed values (mean=50, std=10) and add 5 extreme outliers (values like 200, -100). Then:

1. Detect outliers using the IQR method
2. Detect outliers using the Z-score method
3. Compare the results: do both methods find the same outliers?
4. Create box plots before and after removing outliers

### Exercise 3: Date Cleaning Challenge

Create a column with dates in these formats and convert all to proper datetime:
- "2023-01-15"
- "01/15/2023"
- "January 15, 2023"
- "15-Jan-2023"
- "2023.01.15"

Then extract: year, month, day of week, and whether it is a weekend.

---

## What Is Next?

Your data is now clean. Missing values are filled. Duplicates are removed. Data types are correct. Outliers are handled. Strings are consistent.

But clean data is just the starting point. In Chapter 5, you will learn Feature Engineering -- the art of creating new columns that help your model make better predictions. You will learn to extract information from dates, create new features from existing ones, transform skewed data, and select the most important features. Feature engineering is often the difference between a mediocre model and a great one.
