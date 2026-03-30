# Chapter 14: Pandas Part 1 — Excel in Python

## What You Will Learn

- What Pandas is and why it is essential for data work
- The two main data structures: Series and DataFrame
- How to create DataFrames from dictionaries and lists
- How to read CSV files with `read_csv`
- How to explore data: head, tail, info, describe, shape, columns, dtypes
- How to select columns and rows
- How to filter data with conditions
- How to sort data
- How to calculate basic statistics on columns

## Why This Chapter Matters

If you have ever used Excel or Google Sheets, you know how useful it is to organize data in rows and columns. Pandas gives you the same power, but inside Python.

Why not just use Excel?

- Excel struggles with large files (millions of rows). Pandas handles them easily.
- Excel requires clicking. Pandas uses code — so you can repeat your work automatically.
- Pandas connects directly to Python's entire ecosystem — NumPy, visualization, machine learning.

Almost every data science project starts with Pandas. It is your most important tool for loading, cleaning, and exploring data.

Think of Pandas as **Excel on steroids, controlled by code**.

---

## 14.1 What Is Pandas?

Pandas is a Python library for working with **structured data** — data organized in rows and columns, like a spreadsheet or database table.

It is built on top of NumPy, so it is fast. But it adds labels, column names, and many convenience features that NumPy does not have.

### Installing Pandas

```bash
pip install pandas
```

### Importing Pandas

```python
import pandas as pd
```

Everyone uses `pd` as the alias. This is a universal convention.

---

## 14.2 The Two Main Data Structures

Pandas has two main data structures:

```
Series (1D):              DataFrame (2D):

Index | Value             |  Name  |  Age  | City
------+-------            +--------+-------+----------
  0   | Alice               Alice  |  25   | New York
  1   | Bob                 Bob    |  30   | London
  2   | Charlie             Charlie|  35   | Paris

One column                Multiple columns
Like a single              Like a spreadsheet
column in Excel            or table
```

### Series — A Single Column

A Series is like a labeled list. Each value has an index (label).

```python
import pandas as pd

# Create a Series from a list
ages = pd.Series([25, 30, 35, 28])
print(ages)
```

**Expected Output:**
```
0    25
1    30
2    35
3    28
dtype: int64
```

**Line-by-line explanation:**

- `pd.Series([25, 30, 35, 28])` — Creates a Series with automatic numeric indices (0, 1, 2, 3).
- The left column (0, 1, 2, 3) is the **index**.
- The right column (25, 30, 35, 28) is the **data**.
- `dtype: int64` tells you the data type.

### Series with Custom Labels

```python
import pandas as pd

ages = pd.Series([25, 30, 35], index=["Alice", "Bob", "Charlie"])
print(ages)
print(ages["Bob"])
```

**Expected Output:**
```
Alice      25
Bob        30
Charlie    35
dtype: int64
30
```

### DataFrame — A Table

A DataFrame is a table. It has rows and columns, just like a spreadsheet.

```python
import pandas as pd

data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "London", "Paris"]
}

df = pd.DataFrame(data)
print(df)
```

**Expected Output:**
```
      Name  Age      City
0    Alice   25  New York
1      Bob   30    London
2  Charlie   35     Paris
```

**Line-by-line explanation:**

- `data = {...}` — A dictionary where each key becomes a column name and each value (a list) becomes the column data.
- `pd.DataFrame(data)` — Converts the dictionary into a DataFrame.
- The numbers on the left (0, 1, 2) are the index — automatically assigned.

```
How a DataFrame is structured:

              Column     Column     Column
              "Name"     "Age"      "City"
              |          |          |
Index 0 -->   Alice      25         New York
Index 1 -->   Bob        30         London
Index 2 -->   Charlie    35         Paris
```

---

## 14.3 Creating DataFrames

### From a Dictionary (most common)

```python
import pandas as pd

students = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Math": [95, 82, 90, 78],
    "Science": [88, 95, 85, 92],
    "English": [92, 78, 88, 85]
})
print(students)
```

**Expected Output:**
```
      Name  Math  Science  English
0    Alice    95       88       92
1      Bob    82       95       78
2  Charlie    90       85       88
3    Diana    78       92       85
```

### From a List of Dictionaries

```python
import pandas as pd

people = [
    {"Name": "Alice", "Age": 25, "City": "New York"},
    {"Name": "Bob", "Age": 30, "City": "London"},
    {"Name": "Charlie", "Age": 35, "City": "Paris"}
]

df = pd.DataFrame(people)
print(df)
```

**Expected Output:**
```
      Name  Age      City
0    Alice   25  New York
1      Bob   30    London
2  Charlie   35     Paris
```

### From a List of Lists

```python
import pandas as pd

data = [
    ["Alice", 25, "New York"],
    ["Bob", 30, "London"],
    ["Charlie", 35, "Paris"]
]

df = pd.DataFrame(data, columns=["Name", "Age", "City"])
print(df)
```

**Expected Output:**
```
      Name  Age      City
0    Alice   25  New York
1      Bob   30    London
2  Charlie   35     Paris
```

When using lists of lists, you must provide column names with the `columns` parameter.

---

## 14.4 Reading CSV Files

CSV (Comma-Separated Values) is the most common format for data files. Pandas can read them with a single line.

### Example: Reading a CSV file

```python
import pandas as pd

# If you have a file called "data.csv":
df = pd.read_csv("data.csv")
print(df)
```

### What a CSV file looks like

A CSV file is just a text file where values are separated by commas:

```
Name,Age,City,Salary
Alice,25,New York,70000
Bob,30,London,85000
Charlie,35,Paris,92000
Diana,28,Tokyo,78000
```

```
CSV file          -->       DataFrame
(text file)                 (Python table)

Name,Age,City               | Name    | Age | City
Alice,25,New York           | Alice   | 25  | New York
Bob,30,London               | Bob     | 30  | London
Charlie,35,Paris             | Charlie | 35  | Paris
```

### Common read_csv Options

```python
import pandas as pd

# Basic read
df = pd.read_csv("data.csv")

# Use a different separator (like tabs)
df = pd.read_csv("data.tsv", sep="\t")

# Skip the first few rows
df = pd.read_csv("data.csv", skiprows=2)

# Only read specific columns
df = pd.read_csv("data.csv", usecols=["Name", "Age"])

# Set a specific column as the index
df = pd.read_csv("data.csv", index_col="Name")

# Handle missing values
df = pd.read_csv("data.csv", na_values=["N/A", "missing", ""])
```

### Creating a Sample CSV to Practice

If you do not have a CSV file, you can create one with Python:

```python
import pandas as pd

# Create a DataFrame
data = {
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Age": [25, 30, 35, 28, 22],
    "City": ["New York", "London", "Paris", "Tokyo", "Berlin"],
    "Salary": [70000, 85000, 92000, 78000, 65000]
}

df = pd.DataFrame(data)

# Save to CSV
df.to_csv("employees.csv", index=False)
print("File saved!")

# Read it back
df2 = pd.read_csv("employees.csv")
print(df2)
```

**Expected Output:**
```
File saved!
      Name  Age      City  Salary
0    Alice   25  New York   70000
1      Bob   30    London   85000
2  Charlie   35     Paris   92000
3    Diana   28     Tokyo   78000
4      Eve   22    Berlin   65000
```

---

## 14.5 Exploring Your Data

When you load a dataset, the first thing you should do is explore it. Pandas gives you many tools for this.

### Setting Up Example Data

```python
import pandas as pd
import numpy as np

# Let us create a sample dataset
np.random.seed(42)
data = {
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve",
             "Frank", "Grace", "Henry", "Ivy", "Jack"],
    "Age": [25, 30, 35, 28, 22, 45, 33, 29, 27, 31],
    "Department": ["Sales", "IT", "IT", "HR", "Sales",
                    "IT", "HR", "Sales", "IT", "HR"],
    "Salary": [55000, 72000, 68000, 61000, 48000,
               95000, 70000, 58000, 64000, 67000],
    "Experience": [2, 5, 8, 3, 1, 15, 7, 4, 3, 6]
}

df = pd.DataFrame(data)
```

### head() and tail() — Peek at the Data

```python
# First 5 rows (default)
print(df.head())
```

**Expected Output:**
```
      Name  Age Department  Salary  Experience
0    Alice   25      Sales   55000           2
1      Bob   30         IT   72000           5
2  Charlie   35         IT   68000           8
3    Diana   28         HR   61000           3
4      Eve   22      Sales   48000           1
```

```python
# Last 3 rows
print(df.tail(3))
```

**Expected Output:**
```
    Name  Age Department  Salary  Experience
7  Henry   29      Sales   58000           4
8    Ivy   27         IT   64000           3
9   Jack   31         HR   67000           6
```

### shape — How Big Is the Data?

```python
print(df.shape)
```

**Expected Output:**
```
(10, 5)
```

This means 10 rows and 5 columns.

### columns — What Columns Exist?

```python
print(df.columns)
```

**Expected Output:**
```
Index(['Name', 'Age', 'Department', 'Salary', 'Experience'], dtype='object')
```

### dtypes — What Type Is Each Column?

```python
print(df.dtypes)
```

**Expected Output:**
```
Name          object
Age            int64
Department    object
Salary         int64
Experience     int64
dtype: object
```

`object` means text (strings). `int64` means integers.

### info() — Everything at a Glance

```python
df.info()
```

**Expected Output:**
```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 10 entries, 0 to 9
Data columns (total 5 columns):
 #   Column      Non-Null Count  Dtype
---  ------      --------------  -----
 0   Name        10 non-null     object
 1   Age         10 non-null     int64
 2   Department  10 non-null     object
 3   Salary      10 non-null     int64
 4   Experience  10 non-null     int64
dtypes: int64(3), object(2)
memory usage: 528.0+ bytes
```

**Line-by-line explanation:**

- `RangeIndex: 10 entries` — 10 rows, indexed 0 to 9.
- `Data columns (total 5 columns)` — 5 columns.
- `Non-Null Count` — How many values are not missing. 10 non-null means no missing data.
- `Dtype` — Data type of each column.
- `memory usage` — How much memory the DataFrame uses.

### describe() — Statistics for Number Columns

```python
print(df.describe())
```

**Expected Output:**
```
             Age        Salary  Experience
count  10.000000     10.000000   10.000000
mean   30.500000  65800.000000    5.400000
std     6.276942  12816.474486    3.893654
min    22.000000  48000.000000    1.000000
25%    27.250000  57250.000000    2.750000
50%    29.500000  65500.000000    4.500000
75%    33.500000  69500.000000    7.250000
max    45.000000  95000.000000   15.000000
```

```
What describe() tells you:

count  = number of values (not missing)
mean   = average
std    = standard deviation (spread)
min    = smallest value
25%    = 25th percentile (lower quarter)
50%    = median (middle value)
75%    = 75th percentile (upper quarter)
max    = largest value
```

---

## 14.6 Selecting Columns

### Selecting a Single Column

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "London", "Paris"]
})

# Method 1: Dot notation
print(df.Name)

# Method 2: Bracket notation (preferred)
print(df["Age"])
```

**Expected Output:**
```
0      Alice
1        Bob
2    Charlie
Name: Name, dtype: object
0    25
1    30
2    35
Name: Age, dtype: int64
```

**Note:** Bracket notation is preferred because:
- It works with column names that have spaces: `df["First Name"]`
- It works with names that match Python keywords: `df["class"]`
- It is less ambiguous

### Selecting Multiple Columns

```python
subset = df[["Name", "City"]]
print(subset)
```

**Expected Output:**
```
      Name      City
0    Alice  New York
1      Bob    London
2  Charlie     Paris
```

Use double brackets `[[ ]]` for multiple columns. The outer brackets are for selection. The inner brackets define a list of column names.

```
Single column:   df["Name"]        --> returns a Series
Multiple cols:   df[["Name","Age"]] --> returns a DataFrame
                    ^            ^
                    inner brackets = list
```

---

## 14.7 Selecting Rows with loc and iloc

Pandas has two ways to select rows:

- **`loc`** — Select by **label** (name/index value)
- **`iloc`** — Select by **integer position** (0, 1, 2, ...)

Think of it this way:

```
loc  = LOCation by label     (like finding a book by title)
iloc = Integer LOCation       (like finding a book by shelf position)
```

### Setting Up Example Data

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Age": [25, 30, 35, 28, 22],
    "City": ["New York", "London", "Paris", "Tokyo", "Berlin"],
    "Salary": [70000, 85000, 92000, 78000, 65000]
})
print(df)
```

**Expected Output:**
```
      Name  Age      City  Salary
0    Alice   25  New York   70000
1      Bob   30    London   85000
2  Charlie   35     Paris   92000
3    Diana   28     Tokyo   78000
4      Eve   22    Berlin   65000
```

### iloc — Select by Position

```python
# First row
print(df.iloc[0])
```

**Expected Output:**
```
Name       Alice
Age           25
City    New York
Salary     70000
Name: 0, dtype: object
```

```python
# Rows 1 to 3
print(df.iloc[1:4])
```

**Expected Output:**
```
      Name  Age    City  Salary
1      Bob   30  London   85000
2  Charlie   35   Paris   92000
3    Diana   28   Tokyo   78000
```

```python
# Specific rows and columns
# Rows 0 and 2, Columns 0 and 2
print(df.iloc[[0, 2], [0, 2]])
```

**Expected Output:**
```
      Name      City
0    Alice  New York
2  Charlie     Paris
```

### loc — Select by Label

```python
# Row with index label 0
print(df.loc[0])
```

**Expected Output:**
```
Name       Alice
Age           25
City    New York
Salary     70000
Name: 0, dtype: object
```

```python
# Rows 1 to 3 (inclusive with loc!)
print(df.loc[1:3])
```

**Expected Output:**
```
      Name  Age    City  Salary
1      Bob   30  London   85000
2  Charlie   35   Paris   92000
3    Diana   28   Tokyo   78000
```

```python
# Select specific rows and columns by name
print(df.loc[0:2, ["Name", "Salary"]])
```

**Expected Output:**
```
      Name  Salary
0    Alice   70000
1      Bob   85000
2  Charlie   92000
```

### Key Difference: loc vs iloc with slicing

```
iloc[1:3]  -->  rows at positions 1 and 2 (end excluded)
loc[1:3]   -->  rows with labels 1, 2, AND 3 (end included!)

iloc follows Python slicing rules (end excluded)
loc includes BOTH endpoints
```

---

## 14.8 Filtering with Conditions

This is one of the most powerful features of Pandas. You can select rows based on conditions.

### Example: Simple Filter

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Age": [25, 30, 35, 28, 22],
    "Department": ["Sales", "IT", "IT", "HR", "Sales"],
    "Salary": [70000, 85000, 92000, 78000, 65000]
})

# People older than 28
old_enough = df[df["Age"] > 28]
print(old_enough)
```

**Expected Output:**
```
      Name  Age Department  Salary
1      Bob   30         IT   85000
2  Charlie   35         IT   92000
```

**Line-by-line explanation:**

- `df["Age"] > 28` — Creates a True/False Series: `[False, True, True, False, False]`.
- `df[df["Age"] > 28]` — Uses the True/False Series to filter. Only rows where the condition is True are kept.

```
How filtering works:

df["Age"] > 28:

Index | Age | > 28?
------+-----+------
  0   | 25  | False   <-- excluded
  1   | 30  | True    <-- kept
  2   | 35  | True    <-- kept
  3   | 28  | False   <-- excluded
  4   | 22  | False   <-- excluded
```

### Multiple Conditions

```python
# IT department AND salary above 80000
result = df[(df["Department"] == "IT") & (df["Salary"] > 80000)]
print(result)
```

**Expected Output:**
```
      Name  Age Department  Salary
1      Bob   30         IT   85000
2  Charlie   35         IT   92000
```

```python
# Sales OR HR department
result = df[(df["Department"] == "Sales") | (df["Department"] == "HR")]
print(result)
```

**Expected Output:**
```
     Name  Age Department  Salary
0   Alice   25      Sales   70000
3   Diana   28         HR   78000
4     Eve   22      Sales   65000
```

**Important rules for multiple conditions:**

- Use `&` for AND (not `and`)
- Use `|` for OR (not `or`)
- Wrap each condition in parentheses `()`

### Using isin() for Multiple Values

```python
# Departments in Sales or HR (cleaner way)
result = df[df["Department"].isin(["Sales", "HR"])]
print(result)
```

**Expected Output:**
```
     Name  Age Department  Salary
0   Alice   25      Sales   70000
3   Diana   28         HR   78000
4     Eve   22      Sales   65000
```

### String Conditions

```python
# Names that start with "A"
result = df[df["Name"].str.startswith("A")]
print(result)

# Names that contain "li"
result = df[df["Name"].str.contains("li")]
print(result)
```

**Expected Output:**
```
    Name  Age Department  Salary
0  Alice   25      Sales   70000
      Name  Age Department  Salary
0    Alice   25      Sales   70000
2  Charlie   35         IT   92000
```

---

## 14.9 Sorting Data

### sort_values — Sort by a Column

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Age": [25, 30, 35, 28, 22],
    "Salary": [70000, 85000, 92000, 78000, 65000]
})

# Sort by Age (ascending)
print(df.sort_values("Age"))
```

**Expected Output:**
```
      Name  Age  Salary
4      Eve   22   65000
0    Alice   25   70000
3    Diana   28   78000
1      Bob   30   85000
2  Charlie   35   92000
```

```python
# Sort by Salary (descending)
print(df.sort_values("Salary", ascending=False))
```

**Expected Output:**
```
      Name  Age  Salary
2  Charlie   35   92000
1      Bob   30   85000
3    Diana   28   78000
0    Alice   25   70000
4      Eve   22   65000
```

### Sort by Multiple Columns

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Department": ["IT", "Sales", "IT", "Sales"],
    "Salary": [70000, 65000, 92000, 78000]
})

# Sort by Department first, then by Salary (descending)
result = df.sort_values(["Department", "Salary"], ascending=[True, False])
print(result)
```

**Expected Output:**
```
      Name Department  Salary
2  Charlie         IT   92000
0    Alice         IT   70000
3    Diana      Sales   78000
1      Bob      Sales   65000
```

---

## 14.10 Basic Statistics

Pandas makes it easy to calculate statistics on columns.

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "Salary": [70000, 85000, 92000, 78000, 65000],
    "Age": [25, 30, 35, 28, 22]
})

print(f"Mean salary:   ${df['Salary'].mean():,.0f}")
print(f"Median salary: ${df['Salary'].median():,.0f}")
print(f"Max salary:    ${df['Salary'].max():,.0f}")
print(f"Min salary:    ${df['Salary'].min():,.0f}")
print(f"Total salary:  ${df['Salary'].sum():,.0f}")
print(f"Std deviation: ${df['Salary'].std():,.0f}")
print(f"Count:          {df['Salary'].count()}")
```

**Expected Output:**
```
Mean salary:   $78,000
Median salary: $78,000
Max salary:    $92,000
Min salary:    $65,000
Total salary:  $390,000
Std deviation: $10,368
Count:          5
```

### Value Counts — Count Unique Values

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve",
             "Frank", "Grace", "Henry"],
    "Department": ["IT", "Sales", "IT", "HR", "Sales",
                    "IT", "HR", "Sales"]
})

print(df["Department"].value_counts())
```

**Expected Output:**
```
Sales    3
IT       3
HR       2
Name: Department, dtype: int64
```

### Unique Values

```python
print(df["Department"].unique())
print(f"Number of unique departments: {df['Department'].nunique()}")
```

**Expected Output:**
```
['IT' 'Sales' 'HR']
Number of unique departments: 3
```

---

## Common Mistakes

### Mistake 1: Using single brackets for multiple columns

```python
# Wrong (gives an error):
# df["Name", "Age"]

# Right:
df[["Name", "Age"]]
```

Use double brackets `[["col1", "col2"]]` for multiple columns.

### Mistake 2: Using `and`/`or` instead of `&`/`|`

```python
# Wrong:
# df[(df["Age"] > 25) and (df["Salary"] > 70000)]

# Right:
df[(df["Age"] > 25) & (df["Salary"] > 70000)]
```

Use `&` for AND and `|` for OR. Always wrap conditions in parentheses.

### Mistake 3: Forgetting that loc includes the endpoint

```python
# iloc[1:3] gives rows 1, 2 (not 3)
# loc[1:3] gives rows 1, 2, 3 (includes 3!)
```

### Mistake 4: Modifying a copy instead of the original

```python
# This might give a warning:
df[df["Age"] > 30]["Salary"] = 100000   # Does NOT work!

# Do this instead:
df.loc[df["Age"] > 30, "Salary"] = 100000  # Works!
```

### Mistake 5: Not checking data types after loading

```python
# Always check dtypes after loading data:
df = pd.read_csv("data.csv")
print(df.dtypes)

# Numbers might be loaded as strings!
# Use df["column"] = pd.to_numeric(df["column"]) to fix
```

---

## Best Practices

1. **Always explore your data first.** Use `head()`, `info()`, `describe()`, and `shape` before doing anything else.
2. **Use bracket notation for column selection.** `df["Name"]` is more reliable than `df.Name`.
3. **Use `loc` and `iloc` for row selection.** They are explicit and avoid ambiguity.
4. **Check for missing values early.** Use `df.isnull().sum()` after loading data.
5. **Do not modify data in place unless you mean to.** Many Pandas operations return a new DataFrame.
6. **Use `value_counts()` to understand categorical columns.** It quickly shows the distribution.
7. **Name your DataFrames clearly.** Use names like `customers_df` or `sales_data`, not just `df`.
8. **Save your work.** Use `df.to_csv()` to save processed data.

---

## Quick Summary

| Function | What It Does | Example |
|---|---|---|
| `pd.DataFrame()` | Create a DataFrame | `pd.DataFrame({"A": [1,2]})` |
| `pd.read_csv()` | Read a CSV file | `pd.read_csv("file.csv")` |
| `.head()` | First N rows | `df.head(5)` |
| `.tail()` | Last N rows | `df.tail(3)` |
| `.shape` | (rows, columns) | `df.shape` |
| `.info()` | Column types and counts | `df.info()` |
| `.describe()` | Statistics summary | `df.describe()` |
| `.columns` | List of column names | `df.columns` |
| `.dtypes` | Data types of columns | `df.dtypes` |
| `df["col"]` | Select a column | `df["Age"]` |
| `df[["a","b"]]` | Select columns | `df[["Name","Age"]]` |
| `.loc[]` | Select by label | `df.loc[0:2, "Name"]` |
| `.iloc[]` | Select by position | `df.iloc[0:2, 0:3]` |
| `.sort_values()` | Sort rows | `df.sort_values("Age")` |
| `.value_counts()` | Count unique values | `df["Col"].value_counts()` |

---

## Key Points to Remember

1. Pandas is built on NumPy and designed for tabular data.
2. A Series is a single column. A DataFrame is a table (multiple columns).
3. `pd.read_csv()` reads CSV files into a DataFrame.
4. Always explore data first: `head()`, `info()`, `describe()`, `shape`.
5. Use `df["column"]` for one column, `df[["col1", "col2"]]` for multiple.
6. `loc` uses labels (includes endpoint), `iloc` uses positions (excludes endpoint).
7. Filter with conditions: `df[df["Age"] > 30]`.
8. Use `&` for AND and `|` for OR in filters, with parentheses around each condition.
9. `sort_values()` sorts by one or more columns.
10. `describe()` gives you count, mean, std, min, max, and percentiles automatically.

---

## Practice Questions

**Question 1:** What is the difference between a Series and a DataFrame?

**Answer:** A Series is a one-dimensional labeled array — like a single column of data. A DataFrame is a two-dimensional table with rows and columns — like a spreadsheet. A DataFrame is essentially a collection of Series that share the same index.

**Question 2:** What is the difference between `df.loc[1:3]` and `df.iloc[1:3]`?

**Answer:** `df.loc[1:3]` selects rows with labels 1, 2, and 3 (endpoint included). `df.iloc[1:3]` selects rows at positions 1 and 2 (endpoint excluded, like normal Python slicing).

**Question 3:** How do you filter a DataFrame to show only rows where Age is greater than 25 AND Department is "IT"?

**Answer:** `df[(df["Age"] > 25) & (df["Department"] == "IT")]`. You must use `&` (not `and`) and wrap each condition in parentheses.

**Question 4:** What does `df.describe()` show you?

**Answer:** It shows summary statistics for all numeric columns: count (number of non-null values), mean, standard deviation, minimum, 25th percentile, median (50th percentile), 75th percentile, and maximum.

**Question 5:** What is wrong with this code: `df["Name", "Age"]`?

**Answer:** To select multiple columns, you need double brackets: `df[["Name", "Age"]]`. The outer brackets are the selection operator, and the inner brackets create a list of column names.

---

## Exercises

### Exercise 1: Employee Analysis

Create a DataFrame of employees and answer questions about it.

**Sample Solution:**

```python
import pandas as pd

employees = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve",
             "Frank", "Grace", "Henry", "Ivy", "Jack"],
    "Department": ["Engineering", "Marketing", "Engineering",
                   "HR", "Marketing", "Engineering", "HR",
                   "Marketing", "Engineering", "HR"],
    "Salary": [95000, 72000, 88000, 65000, 78000,
               102000, 68000, 75000, 91000, 62000],
    "Years": [5, 3, 7, 2, 4, 10, 3, 5, 6, 1]
})

# 1. How many employees are there?
print(f"Total employees: {len(employees)}")

# 2. What is the average salary?
print(f"Average salary: ${employees['Salary'].mean():,.0f}")

# 3. Who earns the most?
max_idx = employees["Salary"].idxmax()
print(f"Highest earner: {employees.loc[max_idx, 'Name']}")

# 4. How many people are in each department?
print(employees["Department"].value_counts())

# 5. Engineers with salary above 90000?
high_eng = employees[(employees["Department"] == "Engineering") &
                      (employees["Salary"] > 90000)]
print(f"\nHigh-earning engineers:\n{high_eng[['Name', 'Salary']]}")
```

### Exercise 2: CSV Practice

Create a CSV file, read it, explore it, and filter it.

**Sample Solution:**

```python
import pandas as pd

# Create sample data
products = pd.DataFrame({
    "Product": ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard",
                "Mouse", "Headphones", "Webcam", "Speaker", "SSD"],
    "Category": ["Computer", "Phone", "Tablet", "Accessory", "Accessory",
                 "Accessory", "Audio", "Accessory", "Audio", "Computer"],
    "Price": [999, 699, 449, 299, 79, 49, 199, 89, 149, 129],
    "Stock": [50, 120, 80, 65, 200, 300, 150, 90, 110, 180]
})

# Save to CSV
products.to_csv("products.csv", index=False)

# Read it back
df = pd.read_csv("products.csv")

# Explore
print("Shape:", df.shape)
print("\nFirst 3 rows:")
print(df.head(3))
print("\nStatistics:")
print(df.describe())

# Products over $200
expensive = df[df["Price"] > 200].sort_values("Price", ascending=False)
print(f"\nProducts over $200:\n{expensive[['Product', 'Price']]}")

# Accessories under $100
cheap_acc = df[(df["Category"] == "Accessory") & (df["Price"] < 100)]
print(f"\nCheap accessories:\n{cheap_acc[['Product', 'Price']]}")
```

### Exercise 3: Data Detective

Given a dataset, answer specific questions using Pandas operations.

**Sample Solution:**

```python
import pandas as pd
import numpy as np

# Create a dataset of student grades
np.random.seed(42)
students = pd.DataFrame({
    "Student": [f"Student_{i}" for i in range(1, 21)],
    "Math": np.random.randint(50, 100, 20),
    "Science": np.random.randint(50, 100, 20),
    "English": np.random.randint(50, 100, 20),
    "Grade": np.random.choice(["A", "B", "C", "D"], 20)
})

# 1. What is the average Math score?
print(f"Average Math: {students['Math'].mean():.1f}")

# 2. How many students got each grade?
print(f"\nGrade distribution:\n{students['Grade'].value_counts()}")

# 3. Top 5 students by Science score
top5 = students.sort_values("Science", ascending=False).head(5)
print(f"\nTop 5 in Science:\n{top5[['Student', 'Science']]}")

# 4. Students who scored above 80 in ALL subjects
high_achievers = students[
    (students["Math"] > 80) &
    (students["Science"] > 80) &
    (students["English"] > 80)
]
print(f"\nHigh achievers (80+ in all):\n{high_achievers[['Student', 'Math', 'Science', 'English']]}")
```

---

## What Is Next?

You now know the basics of Pandas — creating DataFrames, reading files, exploring data, selecting, filtering, and sorting. In the next chapter, we will go deeper with **Pandas Part 2**, where you will learn to handle missing data, group and aggregate data, merge tables together, and much more.
