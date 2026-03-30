# Chapter 11: Sorting -- Merge Sort and Quick Sort

## What You Will Learn

- How Merge Sort uses divide and conquer to sort in O(n log n)
- Step-by-step ASCII walkthrough of the split-and-merge process
- How Quick Sort partitions around a pivot to sort in O(n log n) average
- ASCII walkthrough of the partition scheme
- Why Quick Sort has O(n^2) worst case and how pivot selection fixes it
- The difference between in-place and not-in-place sorting
- A comprehensive comparison of all sorting algorithms
- How Python's `sorted()` and Java's `Arrays.sort()` work internally

## Why This Chapter Matters

The O(n^2) algorithms from Chapter 10 work for small inputs but become impractical for large datasets. Sorting a million elements with Insertion Sort takes roughly a trillion operations. Merge Sort and Quick Sort, both at O(n log n) average, handle the same million elements in about 20 million operations -- a 50,000x speedup.

These two algorithms are the workhorses of real-world sorting. Merge Sort guarantees O(n log n) in all cases and is the basis for external sorting (sorting data too large to fit in memory). Quick Sort is typically faster in practice due to better cache behavior and lower constant factors, which is why it (or its variants) powers most standard library sort implementations.

---

## 11.1 Merge Sort

### The Idea: Divide and Conquer

Merge Sort follows three steps:

1. **Divide**: Split the array into two halves
2. **Conquer**: Recursively sort each half
3. **Combine**: Merge the two sorted halves into one sorted array

The key insight is that merging two already-sorted arrays is easy and fast -- O(n).

### ASCII Walkthrough: Splitting Phase

```
Original: [38, 27, 43, 3, 9, 82, 10]

                 [38, 27, 43, 3, 9, 82, 10]
                /                            \
        [38, 27, 43, 3]              [9, 82, 10]
        /            \                /         \
    [38, 27]      [43, 3]        [9, 82]      [10]
    /     \       /     \        /     \         |
  [38]   [27]  [43]    [3]    [9]    [82]      [10]
```

Each single element is a sorted array (base case).

### ASCII Walkthrough: Merging Phase

```
Merge [38] and [27]:
  Compare 38, 27 -> take 27, then take 38 -> [27, 38]

Merge [43] and [3]:
  Compare 43, 3 -> take 3, then take 43 -> [3, 43]

Merge [9] and [82]:
  Compare 9, 82 -> take 9, then take 82 -> [9, 82]

Merge [27, 38] and [3, 43]:
  Compare 27, 3 -> take 3
  Compare 27, 43 -> take 27
  Compare 38, 43 -> take 38
  Take remaining 43
  Result: [3, 27, 38, 43]

Merge [9, 82] and [10]:
  Compare 9, 10 -> take 9
  Compare 82, 10 -> take 10
  Take remaining 82
  Result: [9, 10, 82]

Merge [3, 27, 38, 43] and [9, 10, 82]:
  Compare 3, 9   -> take 3
  Compare 27, 9  -> take 9
  Compare 27, 10 -> take 10
  Compare 27, 82 -> take 27
  Compare 38, 82 -> take 38
  Compare 43, 82 -> take 43
  Take remaining 82
  Result: [3, 9, 10, 27, 38, 43, 82]
```

### How Merging Works (Detailed)

```
Merge [3, 27, 38] and [9, 10, 43]:

Left:    [3, 27, 38]     Right:  [9, 10, 43]
          ^                        ^
          i                        j

Step 1: 3 < 9  -> result = [3],          i++
Step 2: 27 > 9 -> result = [3, 9],       j++
Step 3: 27 > 10 -> result = [3, 9, 10],  j++
Step 4: 27 < 43 -> result = [3, 9, 10, 27],   i++
Step 5: 38 < 43 -> result = [3, 9, 10, 27, 38], i++
Step 6: Left exhausted, append remaining right:
        result = [3, 9, 10, 27, 38, 43]
```

### Python -- Merge Sort

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr  # Base case

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])     # Sort left half
    right = merge_sort(arr[mid:])    # Sort right half

    return merge(left, right)


def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= ensures stability
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Append remaining elements
    result.extend(left[i:])
    result.extend(right[j:])

    return result


data = [38, 27, 43, 3, 9, 82, 10]
print(merge_sort(data))  # Output: [3, 9, 10, 27, 38, 43, 82]
```

### Java -- Merge Sort

```java
import java.util.Arrays;

public class MergeSort {
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
            if (left[i] <= right[j]) {
                result[k++] = left[i++];
            } else {
                result[k++] = right[j++];
            }
        }

        while (i < left.length) result[k++] = left[i++];
        while (j < right.length) result[k++] = right[j++];

        return result;
    }

    public static void main(String[] args) {
        int[] data = {38, 27, 43, 3, 9, 82, 10};
        System.out.println(Arrays.toString(mergeSort(data)));
        // Output: [3, 9, 10, 27, 38, 43, 82]
    }
}
```

### Merge Sort Complexity

| Case    | Time       | Why                                          |
|---------|------------|----------------------------------------------|
| Best    | O(n log n) | Always splits and merges, regardless of input|
| Average | O(n log n) | Same as best                                 |
| Worst   | O(n log n) | Same as best -- always guaranteed             |

- **Space**: O(n) -- requires a temporary array for merging
- **Stable**: Yes -- uses `<=` when comparing, so equal elements maintain order
- **Not in-place**: Requires O(n) extra memory

### Why O(n log n)?

```
Level 0: 1 array  of size n          -> n work to merge
Level 1: 2 arrays of size n/2        -> n work to merge
Level 2: 4 arrays of size n/4        -> n work to merge
...
Level k: 2^k arrays of size n/2^k    -> n work to merge

Total levels: log2(n)
Total work: n * log2(n) = O(n log n)

         [n elements]              <- n work
        /            \
   [n/2]              [n/2]        <- n work
   /    \              /    \
[n/4]  [n/4]       [n/4]  [n/4]   <- n work

log n levels x n work per level = O(n log n)
```

---

## 11.2 Quick Sort

### The Idea: Partition and Conquer

Quick Sort works differently from Merge Sort:

1. **Choose a pivot**: Pick one element from the array
2. **Partition**: Rearrange the array so all elements smaller than the pivot are on the left and all elements larger are on the right
3. **Recurse**: Apply Quick Sort to the left and right partitions

Unlike Merge Sort, the "hard work" happens in the partition step, and no merging is needed afterward.

### ASCII Walkthrough: Partition

```
Array: [8, 3, 5, 1, 9, 2, 7, 4]
Pivot: 4 (choosing last element)

Goal: Everything < 4 goes left, everything >= 4 goes right

i = -1 (boundary of the "less than pivot" section)
j scans from left to right:

j=0: arr[0]=8 >= 4 -> skip            [8, 3, 5, 1, 9, 2, 7, 4]  i=-1
j=1: arr[1]=3 < 4  -> i=0, swap(0,1)  [3, 8, 5, 1, 9, 2, 7, 4]  i=0
j=2: arr[2]=5 >= 4 -> skip            [3, 8, 5, 1, 9, 2, 7, 4]  i=0
j=3: arr[3]=1 < 4  -> i=1, swap(1,3)  [3, 1, 5, 8, 9, 2, 7, 4]  i=1
j=4: arr[4]=9 >= 4 -> skip            [3, 1, 5, 8, 9, 2, 7, 4]  i=1
j=5: arr[5]=2 < 4  -> i=2, swap(2,5)  [3, 1, 2, 8, 9, 5, 7, 4]  i=2
j=6: arr[6]=7 >= 4 -> skip            [3, 1, 2, 8, 9, 5, 7, 4]  i=2

Place pivot: swap(i+1, pivot)          [3, 1, 2, 4, 9, 5, 7, 8]
                                              ^
                                           pivot in correct position!

Left of pivot:  [3, 1, 2]  (all < 4)
Right of pivot: [9, 5, 7, 8]  (all >= 4)
```

### Full Quick Sort Walkthrough

```
[8, 3, 5, 1, 9, 2, 7, 4]

Step 1: Partition around 4
  [3, 1, 2] | 4 | [9, 5, 7, 8]

Step 2: Partition [3, 1, 2] around 2
  [1] | 2 | [3]

Step 3: Partition [9, 5, 7, 8] around 8
  [5, 7] | 8 | [9]

Step 4: Partition [5, 7] around 7
  [5] | 7

Final: [1, 2, 3, 4, 5, 7, 8, 9]
```

### Python -- Quick Sort

```python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr  # Base case

    pivot = arr[-1]
    left = [x for x in arr[:-1] if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr[:-1] if x > pivot]

    return quick_sort(left) + middle + quick_sort(right)


data = [8, 3, 5, 1, 9, 2, 7, 4]
print(quick_sort(data))  # Output: [1, 2, 3, 4, 5, 7, 8, 9]
```

### Python -- Quick Sort (In-Place, Lomuto Partition)

```python
def quick_sort_inplace(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1

    if low < high:
        pivot_index = partition(arr, low, high)
        quick_sort_inplace(arr, low, pivot_index - 1)
        quick_sort_inplace(arr, pivot_index + 1, high)


def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


data = [8, 3, 5, 1, 9, 2, 7, 4]
quick_sort_inplace(data)
print(data)  # Output: [1, 2, 3, 4, 5, 7, 8, 9]
```

### Java -- Quick Sort (In-Place)

```java
import java.util.Arrays;

public class QuickSort {
    public static void quickSort(int[] arr, int low, int high) {
        if (low < high) {
            int pivotIndex = partition(arr, low, high);
            quickSort(arr, low, pivotIndex - 1);
            quickSort(arr, pivotIndex + 1, high);
        }
    }

    private static int partition(int[] arr, int low, int high) {
        int pivot = arr[high];
        int i = low - 1;

        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }

        int temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;

        return i + 1;
    }

    public static void main(String[] args) {
        int[] data = {8, 3, 5, 1, 9, 2, 7, 4};
        quickSort(data, 0, data.length - 1);
        System.out.println(Arrays.toString(data));
        // Output: [1, 2, 3, 4, 5, 7, 8, 9]
    }
}
```

### Quick Sort Complexity

| Case    | Time       | When it happens                                |
|---------|------------|------------------------------------------------|
| Best    | O(n log n) | Pivot always splits the array in half          |
| Average | O(n log n) | Random pivots give balanced-enough partitions  |
| Worst   | O(n^2)     | Pivot is always the min or max (sorted input!) |

- **Space**: O(log n) average for the call stack; O(n) worst case
- **Stable**: No -- partition swaps can change relative order of equal elements
- **In-place**: Yes (Lomuto or Hoare partition) -- only O(log n) extra for the stack

### Why O(n^2) Worst Case?

When the pivot is always the smallest or largest element, partitioning produces one empty subarray and one of size n-1:

```
Worst case: already sorted array [1, 2, 3, 4, 5] with last element as pivot

Partition around 5:  [1,2,3,4] | 5 | []     <- n-1 elements left
Partition around 4:  [1,2,3] | 4 | []       <- n-2 elements left
Partition around 3:  [1,2] | 3 | []         <- n-3 elements left
Partition around 2:  [1] | 2 | []

Total work: n + (n-1) + (n-2) + ... + 1 = O(n^2)
```

---

## 11.3 Pivot Selection Strategies

The pivot choice determines Quick Sort's performance. Here are the main strategies:

### Strategy 1: Last Element (Basic)

```python
pivot = arr[high]
```
Simple but vulnerable to sorted/nearly sorted input (O(n^2) worst case).

### Strategy 2: Random Pivot

```python
import random

def partition_random(arr, low, high):
    rand_index = random.randint(low, high)
    arr[rand_index], arr[high] = arr[high], arr[rand_index]
    return partition(arr, low, high)  # Then use normal partition
```
Makes the worst case extremely unlikely (expected O(n log n) for any input).

### Strategy 3: Median of Three

Pick three elements (first, middle, last), use the median as the pivot:

```python
def median_of_three(arr, low, high):
    mid = (low + high) // 2
    # Sort the three elements
    if arr[low] > arr[mid]:
        arr[low], arr[mid] = arr[mid], arr[low]
    if arr[low] > arr[high]:
        arr[low], arr[high] = arr[high], arr[low]
    if arr[mid] > arr[high]:
        arr[mid], arr[high] = arr[high], arr[mid]
    # Median is now at mid; swap to high-1 for partitioning
    arr[mid], arr[high] = arr[high], arr[mid]
    return arr[high]
```
Avoids worst case on sorted input. Used by many standard libraries.

---

## 11.4 In-Place vs Not In-Place

| Aspect        | In-Place           | Not In-Place          |
|---------------|--------------------|-----------------------|
| Extra memory  | O(1) or O(log n)   | O(n)                  |
| Examples      | Quick Sort         | Merge Sort            |
| Trade-off     | Harder to implement| Simpler, often stable |

Merge Sort needs O(n) extra space for the temporary arrays during merging. Quick Sort (with Lomuto/Hoare partition) sorts within the original array, using only O(log n) stack space.

---

## 11.5 Comprehensive Sorting Algorithm Comparison

| Algorithm       | Best       | Average    | Worst      | Space  | Stable | In-Place |
|-----------------|------------|------------|------------|--------|--------|----------|
| Bubble Sort     | O(n)       | O(n^2)     | O(n^2)     | O(1)   | Yes    | Yes      |
| Selection Sort  | O(n^2)     | O(n^2)     | O(n^2)     | O(1)   | No     | Yes      |
| Insertion Sort  | O(n)       | O(n^2)     | O(n^2)     | O(1)   | Yes    | Yes      |
| Merge Sort      | O(n log n) | O(n log n) | O(n log n) | O(n)   | Yes    | No       |
| Quick Sort      | O(n log n) | O(n log n) | O(n^2)     | O(log n)| No    | Yes      |
| Heap Sort       | O(n log n) | O(n log n) | O(n log n) | O(1)   | No     | Yes      |
| Timsort         | O(n)       | O(n log n) | O(n log n) | O(n)   | Yes    | No       |

### When to Use Which

| Scenario                          | Best Algorithm    | Why                              |
|-----------------------------------|-------------------|----------------------------------|
| Small array (n < 20)              | Insertion Sort    | Low overhead, fast for small n   |
| Nearly sorted data                | Insertion Sort    | O(n) best case, adaptive         |
| Need guaranteed O(n log n)        | Merge Sort        | No worst case degradation        |
| General purpose, in-place         | Quick Sort        | Fastest on average, cache-friendly|
| Stability required                | Merge Sort        | Stable O(n log n)                |
| External sorting (large files)    | Merge Sort        | Sequential access pattern        |
| Memory constrained                | Quick Sort        | O(log n) space vs O(n)           |

---

## 11.6 How Python sorted() and Java Arrays.sort() Work

### Python: Timsort

Python uses **Timsort** (invented by Tim Peters in 2002), a hybrid of Merge Sort and Insertion Sort:

1. Scan the array for existing sorted "runs" (ascending or descending sequences)
2. If a run is shorter than a minimum (typically 32), extend it using Insertion Sort
3. Merge runs using a modified Merge Sort with smart merge ordering

```python
# Python's built-in sort is Timsort
data = [38, 27, 43, 3, 9, 82, 10]
print(sorted(data))       # Output: [3, 9, 10, 27, 38, 43, 82]
data.sort()               # In-place sort (also Timsort)

# Timsort is stable
students = [("Alice", 85), ("Bob", 90), ("Charlie", 85)]
students.sort(key=lambda x: x[1])
print(students)
# Output: [('Alice', 85), ('Charlie', 85), ('Bob', 90)]
# Alice stays before Charlie (stable)
```

**Properties**: O(n log n) worst case, O(n) best case (already sorted), stable, O(n) space.

### Java: Dual-Pivot Quick Sort and Timsort

Java uses different algorithms depending on the data type:

- **Primitive arrays** (`int[]`, `double[]`): **Dual-Pivot Quick Sort** -- uses two pivots to create three partitions, reducing comparisons. Falls back to Insertion Sort for small subarrays.

- **Object arrays** (`Integer[]`, `String[]`): **Timsort** -- same algorithm as Python. Stability matters for objects because you might sort by multiple fields.

```java
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class JavaSortDemo {
    public static void main(String[] args) {
        // Primitive array -> Dual-Pivot Quick Sort
        int[] primitives = {38, 27, 43, 3, 9, 82, 10};
        Arrays.sort(primitives);
        System.out.println(Arrays.toString(primitives));
        // Output: [3, 9, 10, 27, 38, 43, 82]

        // Object array -> Timsort (stable)
        String[] words = {"banana", "apple", "cherry"};
        Arrays.sort(words);
        System.out.println(Arrays.toString(words));
        // Output: [apple, banana, cherry]

        // Custom comparator
        Integer[] nums = {3, 1, 4, 1, 5, 9};
        Arrays.sort(nums, Collections.reverseOrder());
        System.out.println(Arrays.toString(nums));
        // Output: [9, 5, 4, 3, 1, 1]
    }
}
```

---

## 11.7 Common Mistakes

1. **Choosing the last element as pivot on sorted data**: This gives O(n^2) for Quick Sort. Use random pivot or median-of-three.

2. **Forgetting the base case in recursive sorts**: Both Merge Sort and Quick Sort need `if len(arr) <= 1: return` (or `if low >= high: return`).

3. **Not copying when necessary**: In Python, `arr[:mid]` creates a copy. If you forget to copy, you may accidentally modify the original array during merging.

4. **Using `<` instead of `<=` in merge**: Using `<` instead of `<=` when comparing elements in the merge step breaks stability. Equal elements from the left array should come first.

5. **Stack overflow with Quick Sort on large sorted arrays**: If the pivot selection is poor, recursion depth can reach n. Use iterative Quick Sort or tail-call optimization for production code.

---

## 11.8 Best Practices

1. **Use built-in sort functions**: `sorted()` in Python and `Arrays.sort()` in Java are extremely optimized. Only implement your own sort for learning or specialized needs.

2. **Choose Merge Sort when stability matters**: It is the only O(n log n) sort that is guaranteed stable.

3. **Use Quick Sort with randomized pivot**: This ensures expected O(n log n) regardless of input distribution.

4. **Switch to Insertion Sort for small partitions**: When Quick Sort or Merge Sort recurses to a subarray of size < 16-32, switch to Insertion Sort for better constant factors.

5. **For interviews, know the trade-offs**: Be able to discuss when Merge Sort is better than Quick Sort (stability, guaranteed O(n log n)) and vice versa (in-place, better cache performance).

---

## Quick Summary

**Merge Sort** divides the array in half, recursively sorts each half, and merges the sorted halves. It guarantees O(n log n) in all cases, is stable, but requires O(n) extra space. **Quick Sort** picks a pivot, partitions the array around it, and recursively sorts the partitions. It averages O(n log n) and is in-place, but has O(n^2) worst case with bad pivot choices. Python uses Timsort (Merge Sort + Insertion Sort hybrid). Java uses Dual-Pivot Quick Sort for primitives and Timsort for objects.

---

## Key Points

- Merge Sort: always O(n log n), stable, O(n) space, not in-place
- Quick Sort: O(n log n) average, O(n^2) worst case, not stable, in-place
- Merge Sort splits first, then merges; Quick Sort partitions first, then recurses
- Bad pivot selection causes Quick Sort's worst case -- use random or median-of-three
- Merge Sort is best for external sorting and when stability is required
- Quick Sort is best for in-memory sorting with good cache performance
- Python's `sorted()` uses Timsort; Java's `Arrays.sort()` uses Dual-Pivot Quick Sort for primitives
- Both real-world implementations fall back to Insertion Sort for small subarrays

---

## Practice Questions

1. Sort the array [6, 5, 3, 1, 8, 7, 2, 4] using Merge Sort. Draw the complete split tree and then show each merge step.

2. Partition the array [10, 7, 8, 9, 1, 5] using the last element (5) as the pivot. Show the state of the array after each comparison.

3. Why does Quick Sort have O(n^2) worst case while Merge Sort is always O(n log n)? What input causes Quick Sort's worst case when using the last element as pivot?

4. You need to sort 10 million records of student data by grade, and students with the same grade must maintain their original order. Which algorithm do you choose and why?

5. Why does Java use different sorting algorithms for primitive arrays vs object arrays?

---

## LeetCode-Style Problems

### Problem 1: Sort an Array (LeetCode 912)

**Problem**: Implement a sorting algorithm to sort an array. (This is a great practice problem for implementing Merge Sort or Quick Sort from scratch.)

**Python Solution (Merge Sort)**:

```python
def sort_array(nums):
    if len(nums) <= 1:
        return nums

    mid = len(nums) // 2
    left = sort_array(nums[:mid])
    right = sort_array(nums[mid:])

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


print(sort_array([5, 2, 3, 1]))  # Output: [1, 2, 3, 5]
print(sort_array([5, 1, 1, 2, 0, 0]))  # Output: [0, 0, 1, 1, 2, 5]
```

**Java Solution (Quick Sort with Random Pivot)**:

```java
import java.util.*;

public class SortArray {
    private static Random rand = new Random();

    public static int[] sortArray(int[] nums) {
        quickSort(nums, 0, nums.length - 1);
        return nums;
    }

    private static void quickSort(int[] arr, int low, int high) {
        if (low < high) {
            int pivotIdx = partition(arr, low, high);
            quickSort(arr, low, pivotIdx - 1);
            quickSort(arr, pivotIdx + 1, high);
        }
    }

    private static int partition(int[] arr, int low, int high) {
        // Random pivot to avoid worst case
        int randIdx = low + rand.nextInt(high - low + 1);
        int temp = arr[randIdx];
        arr[randIdx] = arr[high];
        arr[high] = temp;

        int pivot = arr[high];
        int i = low - 1;

        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }

        temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;

        return i + 1;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(sortArray(new int[]{5, 2, 3, 1})));
        // Output: [1, 2, 3, 5]
    }
}
```

**Complexity**: Merge Sort: O(n log n) time, O(n) space. Quick Sort: O(n log n) average time, O(log n) space.

---

### Problem 2: Merge Sorted Arrays (LeetCode 88)

**Problem**: Given two sorted integer arrays `nums1` and `nums2`, merge `nums2` into `nums1` in-place. `nums1` has enough space at the end to hold the merged result.

**Approach**: Merge from the end. Use three pointers: one at the end of nums1's values, one at the end of nums2, and one at the true end of nums1. This avoids overwriting values we still need.

```
nums1 = [1, 2, 3, 0, 0, 0], m = 3
nums2 = [2, 5, 6],           n = 3

Merge from the end:
  p1=2(val 3), p2=2(val 6), p=5: 6>3, place 6 at index 5
  p1=2(val 3), p2=1(val 5), p=4: 5>3, place 5 at index 4
  p1=2(val 3), p2=0(val 2), p=3: 3>2, place 3 at index 3
  p1=1(val 2), p2=0(val 2), p=2: 2>=2, place 2 at index 2
  p1=0(val 1), p2=-1,       p=1: copy remaining nums1

Result: [1, 2, 2, 3, 5, 6]
```

**Python Solution**:

```python
def merge(nums1, m, nums2, n):
    p1 = m - 1
    p2 = n - 1
    p = m + n - 1

    while p1 >= 0 and p2 >= 0:
        if nums1[p1] > nums2[p2]:
            nums1[p] = nums1[p1]
            p1 -= 1
        else:
            nums1[p] = nums2[p2]
            p2 -= 1
        p -= 1

    # Copy remaining elements from nums2 (if any)
    nums1[:p2 + 1] = nums2[:p2 + 1]


nums1 = [1, 2, 3, 0, 0, 0]
merge(nums1, 3, [2, 5, 6], 3)
print(nums1)  # Output: [1, 2, 2, 3, 5, 6]
```

**Java Solution**:

```java
public class MergeSortedArrays {
    public static void merge(int[] nums1, int m, int[] nums2, int n) {
        int p1 = m - 1;
        int p2 = n - 1;
        int p = m + n - 1;

        while (p1 >= 0 && p2 >= 0) {
            if (nums1[p1] > nums2[p2]) {
                nums1[p--] = nums1[p1--];
            } else {
                nums1[p--] = nums2[p2--];
            }
        }

        while (p2 >= 0) {
            nums1[p--] = nums2[p2--];
        }
    }

    public static void main(String[] args) {
        int[] nums1 = {1, 2, 3, 0, 0, 0};
        merge(nums1, 3, new int[]{2, 5, 6}, 3);
        System.out.println(java.util.Arrays.toString(nums1));
        // Output: [1, 2, 2, 3, 5, 6]
    }
}
```

**Complexity**: Time: O(m + n). Space: O(1).

---

### Problem 3: Kth Largest Element (LeetCode 215)

**Problem**: Find the kth largest element in an unsorted array. For example, in [3,2,1,5,6,4] and k=2, the answer is 5.

**Approach**: Use Quick Select -- a modified Quick Sort that only recurses into the partition containing the target index. Average O(n), worst O(n^2).

```
[3, 2, 1, 5, 6, 4], k = 2
Target index (0-based, for kth largest): n - k = 6 - 2 = 4

Partition around pivot 4:
  [3, 2, 1] | 4 | [5, 6]
  Pivot at index 3, target is index 4 -> search right partition

Partition [5, 6] around 6:
  [5] | 6
  Pivot at index 5, target is index 4 -> search left partition

Only [5] left -> answer is 5
```

**Python Solution**:

```python
import random

def find_kth_largest(nums, k):
    target = len(nums) - k  # Convert to index of kth largest

    def quick_select(left, right):
        # Random pivot
        pivot_idx = random.randint(left, right)
        nums[pivot_idx], nums[right] = nums[right], nums[pivot_idx]

        pivot = nums[right]
        store = left

        for i in range(left, right):
            if nums[i] < pivot:
                nums[store], nums[i] = nums[i], nums[store]
                store += 1

        nums[store], nums[right] = nums[right], nums[store]

        if store == target:
            return nums[store]
        elif store < target:
            return quick_select(store + 1, right)
        else:
            return quick_select(left, store - 1)

    return quick_select(0, len(nums) - 1)


print(find_kth_largest([3, 2, 1, 5, 6, 4], 2))  # Output: 5
print(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))  # Output: 4
```

**Java Solution**:

```java
import java.util.Random;

public class KthLargest {
    private static Random rand = new Random();

    public static int findKthLargest(int[] nums, int k) {
        int target = nums.length - k;
        return quickSelect(nums, 0, nums.length - 1, target);
    }

    private static int quickSelect(int[] nums, int left, int right, int target) {
        int pivotIdx = left + rand.nextInt(right - left + 1);
        int temp = nums[pivotIdx];
        nums[pivotIdx] = nums[right];
        nums[right] = temp;

        int pivot = nums[right];
        int store = left;

        for (int i = left; i < right; i++) {
            if (nums[i] < pivot) {
                temp = nums[store];
                nums[store] = nums[i];
                nums[i] = temp;
                store++;
            }
        }

        temp = nums[store];
        nums[store] = nums[right];
        nums[right] = temp;

        if (store == target) return nums[store];
        else if (store < target) return quickSelect(nums, store + 1, right, target);
        else return quickSelect(nums, left, store - 1, target);
    }

    public static void main(String[] args) {
        System.out.println(findKthLargest(new int[]{3, 2, 1, 5, 6, 4}, 2));
        // Output: 5
    }
}
```

**Complexity**: Time: O(n) average, O(n^2) worst case. Space: O(1) (in-place partitioning, tail recursion can be optimized to iterative).

---

## What Is Next?

With sorting under your belt, you are ready for one of the most powerful applications of sorted data: **Binary Search**. In the next chapter, you will learn how to search a sorted array in O(log n) time -- cutting the search space in half with every step. Binary search is deceptively simple in concept but notoriously tricky in implementation, and it is one of the most frequently tested topics in coding interviews.
