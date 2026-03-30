# Chapter 2: Data Collection

## What You Will Learn

In this chapter, you will learn:

- Where data comes from and the common formats
- How to load CSV files using Pandas
- How to load JSON data
- How to use free datasets from Kaggle
- How to use built-in datasets from scikit-learn
- How to explore your data with shape, dtypes, head(), info(), and describe()
- Why you split data into training and testing sets
- How to use train_test_split from scikit-learn

## Why This Chapter Matters

Machine learning runs on data. Without data, there is no learning. Period.

Think of data as the fuel for your ML engine. A sports car with no fuel goes nowhere. The best ML algorithm with no data does nothing.

But data does not just appear. You need to know where to find it, how to load it, and how to prepare it. You also need to understand your data before feeding it to a model. What columns does it have? How many rows? Are there missing values?

This chapter teaches you all of that. By the end, you will be able to find data, load it into Python, explore it, and split it properly for machine learning.

---

## Where Does Data Come From?

Data comes from many sources. Here are the most common ones:

```
+------------------------------------------------------------------+
|                   COMMON DATA SOURCES                             |
|                                                                   |
|  +----------+  +----------+  +----------+  +----------+          |
|  |  CSV     |  | Database |  |   API    |  |   Web    |          |
|  |  Files   |  |  (SQL)   |  | (REST)   |  | Scraping |          |
|  +----------+  +----------+  +----------+  +----------+          |
|                                                                   |
|  Spreadsheet   Structured    Live data     Extract                |
|  exports,      storage,     from web      data from              |
|  simple text   companies    services      websites               |
|  files         use daily                                         |
|                                                                   |
|  +----------+  +----------+  +----------+                        |
|  |  JSON    |  |  Excel   |  | Built-in |                        |
|  |  Files   |  |  Files   |  | Datasets |                        |
|  +----------+  +----------+  +----------+                        |
|                                                                   |
|  Web APIs,     Business      Practice                            |
|  config        reports,      datasets in                         |
|  files         common in     scikit-learn                        |
|                offices                                           |
+------------------------------------------------------------------+
```

For beginners, the most common sources are:

1. **CSV files** - The most common format. Simple text files where values are separated by commas.
2. **JSON files** - Common for web data and APIs. Stores data in key-value pairs.
3. **Built-in datasets** - Scikit-learn comes with several practice datasets.
4. **Kaggle** - A free platform with thousands of datasets for practice.

Let us learn how to load each one.

---

## Loading CSV Files with Pandas

**CSV** stands for Comma-Separated Values. It is a simple text file where each line is a row and columns are separated by commas.

Here is what a CSV file looks like inside:

```
name,age,city,salary
Alice,30,New York,70000
Bob,25,Chicago,55000
Carol,35,Boston,85000
Dave,28,Seattle,62000
```

**Pandas** is the most popular Python library for working with data. Think of it as a super-powered spreadsheet inside Python.

> **Pandas:** A Python library for data analysis. It provides DataFrames (tables with rows and columns) that make it easy to load, explore, and manipulate data.

> **DataFrame:** A two-dimensional table of data with rows and columns, like a spreadsheet. Each column has a name and a data type.

### Creating a Sample CSV and Loading It

```python
import pandas as pd

# First, let us create a sample CSV file
sample_data = """name,age,city,salary
Alice,30,New York,70000
Bob,25,Chicago,55000
Carol,35,Boston,85000
Dave,28,Seattle,62000
Eve,32,Denver,72000"""

# Write it to a file
with open("employees.csv", "w") as f:
    f.write(sample_data)

# Now load it with Pandas
df = pd.read_csv("employees.csv")

# Display the data
print(df)
```

**Expected Output:**
```
    name  age      city  salary
0  Alice   30  New York   70000
1    Bob   25   Chicago   55000
2  Carol   35    Boston   85000
3   Dave   28   Seattle   62000
4    Eve   32    Denver   72000
```

**Line-by-line explanation:**

- `import pandas as pd` - Import Pandas and give it the short name `pd`. This is a universal convention. Every data scientist writes `pd`.
- `sample_data = """..."""` - A multi-line string containing our CSV data. In real projects, this file already exists on your computer.
- `with open("employees.csv", "w") as f:` - Create a new file called `employees.csv` for writing.
- `f.write(sample_data)` - Write our sample data to the file.
- `df = pd.read_csv("employees.csv")` - Load the CSV file into a Pandas DataFrame. The variable `df` is a convention that stands for DataFrame.
- `print(df)` - Display the table. Notice Pandas adds an index (0, 1, 2, 3, 4) on the left.

### Common read_csv Options

```python
import pandas as pd

# Basic load
df = pd.read_csv("employees.csv")

# Load with a different separator (like tabs or semicolons)
# df = pd.read_csv("data.tsv", sep="\t")

# Load only specific columns
df_subset = pd.read_csv("employees.csv", usecols=["name", "salary"])
print("Only name and salary:")
print(df_subset)
print()

# Load and set a specific column as the index
df_indexed = pd.read_csv("employees.csv", index_col="name")
print("With name as index:")
print(df_indexed)
```

**Expected Output:**
```
Only name and salary:
    name  salary
0  Alice   70000
1    Bob   55000
2  Carol   85000
3   Dave   62000
4    Eve   72000

With name as index:
       age      city  salary
name
Alice   30  New York   70000
Bob     25   Chicago   55000
Carol   35    Boston   85000
Dave    28   Seattle   62000
Eve     32    Denver   72000
```

---

## Loading JSON Data

**JSON** stands for JavaScript Object Notation. It stores data as key-value pairs. It is very common for web data and APIs.

> **JSON:** A text format for storing data using curly braces `{}` for objects and square brackets `[]` for lists. Keys and values are separated by colons.

Here is what JSON data looks like:

```json
[
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "Chicago"},
    {"name": "Carol", "age": 35, "city": "Boston"}
]
```

### Loading JSON with Pandas

```python
import pandas as pd
import json

# Create a sample JSON file
sample_json = [
    {"name": "Alice", "age": 30, "city": "New York", "salary": 70000},
    {"name": "Bob", "age": 25, "city": "Chicago", "salary": 55000},
    {"name": "Carol", "age": 35, "city": "Boston", "salary": 85000},
    {"name": "Dave", "age": 28, "city": "Seattle", "salary": 62000}
]

# Write to a JSON file
with open("employees.json", "w") as f:
    json.dump(sample_json, f)

# Load JSON into a DataFrame
df = pd.read_json("employees.json")

print("Data from JSON:")
print(df)
print()

# You can also load JSON from a string
json_string = '[{"product": "laptop", "price": 999}, {"product": "mouse", "price": 25}]'
df_products = pd.read_json(json_string)
print("Products:")
print(df_products)
```

**Expected Output:**
```
Data from JSON:
    name  age      city  salary
0  Alice   30  New York   70000
1    Bob   25   Chicago   55000
2  Carol   35    Boston   85000
3   Dave   28   Seattle   62000

Products:
  product  price
0  laptop    999
1   mouse     25
```

**Line-by-line explanation:**

- `import json` - Import Python's built-in JSON library for writing JSON files.
- `sample_json = [...]` - A Python list of dictionaries. Each dictionary is one record.
- `json.dump(sample_json, f)` - Write the Python data to a JSON file.
- `pd.read_json("employees.json")` - Pandas can read JSON files directly into a DataFrame.
- `pd.read_json(json_string)` - You can also pass a JSON string directly, without a file.

---

## Introduction to Kaggle: Free Datasets

**Kaggle** is a free platform where data scientists share datasets and compete in ML challenges. It has thousands of high-quality datasets on every topic imaginable.

> **Kaggle:** A free online platform owned by Google where you can find datasets, compete in ML competitions, and learn data science. Website: kaggle.com

### How to Use Kaggle

1. Go to kaggle.com and create a free account
2. Click "Datasets" in the navigation menu
3. Search for any topic (e.g., "housing prices", "titanic", "weather")
4. Download the dataset (usually a CSV file)
5. Load it with `pd.read_csv()`

### Popular Beginner Datasets on Kaggle

```
+------------------------------------------------------------------+
|              POPULAR KAGGLE DATASETS FOR BEGINNERS                |
|                                                                   |
|  Dataset              Rows      Task                              |
|  ---------------------------------------------------------------- |
|  Titanic              891       Predict survival (classification) |
|  House Prices          1,460    Predict price (regression)        |
|  Iris Flowers          150      Classify species (classification) |
|  MNIST Digits          70,000   Recognize digits (classification) |
|  Heart Disease          303     Predict disease (classification)  |
|  Wine Quality          6,497    Rate wine (regression)            |
+------------------------------------------------------------------+
```

---

## Using Built-in Datasets from scikit-learn

Scikit-learn comes with several built-in datasets. These are perfect for practice because you do not need to download anything.

### Available Datasets

```python
# See what datasets are available
from sklearn import datasets

# Small datasets (loaded into memory)
# datasets.load_iris()          - 150 flowers, 4 features
# datasets.load_wine()          - 178 wines, 13 features
# datasets.load_digits()        - 1,797 handwritten digits
# datasets.load_breast_cancer() - 569 tumors, 30 features

# You can also generate synthetic datasets
# datasets.make_classification() - Create fake classification data
# datasets.make_regression()     - Create fake regression data
```

### Loading the Iris Dataset

```python
from sklearn.datasets import load_iris

# Load the dataset
iris = load_iris()

# What is inside?
print("Type:", type(iris))
print("Keys:", iris.keys())
print()

# The data (features)
print("Data shape:", iris.data.shape)
print("First 3 rows:")
print(iris.data[:3])
print()

# The labels (target)
print("Target shape:", iris.target.shape)
print("First 10 labels:", iris.target[:10])
print()

# Feature names and target names
print("Feature names:", iris.feature_names)
print("Target names:", iris.target_names)
```

**Expected Output:**
```
Type: <class 'sklearn.utils._bunch.Bunch'>
Keys: dict_keys(['data', 'target', 'frame', 'target_names',
                  'DESCR', 'feature_names', 'filename',
                  'data_module'])

Data shape: (150, 4)
First 3 rows:
[[5.1 3.5 1.4 0.2]
 [4.9 3.  1.4 0.2]
 [4.7 3.2 1.3 0.2]]

Target shape: (150,)
First 10 labels: [0 0 0 0 0 0 0 0 0 0]

Feature names: ['sepal length (cm)', 'sepal width (cm)',
                'petal length (cm)', 'petal width (cm)']
Target names: ['setosa' 'versicolor' 'virginica']
```

**Line-by-line explanation:**

- `load_iris()` - Returns a Bunch object (like a dictionary). It contains the data, labels, and descriptions.
- `iris.data` - A NumPy array with shape (150, 4). That means 150 flowers, each with 4 measurements.
- `iris.data.shape` - The shape tells you (rows, columns). 150 rows and 4 columns.
- `iris.data[:3]` - The first 3 rows of data. Each row is one flower.
- `iris.target` - The labels. 0 = setosa, 1 = versicolor, 2 = virginica.
- `iris.feature_names` - The names of the 4 measurements (sepal length, sepal width, petal length, petal width).
- `iris.target_names` - The names of the 3 species.

### Converting to a Pandas DataFrame

Working with a Pandas DataFrame is often easier than raw NumPy arrays.

```python
from sklearn.datasets import load_iris
import pandas as pd

# Load iris
iris = load_iris()

# Convert to DataFrame
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['species'] = iris.target

# Map numbers to species names
species_map = {0: 'setosa', 1: 'versicolor', 2: 'virginica'}
df['species_name'] = df['species'].map(species_map)

print(df.head())
print()
print("Shape:", df.shape)
```

**Expected Output:**
```
   sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)  species species_name
0                5.1               3.5                1.4               0.2        0       setosa
1                4.9               3.0                1.4               0.2        0       setosa
2                4.7               3.2                1.3               0.2        0       setosa
3                4.6               3.1                1.5               0.2        0       setosa
4                5.0               3.6                1.4               0.2        0       setosa

Shape: (150, 6)
```

### Generating Synthetic Data

Sometimes you need custom data for testing. Scikit-learn can create it for you.

```python
from sklearn.datasets import make_classification
import pandas as pd

# Create a fake dataset with 200 samples and 4 features
X, y = make_classification(
    n_samples=200,       # 200 data points
    n_features=4,        # 4 columns
    n_informative=2,     # 2 columns actually matter
    n_redundant=1,       # 1 column is redundant
    n_classes=2,         # 2 categories (binary)
    random_state=42      # Same result every time
)

# Convert to DataFrame for easy viewing
df = pd.DataFrame(X, columns=['feature_1', 'feature_2',
                               'feature_3', 'feature_4'])
df['target'] = y

print("Shape:", df.shape)
print()
print("First 5 rows:")
print(df.head())
print()
print("Class distribution:")
print(df['target'].value_counts())
```

**Expected Output:**
```
Shape: (200, 5)

First 5 rows:
   feature_1  feature_2  feature_3  feature_4  target
0   0.886878  -0.414203   1.263610   0.573804       0
1   0.893680   1.025498   0.150783  -1.792567       0
2  -0.601327  -1.650800   0.082664  -1.131973       1
3  -2.265463  -0.186060  -1.119890  -0.668834       1
4   0.883931   0.498697   0.863498  -0.526907       0

Class distribution:
target
0    100
1    100
Name: count, dtype: int64
```

**Line-by-line explanation:**

- `make_classification(...)` - Creates fake classification data. You control how many samples, features, and classes.
- `n_samples=200` - Generate 200 data points (rows).
- `n_features=4` - Each data point has 4 features (columns).
- `n_informative=2` - Only 2 features actually help predict the target. The others add noise.
- `n_redundant=1` - 1 feature is a copy of another (redundant).
- `n_classes=2` - Two categories: 0 and 1.
- `random_state=42` - Seed for random number generator. Same seed = same data every time.
- `value_counts()` - Shows how many of each class we have. 100 of class 0 and 100 of class 1.

---

## Understanding Your Data: Essential Commands

Before you do anything with your data, you need to understand it. Pandas provides several commands for this.

Think of it like this: before you drive to a new city, you look at a map. Before you build an ML model, you look at your data.

### The Essential Data Exploration Commands

```python
import pandas as pd
from sklearn.datasets import load_iris

# Load iris into a DataFrame
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['species'] = iris.target

# 1. head() - See the first few rows
print("=== head() - First 5 rows ===")
print(df.head())
print()

# 2. tail() - See the last few rows
print("=== tail() - Last 3 rows ===")
print(df.tail(3))
print()

# 3. shape - How many rows and columns?
print("=== shape ===")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
print()

# 4. dtypes - What type is each column?
print("=== dtypes ===")
print(df.dtypes)
print()

# 5. info() - Overview of the DataFrame
print("=== info() ===")
df.info()
print()

# 6. describe() - Statistical summary
print("=== describe() ===")
print(df.describe())
```

**Expected Output:**
```
=== head() - First 5 rows ===
   sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)  species
0                5.1               3.5                1.4               0.2        0
1                4.9               3.0                1.4               0.2        0
2                4.7               3.2                1.3               0.2        0
3                4.6               3.1                1.5               0.2        0
4                5.0               3.6                1.4               0.2        0

=== tail() - Last 3 rows ===
     sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)  species
147                6.5               3.0                5.2               2.0        2
148                6.2               3.4                5.4               2.3        2
149                5.9               3.0                5.1               1.8        2

=== shape ===
Rows: 150
Columns: 5

=== dtypes ===
sepal length (cm)    float64
sepal width (cm)     float64
petal length (cm)    float64
petal width (cm)     float64
species                int64
dtype: object

=== info() ===
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 150 entries, 0 to 149
Data columns (total 5 columns):
 #   Column             Non-Null Count  Dtype
---  ------             --------------  -----
 0   sepal length (cm)  150 non-null    float64
 1   sepal width (cm)   150 non-null    float64
 2   petal length (cm)  150 non-null    float64
 3   petal width (cm)   150 non-null    float64
 4   species            150 non-null    int64
dtypes: float64(4), int64(1)
memory usage: 6.0 KB

=== describe() ===
       sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)     species
count         150.000000        150.000000         150.000000        150.000000  150.000000
mean            5.843333          3.057333           3.758000          1.199333    1.000000
std             0.828066          0.435866           1.765298          0.762238    0.819232
min             4.300000          2.000000           1.000000          0.100000    0.000000
25%             5.100000          2.800000           1.600000          0.300000    0.000000
50%             5.800000          3.000000           4.350000          1.300000    1.000000
75%             6.400000          3.300000           5.100000          1.800000    2.000000
max             7.900000          4.400000           6.900000          2.500000    2.000000
```

### What Each Command Tells You

```
+------------------------------------------------------------------+
|   COMMAND       WHAT IT DOES           WHY YOU NEED IT            |
|   ----------------------------------------------------------------|
|   head()        Shows first 5 rows     Quick peek at your data   |
|   tail()        Shows last 5 rows      Check end of data         |
|   shape         (rows, columns)        How big is the data?      |
|   dtypes        Data type per column   Numbers? Text? Dates?     |
|   info()        Full overview          Missing values? Types?    |
|   describe()    Statistics             Min, max, average, etc.   |
+------------------------------------------------------------------+
```

### Understanding describe() Output

The `describe()` function gives you eight statistics for each numeric column:

- **count** - How many non-missing values. If this is less than the total rows, you have missing data.
- **mean** - The average value. Add all values and divide by count.
- **std** - Standard deviation. Measures how spread out the values are. Higher = more spread.
- **min** - The smallest value.
- **25%** - The 25th percentile. 25% of values are below this number.
- **50%** - The median (middle value). Half the values are above, half below.
- **75%** - The 75th percentile. 75% of values are below this number.
- **max** - The largest value.

---

## Train/Test Split: Why We Hold Back Data

This is one of the most important concepts in machine learning.

### The Problem

Imagine a student who studies for an exam by memorizing the answer key. On the actual exam, they use those exact same questions. They score 100%.

Did they really learn the material? No. They just memorized the answers.

The same thing happens with ML models. If you train a model on ALL your data and then test it on the SAME data, it will look amazing. But it is just memorizing, not learning.

> **Overfitting:** When a model memorizes the training data instead of learning general patterns. It performs great on training data but poorly on new, unseen data.

### The Solution: Train/Test Split

Split your data into two parts:

1. **Training set (typically 80%):** The model learns from this data
2. **Testing set (typically 20%):** You evaluate the model on this data

The model NEVER sees the testing data during training. This gives you an honest measure of how well it will perform on new data.

```
+------------------------------------------------------------------+
|              TRAIN / TEST SPLIT                                   |
|                                                                   |
|   Your Full Dataset (100 samples)                                 |
|   +----------------------------------------------------+         |
|   |  Training Data (80 samples)  | Test Data (20)      |         |
|   |  Model learns from these     | Model tested on     |         |
|   |                              | these (never seen)   |         |
|   +----------------------------------------------------+         |
|                                                                   |
|   Step 1: Train model on training data                            |
|   Step 2: Predict on test data                                    |
|   Step 3: Compare predictions to actual answers                   |
|   Step 4: Calculate accuracy                                      |
+------------------------------------------------------------------+
```

### Using train_test_split

Scikit-learn makes splitting easy with `train_test_split`.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Load data
iris = load_iris()
X = iris.data    # Features
y = iris.target  # Labels

print("Full dataset:")
print("  X shape:", X.shape)
print("  y shape:", y.shape)
print()

# Split: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,       # 20% for testing
    random_state=42      # Same split every time
)

print("After split:")
print("  X_train shape:", X_train.shape)
print("  X_test shape:", X_test.shape)
print("  y_train shape:", y_train.shape)
print("  y_test shape:", y_test.shape)
print()

# Verify the split
total = len(X_train) + len(X_test)
print(f"Training: {len(X_train)} ({len(X_train)/total*100:.0f}%)")
print(f"Testing:  {len(X_test)} ({len(X_test)/total*100:.0f}%)")
```

**Expected Output:**
```
Full dataset:
  X shape: (150, 4)
  y shape: (150,)

After split:
  X_train shape: (120, 4)
  X_test shape: (30, 4)
  y_train shape: (120,)
  y_test shape: (30,)

Training: 120 (80%)
Testing:  30 (20%)
```

**Line-by-line explanation:**

- `X = iris.data` - The features (input). Capital X by convention.
- `y = iris.target` - The labels (output). Lowercase y by convention.
- `train_test_split(X, y, test_size=0.2, random_state=42)` - Split both X and y into training and testing sets. It returns four things: X_train, X_test, y_train, y_test.
- `test_size=0.2` - Use 20% for testing. The remaining 80% is for training. Common splits are 80/20 or 70/30.
- `random_state=42` - A seed for the random shuffle. The data is shuffled before splitting. Using the same seed gives the same split every time, which is important for reproducibility.

### The stratify Parameter

When your classes are imbalanced (more of one class than another), use `stratify` to ensure each set has the same proportion of classes.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import numpy as np

iris = load_iris()
X = iris.data
y = iris.target

# Without stratify
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# With stratify
X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Original class distribution:")
unique, counts = np.unique(y, return_counts=True)
for u, c in zip(unique, counts):
    print(f"  Class {u}: {c} ({c/len(y)*100:.1f}%)")

print()
print("Test set WITHOUT stratify:")
unique, counts = np.unique(y_test, return_counts=True)
for u, c in zip(unique, counts):
    print(f"  Class {u}: {c} ({c/len(y_test)*100:.1f}%)")

print()
print("Test set WITH stratify:")
unique, counts = np.unique(y_test_s, return_counts=True)
for u, c in zip(unique, counts):
    print(f"  Class {u}: {c} ({c/len(y_test_s)*100:.1f}%)")
```

**Expected Output:**
```
Original class distribution:
  Class 0: 50 (33.3%)
  Class 1: 50 (33.3%)
  Class 2: 50 (33.3%)

Test set WITHOUT stratify:
  Class 0: 10 (33.3%)
  Class 1: 9 (30.0%)
  Class 2: 11 (36.7%)

Test set WITH stratify:
  Class 0: 10 (33.3%)
  Class 1: 10 (33.3%)
  Class 2: 10 (33.3%)
```

With `stratify=y`, each class is perfectly represented in both the training and testing sets. This is especially important when one class is much rarer than others.

---

## Putting It All Together: Complete Data Loading Workflow

Here is a complete workflow from loading to splitting.

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris

# ============================================
# STEP 1: Load the data
# ============================================
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['species'] = iris.target

print("Step 1: Data loaded")
print(f"Shape: {df.shape}")
print()

# ============================================
# STEP 2: Quick exploration
# ============================================
print("Step 2: Quick look at the data")
print(df.head())
print()

print("Data types:")
print(df.dtypes)
print()

print("Statistical summary:")
print(df.describe())
print()

print("Missing values:")
print(df.isnull().sum())
print()

print("Class distribution:")
print(df['species'].value_counts())
print()

# ============================================
# STEP 3: Separate features and target
# ============================================
X = df.drop('species', axis=1)  # Everything except 'species'
y = df['species']               # Only the 'species' column

print("Step 3: Features and target separated")
print(f"Features shape: {X.shape}")
print(f"Target shape: {y.shape}")
print()

# ============================================
# STEP 4: Split into training and testing
# ============================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Step 4: Data split complete")
print(f"Training set: {X_train.shape[0]} samples")
print(f"Testing set:  {X_test.shape[0]} samples")
print()
print("Ready for machine learning!")
```

**Expected Output:**
```
Step 1: Data loaded
Shape: (150, 5)

Step 2: Quick look at the data
   sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)  species
0                5.1               3.5                1.4               0.2        0
1                4.9               3.0                1.4               0.2        0
2                4.7               3.2                1.3               0.2        0
3                4.6               3.1                1.5               0.2        0
4                5.0               3.6                1.4               0.2        0

Data types:
sepal length (cm)    float64
sepal width (cm)     float64
petal length (cm)    float64
petal width (cm)     float64
species                int64
dtype: object

Statistical summary:
       sepal length (cm)  sepal width (cm)  ...  petal width (cm)     species
count         150.000000        150.000000  ...        150.000000  150.000000
mean            5.843333          3.057333  ...          1.199333    1.000000
std             0.828066          0.435866  ...          0.762238    0.819232
min             4.300000          2.000000  ...          0.100000    0.000000
25%             5.100000          2.800000  ...          0.300000    0.000000
50%             5.800000          3.000000  ...          1.300000    1.000000
75%             6.400000          3.300000  ...          1.800000    2.000000
max             7.900000          4.400000  ...          2.500000    2.000000

Missing values:
sepal length (cm)    0
sepal width (cm)     0
petal length (cm)    0
petal width (cm)     0
species              0
dtype: int64

Class distribution:
species
0    50
1    50
2    50
Name: count, dtype: int64

Step 3: Features and target separated
Features shape: (150, 4)
Target shape: (150,)

Step 4: Data split complete
Training set: 120 samples
Testing set:  30 samples

Ready for machine learning!
```

---

## Common Mistakes

1. **Not exploring data before modeling.** Always run `head()`, `shape`, `info()`, and `describe()` first. You need to know what you are working with.

2. **Forgetting to split data.** If you train and test on the same data, your accuracy will be misleadingly high. Always use `train_test_split`.

3. **Using too little test data.** If your test set is too small, your accuracy estimate will be unreliable. 20% is a good default.

4. **Not setting random_state.** Without `random_state`, your split changes every time you run the code. This makes debugging hard. Always set it for reproducibility.

5. **Forgetting to separate features and target.** The model needs X (features) and y (target) as separate inputs. Do not feed the entire DataFrame (including the answer column) to the model.

6. **Not checking for missing values.** Missing values can crash your model or produce bad results. Always check with `df.isnull().sum()`.

---

## Best Practices

1. **Always explore before modeling.** Run the six essential commands: `head()`, `tail()`, `shape`, `dtypes`, `info()`, `describe()`.

2. **Use consistent variable names.** Use `df` for DataFrames, `X` for features, `y` for target, `X_train/X_test/y_train/y_test` for splits.

3. **Set random_state everywhere.** This ensures reproducibility. Use the same number (42 is a common choice) everywhere.

4. **Use stratify for classification.** When splitting classification data, use `stratify=y` to maintain class proportions.

5. **Document your data source.** Write a comment noting where the data came from, when it was downloaded, and any preprocessing steps.

6. **Start with built-in datasets.** When learning, use scikit-learn's built-in datasets. They are clean, well-documented, and ready to use.

---

## Quick Summary

Data is the fuel for machine learning. It comes from CSV files, JSON files, databases, APIs, and free platforms like Kaggle. Pandas is the essential tool for loading and exploring data in Python. Before building any model, you must understand your data using commands like head(), shape, info(), and describe(). The most critical concept is the train/test split: always hold back a portion of your data (typically 20%) to test your model honestly. Use scikit-learn's train_test_split function with random_state for reproducibility and stratify for classification problems.

---

## Key Points to Remember

- **CSV files** are the most common data format. Load them with `pd.read_csv()`.
- **JSON files** store key-value data. Load them with `pd.read_json()`.
- **Kaggle** (kaggle.com) has thousands of free datasets for practice.
- **scikit-learn** has built-in datasets: `load_iris()`, `load_wine()`, `load_digits()`, and more.
- **head()** shows the first 5 rows. **tail()** shows the last 5.
- **shape** tells you (rows, columns).
- **info()** shows column types and missing value counts.
- **describe()** gives statistical summaries (mean, min, max, etc.).
- **Train/test split** divides data into learning data and evaluation data.
- **test_size=0.2** means 20% for testing, 80% for training.
- **random_state** ensures the same split every time.
- **stratify=y** maintains class proportions in both sets.
- Always explore your data BEFORE building a model.

---

## Practice Questions

### Question 1
What does `pd.read_csv("data.csv")` return?

**Answer:** It returns a Pandas **DataFrame**, which is a two-dimensional table with rows and columns. Each column has a name (from the CSV header) and a data type. The rows are indexed starting from 0.

### Question 2
You have a dataset with 1,000 rows. You use `train_test_split` with `test_size=0.3`. How many rows will be in the training set and testing set?

**Answer:** The training set will have **700 rows** (70% of 1,000) and the testing set will have **300 rows** (30% of 1,000).

### Question 3
Why should you NOT test your model on the same data you used to train it?

**Answer:** Because the model may have **memorized** the training data (overfitting) rather than learning general patterns. Testing on the same data gives a misleadingly high accuracy. It is like a student scoring 100% on an exam when they had the answer key. You need to test on **unseen data** to get an honest measure of performance.

### Question 4
What is the purpose of the `random_state` parameter in `train_test_split`?

**Answer:** The `random_state` parameter sets a **seed for the random number generator**. The data is shuffled before splitting, and the seed controls the shuffle. Using the same `random_state` value (like 42) ensures you get the **exact same split** every time you run the code. This is important for **reproducibility** -- other people can reproduce your results.

### Question 5
What does `df.describe()` show you?

**Answer:** `df.describe()` shows a **statistical summary** of each numeric column. It includes: count (non-missing values), mean (average), std (standard deviation), min (smallest value), 25th percentile, 50th percentile (median), 75th percentile, and max (largest value). It helps you quickly understand the range and distribution of your data.

---

## Exercises

### Exercise 1: Load and Explore a Dataset

Load the Wine dataset from scikit-learn (`from sklearn.datasets import load_wine`). Convert it to a Pandas DataFrame. Then answer these questions using Python code:

1. How many wine samples are there?
2. How many features does each sample have?
3. What are the feature names?
4. How many classes are there?
5. What is the mean alcohol content? (Hint: the first feature is alcohol)

### Exercise 2: Practice Train/Test Split

Using the Wine dataset from Exercise 1:

1. Split the data into 70% training and 30% testing
2. Print the number of samples in each set
3. Check the class distribution in both sets (with and without stratify)
4. Train a `DecisionTreeClassifier` on the training set
5. Calculate accuracy on the test set

### Exercise 3: Load Your Own CSV

Create a CSV file with at least 10 rows of data about any topic you like (movies, books, sports teams, etc.). Include at least 4 columns with a mix of numbers and text. Then:

1. Load it with `pd.read_csv()`
2. Run all six exploration commands (head, tail, shape, dtypes, info, describe)
3. Write a brief summary of what you learned about your data

---

## What Is Next?

You now know how to find data, load it, explore it, and split it. But looking at numbers in tables only tells you so much.

In Chapter 3, you will learn Exploratory Data Analysis (EDA). You will create visualizations -- histograms, scatter plots, heatmaps, and box plots -- that reveal patterns, relationships, and problems in your data. Visualizing data is like reading a map before a road trip. It shows you where you are going and what obstacles to watch for.
