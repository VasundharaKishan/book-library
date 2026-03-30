# Chapter 3: Arrays

## What You Will Learn

- What arrays are and how they are stored in memory
- Why array access is O(1) and how memory addressing works
- The cost of insertion, deletion, and searching in arrays
- How dynamic arrays (Python list, Java ArrayList) grow automatically
- Common array operations and patterns
- How to solve classic problems: Two Sum, Rotate Array, and Maximum Subarray (Kadane's Algorithm)
- Differences between Python lists and Java ArrayLists

## Why This Chapter Matters

Arrays are the bedrock of programming. Nearly every other data structure is built on top of arrays or exists to solve a problem that arrays handle poorly. When an interviewer says "Given an array...", they are testing whether you understand the most fundamental data structure in computer science. Master arrays and you have a foundation for everything that follows.

---

## 3.1 What Is an Array?

An array is a **contiguous block of memory** that stores elements of the same type in numbered positions. Think of it like a row of numbered lockers in a school hallway.

```
    ARRAY = A ROW OF NUMBERED LOCKERS

    Index:   0     1     2     3     4     5
          +-----+-----+-----+-----+-----+-----+
          | 10  | 20  | 30  | 40  | 50  | 60  |
          +-----+-----+-----+-----+-----+-----+

    - Each locker has a NUMBER (index), starting from 0.
    - Each locker holds ONE item (value).
    - All lockers are the SAME SIZE.
    - All lockers are RIGHT NEXT TO EACH OTHER (contiguous).
```

### Key Properties

1. **Fixed size** (in traditional arrays): You decide the number of lockers when you build the hallway. You cannot add more lockers without building a new hallway.
2. **Zero-indexed**: The first element is at index 0, not index 1.
3. **Contiguous memory**: Elements sit side by side in memory with no gaps.
4. **Homogeneous**: All elements are the same type (in statically typed languages like Java).

---

## 3.2 Memory Layout: Why O(1) Access

The magic of arrays is **instant access to any element**. Here is why.

When you create an array, the computer allocates a contiguous block of memory. Each element takes the same number of bytes. To find any element, the computer uses simple arithmetic:

```
    Memory Address of element[i] = base_address + (i * element_size)

    Example: Array of integers (4 bytes each), starting at address 1000

    Index:    0      1      2      3      4      5
    Address: 1000   1004   1008   1012   1016   1020
          +------+------+------+------+------+------+
          |  10  |  20  |  30  |  40  |  50  |  60  |
          +------+------+------+------+------+------+

    Want element[3]?
    Address = 1000 + (3 * 4) = 1012  --> Go directly to 1012 --> 40
    No scanning needed!  This is O(1).
```

This is why accessing `arr[3]` is instant -- the computer does one multiplication and one addition, regardless of whether the array has 10 elements or 10 million.

---

## 3.3 Array Operations and Their Complexity

### Access -- O(1)

Reading or writing an element by index is constant time.

**Python**:
```python
arr = [10, 20, 30, 40, 50]

# Access (read) -- O(1)
print(arr[2])      # Output: 30

# Modify (write) -- O(1)
arr[2] = 99
print(arr[2])      # Output: 99
print(arr)          # Output: [10, 20, 99, 40, 50]
```

**Java**:
```java
public class ArrayAccess {
    public static void main(String[] args) {
        int[] arr = {10, 20, 30, 40, 50};

        // Access -- O(1)
        System.out.println(arr[2]);      // Output: 30

        // Modify -- O(1)
        arr[2] = 99;
        System.out.println(arr[2]);      // Output: 99
    }
}
```

**Output**:
```
30
99
```

---

### Search -- O(n)

To find a value (not by index), you must check each element one at a time.

```
    Searching for 40 in [10, 20, 30, 40, 50]

    Check index 0: 10 == 40? No.
    Check index 1: 20 == 40? No.
    Check index 2: 30 == 40? No.
    Check index 3: 40 == 40? Yes! Found at index 3.

    Worst case: element is at the end or not present --> O(n)
```

**Python**:
```python
def linear_search(arr, target):
    """O(n) -- check each element."""
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

# Test
print(linear_search([10, 20, 30, 40, 50], 40))   # Output: 3
print(linear_search([10, 20, 30, 40, 50], 99))   # Output: -1
```

**Java**:
```java
public class LinearSearch {
    public static int linearSearch(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) return i;
        }
        return -1;
    }

    public static void main(String[] args) {
        System.out.println(linearSearch(new int[]{10,20,30,40,50}, 40)); // 3
        System.out.println(linearSearch(new int[]{10,20,30,40,50}, 99)); // -1
    }
}
```

**Output**:
```
3
-1
```

---

### Insert -- O(n)

Inserting an element in the middle requires shifting all subsequent elements to make room.

```
    Insert 25 at index 2 in [10, 20, 30, 40, 50]

    Step 1: Shift elements right to make room
    [10, 20, 30, 40, 50, _ ]
    [10, 20, 30, 40, _ , 50]    shift 50
    [10, 20, 30, _ , 40, 50]    shift 40
    [10, 20, _ , 30, 40, 50]    shift 30

    Step 2: Place 25 at index 2
    [10, 20, 25, 30, 40, 50]

    Shifted 3 elements. Worst case (insert at index 0): shift ALL n elements.
    Time: O(n)
```

**Python**:
```python
# Python lists handle this internally
arr = [10, 20, 30, 40, 50]
arr.insert(2, 25)       # Insert 25 at index 2
print(arr)               # Output: [10, 20, 25, 30, 40, 50]

# Insert at end (append) -- O(1) amortized
arr.append(60)
print(arr)               # Output: [10, 20, 25, 30, 40, 50, 60]
```

**Java**:
```java
import java.util.ArrayList;

public class ArrayInsert {
    public static void main(String[] args) {
        ArrayList<Integer> arr = new ArrayList<>();
        for (int x : new int[]{10, 20, 30, 40, 50}) arr.add(x);

        arr.add(2, 25);      // Insert 25 at index 2 -- O(n)
        System.out.println(arr); // [10, 20, 25, 30, 40, 50]

        arr.add(60);          // Append to end -- O(1) amortized
        System.out.println(arr); // [10, 20, 25, 30, 40, 50, 60]
    }
}
```

**Output**:
```
[10, 20, 25, 30, 40, 50]
[10, 20, 25, 30, 40, 50, 60]
```

---

### Delete -- O(n)

Deleting an element in the middle requires shifting all subsequent elements to fill the gap.

```
    Delete element at index 2 from [10, 20, 30, 40, 50]

    Step 1: Remove element at index 2
    [10, 20, _ , 40, 50]

    Step 2: Shift elements left to fill the gap
    [10, 20, 40, _ , 50]    shift 40 left
    [10, 20, 40, 50, _ ]    shift 50 left

    Result: [10, 20, 40, 50]

    Worst case (delete index 0): shift ALL remaining elements.
    Time: O(n)
```

**Python**:
```python
arr = [10, 20, 30, 40, 50]

# Delete by index -- O(n)
arr.pop(2)             # Remove element at index 2
print(arr)              # Output: [10, 20, 40, 50]

# Delete from end -- O(1)
arr.pop()              # Remove last element
print(arr)              # Output: [10, 20, 40]

# Delete by value -- O(n) (search + shift)
arr = [10, 20, 30, 40, 50]
arr.remove(30)          # Find and remove 30
print(arr)              # Output: [10, 20, 40, 50]
```

**Java**:
```java
import java.util.ArrayList;

public class ArrayDelete {
    public static void main(String[] args) {
        ArrayList<Integer> arr = new ArrayList<>();
        for (int x : new int[]{10, 20, 30, 40, 50}) arr.add(x);

        arr.remove(2);             // Remove at index 2 -- O(n)
        System.out.println(arr);    // [10, 20, 40, 50]

        arr.remove(arr.size() - 1); // Remove last -- O(1)
        System.out.println(arr);    // [10, 20, 40]
    }
}
```

**Output**:
```
[10, 20, 40, 50]
[10, 20, 40]
```

### Operations Summary Table

| Operation | Time Complexity | Notes |
|---|---|---|
| Access by index | O(1) | Direct address calculation |
| Search by value | O(n) | Must scan; O(log n) if sorted (binary search) |
| Insert at end | O(1) amortized | May trigger resize |
| Insert at index i | O(n) | Shift n-i elements right |
| Delete from end | O(1) | No shifting needed |
| Delete at index i | O(n) | Shift n-i elements left |

---

## 3.4 Dynamic Arrays

Traditional arrays have a fixed size. But in practice, you often do not know how many elements you will need. **Dynamic arrays** solve this by automatically resizing when they run out of space.

Python's `list` and Java's `ArrayList` are both dynamic arrays.

```
    HOW DYNAMIC ARRAYS GROW

    Initial state: capacity = 4, size = 0
    [_, _, _, _]

    After adding 1, 2, 3, 4: capacity = 4, size = 4 (FULL!)
    [1, 2, 3, 4]

    Adding 5: No room! Resize to capacity 8, copy everything.
    Old: [1, 2, 3, 4]
    New: [1, 2, 3, 4, 5, _, _, _]   <-- capacity doubled

    This resize is O(n), but it happens so rarely that
    the amortized cost per append is O(1).

    Growth factor:
    - Python list: ~1.125x (grows by about 12.5%)
    - Java ArrayList: 1.5x (grows by 50%)
    - Many implementations: 2x (double)
```

### Building a Simple Dynamic Array

**Python**:
```python
class DynamicArray:
    def __init__(self):
        self.capacity = 2
        self.size = 0
        self.data = [None] * self.capacity

    def append(self, value):
        if self.size == self.capacity:
            self._resize()
        self.data[self.size] = value
        self.size += 1

    def _resize(self):
        self.capacity *= 2
        new_data = [None] * self.capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        print(f"  Resized to capacity {self.capacity}")

    def get(self, index):
        if 0 <= index < self.size:
            return self.data[index]
        raise IndexError("Index out of bounds")

    def __str__(self):
        return str([self.data[i] for i in range(self.size)])

# Test
darr = DynamicArray()
for i in range(1, 9):
    darr.append(i * 10)
    print(f"Added {i*10}: size={darr.size}, capacity={darr.capacity}")
```

**Output**:
```
Added 10: size=1, capacity=2
Added 20: size=2, capacity=2
  Resized to capacity 4
Added 30: size=3, capacity=4
Added 40: size=4, capacity=4
  Resized to capacity 8
Added 50: size=5, capacity=8
Added 60: size=6, capacity=8
Added 70: size=7, capacity=8
Added 80: size=8, capacity=8
```

---

## 3.5 Python list vs Java ArrayList

| Feature | Python `list` | Java `ArrayList` |
|---|---|---|
| Type restriction | Can mix types | Single type (uses generics) |
| Syntax to create | `arr = [1, 2, 3]` | `ArrayList<Integer> arr = new ArrayList<>();` |
| Access element | `arr[i]` | `arr.get(i)` |
| Set element | `arr[i] = val` | `arr.set(i, val)` |
| Add to end | `arr.append(val)` | `arr.add(val)` |
| Insert at index | `arr.insert(i, val)` | `arr.add(i, val)` |
| Remove by index | `arr.pop(i)` | `arr.remove(i)` |
| Length | `len(arr)` | `arr.size()` |
| Slicing | `arr[1:4]` | `arr.subList(1, 4)` |
| Sort | `arr.sort()` | `Collections.sort(arr)` |
| Contains | `val in arr` | `arr.contains(val)` |
| Growth factor | ~1.125x | 1.5x |

**Important**: Java also has plain arrays (`int[]`) which are fixed-size and more performant. Use `int[]` when the size is known, `ArrayList` when it may change.

---

## 3.6 Problem: Two Sum

**Problem**: Given an array of integers `nums` and an integer `target`, return the indices of the two numbers that add up to `target`. Assume exactly one solution exists.

### Approach 1: Brute Force -- O(n^2)

Check every pair of numbers.

```
    nums = [2, 7, 11, 15], target = 9

    Check pair (2, 7):  2 + 7 = 9   Found! Return [0, 1]

    But what if the answer is at the end?
    We might check ALL n*(n-1)/2 pairs --> O(n^2)
```

**Python**:
```python
def two_sum_brute(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

# Test
print(two_sum_brute([2, 7, 11, 15], 9))    # Output: [0, 1]
print(two_sum_brute([3, 2, 4], 6))          # Output: [1, 2]
print(two_sum_brute([3, 3], 6))             # Output: [0, 1]
```

**Java**:
```java
import java.util.Arrays;

public class TwoSumBrute {
    public static int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                if (nums[i] + nums[j] == target) {
                    return new int[]{i, j};
                }
            }
        }
        return new int[]{};
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(twoSum(new int[]{2,7,11,15}, 9)));
        // Output: [0, 1]
    }
}
```

**Complexity**: Time O(n^2), Space O(1).

### Approach 2: Hash Map -- O(n)

For each number, check if its complement (target - number) has already been seen.

```
    nums = [2, 7, 11, 15], target = 9

    Step 1: num = 2, complement = 9 - 2 = 7
            Is 7 in our map? No.
            Store {2: 0}

    Step 2: num = 7, complement = 9 - 7 = 2
            Is 2 in our map? YES! At index 0.
            Return [0, 1]

    Walkthrough with map state:
    +------+-----+------------+-----------+-------------------+
    | Step | num | complement | In map?   | Map state         |
    +------+-----+------------+-----------+-------------------+
    |  1   |  2  |     7      |   No      | {2: 0}            |
    |  2   |  7  |     2      |  Yes (0)  | Return [0, 1]     |
    +------+-----+------------+-----------+-------------------+
```

**Python**:
```python
def two_sum(nums, target):
    seen = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Test
print(two_sum([2, 7, 11, 15], 9))    # Output: [0, 1]
print(two_sum([3, 2, 4], 6))          # Output: [1, 2]
print(two_sum([3, 3], 6))             # Output: [0, 1]
```

**Java**:
```java
import java.util.*;

public class TwoSumHash {
    public static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (seen.containsKey(complement)) {
                return new int[]{seen.get(complement), i};
            }
            seen.put(nums[i], i);
        }
        return new int[]{};
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(twoSum(new int[]{2,7,11,15}, 9)));
        // Output: [0, 1]
    }
}
```

**Output**:
```
[0, 1]
[1, 2]
[0, 1]
```

**Complexity**: Time O(n), Space O(n). We traded space for time -- a hash map lets us do lookups in O(1).

---

## 3.7 Problem: Rotate Array

**Problem**: Given an array, rotate it to the right by `k` steps.

**Example**: [1, 2, 3, 4, 5, 6, 7], k = 3 -> [5, 6, 7, 1, 2, 3, 4]

### Approach: Reverse Three Times -- O(n) time, O(1) space

```
    Original:        [1, 2, 3, 4, 5, 6, 7]   k = 3

    Step 1: Reverse entire array
                     [7, 6, 5, 4, 3, 2, 1]

    Step 2: Reverse first k elements
                     [5, 6, 7, 4, 3, 2, 1]
                      ^-----^

    Step 3: Reverse remaining n-k elements
                     [5, 6, 7, 1, 2, 3, 4]
                               ^--------^

    Done! Rotated right by 3.
```

**Python**:
```python
def rotate(nums, k):
    n = len(nums)
    k = k % n  # Handle k > n

    def reverse(arr, start, end):
        while start < end:
            arr[start], arr[end] = arr[end], arr[start]
            start += 1
            end -= 1

    reverse(nums, 0, n - 1)      # Reverse all
    reverse(nums, 0, k - 1)      # Reverse first k
    reverse(nums, k, n - 1)      # Reverse rest

# Test
arr = [1, 2, 3, 4, 5, 6, 7]
rotate(arr, 3)
print(arr)  # Output: [5, 6, 7, 1, 2, 3, 4]

arr2 = [-1, -100, 3, 99]
rotate(arr2, 2)
print(arr2)  # Output: [3, 99, -1, -100]
```

**Java**:
```java
import java.util.Arrays;

public class RotateArray {
    public static void rotate(int[] nums, int k) {
        int n = nums.length;
        k = k % n;

        reverse(nums, 0, n - 1);
        reverse(nums, 0, k - 1);
        reverse(nums, k, n - 1);
    }

    private static void reverse(int[] arr, int start, int end) {
        while (start < end) {
            int temp = arr[start];
            arr[start] = arr[end];
            arr[end] = temp;
            start++;
            end--;
        }
    }

    public static void main(String[] args) {
        int[] arr = {1, 2, 3, 4, 5, 6, 7};
        rotate(arr, 3);
        System.out.println(Arrays.toString(arr));
        // Output: [5, 6, 7, 1, 2, 3, 4]
    }
}
```

**Output**:
```
[5, 6, 7, 1, 2, 3, 4]
[3, 99, -1, -100]
```

**Complexity**: Time O(n), Space O(1). Each element is swapped at most twice.

---

## 3.8 Problem: Maximum Subarray (Kadane's Algorithm)

**Problem**: Given an integer array, find the contiguous subarray with the largest sum, and return that sum.

**Example**: [-2, 1, -3, 4, -1, 2, 1, -5, 4] -> The subarray [4, -1, 2, 1] has the largest sum = 6.

### Brute Force -- O(n^2)

Check every possible subarray:

```python
def max_subarray_brute(nums):
    max_sum = nums[0]
    for i in range(len(nums)):
        current_sum = 0
        for j in range(i, len(nums)):
            current_sum += nums[j]
            max_sum = max(max_sum, current_sum)
    return max_sum
```

### Kadane's Algorithm -- O(n)

The key insight: at each position, either extend the current subarray or start a new one. If the running sum becomes negative, it is better to start fresh.

```
    Kadane's Algorithm Walkthrough
    nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

    +-------+------+-------------+----------+--------------------------+
    | Index | num  | current_sum | max_sum  | Decision                 |
    +-------+------+-------------+----------+--------------------------+
    |   0   |  -2  |     -2      |   -2     | Start: current = -2      |
    |   1   |   1  |      1      |    1     | -2+1=-1 < 1, restart at 1|
    |   2   |  -3  |     -2      |    1     | 1+(-3)=-2, extend        |
    |   3   |   4  |      4      |    4     | -2+4=2 < 4, restart at 4 |
    |   4   |  -1  |      3      |    4     | 4+(-1)=3, extend         |
    |   5   |   2  |      5      |    5     | 3+2=5, extend            |
    |   6   |   1  |      6      |    6     | 5+1=6, extend            |
    |   7   |  -5  |      1      |    6     | 6+(-5)=1, extend         |
    |   8   |   4  |      5      |    6     | 1+4=5, extend            |
    +-------+------+-------------+----------+--------------------------+

    Answer: 6 (subarray [4, -1, 2, 1])
```

**Python**:
```python
def max_subarray(nums):
    current_sum = nums[0]
    max_sum = nums[0]

    for num in nums[1:]:
        # Either extend the current subarray or start a new one
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)

    return max_sum

# Test
print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))  # Output: 6
print(max_subarray([1]))                                 # Output: 1
print(max_subarray([5, 4, -1, 7, 8]))                   # Output: 23
print(max_subarray([-1]))                                # Output: -1
print(max_subarray([-2, -1]))                            # Output: -1
```

**Java**:
```java
public class MaxSubarray {
    public static int maxSubArray(int[] nums) {
        int currentSum = nums[0];
        int maxSum = nums[0];

        for (int i = 1; i < nums.length; i++) {
            currentSum = Math.max(nums[i], currentSum + nums[i]);
            maxSum = Math.max(maxSum, currentSum);
        }
        return maxSum;
    }

    public static void main(String[] args) {
        System.out.println(maxSubArray(new int[]{-2,1,-3,4,-1,2,1,-5,4})); // 6
        System.out.println(maxSubArray(new int[]{1}));                      // 1
        System.out.println(maxSubArray(new int[]{5,4,-1,7,8}));            // 23
    }
}
```

**Output**:
```
6
1
23
-1
-1
```

**Complexity**: Time O(n), Space O(1). Kadane's algorithm is a classic example of a single-pass greedy approach.

---

## Common Mistakes

1. **Off-by-one errors.** Arrays are 0-indexed. The last element of an array of size n is at index n-1, not n. Accessing index n causes an IndexError/ArrayIndexOutOfBoundsException.
2. **Modifying an array while iterating.** Deleting elements during a for loop changes the indices and leads to skipped elements or crashes. Iterate backward or build a new array instead.
3. **Forgetting k % n for rotation.** If k is larger than the array length, rotating by k is the same as rotating by k % n. Without this, you get index errors.
4. **Using the wrong approach for Two Sum.** The brute force O(n^2) solution works but will time out on large inputs. Always consider hash maps for complement-finding problems.
5. **Initializing max_sum to 0 in Kadane's.** If all numbers are negative, the answer should be the largest negative number, not 0. Initialize with the first element.

## Best Practices

1. **Use hash maps to eliminate nested loops.** Many O(n^2) brute-force solutions can be reduced to O(n) with a hash map.
2. **Consider edge cases first**: empty array, single element, all duplicates, all negative numbers.
3. **Prefer in-place operations** when possible to save space. The rotate-by-reversal technique is a great example.
4. **Know your language's array API**: `append`, `pop`, `insert`, `sort`, `reverse`, `index`, slicing (Python) or `add`, `remove`, `set`, `get`, `sort`, `subList` (Java).
5. **Draw out the array state** step by step when debugging. Visualizing pointer positions and array modifications prevents logical errors.

---

## Quick Summary

Arrays store elements contiguously in memory, enabling O(1) access by index. The trade-off is that insertion and deletion in the middle require O(n) shifting. Dynamic arrays (Python list, Java ArrayList) automatically resize when full, giving amortized O(1) append. The Two Sum problem showcases the power of hash maps to reduce O(n^2) to O(n). Kadane's algorithm finds the maximum subarray sum in O(n) with a single pass. Array rotation can be done in O(n) time and O(1) space using three reversals.

## Key Points

- **Access is O(1)** because of contiguous memory and address arithmetic.
- **Insertion and deletion are O(n)** in the worst case due to element shifting, except at the end where they are O(1).
- **Dynamic arrays** double (or grow by a factor) when full, making append amortized O(1).
- **Two Sum** is the most common interview problem. Know both the O(n^2) brute force and the O(n) hash map approach.
- **Kadane's Algorithm** finds the maximum subarray sum in O(n) by deciding at each element whether to extend the current subarray or start fresh.
- **Array rotation by k** can be done in-place with three reversals.
- Always handle edge cases: empty arrays, single elements, and values of k larger than the array length.

---

## Practice Questions

1. Given an array [4, 2, 7, 1, 9, 3], trace through linear search to find the value 9. How many comparisons are needed?

2. Explain why inserting an element at the beginning of an array is O(n), but inserting at the end is O(1).

3. A dynamic array has capacity 8 and currently holds 8 elements. You append one more element. Describe exactly what happens in memory.

4. You need to check if an array of 10 million integers contains a specific value. The array is unsorted. What is the time complexity? How could you improve it?

5. Trace through Kadane's algorithm on the array [3, -4, 2, -1, 2, 6, -5, 3]. Show the current_sum and max_sum at each step.

---

## LeetCode-Style Problems

### Problem 1: Remove Duplicates from Sorted Array (Easy)

**Problem**: Given a sorted array, remove duplicates in-place so each element appears only once. Return the new length. Modify the array in-place with O(1) extra memory.

**Example**: [1, 1, 2] -> Return 2, array becomes [1, 2, ...]

```
    Two-pointer approach:

    [1, 1, 2, 2, 3]
     ^  ^
     w  r         w = write pointer, r = read pointer

    arr[r] == arr[w]? (1 == 1)  Skip. r++
    [1, 1, 2, 2, 3]
     ^     ^
     w     r

    arr[r] != arr[w]? (2 != 1)  w++, copy. arr[w] = arr[r]
    [1, 2, 2, 2, 3]
        ^     ^
        w     r

    arr[r] == arr[w]? (2 == 2)  Skip. r++
    [1, 2, 2, 2, 3]
        ^        ^
        w        r

    arr[r] != arr[w]? (3 != 2)  w++, copy. arr[w] = arr[r]
    [1, 2, 3, 2, 3]
           ^     ^
           w     r

    r reached end. Answer: w + 1 = 3
```

**Python**:
```python
def remove_duplicates(nums):
    if not nums:
        return 0

    write = 0
    for read in range(1, len(nums)):
        if nums[read] != nums[write]:
            write += 1
            nums[write] = nums[read]
    return write + 1

# Test
nums = [1, 1, 2]
k = remove_duplicates(nums)
print(k, nums[:k])  # Output: 2 [1, 2]

nums2 = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
k2 = remove_duplicates(nums2)
print(k2, nums2[:k2])  # Output: 5 [0, 1, 2, 3, 4]
```

**Java**:
```java
import java.util.Arrays;

public class RemoveDuplicates {
    public static int removeDuplicates(int[] nums) {
        if (nums.length == 0) return 0;

        int write = 0;
        for (int read = 1; read < nums.length; read++) {
            if (nums[read] != nums[write]) {
                write++;
                nums[write] = nums[read];
            }
        }
        return write + 1;
    }

    public static void main(String[] args) {
        int[] nums = {0,0,1,1,1,2,2,3,3,4};
        int k = removeDuplicates(nums);
        System.out.println(k + " " + Arrays.toString(Arrays.copyOf(nums, k)));
        // Output: 5 [0, 1, 2, 3, 4]
    }
}
```

**Output**:
```
2 [1, 2]
5 [0, 1, 2, 3, 4]
```

**Complexity**: Time O(n), Space O(1). The two-pointer technique is a fundamental array pattern.

---

### Problem 2: Best Time to Buy and Sell Stock (Easy)

**Problem**: Given an array where `prices[i]` is the stock price on day i, find the maximum profit from one buy and one sell. You must buy before you sell.

**Python**:
```python
def max_profit(prices):
    min_price = prices[0]
    max_profit_val = 0

    for price in prices[1:]:
        if price < min_price:
            min_price = price
        else:
            profit = price - min_price
            max_profit_val = max(max_profit_val, profit)

    return max_profit_val

# Test
print(max_profit([7, 1, 5, 3, 6, 4]))  # Output: 5  (buy at 1, sell at 6)
print(max_profit([7, 6, 4, 3, 1]))     # Output: 0  (no profitable trade)
```

**Java**:
```java
public class BuyAndSell {
    public static int maxProfit(int[] prices) {
        int minPrice = prices[0];
        int maxProfit = 0;

        for (int i = 1; i < prices.length; i++) {
            if (prices[i] < minPrice) {
                minPrice = prices[i];
            } else {
                maxProfit = Math.max(maxProfit, prices[i] - minPrice);
            }
        }
        return maxProfit;
    }

    public static void main(String[] args) {
        System.out.println(maxProfit(new int[]{7,1,5,3,6,4})); // 5
        System.out.println(maxProfit(new int[]{7,6,4,3,1}));   // 0
    }
}
```

**Output**:
```
5
0
```

**Complexity**: Time O(n), Space O(1). Track the minimum price seen so far and calculate profit at each step.

---

### Problem 3: Move Zeroes (Easy)

**Problem**: Given an array, move all 0s to the end while maintaining the relative order of non-zero elements. Do it in-place.

**Example**: [0, 1, 0, 3, 12] -> [1, 3, 12, 0, 0]

**Python**:
```python
def move_zeroes(nums):
    write = 0  # Position to write next non-zero element

    # Move all non-zero elements to the front
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write] = nums[read]
            write += 1

    # Fill the rest with zeros
    while write < len(nums):
        nums[write] = 0
        write += 1

# Test
arr = [0, 1, 0, 3, 12]
move_zeroes(arr)
print(arr)  # Output: [1, 3, 12, 0, 0]

arr2 = [0]
move_zeroes(arr2)
print(arr2)  # Output: [0]
```

**Java**:
```java
import java.util.Arrays;

public class MoveZeroes {
    public static void moveZeroes(int[] nums) {
        int write = 0;

        for (int read = 0; read < nums.length; read++) {
            if (nums[read] != 0) {
                nums[write] = nums[read];
                write++;
            }
        }

        while (write < nums.length) {
            nums[write] = 0;
            write++;
        }
    }

    public static void main(String[] args) {
        int[] arr = {0, 1, 0, 3, 12};
        moveZeroes(arr);
        System.out.println(Arrays.toString(arr)); // [1, 3, 12, 0, 0]
    }
}
```

**Output**:
```
[1, 3, 12, 0, 0]
[0]
```

**Complexity**: Time O(n), Space O(1). Another application of the two-pointer pattern.

---

### Problem 4: Product of Array Except Self (Medium)

**Problem**: Given an array `nums`, return an array where each element at index i is the product of all elements except `nums[i]`. Do it in O(n) without using division.

**Example**: [1, 2, 3, 4] -> [24, 12, 8, 6]

```
    Build two passes:

    Left products:  For each i, product of all elements to its LEFT.
    Right products: For each i, product of all elements to its RIGHT.
    Answer[i] = left[i] * right[i]

    nums =    [1,   2,   3,   4]
    left =    [1,   1,   2,   6]     (running product from left)
    right =   [24,  12,  4,   1]     (running product from right)
    answer =  [24,  12,  8,   6]     (left * right)
```

**Python**:
```python
def product_except_self(nums):
    n = len(nums)
    answer = [1] * n

    # Left pass: answer[i] = product of all elements to the left of i
    left_product = 1
    for i in range(n):
        answer[i] = left_product
        left_product *= nums[i]

    # Right pass: multiply by product of all elements to the right of i
    right_product = 1
    for i in range(n - 1, -1, -1):
        answer[i] *= right_product
        right_product *= nums[i]

    return answer

# Test
print(product_except_self([1, 2, 3, 4]))      # Output: [24, 12, 8, 6]
print(product_except_self([-1, 1, 0, -3, 3]))  # Output: [0, 0, 9, 0, 0]
```

**Java**:
```java
import java.util.Arrays;

public class ProductExceptSelf {
    public static int[] productExceptSelf(int[] nums) {
        int n = nums.length;
        int[] answer = new int[n];
        Arrays.fill(answer, 1);

        int leftProduct = 1;
        for (int i = 0; i < n; i++) {
            answer[i] = leftProduct;
            leftProduct *= nums[i];
        }

        int rightProduct = 1;
        for (int i = n - 1; i >= 0; i--) {
            answer[i] *= rightProduct;
            rightProduct *= nums[i];
        }
        return answer;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(productExceptSelf(new int[]{1,2,3,4})));
        // Output: [24, 12, 8, 6]
    }
}
```

**Output**:
```
[24, 12, 8, 6]
[0, 0, 9, 0, 0]
```

**Complexity**: Time O(n), Space O(1) (excluding the output array). Two passes with running products.

---

## What Is Next?

In Chapter 4, you will learn about **Strings** -- which are essentially arrays of characters with special properties. You will discover why strings are immutable in Python and Java, how to efficiently concatenate strings, and how to solve classic problems like valid palindrome, reverse words, and group anagrams.
