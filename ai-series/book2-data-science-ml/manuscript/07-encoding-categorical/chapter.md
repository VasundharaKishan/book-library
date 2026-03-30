# Chapter 7: Encoding Categorical Variables

## What You Will Learn

In this chapter, you will learn:

- Why machine learning models need numbers, not words
- How Label Encoding converts categories to numbers
- How One-Hot Encoding creates separate columns for each category
- How to use pandas `get_dummies()` for quick encoding
- How to use sklearn `OneHotEncoder` for production-ready encoding
- How to handle high-cardinality features (categories with many unique values)
- When to use Ordinal Encoding for ordered categories
- How to encode a dataset with mixed types (numbers and categories together)

## Why This Chapter Matters

Imagine you walk into a restaurant and tell the waiter: "I want something delicious." The waiter cannot cook "delicious." They need a specific order. "Grilled chicken" or "pasta" or "salad." They need something concrete to work with.

Machine learning models are like that waiter. You cannot feed them words like "Red," "Blue," or "Green." They only understand numbers. If your dataset has a column called "Color" with values like "Red," "Blue," and "Green," you must convert those words into numbers before the model can use them.

This conversion is called **encoding**. Get it wrong, and your model learns nonsense. Get it right, and your model understands your data perfectly. This chapter shows you every major encoding technique and when to use each one.

---

## 7.1 Why Models Need Numbers

### The Problem: Words in Your Data

Most real-world datasets contain text categories. Here are some examples:

```
Dataset: Customer Information
================================
Name        City          Gender    Age    Salary
Alice       New York      Female    30     50000
Bob         Chicago       Male      25     45000
Charlie     New York      Male      35     60000
Diana       Los Angeles   Female    28     55000
```

The columns "City" and "Gender" contain words. A machine learning model cannot do math with words. It needs numbers.

### What Happens If You Ignore This?

If you try to train a model with text columns, you will get an error:

```python
import pandas as pd
from sklearn.linear_model import LinearRegression

# Create sample data
data = pd.DataFrame({
    'city': ['New York', 'Chicago', 'New York', 'Los Angeles'],
    'age': [30, 25, 35, 28],
    'salary': [50000, 45000, 60000, 55000]
})

# Try to use text data directly
model = LinearRegression()
model.fit(data[['city', 'age']], data['salary'])
```

**Expected Output:**
```
ValueError: could not convert string to float: 'New York'
```

The model says: "I do not know what 'New York' means. Give me a number!"

### Types of Categorical Data

Before we encode, we need to understand two types of categories:

```
Categorical Data Types
=======================

1. NOMINAL (No Order)              2. ORDINAL (Has Order)
   - Colors: Red, Blue, Green         - Size: Small, Medium, Large
   - City: NYC, Chicago, LA           - Rating: Bad, OK, Good, Great
   - Gender: Male, Female             - Education: High School, Bachelor, Master
   - Animal: Cat, Dog, Bird           - Temperature: Cold, Warm, Hot

   No category is "bigger"            Categories have a natural ranking
   than another.                      Small < Medium < Large
```

This distinction matters. The encoding method you choose depends on whether your categories have an order or not.

---

## 7.2 Label Encoding

### The Idea

Label Encoding is the simplest approach. It assigns a unique number to each category.

```
Label Encoding Example
=======================

Original:    Red    Blue    Green    Red    Blue
Encoded:      0       1       2       0       1

Mapping:
  Red   -> 0
  Blue  -> 1
  Green -> 2
```

**Think of it like this:** You are numbering seats in a theater. Seat A gets number 0, Seat B gets number 1, Seat C gets number 2. The numbers are just labels. They do not mean Seat C is "better" than Seat A.

### Label Encoding with sklearn

```python
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Create sample data
colors = ['Red', 'Blue', 'Green', 'Red', 'Blue', 'Green', 'Red']

# Create the encoder
label_encoder = LabelEncoder()

# Fit and transform
encoded = label_encoder.fit_transform(colors)

print("Original:", colors)
print("Encoded: ", encoded)
print("Classes: ", label_encoder.classes_)
```

**Expected Output:**
```
Original: ['Red', 'Blue', 'Green', 'Red', 'Blue', 'Green', 'Red']
Encoded:  [2 0 1 2 0 1 2]
Classes:  ['Blue' 'Green' 'Red']
```

**Line-by-line explanation:**

- `LabelEncoder()` creates the encoder object.
- `fit_transform(colors)` does two things: learns the categories (fit), then converts them to numbers (transform).
- `classes_` shows all unique categories the encoder learned. They are sorted alphabetically. Blue=0, Green=1, Red=2.

### Reversing Label Encoding

You can convert numbers back to words:

```python
# Convert numbers back to words
decoded = label_encoder.inverse_transform([2, 0, 1])
print("Decoded:", decoded)
```

**Expected Output:**
```
Decoded: ['Red' 'Blue' 'Green']
```

### The Danger of Label Encoding

Label Encoding has a serious problem with nominal data. Look at this:

```
City Encoding:
  Chicago     -> 0
  Los Angeles -> 1
  New York    -> 2

The model now thinks:
  New York (2) > Los Angeles (1) > Chicago (0)
  New York (2) = Chicago (0) + Los Angeles (1)  ??? NONSENSE!
```

The model sees numbers and assumes they have mathematical meaning. It thinks New York is "greater" than Chicago. It might even think New York equals Chicago plus Los Angeles. This is wrong.

**Rule:** Use Label Encoding only for:
- The target variable (what you are predicting)
- Ordinal data (categories with a natural order)

**Never** use Label Encoding for nominal input features. Use One-Hot Encoding instead.

---

## 7.3 One-Hot Encoding

### The Idea

One-Hot Encoding creates a new column for each category. Each column contains 0 or 1. A 1 means "this row belongs to this category." A 0 means "it does not."

```
One-Hot Encoding Example
==========================

Original Data:
  Color
  -----
  Red
  Blue
  Green
  Red

After One-Hot Encoding:
  Color_Red    Color_Blue    Color_Green
  ---------   ----------    -----------
      1            0              0
      0            1              0
      0            0              1
      1            0              0
```

**Think of it like this:** You have a row of light switches. Each switch represents one category. Only one switch is ON (1) at a time. All others are OFF (0). That is why it is called "one-hot" -- one switch is hot (on).

```
One-Hot = One light is ON
===========================

Red:    [ON ] [OFF] [OFF]    ->  [1, 0, 0]
Blue:   [OFF] [ON ] [OFF]    ->  [0, 1, 0]
Green:  [OFF] [OFF] [ON ]    ->  [0, 0, 1]
```

### Why One-Hot Encoding Works

With One-Hot Encoding, the model does not see any ordering:

```
Label Encoding (BAD for nominal):
  Red=0, Blue=1, Green=2
  Model thinks: Green > Blue > Red   (WRONG!)

One-Hot Encoding (GOOD for nominal):
  Red   = [1, 0, 0]
  Blue  = [0, 1, 0]
  Green = [0, 0, 1]
  Model sees: These are three separate, equal categories (CORRECT!)
```

No category is "greater" than another. Each category is independent.

---

## 7.4 One-Hot Encoding with pandas get_dummies

### Quick Encoding with get_dummies

The fastest way to one-hot encode is with pandas:

```python
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'color': ['Red', 'Blue', 'Green', 'Red', 'Blue'],
    'size': [10, 20, 15, 12, 18]
})

print("Before encoding:")
print(df)
print()

# One-hot encode the 'color' column
df_encoded = pd.get_dummies(df, columns=['color'])

print("After encoding:")
print(df_encoded)
```

**Expected Output:**
```
Before encoding:
   color  size
0    Red    10
1   Blue    20
2  Green    15
3    Red    12
4   Blue    18

After encoding:
   size  color_Blue  color_Green  color_Red
0    10       False        False       True
1    20        True        False      False
2    15       False         True      False
3    12       False        False       True
4    18        True        False      False
```

**Line-by-line explanation:**

- `pd.get_dummies(df, columns=['color'])` converts the "color" column into separate True/False columns.
- The original "color" column is removed.
- Three new columns appear: `color_Blue`, `color_Green`, `color_Red`.
- Numeric columns like "size" are left untouched.

### Getting 0s and 1s Instead of True/False

```python
# Use dtype parameter for integer encoding
df_encoded = pd.get_dummies(df, columns=['color'], dtype=int)

print(df_encoded)
```

**Expected Output:**
```
   size  color_Blue  color_Green  color_Red
0    10           0            0          1
1    20           1            0          0
2    15           0            1          0
3    12           0            0          1
4    18           1            0          0
```

### The drop_first Parameter

When you have 3 categories, you only need 2 columns to represent them. If it is NOT Blue and NOT Green, it MUST be Red. This is called **dropping the first category**.

```
Why drop_first works:
======================

All three columns:           With drop_first=True:
  Blue  Green  Red             Blue  Green
  0     0      1     Red  ->   0     0       (Not Blue, Not Green = Red!)
  1     0      0     Blue ->   1     0
  0     1      0     Green->   0     1
```

```python
# Drop first category to avoid redundancy
df_encoded = pd.get_dummies(df, columns=['color'], drop_first=True, dtype=int)

print(df_encoded)
```

**Expected Output:**
```
   size  color_Green  color_Red
0    10            0          1
1    20            0          0
2    15            1          0
3    12            0          1
4    18            0          0
```

**Why drop one column?** Some models (especially linear regression) get confused when columns are perfectly correlated. If you know two of the three values, you always know the third. This is called **multicollinearity**. Dropping one column fixes it.

---

## 7.5 One-Hot Encoding with sklearn OneHotEncoder

### Why Use sklearn Instead of pandas?

Pandas `get_dummies` is great for quick exploration. But it has a problem in production:

```
The Problem with get_dummies:
==============================

Training data has:    Red, Blue, Green
Test data has:        Red, Blue          (no Green!)

get_dummies on training: 3 columns (Red, Blue, Green)
get_dummies on test:     2 columns (Red, Blue)

MISMATCH! The model expects 3 columns but gets 2. ERROR!
```

sklearn `OneHotEncoder` solves this. It remembers the categories from training and always produces the same columns.

### Using OneHotEncoder

```python
from sklearn.preprocessing import OneHotEncoder
import numpy as np

# Create sample data
colors = np.array(['Red', 'Blue', 'Green', 'Red', 'Blue']).reshape(-1, 1)

# Create and fit the encoder
encoder = OneHotEncoder(sparse_output=False)
encoded = encoder.fit_transform(colors)

print("Original shape:", colors.shape)
print("Encoded shape: ", encoded.shape)
print()
print("Encoded data:")
print(encoded)
print()
print("Feature names:", encoder.get_feature_names_out())
```

**Expected Output:**
```
Original shape: (5, 1)
Encoded shape:  (5, 3)

Encoded data:
[[0. 0. 1.]
 [1. 0. 0.]
 [0. 1. 0.]
 [0. 0. 1.]
 [1. 0. 0.]]

Feature names: ['x0_Blue' 'x0_Green' 'x0_Red']
```

**Line-by-line explanation:**

- `reshape(-1, 1)` changes the array from a flat list to a column. sklearn expects 2D data (rows and columns).
- `sparse_output=False` tells the encoder to return a regular array. Without this, it returns a sparse matrix (a memory-efficient format).
- `fit_transform()` learns the categories and encodes them in one step.
- `get_feature_names_out()` shows the column names. "x0" means "first input column."

### Handling Unknown Categories in Test Data

```python
# Fit on training data
train_colors = np.array(['Red', 'Blue', 'Green']).reshape(-1, 1)
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
encoder.fit(train_colors)

# Transform test data (has "Yellow" which was not in training)
test_colors = np.array(['Red', 'Yellow', 'Blue']).reshape(-1, 1)
test_encoded = encoder.transform(test_colors)

print("Test data encoded:")
print(test_encoded)
```

**Expected Output:**
```
Test data encoded:
[[0. 0. 1.]
 [0. 0. 0.]
 [1. 0. 0.]]
```

**What happened?** "Yellow" was not in the training data. With `handle_unknown='ignore'`, the encoder sets all columns to 0 for unknown categories. Without this parameter, it would throw an error.

### Dropping One Category in sklearn

```python
# Drop first category to avoid multicollinearity
encoder = OneHotEncoder(sparse_output=False, drop='first')
encoded = encoder.fit_transform(colors)

print("Feature names:", encoder.get_feature_names_out())
print("Encoded:")
print(encoded)
```

**Expected Output:**
```
Feature names: ['x0_Green' 'x0_Red']
Encoded:
[[0. 1.]
 [0. 0.]
 [1. 0.]
 [0. 1.]
 [0. 0.]]
```

---

## 7.6 Ordinal Encoding

### When Categories Have an Order

Some categories have a natural ranking. Small is less than Medium. Medium is less than Large. For these, we want the numbers to reflect the order.

```
Ordinal Encoding Example
==========================

Category       Number
--------       ------
Small      ->    0
Medium     ->    1
Large      ->    2
Extra Large->    3

The order matters: Small < Medium < Large < Extra Large
The numbers reflect this: 0 < 1 < 2 < 3
```

**Think of it like this:** School grades have an order. A is better than B, B is better than C. If you encode A=3, B=2, C=1, the numbers correctly show that A > B > C. The ordering is meaningful.

### Ordinal Encoding with sklearn

```python
from sklearn.preprocessing import OrdinalEncoder
import numpy as np

# Define the categories IN ORDER
size_categories = [['Small', 'Medium', 'Large', 'Extra Large']]

# Create sample data
sizes = np.array(['Large', 'Small', 'Medium', 'Extra Large', 'Small']).reshape(-1, 1)

# Create encoder with specified order
encoder = OrdinalEncoder(categories=size_categories)
encoded = encoder.fit_transform(sizes)

print("Original:", sizes.flatten())
print("Encoded: ", encoded.flatten())
```

**Expected Output:**
```
Original: ['Large' 'Small' 'Medium' 'Extra Large' 'Small']
Encoded:  [2. 0. 1. 3. 0.]
```

**Line-by-line explanation:**

- `categories=size_categories` tells the encoder the correct order. Small=0, Medium=1, Large=2, Extra Large=3.
- Without specifying categories, the encoder would sort alphabetically. "Extra Large" would come first (E before L, M, S). That would be wrong.

### Another Example: Education Level

```python
from sklearn.preprocessing import OrdinalEncoder
import numpy as np

# Define education levels in order
edu_order = [['High School', 'Bachelor', 'Master', 'PhD']]

# Sample data
education = np.array([
    'Bachelor', 'PhD', 'High School', 'Master', 'Bachelor'
]).reshape(-1, 1)

encoder = OrdinalEncoder(categories=edu_order)
encoded = encoder.fit_transform(education)

print("Education levels encoded:")
for original, number in zip(education.flatten(), encoded.flatten()):
    print(f"  {original:15s} -> {number:.0f}")
```

**Expected Output:**
```
Education levels encoded:
  Bachelor        -> 1
  PhD             -> 3
  High School     -> 0
  Master          -> 2
  Bachelor        -> 1
```

### When to Use Which Encoding

```
Decision Guide: Which Encoding to Use?
========================================

Is the data categorical?
  |
  +-- NO  -> No encoding needed (it is already a number)
  |
  +-- YES -> Does it have a natural order?
              |
              +-- YES (ordinal) -> Use Ordinal Encoding
              |    Examples: Size (S/M/L), Rating (1-5),
              |    Education (HS/BS/MS/PhD)
              |
              +-- NO (nominal) -> How many unique values?
                   |
                   +-- FEW (< 10-15) -> Use One-Hot Encoding
                   |    Examples: Color, Gender, Country
                   |
                   +-- MANY (> 15)   -> See Section 7.7
                        Examples: ZIP code, City name,
                        Product ID
```

---

## 7.7 Handling High-Cardinality Features

### What is High Cardinality?

**Cardinality** means the number of unique values in a category. **High cardinality** means there are many unique values.

```
Low Cardinality (Few unique values):
  Gender:  Male, Female, Other           -> 3 values
  Color:   Red, Blue, Green, Yellow      -> 4 values

High Cardinality (Many unique values):
  City:    New York, Chicago, LA, ...    -> 100+ values
  ZIP code: 10001, 60601, 90001, ...     -> 40,000+ values
  Product ID: SKU001, SKU002, ...        -> 10,000+ values
```

### Why High Cardinality is a Problem

If you one-hot encode a column with 1,000 unique cities, you get 1,000 new columns:

```
One-Hot Encoding 1000 Cities
==============================

Original: 1 column ("city")
After:    1000 columns!

city_New_York  city_Chicago  city_LA  ...  city_Zanesville
     1              0           0     ...       0
     0              1           0     ...       0
     0              0           1     ...       0

Most values are 0. This is called a SPARSE matrix.
It wastes memory and can confuse models.
```

### Strategies for High Cardinality

**Strategy 1: Frequency Encoding**

Replace each category with how often it appears:

```python
import pandas as pd

# Sample data with many cities
df = pd.DataFrame({
    'city': ['New York', 'Chicago', 'New York', 'LA', 'Chicago',
             'New York', 'LA', 'Chicago', 'Miami', 'New York'],
    'salary': [70000, 55000, 72000, 65000, 58000,
               75000, 63000, 56000, 60000, 71000]
})

# Count how often each city appears
city_counts = df['city'].value_counts()
print("City frequencies:")
print(city_counts)
print()

# Replace city names with their frequency
df['city_freq'] = df['city'].map(city_counts)

print("Data with frequency encoding:")
print(df[['city', 'city_freq', 'salary']])
```

**Expected Output:**
```
City frequencies:
city
New York    4
Chicago     3
LA          2
Miami       1
Name: count, dtype: int64

Data with frequency encoding:
       city  city_freq  salary
0  New York          4   70000
1   Chicago          3   55000
2  New York          4   72000
3        LA          2   65000
4   Chicago          3   58000
5  New York          4   75000
6        LA          2   63000
7   Chicago          3   56000
8     Miami          1   60000
9  New York          4   71000
```

**Strategy 2: Group Rare Categories**

Combine infrequent categories into an "Other" group:

```python
import pandas as pd

df = pd.DataFrame({
    'city': ['New York', 'New York', 'New York', 'Chicago', 'Chicago',
             'LA', 'Miami', 'Boston', 'Seattle', 'Denver']
})

# Find cities that appear less than 2 times
city_counts = df['city'].value_counts()
rare_cities = city_counts[city_counts < 2].index

print("Rare cities:", list(rare_cities))

# Replace rare cities with "Other"
df['city_grouped'] = df['city'].replace(rare_cities, 'Other')

print("\nAfter grouping:")
print(df['city_grouped'].value_counts())
```

**Expected Output:**
```
Rare cities: ['LA', 'Miami', 'Boston', 'Seattle', 'Denver']

After grouping:
city_grouped
Other       5
New York    3
Chicago     2
Name: count, dtype: int64
```

Now you can safely one-hot encode "city_grouped" because it only has 3 unique values.

---

## 7.8 Complete Example: Encoding Mixed Data Types

Let's put everything together with a realistic dataset. We will encode a dataset that has multiple categorical columns of different types.

### The Dataset

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Create a realistic employee dataset
data = pd.DataFrame({
    'department': ['Engineering', 'Sales', 'Engineering', 'HR', 'Sales',
                   'Engineering', 'HR', 'Sales', 'Engineering', 'Sales',
                   'HR', 'Engineering', 'Sales', 'HR', 'Engineering'],
    'education': ['Master', 'Bachelor', 'PhD', 'Bachelor', 'High School',
                  'Master', 'Master', 'Bachelor', 'PhD', 'Master',
                  'Bachelor', 'Bachelor', 'Master', 'High School', 'Master'],
    'experience_years': [5, 3, 8, 2, 1, 6, 4, 3, 10, 7,
                         2, 4, 5, 1, 8],
    'performance': ['Good', 'Average', 'Excellent', 'Average', 'Poor',
                    'Good', 'Good', 'Average', 'Excellent', 'Good',
                    'Average', 'Good', 'Good', 'Poor', 'Excellent'],
    'salary': [85000, 55000, 110000, 45000, 35000,
               90000, 65000, 52000, 120000, 80000,
               42000, 70000, 72000, 38000, 105000]
})

print("Original Dataset:")
print(data)
print()
print("Data types:")
print(data.dtypes)
print()
print("Unique values per column:")
for col in data.columns:
    print(f"  {col}: {data[col].nunique()} unique values")
```

**Expected Output:**
```
Original Dataset:
       department   education  experience_years performance  salary
0     Engineering      Master                 5        Good   85000
1           Sales    Bachelor                 3     Average   55000
2     Engineering         PhD                 8   Excellent  110000
3              HR    Bachelor                 2     Average   45000
4           Sales  High School                1        Poor   35000
5     Engineering      Master                 6        Good   90000
6              HR      Master                 4        Good   65000
7           Sales    Bachelor                 3     Average   52000
8     Engineering         PhD                10   Excellent  120000
9           Sales      Master                 7        Good   80000
10             HR    Bachelor                 2     Average   42000
11    Engineering    Bachelor                 4        Good   70000
12          Sales      Master                 5        Good   72000
13             HR  High School                1        Poor   38000
14    Engineering      Master                 8   Excellent  105000

Data types:
department          object
education           object
experience_years     int64
performance         object
salary               int64
dtype: object

Unique values per column:
  department: 3 unique values
  education: 4 unique values
  experience_years: 9 unique values
  performance: 4 unique values
  salary: 15 unique values
```

### Analyzing Each Column

```
Column Analysis:
=================

Column              Type        Encoding Method
------              ----        ---------------
department          Nominal     One-Hot Encoding (no natural order)
education           Ordinal     Ordinal Encoding (HS < Bachelor < Master < PhD)
experience_years    Numeric     No encoding needed
performance         Ordinal     Ordinal Encoding (Poor < Average < Good < Excellent)
salary              Numeric     Target variable - no encoding needed
```

### Step-by-Step Encoding

```python
# Step 1: Ordinal Encoding for 'education'
edu_order = [['High School', 'Bachelor', 'Master', 'PhD']]
edu_encoder = OrdinalEncoder(categories=edu_order)
data['education_encoded'] = edu_encoder.fit_transform(data[['education']])

print("Education encoding:")
for orig, enc in zip(data['education'], data['education_encoded']):
    print(f"  {orig:15s} -> {enc:.0f}")
```

**Expected Output:**
```
Education encoding:
  Master          -> 2
  Bachelor        -> 1
  PhD             -> 3
  Bachelor        -> 1
  High School     -> 0
  Master          -> 2
  Master          -> 2
  Bachelor        -> 1
  PhD             -> 3
  Master          -> 2
  Bachelor        -> 1
  Bachelor        -> 1
  Master          -> 2
  High School     -> 0
  Master          -> 2
```

```python
# Step 2: Ordinal Encoding for 'performance'
perf_order = [['Poor', 'Average', 'Good', 'Excellent']]
perf_encoder = OrdinalEncoder(categories=perf_order)
data['performance_encoded'] = perf_encoder.fit_transform(data[['performance']])

print("Performance encoding:")
for orig, enc in zip(data['performance'], data['performance_encoded']):
    print(f"  {orig:12s} -> {enc:.0f}")
```

**Expected Output:**
```
Performance encoding:
  Good         -> 2
  Average      -> 1
  Excellent    -> 3
  Average      -> 1
  Poor         -> 0
  Good         -> 2
  Good         -> 2
  Average      -> 1
  Excellent    -> 3
  Good         -> 2
  Average      -> 1
  Good         -> 2
  Good         -> 2
  Poor         -> 0
  Excellent    -> 3
```

```python
# Step 3: One-Hot Encoding for 'department'
dept_encoded = pd.get_dummies(data['department'], prefix='dept', dtype=int, drop_first=True)

print("Department one-hot encoding:")
print(dept_encoded)
```

**Expected Output:**
```
Department one-hot encoding:
    dept_HR  dept_Sales
0         0           0
1         0           1
2         0           0
3         1           0
4         0           1
5         0           0
6         1           0
7         0           1
8         0           0
9         0           1
10        1           0
11        0           0
12        0           1
13        1           0
14        0           0
```

```python
# Step 4: Combine everything into the final dataset
final_data = pd.concat([
    dept_encoded,
    data[['education_encoded', 'experience_years', 'performance_encoded', 'salary']]
], axis=1)

print("Final encoded dataset:")
print(final_data)
```

**Expected Output:**
```
Final encoded dataset:
    dept_HR  dept_Sales  education_encoded  experience_years  performance_encoded  salary
0         0           0                2.0                 5                  2.0   85000
1         0           1                1.0                 3                  1.0   55000
2         0           0                3.0                 8                  3.0  110000
3         1           0                1.0                 2                  1.0   45000
4         0           1                0.0                 1                  0.0   35000
5         0           0                2.0                 6                  2.0   90000
6         1           0                2.0                 4                  2.0   65000
7         0           1                1.0                 3                  1.0   52000
8         0           0                3.0                10                  3.0  120000
9         0           1                2.0                 7                  2.0   80000
10        1           0                1.0                 2                  1.0   42000
11        0           0                1.0                 4                  2.0   70000
12        0           1                2.0                 5                  2.0   72000
13        1           0                0.0                 1                  0.0   38000
14        0           0                2.0                 8                  3.0  105000
```

### Using ColumnTransformer for Clean Pipelines

In real projects, you should use sklearn `ColumnTransformer`. It applies different encodings to different columns in one step:

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

# Define which columns get which encoding
preprocessor = ColumnTransformer(
    transformers=[
        ('dept_onehot', OneHotEncoder(drop='first', sparse_output=False),
         ['department']),
        ('edu_ordinal', OrdinalEncoder(
            categories=[['High School', 'Bachelor', 'Master', 'PhD']]),
         ['education']),
        ('perf_ordinal', OrdinalEncoder(
            categories=[['Poor', 'Average', 'Good', 'Excellent']]),
         ['performance']),
    ],
    remainder='passthrough'  # Keep numeric columns as-is
)

# Prepare features and target
X = data[['department', 'education', 'experience_years', 'performance']]
y = data['salary']

# Fit and transform
X_encoded = preprocessor.fit_transform(X)

print("Shape before encoding:", X.shape)
print("Shape after encoding: ", X_encoded.shape)
print()
print("Encoded features (first 5 rows):")
print(X_encoded[:5])
```

**Expected Output:**
```
Shape before encoding: (15, 4)
Shape after encoding:  (15, 5)

Encoded features (first 5 rows):
[[ 0.  0.  2.  2.  5.]
 [ 0.  1.  1.  1.  3.]
 [ 0.  0.  3.  3.  8.]
 [ 1.  0.  1.  1.  2.]
 [ 0.  1.  0.  0.  1.]]
```

**Line-by-line explanation:**

- `ColumnTransformer` takes a list of `(name, transformer, columns)` tuples.
- `'dept_onehot'` applies `OneHotEncoder` to the "department" column. With `drop='first'`, it creates 2 columns instead of 3.
- `'edu_ordinal'` applies `OrdinalEncoder` to "education" with the correct order.
- `'perf_ordinal'` applies `OrdinalEncoder` to "performance" with the correct order.
- `remainder='passthrough'` means numeric columns ("experience_years") pass through unchanged.

### Training a Model on Encoded Data

```python
# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Fit preprocessor on training data and transform
X_train_encoded = preprocessor.fit_transform(X_train)
X_test_encoded = preprocessor.transform(X_test)  # Only transform!

# Train model
model = LinearRegression()
model.fit(X_train_encoded, y_train)

# Evaluate
train_score = model.score(X_train_encoded, y_train)
test_score = model.score(X_test_encoded, y_test)

print(f"Training R-squared: {train_score:.4f}")
print(f"Test R-squared:     {test_score:.4f}")
```

**Expected Output:**
```
Training R-squared: 0.9870
Test R-squared:     0.9450
```

**Important:** Notice we use `fit_transform` on training data but only `transform` on test data. This is the same critical rule from Chapter 6 on feature scaling. The preprocessor learns the categories from training data only. It then applies the same encoding to test data.

---

## Common Mistakes

```
Mistake 1: Using Label Encoding for nominal features
------------------------------------------------------
WRONG:  city_encoded: NYC=0, Chicago=1, LA=2
        Model thinks: LA > Chicago > NYC  (NONSENSE!)
RIGHT:  Use One-Hot Encoding for nominal categories.

Mistake 2: Fitting encoder on ALL data (train + test)
------------------------------------------------------
WRONG:  encoder.fit_transform(all_data)
        This leaks test information into training.
RIGHT:  encoder.fit(train_data)
        encoder.transform(test_data)

Mistake 3: Forgetting to handle unknown categories
------------------------------------------------------
WRONG:  OneHotEncoder()  (crashes on unknown test values)
RIGHT:  OneHotEncoder(handle_unknown='ignore')

Mistake 4: One-hot encoding high-cardinality features
------------------------------------------------------
WRONG:  pd.get_dummies(df['zip_code'])  (creates 40,000 columns!)
RIGHT:  Use frequency encoding or group rare categories.

Mistake 5: Not specifying order for ordinal data
------------------------------------------------------
WRONG:  OrdinalEncoder()  (sorts alphabetically)
        Bachelor=0, High School=1, Master=2, PhD=3
        High School > Bachelor ???
RIGHT:  OrdinalEncoder(categories=[['High School', 'Bachelor', 'Master', 'PhD']])
```

---

## Best Practices

1. **Identify your category type first.** Is it nominal (no order) or ordinal (has order)? This determines the encoding method.

2. **Use One-Hot Encoding for nominal features with few categories.** It is safe and effective for features with less than 10-15 unique values.

3. **Use Ordinal Encoding only when order matters.** Always specify the order explicitly. Never rely on alphabetical sorting.

4. **Use sklearn encoders in production.** `pd.get_dummies` is fine for exploration, but sklearn encoders remember categories and handle new data correctly.

5. **Always fit on training data only.** Fit the encoder on training data, then transform both training and test data.

6. **Handle high cardinality carefully.** Use frequency encoding, group rare categories, or consider target encoding for features with many unique values.

7. **Use `drop='first'` for linear models.** This avoids multicollinearity. Tree-based models do not need this.

8. **Use `ColumnTransformer` for real projects.** It keeps your encoding pipeline clean and reproducible.

---

## Quick Summary

```
Encoding Methods Summary
==========================

Method              When to Use                     Creates
------              -----------                     -------
Label Encoding      Target variable only            1 column (numbers)
One-Hot Encoding    Nominal features (few values)   N columns (0s and 1s)
Ordinal Encoding    Ordered categories              1 column (ordered numbers)
Frequency Encoding  High cardinality nominal        1 column (count values)
Group Rare + OHE    High cardinality nominal        Few columns (grouped)
```

---

## Key Points

1. Machine learning models only understand numbers. Categorical data must be encoded before training.

2. **Label Encoding** assigns a number to each category. Only use it for the target variable or when using tree-based models.

3. **One-Hot Encoding** creates a separate binary column for each category. Use it for nominal features with few unique values.

4. **Ordinal Encoding** preserves the natural order of categories. Always specify the order explicitly.

5. **High-cardinality features** (many unique values) should not be one-hot encoded. Use frequency encoding or group rare categories.

6. **ColumnTransformer** lets you apply different encodings to different columns in one clean step.

7. Always fit encoders on training data only, then transform both train and test.

---

## Practice Questions

1. You have a "weather" column with values: Sunny, Rainy, Cloudy, Snowy. What encoding method should you use and why?

2. You have a "satisfaction" column with values: Very Unhappy, Unhappy, Neutral, Happy, Very Happy. What encoding method should you use? Write the code.

3. You have a "product_id" column with 5,000 unique product IDs. Why is one-hot encoding a bad idea? What would you do instead?

4. Explain why `drop_first=True` is important for linear models but not for decision trees.

5. Your training data has three cities: NYC, LA, Chicago. Your test data has a fourth city: Miami. What happens if you use `pd.get_dummies`? What happens if you use sklearn `OneHotEncoder` with `handle_unknown='ignore'`?

---

## Exercises

### Exercise 1: Encode a Survey Dataset

Create a DataFrame with the following columns:
- `age_group`: "18-25", "26-35", "36-45", "46-55", "56+" (ordinal)
- `favorite_color`: "Red", "Blue", "Green", "Yellow" (nominal)
- `satisfaction`: "Low", "Medium", "High" (ordinal)
- `score`: random numbers between 1 and 100

Encode all categorical columns appropriately. Use `OrdinalEncoder` for ordinal columns and `OneHotEncoder` for nominal columns. Print the final encoded DataFrame.

### Exercise 2: Handle High Cardinality

Create a DataFrame with 100 rows and a "country" column containing 30 different country names. Most countries should appear only once or twice, but a few should appear many times. Apply frequency encoding and also try grouping rare countries (appearing less than 3 times) into "Other." Compare the results.

### Exercise 3: Build a Complete Pipeline

Using the employee dataset from Section 7.8, build a complete pipeline using `ColumnTransformer` that:
1. One-hot encodes the department column
2. Ordinal encodes the education column
3. Ordinal encodes the performance column
4. Passes numeric columns through unchanged

Split the data 70/30, train a `LinearRegression` model, and report the R-squared score on both training and test data.

---

## What Is Next?

You now know how to convert categorical data into numbers that models can understand. Combined with the feature scaling techniques from Chapter 6, you can prepare almost any dataset for machine learning.

But what happens when your dataset has too many features? Having 50 or 100 columns can slow down your model and even hurt its accuracy. In Chapter 8, you will learn about **Dimensionality Reduction** -- techniques that reduce the number of features while keeping the important information. You will learn about PCA and t-SNE, two powerful tools for simplifying complex datasets.
