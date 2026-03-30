# Chapter 15: Pandas Part 2 — Transforming and Combining Data

## What You Will Learn

- How to handle missing data (isna, dropna, fillna)
- How groupby works (split-apply-combine)
- Aggregation functions for grouped data
- How to merge and join DataFrames (inner, left, right, outer)
- How to create pivot tables
- How to use the apply function
- How to create new columns from existing ones
- String methods on columns
- How to save DataFrames to CSV and Excel

## Why This Chapter Matters

In Part 1, you learned to load, explore, filter, and sort data. But real-world data is messy. It has missing values, needs to be grouped and summarized, and often lives in multiple tables that must be combined.

This chapter teaches you the tools that data scientists use every day:

- **Missing data** — Real datasets always have gaps. You need to handle them.
- **Groupby** — "What is the average salary per department?" This kind of question requires grouping.
- **Merging** — Data often lives in separate tables. You need to combine them.
- **Transformations** — You will create new columns, clean strings, and reshape data.

After this chapter, you will be able to handle most real-world data tasks.

---

## 15.1 Handling Missing Data

Missing data is a fact of life. Surveys have unanswered questions. Sensors fail. Files get corrupted. Pandas uses `NaN` (Not a Number) to represent missing values.

```
What does missing data look like?

| Name    | Age  | City     |
|---------|------|----------|
| Alice   | 25   | New York |
| Bob     | NaN  | London   |    <-- Age is missing
| Charlie | 35   | NaN      |    <-- City is missing
| NaN     | 28   | Tokyo    |    <-- Name is missing
```

### Detecting Missing Values

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", None, "Eve"],
    "Age": [25, np.nan, 35, 28, np.nan],
    "City": ["New York", "London", np.nan, "Tokyo", "Berlin"],
    "Salary": [70000, 85000, np.nan, np.nan, 65000]
})

print(df)
print()

# Check for missing values
print(df.isna())
```

**Expected Output:**
```
      Name   Age      City   Salary
0    Alice  25.0  New York  70000.0
1      Bob   NaN    London  85000.0
2  Charlie  35.0       NaN      NaN
3     None  28.0     Tokyo      NaN
4      Eve   NaN    Berlin  65000.0

    Name    Age   City  Salary
0  False  False  False   False
1  False   True  False   False
2  False  False   True    True
3   True  False  False    True
4  False   True  False   False
```

### Counting Missing Values

```python
# How many missing values per column?
print(df.isna().sum())
```

**Expected Output:**
```
Name      1
Age       2
City      1
Salary    2
dtype: int64
```

```python
# Total missing values in the entire DataFrame
print(f"Total missing: {df.isna().sum().sum()}")
```

**Expected Output:**
```
Total missing: 6
```

### dropna — Remove Missing Data

```python
# Drop rows with ANY missing value
clean = df.dropna()
print(clean)
```

**Expected Output:**
```
    Name   Age      City   Salary
0  Alice  25.0  New York  70000.0
```

Only Alice's row has no missing values, so she is the only one left.

```python
# Drop rows where a SPECIFIC column is missing
clean = df.dropna(subset=["Age"])
print(clean)
```

**Expected Output:**
```
      Name   Age      City   Salary
0    Alice  25.0  New York  70000.0
2  Charlie  35.0       NaN      NaN
3     None  28.0     Tokyo      NaN
```

This keeps rows where Age is not missing, even if other columns have missing values.

### fillna — Fill Missing Values

Instead of removing missing data, you can fill it with a value.

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, np.nan, 35],
    "Salary": [70000, np.nan, np.nan]
})

# Fill with a specific value
print(df["Age"].fillna(0))

# Fill with the mean
print(df["Age"].fillna(df["Age"].mean()))

# Fill with the previous value (forward fill)
print(df["Salary"].fillna(method="ffill"))

# Fill different columns with different values
filled = df.fillna({"Age": df["Age"].mean(), "Salary": 0})
print(filled)
```

**Expected Output:**
```
0    25.0
1     0.0
2    35.0
Name: Age, dtype: float64
0    25.0
1    30.0
2    35.0
Name: Age, dtype: float64
0    70000.0
1    70000.0
2    70000.0
Name: Salary, dtype: float64
      Name   Age   Salary
0    Alice  25.0  70000.0
1      Bob  30.0      0.0
2  Charlie  35.0      0.0
```

```
Choosing how to fill missing values:

+-------------------+----------------------------------+
| Method            | When to use                      |
+-------------------+----------------------------------+
| fillna(0)         | When missing means "zero"        |
| fillna(mean)      | For numeric data, average is OK  |
| fillna(median)    | When data has outliers            |
| fillna("Unknown") | For text data                    |
| fillna(ffill)     | Time series (use last known)     |
| dropna()          | When you have plenty of data     |
+-------------------+----------------------------------+
```

---

## 15.2 Groupby — Split-Apply-Combine

The `groupby` operation is one of the most powerful tools in Pandas. It follows a simple pattern called **split-apply-combine**.

```
Split-Apply-Combine:

  Original Data        Split           Apply         Combine
+------+------+    +------+------+                +------+------+
| Dept | Sal  |    | IT   | 72k  |  mean(IT)      | IT   | 80k  |
| IT   | 72k  |    | IT   | 88k  |  = 80k         | HR   | 66.5k|
| HR   | 65k  |    +------+------+                | Sales| 72.5k|
| IT   | 88k  |    | HR   | 65k  |  mean(HR)      +------+------+
| Sales| 78k  |    | HR   | 68k  |  = 66.5k
| HR   | 68k  |    +------+------+
| Sales| 67k  |    | Sales| 78k  |  mean(Sales)
+------+------+    | Sales| 67k  |  = 72.5k
                   +------+------+
   1. SPLIT into     2. APPLY a        3. COMBINE
      groups            function           results
```

### Example 1: Basic groupby

```python
import pandas as pd

df = pd.DataFrame({
    "Department": ["IT", "HR", "IT", "Sales", "HR",
                   "IT", "Sales", "HR"],
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve",
             "Frank", "Grace", "Henry"],
    "Salary": [72000, 65000, 88000, 78000, 68000,
               95000, 67000, 61000]
})

# Average salary by department
result = df.groupby("Department")["Salary"].mean()
print(result)
```

**Expected Output:**
```
Department
HR       64666.666667
IT       85000.000000
Sales    72500.000000
Name: Salary, dtype: float64
```

**Line-by-line explanation:**

- `df.groupby("Department")` — Split the data into groups based on the Department column.
- `["Salary"]` — We only care about the Salary column.
- `.mean()` — Calculate the average for each group.

### Example 2: Multiple aggregations

```python
result = df.groupby("Department")["Salary"].agg(["mean", "min", "max", "count"])
print(result)
```

**Expected Output:**
```
                 mean    min    max  count
Department
HR          64666.67  61000  68000      3
IT          85000.00  72000  95000      3
Sales       72500.00  67000  78000      2
```

### Example 3: Group by multiple columns

```python
import pandas as pd

df = pd.DataFrame({
    "Department": ["IT", "IT", "HR", "HR", "IT", "HR"],
    "Level": ["Junior", "Senior", "Junior", "Senior", "Junior", "Senior"],
    "Salary": [60000, 95000, 55000, 80000, 65000, 85000]
})

result = df.groupby(["Department", "Level"])["Salary"].mean()
print(result)
```

**Expected Output:**
```
Department  Level
HR          Junior    55000.0
            Senior    82500.0
IT          Junior    62500.0
            Senior    95000.0
Name: Salary, dtype: float64
```

### Example 4: Custom aggregation with agg

```python
import pandas as pd

df = pd.DataFrame({
    "Department": ["IT", "HR", "IT", "Sales", "HR", "IT"],
    "Salary": [72000, 65000, 88000, 78000, 68000, 95000],
    "Age": [25, 30, 35, 28, 32, 45]
})

result = df.groupby("Department").agg(
    avg_salary=("Salary", "mean"),
    max_salary=("Salary", "max"),
    num_employees=("Salary", "count"),
    avg_age=("Age", "mean")
)
print(result)
```

**Expected Output:**
```
            avg_salary  max_salary  num_employees    avg_age
Department
HR             66500.0       68000              2  31.000000
IT             85000.0       95000              3  35.000000
Sales          78000.0       78000              1  28.000000
```

---

## 15.3 Merging DataFrames — Like SQL Joins

Often your data lives in multiple tables. Merging lets you combine them.

Think of it like connecting puzzle pieces. Each table has a common column (like an ID) that tells Pandas how to match rows.

```
Table 1 (Employees):      Table 2 (Departments):

| EmpID | Name    |       | DeptID | DeptName    |
|-------|---------|       |--------|-------------|
| 1     | Alice   |       | 101    | Engineering |
| 2     | Bob     |       | 102    | Marketing   |
| 3     | Charlie |       | 103    | Sales       |

                MERGE ON what?
                We need a common column!
```

### The Four Types of Joins

```
INNER JOIN:  Keep only matching rows from BOTH tables
LEFT JOIN:   Keep ALL rows from left table, matching from right
RIGHT JOIN:  Keep ALL rows from right table, matching from left
OUTER JOIN:  Keep ALL rows from BOTH tables

+-------+-------+     +-------+-------+
| Left  |       |     |       | Right |
| Table |  BOTH |     | BOTH  | Table |
|       |       |     |       |       |
+-------+-------+     +-------+-------+

Inner: Only BOTH
Left:  Left + BOTH
Right: BOTH + Right
Outer: Left + BOTH + Right
```

### Setting Up Example Data

```python
import pandas as pd

employees = pd.DataFrame({
    "EmpID": [1, 2, 3, 4, 5],
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "DeptID": [101, 102, 101, 103, 104]
})

departments = pd.DataFrame({
    "DeptID": [101, 102, 103, 105],
    "DeptName": ["Engineering", "Marketing", "Sales", "HR"]
})

print("Employees:")
print(employees)
print("\nDepartments:")
print(departments)
```

**Expected Output:**
```
Employees:
   EmpID     Name  DeptID
0      1    Alice     101
1      2      Bob     102
2      3  Charlie     101
3      4    Diana     103
4      5      Eve     104

Departments:
   DeptID     DeptName
0     101  Engineering
1     102    Marketing
2     103        Sales
3     105           HR
```

Notice: Eve has DeptID 104 (not in departments). HR has DeptID 105 (no employees).

### Inner Join — Only Matches

```python
result = pd.merge(employees, departments, on="DeptID", how="inner")
print(result)
```

**Expected Output:**
```
   EmpID     Name  DeptID     DeptName
0      1    Alice     101  Engineering
1      3  Charlie     101  Engineering
2      2      Bob     102    Marketing
3      4    Diana     103        Sales
```

Eve (DeptID 104) is gone — no matching department. HR (DeptID 105) is gone — no matching employee.

### Left Join — Keep All Left Rows

```python
result = pd.merge(employees, departments, on="DeptID", how="left")
print(result)
```

**Expected Output:**
```
   EmpID     Name  DeptID     DeptName
0      1    Alice     101  Engineering
1      2      Bob     102    Marketing
2      3  Charlie     101  Engineering
3      4    Diana     103        Sales
4      5      Eve     104          NaN
```

All employees are kept. Eve has NaN for DeptName because there is no matching department.

### Right Join — Keep All Right Rows

```python
result = pd.merge(employees, departments, on="DeptID", how="right")
print(result)
```

**Expected Output:**
```
   EmpID     Name  DeptID     DeptName
0    1.0    Alice     101  Engineering
1    3.0  Charlie     101  Engineering
2    2.0      Bob     102    Marketing
3    4.0    Diana     103        Sales
4    NaN      NaN     105           HR
```

All departments are kept. HR has NaN for EmpID and Name because there are no employees in HR.

### Outer Join — Keep Everything

```python
result = pd.merge(employees, departments, on="DeptID", how="outer")
print(result)
```

**Expected Output:**
```
   EmpID     Name  DeptID     DeptName
0    1.0    Alice     101  Engineering
1    3.0  Charlie     101  Engineering
2    2.0      Bob     102    Marketing
3    4.0    Diana     103        Sales
4    5.0      Eve     104          NaN
5    NaN      NaN     105           HR
```

Everything from both tables is kept. Missing values are filled with NaN.

### When Column Names Differ

```python
import pandas as pd

orders = pd.DataFrame({
    "OrderID": [1, 2, 3],
    "CustomerID": [101, 102, 101],
    "Amount": [250, 180, 340]
})

customers = pd.DataFrame({
    "CustID": [101, 102, 103],
    "Name": ["Alice", "Bob", "Charlie"]
})

# Use left_on and right_on when column names are different
result = pd.merge(orders, customers,
                  left_on="CustomerID", right_on="CustID",
                  how="inner")
print(result)
```

**Expected Output:**
```
   OrderID  CustomerID  Amount  CustID   Name
0        1         101     250     101  Alice
1        3         101     340     101  Alice
2        2         102     180     102    Bob
```

---

## 15.4 Pivot Tables

A pivot table reorganizes your data to make it easier to analyze. If you have ever used pivot tables in Excel, this is the same thing.

```python
import pandas as pd

sales = pd.DataFrame({
    "Date": ["Mon", "Mon", "Tue", "Tue", "Wed", "Wed"],
    "Product": ["A", "B", "A", "B", "A", "B"],
    "Sales": [100, 200, 150, 180, 120, 220]
})

print("Original:")
print(sales)

# Create a pivot table
pivot = sales.pivot_table(
    values="Sales",
    index="Date",
    columns="Product",
    aggfunc="sum"
)
print("\nPivot Table:")
print(pivot)
```

**Expected Output:**
```
Original:
  Date Product  Sales
0  Mon       A    100
1  Mon       B    200
2  Tue       A    150
3  Tue       B    180
4  Wed       A    120
5  Wed       B    220

Pivot Table:
Product    A    B
Date
Mon      100  200
Tue      150  180
Wed      120  220
```

```
What pivot_table does:

Original (long format):         Pivot (wide format):

Date | Product | Sales          Date | A   | B
Mon  | A       | 100            Mon  | 100 | 200
Mon  | B       | 200            Tue  | 150 | 180
Tue  | A       | 150    --->    Wed  | 120 | 220
Tue  | B       | 180
Wed  | A       | 120
Wed  | B       | 220
```

### Pivot Table with Multiple Aggregations

```python
import pandas as pd

sales = pd.DataFrame({
    "Region": ["East", "East", "West", "West", "East", "West"],
    "Product": ["A", "B", "A", "B", "A", "A"],
    "Revenue": [100, 200, 150, 300, 120, 180]
})

pivot = sales.pivot_table(
    values="Revenue",
    index="Region",
    columns="Product",
    aggfunc=["sum", "mean", "count"]
)
print(pivot)
```

**Expected Output:**
```
          sum        mean          count
Product     A      B     A      B     A    B
Region
East      220  200.0  110.0  200.0   2.0  1.0
West      330  300.0  165.0  300.0   2.0  1.0
```

---

## 15.5 The Apply Function

The `apply` function lets you run any function on every element, row, or column. It is incredibly flexible.

### Apply to a Column

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Salary": [70000, 85000, 92000]
})

# Apply a function to each salary
def add_bonus(salary):
    return salary * 1.10   # 10% bonus

df["With_Bonus"] = df["Salary"].apply(add_bonus)
print(df)
```

**Expected Output:**
```
      Name  Salary  With_Bonus
0    Alice   70000     77000.0
1      Bob   85000     93500.0
2  Charlie   92000    101200.0
```

### Apply with Lambda (Short Functions)

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Salary": [70000, 85000, 92000]
})

# Same thing with a lambda function
df["Tax"] = df["Salary"].apply(lambda x: x * 0.3)
df["Net"] = df["Salary"] - df["Tax"]
print(df)
```

**Expected Output:**
```
      Name  Salary      Tax      Net
0    Alice   70000  21000.0  49000.0
1      Bob   85000  25500.0  59500.0
2  Charlie   92000  27600.0  64400.0
```

**Line-by-line explanation:**

- `lambda x: x * 0.3` — A short, one-line function. `x` is each salary value. It returns 30% of it.
- `.apply(lambda x: ...)` — Runs the lambda on every element in the column.

### Apply to Rows

```python
import pandas as pd

df = pd.DataFrame({
    "Math": [85, 92, 78],
    "Science": [90, 88, 95],
    "English": [88, 76, 82]
})

# Calculate average across columns for each row
df["Average"] = df.apply(lambda row: row.mean(), axis=1)
print(df)
```

**Expected Output:**
```
   Math  Science  English    Average
0    85       90       88  87.666667
1    92       88       76  85.333333
2    78       95       82  85.000000
```

`axis=1` means "apply the function across each row." `axis=0` would apply it down each column.

---

## 15.6 Creating New Columns

You can create new columns from existing ones using arithmetic, conditions, or functions.

### Arithmetic Operations

```python
import pandas as pd

df = pd.DataFrame({
    "Product": ["A", "B", "C"],
    "Price": [10.00, 25.00, 15.00],
    "Quantity": [100, 50, 200]
})

# New column from arithmetic
df["Revenue"] = df["Price"] * df["Quantity"]
df["Tax"] = df["Revenue"] * 0.08
df["Total"] = df["Revenue"] + df["Tax"]
print(df)
```

**Expected Output:**
```
  Product  Price  Quantity  Revenue    Tax    Total
0       A   10.0       100   1000.0   80.0   1080.0
1       B   25.0        50   1250.0  100.0   1350.0
2       C   15.0       200   3000.0  240.0   3240.0
```

### Conditional Columns

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Score": [92, 75, 88, 65]
})

# Create a Pass/Fail column
df["Result"] = np.where(df["Score"] >= 70, "Pass", "Fail")
print(df)
```

**Expected Output:**
```
      Name  Score Result
0    Alice     92   Pass
1      Bob     75   Pass
2  Charlie     88   Pass
3    Diana     65   Fail
```

**Line-by-line explanation:**

- `np.where(condition, value_if_true, value_if_false)` — Like an if/else for every row.
- `df["Score"] >= 70` — The condition.
- `"Pass"` — Value when the condition is True.
- `"Fail"` — Value when the condition is False.

### Multiple Conditions with np.select

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Score": [95, 82, 68, 55]
})

conditions = [
    df["Score"] >= 90,
    df["Score"] >= 80,
    df["Score"] >= 70,
]
choices = ["A", "B", "C"]

df["Grade"] = np.select(conditions, choices, default="F")
print(df)
```

**Expected Output:**
```
      Name  Score Grade
0    Alice     95     A
1      Bob     82     B
2  Charlie     68     F
3    Diana     55     F
```

---

## 15.7 String Methods on Columns

Pandas has built-in string methods that work on entire columns. Access them with `.str`.

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["alice smith", "BOB JONES", "Charlie Brown"],
    "Email": ["alice@gmail.com", "bob@yahoo.com", "charlie@gmail.com"],
    "City": ["  New York  ", "london", "PARIS"]
})

# Convert to uppercase
print(df["Name"].str.upper())

# Convert to lowercase
print(df["Name"].str.lower())

# Title case (capitalize each word)
print(df["Name"].str.title())

# Strip whitespace
print(df["City"].str.strip())

# Check if it contains a substring
print(df["Email"].str.contains("gmail"))

# Split strings
print(df["Email"].str.split("@"))

# Extract part of a string
df["Domain"] = df["Email"].str.split("@").str[1]
print(df[["Email", "Domain"]])

# Replace text
print(df["City"].str.strip().str.replace("london", "London"))

# Get string length
print(df["Name"].str.len())
```

**Expected Output:**
```
0      ALICE SMITH
1        BOB JONES
2    CHARLIE BROWN
Name: Name, dtype: object
0      alice smith
1        bob jones
2    charlie brown
Name: Name, dtype: object
0      Alice Smith
1        Bob Jones
2    Charlie Brown
Name: Name, dtype: object
0    New York
1      london
2       PARIS
Name: City, dtype: object
0     True
1    False
2     True
Name: Email, dtype: bool
0      [alice, gmail.com]
1        [bob, yahoo.com]
2    [charlie, gmail.com]
Name: Email, dtype: object
        Email     Domain
0  alice@gmail.com  gmail.com
1    bob@yahoo.com  yahoo.com
2  charlie@gmail.com  gmail.com
0    New York
1      London
2       PARIS
Name: City, dtype: object
0    11
1     9
2    13
Name: Name, dtype: int64
```

### Quick Reference for String Methods

```
+----------------------+---------------------------+
| Method               | What It Does              |
+----------------------+---------------------------+
| .str.upper()         | ALL UPPERCASE             |
| .str.lower()         | all lowercase             |
| .str.title()         | Title Case                |
| .str.strip()         | Remove whitespace         |
| .str.contains("x")   | True if contains "x"     |
| .str.startswith("x") | True if starts with "x"  |
| .str.endswith("x")   | True if ends with "x"    |
| .str.replace("a","b")| Replace "a" with "b"     |
| .str.split("x")      | Split by "x"             |
| .str.len()           | Length of each string     |
| .str[0:3]            | Slice each string         |
+----------------------+---------------------------+
```

---

## 15.8 Saving DataFrames

After processing your data, you need to save it.

### Save to CSV

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "London", "Paris"]
})

# Save to CSV (no index column)
df.to_csv("output.csv", index=False)
print("Saved to output.csv!")

# Save with a specific separator
df.to_csv("output.tsv", sep="\t", index=False)

# Save only specific columns
df.to_csv("names_only.csv", columns=["Name", "City"], index=False)
```

### Save to Excel

```python
import pandas as pd

# You need openpyxl installed: pip install openpyxl

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "Salary": [70000, 85000, 92000]
})

# Save to Excel
df.to_excel("output.xlsx", index=False, sheet_name="Employees")
print("Saved to output.xlsx!")
```

### Save Multiple Sheets to Excel

```python
import pandas as pd

df1 = pd.DataFrame({"Name": ["Alice"], "Age": [25]})
df2 = pd.DataFrame({"Product": ["Laptop"], "Price": [999]})

with pd.ExcelWriter("multi_sheet.xlsx") as writer:
    df1.to_excel(writer, sheet_name="Employees", index=False)
    df2.to_excel(writer, sheet_name="Products", index=False)

print("Saved to multi_sheet.xlsx!")
```

```
Common save formats:

+------------------+----------------------------------+
| Method           | Use Case                         |
+------------------+----------------------------------+
| to_csv()         | Universal, works everywhere      |
| to_excel()       | When sharing with Excel users    |
| to_json()        | For web applications             |
| to_sql()         | Save to a database               |
| to_parquet()     | Big data, very efficient         |
+------------------+----------------------------------+
```

---

## 15.9 Putting It All Together

Here is a realistic example that uses many of the techniques from this chapter.

```python
import pandas as pd
import numpy as np

# Create sample sales data
np.random.seed(42)
sales = pd.DataFrame({
    "Date": pd.date_range("2024-01-01", periods=100, freq="D"),
    "Product": np.random.choice(["Laptop", "Phone", "Tablet"], 100),
    "Region": np.random.choice(["North", "South", "East", "West"], 100),
    "Units": np.random.randint(1, 20, 100),
    "Price": np.random.choice([999, 699, 449], 100)
})

# Add some missing values
sales.loc[5, "Units"] = np.nan
sales.loc[15, "Price"] = np.nan
sales.loc[25, "Region"] = np.nan

# 1. Check for missing values
print("Missing values:")
print(sales.isna().sum())

# 2. Fill missing values
sales["Units"] = sales["Units"].fillna(sales["Units"].median())
sales["Price"] = sales["Price"].fillna(sales["Price"].median())
sales["Region"] = sales["Region"].fillna("Unknown")

# 3. Create Revenue column
sales["Revenue"] = sales["Units"] * sales["Price"]

# 4. Group by Product
print("\nRevenue by Product:")
print(sales.groupby("Product")["Revenue"].agg(["sum", "mean", "count"]))

# 5. Pivot table: Product vs Region
print("\nTotal Revenue by Product and Region:")
pivot = sales.pivot_table(
    values="Revenue",
    index="Product",
    columns="Region",
    aggfunc="sum",
    fill_value=0
)
print(pivot)

# 6. Save results
sales.to_csv("sales_processed.csv", index=False)
print("\nSaved to sales_processed.csv!")
```

---

## Common Mistakes

### Mistake 1: Forgetting inplace parameter

```python
# This does NOT modify df:
df.dropna()
df.fillna(0)
df.sort_values("Age")

# You must either assign the result:
df = df.dropna()

# Or use inplace=True:
df.dropna(inplace=True)
```

### Mistake 2: Wrong merge type

```python
# If you lose rows unexpectedly, check your merge type
# Inner join drops non-matching rows
# Use left join to keep all rows from the left table
result = pd.merge(left, right, on="ID", how="left")  # keeps all left rows
```

### Mistake 3: Not resetting the index after groupby

```python
# After groupby, the grouped column becomes the index
result = df.groupby("Department")["Salary"].mean()
# result is a Series with Department as index

# To make it a regular DataFrame:
result = df.groupby("Department")["Salary"].mean().reset_index()
```

### Mistake 4: Using apply when vectorized operations work

```python
# Slow (apply):
df["double"] = df["value"].apply(lambda x: x * 2)

# Fast (vectorized):
df["double"] = df["value"] * 2
```

Use `apply` only when you need complex logic that cannot be vectorized.

### Mistake 5: Forgetting to install openpyxl for Excel

```python
# If you get: ModuleNotFoundError: No module named 'openpyxl'
# Run: pip install openpyxl
```

---

## Best Practices

1. **Handle missing data early.** Check for NaN values right after loading data.
2. **Use the right merge type.** Think about which rows you want to keep.
3. **Use vectorized operations before apply.** They are much faster.
4. **Reset index after groupby** if you need a regular DataFrame.
5. **Name columns descriptively.** Use `avg_salary` instead of `col1`.
6. **Save intermediate results.** Write to CSV after major transformations.
7. **Chain operations carefully.** Keep chains short and readable.
8. **Use `index=False` when saving to CSV.** Otherwise Pandas adds an extra index column.

---

## Quick Summary

| Function | What It Does | Example |
|---|---|---|
| `.isna()` | Detect missing values | `df.isna().sum()` |
| `.dropna()` | Remove missing rows | `df.dropna()` |
| `.fillna()` | Fill missing values | `df.fillna(0)` |
| `.groupby()` | Group data | `df.groupby("col").mean()` |
| `.agg()` | Multiple aggregations | `.agg(["sum","mean"])` |
| `pd.merge()` | Join two tables | `pd.merge(a, b, on="ID")` |
| `.pivot_table()` | Reshape data | `df.pivot_table(...)` |
| `.apply()` | Apply function to each element | `df["col"].apply(func)` |
| `.str.method()` | String operations | `df["col"].str.upper()` |
| `.to_csv()` | Save to CSV | `df.to_csv("file.csv")` |
| `.to_excel()` | Save to Excel | `df.to_excel("file.xlsx")` |

---

## Key Points to Remember

1. Missing data appears as NaN. Use `isna()` to find it, `dropna()` to remove it, `fillna()` to replace it.
2. Groupby follows the split-apply-combine pattern: split data into groups, apply a function, combine results.
3. Use `agg()` for multiple aggregation functions at once.
4. There are four merge types: inner (matches only), left (keep all left), right (keep all right), outer (keep everything).
5. Pivot tables reshape long data into wide format for easier comparison.
6. `apply()` runs a function on every element. Use lambda for short functions.
7. Vectorized operations (`df["col"] * 2`) are faster than `apply()`.
8. Use `.str` accessor for string operations on columns.
9. Save data with `to_csv()` or `to_excel()`. Use `index=False` to avoid extra index columns.
10. Always handle missing data before doing analysis.

---

## Practice Questions

**Question 1:** What is the difference between `dropna()` and `fillna()`?

**Answer:** `dropna()` removes rows (or columns) that contain missing values. The data is gone. `fillna()` replaces missing values with a value you choose (like 0, the mean, or a string). The rows are kept, and the gaps are filled.

**Question 2:** Explain the split-apply-combine pattern in groupby.

**Answer:** First, the data is SPLIT into groups based on a column's values (like splitting employees by department). Then a function is APPLIED to each group independently (like calculating the mean salary for each department). Finally, the results are COMBINED back into a single output.

**Question 3:** What is the difference between an inner join and a left join?

**Answer:** An inner join keeps only rows that have matching keys in BOTH tables. If a key exists in only one table, that row is dropped. A left join keeps ALL rows from the left table. If a row in the left table has no match in the right table, the right table's columns are filled with NaN.

**Question 4:** When should you use `apply()` vs vectorized operations?

**Answer:** Use vectorized operations (like `df["col"] * 2`) whenever possible because they are much faster. Use `apply()` only when you need complex logic that cannot be expressed as a simple arithmetic or comparison operation on the column.

**Question 5:** What does `df.to_csv("file.csv", index=False)` do?

**Answer:** It saves the DataFrame to a CSV file called "file.csv". The `index=False` parameter tells Pandas not to write the row index as an extra column in the file. Without this, the CSV would have an extra unnamed column with numbers 0, 1, 2, etc.

---

## Exercises

### Exercise 1: Clean and Analyze Sales Data

Create a messy dataset, clean it, and analyze it.

**Sample Solution:**

```python
import pandas as pd
import numpy as np

# Create messy data
np.random.seed(42)
data = pd.DataFrame({
    "Product": ["Laptop", "Phone", np.nan, "Laptop", "Tablet",
                "Phone", "Laptop", np.nan, "Tablet", "Phone"],
    "Region": ["East", "West", "East", np.nan, "North",
               "East", "West", "North", "East", np.nan],
    "Revenue": [1200, np.nan, 450, 1300, 400,
                np.nan, 1100, 500, np.nan, 650],
    "Units": [1, 2, np.nan, 1, 3, 2, 1, np.nan, 2, 1]
})

print("Before cleaning:")
print(data)
print(f"\nMissing values:\n{data.isna().sum()}")

# Clean the data
data["Product"] = data["Product"].fillna("Unknown")
data["Region"] = data["Region"].fillna("Unknown")
data["Revenue"] = data["Revenue"].fillna(data["Revenue"].median())
data["Units"] = data["Units"].fillna(data["Units"].median())

print("\nAfter cleaning:")
print(data)

# Analyze
print("\nRevenue by Product:")
print(data.groupby("Product")["Revenue"].agg(["mean", "sum", "count"]))

print("\nRevenue by Region:")
print(data.groupby("Region")["Revenue"].agg(["mean", "sum"]))
```

### Exercise 2: Merge Customer and Order Data

Practice joining tables together.

**Sample Solution:**

```python
import pandas as pd

customers = pd.DataFrame({
    "CustomerID": [1, 2, 3, 4, 5],
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "City": ["New York", "London", "Paris", "Tokyo", "Berlin"]
})

orders = pd.DataFrame({
    "OrderID": [101, 102, 103, 104, 105, 106],
    "CustomerID": [1, 2, 1, 3, 6, 2],
    "Amount": [250, 180, 340, 520, 90, 275]
})

# Inner join: only customers who have orders
inner = pd.merge(customers, orders, on="CustomerID", how="inner")
print("Inner join:")
print(inner)

# Left join: all customers, even without orders
left = pd.merge(customers, orders, on="CustomerID", how="left")
print("\nLeft join:")
print(left)

# Analysis: total spending per customer
spending = inner.groupby("Name")["Amount"].sum().sort_values(ascending=False)
print("\nTotal spending per customer:")
print(spending)
```

### Exercise 3: Groupby and Pivot Table

Analyze employee data using groupby and pivot tables.

**Sample Solution:**

```python
import pandas as pd
import numpy as np

np.random.seed(42)
employees = pd.DataFrame({
    "Name": [f"Employee_{i}" for i in range(1, 21)],
    "Department": np.random.choice(["Engineering", "Marketing",
                                     "Sales", "HR"], 20),
    "Level": np.random.choice(["Junior", "Mid", "Senior"], 20),
    "Salary": np.random.randint(50000, 120000, 20),
    "Years": np.random.randint(1, 15, 20)
})

# 1. Average salary by department
print("Average Salary by Department:")
print(employees.groupby("Department")["Salary"].mean().round(0))

# 2. Count by department and level
print("\nCount by Department and Level:")
print(employees.groupby(["Department", "Level"]).size().reset_index(name="Count"))

# 3. Pivot table: Department vs Level showing average salary
print("\nPivot Table (Average Salary):")
pivot = employees.pivot_table(
    values="Salary",
    index="Department",
    columns="Level",
    aggfunc="mean",
    fill_value=0
).round(0)
print(pivot)

# 4. Create seniority category
employees["Category"] = np.select(
    [employees["Years"] <= 3,
     employees["Years"] <= 7,
     employees["Years"] > 7],
    ["New", "Experienced", "Veteran"]
)

print("\nEmployee Categories:")
print(employees["Category"].value_counts())
```

---

## What Is Next?

Congratulations! You now have a solid foundation in Pandas — from loading data to cleaning, transforming, grouping, and merging. In the next chapter, we will learn **Matplotlib** — Python's library for creating charts and visualizations. You will learn to turn your data into beautiful plots and graphs.
