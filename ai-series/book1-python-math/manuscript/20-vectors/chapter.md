# Chapter 20: Vectors — The Building Blocks of Machine Learning

## What You Will Learn

In this chapter, you will learn how to:

- Understand what a vector is (a list of numbers with direction)
- Create vectors using NumPy
- Add and subtract vectors (the walking analogy)
- Multiply vectors by scalars
- Calculate the dot product (a similarity measure — KEY in ML)
- Find the magnitude (length) of a vector
- Understand unit vectors
- Calculate the distance between vectors (Euclidean distance)
- Understand why vectors matter in ML (features are vectors!)
- Visualize 2D vectors with Matplotlib

## Why This Chapter Matters

In machine learning, everything is a vector.

- A photo? It is a vector of pixel values.
- A sentence? It is a vector of word embeddings.
- A patient's medical record? It is a vector of measurements.
- A house listing? It is a vector of features (size, bedrooms, price).

When you hear "the model processes the input," what it really means is "the model does math on vectors." Understanding vectors is not optional in ML. It is fundamental.

```
+--------------------------------------------------+
|  Everything Is a Vector                           |
+--------------------------------------------------+
|                                                   |
|  A patient:  [age, weight, blood_pressure, ...]   |
|              [35,  70,     120,            ...]   |
|              That is a vector!                    |
|                                                   |
|  A house:    [sqft, bedrooms, bathrooms, price]   |
|              [1500, 3,        2,         300000]  |
|              That is a vector!                    |
|                                                   |
|  A word:     [0.2, -0.5, 0.8, 0.1, ...]          |
|              That is a vector! (word embedding)   |
|                                                   |
+--------------------------------------------------+
```

---

## 20.1 What Is a Vector?

A **vector** is a list of numbers. That is it. At its simplest, a vector is just an ordered collection of numbers.

But vectors also have a geometric meaning: they represent both a **direction** and a **magnitude** (length).

**Real-life analogy:** Think of GPS directions. "Go 3 miles east and 4 miles north" is a vector: [3, 4]. The numbers tell you both the direction (northeast) and the distance (5 miles total, by the Pythagorean theorem).

```
A 2D vector [3, 4]:

  y
  5 |          * (3, 4)
  4 |        / |
  3 |      /   |
  2 |    /     |     The arrow is the vector.
  1 |  /       |     Direction: northeast
  0 +--+--+--+-+--  Length: 5
     0  1  2  3  x
```

### Scalar vs Vector

```
Scalar:  a single number           5
         (just a magnitude)        "How much?"

Vector:  a list of numbers         [3, 4]
         (direction + magnitude)   "How much AND which way?"
```

### Dimensions

The number of elements in a vector is its **dimension**.

```
1D vector:   [5]              one number
2D vector:   [3, 4]           two numbers (x, y)
3D vector:   [1, 2, 3]        three numbers (x, y, z)
nD vector:   [a, b, c, ...]   n numbers (common in ML)
```

In machine learning, vectors often have hundreds or thousands of dimensions. A 768-dimensional vector is normal when working with language models.

---

## 20.2 Creating Vectors with NumPy

In Python, we use NumPy arrays to represent vectors.

```python
import numpy as np

# Create a vector
v = np.array([3, 4])
print(f"Vector: {v}")
print(f"Dimensions: {v.shape}")
print(f"Number of elements: {len(v)}")
```

**Expected Output:**

```
Vector: [3 4]
Dimensions: (2,)
Number of elements: 2
```

### Different Ways to Create Vectors

```python
import numpy as np

# From a list
v1 = np.array([1, 2, 3])
print(f"From list: {v1}")

# All zeros
v2 = np.zeros(5)
print(f"Zeros: {v2}")

# All ones
v3 = np.ones(4)
print(f"Ones: {v3}")

# Range of numbers
v4 = np.arange(0, 10, 2)
print(f"Range: {v4}")

# Random values
v5 = np.random.rand(3)
print(f"Random: {v5}")
```

**Expected Output:**

```
From list: [1 2 3]
Zeros: [0. 0. 0. 0. 0.]
Ones: [1. 1. 1. 1.]
Range: [0 2 4 6 8]
Random: [0.5488 0.7152 0.6028]
```

(Random values will differ each time.)

---

## 20.3 Vector Addition and Subtraction

Adding two vectors means adding their corresponding elements. Subtracting works the same way.

**Real-life analogy — the walking analogy:** Imagine you walk 3 blocks east and 1 block north (vector [3, 1]). Then you walk 1 block east and 2 blocks north (vector [1, 2]). Your total displacement is [3+1, 1+2] = [4, 3]. You ended up 4 blocks east and 3 blocks north.

```
Vector addition:

  [3, 1] + [1, 2] = [3+1, 1+2] = [4, 3]

  Walk 1:  [3, 1]        Walk 2: [1, 2]       Total: [4, 3]

      N                      N                      N
   1  |  *               2  |     *              3  |        *
      |  /                  |    /                  |       /
      +--->  E               +-->  E                +---->  E
         3                    1                        4
```

```python
import numpy as np

a = np.array([3, 1])
b = np.array([1, 2])

# Addition
result_add = a + b
print(f"a + b = {result_add}")

# Subtraction
result_sub = a - b
print(f"a - b = {result_sub}")
```

**Expected Output:**

```
a + b = [4 3]
a - b = [2 -1]
```

**Line-by-line explanation:**

```python
result_add = a + b
```

NumPy adds corresponding elements: `[3+1, 1+2]` = `[4, 3]`. This is called **element-wise** addition.

```python
result_sub = a - b
```

Similarly: `[3-1, 1-2]` = `[2, -1]`.

### Rules for Vector Addition

Both vectors must have the same number of elements.

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5])

# This will cause an error!
try:
    result = a + b
except ValueError as e:
    print(f"Error: {e}")
```

**Expected Output:**

```
Error: operands could not be broadcast together with shapes (3,) (2,)
```

---

## 20.4 Scalar Multiplication

Multiplying a vector by a **scalar** (a single number) multiplies every element by that number.

**Real-life analogy:** If your recipe serves 2 people and you need to serve 6, you multiply everything by 3. Ingredients [flour=200g, sugar=100g, eggs=2] become [600g, 300g, 6].

```
Scalar multiplication:

  3 * [2, 4, 1] = [3*2, 3*4, 3*1] = [6, 12, 3]

  Original vector:     Scaled by 3:
       *                     *
      /                     /
     * (2,4)               * (6,12)
    /                     /
   *                     *
  Same direction, 3x longer
```

```python
import numpy as np

v = np.array([2, 4, 1])
scalar = 3

result = scalar * v
print(f"3 * [2, 4, 1] = {result}")

# Negative scalar reverses direction
result_neg = -1 * v
print(f"-1 * [2, 4, 1] = {result_neg}")

# Fractional scalar shrinks the vector
result_half = 0.5 * v
print(f"0.5 * [2, 4, 1] = {result_half}")
```

**Expected Output:**

```
3 * [2, 4, 1] = [ 6 12  3]
-1 * [2, 4, 1] = [-2 -4 -1]
0.5 * [2, 4, 1] = [1.  2.  0.5]
```

### What Scalar Multiplication Does

```
scalar > 1:     stretches the vector (makes it longer)
scalar = 1:     no change
0 < scalar < 1: shrinks the vector (makes it shorter)
scalar = 0:     zero vector (no direction, no length)
scalar < 0:     reverses direction AND scales
```

---

## 20.5 Dot Product — The Similarity Measure

The **dot product** is one of the most important operations in machine learning. It multiplies corresponding elements and adds the results.

```
Dot product of [a1, a2, a3] and [b1, b2, b3]:

  a . b = a1*b1 + a2*b2 + a3*b3
```

**Real-life analogy:** Imagine you are shopping. Your cart has [2 apples, 3 bananas, 1 orange]. Prices are [$1, $0.50, $2]. The dot product gives you the total cost:

```
quantities = [2,    3,     1]
prices     = [$1,   $0.50, $2]

total = 2*1 + 3*0.50 + 1*2 = 2 + 1.50 + 2 = $5.50
```

That total is the dot product!

```python
import numpy as np

quantities = np.array([2, 3, 1])
prices = np.array([1.00, 0.50, 2.00])

# Dot product
total = np.dot(quantities, prices)
print(f"Total cost: ${total:.2f}")

# Alternative syntax
total2 = quantities @ prices    # The @ operator
print(f"Total cost: ${total2:.2f}")
```

**Expected Output:**

```
Total cost: $5.50
Total cost: $5.50
```

**Line-by-line explanation:**

```python
total = np.dot(quantities, prices)
```

`np.dot()` multiplies corresponding elements and sums: `2*1 + 3*0.5 + 1*2 = 5.5`.

```python
total2 = quantities @ prices
```

The `@` operator is Python's shorthand for the dot product. Same result, cleaner syntax.

### Dot Product as Similarity

Here is why the dot product is KEY in ML: it measures **how similar two vectors are**.

```
Similar vectors      -->  large positive dot product
Opposite vectors     -->  large negative dot product
Perpendicular vectors --> dot product = 0 (unrelated)

   Similar:          Opposite:         Perpendicular:
      / /              /  \              /
     / /              /    \            |
    / /              /      \           |
   Large positive    Large negative     Zero
```

```python
import numpy as np

# Two similar vectors (pointing roughly the same way)
a = np.array([1, 2, 3])
b = np.array([2, 3, 4])
print(f"Similar vectors:  dot = {np.dot(a, b)}")

# Two opposite vectors
c = np.array([1, 2, 3])
d = np.array([-1, -2, -3])
print(f"Opposite vectors: dot = {np.dot(c, d)}")

# Two perpendicular vectors (at right angles)
e = np.array([1, 0])
f = np.array([0, 1])
print(f"Perpendicular:    dot = {np.dot(e, f)}")
```

**Expected Output:**

```
Similar vectors:  dot = 20
Opposite vectors: dot = -14
Perpendicular:    dot = 0
```

### Why the Dot Product Is KEY in ML

The dot product is everywhere in machine learning:

```
+--------------------------------------------------+
|  Where dot products appear in ML:                 |
+--------------------------------------------------+
|                                                   |
|  Linear regression:   prediction = w . x + b      |
|     "The prediction is the dot product of         |
|      weights and features, plus bias"             |
|                                                   |
|  Neural networks:     z = w . x + b               |
|     "Each neuron computes a dot product"          |
|                                                   |
|  Similarity search:   sim = a . b                 |
|     "How similar are two items?"                  |
|                                                   |
|  Attention mechanism: score = q . k               |
|     "How much should we pay attention?"           |
|                                                   |
+--------------------------------------------------+
```

```python
import numpy as np

# A simple "neuron" is just a dot product + bias
features = np.array([0.5, 0.8, 0.2])    # input features
weights = np.array([0.4, 0.6, 0.3])     # learned weights
bias = 0.1                               # learned bias

# This IS what a neuron does
output = np.dot(features, weights) + bias
print(f"Neuron output: {output}")
print(f"Breakdown: {0.5*0.4} + {0.8*0.6} + {0.2*0.3} + {bias} = {output}")
```

**Expected Output:**

```
Neuron output: 0.84
Breakdown: 0.2 + 0.48 + 0.06 + 0.1 = 0.84
```

---

## 20.6 Vector Norm / Magnitude (Length)

The **magnitude** (or **norm**) of a vector is its length. Think of it as "how long is the arrow?"

For a 2D vector [x, y], the magnitude is calculated using the Pythagorean theorem:

```
||v|| = sqrt(x^2 + y^2)

For vector [3, 4]:
||v|| = sqrt(3^2 + 4^2) = sqrt(9 + 16) = sqrt(25) = 5
```

**Real-life analogy:** If you walk 3 blocks east and 4 blocks north, how far are you from where you started? The answer is 5 blocks (as the crow flies). This is the magnitude of the vector [3, 4].

```
     4 |     * (3, 4)
       |    /|
       |   / |
  5    |  /  | 4
       | /   |
       |/    |
       +-----+---
         3

  3^2 + 4^2 = 9 + 16 = 25
  sqrt(25) = 5
```

```python
import numpy as np

v = np.array([3, 4])

# Calculate magnitude
magnitude = np.linalg.norm(v)
print(f"Vector: {v}")
print(f"Magnitude: {magnitude}")

# Manual calculation
manual = np.sqrt(3**2 + 4**2)
print(f"Manual: {manual}")
```

**Expected Output:**

```
Vector: [3 4]
Magnitude: 5.0
Manual: 5.0
```

**Line-by-line explanation:**

```python
magnitude = np.linalg.norm(v)
```

`np.linalg.norm()` calculates the Euclidean norm (the most common type of length). For a vector with n elements, it computes: sqrt(v1^2 + v2^2 + ... + vn^2).

### Higher-Dimensional Vectors

The formula extends naturally to any number of dimensions:

```python
import numpy as np

# 3D vector
v3d = np.array([1, 2, 3])
print(f"3D magnitude: {np.linalg.norm(v3d):.4f}")
# sqrt(1 + 4 + 9) = sqrt(14) = 3.7417

# 5D vector
v5d = np.array([1, 2, 3, 4, 5])
print(f"5D magnitude: {np.linalg.norm(v5d):.4f}")
# sqrt(1 + 4 + 9 + 16 + 25) = sqrt(55) = 7.4162
```

**Expected Output:**

```
3D magnitude: 3.7417
5D magnitude: 7.4162
```

---

## 20.7 Unit Vectors

A **unit vector** is a vector with a magnitude of exactly 1. It keeps the direction but normalizes the length.

**Real-life analogy:** A compass needle points north. It does not tell you how far north to go — just the direction. A unit vector is like that compass needle: pure direction, standardized length.

To create a unit vector, divide the vector by its magnitude:

```
unit vector = v / ||v||

For v = [3, 4]:
||v|| = 5
unit = [3/5, 4/5] = [0.6, 0.8]

Check: sqrt(0.6^2 + 0.8^2) = sqrt(0.36 + 0.64) = sqrt(1.0) = 1
```

```python
import numpy as np

v = np.array([3, 4])

# Calculate unit vector
magnitude = np.linalg.norm(v)
unit = v / magnitude

print(f"Original vector: {v}")
print(f"Magnitude: {magnitude}")
print(f"Unit vector: {unit}")
print(f"Unit vector magnitude: {np.linalg.norm(unit)}")
```

**Expected Output:**

```
Original vector: [3 4]
Magnitude: 5.0
Unit vector: [0.6 0.8]
Unit vector magnitude: 1.0
```

### Why Unit Vectors Matter in ML

**Normalization** is a critical preprocessing step in ML. When you normalize vectors (convert them to unit vectors), you remove the effect of magnitude and focus on direction.

This is important because:

```
Without normalization:           With normalization:

Person A: [1000, 50]             Person A: [0.999, 0.050]
  (income=$1000, age=50)          (mostly about income)

Person B: [100000, 25]           Person B: [1.000, 0.000]
  (income=$100000, age=25)        (almost entirely income)

The large income numbers         Now income and age are
dominate the calculation.         on comparable scales.
```

```python
import numpy as np

# Feature vectors (income, age)
person_a = np.array([1000, 50])
person_b = np.array([100000, 25])

# Normalize both
unit_a = person_a / np.linalg.norm(person_a)
unit_b = person_b / np.linalg.norm(person_b)

print(f"Original A: {person_a}")
print(f"Unit A:     {unit_a}")
print(f"\nOriginal B: {person_b}")
print(f"Unit B:     {unit_b}")
```

**Expected Output:**

```
Original A: [1000   50]
Unit A:     [0.99875156 0.04993758]

Original B: [100000     25]
Unit B:     [1.00000000e+00 2.50000002e-04]
```

---

## 20.8 Distance Between Vectors (Euclidean Distance)

The **Euclidean distance** between two vectors tells you how far apart they are. It is the most common distance measure in ML.

```
Distance between a and b:

  d = ||a - b|| = sqrt((a1-b1)^2 + (a2-b2)^2 + ...)

  It is just the magnitude of the difference vector!
```

**Real-life analogy:** Two cities on a map. City A is at coordinates (2, 3). City B is at (5, 7). The straight-line distance is sqrt((5-2)^2 + (7-3)^2) = sqrt(9 + 16) = 5.

```
   7 |           B
     |         / |
     |       /   |
     |     /     | 4
   3 | A /       |
     |   3       |
     +---+---+---+---
         2       5

  Distance = sqrt(3^2 + 4^2) = 5
```

```python
import numpy as np

a = np.array([2, 3])
b = np.array([5, 7])

# Method 1: Manual calculation
distance = np.sqrt(np.sum((a - b) ** 2))
print(f"Distance (manual): {distance}")

# Method 2: Using np.linalg.norm
distance2 = np.linalg.norm(a - b)
print(f"Distance (norm): {distance2}")
```

**Expected Output:**

```
Distance (manual): 5.0
Distance (norm): 5.0
```

**Line-by-line explanation:**

```python
distance = np.sqrt(np.sum((a - b) ** 2))
```

Step by step:
1. `a - b` = `[2-5, 3-7]` = `[-3, -4]` (difference vector)
2. `** 2` = `[9, 16]` (square each element)
3. `np.sum()` = `25` (sum them up)
4. `np.sqrt()` = `5.0` (take the square root)

### Distance in ML: Finding Similar Items

In ML, items that are "close" (small distance) are considered similar.

```python
import numpy as np

# Movie ratings for three users [action, comedy, drama, horror]
alice =  np.array([5, 3, 4, 1])
bob =    np.array([4, 4, 5, 1])
charlie = np.array([1, 1, 2, 5])

# Calculate distances
dist_ab = np.linalg.norm(alice - bob)
dist_ac = np.linalg.norm(alice - charlie)
dist_bc = np.linalg.norm(bob - charlie)

print(f"Distance Alice-Bob:     {dist_ab:.2f}")
print(f"Distance Alice-Charlie: {dist_ac:.2f}")
print(f"Distance Bob-Charlie:   {dist_bc:.2f}")

# Find who is most similar to Alice
if dist_ab < dist_ac:
    print("\nAlice is most similar to Bob")
else:
    print("\nAlice is most similar to Charlie")
```

**Expected Output:**

```
Distance Alice-Bob:     1.73
Distance Alice-Charlie: 5.74
Distance Bob-Charlie:   6.08

Alice is most similar to Bob
```

Alice and Bob have similar tastes (small distance). Charlie likes very different movies (large distance). This is how recommendation systems work.

---

## 20.9 Why Vectors Matter in ML — Features Are Vectors

In machine learning, each data point is represented as a vector of **features**. A feature is a measurable property.

```
+--------------------------------------------------+
|  Real-World Data as Vectors                       |
+--------------------------------------------------+
|                                                   |
|  Predicting house prices:                         |
|  Features: [sqft, bedrooms, bathrooms, age]       |
|  House 1:  [1500, 3, 2, 10]   <-- this is a     |
|  House 2:  [2000, 4, 3, 5]        vector!        |
|  House 3:  [800,  1, 1, 50]                      |
|                                                   |
|  Email spam detection:                            |
|  Features: [word_count, has_link, caps_ratio]     |
|  Email 1:  [50, 0, 0.02]    <-- not spam         |
|  Email 2:  [10, 1, 0.80]    <-- spam             |
|                                                   |
|  Image recognition (simplified):                  |
|  Features: [pixel_1, pixel_2, ..., pixel_784]     |
|  Image:    [0, 0, 128, 255, 200, ...]             |
|            (each pixel value is a feature)        |
|                                                   |
+--------------------------------------------------+
```

### A Complete ML Example with Vectors

```python
import numpy as np

# Three houses: [sqft, bedrooms, distance_to_school_miles]
house_a = np.array([1500, 3, 0.5])
house_b = np.array([1600, 3, 0.4])
house_c = np.array([3000, 5, 2.0])

# A buyer wants: [1550, 3, 0.5]
buyer_wants = np.array([1550, 3, 0.5])

# Find the closest house using Euclidean distance
dist_a = np.linalg.norm(buyer_wants - house_a)
dist_b = np.linalg.norm(buyer_wants - house_b)
dist_c = np.linalg.norm(buyer_wants - house_c)

print(f"Distance to House A: {dist_a:.2f}")
print(f"Distance to House B: {dist_b:.2f}")
print(f"Distance to House C: {dist_c:.2f}")

# This is basically k-Nearest Neighbors (kNN) algorithm!
distances = {"House A": dist_a, "House B": dist_b, "House C": dist_c}
best_match = min(distances, key=distances.get)
print(f"\nBest match: {best_match}")
```

**Expected Output:**

```
Distance to House A: 50.00
Distance to House B: 50.01
Distance to House C: 1500.00

Best match: House A
```

This is a simplified version of the **k-Nearest Neighbors** algorithm — one of the most intuitive ML algorithms. It literally finds the closest vectors.

---

## 20.10 Visualizing 2D Vectors with Matplotlib

Seeing vectors as arrows on a chart makes the math much more intuitive.

### Drawing a Single Vector

```python
import matplotlib.pyplot as plt
import numpy as np

# Vector [3, 4]
v = np.array([3, 4])

# Create the plot
fig, ax = plt.subplots(figsize=(6, 6))

# Draw the vector as an arrow from origin (0,0) to (3,4)
ax.quiver(0, 0, v[0], v[1], angles="xy", scale_units="xy", scale=1,
          color="blue")

# Set up the chart
ax.set_xlim(-1, 6)
ax.set_ylim(-1, 6)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Vector [3, 4]")
ax.grid(True)
ax.set_aspect("equal")

# Mark the point
ax.annotate(f"({v[0]}, {v[1]})", xy=(v[0], v[1]),
            xytext=(v[0]+0.3, v[1]+0.3), fontsize=12)

plt.show()
```

**Expected Output:**

A blue arrow from the origin (0, 0) to the point (3, 4).

```
y
5 |
4 |        -->* (3, 4)
3 |       /
2 |     /
1 |   /
0 +-/--+--+--+--+--
  0  1  2  3  4  5  x
```

**Line-by-line explanation:**

```python
ax.quiver(0, 0, v[0], v[1], angles="xy", scale_units="xy", scale=1, color="blue")
```

`quiver` draws an arrow. Arguments are: start_x, start_y, direction_x, direction_y. The extra parameters make the arrow display correctly on the xy grid.

### Visualizing Vector Addition

```python
import matplotlib.pyplot as plt
import numpy as np

a = np.array([3, 1])
b = np.array([1, 3])
c = a + b    # [4, 4]

fig, ax = plt.subplots(figsize=(7, 7))

# Draw vector a (blue)
ax.quiver(0, 0, a[0], a[1], angles="xy", scale_units="xy", scale=1,
          color="blue", label=f"a = {list(a)}")

# Draw vector b starting from tip of a (red)
ax.quiver(a[0], a[1], b[0], b[1], angles="xy", scale_units="xy", scale=1,
          color="red", label=f"b = {list(b)}")

# Draw result vector (green, dashed)
ax.quiver(0, 0, c[0], c[1], angles="xy", scale_units="xy", scale=1,
          color="green", label=f"a + b = {list(c)}", linestyle="--")

ax.set_xlim(-1, 6)
ax.set_ylim(-1, 6)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Vector Addition: a + b")
ax.legend()
ax.grid(True)
ax.set_aspect("equal")

plt.show()
```

**Expected Output:**

Three arrows. Blue goes from (0,0) to (3,1). Red continues from (3,1) to (4,4). Green goes directly from (0,0) to (4,4) — the same endpoint.

```
y
5 |
4 |              * (4, 4)
  |             /|
3 |           /  |
  |      b  /   |
2 |       /     |
1 |   * /       |  a + b (green diagonal)
  |  a          |
0 +--+--+--+--+-+--
  0  1  2  3  4  5  x

Blue (a): origin to (3,1)
Red (b): (3,1) to (4,4)
Green (a+b): origin to (4,4)
```

### Visualizing the Dot Product Geometrically

```python
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Case 1: Similar direction (positive dot product)
a1, b1 = np.array([3, 1]), np.array([2, 3])
axes[0].quiver(0, 0, a1[0], a1[1], angles="xy", scale_units="xy",
               scale=1, color="blue", label="a")
axes[0].quiver(0, 0, b1[0], b1[1], angles="xy", scale_units="xy",
               scale=1, color="red", label="b")
axes[0].set_title(f"Similar: dot = {np.dot(a1, b1)}")
axes[0].set_xlim(-1, 5)
axes[0].set_ylim(-1, 5)
axes[0].legend()
axes[0].grid(True)
axes[0].set_aspect("equal")

# Case 2: Perpendicular (zero dot product)
a2, b2 = np.array([3, 0]), np.array([0, 3])
axes[1].quiver(0, 0, a2[0], a2[1], angles="xy", scale_units="xy",
               scale=1, color="blue", label="a")
axes[1].quiver(0, 0, b2[0], b2[1], angles="xy", scale_units="xy",
               scale=1, color="red", label="b")
axes[1].set_title(f"Perpendicular: dot = {np.dot(a2, b2)}")
axes[1].set_xlim(-1, 5)
axes[1].set_ylim(-1, 5)
axes[1].legend()
axes[1].grid(True)
axes[1].set_aspect("equal")

# Case 3: Opposite direction (negative dot product)
a3, b3 = np.array([3, 1]), np.array([-2, -1])
axes[2].quiver(0, 0, a3[0], a3[1], angles="xy", scale_units="xy",
               scale=1, color="blue", label="a")
axes[2].quiver(0, 0, b3[0], b3[1], angles="xy", scale_units="xy",
               scale=1, color="red", label="b")
axes[2].set_title(f"Opposite: dot = {np.dot(a3, b3)}")
axes[2].set_xlim(-4, 5)
axes[2].set_ylim(-3, 3)
axes[2].legend()
axes[2].grid(True)
axes[2].set_aspect("equal")

plt.tight_layout()
plt.show()
```

**Expected Output:**

Three charts showing pairs of vectors:
1. Similar direction: positive dot product (9)
2. Perpendicular: zero dot product (0)
3. Opposite direction: negative dot product (-7)

---

## Common Mistakes

**Mistake 1: Trying to add vectors of different sizes.**

```python
a = np.array([1, 2, 3])
b = np.array([4, 5])
result = a + b    # ERROR!
```

**Fix:** Make sure both vectors have the same number of elements. Check with `len(a)` or `a.shape`.

---

**Mistake 2: Confusing dot product with element-wise multiplication.**

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Element-wise multiplication (NOT the dot product)
wrong = a * b           # [4, 10, 18] - a vector

# Dot product (correct)
right = np.dot(a, b)    # 32 - a single number
```

**Fix:** Use `np.dot()` or `@` for the dot product. Use `*` only when you want element-wise multiplication.

---

**Mistake 3: Dividing by zero when making a unit vector.**

```python
v = np.array([0, 0, 0])
unit = v / np.linalg.norm(v)    # Division by zero!
```

**Fix:** Check if the magnitude is zero before normalizing:

```python
magnitude = np.linalg.norm(v)
if magnitude > 0:
    unit = v / magnitude
else:
    print("Cannot normalize a zero vector")
```

---

**Mistake 4: Forgetting that distance is always positive.**

```python
import numpy as np

a = np.array([5, 5])
b = np.array([1, 1])

# Distance is the same in both directions
print(np.linalg.norm(a - b))    # 5.66
print(np.linalg.norm(b - a))    # 5.66 (same!)
```

Distance from A to B equals distance from B to A. Always.

---

**Mistake 5: Using Python lists instead of NumPy arrays.**

```python
# Python lists do NOT support vector math
a = [1, 2, 3]
b = [4, 5, 6]
result = a + b    # [1, 2, 3, 4, 5, 6]  -- concatenation, NOT addition!

# NumPy arrays DO support vector math
import numpy as np
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
result = a + b    # [5, 7, 9]  -- element-wise addition!
```

**Fix:** Always use `np.array()` for vector math. Python lists do not support element-wise operations.

---

## Best Practices

1. **Always use NumPy arrays for vectors**, not Python lists. NumPy is faster and supports all the math operations you need.

2. **Check dimensions before operations.** Use `.shape` to verify vectors are the right size.

3. **Normalize vectors when comparing similarity.** Without normalization, larger values dominate the result.

4. **Use `np.linalg.norm()` for magnitude and distance.** It is optimized and handles any number of dimensions.

5. **Visualize vectors in 2D.** Even if your real data has 100 dimensions, drawing 2D examples helps build intuition.

6. **Remember: dot product = similarity.** When two vectors point the same way, their dot product is large and positive.

7. **Think of features as dimensions.** A dataset with 5 features means each data point is a 5D vector. The math is the same whether you have 2 dimensions or 2000.

---

## Quick Summary

```
+----------------------------------------------------------+
|  Vectors Quick Reference                                  |
+----------------------------------------------------------+
|  Create:          np.array([1, 2, 3])                     |
|                                                           |
|  Addition:        a + b         (element-wise)            |
|  Subtraction:     a - b         (element-wise)            |
|  Scalar multiply: 3 * v         (scales all elements)     |
|  Dot product:     np.dot(a, b)  or  a @ b                 |
|  Magnitude:       np.linalg.norm(v)                       |
|  Unit vector:     v / np.linalg.norm(v)                   |
|  Distance:        np.linalg.norm(a - b)                   |
|                                                           |
|  Key insight:     dot product measures similarity         |
|  ML connection:   every data point IS a vector            |
|  Visualization:   ax.quiver() for arrows                  |
+----------------------------------------------------------+
```

---

## Key Points to Remember

1. **A vector** is a list of numbers with direction and magnitude. In ML, every data point is a vector of features.

2. **Vector addition** adds corresponding elements. It is like combining two movements.

3. **Scalar multiplication** scales every element by the same number. It stretches or shrinks the vector.

4. **The dot product** multiplies corresponding elements and sums the results. It measures how similar two vectors are. This is the most important operation in ML.

5. **Magnitude** (norm) is the length of a vector. Calculated with `np.linalg.norm()`.

6. **Unit vectors** have a magnitude of 1. They represent pure direction. Normalizing data is creating unit vectors.

7. **Euclidean distance** between two vectors is `np.linalg.norm(a - b)`. Small distance means similar. Large distance means different.

---

## Practice Questions

**Question 1:** What is the dot product of [2, 3, 1] and [4, 1, 5]?

**Answer:** The dot product is `2*4 + 3*1 + 1*5 = 8 + 3 + 5 = 16`. In Python: `np.dot([2,3,1], [4,1,5])` returns 16.

---

**Question 2:** What is the magnitude of the vector [3, 4]?

**Answer:** The magnitude is `sqrt(3^2 + 4^2) = sqrt(9 + 16) = sqrt(25) = 5`. This is the classic 3-4-5 right triangle. In Python: `np.linalg.norm([3, 4])` returns 5.0.

---

**Question 3:** Why is the dot product considered a "similarity measure"?

**Answer:** When two vectors point in the same direction (are similar), their corresponding elements tend to have the same sign and similar magnitudes, producing large positive products that sum to a large positive number. When they point in opposite directions, the products are negative, giving a negative sum. When they are perpendicular (unrelated), the positive and negative products cancel out, giving zero. This makes the dot product a natural measure of how aligned or similar two vectors are.

---

**Question 4:** What is the Euclidean distance between [1, 2, 3] and [4, 6, 3]?

**Answer:** `d = sqrt((4-1)^2 + (6-2)^2 + (3-3)^2) = sqrt(9 + 16 + 0) = sqrt(25) = 5`. In Python: `np.linalg.norm(np.array([1,2,3]) - np.array([4,6,3]))` returns 5.0.

---

**Question 5:** Why do we say "features are vectors" in machine learning?

**Answer:** In ML, each data point is described by a set of features (measurements or properties). These features are stored as a list of numbers, which is exactly what a vector is. For example, a house described by [1500 sqft, 3 bedrooms, 2 bathrooms] is a 3-dimensional vector. All the vector math we learn (dot products, distances, norms) is what ML algorithms use to process this data, find patterns, and make predictions.

---

## Exercises

### Exercise 1: Vector Operations Practice

Create two vectors:

- `a = [2, 5, 1, 8]`
- `b = [3, 1, 4, 2]`

Calculate:
1. `a + b`
2. `a - b`
3. `3 * a`
4. The dot product of `a` and `b`
5. The magnitude of `a`
6. The Euclidean distance between `a` and `b`

Verify each result by hand, then confirm with NumPy.

**Hint:** The dot product is `2*3 + 5*1 + 1*4 + 8*2`. The magnitude uses `np.linalg.norm()`.

---

### Exercise 2: Movie Recommender

Five users rated four movie genres on a scale of 1-5:

```
           Action  Comedy  Drama  Horror
User 1:    [5,     2,      3,     1]
User 2:    [4,     3,      4,     1]
User 3:    [1,     5,      2,     4]
User 4:    [5,     1,      2,     2]
User 5:    [2,     4,      5,     1]
```

A new user has ratings `[4, 3, 3, 1]`. Find which existing user is most similar using:
1. Euclidean distance (smallest = most similar)
2. Dot product (largest = most similar)

Do both methods agree on the most similar user?

**Hint:** Loop through all users, calculate the distance/dot product to the new user, and find the minimum distance or maximum dot product.

---

### Exercise 3: Visualize Vector Operations

Create a 2D visualization that shows:
1. Vector `a = [4, 1]` in blue
2. Vector `b = [1, 3]` in red
3. Their sum `a + b` in green
4. Their difference `a - b` in orange

All vectors should start from the origin. Add a legend and grid. Make the aspect ratio equal so the arrows look correct.

**Hint:** Use `ax.quiver()` for each vector. Use `ax.set_aspect("equal")` to prevent distortion.

---

## What Is Next?

You now understand vectors — the fundamental data structure of machine learning. In the next chapter, you will learn about **matrices** — rectangular grids of numbers that extend vectors to two dimensions. If a vector is a row of data, a matrix is a whole table of data. Matrices are how we process multiple data points at once, and they are essential for understanding how neural networks work.
