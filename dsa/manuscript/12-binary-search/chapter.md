# Chapter 12: Binary Search

## What You Will Learn

- What binary search is and why it is so powerful (the guessing game analogy)
- The prerequisite: sorted data
- Iterative and recursive implementations in Python and Java
- How to visualize binary search with left/right pointer diagrams
- The off-by-one errors that make binary search notoriously tricky
- Important variants: find first/last occurrence, search in rotated array, find peak element, search insert position
- A reusable template for solving binary search problems

## Why This Chapter Matters

Binary search is one of the most important algorithms in computer science. It lets you search through a million elements in just 20 steps, a billion elements in 30 steps, and a trillion elements in 40 steps. That is the power of O(log n).

The concept is simple -- cut the search space in half at every step. But the implementation is deceptively tricky. Off-by-one bugs, infinite loops, and incorrect boundary conditions plague even experienced programmers. Jon Bentley, in his classic book "Programming Pearls," reported that 90% of professional programmers could not write a correct binary search. Java's own `Arrays.binarySearch` had a subtle integer overflow bug that went undetected for nearly a decade.

This chapter will teach you not just how binary search works, but how to write it correctly every time.

---

## 12.1 What Is Binary Search?

### The Guessing Game: "Higher or Lower"

Imagine someone picks a number between 1 and 100, and you have to guess it. After each guess, they tell you "higher" or "lower."

**Bad strategy (linear search)**: Guess 1, 2, 3, 4, ... up to 100 guesses.

**Good strategy (binary search)**: Always guess the middle of the remaining range.

```
Secret number: 73
Range: [1, 100]

Guess 1: 50   "Higher!"    Range: [51, 100]
Guess 2: 75   "Lower!"     Range: [51, 74]
Guess 3: 62   "Higher!"    Range: [63, 74]
Guess 4: 68   "Higher!"    Range: [69, 74]
Guess 5: 71   "Higher!"    Range: [72, 74]
Guess 6: 73   "Correct!"

6 guesses instead of 73!
```

Each guess eliminates half the remaining possibilities. For n elements, you need at most **log2(n)** guesses.

```
n = 100     -> ~7 guesses
n = 1,000   -> ~10 guesses
n = 1,000,000 -> ~20 guesses
n = 1,000,000,000 -> ~30 guesses
```

### Prerequisite: Sorted Data

Binary search only works on **sorted** data. If the data is not sorted, the "higher or lower" comparison gives you no useful information about which half to eliminate.

---

## 12.2 Basic Binary Search -- Iterative

### How It Works

```
Find target = 23 in sorted array:

Array: [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
Index:  0  1  2   3   4   5   6   7   8   9

Step 1: left=0, right=9, mid=4
        [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
         ^            ^                    ^
        left         mid                 right
        arr[4]=16 < 23 -> search right half
        left = mid + 1 = 5

Step 2: left=5, right=9, mid=7
        [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
                           ^        ^       ^
                          left     mid    right
        arr[7]=56 > 23 -> search left half
        right = mid - 1 = 6

Step 3: left=5, right=6, mid=5
        [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
                           ^   ^
                        left/mid right
        arr[5]=23 == 23 -> FOUND! Return index 5
```

### Python -- Iterative Binary Search

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2  # Avoids integer overflow

        if arr[mid] == target:
            return mid          # Found!
        elif arr[mid] < target:
            left = mid + 1      # Search right half
        else:
            right = mid - 1     # Search left half

    return -1  # Not found


data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print(binary_search(data, 23))   # Output: 5
print(binary_search(data, 72))   # Output: 8
print(binary_search(data, 15))   # Output: -1 (not found)
```

### Java -- Iterative Binary Search

```java
public class BinarySearch {
    public static int binarySearch(int[] arr, int target) {
        int left = 0, right = arr.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;  // Avoids overflow

            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return -1;  // Not found
    }

    public static void main(String[] args) {
        int[] data = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};
        System.out.println(binarySearch(data, 23));  // Output: 5
        System.out.println(binarySearch(data, 15));  // Output: -1
    }
}
```

### Why `left + (right - left) // 2` Instead of `(left + right) // 2`?

```
If left = 2,000,000,000 and right = 2,000,000,000:

(left + right) / 2 = 4,000,000,000 / 2
                    = INTEGER OVERFLOW in Java! (int max is ~2.1 billion)

left + (right - left) / 2 = 2,000,000,000 + 0 / 2
                           = 2,000,000,000  (correct, no overflow)
```

In Python, integers have arbitrary precision, so overflow is not a concern. But using `left + (right - left) // 2` is a good habit that makes your code portable to Java, C++, and other languages.

---

## 12.3 Basic Binary Search -- Recursive

```python
def binary_search_recursive(arr, target, left=0, right=None):
    if right is None:
        right = len(arr) - 1

    if left > right:
        return -1  # Base case: not found

    mid = left + (right - left) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)


data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print(binary_search_recursive(data, 23))  # Output: 5
print(binary_search_recursive(data, 15))  # Output: -1
```

### Java -- Recursive Binary Search

```java
public class BinarySearchRecursive {
    public static int binarySearch(int[] arr, int target) {
        return helper(arr, target, 0, arr.length - 1);
    }

    private static int helper(int[] arr, int target, int left, int right) {
        if (left > right) return -1;

        int mid = left + (right - left) / 2;

        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) return helper(arr, target, mid + 1, right);
        else return helper(arr, target, left, mid - 1);
    }

    public static void main(String[] args) {
        int[] data = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};
        System.out.println(binarySearch(data, 23));  // Output: 5
    }
}
```

### Iterative vs Recursive

| Aspect           | Iterative          | Recursive              |
|------------------|--------------------|------------------------|
| Space            | O(1)               | O(log n) call stack    |
| Readability      | Slightly verbose    | More elegant           |
| Performance      | Slightly faster     | Function call overhead |
| Recommendation   | Preferred           | Good for learning      |

In interviews and production code, **prefer the iterative version** -- it avoids stack overflow on very large arrays.

### Time and Space Complexity

| Metric     | Value    | Why                                |
|------------|----------|------------------------------------|
| Time       | O(log n) | Halves the search space each step  |
| Space (iterative) | O(1) | Only uses left, right, mid      |
| Space (recursive) | O(log n) | Call stack depth              |

---

## 12.4 Off-By-One Errors: The #1 Bug

Binary search is notorious for off-by-one bugs. Here are the three critical decisions and the correct choices:

### Decision 1: `while left <= right` or `while left < right`?

```
Use left <= right when:
  - You return from INSIDE the loop (when arr[mid] == target)
  - left == right is a valid state (single element to check)

Use left < right when:
  - You return AFTER the loop (left/right converge to the answer)
  - Used in "find boundary" problems
```

### Decision 2: `right = mid` or `right = mid - 1`?

```
Use right = mid - 1 when:
  - You already checked arr[mid] and it is not the answer
  - Used with left <= right

Use right = mid when:
  - arr[mid] might still be the answer (boundary search)
  - Used with left < right
```

### Decision 3: `left = mid + 1` or `left = mid`?

```
ALWAYS use left = mid + 1 (not left = mid)
  - left = mid can cause an infinite loop!
  - Exception: only when mid is calculated differently (e.g., ceiling division)
```

### The Infinite Loop Trap

```python
# DANGER: This loops forever when left + 1 == right
left, right = 0, 1
while left < right:
    mid = (left + right) // 2  # mid = 0 (same as left!)
    left = mid                  # left stays 0, loop never ends!

# FIX: Use left = mid + 1, or use ceiling division
left, right = 0, 1
while left < right:
    mid = (left + right + 1) // 2  # Ceiling: mid = 1
    left = mid                      # Now left = 1, loop ends
```

---

## 12.5 Binary Search Template

Here is a reliable template that works for most binary search problems:

### Template 1: Find Exact Value

```python
def binary_search_exact(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
```

### Template 2: Find Left Boundary (First Occurrence)

```python
def find_left_boundary(arr, target):
    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid       # Record this, but keep searching left
            right = mid - 1
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result
```

### Template 3: Find Right Boundary (Last Occurrence)

```python
def find_right_boundary(arr, target):
    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid       # Record this, but keep searching right
            left = mid + 1
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result
```

### Visualization: Finding First and Last Occurrence

```
Array: [1, 2, 2, 2, 2, 3, 4, 5]
Target: 2

First occurrence (left boundary):
  Step 1: mid=3, arr[3]=2 == target -> result=3, search LEFT (right=2)
  Step 2: mid=1, arr[1]=2 == target -> result=1, search LEFT (right=0)
  Step 3: mid=0, arr[0]=1 < target  -> search RIGHT (left=1)
  left > right, stop. Answer: 1

Last occurrence (right boundary):
  Step 1: mid=3, arr[3]=2 == target -> result=3, search RIGHT (left=4)
  Step 2: mid=5, arr[5]=3 > target  -> search LEFT (right=4)
  Step 3: mid=4, arr[4]=2 == target -> result=4, search RIGHT (left=5)
  left > right, stop. Answer: 4
```

---

## 12.6 Common Mistakes

1. **Forgetting the sorted requirement**: Binary search only works on sorted data. If the array is not sorted, sort it first (O(n log n)) or use linear search.

2. **Integer overflow in mid calculation**: In Java/C++, `(left + right) / 2` can overflow. Always use `left + (right - left) / 2`.

3. **Off-by-one in loop condition**: Using `left < right` when you should use `left <= right` (or vice versa) leads to missed elements or infinite loops.

4. **Not adjusting boundaries correctly**: Using `right = mid` with `while left <= right` can cause infinite loops. Match your boundary updates to your loop condition.

5. **Returning the wrong value**: For "insert position" problems, return `left` after the loop (not -1). For "first/last occurrence," track the result separately.

---

## 12.7 Best Practices

1. **Always use `left + (right - left) // 2`**: It prevents integer overflow and works in every language.

2. **Pick one template and master it**: Do not mix and match styles. The "result variable" templates above are safe and flexible.

3. **Test edge cases**: Empty array, single element, target at index 0, target at last index, target not present, all elements equal to target.

4. **Verify with small examples**: Before submitting, trace through a 3-element array by hand. Most bugs show up immediately.

5. **Think in terms of "search space reduction"**: Binary search is not just for sorted arrays. It works whenever you can eliminate half the search space with a single test (monotonic condition).

---

## Quick Summary

**Binary search** finds a target in a sorted array by repeatedly halving the search space. The iterative version uses `left` and `right` pointers that converge toward the target. The algorithm runs in **O(log n)** time and **O(1)** space (iterative). The main implementation challenges are **off-by-one errors** -- choosing the correct loop condition, boundary updates, and return value. The technique extends to finding boundaries (first/last occurrence), search insert positions, and searching in modified sorted structures (rotated arrays, peak elements).

---

## Key Points

- Binary search requires sorted data and runs in O(log n) time
- Use `left + (right - left) // 2` to calculate mid (prevents overflow)
- Iterative is preferred over recursive (O(1) space vs O(log n))
- The loop condition (`<=` vs `<`) must match the boundary updates
- `left = mid` without ceiling division causes infinite loops
- Use the "result variable" technique for boundary searches (first/last occurrence)
- Binary search applies beyond sorted arrays -- any monotonic condition works
- Test with edge cases: empty, single element, target at boundaries, target absent

---

## Practice Questions

1. Trace binary search on `[3, 7, 11, 15, 19, 23, 27]` looking for the value 19. Show `left`, `right`, and `mid` at each step.

2. What happens if you use `(left + right) / 2` in Java with `left = 1,500,000,000` and `right = 2,000,000,000`? What is the fix?

3. An array contains `[1, 1, 2, 2, 2, 3, 3]`. Write down the steps to find the first and last occurrence of 2 using the boundary templates.

4. Can you use binary search on an unsorted array? Why or why not?

5. You have a sorted array of 1 billion elements. How many comparisons does binary search need in the worst case? How many would linear search need?

---

## LeetCode-Style Problems

### Problem 1: Search Insert Position (LeetCode 35)

**Problem**: Given a sorted array and a target value, return the index if the target is found. If not, return the index where it would be inserted to keep the array sorted.

**Approach**: Standard binary search. If not found, `left` points to the correct insertion position.

```
[1, 3, 5, 6], target = 5 -> return 2 (found at index 2)
[1, 3, 5, 6], target = 2 -> return 1 (would insert at index 1)
[1, 3, 5, 6], target = 7 -> return 4 (would insert at end)
[1, 3, 5, 6], target = 0 -> return 0 (would insert at beginning)
```

**Python Solution**:

```python
def search_insert(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return left  # Insertion point


print(search_insert([1, 3, 5, 6], 5))  # Output: 2
print(search_insert([1, 3, 5, 6], 2))  # Output: 1
print(search_insert([1, 3, 5, 6], 7))  # Output: 4
print(search_insert([1, 3, 5, 6], 0))  # Output: 0
```

**Java Solution**:

```java
public class SearchInsert {
    public static int searchInsert(int[] nums, int target) {
        int left = 0, right = nums.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (nums[mid] == target) return mid;
            else if (nums[mid] < target) left = mid + 1;
            else right = mid - 1;
        }

        return left;
    }

    public static void main(String[] args) {
        System.out.println(searchInsert(new int[]{1, 3, 5, 6}, 5));  // Output: 2
        System.out.println(searchInsert(new int[]{1, 3, 5, 6}, 2));  // Output: 1
    }
}
```

**Complexity**: Time: O(log n). Space: O(1).

---

### Problem 2: Find First and Last Position (LeetCode 34)

**Problem**: Given a sorted array and a target, find the starting and ending position of the target. Return `[-1, -1]` if not found. Must run in O(log n).

**Approach**: Run two binary searches -- one to find the left boundary (first occurrence) and one to find the right boundary (last occurrence).

```
[5, 7, 7, 8, 8, 10], target = 8

Find first 8: left boundary search -> index 3
Find last 8:  right boundary search -> index 4
Result: [3, 4]

[5, 7, 7, 8, 8, 10], target = 6
Not found -> [-1, -1]
```

**Python Solution**:

```python
def search_range(nums, target):
    def find_left():
        left, right = 0, len(nums) - 1
        result = -1
        while left <= right:
            mid = left + (right - left) // 2
            if nums[mid] == target:
                result = mid
                right = mid - 1  # Keep searching left
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return result

    def find_right():
        left, right = 0, len(nums) - 1
        result = -1
        while left <= right:
            mid = left + (right - left) // 2
            if nums[mid] == target:
                result = mid
                left = mid + 1   # Keep searching right
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return result

    return [find_left(), find_right()]


print(search_range([5, 7, 7, 8, 8, 10], 8))  # Output: [3, 4]
print(search_range([5, 7, 7, 8, 8, 10], 6))  # Output: [-1, -1]
print(search_range([], 0))                      # Output: [-1, -1]
```

**Java Solution**:

```java
public class SearchRange {
    public static int[] searchRange(int[] nums, int target) {
        return new int[]{findLeft(nums, target), findRight(nums, target)};
    }

    private static int findLeft(int[] nums, int target) {
        int left = 0, right = nums.length - 1, result = -1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) {
                result = mid;
                right = mid - 1;
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return result;
    }

    private static int findRight(int[] nums, int target) {
        int left = 0, right = nums.length - 1, result = -1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) {
                result = mid;
                left = mid + 1;
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return result;
    }

    public static void main(String[] args) {
        int[] result = searchRange(new int[]{5, 7, 7, 8, 8, 10}, 8);
        System.out.println(result[0] + ", " + result[1]);  // Output: 3, 4
    }
}
```

**Complexity**: Time: O(log n) -- two binary searches. Space: O(1).

---

### Problem 3: Search in Rotated Sorted Array (LeetCode 33)

**Problem**: A sorted array has been rotated at some pivot (e.g., `[4,5,6,7,0,1,2]` is `[0,1,2,4,5,6,7]` rotated at index 4). Search for a target in O(log n).

**Approach**: At each step, one half of the array is always sorted. Determine which half is sorted, then check if the target falls within that sorted half.

```
[4, 5, 6, 7, 0, 1, 2], target = 0

Step 1: left=0, right=6, mid=3, arr[mid]=7
  Left half [4,5,6,7] is sorted (arr[left]=4 <= arr[mid]=7)
  Is target in [4, 7]? No (0 < 4)
  -> Search right: left = 4

Step 2: left=4, right=6, mid=5, arr[mid]=1
  Left half [0,1] is sorted (arr[left]=0 <= arr[mid]=1)
  Is target in [0, 1]? Yes (0 >= 0 and 0 <= 1)
  -> Search left: right = 4  (not right=5 since we check left half)

Wait -- let me retrace more carefully:
Step 2: left=4, right=6, mid=5, arr[mid]=1
  Left half [0,1]: arr[4]=0 <= arr[5]=1, so left half is sorted
  Is target=0 in [0, 1]? Yes -> right = mid - 1 = 4

Step 3: left=4, right=4, mid=4, arr[mid]=0
  arr[mid]=0 == target -> Found at index 4!
```

**Python Solution**:

```python
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if nums[mid] == target:
            return mid

        # Left half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1  # Target is in left half
            else:
                left = mid + 1   # Target is in right half
        # Right half is sorted
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1   # Target is in right half
            else:
                right = mid - 1  # Target is in left half

    return -1


print(search_rotated([4, 5, 6, 7, 0, 1, 2], 0))  # Output: 4
print(search_rotated([4, 5, 6, 7, 0, 1, 2], 3))  # Output: -1
print(search_rotated([1], 0))                       # Output: -1
```

**Java Solution**:

```java
public class SearchRotated {
    public static int search(int[] nums, int target) {
        int left = 0, right = nums.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;

            if (nums[mid] == target) return mid;

            if (nums[left] <= nums[mid]) {  // Left half sorted
                if (nums[left] <= target && target < nums[mid]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            } else {  // Right half sorted
                if (nums[mid] < target && target <= nums[right]) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }

        return -1;
    }

    public static void main(String[] args) {
        System.out.println(search(new int[]{4, 5, 6, 7, 0, 1, 2}, 0));
        // Output: 4
    }
}
```

**Complexity**: Time: O(log n). Space: O(1).

---

### Problem 4: Find Peak Element (LeetCode 162)

**Problem**: A peak element is an element that is strictly greater than its neighbors. Given an array where `nums[i] != nums[i+1]`, find a peak element and return its index. The array may contain multiple peaks -- return any one.

**Approach**: If `nums[mid] < nums[mid + 1]`, a peak must exist to the right (the values are going up). Otherwise, a peak must exist to the left (or at mid itself).

```
[1, 2, 3, 1]

Step 1: left=0, right=3, mid=1
  nums[1]=2 < nums[2]=3 -> peak is to the right
  left = 2

Step 2: left=2, right=3, mid=2
  nums[2]=3 > nums[3]=1 -> peak is at mid or to the left
  right = 2

left == right == 2 -> Peak at index 2 (value 3)
```

**Python Solution**:

```python
def find_peak_element(nums):
    left, right = 0, len(nums) - 1

    while left < right:
        mid = left + (right - left) // 2

        if nums[mid] < nums[mid + 1]:
            left = mid + 1   # Peak is to the right
        else:
            right = mid      # Peak is at mid or to the left

    return left  # left == right == peak index


print(find_peak_element([1, 2, 3, 1]))      # Output: 2
print(find_peak_element([1, 2, 1, 3, 5, 6, 4]))  # Output: 5 (or 1)
```

**Java Solution**:

```java
public class FindPeak {
    public static int findPeakElement(int[] nums) {
        int left = 0, right = nums.length - 1;

        while (left < right) {
            int mid = left + (right - left) / 2;

            if (nums[mid] < nums[mid + 1]) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        return left;
    }

    public static void main(String[] args) {
        System.out.println(findPeakElement(new int[]{1, 2, 3, 1}));
        // Output: 2
    }
}
```

**Note**: This problem uses `while left < right` (not `<=`) and `right = mid` (not `mid - 1`) because mid might be the peak. This is the "converging pointers" style of binary search.

**Complexity**: Time: O(log n). Space: O(1).

---

### Problem 5: Search a 2D Matrix (LeetCode 74)

**Problem**: Search for a value in an m x n matrix where each row is sorted and the first element of each row is greater than the last element of the previous row. The entire matrix, read row by row, is sorted.

**Approach**: Treat the 2D matrix as a 1D sorted array. Map index `i` to `matrix[i // cols][i % cols]`.

```
Matrix:
  [1,  3,  5,  7]
  [10, 11, 16, 20]
  [23, 30, 34, 60]

As 1D: [1, 3, 5, 7, 10, 11, 16, 20, 23, 30, 34, 60]

Target = 3:
  Binary search on indices 0-11
  mid = 5, value = matrix[5//4][5%4] = matrix[1][1] = 11 > 3 -> right = 4
  mid = 2, value = matrix[2//4][2%4] = matrix[0][2] = 5  > 3 -> right = 1
  mid = 0, value = matrix[0//4][0%4] = matrix[0][0] = 1  < 3 -> left = 1
  mid = 1, value = matrix[1//4][1%4] = matrix[0][1] = 3 == 3 -> Found!
```

**Python Solution**:

```python
def search_matrix(matrix, target):
    if not matrix or not matrix[0]:
        return False

    rows, cols = len(matrix), len(matrix[0])
    left, right = 0, rows * cols - 1

    while left <= right:
        mid = left + (right - left) // 2
        value = matrix[mid // cols][mid % cols]

        if value == target:
            return True
        elif value < target:
            left = mid + 1
        else:
            right = mid - 1

    return False


matrix = [
    [1,  3,  5,  7],
    [10, 11, 16, 20],
    [23, 30, 34, 60]
]
print(search_matrix(matrix, 3))   # Output: True
print(search_matrix(matrix, 13))  # Output: False
```

**Java Solution**:

```java
public class SearchMatrix {
    public static boolean searchMatrix(int[][] matrix, int target) {
        if (matrix.length == 0 || matrix[0].length == 0) return false;

        int rows = matrix.length, cols = matrix[0].length;
        int left = 0, right = rows * cols - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;
            int value = matrix[mid / cols][mid % cols];

            if (value == target) return true;
            else if (value < target) left = mid + 1;
            else right = mid - 1;
        }

        return false;
    }

    public static void main(String[] args) {
        int[][] matrix = {
            {1, 3, 5, 7},
            {10, 11, 16, 20},
            {23, 30, 34, 60}
        };
        System.out.println(searchMatrix(matrix, 3));   // Output: true
        System.out.println(searchMatrix(matrix, 13));  // Output: false
    }
}
```

**Complexity**: Time: O(log(m * n)). Space: O(1).

---

## What Is Next?

Binary search is one of the most versatile techniques in your toolkit. You have seen it on sorted arrays, rotated arrays, 2D matrices, and peak-finding problems. In the next chapter, we begin exploring **Trees** -- hierarchical data structures where binary search takes its most natural form as the **Binary Search Tree**. Trees unlock entirely new classes of problems and are the foundation of databases, file systems, and many other core systems.
