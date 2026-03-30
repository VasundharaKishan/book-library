# Chapter 6: Lists and Tuples — Organizing Your Data

## What You Will Learn

- What lists are and why they matter
- How to create lists and access items
- How indexing works (starting from 0)
- How to slice lists to get parts of them
- How to add, remove, and change items
- How to sort lists and find their length
- What list comprehensions are
- What tuples are and how they differ from lists
- When to use lists vs tuples

## Why This Chapter Matters

Think about your daily life. You make shopping lists. You keep to-do lists. You have a list of favorite movies. Lists are everywhere.

In programming, lists are just as important. They let you store multiple items in one place. Instead of creating 100 separate variables, you put everything in one list.

When you work with AI and machine learning later, you will use lists constantly. A dataset is basically a big list of data points. A neural network has lists of weights. Training results go into lists.

Lists and tuples are your first step into **data structures**. A data structure is a way to organize data. Think of it like choosing the right container. You would not put soup in a paper bag. You would not put a sandwich in a glass. The right container matters.

---

## 6.1 What Is a List?

A list is a collection of items in a specific order.

Think of a **shopping list**:

```
+---------------------------+
|     My Shopping List      |
+---------------------------+
| 1. Eggs                   |
| 2. Milk                   |
| 3. Bread                  |
| 4. Butter                 |
| 5. Cheese                 |
+---------------------------+
```

In Python, this looks like:

```python
shopping_list = ["Eggs", "Milk", "Bread", "Butter", "Cheese"]
print(shopping_list)
```

**Expected Output:**
```
['Eggs', 'Milk', 'Bread', 'Butter', 'Cheese']
```

**Line-by-line explanation:**
- **Line 1:** We create a list called `shopping_list`. We use square brackets `[]`. Each item is separated by a comma.
- **Line 2:** We print the entire list. Python shows it with square brackets.

### Key Facts About Lists

```
+-----------------------------------------------+
|            Python Lists                        |
+-----------------------------------------------+
| - Ordered (items stay in the order you add)    |
| - Changeable (you can add, remove, modify)     |
| - Allow duplicates (same item can appear twice)|
| - Can hold different types (mix numbers, text) |
+-----------------------------------------------+
```

### Lists Can Hold Anything

```python
# A list of numbers
scores = [95, 87, 92, 78, 100]
print(scores)

# A list of mixed types
mixed = ["Alice", 25, True, 3.14]
print(mixed)

# An empty list
empty = []
print(empty)
```

**Expected Output:**
```
[95, 87, 92, 78, 100]
['Alice', 25, True, 3.14]
[]
```

**Line-by-line explanation:**
- **Line 2:** A list of integers. All items are numbers.
- **Line 3:** Print the number list.
- **Line 6:** A list with a string, an integer, a boolean, and a float. Python does not mind mixing types.
- **Line 7:** Print the mixed list.
- **Line 10:** An empty list. It has no items yet. We can add items later.
- **Line 11:** Print the empty list. It shows `[]`.

---

## 6.2 Indexing — Finding Items by Position

Every item in a list has a **position number** called an **index**.

Here is the important part: **Python starts counting at 0, not 1.**

```
+---------------------------------------------+
|  shopping_list = ["Eggs", "Milk", "Bread",  |
|                    "Butter", "Cheese"]       |
+---------------------------------------------+
|  Index:    0       1        2       3     4  |
+---------------------------------------------+
|  Item:   Eggs    Milk    Bread  Butter Cheese|
+---------------------------------------------+
```

Think of it like an elevator in a building. In many countries, the ground floor is floor 0, not floor 1.

```python
shopping_list = ["Eggs", "Milk", "Bread", "Butter", "Cheese"]

# Get the first item (index 0)
first_item = shopping_list[0]
print("First item:", first_item)

# Get the third item (index 2)
third_item = shopping_list[2]
print("Third item:", third_item)

# Get the last item (index 4)
last_item = shopping_list[4]
print("Last item:", last_item)
```

**Expected Output:**
```
First item: Eggs
Third item: Bread
Last item: Cheese
```

**Line-by-line explanation:**
- **Line 4:** `shopping_list[0]` gets the item at index 0. That is "Eggs".
- **Line 5:** Print it.
- **Line 8:** `shopping_list[2]` gets the item at index 2. Count: 0=Eggs, 1=Milk, 2=Bread.
- **Line 12:** `shopping_list[4]` gets the last item. There are 5 items, so the last index is 4.

### Negative Indexing

Python has a shortcut. You can count from the end using negative numbers.

```
+-----------------------------------------------+
|  Positive index:   0     1      2      3    4  |
|  Item:           Eggs  Milk  Bread  Butter Cheese|
|  Negative index:  -5    -4    -3     -2    -1  |
+-----------------------------------------------+
```

```python
shopping_list = ["Eggs", "Milk", "Bread", "Butter", "Cheese"]

# Last item
print(shopping_list[-1])

# Second to last
print(shopping_list[-2])

# First item (using negative)
print(shopping_list[-5])
```

**Expected Output:**
```
Cheese
Butter
Eggs
```

**Line-by-line explanation:**
- **Line 4:** `-1` means "the last item." This is very useful when you do not know how long the list is.
- **Line 7:** `-2` means "second from the end." That is Butter.
- **Line 10:** `-5` goes all the way back to the first item.

---

## 6.3 Slicing — Getting Parts of a List

Slicing lets you get a **portion** of a list. Think of slicing a loaf of bread. You pick where to start cutting and where to stop.

The syntax is: `list[start:stop]`

Important rule: **The start index is included. The stop index is NOT included.**

```
+---------------------------------------------------+
|  list[start:stop]                                  |
|                                                    |
|  - start: where to begin (included)                |
|  - stop:  where to end (NOT included)              |
|                                                    |
|  Think of it like a fence:                         |
|  You include the start post.                       |
|  You stop BEFORE the stop post.                    |
+---------------------------------------------------+
```

```python
fruits = ["apple", "banana", "cherry", "date", "elderberry"]

# Get items from index 1 to 3 (not including 3)
print(fruits[1:3])

# Get the first 3 items
print(fruits[0:3])

# Get items from index 2 to the end
print(fruits[2:])

# Get items from the start to index 3
print(fruits[:3])

# Get a copy of the whole list
print(fruits[:])
```

**Expected Output:**
```
['banana', 'cherry']
['apple', 'banana', 'cherry']
['cherry', 'date', 'elderberry']
['apple', 'banana', 'cherry']
['apple', 'banana', 'cherry', 'date', 'elderberry']
```

**Line-by-line explanation:**
- **Line 4:** `[1:3]` gets index 1 and 2. It stops before index 3.
- **Line 7:** `[0:3]` gets index 0, 1, and 2. The first three items.
- **Line 10:** `[2:]` starts at index 2 and goes to the end. When you leave out the stop, Python goes to the end.
- **Line 13:** `[:3]` starts at the beginning and stops before index 3. When you leave out the start, Python starts from 0.
- **Line 16:** `[:]` gets everything. This is a quick way to copy a list.

### Slicing with Steps

You can also skip items using a third number: `list[start:stop:step]`

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Every other item
print(numbers[::2])

# Every other item starting from index 1
print(numbers[1::2])

# Reverse the list
print(numbers[::-1])
```

**Expected Output:**
```
[0, 2, 4, 6, 8]
[1, 3, 5, 7, 9]
[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
```

**Line-by-line explanation:**
- **Line 4:** `[::2]` means start at the beginning, go to the end, step by 2. So it gets every other item.
- **Line 7:** `[1::2]` starts at index 1, goes to the end, step by 2. Gets odd-indexed items.
- **Line 10:** `[::-1]` reverses the list. The step is -1, so it goes backwards.

---

## 6.4 Modifying Lists

Lists are **mutable**. That means you can change them after creation.

### Changing an Item

```python
colors = ["red", "green", "blue"]
print("Before:", colors)

# Change the second item
colors[1] = "yellow"
print("After:", colors)
```

**Expected Output:**
```
Before: ['red', 'green', 'blue']
After: ['red', 'yellow', 'blue']
```

**Line-by-line explanation:**
- **Line 5:** `colors[1] = "yellow"` replaces "green" with "yellow." We use the index to say which item to change.

### Adding Items

There are several ways to add items to a list.

```python
# Start with a list
fruits = ["apple", "banana"]
print("Start:", fruits)

# append() - adds to the END
fruits.append("cherry")
print("After append:", fruits)

# insert() - adds at a SPECIFIC position
fruits.insert(1, "blueberry")
print("After insert:", fruits)

# extend() - adds MULTIPLE items
fruits.extend(["date", "elderberry"])
print("After extend:", fruits)
```

**Expected Output:**
```
Start: ['apple', 'banana']
After append: ['apple', 'banana', 'cherry']
After insert: ['apple', 'blueberry', 'banana', 'cherry']
After extend: ['apple', 'blueberry', 'banana', 'cherry', 'date', 'elderberry']
```

**Line-by-line explanation:**
- **Line 6:** `append("cherry")` adds "cherry" at the end. Like adding an item to the bottom of your shopping list.
- **Line 10:** `insert(1, "blueberry")` puts "blueberry" at index 1. Everything else shifts to the right.
- **Line 14:** `extend(["date", "elderberry"])` adds multiple items at the end. It is like appending several items at once.

```
+-----------------------------------------------+
|  append vs insert vs extend                    |
+-----------------------------------------------+
|                                                |
|  append("X"):    [A, B, C] -> [A, B, C, X]    |
|                              adds to end       |
|                                                |
|  insert(1,"X"):  [A, B, C] -> [A, X, B, C]    |
|                              adds at position  |
|                                                |
|  extend([X,Y]):  [A, B, C] -> [A, B, C, X, Y] |
|                              adds multiple     |
+-----------------------------------------------+
```

### Removing Items

```python
animals = ["cat", "dog", "fish", "bird", "dog"]
print("Start:", animals)

# remove() - removes the FIRST matching item
animals.remove("dog")
print("After remove:", animals)

# pop() - removes by INDEX and returns the item
removed = animals.pop(2)
print("Popped:", removed)
print("After pop:", animals)

# pop() with no argument - removes the LAST item
last = animals.pop()
print("Popped last:", last)
print("After pop:", animals)

# del - removes by index (does not return the item)
del animals[0]
print("After del:", animals)
```

**Expected Output:**
```
Start: ['cat', 'dog', 'fish', 'bird', 'dog']
After remove: ['cat', 'fish', 'bird', 'dog']
Popped: bird
After pop: ['cat', 'fish', 'dog']
Popped last: dog
After pop: ['cat', 'fish']
After del: ['fish']
```

**Line-by-line explanation:**
- **Line 5:** `remove("dog")` finds the first "dog" and removes it. The second "dog" stays.
- **Line 9:** `pop(2)` removes the item at index 2 and gives it back. We store it in `removed`.
- **Line 14:** `pop()` with no number removes the last item.
- **Line 19:** `del animals[0]` deletes the item at index 0. Unlike `pop()`, it does not give the item back.

---

## 6.5 Sorting Lists

### sort() — Changes the Original List

```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
print("Before:", numbers)

# Sort in ascending order (smallest to biggest)
numbers.sort()
print("Sorted:", numbers)

# Sort in descending order (biggest to smallest)
numbers.sort(reverse=True)
print("Reversed:", numbers)
```

**Expected Output:**
```
Before: [3, 1, 4, 1, 5, 9, 2, 6]
Sorted: [1, 1, 2, 3, 4, 5, 6, 9]
Reversed: [9, 6, 5, 4, 3, 2, 1, 1]
```

### sorted() — Creates a New List

```python
original = [3, 1, 4, 1, 5]
new_list = sorted(original)

print("Original:", original)
print("New list:", new_list)
```

**Expected Output:**
```
Original: [3, 1, 4, 1, 5]
New list: [1, 1, 3, 4, 5]
```

**Line-by-line explanation:**
- **Line 2:** `sorted()` creates a brand new sorted list. The original list stays the same.
- **Line 4-5:** See? The original is unchanged.

```
+-------------------------------------------+
|  sort() vs sorted()                        |
+-------------------------------------------+
|                                            |
|  .sort()   -> changes the ORIGINAL list    |
|               returns None                 |
|                                            |
|  sorted()  -> creates a NEW sorted list    |
|               original stays the same      |
+-------------------------------------------+
```

---

## 6.6 Useful List Operations

### len() — Finding the Length

```python
fruits = ["apple", "banana", "cherry"]
print("Number of fruits:", len(fruits))

empty = []
print("Number of items:", len(empty))
```

**Expected Output:**
```
Number of fruits: 3
Number of items: 0
```

### Checking If an Item Exists

```python
fruits = ["apple", "banana", "cherry"]

# Check with 'in' keyword
if "banana" in fruits:
    print("Yes, banana is in the list!")

if "grape" not in fruits:
    print("No, grape is NOT in the list.")
```

**Expected Output:**
```
Yes, banana is in the list!
No, grape is NOT in the list.
```

### Counting and Finding

```python
numbers = [1, 2, 3, 2, 4, 2, 5]

# count() - how many times does 2 appear?
print("Count of 2:", numbers.count(2))

# index() - where is the first 2?
print("First 2 is at index:", numbers.index(2))

# min and max
print("Smallest:", min(numbers))
print("Largest:", max(numbers))
print("Total:", sum(numbers))
```

**Expected Output:**
```
Count of 2: 3
First 2 is at index: 1
Smallest: 1
Largest: 5
Total: 19
```

---

## 6.7 List Comprehensions — A Shortcut

List comprehensions let you create lists in one line. They are a Python shortcut.

Think of it like a factory assembly line:

```
+---------------------------------------------------+
|           List Comprehension Factory               |
|                                                    |
|  Raw materials   ->  [Process]  ->  Finished list  |
|  (old list)         (transform)    (new list)      |
|                                                    |
|  [1, 2, 3, 4, 5] -> [x * 2]   -> [2, 4, 6, 8, 10]|
+---------------------------------------------------+
```

### Basic Syntax

```python
# The long way
squares = []
for x in range(5):
    squares.append(x ** 2)
print("Long way:", squares)

# The short way (list comprehension)
squares = [x ** 2 for x in range(5)]
print("Short way:", squares)
```

**Expected Output:**
```
Long way: [0, 1, 4, 9, 16]
Short way: [0, 1, 4, 9, 16]
```

**Line-by-line explanation:**
- **Lines 2-4:** The traditional way. Create an empty list, loop through numbers, append each square.
- **Line 8:** The comprehension does the same thing in one line. Read it as: "Give me x squared, for each x in range 5."

### With a Condition

```python
# Get only even numbers from 0 to 9
evens = [x for x in range(10) if x % 2 == 0]
print("Evens:", evens)

# Get words longer than 3 letters
words = ["hi", "hello", "hey", "howdy", "yo"]
long_words = [w for w in words if len(w) > 3]
print("Long words:", long_words)
```

**Expected Output:**
```
Evens: [0, 2, 4, 6, 8]
Long words: ['hello', 'howdy']
```

**Line-by-line explanation:**
- **Line 2:** Read it as: "Give me x, for each x in range 10, but only if x is even."
- **Line 7:** "Give me the word w, for each w in words, but only if its length is more than 3."

```
+----------------------------------------------------+
|  List Comprehension Pattern:                        |
|                                                     |
|  [expression  for item in iterable  if condition]   |
|   ^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^    |
|   what to     where to get          filter          |
|   produce     the items             (optional)      |
+----------------------------------------------------+
```

---

## 6.8 Tuples — Immutable Lists

A tuple is like a list, but you **cannot change it** after creation.

Think of a list as a whiteboard (you can erase and rewrite). Think of a tuple as a printed book (once printed, it is fixed).

```python
# Creating a tuple (use parentheses, not square brackets)
coordinates = (10, 20)
print(coordinates)

# A tuple with more items
colors = ("red", "green", "blue")
print(colors)

# Accessing items (same as lists)
print("First color:", colors[0])
print("Last color:", colors[-1])
```

**Expected Output:**
```
(10, 20)
('red', 'green', 'blue')
First color: red
Last color: blue
```

**Line-by-line explanation:**
- **Line 2:** Tuples use parentheses `()` instead of square brackets `[]`.
- **Line 6:** A tuple with three strings.
- **Line 10-11:** Indexing works the same as lists.

### Tuples Cannot Be Changed

```python
colors = ("red", "green", "blue")

# This will cause an ERROR:
try:
    colors[0] = "yellow"
except TypeError as e:
    print("Error:", e)
```

**Expected Output:**
```
Error: 'tuple' object does not support item assignment
```

**Line-by-line explanation:**
- **Line 5:** We try to change the first item. Python says NO. Tuples are immutable (unchangeable).

### Tuple Unpacking

Unpacking is a neat trick. You can assign each item in a tuple to its own variable in one line.

```python
# Unpacking a tuple
person = ("Alice", 30, "Engineer")
name, age, job = person

print("Name:", name)
print("Age:", age)
print("Job:", job)
```

**Expected Output:**
```
Name: Alice
Age: 30
Job: Engineer
```

**Line-by-line explanation:**
- **Line 3:** This takes each item from the tuple and puts it into a separate variable. The first item goes to `name`, the second to `age`, the third to `job`.

```python
# Unpacking works with lists too
coordinates = [4, 7]
x, y = coordinates
print(f"x = {x}, y = {y}")

# Swap two variables using unpacking
a = 10
b = 20
a, b = b, a
print(f"a = {a}, b = {b}")
```

**Expected Output:**
```
x = 4, y = 7
a = 20, b = 10
```

**Line-by-line explanation:**
- **Line 3:** Unpack a list into x and y.
- **Line 9:** A famous Python trick. Swap two variables in one line. No temporary variable needed!

---

## 6.9 When to Use Lists vs Tuples

```
+------------------------------------------------+
|          Lists vs Tuples                        |
+------------------------------------------------+
|  Feature        |  List       |  Tuple          |
+------------------------------------------------+
|  Symbol         |  []         |  ()             |
|  Changeable?    |  Yes        |  No             |
|  Use when...    |  Data may   |  Data should    |
|                 |  change     |  stay fixed     |
+------------------------------------------------+
|                                                 |
|  Examples:                                      |
|  List:  shopping items, scores, to-do tasks     |
|  Tuple: coordinates (x,y), RGB color (255,0,0)  |
|         days of week, database records           |
+------------------------------------------------+
```

### Why Use Tuples?

1. **Safety:** Data cannot be accidentally changed.
2. **Speed:** Tuples are slightly faster than lists.
3. **Dictionary keys:** Tuples can be used as dictionary keys. Lists cannot. (You will learn about dictionaries in the next chapter.)

```python
# Good use of tuple: fixed data
months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# Good use of list: data that changes
grades = [85, 92, 78]
grades.append(95)  # Student got a new grade
print("Months:", months[0], "-", months[-1])
print("Grades:", grades)
```

**Expected Output:**
```
Months: Jan - Dec
Grades: [85, 92, 78, 95]
```

---

## 6.10 Practical Example — Data for Machine Learning

Here is a real-world example. When preparing data for AI, you often work with lists.

```python
# Student test scores
scores = [85, 92, 78, 95, 88, 76, 91, 83, 97, 80]

# Find basic statistics
total_students = len(scores)
average_score = sum(scores) / len(scores)
highest = max(scores)
lowest = min(scores)

print(f"Total students: {total_students}")
print(f"Average score: {average_score}")
print(f"Highest score: {highest}")
print(f"Lowest score: {lowest}")

# Separate passing and failing (passing = 80 or above)
passing = [s for s in scores if s >= 80]
failing = [s for s in scores if s < 80]

print(f"\nPassing scores: {passing}")
print(f"Failing scores: {failing}")
print(f"Pass rate: {len(passing)/total_students*100:.1f}%")
```

**Expected Output:**
```
Total students: 10
Average score: 86.5
Highest score: 97
Lowest score: 76

Passing scores: [85, 92, 95, 88, 91, 83, 97, 80]
Failing scores: [78, 76]
Pass rate: 80.0%
```

**Line-by-line explanation:**
- **Line 5:** `len(scores)` counts how many scores we have.
- **Line 6:** Average = total divided by count.
- **Line 7-8:** `max()` and `min()` find the biggest and smallest values.
- **Line 16:** List comprehension filters scores that are 80 or above.
- **Line 17:** Another comprehension filters scores below 80.
- **Line 21:** Calculate the pass rate as a percentage.

---

## Common Mistakes

### Mistake 1: Index Out of Range

```python
fruits = ["apple", "banana", "cherry"]
# There is no index 3! (valid: 0, 1, 2)
try:
    print(fruits[3])
except IndexError as e:
    print("Error:", e)
```

**Expected Output:**
```
Error: list index out of range
```

**Fix:** Remember, if a list has 3 items, the last index is 2 (not 3).

### Mistake 2: Forgetting That sort() Returns None

```python
numbers = [3, 1, 4, 1, 5]

# WRONG - sort() returns None
result = numbers.sort()
print("Result:", result)
print("Numbers:", numbers)
```

**Expected Output:**
```
Result: None
Numbers: [1, 1, 3, 4, 5]
```

**Fix:** Use `sorted()` if you want a new sorted list. Or just call `.sort()` on its own.

### Mistake 3: Modifying a List While Looping

```python
# WRONG way - unpredictable results
numbers = [1, 2, 3, 4, 5]
# Don't do this:
# for n in numbers:
#     if n % 2 == 0:
#         numbers.remove(n)

# RIGHT way - use list comprehension
numbers = [1, 2, 3, 4, 5]
odd_numbers = [n for n in numbers if n % 2 != 0]
print("Odd numbers:", odd_numbers)
```

**Expected Output:**
```
Odd numbers: [1, 3, 5]
```

### Mistake 4: Confusing append() and extend()

```python
list_a = [1, 2, 3]
list_b = [1, 2, 3]

# append adds the WHOLE list as ONE item
list_a.append([4, 5])
print("append:", list_a)

# extend adds EACH item separately
list_b.extend([4, 5])
print("extend:", list_b)
```

**Expected Output:**
```
append: [1, 2, 3, [4, 5]]
extend: [1, 2, 3, 4, 5]
```

---

## Best Practices

1. **Use descriptive names.** Call your list `student_names`, not `x`.
2. **Use list comprehensions for simple transformations.** But keep them readable. If it gets too complex, use a regular for loop.
3. **Use tuples for fixed data.** If the data should not change, use a tuple.
4. **Use `in` to check membership.** Write `if "apple" in fruits` instead of looping through the list manually.
5. **Be careful with large lists.** Inserting at the beginning of a huge list is slow. Appending at the end is fast.

---

## Quick Summary

| Operation | Syntax | Example |
|-----------|--------|---------|
| Create list | `[item1, item2]` | `[1, 2, 3]` |
| Access item | `list[index]` | `fruits[0]` |
| Slice | `list[start:stop]` | `fruits[1:3]` |
| Add to end | `list.append(item)` | `fruits.append("date")` |
| Add at position | `list.insert(i, item)` | `fruits.insert(0, "fig")` |
| Remove item | `list.remove(item)` | `fruits.remove("apple")` |
| Remove by index | `list.pop(index)` | `fruits.pop(2)` |
| Sort | `list.sort()` | `numbers.sort()` |
| Length | `len(list)` | `len(fruits)` |
| Create tuple | `(item1, item2)` | `(10, 20)` |
| Unpack | `a, b = tuple` | `x, y = (3, 4)` |

---

## Key Points to Remember

1. **Lists use square brackets `[]`.** Tuples use parentheses `()`.
2. **Indexing starts at 0.** The first item is at index 0, not 1.
3. **Negative indexing counts from the end.** `-1` is the last item.
4. **Slicing uses `[start:stop]`.** The stop index is NOT included.
5. **Lists are mutable.** You can change, add, and remove items.
6. **Tuples are immutable.** Once created, they cannot be changed.
7. **List comprehensions** create lists in a short, readable way.
8. **Use `in`** to check if an item exists in a list.

---

## Practice Questions

**Question 1:** What will this code print?
```python
animals = ["cat", "dog", "bird", "fish"]
print(animals[1])
print(animals[-1])
```

<details>
<summary>Answer</summary>

```
dog
fish
```
`animals[1]` is the second item (index starts at 0). `animals[-1]` is the last item.
</details>

---

**Question 2:** What is the difference between `append()` and `extend()`?

<details>
<summary>Answer</summary>

`append()` adds one item to the end of a list. If you append a list, the entire list becomes one item.
`extend()` adds each item from another list individually.

```python
a = [1, 2]
a.append([3, 4])   # a is now [1, 2, [3, 4]]

b = [1, 2]
b.extend([3, 4])   # b is now [1, 2, 3, 4]
```
</details>

---

**Question 3:** What will this list comprehension produce?
```python
result = [x * 3 for x in range(4)]
```

<details>
<summary>Answer</summary>

```
[0, 3, 6, 9]
```
`range(4)` gives 0, 1, 2, 3. Each is multiplied by 3.
</details>

---

**Question 4:** Why would you use a tuple instead of a list?

<details>
<summary>Answer</summary>

Use a tuple when:
- The data should not change (like coordinates, RGB colors, or days of the week).
- You want to use it as a dictionary key (lists cannot be dictionary keys).
- You want slightly better performance.
</details>

---

**Question 5:** What happens if you try to change an item in a tuple?

<details>
<summary>Answer</summary>

You get a `TypeError`. Tuples are immutable, so `my_tuple[0] = "new_value"` will raise an error saying `'tuple' object does not support item assignment`.
</details>

---

## Exercises

### Exercise 1: Grade Analyzer

Write a program that:
1. Creates a list of 7 test grades.
2. Prints the highest and lowest grade.
3. Prints the average grade.
4. Creates a new list with only grades above 80.
5. Sorts the original list from highest to lowest and prints it.

<details>
<summary>Solution</summary>

```python
# Step 1: Create a list of grades
grades = [88, 72, 95, 64, 83, 91, 77]

# Step 2: Highest and lowest
print("Highest grade:", max(grades))
print("Lowest grade:", min(grades))

# Step 3: Average
average = sum(grades) / len(grades)
print(f"Average grade: {average:.1f}")

# Step 4: Grades above 80
above_80 = [g for g in grades if g > 80]
print("Grades above 80:", above_80)

# Step 5: Sort highest to lowest
grades.sort(reverse=True)
print("Sorted (high to low):", grades)
```

**Expected Output:**
```
Highest grade: 95
Lowest grade: 64
Average grade: 81.4
Grades above 80: [88, 95, 83, 91]
Sorted (high to low): [95, 91, 88, 83, 77, 72, 64]
```
</details>

---

### Exercise 2: Shopping List Manager

Write a program that starts with an empty shopping list and:
1. Adds "milk", "eggs", and "bread" to the list.
2. Inserts "butter" at the beginning.
3. Removes "eggs" from the list.
4. Prints the final list and its length.

<details>
<summary>Solution</summary>

```python
# Start with an empty list
shopping = []

# Step 1: Add items
shopping.append("milk")
shopping.append("eggs")
shopping.append("bread")
print("After adding:", shopping)

# Step 2: Insert butter at the beginning
shopping.insert(0, "butter")
print("After insert:", shopping)

# Step 3: Remove eggs
shopping.remove("eggs")
print("After remove:", shopping)

# Step 4: Print final list and length
print(f"\nFinal list: {shopping}")
print(f"Number of items: {len(shopping)}")
```

**Expected Output:**
```
After adding: ['milk', 'eggs', 'bread']
After insert: ['butter', 'milk', 'eggs', 'bread']
After remove: ['butter', 'milk', 'bread']

Final list: ['butter', 'milk', 'bread']
Number of items: 3
```
</details>

---

### Exercise 3: Coordinate Tracker

Create a program that:
1. Stores 3 coordinates as tuples: (1, 2), (4, 6), (7, 8).
2. Uses tuple unpacking to print each x and y value separately.
3. Calculates the distance from the origin (0, 0) for each point using the formula: distance = (x**2 + y**2) ** 0.5

<details>
<summary>Solution</summary>

```python
# Step 1: Store coordinates as tuples in a list
points = [(1, 2), (4, 6), (7, 8)]

# Step 2 and 3: Unpack and calculate distance
for point in points:
    x, y = point  # Tuple unpacking
    distance = (x**2 + y**2) ** 0.5
    print(f"Point ({x}, {y}) -> Distance from origin: {distance:.2f}")
```

**Expected Output:**
```
Point (1, 2) -> Distance from origin: 2.24
Point (4, 6) -> Distance from origin: 7.21
Point (7, 8) -> Distance from origin: 10.63
```
</details>

---

## What Is Next?

Now that you can store collections of items in lists and tuples, you are ready to learn about **dictionaries and sets** in Chapter 7. Dictionaries let you store data in **key-value pairs** — like a phone book where each name has a number. Sets store only **unique items** — no duplicates allowed. These tools will make your data handling even more powerful.
