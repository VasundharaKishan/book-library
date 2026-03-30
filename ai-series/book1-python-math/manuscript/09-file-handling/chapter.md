# Chapter 9: File Handling — Reading and Writing Data

## What You Will Learn

- How to open and read files
- The difference between `read()`, `readline()`, and `readlines()`
- How to write data to files
- How to use the `with` statement (context manager)
- How to read and write CSV files
- What file modes are (r, w, a)
- How to check if a file exists
- Practical examples of reading data files for machine learning

## Why This Chapter Matters

So far, all your data has lived inside your Python code. But real-world data lives in **files**. Spreadsheets, text files, CSV files, JSON files — data is stored on disk.

When you work with AI and machine learning, you will:
- **Read** datasets from files
- **Write** results to files
- **Log** training progress to files
- **Save** model predictions to files

File handling is the bridge between your code and the outside world. Without it, your programs cannot access real data.

Think of it like this: your program is a chef. Files are the ingredients in the pantry. The chef needs to open the pantry, take out ingredients, and also put leftovers back.

---

## 9.1 Opening and Reading Files

### The Basic Way

```python
# First, let's create a sample file to work with
# (We'll learn writing in detail later)
with open("sample.txt", "w") as f:
    f.write("Hello, World!\n")
    f.write("This is line 2.\n")
    f.write("Python is fun.\n")
    f.write("File handling is easy.\n")

# Now let's read it
file = open("sample.txt", "r")
content = file.read()
print(content)
file.close()
```

**Expected Output:**
```
Hello, World!
This is line 2.
Python is fun.
File handling is easy.

```

**Line-by-line explanation:**
- **Lines 3-7:** We create a sample file first (do not worry about this yet — we will cover writing in detail soon).
- **Line 10:** `open("sample.txt", "r")` opens the file. `"r"` means read mode.
- **Line 11:** `.read()` reads the **entire** file content as one big string.
- **Line 12:** Print the content.
- **Line 13:** `.close()` closes the file. **Always close files when you are done.**

```
+-----------------------------------------------+
|  Opening a File                                |
+-----------------------------------------------+
|                                                |
|  file = open("filename.txt", "mode")           |
|                                                |
|  Common modes:                                 |
|    "r"  -> Read (default). File must exist.    |
|    "w"  -> Write. Creates or overwrites file.  |
|    "a"  -> Append. Adds to end of file.        |
|    "r+" -> Read and write.                     |
+-----------------------------------------------+
```

### The Problem with the Basic Way

What if your code crashes before reaching `file.close()`? The file stays open. This can cause problems. There is a better way.

---

## 9.2 The `with` Statement — The Right Way

The `with` statement automatically closes the file for you. Even if an error occurs.

```python
# The RIGHT way to open files
with open("sample.txt", "r") as file:
    content = file.read()
    print(content)

# File is automatically closed here!
# No need to call file.close()
```

**Expected Output:**
```
Hello, World!
This is line 2.
Python is fun.
File handling is easy.

```

**Line-by-line explanation:**
- **Line 2:** `with open(...) as file:` opens the file AND guarantees it will be closed when the block ends.
- **Line 3-4:** Read and print, same as before.
- **Line 6:** When the indented block ends, Python closes the file automatically.

```
+-----------------------------------------------+
|  with statement (Context Manager)              |
+-----------------------------------------------+
|                                                |
|  WITHOUT with:               WITH with:        |
|                                                |
|  f = open("file.txt")       with open("file.txt") as f:
|  content = f.read()             content = f.read()
|  f.close()  # easy to forget    # auto-closed!
|                                                |
|  Rule: ALWAYS use 'with' for file operations.  |
+-----------------------------------------------+
```

---

## 9.3 Three Ways to Read

### read() — Read Everything

```python
with open("sample.txt", "r") as file:
    content = file.read()
    print("--- read() ---")
    print(content)
    print(f"Type: {type(content)}")
```

**Expected Output:**
```
--- read() ---
Hello, World!
This is line 2.
Python is fun.
File handling is easy.

Type: <class 'str'>
```

`read()` gives you the entire file as **one string**.

### readline() — Read One Line

```python
with open("sample.txt", "r") as file:
    print("--- readline() ---")
    line1 = file.readline()
    line2 = file.readline()
    print(f"Line 1: {line1.strip()}")
    print(f"Line 2: {line2.strip()}")
```

**Expected Output:**
```
--- readline() ---
Line 1: Hello, World!
Line 2: This is line 2.
```

**Line-by-line explanation:**
- **Line 3:** `.readline()` reads one line and moves to the next.
- **Line 4:** Calling it again reads the second line.
- **Lines 5-6:** `.strip()` removes the newline character `\n` at the end.

### readlines() — Read All Lines into a List

```python
with open("sample.txt", "r") as file:
    lines = file.readlines()
    print("--- readlines() ---")
    print(f"Type: {type(lines)}")
    print(f"Number of lines: {len(lines)}")
    for i, line in enumerate(lines):
        print(f"  Line {i}: {line.strip()}")
```

**Expected Output:**
```
--- readlines() ---
Type: <class 'list'>
Number of lines: 4
  Line 0: Hello, World!
  Line 1: This is line 2.
  Line 2: Python is fun.
  Line 3: File handling is easy.
```

**Line-by-line explanation:**
- **Line 2:** `.readlines()` reads all lines and returns them as a **list of strings**.
- **Line 6:** We use `enumerate()` to get both the index and the line.

```
+-----------------------------------------------+
|  read() vs readline() vs readlines()           |
+-----------------------------------------------+
|                                                |
|  .read()       -> One big string               |
|                   "Hello\nWorld\n"              |
|                                                |
|  .readline()   -> One line at a time           |
|                   "Hello\n"                    |
|                                                |
|  .readlines()  -> List of all lines            |
|                   ["Hello\n", "World\n"]        |
+-----------------------------------------------+
```

### Reading Line by Line (Memory-Friendly)

For large files, read one line at a time. This uses less memory.

```python
with open("sample.txt", "r") as file:
    print("--- Line by line ---")
    for line in file:
        print(f"  > {line.strip()}")
```

**Expected Output:**
```
--- Line by line ---
  > Hello, World!
  > This is line 2.
  > Python is fun.
  > File handling is easy.
```

**Line-by-line explanation:**
- **Line 3:** You can loop directly over the file object. Python reads one line at a time. This is the best approach for large files.

---

## 9.4 Writing to Files

### Write Mode ("w") — Create or Overwrite

```python
# Writing to a file
with open("output.txt", "w") as file:
    file.write("First line.\n")
    file.write("Second line.\n")
    file.write("Third line.\n")

# Verify by reading it back
with open("output.txt", "r") as file:
    print(file.read())
```

**Expected Output:**
```
First line.
Second line.
Third line.

```

**Line-by-line explanation:**
- **Line 2:** `"w"` mode creates the file if it does not exist. If it exists, it **erases everything** and starts fresh.
- **Line 3-5:** `.write()` writes a string to the file. You must add `\n` yourself for new lines.

> **Warning:** `"w"` mode erases the file content! Use `"a"` mode to add to an existing file.

### Append Mode ("a") — Add to the End

```python
# Append to the file
with open("output.txt", "a") as file:
    file.write("Fourth line (appended).\n")
    file.write("Fifth line (appended).\n")

# Read the full file
with open("output.txt", "r") as file:
    print(file.read())
```

**Expected Output:**
```
First line.
Second line.
Third line.
Fourth line (appended).
Fifth line (appended).

```

**Line-by-line explanation:**
- **Line 2:** `"a"` mode opens the file and positions the cursor at the end. New content is added after existing content.

### writelines() — Write Multiple Lines

```python
lines = ["Apple\n", "Banana\n", "Cherry\n"]

with open("fruits.txt", "w") as file:
    file.writelines(lines)

with open("fruits.txt", "r") as file:
    print(file.read())
```

**Expected Output:**
```
Apple
Banana
Cherry

```

**Line-by-line explanation:**
- **Line 3-4:** `.writelines()` writes a list of strings. Note: it does NOT add newlines automatically. You must include `\n` in each string.

```
+-----------------------------------------------+
|  File Modes Summary                            |
+-----------------------------------------------+
|                                                |
|  Mode  |  Description          |  File exists? |
|  ------+-----------------------+---------------|
|  "r"   |  Read only            |  Must exist   |
|  "w"   |  Write (overwrite)    |  Created/Reset|
|  "a"   |  Append (add to end)  |  Created/Added|
|  "r+"  |  Read and write       |  Must exist   |
+-----------------------------------------------+
```

---

## 9.5 Reading CSV Files

CSV stands for **Comma-Separated Values**. It is the most common format for data in data science and machine learning.

```
+-----------------------------------------------+
|  What a CSV file looks like:                   |
+-----------------------------------------------+
|                                                |
|  name,age,grade                                |
|  Alice,20,A                                    |
|  Bob,22,B                                      |
|  Charlie,21,A                                  |
|                                                |
|  - First row is usually headers                |
|  - Values are separated by commas              |
|  - Each row is one record                      |
+-----------------------------------------------+
```

### Create a Sample CSV File

```python
# Create a sample CSV file
with open("students.csv", "w") as file:
    file.write("name,age,grade,score\n")
    file.write("Alice,20,A,95\n")
    file.write("Bob,22,B,82\n")
    file.write("Charlie,21,A,91\n")
    file.write("Diana,23,C,73\n")
    file.write("Eve,20,B,85\n")

print("CSV file created!")
```

**Expected Output:**
```
CSV file created!
```

### Reading CSV with the csv Module

```python
import csv

with open("students.csv", "r") as file:
    reader = csv.reader(file)

    # Read the header
    header = next(reader)
    print("Headers:", header)

    # Read each row
    print("\nData:")
    for row in reader:
        print(f"  {row}")
```

**Expected Output:**
```
Headers: ['name', 'age', 'grade', 'score']

Data:
  ['Alice', '20', 'A', '95']
  ['Bob', '22', 'B', '82']
  ['Charlie', '21', 'A', '91']
  ['Diana', '23', 'C', '73']
  ['Eve', '20', 'B', '85']
```

**Line-by-line explanation:**
- **Line 1:** Import Python's built-in `csv` module.
- **Line 4:** `csv.reader(file)` creates a reader object. Each row becomes a list of strings.
- **Line 7:** `next(reader)` reads the first row (the header).
- **Line 11-12:** Loop through remaining rows.

### Reading CSV as Dictionaries

```python
import csv

with open("students.csv", "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        print(f"{row['name']}: age={row['age']}, "
              f"grade={row['grade']}, score={row['score']}")
```

**Expected Output:**
```
Alice: age=20, grade=A, score=95
Bob: age=22, grade=B, score=82
Charlie: age=21, grade=A, score=91
Diana: age=23, grade=C, score=73
Eve: age=20, grade=B, score=85
```

**Line-by-line explanation:**
- **Line 4:** `csv.DictReader` automatically uses the first row as keys. Each row becomes a dictionary.
- **Line 7:** You can access values by column name, like `row['name']`. This is much easier to read!

---

## 9.6 Writing CSV Files

```python
import csv

# Data to write
students = [
    ["Name", "Age", "Grade", "Score"],
    ["Alice", 20, "A", 95],
    ["Bob", 22, "B", 82],
    ["Charlie", 21, "A", 91]
]

# Write using csv.writer
with open("output_students.csv", "w", newline="") as file:
    writer = csv.writer(file)
    for row in students:
        writer.writerow(row)

print("CSV written!")

# Verify by reading it back
with open("output_students.csv", "r") as file:
    print(file.read())
```

**Expected Output:**
```
CSV written!
Name,Age,Grade,Score
Alice,20,A,95
Bob,22,B,82
Charlie,21,A,91

```

**Line-by-line explanation:**
- **Line 12:** `newline=""` prevents extra blank lines on Windows.
- **Line 13:** `csv.writer(file)` creates a writer object.
- **Line 15:** `.writerow(row)` writes one row to the file.

### Writing Dictionaries to CSV

```python
import csv

students = [
    {"name": "Alice", "age": 20, "score": 95},
    {"name": "Bob", "age": 22, "score": 82},
    {"name": "Charlie", "age": 21, "score": 91}
]

with open("dict_output.csv", "w", newline="") as file:
    fieldnames = ["name", "age", "score"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()   # Write the header row
    writer.writerows(students)  # Write all data rows

print("Dictionary CSV written!")

with open("dict_output.csv", "r") as file:
    print(file.read())
```

**Expected Output:**
```
Dictionary CSV written!
name,age,score
Alice,20,95
Bob,22,82
Charlie,21,91

```

**Line-by-line explanation:**
- **Line 10:** `fieldnames` defines the column names and their order.
- **Line 11:** `DictWriter` writes dictionaries as CSV rows.
- **Line 13:** `.writeheader()` writes the column names as the first row.
- **Line 14:** `.writerows()` writes all the data rows at once.

---

## 9.7 Checking If a File Exists

Before reading a file, it is good to check if it exists.

```python
import os

# Check if a file exists
filename = "students.csv"
if os.path.exists(filename):
    print(f"'{filename}' exists!")
    # Safe to read it
    with open(filename, "r") as file:
        first_line = file.readline()
        print(f"First line: {first_line.strip()}")
else:
    print(f"'{filename}' does NOT exist.")

# Check a file that does not exist
missing = "nonexistent.txt"
if os.path.exists(missing):
    print(f"'{missing}' exists!")
else:
    print(f"'{missing}' does NOT exist.")
```

**Expected Output:**
```
'students.csv' exists!
First line: name,age,grade,score
'nonexistent.txt' does NOT exist.
```

**Line-by-line explanation:**
- **Line 1:** Import the `os` module. It has tools for working with the operating system.
- **Line 5:** `os.path.exists()` returns `True` if the file exists, `False` otherwise.

### Other Useful os.path Functions

```python
import os

filename = "students.csv"

print(f"Exists: {os.path.exists(filename)}")
print(f"Is a file: {os.path.isfile(filename)}")
print(f"Is a directory: {os.path.isdir(filename)}")
print(f"File size: {os.path.getsize(filename)} bytes")
```

**Expected Output:**
```
Exists: True
Is a file: True
Is a directory: False
File size: 120 bytes
```

---

## 9.8 Practical Examples for Machine Learning

### Example 1: Reading a Dataset and Computing Statistics

```python
import csv

# Create a sample dataset
with open("iris_sample.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["sepal_length", "sepal_width", "petal_length", "petal_width", "species"])
    writer.writerow([5.1, 3.5, 1.4, 0.2, "setosa"])
    writer.writerow([4.9, 3.0, 1.4, 0.2, "setosa"])
    writer.writerow([7.0, 3.2, 4.7, 1.4, "versicolor"])
    writer.writerow([6.4, 3.2, 4.5, 1.5, "versicolor"])
    writer.writerow([6.3, 3.3, 6.0, 2.5, "virginica"])
    writer.writerow([5.8, 2.7, 5.1, 1.9, "virginica"])

# Read and analyze the dataset
with open("iris_sample.csv", "r") as f:
    reader = csv.DictReader(f)

    species_count = {}
    sepal_lengths = []

    for row in reader:
        # Count species
        species = row["species"]
        species_count[species] = species_count.get(species, 0) + 1

        # Collect sepal lengths
        sepal_lengths.append(float(row["sepal_length"]))

print("Species distribution:")
for species, count in species_count.items():
    print(f"  {species}: {count}")

print(f"\nSepal length statistics:")
print(f"  Mean: {sum(sepal_lengths) / len(sepal_lengths):.2f}")
print(f"  Min: {min(sepal_lengths):.2f}")
print(f"  Max: {max(sepal_lengths):.2f}")
```

**Expected Output:**
```
Species distribution:
  setosa: 2
  versicolor: 2
  virginica: 2

Sepal length statistics:
  Mean: 5.92
  Min: 4.90
  Max: 7.00
```

### Example 2: Logging Training Results

```python
import csv

# Simulate training results
epochs = 5
results = []

for epoch in range(1, epochs + 1):
    # Simulated values (in real ML, these come from training)
    loss = 1.0 / epoch
    accuracy = 1 - (1.0 / (epoch + 1))
    results.append({
        "epoch": epoch,
        "loss": round(loss, 4),
        "accuracy": round(accuracy, 4)
    })

# Write results to CSV
with open("training_log.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["epoch", "loss", "accuracy"])
    writer.writeheader()
    writer.writerows(results)

# Read and display the log
print("Training Log:")
print(f"{'Epoch':<10}{'Loss':<10}{'Accuracy':<10}")
print("-" * 30)

with open("training_log.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['epoch']:<10}{row['loss']:<10}{row['accuracy']:<10}")
```

**Expected Output:**
```
Training Log:
Epoch     Loss      Accuracy
------------------------------
1         1.0       0.5
2         0.5       0.6667
3         0.3333    0.75
4         0.25      0.8
5         0.2       0.8333
```

### Example 3: Reading Data into Lists for Processing

```python
import csv

# Read the CSV into structured data
with open("students.csv", "r") as f:
    reader = csv.DictReader(f)
    students = list(reader)  # Convert to a list of dictionaries

# Now we can process the data like in ML pipelines
print(f"Total students: {len(students)}")
print(f"First student: {students[0]}")

# Extract features (like you would for ML)
names = [s["name"] for s in students]
scores = [int(s["score"]) for s in students]

print(f"\nNames: {names}")
print(f"Scores: {scores}")
print(f"Average score: {sum(scores) / len(scores):.1f}")
```

**Expected Output:**
```
Total students: 5
First student: {'name': 'Alice', 'age': '20', 'grade': 'A', 'score': '95'}

Names: ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
Scores: [95, 82, 91, 73, 85]
Average score: 85.2
```

---

## Common Mistakes

### Mistake 1: Forgetting to Close Files

```python
# WRONG - file stays open if error occurs
# file = open("data.txt", "r")
# content = file.read()
# file.close()  # Might never run if error above!

# RIGHT - always use 'with'
with open("sample.txt", "r") as file:
    content = file.read()
# File is closed automatically
print("File read successfully with 'with' statement.")
```

**Expected Output:**
```
File read successfully with 'with' statement.
```

### Mistake 2: Using "w" Mode When You Meant "a"

```python
# This ERASES the file and writes new content!
with open("demo_overwrite.txt", "w") as f:
    f.write("First time writing.\n")

with open("demo_overwrite.txt", "w") as f:  # Oops! "w" erases!
    f.write("Second time writing.\n")

with open("demo_overwrite.txt", "r") as f:
    print("With 'w' mode:")
    print(f.read())

# This ADDS to the file
with open("demo_append.txt", "w") as f:
    f.write("First time writing.\n")

with open("demo_append.txt", "a") as f:  # "a" adds!
    f.write("Second time writing.\n")

with open("demo_append.txt", "r") as f:
    print("With 'a' mode:")
    print(f.read())
```

**Expected Output:**
```
With 'w' mode:
Second time writing.

With 'a' mode:
First time writing.
Second time writing.

```

### Mistake 3: Forgetting to Convert CSV Strings to Numbers

```python
import csv

with open("students.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # CSV values are ALWAYS strings!
        score = row["score"]
        print(f"{row['name']}: score type = {type(score)}, value = {score}")
        break

# Always convert when needed
print("\nConverted:", int("95") + int("82"))
```

**Expected Output:**
```
Alice: score type = <class 'str'>, value = 95

Converted: 177
```

### Mistake 4: Not Handling Missing Files

```python
import os

filename = "does_not_exist.txt"

# WRONG - crashes if file missing
# with open(filename, "r") as f:
#     content = f.read()

# RIGHT - check first
if os.path.exists(filename):
    with open(filename, "r") as f:
        content = f.read()
else:
    print(f"File '{filename}' not found. Using default data.")
```

**Expected Output:**
```
File 'does_not_exist.txt' not found. Using default data.
```

---

## Best Practices

1. **Always use `with` statements.** They guarantee files are closed properly.
2. **Use `"r"` mode for reading, `"w"` for new files, `"a"` to add.** Know the difference.
3. **Use `csv.DictReader` for CSV files.** Column names make your code more readable.
4. **Convert CSV values to the right type.** CSV values are always strings.
5. **Check if files exist before reading.** Use `os.path.exists()`.
6. **Read large files line by line.** Do not load a huge file into memory all at once.
7. **Use `newline=""` when writing CSV on Windows.** This prevents extra blank lines.

---

## Quick Summary

| Operation | Code |
|-----------|------|
| Open for reading | `open("file.txt", "r")` |
| Open for writing | `open("file.txt", "w")` |
| Open for appending | `open("file.txt", "a")` |
| Read all content | `file.read()` |
| Read one line | `file.readline()` |
| Read all lines as list | `file.readlines()` |
| Write a string | `file.write("text\n")` |
| Write a list | `file.writelines(list)` |
| Context manager | `with open(...) as f:` |
| Read CSV | `csv.reader(file)` |
| Read CSV as dict | `csv.DictReader(file)` |
| Write CSV | `csv.writer(file)` |
| Check file exists | `os.path.exists("file")` |

---

## Key Points to Remember

1. **Always use `with` to open files.** It closes them automatically.
2. **`"w"` mode erases existing content.** Use `"a"` to append.
3. **`read()` returns a string.** `readlines()` returns a list.
4. **CSV values are always strings.** Convert to int or float when needed.
5. **`csv.DictReader` makes CSV easy.** It uses column names as keys.
6. **Check if files exist** with `os.path.exists()` before reading.
7. **Read large files line by line** to save memory.
8. **Always add `\n`** at the end of lines when using `write()`.

---

## Practice Questions

**Question 1:** What is the difference between `"w"` and `"a"` file modes?

<details>
<summary>Answer</summary>

- `"w"` (write) creates a new file or **erases** existing content and writes from scratch.
- `"a"` (append) creates a new file or **adds** to the end of existing content.

Use `"w"` when you want to start fresh. Use `"a"` when you want to keep existing data.
</details>

---

**Question 2:** Why should you use the `with` statement instead of `open()` and `close()`?

<details>
<summary>Answer</summary>

The `with` statement guarantees the file is closed, even if an error occurs. Without `with`, if your code crashes between `open()` and `close()`, the file stays open, which can cause data loss or corruption.
</details>

---

**Question 3:** What does `csv.DictReader` do differently from `csv.reader`?

<details>
<summary>Answer</summary>

- `csv.reader` returns each row as a **list** of strings. You access values by index: `row[0]`.
- `csv.DictReader` returns each row as a **dictionary**. You access values by column name: `row["name"]`. It automatically uses the first row as keys.
</details>

---

**Question 4:** What type are values when you read them from a CSV file?

<details>
<summary>Answer</summary>

All values from a CSV file are **strings**, even numbers. You need to convert them:
```python
age = int(row["age"])      # string to integer
score = float(row["score"]) # string to float
```
</details>

---

**Question 5:** How do you read a large file without loading it all into memory?

<details>
<summary>Answer</summary>

Loop over the file object directly. Python reads one line at a time:
```python
with open("large_file.txt", "r") as f:
    for line in f:
        # Process one line at a time
        print(line.strip())
```
This is much more memory-efficient than `f.read()` or `f.readlines()`.
</details>

---

## Exercises

### Exercise 1: Line Counter

Write a program that:
1. Creates a text file with at least 5 lines of text.
2. Reads the file and counts the total number of lines.
3. Counts the number of non-empty lines.
4. Prints both counts.

<details>
<summary>Solution</summary>

```python
# Step 1: Create the file
with open("poem.txt", "w") as f:
    f.write("Roses are red,\n")
    f.write("Violets are blue,\n")
    f.write("\n")
    f.write("Python is awesome,\n")
    f.write("\n")
    f.write("And so are you.\n")

# Step 2 and 3: Read and count
with open("poem.txt", "r") as f:
    lines = f.readlines()

total_lines = len(lines)
non_empty = len([line for line in lines if line.strip()])

# Step 4: Print results
print(f"Total lines: {total_lines}")
print(f"Non-empty lines: {non_empty}")
```

**Expected Output:**
```
Total lines: 6
Non-empty lines: 4
```
</details>

---

### Exercise 2: CSV Score Analyzer

Write a program that:
1. Creates a CSV file with columns: student, math, science, english.
2. Add at least 4 students with scores.
3. Reads the file and calculates each student's average.
4. Finds the student with the highest average.
5. Writes the results to a new CSV file.

<details>
<summary>Solution</summary>

```python
import csv

# Step 1 and 2: Create the CSV file
with open("scores.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["student", "math", "science", "english"])
    writer.writerow(["Alice", 90, 85, 92])
    writer.writerow(["Bob", 78, 88, 75])
    writer.writerow(["Charlie", 95, 92, 98])
    writer.writerow(["Diana", 82, 79, 86])

# Step 3: Read and calculate averages
results = []
with open("scores.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        math = int(row["math"])
        science = int(row["science"])
        english = int(row["english"])
        average = (math + science + english) / 3
        results.append({
            "student": row["student"],
            "math": math,
            "science": science,
            "english": english,
            "average": round(average, 1)
        })

# Print results
print("Student Averages:")
for r in results:
    print(f"  {r['student']}: {r['average']}")

# Step 4: Find highest average
best = max(results, key=lambda x: x["average"])
print(f"\nBest student: {best['student']} ({best['average']})")

# Step 5: Write results to new file
with open("results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["student", "math", "science", "english", "average"])
    writer.writeheader()
    writer.writerows(results)

print("\nResults written to results.csv")
```

**Expected Output:**
```
Student Averages:
  Alice: 89.0
  Bob: 80.3
  Charlie: 95.0
  Diana: 82.3

Best student: Charlie (95.0)

Results written to results.csv
```
</details>

---

### Exercise 3: Simple Log File

Write a program that:
1. Creates a function `log_message(message)` that appends a timestamped message to a log file.
2. Call the function 3 times with different messages.
3. Read and display the log file contents.

Hint: Use `"a"` mode for appending.

<details>
<summary>Solution</summary>

```python
from datetime import datetime

def log_message(message, filename="app.log"):
    """Append a timestamped message to a log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# Clear the log first (fresh start)
with open("app.log", "w") as f:
    pass  # Empty the file

# Step 2: Log some messages
log_message("Application started")
log_message("User logged in")
log_message("Data processed successfully")

# Step 3: Read and display
print("Log file contents:")
print("-" * 50)
with open("app.log", "r") as f:
    print(f.read())
```

**Expected Output:**
```
Log file contents:
--------------------------------------------------
[2026-03-25 10:30:15] Application started
[2026-03-25 10:30:15] User logged in
[2026-03-25 10:30:15] Data processed successfully

```
(Note: The timestamps will show your actual current time.)
</details>

---

## What Is Next?

You now know how to read and write files, which connects your Python programs to the outside world. In Chapter 10, you will learn about **Object-Oriented Programming (OOP)** — a way to organize your code using classes and objects. Think of it as creating your own custom data types. OOP is used heavily in Python libraries for AI and machine learning, so understanding it will help you read and write better code.
