# Chapter 5: Loops — Repeating Things Automatically

---

## What You Will Learn

- What loops are and why they save you from writing the same code over and over
- How to use `for` loops to go through a list of items
- How to use `range()` to repeat something a specific number of times
- How to use `while` loops for repeating until a condition is false
- How to control loops with `break` and `continue`
- How to use nested loops (a loop inside a loop)
- Common loop patterns used in data science and AI

---

## Why This Chapter Matters

Imagine you have a list of 1,000 exam scores and you need to find the average. Without loops, you would need to write 1,000 lines of code — one for each score. With a loop, you write 3 lines and let the computer do the repetitive work.

In AI and machine learning, loops are everywhere. Training a model means repeating the learning process thousands of times. Processing a dataset means going through every row. Loops are how computers handle repetition, and repetition is what makes AI possible.

---

## The for Loop — Going Through Items One by One

A `for` loop takes a collection of items and does something with each item, one at a time. Think of it like a teacher calling attendance — they go through the list of names one by one.

```python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)
```

**What you see:**
```
apple
banana
cherry
```

**How it works, line by line:**

```
Line 1: fruits = ["apple", "banana", "cherry"]
         We create a list with three items.

Line 3: for fruit in fruits:
         This says: "Take each item from the list, one at a time,
         and temporarily call it 'fruit'."

         Round 1: fruit = "apple"
         Round 2: fruit = "banana"
         Round 3: fruit = "cherry"

Line 4:     print(fruit)
             This runs for EACH round. It prints the current fruit.
```

```
How a for Loop Works:
+------------------------------------------------------------------+
|                                                                   |
|  fruits = ["apple", "banana", "cherry"]                           |
|                                                                   |
|  Round 1:  fruit = "apple"   --> print("apple")                  |
|  Round 2:  fruit = "banana"  --> print("banana")                 |
|  Round 3:  fruit = "cherry"  --> print("cherry")                 |
|  Done!     No more items.    --> Loop ends.                       |
|                                                                   |
+------------------------------------------------------------------+
```

### Looping Through Numbers

```python
scores = [85, 92, 78, 95, 88]

total = 0
for score in scores:
    total = total + score

average = total / len(scores)
print("Average score:", average)
```

**What you see:**
```
Average score: 87.6
```

This is exactly the kind of thing you do in data science — go through a list of numbers and calculate something.

### Looping Through Strings

A string is just a sequence of characters. You can loop through each letter:

```python
word = "AI"

for letter in word:
    print(letter)
```

**What you see:**
```
A
I
```

---

## range() — Repeating a Specific Number of Times

Sometimes you do not have a list. You just want to repeat something 5 times, or 100 times. That is what `range()` does.

```python
for i in range(5):
    print("Hello!", i)
```

**What you see:**
```
Hello! 0
Hello! 1
Hello! 2
Hello! 3
Hello! 4
```

**Important:** `range(5)` gives you the numbers 0, 1, 2, 3, 4. It starts at 0 and stops **before** 5. This is a common source of confusion for beginners.

```
range() Explained:
+------------------------------------------------------------------+
|                                                                   |
|  range(5)        --> 0, 1, 2, 3, 4       (5 numbers, start at 0) |
|  range(1, 6)     --> 1, 2, 3, 4, 5       (start at 1, stop at 6) |
|  range(0, 10, 2) --> 0, 2, 4, 6, 8       (step by 2)             |
|  range(10, 0, -1)--> 10, 9, 8, ... 1     (count backwards)       |
|                                                                   |
|  range(start, stop, step)                                         |
|  - start: where to begin (default 0)                              |
|  - stop:  where to end (NOT included)                             |
|  - step:  how much to skip (default 1)                            |
+------------------------------------------------------------------+
```

### range() with Start and Stop

```python
# Print numbers from 1 to 5
for i in range(1, 6):
    print(i)
```

**What you see:**
```
1
2
3
4
5
```

### range() with Step

```python
# Count by 2s
for i in range(0, 10, 2):
    print(i, end=" ")
```

**What you see:**
```
0 2 4 6 8
```

### Using range() to Access List Items by Position

```python
colors = ["red", "green", "blue"]

for i in range(len(colors)):
    print(f"Color {i}: {colors[i]}")
```

**What you see:**
```
Color 0: red
Color 1: green
Color 2: blue
```

**Tip:** In most cases, looping directly (`for color in colors`) is cleaner than using `range(len(...))`. Use `range` when you need the index number.

### enumerate() — The Best of Both Worlds

If you need both the item AND its position, use `enumerate()`:

```python
colors = ["red", "green", "blue"]

for index, color in enumerate(colors):
    print(f"Color {index}: {color}")
```

**What you see:**
```
Color 0: red
Color 1: green
Color 2: blue
```

This is cleaner and more Pythonic. You will see `enumerate()` a lot in real Python code.

---

## The while Loop — Repeat Until a Condition Is False

A `for` loop goes through a fixed collection. A `while` loop keeps going as long as a condition is true. Think of it like this: "Keep stirring the soup **while** it is not boiling."

```python
count = 0

while count < 5:
    print("Count is:", count)
    count = count + 1

print("Done!")
```

**What you see:**
```
Count is: 0
Count is: 1
Count is: 2
Count is: 3
Count is: 4
Done!
```

```
How a while Loop Works:
+------------------------------------------------------------------+
|                                                                   |
|  count = 0                                                        |
|                                                                   |
|  Check: Is count < 5?  (0 < 5 = True)  --> Run the body          |
|    print("Count is:", 0)                                          |
|    count = 1                                                      |
|                                                                   |
|  Check: Is count < 5?  (1 < 5 = True)  --> Run the body          |
|    print("Count is:", 1)                                          |
|    count = 2                                                      |
|                                                                   |
|  ... (same for 2, 3, 4) ...                                      |
|                                                                   |
|  Check: Is count < 5?  (5 < 5 = False) --> STOP! Exit the loop.  |
|  print("Done!")                                                   |
+------------------------------------------------------------------+
```

### When to Use while vs for

```
Choosing the Right Loop:
+------------------------------------------------------------------+
|                                                                   |
|  Use FOR when:                     Use WHILE when:                |
|  - You know how many times         - You do not know how many     |
|    to repeat                         times to repeat              |
|  - You are going through a list    - You repeat until something   |
|  - You are using range()             specific happens             |
|                                                                   |
|  Examples:                          Examples:                      |
|  - Process each student score      - Ask for input until valid    |
|  - Train for 100 epochs            - Search until found           |
|  - Loop through each pixel         - Keep guessing until correct  |
+------------------------------------------------------------------+
```

### User Input Example with while

```python
password = ""

while password != "python123":
    password = input("Enter the password: ")

print("Access granted!")
```

This keeps asking until the user types the correct password. We do not know in advance how many tries it will take — that is why `while` is the right choice.

---

## Controlling Loops: break and continue

### break — Stop the Loop Early

`break` immediately exits the loop, no matter what.

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

for num in numbers:
    if num == 6:
        print("Found 6! Stopping.")
        break
    print(num)
```

**What you see:**
```
1
2
3
4
5
Found 6! Stopping.
```

The loop stopped at 6 and did not continue to 7, 8, 9, 10.

### continue — Skip This Round

`continue` skips the rest of the current round and moves to the next item.

```python
numbers = [1, 2, 3, 4, 5]

for num in numbers:
    if num == 3:
        continue    # Skip 3
    print(num)
```

**What you see:**
```
1
2
4
5
```

The number 3 was skipped, but the loop kept going.

```
break vs continue:
+------------------------------------------------------------------+
|                                                                   |
|  break:    "Stop the entire loop right now!"                      |
|            Like walking out of a movie theater.                   |
|                                                                   |
|  continue: "Skip this one and go to the next."                   |
|            Like skipping a song on a playlist.                    |
+------------------------------------------------------------------+
```

---

## Nested Loops — A Loop Inside a Loop

You can put one loop inside another. The inner loop runs completely for each round of the outer loop.

```python
for i in range(3):
    for j in range(3):
        print(f"({i}, {j})", end="  ")
    print()   # New line after each row
```

**What you see:**
```
(0, 0)  (0, 1)  (0, 2)
(1, 0)  (1, 1)  (1, 2)
(2, 0)  (2, 1)  (2, 2)
```

```
How Nested Loops Work:
+------------------------------------------------------------------+
|                                                                   |
|  Outer loop: i = 0                                                |
|    Inner loop: j = 0 --> (0,0)                                    |
|    Inner loop: j = 1 --> (0,1)                                    |
|    Inner loop: j = 2 --> (0,2)                                    |
|                                                                   |
|  Outer loop: i = 1                                                |
|    Inner loop: j = 0 --> (1,0)                                    |
|    Inner loop: j = 1 --> (1,1)                                    |
|    Inner loop: j = 2 --> (1,2)                                    |
|                                                                   |
|  Outer loop: i = 2                                                |
|    Inner loop: j = 0 --> (2,0)                                    |
|    Inner loop: j = 1 --> (2,1)                                    |
|    Inner loop: j = 2 --> (2,2)                                    |
|                                                                   |
|  Total rounds: 3 x 3 = 9                                         |
+------------------------------------------------------------------+
```

### Multiplication Table

```python
for i in range(1, 6):
    for j in range(1, 6):
        print(f"{i * j:4}", end="")
    print()
```

**What you see:**
```
   1   2   3   4   5
   2   4   6   8  10
   3   6   9  12  15
   4   8  12  16  20
   5  10  15  20  25
```

### Why Nested Loops Matter for AI

In machine learning:
- Nested loops process 2D data (like pixels in an image — rows and columns)
- Matrix multiplication uses nested loops
- Grid search for hyperparameters uses nested loops

---

## Useful Loop Patterns

### Pattern 1: Accumulating a Total

```python
prices = [10.99, 24.50, 3.75, 15.00]

total = 0
for price in prices:
    total += price     # Same as: total = total + price

print(f"Total: ${total:.2f}")
```

**What you see:**
```
Total: $54.24
```

### Pattern 2: Counting Items That Match

```python
scores = [85, 42, 91, 67, 73, 95, 55, 88]

passing = 0
for score in scores:
    if score >= 70:
        passing += 1

print(f"{passing} students passed out of {len(scores)}")
```

**What you see:**
```
5 students passed out of 8
```

### Pattern 3: Finding the Maximum

```python
temperatures = [72, 85, 68, 91, 77, 83]

highest = temperatures[0]    # Start with the first value
for temp in temperatures:
    if temp > highest:
        highest = temp

print("Highest temperature:", highest)
```

**What you see:**
```
Highest temperature: 91
```

### Pattern 4: Building a New List

```python
numbers = [1, 2, 3, 4, 5]
squares = []

for num in numbers:
    squares.append(num ** 2)

print(squares)
```

**What you see:**
```
[1, 4, 9, 16, 25]
```

### Pattern 5: List Comprehension (The Python Shortcut)

Python has a special shortcut for building a new list from an existing one:

```python
numbers = [1, 2, 3, 4, 5]
squares = [num ** 2 for num in numbers]
print(squares)
```

**What you see:**
```
[1, 4, 9, 16, 25]
```

This does exactly the same thing as Pattern 4, but in one line. List comprehensions are very common in Python and especially in data science code.

```python
# Filter with list comprehension
scores = [85, 42, 91, 67, 73, 95, 55, 88]
passing_scores = [s for s in scores if s >= 70]
print(passing_scores)
```

**What you see:**
```
[85, 91, 73, 95, 88]
```

```
List Comprehension Structure:
+------------------------------------------------------------------+
|                                                                   |
|  [expression for item in collection]                              |
|                                                                   |
|  [expression for item in collection if condition]                 |
|                                                                   |
|  Examples:                                                        |
|  [x * 2 for x in range(5)]        --> [0, 2, 4, 6, 8]           |
|  [x for x in range(10) if x > 5]  --> [6, 7, 8, 9]              |
|  [name.upper() for name in names]  --> ["ALICE", "BOB", ...]     |
+------------------------------------------------------------------+
```

---

## Infinite Loops and How to Avoid Them

A `while` loop that never becomes `False` runs forever. This is called an infinite loop.

```python
# DANGER: This never stops!
# count = 0
# while count < 5:
#     print(count)
#     # Forgot to add: count = count + 1
```

The fix is to always make sure the condition will eventually become `False`:

```python
# SAFE: count increases each round
count = 0
while count < 5:
    print(count)
    count += 1    # This line makes the loop eventually stop
```

**Tip:** If your program seems frozen, it is probably stuck in an infinite loop. Press `Ctrl + C` in the terminal to stop it.

---

## AI Connection: Training Loops

In machine learning, training a model uses a loop. Here is a simplified preview of what you will see in Book 2:

```python
# Simplified training loop (preview)
learning_rate = 0.01
weight = 0.0

for epoch in range(100):
    prediction = weight * 2     # Predict using current weight
    error = 5.0 - prediction    # How far off are we?
    weight = weight + learning_rate * error   # Adjust weight

    if epoch % 20 == 0:    # Print every 20th round
        print(f"Epoch {epoch}: weight = {weight:.4f}, error = {error:.4f}")

print(f"\nFinal weight: {weight:.4f}")
print(f"Prediction for input 2: {weight * 2:.4f} (should be close to 5.0)")
```

**What you see:**
```
Epoch 0: weight = 0.0500, error = 5.0000
Epoch 20: weight = 1.7462, error = 1.5075
Epoch 40: weight = 2.2654, error = 0.4692
Epoch 60: weight = 2.4241, error = 0.1518
Epoch 80: weight = 2.4754, error = 0.0492
Final weight: 2.4920
Prediction for input 2: 4.9840 (should be close to 5.0)
```

The loop repeats the learning process 100 times. Each time, the weight gets a little closer to the right answer. This is exactly how neural networks learn — through repeated loops!

---

## Common Mistakes

1. **Off-by-one with range()**: `range(5)` gives 0 to 4, not 1 to 5. If you want 1 to 5, use `range(1, 6)`.

2. **Forgetting to update the counter in while loops**: If you forget `count += 1`, the loop runs forever. Always check that your while condition will eventually become False.

3. **Modifying a list while looping through it**: This causes skipped items or errors. Create a new list instead, or loop through a copy.

4. **Using the wrong loop type**: If you know the number of repetitions, use `for`. If you are waiting for a condition, use `while`.

---

## Best Practices

1. **Prefer for loops over while loops** when you know the number of iterations. They are safer (no risk of infinite loops) and cleaner.

2. **Use meaningful variable names** in loops: `for student in students` is better than `for x in students`.

3. **Use enumerate() when you need both index and value** — it is cleaner than `range(len(...))`.

4. **Use list comprehensions for simple transformations** — they are shorter and faster than building a list with a for loop.

5. **Avoid deeply nested loops (3+ levels)** — they are hard to read and often slow. Look for ways to simplify.

---

## Quick Summary

| Concept | What It Does | Example |
|---------|-------------|---------|
| `for` loop | Goes through each item in a collection | `for x in [1,2,3]:` |
| `range()` | Generates a sequence of numbers | `range(5)` gives 0,1,2,3,4 |
| `while` loop | Repeats while a condition is True | `while x < 10:` |
| `break` | Stops the loop immediately | Exit early when found |
| `continue` | Skips the current round | Skip invalid items |
| `enumerate()` | Gives index and value together | `for i, x in enumerate(list):` |
| List comprehension | Build a list in one line | `[x*2 for x in range(5)]` |

---

## Key Points to Remember

- A **for loop** goes through a collection item by item. Use it when you know what you are looping through.
- **range(n)** gives numbers from 0 to n-1. Use `range(start, stop, step)` for more control.
- A **while loop** keeps running as long as its condition is True. Always make sure the condition eventually becomes False.
- **break** stops the entire loop. **continue** skips the current round.
- **Nested loops** run the inner loop completely for each round of the outer loop.
- **List comprehensions** are a Pythonic shortcut for building new lists.
- **enumerate()** gives you both the position and the value — use it instead of `range(len(...))`.
- In AI, **training loops** repeat the learning process thousands of times to improve the model.

---

## Practice Questions

**Q1: What numbers does `range(2, 8)` produce?**

2, 3, 4, 5, 6, 7. It starts at 2 and stops before 8.

**Q2: What is the difference between `break` and `continue`?**

`break` exits the entire loop immediately. `continue` skips the rest of the current round and moves to the next item. Think of break as leaving a theater, and continue as skipping a song.

**Q3: When should you use a `while` loop instead of a `for` loop?**

Use `while` when you do not know in advance how many times the loop will run — for example, asking for input until the user types "quit", or searching until something is found.

**Q4: What does this list comprehension produce?**
```python
[x * 3 for x in range(4)]
```

`[0, 3, 6, 9]`. It multiplies each number (0, 1, 2, 3) by 3.

**Q5: What is an infinite loop and how do you prevent it?**

An infinite loop is a `while` loop whose condition never becomes False, so it runs forever. Prevent it by making sure the condition changes inside the loop (like incrementing a counter). If stuck, press Ctrl+C to stop it.

---

## Exercises

**Exercise 1: Sum of Even Numbers**
Write a program that uses a loop to find the sum of all even numbers from 1 to 100. Print the result. (Hint: use `range(2, 101, 2)` or check with `if num % 2 == 0`)

**Exercise 2: Fizz Buzz**
Write a loop that prints numbers from 1 to 30. But:
- If the number is divisible by 3, print "Fizz" instead
- If the number is divisible by 5, print "Buzz" instead
- If divisible by both 3 and 5, print "FizzBuzz"

**Exercise 3: Word Counter**
Given a list of words, use a loop to count how many words have more than 5 letters:
```python
words = ["hello", "programming", "AI", "machine", "cat", "learning", "go"]
```

---

## What Is Next?

In the next chapter, we will learn about **Lists and Tuples** in more detail — Python's most important data structures for organizing collections of data. You will learn how to slice lists, sort them, search through them, and use tuple unpacking. These are the building blocks for handling datasets in data science and AI.
