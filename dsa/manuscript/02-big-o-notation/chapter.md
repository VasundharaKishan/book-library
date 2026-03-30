# Chapter 2: Big O Notation

## What You Will Learn

- What Big O notation is and why it exists
- The seven most common time complexities: O(1), O(log n), O(n), O(n log n), O(n^2), O(2^n), O(n!)
- How to read and interpret a growth comparison table and graph
- Space complexity and how it differs from time complexity
- Best case, worst case, and average case analysis
- A brief introduction to amortized analysis
- How to calculate Big O from real code step by step

## Why This Chapter Matters

Imagine two restaurants. One has a 5-star rating; the other has 2 stars. You do not need to eat at both to know which is probably better. Big O notation is the star rating system for algorithms. It gives you a quick, standardized way to compare solutions without running benchmarks on every possible input. Every technical interview expects you to state the Big O of your solution. Every chapter in this book will analyze complexity. Master this chapter and you have a lens that works everywhere.

---

## 2.1 What Is Big O Notation?

Big O notation describes **how an algorithm's performance scales as the input size grows**. It does not tell you the exact runtime in milliseconds. It tells you the *growth rate*.

Think of it like this: if you are driving somewhere, Big O does not tell you "it will take 47 minutes." It tells you "doubling the distance roughly doubles the time" (that is O(n)) versus "doubling the distance quadruples the time" (that is O(n^2)).

```
    Big O is like a SPEED RATING for algorithms
    =============================================

    Algorithm A:  O(n)     -->  "Linear -- scales well"
    Algorithm B:  O(n^2)   -->  "Quadratic -- gets slow fast"
    Algorithm C:  O(log n) -->  "Logarithmic -- barely slows down"

    Like restaurant star ratings:
    *****  O(1)       Instant, no matter the input
    ****   O(log n)   Barely slows down as input grows
    ***    O(n)       Grows proportionally
    **     O(n^2)     Gets painful quickly
    *      O(2^n)     Unusable for large inputs
```

### The Formal Definition (Simplified)

We say f(n) is O(g(n)) if there exist constants c and n0 such that f(n) <= c * g(n) for all n >= n0.

Translation: **Big O captures the upper bound of growth, ignoring constants and lower-order terms.**

- 5n + 3 is O(n) -- we drop the constant 5 and the additive 3
- 2n^2 + 100n + 999 is O(n^2) -- the n^2 term dominates
- n^3 + n^2 + n + 1 is O(n^3) -- highest power wins

Why drop constants? Because when n is one million, the difference between n and 2n is just a constant factor. But the difference between n and n^2 is the difference between one million and one *trillion*.

---

## 2.2 The Seven Common Complexities

### O(1) -- Constant Time

The algorithm takes the same amount of time regardless of input size. Like looking up a word in a dictionary by page number -- it does not matter if the dictionary has 100 pages or 100,000 pages.

**Python**:
```python
def get_first(arr):
    """Access the first element -- always one operation."""
    return arr[0]

def is_even(n):
    """Check if a number is even -- always one operation."""
    return n % 2 == 0

# Test
print(get_first([10, 20, 30, 40, 50]))  # Output: 10
print(is_even(42))                       # Output: True
```

**Java**:
```java
public class ConstantTime {
    public static int getFirst(int[] arr) {
        return arr[0]; // Always one operation
    }

    public static boolean isEven(int n) {
        return n % 2 == 0; // Always one operation
    }

    public static void main(String[] args) {
        System.out.println(getFirst(new int[]{10, 20, 30, 40, 50})); // Output: 10
        System.out.println(isEven(42));                               // Output: true
    }
}
```

**Output**:
```
10
True
```

**Real-world examples**: Array access by index, hash table lookup, push/pop on a stack.

---

### O(log n) -- Logarithmic Time

Each step cuts the problem in half. Like binary search in a phone book -- with 1,000 pages, you need at most ~10 steps. With 1,000,000 pages, you need at most ~20 steps. Doubling the input only adds *one* more step.

```
    Binary Search: Looking for 7

    [1, 3, 5, 7, 9, 11, 13, 15]     n = 8
               ^
           mid = 9, 7 < 9, go left

    [1, 3, 5, 7]                      n = 4
         ^
     mid = 3, 7 > 3, go right

    [5, 7]                             n = 2
     ^
    mid = 5, 7 > 5, go right

    [7]                                n = 1
     ^
    Found! 3 steps for 8 elements = log2(8) = 3
```

**Python**:
```python
def binary_search(arr, target):
    """O(log n) -- halves the search space each step."""
    left, right = 0, len(arr) - 1
    steps = 0

    while left <= right:
        steps += 1
        mid = (left + right) // 2
        if arr[mid] == target:
            print(f"Found {target} in {steps} steps")
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    print(f"{target} not found after {steps} steps")
    return -1

# Test
arr = list(range(1, 17))  # [1, 2, 3, ..., 16]
binary_search(arr, 13)     # Output: Found 13 in 4 steps (log2(16) = 4)
```

**Java**:
```java
public class BinarySearchDemo {
    public static int binarySearch(int[] arr, int target) {
        int left = 0, right = arr.length - 1;
        int steps = 0;

        while (left <= right) {
            steps++;
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) {
                System.out.println("Found " + target + " in " + steps + " steps");
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        System.out.println(target + " not found after " + steps + " steps");
        return -1;
    }

    public static void main(String[] args) {
        int[] arr = new int[16];
        for (int i = 0; i < 16; i++) arr[i] = i + 1;
        binarySearch(arr, 13); // Output: Found 13 in 4 steps
    }
}
```

**Output**:
```
Found 13 in 4 steps
```

**Real-world examples**: Binary search, balanced BST operations, finding a page in a book.

---

### O(n) -- Linear Time

The algorithm processes each element once. Doubling the input doubles the time. Like reading every page of a book -- a 200-page book takes twice as long as a 100-page book.

**Python**:
```python
def find_max(arr):
    """O(n) -- must check every element."""
    max_val = arr[0]
    for num in arr:
        if num > max_val:
            max_val = num
    return max_val

def contains(arr, target):
    """O(n) -- might need to check every element."""
    for item in arr:
        if item == target:
            return True
    return False

# Test
print(find_max([3, 1, 4, 1, 5, 9, 2, 6]))  # Output: 9
print(contains([10, 20, 30], 20))             # Output: True
print(contains([10, 20, 30], 99))             # Output: False
```

**Java**:
```java
public class LinearTime {
    public static int findMax(int[] arr) {
        int maxVal = arr[0];
        for (int num : arr) {
            if (num > maxVal) maxVal = num;
        }
        return maxVal;
    }

    public static boolean contains(int[] arr, int target) {
        for (int item : arr) {
            if (item == target) return true;
        }
        return false;
    }

    public static void main(String[] args) {
        System.out.println(findMax(new int[]{3,1,4,1,5,9,2,6})); // Output: 9
        System.out.println(contains(new int[]{10,20,30}, 20));     // Output: true
        System.out.println(contains(new int[]{10,20,30}, 99));     // Output: false
    }
}
```

**Output**:
```
9
True (true)
False (false)
```

**Real-world examples**: Linear search, summing an array, printing all elements.

---

### O(n log n) -- Linearithmic Time

This is the sweet spot for sorting. Algorithms like merge sort and quicksort achieve this by dividing the problem (log n levels) and doing linear work at each level.

```
    Merge Sort: n log n

    Level 0 (1 split):  [8, 3, 5, 1, 7, 2, 6, 4]        n work
                        /                    \
    Level 1 (2 parts): [8, 3, 5, 1]   [7, 2, 6, 4]       n work
                       /      \         /      \
    Level 2 (4 parts): [8,3] [5,1]   [7,2] [6,4]          n work
                       / \    / \     / \    / \
    Level 3 (8 parts): 8  3  5  1   7  2  6  4            n work

    log2(8) = 3 levels, each doing n work --> O(n log n)
```

**Python**:
```python
def merge_sort(arr):
    """O(n log n) -- divide and conquer sorting."""
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Test
print(merge_sort([8, 3, 5, 1, 7, 2, 6, 4]))
# Output: [1, 2, 3, 4, 5, 6, 7, 8]
```

**Java**:
```java
import java.util.Arrays;

public class MergeSortDemo {
    public static int[] mergeSort(int[] arr) {
        if (arr.length <= 1) return arr;

        int mid = arr.length / 2;
        int[] left = mergeSort(Arrays.copyOfRange(arr, 0, mid));
        int[] right = mergeSort(Arrays.copyOfRange(arr, mid, arr.length));
        return merge(left, right);
    }

    private static int[] merge(int[] left, int[] right) {
        int[] result = new int[left.length + right.length];
        int i = 0, j = 0, k = 0;
        while (i < left.length && j < right.length) {
            if (left[i] <= right[j]) result[k++] = left[i++];
            else result[k++] = right[j++];
        }
        while (i < left.length) result[k++] = left[i++];
        while (j < right.length) result[k++] = right[j++];
        return result;
    }

    public static void main(String[] args) {
        int[] result = mergeSort(new int[]{8, 3, 5, 1, 7, 2, 6, 4});
        System.out.println(Arrays.toString(result));
        // Output: [1, 2, 3, 4, 5, 6, 7, 8]
    }
}
```

**Output**:
```
[1, 2, 3, 4, 5, 6, 7, 8]
```

**Real-world examples**: Merge sort, quicksort (average case), heap sort.

---

### O(n^2) -- Quadratic Time

Every element is compared with every other element. Doubling the input quadruples the time. Like a round-robin tournament where every player plays every other player.

**Python**:
```python
def bubble_sort(arr):
    """O(n^2) -- nested loops comparing all pairs."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def has_duplicate_brute(arr):
    """O(n^2) -- check every pair."""
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                return True
    return False

# Test
print(bubble_sort([64, 34, 25, 12, 22, 11, 90]))
# Output: [11, 12, 22, 25, 34, 64, 90]

print(has_duplicate_brute([1, 2, 3, 4, 5]))     # Output: False
print(has_duplicate_brute([1, 2, 3, 2, 5]))     # Output: True
```

**Java**:
```java
import java.util.Arrays;

public class QuadraticTime {
    public static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }

    public static void main(String[] args) {
        int[] arr = {64, 34, 25, 12, 22, 11, 90};
        bubbleSort(arr);
        System.out.println(Arrays.toString(arr));
        // Output: [11, 12, 22, 25, 34, 64, 90]
    }
}
```

**Output**:
```
[11, 12, 22, 25, 34, 64, 90]
False
True
```

**Real-world examples**: Bubble sort, selection sort, insertion sort, brute-force pair finding.

---

### O(2^n) -- Exponential Time

The work doubles with each additional element. Like the number of subsets of a set -- a set of 3 has 8 subsets, a set of 10 has 1,024, a set of 30 has over a *billion*.

**Python**:
```python
def fibonacci_recursive(n):
    """O(2^n) -- each call branches into two more."""
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

# Test (small n only -- this gets VERY slow)
for i in range(10):
    print(f"fib({i}) = {fibonacci_recursive(i)}")
# Output: fib(0)=0, fib(1)=1, fib(2)=1, fib(3)=2, ... fib(9)=34
```

**Java**:
```java
public class ExponentialTime {
    public static int fibonacciRecursive(int n) {
        if (n <= 1) return n;
        return fibonacciRecursive(n - 1) + fibonacciRecursive(n - 2);
    }

    public static void main(String[] args) {
        for (int i = 0; i < 10; i++) {
            System.out.println("fib(" + i + ") = " + fibonacciRecursive(i));
        }
    }
}
```

**Output**:
```
fib(0) = 0
fib(1) = 1
fib(2) = 1
fib(3) = 2
fib(4) = 3
fib(5) = 5
fib(6) = 8
fib(7) = 13
fib(8) = 21
fib(9) = 34
```

```
    The Recursive Fibonacci Call Tree for fib(5):

                            fib(5)
                           /      \
                       fib(4)     fib(3)
                      /    \       /    \
                  fib(3)  fib(2) fib(2) fib(1)
                  /   \    / \    / \
              fib(2) fib(1) ...  ...
              / \
          fib(1) fib(0)

    So much repeated work! fib(3) is computed twice, fib(2) three times.
    This is why O(2^n) is terrible.
```

**Real-world examples**: Naive recursive Fibonacci, generating all subsets, brute-force password cracking.

---

### O(n!) -- Factorial Time

The nuclear option. For n = 10, that is 3,628,800 operations. For n = 20, that is 2,432,902,008,176,640,000. These algorithms are only practical for very small inputs.

**Python**:
```python
def permutations(arr, start=0):
    """O(n!) -- generate all permutations."""
    if start == len(arr) - 1:
        print(arr)
        return

    for i in range(start, len(arr)):
        arr[start], arr[i] = arr[i], arr[start]
        permutations(arr, start + 1)
        arr[start], arr[i] = arr[i], arr[start]

# Test
permutations([1, 2, 3])
```

**Output**:
```
[1, 2, 3]
[1, 3, 2]
[2, 1, 3]
[2, 3, 1]
[3, 2, 1]
[3, 1, 2]
```

Six permutations for 3 elements (3! = 6). For 10 elements, there would be 3,628,800 permutations.

**Real-world examples**: Brute-force traveling salesman, generating all permutations.

---

## 2.3 Growth Comparison Table and Graph

### Comparison Table

| n | O(1) | O(log n) | O(n) | O(n log n) | O(n^2) | O(2^n) | O(n!) |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 0 | 1 | 0 | 1 | 2 | 1 |
| 10 | 1 | 3 | 10 | 33 | 100 | 1,024 | 3,628,800 |
| 100 | 1 | 7 | 100 | 664 | 10,000 | 1.27 x 10^30 | 9.3 x 10^157 |
| 1,000 | 1 | 10 | 1,000 | 9,966 | 1,000,000 | OVERFLOW | OVERFLOW |
| 10,000 | 1 | 13 | 10,000 | 132,877 | 100,000,000 | OVERFLOW | OVERFLOW |
| 100,000 | 1 | 17 | 100,000 | 1,660,964 | 10,000,000,000 | OVERFLOW | OVERFLOW |

### ASCII Growth Graph

```
    Operations
    ^
    |                                                        * O(n!)
    |                                                  *
    |                                           *
    |                                    *              * O(2^n)
    |                              *              *
    |                         *             *
    |                    *            *
    |               *           *                    ******* O(n^2)
    |          *          *                   *******
    |     *         *                  *******
    |          *                *******
    |     *              *******                     ....... O(n log n)
    |*              ******.............................
    |          *****......                           ------- O(n)
    |     *****..........----------------------------
    |   **....-----------                            ======= O(log n)
    |  *..----- ==================================
    | *.---====                                      +++++++ O(1)
    |++++++++++++++++++++++++++++++++++++++++++++++
    +---------------------------------------------------> n (input size)
```

The key takeaway: **the gap between complexities explodes as n grows.** An O(n^2) algorithm that works fine on 100 elements becomes unusable on 100,000 elements.

---

## 2.4 Space Complexity

Time complexity measures *how long* an algorithm takes. Space complexity measures *how much extra memory* it uses.

```
    TIME COMPLEXITY:   How many steps?
    SPACE COMPLEXITY:  How much extra memory?

    Both use the same Big O notation.
```

**Python**:
```python
# O(1) space -- constant extra memory
def sum_array(arr):
    total = 0            # Just one extra variable
    for num in arr:
        total += num
    return total

# O(n) space -- extra memory grows with input
def double_array(arr):
    result = []          # New array that grows with input
    for num in arr:
        result.append(num * 2)
    return result

# O(n) space -- recursive call stack
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)  # n stack frames

# Test
print(sum_array([1, 2, 3, 4, 5]))      # Output: 15  (O(1) space)
print(double_array([1, 2, 3, 4, 5]))    # Output: [2, 4, 6, 8, 10] (O(n) space)
print(factorial(5))                      # Output: 120 (O(n) space from call stack)
```

**Java**:
```java
public class SpaceComplexity {
    // O(1) space
    public static int sumArray(int[] arr) {
        int total = 0;
        for (int num : arr) total += num;
        return total;
    }

    // O(n) space
    public static int[] doubleArray(int[] arr) {
        int[] result = new int[arr.length];
        for (int i = 0; i < arr.length; i++) {
            result[i] = arr[i] * 2;
        }
        return result;
    }

    // O(n) space (call stack)
    public static int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }

    public static void main(String[] args) {
        System.out.println(sumArray(new int[]{1,2,3,4,5}));  // 15
        int[] doubled = doubleArray(new int[]{1,2,3,4,5});
        for (int d : doubled) System.out.print(d + " ");     // 2 4 6 8 10
        System.out.println();
        System.out.println(factorial(5));                     // 120
    }
}
```

**Output**:
```
15
[2, 4, 6, 8, 10]
120
```

### Common Space Complexities

| Space | Example |
|---|---|
| O(1) | Swapping two variables, in-place sorting |
| O(log n) | Recursive binary search (call stack depth) |
| O(n) | Creating a copy of the input, hash map of all elements |
| O(n^2) | 2D matrix, adjacency matrix for a graph |

---

## 2.5 Best, Worst, and Average Case

The same algorithm can have different performance depending on the input.

```
    LINEAR SEARCH for target = 5

    Best case:   [5, 8, 3, 1, 9]   --> Found immediately! O(1)
                  ^

    Average case: [8, 3, 5, 1, 9]   --> Found in the middle. O(n/2) = O(n)
                        ^

    Worst case:  [8, 3, 1, 9, 5]   --> Found at the very end. O(n)
                              ^

    Worst case:  [8, 3, 1, 9, 7]   --> Not found at all. O(n)
```

| Case | Description | When we use it |
|---|---|---|
| **Best case** | The most favorable input | Rarely useful -- too optimistic |
| **Average case** | Expected performance over random inputs | Useful for real-world estimates |
| **Worst case** | The most unfavorable input | Most commonly used in Big O |

**When we say O(n), we usually mean the worst case** unless stated otherwise. This gives us a guarantee: "No matter what input you give me, it will never be worse than this."

### Example: Quicksort

- **Best case**: O(n log n) -- pivot always splits the array evenly
- **Average case**: O(n log n) -- random pivots tend to split reasonably
- **Worst case**: O(n^2) -- pivot is always the smallest or largest element

This is why quicksort uses random pivot selection or "median of three" to avoid the worst case in practice.

---

## 2.6 Amortized Analysis (Brief Introduction)

Sometimes an operation is *usually* fast but *occasionally* slow. Amortized analysis averages the cost over a sequence of operations.

**The Classic Example: Dynamic Array (Python list / Java ArrayList)**

```
    Dynamic Array: Adding elements

    Size: 4, Capacity: 4
    [1, 2, 3, 4]  <-- Full!

    Add 5 --> Must resize! Create array of size 8, copy everything.
    [1, 2, 3, 4, 5, _, _, _]  <-- This add was O(n)

    Add 6 --> Space available. Just append.
    [1, 2, 3, 4, 5, 6, _, _]  <-- This add was O(1)

    Add 7 --> Space available. Just append.
    [1, 2, 3, 4, 5, 6, 7, _]  <-- This add was O(1)

    Add 8 --> Space available. Just append.
    [1, 2, 3, 4, 5, 6, 7, 8]  <-- This add was O(1)

    Most appends are O(1), with occasional O(n) resizes.
    Amortized cost per append: O(1)
```

The expensive resize happens so rarely that when you spread its cost across all the cheap appends, each append is effectively O(1). This is called **amortized O(1)**.

You do not need to deeply understand amortized analysis right now. Just remember: **appending to a dynamic array is amortized O(1)**, even though individual resizes are O(n).

---

## 2.7 How to Calculate Big O from Code

Follow these rules:

### Rule 1: Drop Constants

```
    3n + 5         -->  O(n)
    100n           -->  O(n)
    n/2            -->  O(n)
    2^n + 1000n    -->  O(2^n)
```

### Rule 2: Drop Lower-Order Terms

```
    n^2 + n        -->  O(n^2)     (n is negligible next to n^2)
    n^3 + n^2 + n  -->  O(n^3)     (highest power wins)
    n + log n      -->  O(n)       (n grows faster than log n)
```

### Rule 3: Sequential Steps Add

```python
# Step 1: O(n)
for item in arr:
    print(item)

# Step 2: O(n)
for item in arr:
    print(item * 2)

# Total: O(n) + O(n) = O(2n) = O(n)
```

### Rule 4: Nested Loops Multiply

```python
# Outer loop: n iterations
for i in range(n):          # O(n)
    # Inner loop: n iterations
    for j in range(n):      # O(n)
        print(i, j)         # O(1)

# Total: O(n) * O(n) = O(n^2)
```

### Rule 5: Different Inputs Use Different Variables

```python
def print_pairs(arr_a, arr_b):
    for a in arr_a:          # O(a) where a = len(arr_a)
        for b in arr_b:      # O(b) where b = len(arr_b)
            print(a, b)

# Total: O(a * b), NOT O(n^2)
# They are different inputs -- do not assume they are the same size.
```

### Step-by-Step Example: Analyzing Real Code

Let us analyze a function that finds duplicate elements:

**Python**:
```python
def find_duplicates(arr):
    seen = set()           # O(1) -- creating empty set
    duplicates = []        # O(1) -- creating empty list

    for num in arr:        # O(n) -- loop through all elements
        if num in seen:    # O(1) -- set lookup is O(1)
            duplicates.append(num)  # O(1) amortized
        else:
            seen.add(num)  # O(1) -- set insertion is O(1)

    return duplicates      # O(1)

# Analysis:
# The loop runs n times. Each iteration does O(1) work.
# Total time: O(n)
# Space: O(n) for the set and duplicates list

# Test
print(find_duplicates([1, 3, 5, 3, 7, 1, 9]))  # Output: [3, 1]
```

**Java**:
```java
import java.util.*;

public class FindDuplicates {
    public static List<Integer> findDuplicates(int[] arr) {
        Set<Integer> seen = new HashSet<>();
        List<Integer> duplicates = new ArrayList<>();

        for (int num : arr) {            // O(n)
            if (seen.contains(num)) {     // O(1)
                duplicates.add(num);      // O(1) amortized
            } else {
                seen.add(num);            // O(1)
            }
        }
        return duplicates;
    }

    public static void main(String[] args) {
        System.out.println(findDuplicates(new int[]{1,3,5,3,7,1,9}));
        // Output: [3, 1]
    }
}
```

**Output**:
```
[3, 1]
```

### Another Example: Nested Complexity

**Python**:
```python
def mystery(n):
    count = 0
    i = 1
    while i < n:         # How many times does this run?
        j = 1
        while j < n:     # This runs n times for each outer iteration
            count += 1
            j *= 2       # j doubles each time: 1, 2, 4, 8, ...
        i += 1           # i increments by 1 each time

    return count

# Analysis:
# Outer loop: i goes from 1 to n-1 --> O(n) iterations
# Inner loop: j doubles each time --> 1, 2, 4, 8, ... until >= n
#             That is log2(n) iterations
# Total: O(n) * O(log n) = O(n log n)

print(mystery(16))  # Output: 60 (15 outer * 4 inner)
```

**Java**:
```java
public class Mystery {
    public static int mystery(int n) {
        int count = 0;
        int i = 1;
        while (i < n) {
            int j = 1;
            while (j < n) {
                count++;
                j *= 2;
            }
            i++;
        }
        return count;
    }

    public static void main(String[] args) {
        System.out.println(mystery(16)); // Output: 60
    }
}
```

**Output**:
```
60
```

---

## 2.8 Complexity Analysis Walkthrough

Let us put it all together with a complete walkthrough.

**Problem**: Given an array of integers, find if any two numbers sum to a given target.

### Approach 1: Brute Force

```python
def two_sum_brute(arr, target):
    for i in range(len(arr)):              # O(n)
        for j in range(i + 1, len(arr)):   # O(n)
            if arr[i] + arr[j] == target:  # O(1)
                return [i, j]
    return []

# Time: O(n^2) -- two nested loops
# Space: O(1) -- no extra data structures
```

### Approach 2: Hash Map

```python
def two_sum_hash(arr, target):
    seen = {}                              # Space: O(n)
    for i, num in enumerate(arr):          # O(n)
        complement = target - num          # O(1)
        if complement in seen:             # O(1) -- hash lookup
            return [seen[complement], i]
        seen[num] = i                      # O(1) -- hash insert
    return []

# Time: O(n) -- single pass
# Space: O(n) -- hash map stores up to n elements
```

```
    COMPARISON:
    +------------------+----------+----------+
    | Approach         | Time     | Space    |
    +------------------+----------+----------+
    | Brute Force      | O(n^2)   | O(1)    |
    | Hash Map         | O(n)     | O(n)    |
    +------------------+----------+----------+

    Trade-off: We spend more MEMORY to save TIME.
    This is one of the most common trade-offs in CS.
```

---

## Common Mistakes

1. **Confusing Big O with exact runtime.** O(n) does not mean "n milliseconds." It means "runtime grows linearly with input size."
2. **Forgetting to drop constants.** O(2n) is just O(n). O(n/2) is just O(n). Constants do not matter for growth rate.
3. **Assuming nested loops always mean O(n^2).** If the inner loop runs a constant number of times, it is still O(n). If the inner loop depends on a different variable, use a different letter.
4. **Ignoring space complexity.** An O(n) time solution that uses O(n^2) space might be worse than an O(n log n) time solution that uses O(1) space.
5. **Forgetting the call stack.** Recursive algorithms use O(depth) space for the call stack, even if they create no other data structures.

## Best Practices

1. **Always state both time and space complexity** when analyzing an algorithm.
2. **Start by identifying the loops.** Single loop is usually O(n). Nested loops that both depend on n are usually O(n^2). A loop where the variable doubles or halves is O(log n).
3. **Use Big O to compare approaches** before coding. If you know one approach is O(n) and another is O(n^2), implement the O(n) approach.
4. **Remember common complexities**: array access is O(1), hash table operations are O(1) average, sorting is O(n log n), and if you see "all pairs" or "all subsets," think O(n^2) or O(2^n).
5. **Practice by analyzing code you already wrote.** Go back to old projects and figure out the Big O of your functions.

---

## Quick Summary

Big O notation is a standardized way to describe how an algorithm's performance scales with input size. It focuses on growth rate, dropping constants and lower-order terms. The most common complexities from fastest to slowest are O(1), O(log n), O(n), O(n log n), O(n^2), O(2^n), and O(n!). Space complexity uses the same notation but measures memory usage. We typically analyze worst-case performance unless stated otherwise. To calculate Big O: count the loops, check if they are sequential (add) or nested (multiply), identify how loop variables change, and simplify.

## Key Points

- **Big O measures growth rate**, not exact speed. It answers: "How does performance change as input size increases?"
- **Drop constants and lower-order terms**: 5n^2 + 3n + 7 becomes O(n^2).
- **Sequential operations add**: O(n) + O(n) = O(n). **Nested operations multiply**: O(n) * O(n) = O(n^2).
- **Space complexity counts extra memory** used by the algorithm, not the input itself.
- **Worst case is the standard** unless specifically discussing average or best case.
- **Time-space trade-off**: you can often make an algorithm faster by using more memory (e.g., hash maps).
- **Amortized O(1)**: some operations are usually O(1) with rare O(n) spikes that average out.

---

## Practice Questions

1. What is the time complexity of the following code? Explain your reasoning.
   ```python
   for i in range(n):
       for j in range(n):
           for k in range(n):
               print(i + j + k)
   ```

2. What is the time and space complexity of creating a list of all pairs from an array of n elements?

3. An algorithm has complexity O(n^2 + n log n). What does it simplify to and why?

4. You have two algorithms: Algorithm A runs in O(n log n) time and O(n) space. Algorithm B runs in O(n^2) time and O(1) space. Under what circumstances might you prefer Algorithm B?

5. What is the time complexity of the following code?
   ```python
   i = n
   while i > 0:
       print(i)
       i = i // 2
   ```

---

## LeetCode-Style Problems

### Problem 1: Find the Single Number (Easy)

**Problem**: Given a non-empty array of integers where every element appears twice except for one, find that single element. Your solution should have O(n) time and O(1) space.

**Python**:
```python
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num  # XOR: a ^ a = 0, a ^ 0 = a
    return result

# Test
print(single_number([2, 2, 1]))         # Output: 1
print(single_number([4, 1, 2, 1, 2]))   # Output: 4
print(single_number([1]))               # Output: 1
```

**Java**:
```java
public class SingleNumber {
    public static int singleNumber(int[] nums) {
        int result = 0;
        for (int num : nums) {
            result ^= num;
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(singleNumber(new int[]{2, 2, 1}));       // Output: 1
        System.out.println(singleNumber(new int[]{4, 1, 2, 1, 2})); // Output: 4
    }
}
```

**Output**:
```
1
4
1
```

**Complexity**: Time O(n), Space O(1). The XOR trick: every pair cancels out (a XOR a = 0), leaving only the single number.

---

### Problem 2: Contains Duplicate (Easy)

**Problem**: Given an integer array, return true if any value appears at least twice.

**Approach 1 -- Brute Force O(n^2)**:
```python
def contains_duplicate_brute(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False
```

**Approach 2 -- Sort First O(n log n)**:
```python
def contains_duplicate_sort(nums):
    nums.sort()
    for i in range(1, len(nums)):
        if nums[i] == nums[i - 1]:
            return True
    return False
```

**Approach 3 -- Hash Set O(n)**:
```python
def contains_duplicate_set(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

# Test all three
test = [1, 2, 3, 1]
print(contains_duplicate_brute(test))  # Output: True
print(contains_duplicate_sort(test[:]))# Output: True
print(contains_duplicate_set(test))    # Output: True
```

**Java (Hash Set approach)**:
```java
import java.util.HashSet;

public class ContainsDuplicate {
    public static boolean containsDuplicate(int[] nums) {
        HashSet<Integer> seen = new HashSet<>();
        for (int num : nums) {
            if (seen.contains(num)) return true;
            seen.add(num);
        }
        return false;
    }

    public static void main(String[] args) {
        System.out.println(containsDuplicate(new int[]{1,2,3,1}));  // true
        System.out.println(containsDuplicate(new int[]{1,2,3,4}));  // false
    }
}
```

**Output**:
```
True
True
True
```

| Approach | Time | Space |
|---|---|---|
| Brute Force | O(n^2) | O(1) |
| Sort First | O(n log n) | O(1) or O(n) |
| Hash Set | O(n) | O(n) |

---

### Problem 3: Power of Two (Easy)

**Problem**: Given an integer n, return true if it is a power of two.

**Python**:
```python
def is_power_of_two(n):
    """O(1) time, O(1) space -- bit manipulation."""
    if n <= 0:
        return False
    return (n & (n - 1)) == 0
    # Powers of 2 have exactly one bit set: 1, 10, 100, 1000...
    # n-1 flips all bits after that one: 0, 01, 011, 0111...
    # AND of these is always 0 for powers of 2

# Test
print(is_power_of_two(1))    # Output: True  (2^0)
print(is_power_of_two(16))   # Output: True  (2^4)
print(is_power_of_two(3))    # Output: False
print(is_power_of_two(0))    # Output: False
```

**Java**:
```java
public class PowerOfTwo {
    public static boolean isPowerOfTwo(int n) {
        if (n <= 0) return false;
        return (n & (n - 1)) == 0;
    }

    public static void main(String[] args) {
        System.out.println(isPowerOfTwo(1));   // true
        System.out.println(isPowerOfTwo(16));  // true
        System.out.println(isPowerOfTwo(3));   // false
        System.out.println(isPowerOfTwo(0));   // false
    }
}
```

**Output**:
```
True
True
False
False
```

**Complexity**: Time O(1), Space O(1). A beautiful constant-time solution using bit manipulation.

---

## What Is Next?

Now that you can measure and compare algorithm performance, it is time to meet your first data structure. In Chapter 3, you will learn about **Arrays** -- the most fundamental data structure in all of programming. You will see how their memory layout makes access lightning-fast, why insertion and deletion are expensive, and how to solve classic interview problems like Two Sum and Maximum Subarray.
