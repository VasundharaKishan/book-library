# Chapter 10: Sorting -- Bubble Sort, Selection Sort, and Insertion Sort

## What You Will Learn

- Why sorting is one of the most fundamental operations in computer science
- How Bubble Sort works by repeatedly swapping adjacent elements
- How Selection Sort works by finding the minimum element in each pass
- How Insertion Sort works by building a sorted portion one element at a time
- Step-by-step ASCII walkthroughs for each algorithm
- Python and Java implementations with detailed comments
- Time and space complexity analysis for each algorithm
- What stability means in sorting and why it matters
- When Insertion Sort actually outperforms "better" algorithms

## Why This Chapter Matters

Sorting is the backbone of computer science. Binary search requires sorted data. Databases sort results for display. Operating systems sort processes by priority. Even seemingly unrelated problems like finding duplicates, computing medians, and optimizing schedules become much easier once the data is sorted.

The three algorithms in this chapter -- Bubble Sort, Selection Sort, and Insertion Sort -- are all O(n^2) in the worst case, which makes them impractical for large datasets. So why study them? Because they are simple enough to understand completely, they teach you how to analyze algorithms, and Insertion Sort is genuinely useful in practice for small or nearly sorted data. Every professional sort implementation (Python's `sorted()`, Java's `Arrays.sort()`) uses Insertion Sort internally for small subarrays.

---

## 10.1 Why Sorting Matters

### Before and After Sorting

```
Unsorted: [38, 27, 43, 3, 9, 82, 10]

Finding minimum:     Scan entire array    O(n) each time
Finding duplicates:  Compare all pairs    O(n^2)
Binary search:       Not possible

Sorted:   [3, 9, 10, 27, 38, 43, 82]

Finding minimum:     First element        O(1)
Finding duplicates:  Check neighbors      O(n)
Binary search:       Works perfectly      O(log n)
```

### Sorting Terminology

- **In-place**: Uses O(1) extra memory (sorts within the original array).
- **Stable**: Preserves the relative order of equal elements.
- **Comparison-based**: Determines order by comparing pairs of elements.
- **Adaptive**: Runs faster on partially sorted data.

---

## 10.2 Bubble Sort

### The Idea

Bubble Sort repeatedly walks through the array, comparing adjacent elements and swapping them if they are in the wrong order. The largest unsorted element "bubbles up" to its correct position at the end of each pass.

### Step-by-Step Walkthrough

```
Array: [5, 3, 8, 4, 2]

--- Pass 1 ---
Compare 5, 3 -> swap:   [3, 5, 8, 4, 2]
Compare 5, 8 -> ok:     [3, 5, 8, 4, 2]
Compare 8, 4 -> swap:   [3, 5, 4, 8, 2]
Compare 8, 2 -> swap:   [3, 5, 4, 2, 8]   <- 8 is in final position
                                     ^

--- Pass 2 ---
Compare 3, 5 -> ok:     [3, 5, 4, 2, 8]
Compare 5, 4 -> swap:   [3, 4, 5, 2, 8]
Compare 5, 2 -> swap:   [3, 4, 2, 5, 8]   <- 5 is in final position
                                  ^

--- Pass 3 ---
Compare 3, 4 -> ok:     [3, 4, 2, 5, 8]
Compare 4, 2 -> swap:   [3, 2, 4, 5, 8]   <- 4 is in final position
                               ^

--- Pass 4 ---
Compare 3, 2 -> swap:   [2, 3, 4, 5, 8]   <- 3 is in final position
                            ^

Result: [2, 3, 4, 5, 8]   (sorted!)
```

### Python -- Bubble Sort

```python
def bubble_sort(arr):
    n = len(arr)

    for i in range(n - 1):
        swapped = False

        for j in range(n - 1 - i):  # Last i elements already sorted
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        if not swapped:  # Optimization: stop if no swaps occurred
            break

    return arr


data = [5, 3, 8, 4, 2]
print(bubble_sort(data))  # Output: [2, 3, 4, 5, 8]
```

### Java -- Bubble Sort

```java
import java.util.Arrays;

public class BubbleSort {
    public static void bubbleSort(int[] arr) {
        int n = arr.length;

        for (int i = 0; i < n - 1; i++) {
            boolean swapped = false;

            for (int j = 0; j < n - 1 - i; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                    swapped = true;
                }
            }

            if (!swapped) break;  // Already sorted
        }
    }

    public static void main(String[] args) {
        int[] data = {5, 3, 8, 4, 2};
        bubbleSort(data);
        System.out.println(Arrays.toString(data));
        // Output: [2, 3, 4, 5, 8]
    }
}
```

### Complexity Analysis

| Case    | Time   | Why                                              |
|---------|--------|--------------------------------------------------|
| Best    | O(n)   | Already sorted; one pass, no swaps, early exit   |
| Average | O(n^2) | ~n^2/4 comparisons and swaps on average          |
| Worst   | O(n^2) | Reverse sorted; every pair gets swapped           |

- **Space**: O(1) -- in-place
- **Stable**: Yes -- equal elements are never swapped
- **Adaptive**: Yes (with the `swapped` optimization)

---

## 10.3 Selection Sort

### The Idea

Selection Sort divides the array into two parts: a sorted portion (left) and an unsorted portion (right). In each pass, it finds the minimum element in the unsorted portion and swaps it into the next position of the sorted portion.

### Step-by-Step Walkthrough

```
Array: [29, 10, 14, 37, 13]

--- Pass 1: Find minimum in [29, 10, 14, 37, 13] ---
Minimum = 10 (index 1)
Swap arr[0] and arr[1]:  [10, 29, 14, 37, 13]
                          ^^
                         sorted | unsorted

--- Pass 2: Find minimum in [29, 14, 37, 13] ---
Minimum = 13 (index 4)
Swap arr[1] and arr[4]:  [10, 13, 14, 37, 29]
                          ^^^^^^
                         sorted | unsorted

--- Pass 3: Find minimum in [14, 37, 29] ---
Minimum = 14 (index 2)
No swap needed:           [10, 13, 14, 37, 29]
                          ^^^^^^^^^
                          sorted  | unsorted

--- Pass 4: Find minimum in [37, 29] ---
Minimum = 29 (index 4)
Swap arr[3] and arr[4]:  [10, 13, 14, 29, 37]
                          ^^^^^^^^^^^^
                           sorted   | unsorted

Result: [10, 13, 14, 29, 37]  (sorted!)
```

### Python -- Selection Sort

```python
def selection_sort(arr):
    n = len(arr)

    for i in range(n - 1):
        min_index = i

        # Find the minimum element in unsorted portion
        for j in range(i + 1, n):
            if arr[j] < arr[min_index]:
                min_index = j

        # Swap the minimum element with the first unsorted element
        if min_index != i:
            arr[i], arr[min_index] = arr[min_index], arr[i]

    return arr


data = [29, 10, 14, 37, 13]
print(selection_sort(data))  # Output: [10, 13, 14, 29, 37]
```

### Java -- Selection Sort

```java
import java.util.Arrays;

public class SelectionSort {
    public static void selectionSort(int[] arr) {
        int n = arr.length;

        for (int i = 0; i < n - 1; i++) {
            int minIndex = i;

            for (int j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIndex]) {
                    minIndex = j;
                }
            }

            if (minIndex != i) {
                int temp = arr[i];
                arr[i] = arr[minIndex];
                arr[minIndex] = temp;
            }
        }
    }

    public static void main(String[] args) {
        int[] data = {29, 10, 14, 37, 13};
        selectionSort(data);
        System.out.println(Arrays.toString(data));
        // Output: [10, 13, 14, 29, 37]
    }
}
```

### Complexity Analysis

| Case    | Time   | Why                                          |
|---------|--------|----------------------------------------------|
| Best    | O(n^2) | Always scans the entire unsorted portion     |
| Average | O(n^2) | Same number of comparisons regardless        |
| Worst   | O(n^2) | Same as best -- not adaptive                 |

- **Space**: O(1) -- in-place
- **Stable**: No -- the swap can move equal elements past each other
- **Adaptive**: No -- always O(n^2) regardless of input order
- **Advantage**: Minimizes the number of swaps -- at most n-1 swaps total. Useful when writing to memory is expensive.

---

## 10.4 Insertion Sort

### The Idea

Insertion Sort works the way you sort playing cards in your hand. You pick up cards one at a time and insert each card into its correct position among the cards you have already sorted.

### Step-by-Step Walkthrough

```
Array: [5, 2, 4, 6, 1, 3]

--- Step 1: Insert 2 ---
Sorted: [5]  |  Key: 2
2 < 5, shift 5 right:  [_, 5, 4, 6, 1, 3]
Insert 2:               [2, 5, 4, 6, 1, 3]
                         ^^^^
                        sorted

--- Step 2: Insert 4 ---
Sorted: [2, 5]  |  Key: 4
4 < 5, shift 5 right:  [2, _, 5, 6, 1, 3]
4 > 2, stop
Insert 4:               [2, 4, 5, 6, 1, 3]
                         ^^^^^^^
                         sorted

--- Step 3: Insert 6 ---
Sorted: [2, 4, 5]  |  Key: 6
6 > 5, already in place: [2, 4, 5, 6, 1, 3]
                          ^^^^^^^^^^
                           sorted

--- Step 4: Insert 1 ---
Sorted: [2, 4, 5, 6]  |  Key: 1
1 < 6, shift: [2, 4, 5, _, 6, 3]
1 < 5, shift: [2, 4, _, 5, 6, 3]
1 < 4, shift: [2, _, 4, 5, 6, 3]
1 < 2, shift: [_, 2, 4, 5, 6, 3]
Insert 1:     [1, 2, 4, 5, 6, 3]
               ^^^^^^^^^^^^^
                  sorted

--- Step 5: Insert 3 ---
Sorted: [1, 2, 4, 5, 6]  |  Key: 3
3 < 6, shift: [1, 2, 4, 5, _, 6]
3 < 5, shift: [1, 2, 4, _, 5, 6]
3 < 4, shift: [1, 2, _, 4, 5, 6]
3 > 2, stop
Insert 3:     [1, 2, 3, 4, 5, 6]
               ^^^^^^^^^^^^^^^^
                   sorted!
```

### Python -- Insertion Sort

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        # Shift elements greater than key to the right
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key  # Insert key at correct position

    return arr


data = [5, 2, 4, 6, 1, 3]
print(insertion_sort(data))  # Output: [1, 2, 3, 4, 5, 6]
```

### Java -- Insertion Sort

```java
import java.util.Arrays;

public class InsertionSort {
    public static void insertionSort(int[] arr) {
        for (int i = 1; i < arr.length; i++) {
            int key = arr[i];
            int j = i - 1;

            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j];
                j--;
            }

            arr[j + 1] = key;
        }
    }

    public static void main(String[] args) {
        int[] data = {5, 2, 4, 6, 1, 3};
        insertionSort(data);
        System.out.println(Arrays.toString(data));
        // Output: [1, 2, 3, 4, 5, 6]
    }
}
```

### Complexity Analysis

| Case    | Time   | Why                                                    |
|---------|--------|--------------------------------------------------------|
| Best    | O(n)   | Already sorted; inner loop never executes               |
| Average | O(n^2) | Each element compared with half the sorted portion     |
| Worst   | O(n^2) | Reverse sorted; each element shifts to the beginning   |

- **Space**: O(1) -- in-place
- **Stable**: Yes -- equal elements maintain relative order (we use `>`, not `>=`)
- **Adaptive**: Yes -- runs in O(n) on nearly sorted data
- **Online**: Can sort data as it arrives (no need to have all data upfront)

---

## 10.5 Stability Explained

A sorting algorithm is **stable** if elements with equal keys maintain their original relative order.

### Why Stability Matters

Consider sorting students by grade, where some students have the same grade:

```
Original:  [(Alice, B), (Bob, A), (Charlie, B), (Diana, A)]

Stable sort by grade:
  [(Bob, A), (Diana, A), (Alice, B), (Charlie, B)]
  Bob before Diana (original order preserved for equal grades)
  Alice before Charlie (original order preserved)

Unstable sort by grade:
  [(Diana, A), (Bob, A), (Charlie, B), (Alice, B)]
  Diana before Bob? The relative order was changed!
```

Stability matters when you sort by multiple criteria (e.g., sort by name first, then by grade -- you want the name order preserved within each grade).

### Stability of Our Three Algorithms

| Algorithm      | Stable? | Why                                        |
|----------------|---------|--------------------------------------------|
| Bubble Sort    | Yes     | Only swaps adjacent elements when `>`      |
| Selection Sort | No      | Long-range swaps can reorder equal elements|
| Insertion Sort | Yes     | Shifts (not swaps) and uses strict `>`     |

---

## 10.6 Comparison Table

| Property         | Bubble Sort | Selection Sort | Insertion Sort |
|------------------|-------------|----------------|----------------|
| Best case time   | O(n)        | O(n^2)         | O(n)           |
| Average time     | O(n^2)      | O(n^2)         | O(n^2)         |
| Worst case time  | O(n^2)      | O(n^2)         | O(n^2)         |
| Space            | O(1)        | O(1)           | O(1)           |
| Stable           | Yes         | No             | Yes            |
| Adaptive         | Yes         | No             | Yes            |
| Number of swaps  | O(n^2)      | O(n)           | O(n^2) shifts  |
| Online           | No          | No             | Yes            |
| Best for         | Teaching    | Minimal writes | Small/nearly sorted |

---

## 10.7 When Insertion Sort Is Actually Good

Despite being O(n^2), Insertion Sort is genuinely useful in these scenarios:

### 1. Nearly Sorted Data

If only a few elements are out of place, Insertion Sort runs close to O(n):

```
Nearly sorted: [1, 2, 4, 3, 5, 6, 8, 7, 9, 10]
                       ^^^^            ^^^^
                    Only 2 pairs out of order

Insertion Sort: ~12 comparisons (close to n)
Merge Sort:     ~33 comparisons (n log n regardless)
```

### 2. Small Arrays (n < ~20)

The constant factors matter for small arrays. Insertion Sort has:
- No function call overhead (unlike Merge Sort's recursion)
- No temporary array allocation
- Excellent cache performance (all operations are local)

That is why Python's `sorted()` (Timsort) and Java's `Arrays.sort()` both switch to Insertion Sort for small subarrays (typically n < 32).

### 3. Online Sorting

When data arrives one element at a time (e.g., a stream), Insertion Sort naturally handles it:

```python
sorted_data = []

def insert_into_sorted(sorted_list, new_value):
    """Insert a value into an already sorted list."""
    i = len(sorted_list) - 1
    sorted_list.append(new_value)

    while i >= 0 and sorted_list[i] > new_value:
        sorted_list[i + 1] = sorted_list[i]
        i -= 1

    sorted_list[i + 1] = new_value

# Simulating streaming data
for value in [5, 2, 8, 1, 4]:
    insert_into_sorted(sorted_data, value)
    print(sorted_data)

# Output:
# [5]
# [2, 5]
# [2, 5, 8]
# [1, 2, 5, 8]
# [1, 2, 4, 5, 8]
```

---

## 10.8 Common Mistakes

1. **Forgetting to handle the edge case of an empty or single-element array**: Both are already sorted. Your code should handle `len(arr) <= 1` gracefully (most implementations do so naturally).

2. **Off-by-one errors in loop bounds**: In Bubble Sort, the inner loop should run to `n - 1 - i` (not `n - 1`). In Insertion Sort, `j` must stop at `-1` (not `0`).

3. **Using `>=` instead of `>` in Insertion Sort**: Using `>=` breaks stability. Use strict `>` so equal elements are not unnecessarily moved.

4. **Forgetting the `swapped` optimization in Bubble Sort**: Without it, Bubble Sort always runs O(n^2) even on sorted input.

5. **Assuming O(n^2) algorithms are always useless**: Insertion Sort on nearly sorted data or small arrays can beat O(n log n) algorithms due to lower overhead.

---

## 10.9 Best Practices

1. **Use Insertion Sort for small arrays or nearly sorted data**: It outperforms complex algorithms when n is small or the data is almost in order.

2. **Never use Bubble Sort in production code**: It exists for educational purposes. Selection Sort has fewer swaps; Insertion Sort is faster in practice.

3. **Choose stable sorts when order matters**: If you need to preserve the relative order of equal elements (e.g., sorting database records), use Bubble Sort or Insertion Sort (or Merge Sort from the next chapter).

4. **Understand before memorizing**: Do not memorize the code. Understand the process (bubbling, selecting minimum, inserting into sorted portion) and you can write the code from scratch.

5. **Use the comparison table in interviews**: If asked "which O(n^2) sort is best?" the answer is almost always Insertion Sort -- it is adaptive, stable, online, and has real-world use.

---

## Quick Summary

**Bubble Sort** repeatedly compares and swaps adjacent elements until the array is sorted -- simple but slow. **Selection Sort** finds the minimum unsorted element and places it next -- minimizes swaps but is never adaptive. **Insertion Sort** builds a sorted portion by inserting each element into its correct position -- fast for small or nearly sorted data and used inside production sorting algorithms. All three are O(n^2) in the worst case and O(1) space (in-place).

---

## Key Points

- All three algorithms are O(n^2) worst case but O(1) space (in-place)
- Bubble Sort: compare and swap adjacent pairs; the largest "bubbles" to the end
- Selection Sort: find the minimum, swap it to the front; fewest swaps (O(n))
- Insertion Sort: insert each element into the sorted portion; O(n) on nearly sorted data
- Bubble Sort and Insertion Sort are stable; Selection Sort is not
- Insertion Sort is used in production (Timsort, IntroSort) for small subarrays
- The `swapped` flag in Bubble Sort gives O(n) best case on sorted input
- Stability preserves relative order of equal elements -- important for multi-key sorting

---

## Practice Questions

1. Sort the array [6, 3, 8, 2, 7, 4] using Bubble Sort. Show the state of the array after each complete pass.

2. Sort the array [15, 5, 24, 8, 1] using Selection Sort. For each pass, identify the minimum element and show the swap.

3. Sort the array [4, 3, 2, 10, 12, 1, 5] using Insertion Sort. Show the sorted portion growing after each insertion.

4. Is Selection Sort stable? Give a specific example with an array of objects (e.g., cards with suit and rank) that demonstrates why or why not.

5. You have an array of 1 million elements that is "almost sorted" -- only 10 elements are out of place. Which of the three algorithms would you choose and why? What would its approximate time complexity be?

---

## LeetCode-Style Problems

### Problem 1: Sort an Array (Fundamentals)

**Problem**: Implement each of the three sorting algorithms and verify they produce the same output.

**Python Solution**:

```python
def bubble_sort(arr):
    arr = arr[:]
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

def selection_sort(arr):
    arr = arr[:]
    n = len(arr)
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def insertion_sort(arr):
    arr = arr[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


test = [64, 34, 25, 12, 22, 11, 90]
print(bubble_sort(test))     # Output: [11, 12, 22, 25, 34, 64, 90]
print(selection_sort(test))  # Output: [11, 12, 22, 25, 34, 64, 90]
print(insertion_sort(test))  # Output: [11, 12, 22, 25, 34, 64, 90]
```

---

### Problem 2: Sort Colors (LeetCode 75) -- Selection Sort Variant

**Problem**: Given an array with values 0 (red), 1 (white), and 2 (blue), sort it in-place so that objects of the same color are adjacent, in the order red, white, blue.

**Approach**: Use the Dutch National Flag algorithm (a specialized three-way partitioning). While this is not a direct application of the three sorts, it shares the "put elements in the right place" philosophy.

**Python Solution**:

```python
def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1

    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:  # nums[mid] == 2
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
            # Do not advance mid -- need to check swapped value

    return nums


print(sort_colors([2, 0, 2, 1, 1, 0]))  # Output: [0, 0, 1, 1, 2, 2]
print(sort_colors([2, 0, 1]))            # Output: [0, 1, 2]
```

**Java Solution**:

```java
import java.util.Arrays;

public class SortColors {
    public static void sortColors(int[] nums) {
        int low = 0, mid = 0, high = nums.length - 1;

        while (mid <= high) {
            if (nums[mid] == 0) {
                int temp = nums[low];
                nums[low] = nums[mid];
                nums[mid] = temp;
                low++;
                mid++;
            } else if (nums[mid] == 1) {
                mid++;
            } else {
                int temp = nums[mid];
                nums[mid] = nums[high];
                nums[high] = temp;
                high--;
            }
        }
    }

    public static void main(String[] args) {
        int[] nums = {2, 0, 2, 1, 1, 0};
        sortColors(nums);
        System.out.println(Arrays.toString(nums));
        // Output: [0, 0, 1, 1, 2, 2]
    }
}
```

**Complexity**: Time: O(n) -- single pass. Space: O(1).

---

### Problem 3: Counting Inversions (Interview Classic)

**Problem**: Count the number of inversions in an array. An inversion is a pair (i, j) where i < j but arr[i] > arr[j]. This measures how "unsorted" an array is.

**Approach**: Use a modified Insertion Sort. Each time an element is shifted right, it represents one inversion.

```
Array: [2, 4, 1, 3, 5]

Inserting 4: no shifts (4 > 2)         -> 0 inversions
Inserting 1: shift 4, shift 2          -> 2 inversions (4>1, 2>1)
Inserting 3: shift 4                   -> 1 inversion  (4>3)
Inserting 5: no shifts                 -> 0 inversions

Total inversions: 3
Pairs: (2,1), (4,1), (4,3)
```

**Python Solution**:

```python
def count_inversions_insertion(arr):
    arr = arr[:]
    inversions = 0

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            inversions += 1  # Each shift = one inversion
            j -= 1

        arr[j + 1] = key

    return inversions


print(count_inversions_insertion([2, 4, 1, 3, 5]))  # Output: 3
print(count_inversions_insertion([5, 4, 3, 2, 1]))  # Output: 10 (max for n=5)
print(count_inversions_insertion([1, 2, 3, 4, 5]))  # Output: 0 (already sorted)
```

**Java Solution**:

```java
public class CountInversions {
    public static int countInversions(int[] arr) {
        int[] copy = arr.clone();
        int inversions = 0;

        for (int i = 1; i < copy.length; i++) {
            int key = copy[i];
            int j = i - 1;

            while (j >= 0 && copy[j] > key) {
                copy[j + 1] = copy[j];
                inversions++;
                j--;
            }

            copy[j + 1] = key;
        }

        return inversions;
    }

    public static void main(String[] args) {
        System.out.println(countInversions(new int[]{2, 4, 1, 3, 5}));
        // Output: 3
    }
}
```

**Complexity**: Time: O(n^2) with Insertion Sort. (Note: Merge Sort can count inversions in O(n log n) -- see next chapter.)

---

## What Is Next?

The O(n^2) sorts you learned in this chapter work well for small inputs but become painfully slow as data grows. In the next chapter, we study **Merge Sort** and **Quick Sort** -- two divide-and-conquer algorithms that achieve O(n log n) average-case performance, making them practical for sorting millions of elements. You will see how recursion (Chapter 9) powers these algorithms and why Quick Sort is the default choice in most standard libraries.
