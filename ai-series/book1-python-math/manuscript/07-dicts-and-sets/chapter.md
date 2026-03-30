# Chapter 7: Dictionaries and Sets — Labeled Data and Unique Collections

## What You Will Learn

- What dictionaries are and how they work
- How to create, access, and modify dictionaries
- How to loop through dictionaries
- What nested dictionaries are
- How to use dictionary comprehensions
- What sets are and why they are useful
- How to perform set operations (union, intersection, difference)

## Why This Chapter Matters

Imagine you have a phone book. You look up a **name** and find a **phone number**. You do not search page by page. You go directly to the name.

That is exactly what a dictionary does. It pairs a **key** (the name) with a **value** (the phone number). This makes finding data incredibly fast.

In AI and data science, dictionaries are everywhere. Configuration settings, JSON data from APIs, feature mappings, word counts — all use dictionaries.

Sets are useful when you need **unique items only**. Think of collecting unique words from a text, or finding what two datasets have in common. Sets make these tasks easy.

---

## 7.1 What Is a Dictionary?

A dictionary stores data in **key-value pairs**. Each key points to a value.

```
+--------------------------------------------+
|         Phone Book (Dictionary)             |
+--------------------------------------------+
|  Key (Name)      ->   Value (Number)        |
+--------------------------------------------+
|  "Alice"         ->   "555-0101"            |
|  "Bob"           ->   "555-0102"            |
|  "Charlie"       ->   "555-0103"            |
+--------------------------------------------+
```

In Python:

```python
phone_book = {
    "Alice": "555-0101",
    "Bob": "555-0102",
    "Charlie": "555-0103"
}
print(phone_book)
```

**Expected Output:**
```
{'Alice': '555-0101', 'Bob': '555-0102', 'Charlie': '555-0103'}
```

**Line-by-line explanation:**
- **Line 1-5:** We create a dictionary using curly braces `{}`. Each entry has a key, a colon `:`, and a value. Entries are separated by commas.
- **Line 6:** Print the whole dictionary.

### Key Facts About Dictionaries

```
+-----------------------------------------------+
|           Python Dictionaries                  |
+-----------------------------------------------+
| - Use curly braces {}                          |
| - Store key: value pairs                       |
| - Keys must be unique                          |
| - Keys must be immutable (strings, numbers,    |
|   tuples — but NOT lists)                      |
| - Values can be anything                       |
| - Very fast lookups                            |
| - Ordered (since Python 3.7)                   |
+-----------------------------------------------+
```

---

## 7.2 Creating Dictionaries

There are several ways to create a dictionary.

```python
# Method 1: Curly braces (most common)
student = {
    "name": "Alice",
    "age": 20,
    "grade": "A"
}
print("Method 1:", student)

# Method 2: dict() constructor
student2 = dict(name="Bob", age=22, grade="B")
print("Method 2:", student2)

# Method 3: From a list of tuples
pairs = [("x", 10), ("y", 20), ("z", 30)]
coordinates = dict(pairs)
print("Method 3:", coordinates)

# Method 4: Empty dictionary
empty = {}
print("Method 4:", empty)
```

**Expected Output:**
```
Method 1: {'name': 'Alice', 'age': 20, 'grade': 'A'}
Method 2: {'name': 'Bob', 'age': 22, 'grade': 'B'}
Method 3: {'x': 10, 'y': 20, 'z': 30}
Method 4: {}
```

**Line-by-line explanation:**
- **Lines 2-6:** The most common way. Write key-value pairs inside `{}`.
- **Line 10:** Using `dict()`. Note: keys are written without quotes here, like variable names.
- **Lines 14-15:** Convert a list of tuples into a dictionary. Each tuple has two items: (key, value).
- **Line 19:** An empty dictionary. You can add items later.

---

## 7.3 Accessing Values

### Using Square Brackets

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

# Access by key
print(student["name"])
print(student["age"])
```

**Expected Output:**
```
Alice
20
```

### Using .get() — The Safer Way

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

# .get() returns None if key does not exist (no error!)
print(student.get("name"))
print(student.get("email"))
print(student.get("email", "Not found"))
```

**Expected Output:**
```
Alice
None
Not found
```

**Line-by-line explanation:**
- **Line 4:** `.get("name")` works just like `student["name"]`.
- **Line 5:** `.get("email")` returns `None` because "email" does not exist. No error.
- **Line 6:** `.get("email", "Not found")` returns "Not found" as a default value.

```
+------------------------------------------------+
|  [] vs .get()                                   |
+------------------------------------------------+
|                                                 |
|  student["email"]                               |
|  -> KeyError! Program crashes.                  |
|                                                 |
|  student.get("email")                           |
|  -> Returns None. Program continues.            |
|                                                 |
|  student.get("email", "default")                |
|  -> Returns "default". Program continues.       |
+------------------------------------------------+
|  Rule: Use .get() when the key might not exist. |
+------------------------------------------------+
```

---

## 7.4 Adding, Updating, and Deleting

### Adding and Updating

```python
student = {"name": "Alice", "age": 20}
print("Before:", student)

# Add a new key-value pair
student["grade"] = "A"
print("After add:", student)

# Update an existing value
student["age"] = 21
print("After update:", student)

# Update multiple values at once
student.update({"age": 22, "email": "alice@example.com"})
print("After update multiple:", student)
```

**Expected Output:**
```
Before: {'name': 'Alice', 'age': 20}
After add: {'name': 'Alice', 'age': 20, 'grade': 'A'}
After update: {'name': 'Alice', 'age': 21, 'grade': 'A'}
After update multiple: {'name': 'Alice', 'age': 22, 'grade': 'A', 'email': 'alice@example.com'}
```

**Line-by-line explanation:**
- **Line 5:** `student["grade"] = "A"` adds a new key "grade" with value "A".
- **Line 9:** `student["age"] = 21` changes the existing value for "age".
- **Line 13:** `.update()` can change multiple values at once and add new ones.

### Deleting

```python
student = {"name": "Alice", "age": 20, "grade": "A", "email": "a@b.com"}
print("Before:", student)

# del - remove a specific key
del student["email"]
print("After del:", student)

# pop() - remove and return the value
removed_grade = student.pop("grade")
print("Popped:", removed_grade)
print("After pop:", student)

# clear() - remove ALL items
student.clear()
print("After clear:", student)
```

**Expected Output:**
```
Before: {'name': 'Alice', 'age': 20, 'grade': 'A', 'email': 'a@b.com'}
After del: {'name': 'Alice', 'age': 20, 'grade': 'A'}
Popped: A
After pop: {'name': 'Alice', 'age': 20}
After clear: {}
```

**Line-by-line explanation:**
- **Line 5:** `del student["email"]` removes the "email" key and its value.
- **Line 9:** `.pop("grade")` removes "grade" and gives back its value "A".
- **Line 14:** `.clear()` empties the entire dictionary.

---

## 7.5 Dictionary Methods: .keys(), .values(), .items()

These three methods help you look at different parts of a dictionary.

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

# Get all keys
print("Keys:", list(student.keys()))

# Get all values
print("Values:", list(student.values()))

# Get all key-value pairs (as tuples)
print("Items:", list(student.items()))
```

**Expected Output:**
```
Keys: ['name', 'age', 'grade']
Values: ['Alice', 20, 'A']
Items: [('name', 'Alice'), ('age', 20), ('grade', 'A')]
```

**Line-by-line explanation:**
- **Line 4:** `.keys()` gives you all the keys. We wrap it in `list()` to see it as a list.
- **Line 7:** `.values()` gives you all the values.
- **Line 10:** `.items()` gives you each key-value pair as a tuple.

```
+-------------------------------------------------+
|  Dictionary Methods                              |
+-------------------------------------------------+
|                                                  |
|  {"a": 1, "b": 2, "c": 3}                       |
|                                                  |
|  .keys()   ->  ["a", "b", "c"]     (just keys)  |
|  .values() ->  [1, 2, 3]           (just values) |
|  .items()  ->  [("a",1), ("b",2), ("c",3)]      |
|                                     (both)       |
+-------------------------------------------------+
```

---

## 7.6 Looping Through Dictionaries

### Loop Through Keys

```python
fruit_colors = {"apple": "red", "banana": "yellow", "grape": "purple"}

# Loop through keys (default)
for fruit in fruit_colors:
    print(fruit)
```

**Expected Output:**
```
apple
banana
grape
```

### Loop Through Values

```python
fruit_colors = {"apple": "red", "banana": "yellow", "grape": "purple"}

for color in fruit_colors.values():
    print(color)
```

**Expected Output:**
```
red
yellow
purple
```

### Loop Through Keys AND Values

```python
fruit_colors = {"apple": "red", "banana": "yellow", "grape": "purple"}

for fruit, color in fruit_colors.items():
    print(f"A {fruit} is {color}.")
```

**Expected Output:**
```
A apple is red.
A banana is yellow.
A grape is purple.
```

**Line-by-line explanation:**
- **Line 3:** `.items()` returns tuples of (key, value). We unpack each tuple into `fruit` and `color`.

---

## 7.7 Nested Dictionaries

A dictionary can hold another dictionary as a value. This is called **nesting**.

Think of it like a filing cabinet. Each drawer (key) holds a folder (another dictionary).

```
+----------------------------------------------+
|  Students (Nested Dictionary)                 |
+----------------------------------------------+
|  "student1" -> { "name": "Alice",            |
|                  "age": 20,                   |
|                  "grades": [90, 85, 92] }     |
|                                               |
|  "student2" -> { "name": "Bob",              |
|                  "age": 22,                   |
|                  "grades": [78, 82, 88] }     |
+----------------------------------------------+
```

```python
students = {
    "student1": {
        "name": "Alice",
        "age": 20,
        "grades": [90, 85, 92]
    },
    "student2": {
        "name": "Bob",
        "age": 22,
        "grades": [78, 82, 88]
    }
}

# Access nested data
print(students["student1"]["name"])
print(students["student2"]["grades"])

# Access a specific grade
print(students["student1"]["grades"][0])
```

**Expected Output:**
```
Alice
[78, 82, 88]
90
```

**Line-by-line explanation:**
- **Line 15:** First, get `students["student1"]`. That gives you the inner dictionary. Then get `["name"]` from it.
- **Line 16:** Get student2's grades list.
- **Line 19:** Chain the access: dictionary -> inner dictionary -> list item.

### Looping Through Nested Dictionaries

```python
students = {
    "student1": {"name": "Alice", "age": 20},
    "student2": {"name": "Bob", "age": 22},
    "student3": {"name": "Charlie", "age": 21}
}

for student_id, info in students.items():
    print(f"{student_id}: {info['name']}, age {info['age']}")
```

**Expected Output:**
```
student1: Alice, age 20
student2: Bob, age 22
student3: Charlie, age 21
```

---

## 7.8 Dictionary Comprehensions

Just like list comprehensions, you can create dictionaries in one line.

```python
# Create a dictionary of squares
squares = {x: x**2 for x in range(6)}
print(squares)

# Create from two lists using zip
names = ["Alice", "Bob", "Charlie"]
ages = [20, 22, 21]
name_age = {name: age for name, age in zip(names, ages)}
print(name_age)

# With a condition
scores = {"Alice": 95, "Bob": 72, "Charlie": 88, "Diana": 65}
passing = {name: score for name, score in scores.items() if score >= 80}
print("Passing:", passing)
```

**Expected Output:**
```
{0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
{'Alice': 20, 'Bob': 22, 'Charlie': 21}
Passing: {'Alice': 95, 'Charlie': 88}
```

**Line-by-line explanation:**
- **Line 2:** `{x: x**2 for x in range(6)}` creates keys 0-5 with their squares as values.
- **Line 8:** `zip(names, ages)` pairs up items from both lists. The comprehension turns each pair into a key-value entry.
- **Line 13:** Only keeps entries where the score is 80 or above.

```
+-----------------------------------------------------+
|  Dictionary Comprehension Pattern:                   |
|                                                      |
|  {key: value  for item in iterable  if condition}    |
|   ^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^     |
|   what to     where to get          filter           |
|   store       the items             (optional)       |
+-----------------------------------------------------+
```

---

## 7.9 Checking If a Key Exists

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

# Check if a key exists
if "name" in student:
    print("Name exists!")

if "email" not in student:
    print("Email does not exist.")

# Practical use: safe access
key = "email"
if key in student:
    print(student[key])
else:
    print(f"'{key}' not found in student dictionary.")
```

**Expected Output:**
```
Name exists!
Email does not exist.
'email' not found in student dictionary.
```

---

## 7.10 What Is a Set?

A set is a collection of **unique items**. No duplicates allowed.

Think of a bag of marbles. Each marble is a different color. If you try to add a second red marble, the bag ignores it. It already has one.

```
+----------------------------------------------+
|              Set vs List                      |
+----------------------------------------------+
|                                               |
|  List: [1, 2, 2, 3, 3, 3]  (duplicates OK)   |
|  Set:  {1, 2, 3}           (unique only)      |
|                                               |
|  List: ordered (positions matter)             |
|  Set:  unordered (no positions)               |
+----------------------------------------------+
```

```python
# Creating a set
fruits = {"apple", "banana", "cherry"}
print(fruits)

# Duplicates are automatically removed
numbers = {1, 2, 2, 3, 3, 3, 4}
print(numbers)

# Create a set from a list (removes duplicates!)
my_list = [1, 1, 2, 2, 3, 3, 4, 5, 5]
unique = set(my_list)
print("Original list:", my_list)
print("Unique values:", unique)
```

**Expected Output:**
```
{'cherry', 'apple', 'banana'}
{1, 2, 3, 4}
Original list: [1, 1, 2, 2, 3, 3, 4, 5, 5]
Unique values: {1, 2, 3, 4, 5}
```

**Line-by-line explanation:**
- **Line 2:** Sets use curly braces `{}`, like dictionaries. But sets have single values, not key-value pairs.
- **Line 6:** We put in three 3s, two 2s, and two 1s. The set keeps only one of each.
- **Line 10-11:** `set()` converts a list to a set, removing duplicates. Very useful!

> **Note:** Sets are unordered. The items might print in a different order each time.

### Adding and Removing Items in Sets

```python
colors = {"red", "green", "blue"}
print("Start:", colors)

# Add one item
colors.add("yellow")
print("After add:", colors)

# Try to add a duplicate (nothing happens)
colors.add("red")
print("After adding duplicate:", colors)

# Remove an item
colors.remove("green")
print("After remove:", colors)

# discard() - like remove, but no error if item missing
colors.discard("purple")  # No error even though purple is not there
print("After discard:", colors)
```

**Expected Output:**
```
Start: {'blue', 'green', 'red'}
After add: {'blue', 'green', 'yellow', 'red'}
After adding duplicate: {'blue', 'green', 'yellow', 'red'}
After remove: {'blue', 'yellow', 'red'}
After discard: {'blue', 'yellow', 'red'}
```

---

## 7.11 Set Operations

Sets shine when you need to compare groups of data.

```
+-----------------------------------------------+
|  Set Operations (Venn Diagram Style)           |
+-----------------------------------------------+
|                                                |
|  A = {1, 2, 3, 4}    B = {3, 4, 5, 6}         |
|                                                |
|  Union (A | B):        {1, 2, 3, 4, 5, 6}      |
|  Everything from both                          |
|                                                |
|  Intersection (A & B): {3, 4}                  |
|  Only items in BOTH                            |
|                                                |
|  Difference (A - B):   {1, 2}                  |
|  Items in A but NOT in B                       |
|                                                |
|  Symmetric Diff (A ^ B): {1, 2, 5, 6}          |
|  Items in one but NOT both                     |
+-----------------------------------------------+
```

```python
python_students = {"Alice", "Bob", "Charlie", "Diana"}
java_students = {"Charlie", "Diana", "Eve", "Frank"}

# Union: all students (from either class)
all_students = python_students | java_students
print("All students:", all_students)

# Intersection: students in BOTH classes
both_classes = python_students & java_students
print("Both classes:", both_classes)

# Difference: only in Python class
only_python = python_students - java_students
print("Only Python:", only_python)

# Symmetric difference: in one class but not both
one_class_only = python_students ^ java_students
print("One class only:", one_class_only)
```

**Expected Output:**
```
All students: {'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank'}
Both classes: {'Charlie', 'Diana'}
Only Python: {'Alice', 'Bob'}
One class only: {'Alice', 'Bob', 'Eve', 'Frank'}
```

**Line-by-line explanation:**
- **Line 5:** `|` means union. Combine everything. Duplicates are removed automatically.
- **Line 9:** `&` means intersection. Only items found in both sets.
- **Line 13:** `-` means difference. Items in the first set but not in the second.
- **Line 17:** `^` means symmetric difference. Items in one set OR the other, but NOT both.

### Method Names (Alternative Syntax)

```python
A = {1, 2, 3}
B = {2, 3, 4}

print("Union:", A.union(B))
print("Intersection:", A.intersection(B))
print("Difference:", A.difference(B))
print("Symmetric Diff:", A.symmetric_difference(B))
```

**Expected Output:**
```
Union: {1, 2, 3, 4}
Intersection: {2, 3}
Difference: {1}
Symmetric Diff: {1, 4}
```

---

## 7.12 Practical Examples

### Example 1: Word Frequency Counter

```python
text = "the cat sat on the mat the cat"
words = text.split()

# Count each word
word_count = {}
for word in words:
    if word in word_count:
        word_count[word] += 1
    else:
        word_count[word] = 1

print("Word counts:", word_count)

# Find the most common word
most_common = max(word_count, key=word_count.get)
print(f"Most common word: '{most_common}' ({word_count[most_common]} times)")
```

**Expected Output:**
```
Word counts: {'the': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1}
Most common word: 'the' (3 times)
```

**Line-by-line explanation:**
- **Line 2:** `.split()` breaks the string into a list of words.
- **Lines 5-10:** Loop through each word. If we have seen it before, add 1. Otherwise, start at 1.
- **Line 15:** `max()` with `key=word_count.get` finds the key with the highest value.

### Example 2: Finding Unique Items

```python
# Survey responses (people can respond multiple times)
responses = ["Yes", "No", "Yes", "Maybe", "Yes", "No", "Maybe", "Yes"]

# Get unique responses
unique_responses = set(responses)
print("Unique responses:", unique_responses)
print("Number of unique responses:", len(unique_responses))

# Count each response
response_count = {r: responses.count(r) for r in unique_responses}
print("Response counts:", response_count)
```

**Expected Output:**
```
Unique responses: {'Maybe', 'Yes', 'No'}
Number of unique responses: 3
Response counts: {'Maybe': 2, 'Yes': 4, 'No': 2}
```

### Example 3: Simple Data Record for ML

```python
# A data sample as a dictionary (common in ML)
data_point = {
    "features": [5.1, 3.5, 1.4, 0.2],
    "label": "setosa",
    "sample_id": 1
}

print(f"Sample {data_point['sample_id']}:")
print(f"  Features: {data_point['features']}")
print(f"  Label: {data_point['label']}")
print(f"  Number of features: {len(data_point['features'])}")
```

**Expected Output:**
```
Sample 1:
  Features: [5.1, 3.5, 1.4, 0.2]
  Label: setosa
  Number of features: 4
```

---

## Common Mistakes

### Mistake 1: Using [] Instead of {} or Vice Versa

```python
# This is a SET (not a dictionary)
my_set = {"apple", "banana"}

# This is a DICTIONARY (has key: value pairs)
my_dict = {"fruit": "apple", "color": "red"}

# This is an empty DICTIONARY (not a set!)
empty_dict = {}

# To create an empty SET, use set()
empty_set = set()

print(type(my_set))
print(type(my_dict))
print(type(empty_dict))
print(type(empty_set))
```

**Expected Output:**
```
<class 'set'>
<class 'dict'>
<class 'dict'>
<class 'set'>
```

### Mistake 2: Accessing a Key That Does Not Exist

```python
student = {"name": "Alice"}

# WRONG - causes KeyError
try:
    print(student["age"])
except KeyError as e:
    print("KeyError:", e)

# RIGHT - use .get()
print("Age:", student.get("age", "Unknown"))
```

**Expected Output:**
```
KeyError: 'age'
Age: Unknown
```

### Mistake 3: Using a Mutable Key

```python
# WRONG - lists cannot be dictionary keys
try:
    bad_dict = {[1, 2]: "value"}
except TypeError as e:
    print("Error:", e)

# RIGHT - use a tuple instead
good_dict = {(1, 2): "value"}
print("Works:", good_dict)
```

**Expected Output:**
```
Error: unhashable type: 'list'
Works: {(1, 2): 'value'}
```

### Mistake 4: Forgetting That Sets Are Unordered

```python
# Sets have no index
my_set = {"a", "b", "c"}

try:
    print(my_set[0])  # This fails!
except TypeError as e:
    print("Error:", e)

# Convert to list first if you need indexing
my_list = list(my_set)
print("First item:", my_list[0])
```

**Expected Output:**
```
Error: 'set' object is not subscriptable
First item: a
```

---

## Best Practices

1. **Use `.get()` for safe access.** It prevents crashes when a key might not exist.
2. **Use meaningful key names.** Write `student["first_name"]` instead of `student["fn"]`.
3. **Use sets to remove duplicates.** Converting a list to a set is the fastest way.
4. **Use dictionary comprehensions for simple transformations.** But keep them readable.
5. **Use `in` to check for keys.** Write `if "name" in student` before accessing it.
6. **Choose the right data structure:**
   - Need key-value pairs? Use a dictionary.
   - Need unique items? Use a set.
   - Need ordered, changeable items? Use a list.
   - Need ordered, unchangeable items? Use a tuple.

---

## Quick Summary

| Operation | Dictionary Syntax | Set Syntax |
|-----------|------------------|------------|
| Create | `{"key": value}` | `{item1, item2}` |
| Empty | `{}` or `dict()` | `set()` |
| Access | `d["key"]` or `d.get("key")` | N/A (no indexing) |
| Add | `d["key"] = value` | `s.add(item)` |
| Remove | `del d["key"]` or `d.pop("key")` | `s.remove(item)` |
| Check exists | `"key" in d` | `item in s` |
| All keys | `d.keys()` | N/A |
| All values | `d.values()` | N/A |
| Key-value pairs | `d.items()` | N/A |
| Union | N/A | `a \| b` |
| Intersection | N/A | `a & b` |
| Difference | N/A | `a - b` |

---

## Key Points to Remember

1. **Dictionaries store key-value pairs.** Keys must be unique and immutable.
2. **Use `.get()` for safe access.** It returns `None` (or a default) instead of crashing.
3. **`.keys()`, `.values()`, `.items()`** let you access different parts of a dictionary.
4. **Nested dictionaries** hold dictionaries inside dictionaries.
5. **Sets store unique items only.** Duplicates are automatically removed.
6. **Set operations** let you combine, compare, and filter groups of data.
7. **`{}` creates a dictionary, not a set.** Use `set()` for an empty set.
8. **Dictionary comprehensions** work like list comprehensions but produce dictionaries.

---

## Practice Questions

**Question 1:** What will this code print?
```python
d = {"a": 1, "b": 2, "c": 3}
print(d["b"])
print(d.get("d", 0))
```

<details>
<summary>Answer</summary>

```
2
0
```
`d["b"]` returns the value for key "b" which is 2. `d.get("d", 0)` returns 0 because key "d" does not exist, and 0 is the default.
</details>

---

**Question 2:** How do you remove duplicates from a list?

<details>
<summary>Answer</summary>

Convert the list to a set, then back to a list:
```python
my_list = [1, 2, 2, 3, 3, 4]
unique_list = list(set(my_list))
print(unique_list)  # [1, 2, 3, 4]
```
Note: This does not preserve the original order. To preserve order, use `list(dict.fromkeys(my_list))`.
</details>

---

**Question 3:** What is the difference between `remove()` and `pop()` for dictionaries?

<details>
<summary>Answer</summary>

Dictionaries do not have a `remove()` method. They use:
- `del d["key"]` to remove a key (does not return the value).
- `d.pop("key")` to remove a key and return its value.
</details>

---

**Question 4:** Given sets A = {1, 2, 3, 4} and B = {3, 4, 5, 6}, what is A & B?

<details>
<summary>Answer</summary>

`A & B` is the intersection: `{3, 4}`. It contains only items found in both sets.
</details>

---

**Question 5:** Can you use a list as a dictionary key? Why or why not?

<details>
<summary>Answer</summary>

No. Dictionary keys must be immutable (unchangeable). Lists are mutable, so they cannot be keys. Use a tuple instead:
```python
# This works:
d = {(1, 2): "point"}

# This fails:
# d = {[1, 2]: "point"}  # TypeError
```
</details>

---

## Exercises

### Exercise 1: Student Grade Book

Create a dictionary that stores 4 students and their grades (as lists). Then:
1. Print all student names.
2. Add a new grade for one student.
3. Calculate and print the average grade for each student.

<details>
<summary>Solution</summary>

```python
# Create the grade book
grade_book = {
    "Alice": [90, 85, 92],
    "Bob": [78, 82, 88],
    "Charlie": [95, 91, 87],
    "Diana": [72, 68, 75]
}

# Step 1: Print all names
print("Students:", list(grade_book.keys()))

# Step 2: Add a new grade for Alice
grade_book["Alice"].append(96)
print("Alice's grades:", grade_book["Alice"])

# Step 3: Calculate averages
print("\nGrade Averages:")
for student, grades in grade_book.items():
    average = sum(grades) / len(grades)
    print(f"  {student}: {average:.1f}")
```

**Expected Output:**
```
Students: ['Alice', 'Bob', 'Charlie', 'Diana']
Alice's grades: [90, 85, 92, 96]

Grade Averages:
  Alice: 90.8
  Bob: 82.7
  Charlie: 91.0
  Diana: 71.7
```
</details>

---

### Exercise 2: Common Friends

Two people have lists of friends. Use sets to find:
1. All friends combined.
2. Friends they have in common.
3. Friends unique to each person.

<details>
<summary>Solution</summary>

```python
alice_friends = {"Bob", "Charlie", "Diana", "Eve"}
bob_friends = {"Charlie", "Eve", "Frank", "Grace"}

# Step 1: All friends combined (union)
all_friends = alice_friends | bob_friends
print("All friends:", all_friends)

# Step 2: Common friends (intersection)
common = alice_friends & bob_friends
print("Common friends:", common)

# Step 3: Unique to each person (difference)
only_alice = alice_friends - bob_friends
only_bob = bob_friends - alice_friends
print("Only Alice's friends:", only_alice)
print("Only Bob's friends:", only_bob)
```

**Expected Output:**
```
All friends: {'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace'}
Common friends: {'Charlie', 'Eve'}
Only Alice's friends: {'Bob', 'Diana'}
Only Bob's friends: {'Frank', 'Grace'}
```
</details>

---

### Exercise 3: Word Counter

Write a program that:
1. Takes a sentence as a string.
2. Counts how many times each word appears (using a dictionary).
3. Prints the word with the highest count.

<details>
<summary>Solution</summary>

```python
sentence = "I like Python and I like coding and I like learning"
words = sentence.lower().split()

# Count words
word_count = {}
for word in words:
    word_count[word] = word_count.get(word, 0) + 1

print("Word counts:")
for word, count in word_count.items():
    print(f"  '{word}': {count}")

# Find most common word
most_common = max(word_count, key=word_count.get)
print(f"\nMost common: '{most_common}' ({word_count[most_common]} times)")
```

**Expected Output:**
```
Word counts:
  'i': 3
  'like': 3
  'python': 1
  'and': 2
  'coding': 1
  'learning': 1

Most common: 'i' (3 times)
```
</details>

---

## What Is Next?

You now know how to store and organize data with lists, tuples, dictionaries, and sets. In Chapter 8, you will learn about **functions** — reusable blocks of code that work like recipes. Functions will help you write cleaner, shorter, and more organized programs. They are essential for any serious programming, especially in AI and data science.
