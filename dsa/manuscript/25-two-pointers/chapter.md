# Chapter 25: Two Pointers

## What You Will Learn

- What the two-pointer technique is and why it works
- Opposite-direction pointers for problems like Two Sum (sorted), Container With Most Water, and Trapping Rain Water
- Same-direction pointers for Remove Duplicates and Move Zeroes
- Fast and slow pointers for cycle detection and the Happy Number problem
- Templates and pattern recognition for identifying two-pointer problems
- Time and space complexity analysis for each variant

## Why This Chapter Matters

Imagine you have a long bookshelf and need to find two books whose combined page count equals exactly 500. You could check every pair --- but that takes forever. Instead, put one finger on the leftmost book and another on the rightmost. If the sum is too big, move the right finger left. Too small? Move the left finger right. Two fingers, one scan, done.

That is the two-pointer technique. It transforms brute-force O(n^2) solutions into elegant O(n) ones. It appears in roughly 20 percent of coding interview questions across arrays, strings, and linked lists. Master this pattern and you unlock a huge family of problems.

---

## 25.1 What Are Two Pointers?

Two pointers is a technique where you maintain two index variables (or references) that traverse a data structure --- typically an array or linked list. By moving them strategically, you eliminate unnecessary comparisons.

There are three main variants:

```
Variant 1: Opposite Direction
  left -->          <-- right
  [1, 2, 3, 4, 5, 6, 7, 8, 9]

Variant 2: Same Direction (Fast/Slow on array)
  slow ->  fast ->
  [0, 0, 1, 1, 2, 3, 3, 4]

Variant 3: Fast/Slow on Linked List
  slow ->
  1 -> 2 -> 3 -> 4 -> 5
            fast ------->
```

### When to Use Two Pointers

| Signal | Example |
|--------|---------|
| Sorted array + pair/triplet search | Two Sum II, 3Sum |
| In-place modification | Remove Duplicates, Move Zeroes |
| Palindrome check | Valid Palindrome |
| Linked list cycle or middle | Linked List Cycle, Middle of List |
| Converging/diverging scan | Container With Most Water |

---

## 25.2 Opposite-Direction Pointers

The idea: place one pointer at the start and one at the end. Move them toward each other based on a condition.

### Template

```
left = 0
right = len(arr) - 1

while left < right:
    if condition_met(arr[left], arr[right]):
        # record answer
        # move one or both pointers
    elif need_bigger:
        left += 1
    else:
        right -= 1
```

---

### Problem 1: Two Sum II (Sorted Array)

**Problem:** Given a sorted array and a target, find two numbers that add up to the target. Return their 1-indexed positions.

**Example:** `numbers = [2, 7, 11, 15]`, `target = 9` --> `[1, 2]`

#### Step-by-Step Walkthrough

```
Array: [2, 7, 11, 15]    Target: 9

Step 1: left=0, right=3
        2 + 15 = 17 > 9  --> move right

Step 2: left=0, right=2
        2 + 11 = 13 > 9  --> move right

Step 3: left=0, right=1
        2 + 7 = 9 == 9   --> FOUND! Return [1, 2]
```

#### Python Solution

```python
def two_sum(numbers, target):
    left, right = 0, len(numbers) - 1

    while left < right:
        current_sum = numbers[left] + numbers[right]

        if current_sum == target:
            return [left + 1, right + 1]  # 1-indexed
        elif current_sum < target:
            left += 1    # need bigger sum
        else:
            right -= 1   # need smaller sum

    return []  # no solution found

# Test
print(two_sum([2, 7, 11, 15], 9))
# Output: [1, 2]

print(two_sum([2, 3, 4], 6))
# Output: [1, 3]
```

#### Java Solution

```java
public class TwoSumSorted {
    public static int[] twoSum(int[] numbers, int target) {
        int left = 0, right = numbers.length - 1;

        while (left < right) {
            int sum = numbers[left] + numbers[right];

            if (sum == target) {
                return new int[]{left + 1, right + 1};
            } else if (sum < target) {
                left++;
            } else {
                right--;
            }
        }

        return new int[]{};
    }

    public static void main(String[] args) {
        int[] result = twoSum(new int[]{2, 7, 11, 15}, 9);
        System.out.println("[" + result[0] + ", " + result[1] + "]");
        // Output: [1, 2]
    }
}
```

**Why it works:** Because the array is sorted, if the sum is too large, we can only make it smaller by moving `right` left. If too small, move `left` right. Each step eliminates at least one candidate.

**Complexity:**
- Time: O(n) --- each pointer moves at most n times
- Space: O(1) --- only two variables

---

### Problem 2: Container With Most Water

**Problem:** Given `n` vertical lines where line `i` has height `height[i]`, find two lines that together with the x-axis form a container holding the most water.

```
ASCII Diagram:

height = [1, 8, 6, 2, 5, 4, 8, 3, 7]

    |              |
    |              |        |
    |  |           |        |
    |  |     |     |        |
    |  |     |  |  |        |
    |  |     |  |  |  |     |
    |  |  |  |  |  |  |  |  |
 |  |  |  |  |  |  |  |  |  |
 0  1  2  3  4  5  6  7  8

 Best container: lines at index 1 (height 8) and index 8 (height 7)
 Area = min(8, 7) * (8 - 1) = 7 * 7 = 49
```

#### Step-by-Step Walkthrough

```
left=0  right=8   area = min(1,7) * 8 = 8    max=8
left=1  right=8   area = min(8,7) * 7 = 49   max=49
left=1  right=7   area = min(8,3) * 6 = 18   max=49
left=1  right=6   area = min(8,8) * 5 = 40   max=49
...

Key insight: always move the pointer with the SHORTER line.
Why? The area is limited by the shorter line. Moving the taller
line can only decrease width without possibly increasing height.
```

#### Python Solution

```python
def max_area(height):
    left, right = 0, len(height) - 1
    max_water = 0

    while left < right:
        # Calculate area
        width = right - left
        h = min(height[left], height[right])
        area = width * h
        max_water = max(max_water, area)

        # Move the shorter line's pointer
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return max_water

# Test
print(max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]))
# Output: 49

print(max_area([1, 1]))
# Output: 1
```

#### Java Solution

```java
public class ContainerWithMostWater {
    public static int maxArea(int[] height) {
        int left = 0, right = height.length - 1;
        int maxWater = 0;

        while (left < right) {
            int width = right - left;
            int h = Math.min(height[left], height[right]);
            maxWater = Math.max(maxWater, width * h);

            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }

        return maxWater;
    }

    public static void main(String[] args) {
        System.out.println(maxArea(new int[]{1, 8, 6, 2, 5, 4, 8, 3, 7}));
        // Output: 49
    }
}
```

**Complexity:**
- Time: O(n)
- Space: O(1)

---

### Problem 3: Trapping Rain Water

**Problem:** Given `n` bars where each bar has width 1 and height `height[i]`, compute how much water can be trapped after raining.

```
ASCII Diagram:

height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]

                         |
             |           | |     |
    |  water | | water | | | | water | |
 ___| ~~~~~~ | | ~~~~~~ | | | | ~~~~ | |___
 0  1  0  2  1  0  1  3  2  1  2  1

 Water trapped = 6 units

 Detailed view with water (~):
       |
    |~~~~~~~~~~|
    |  |~~~~~| | |~~~|
 ___|__|_____|_|_|_|_|_|___|
 0  1  0  2  1  0  1  3  2  1  2  1
```

#### How It Works

Water at any position = `min(max_left, max_right) - height[i]`

With two pointers, we track the max height seen from each side:

```
Step-by-step:
left=0  right=11  left_max=0  right_max=0
  height[left]=0, height[right]=1
  height[left] <= height[right]
  left_max = max(0, 0) = 0
  water += max(0, 0-0) = 0
  left++

left=1  right=11  left_max=0  right_max=0
  height[left]=1, height[right]=1
  height[left] <= height[right]
  left_max = max(0, 1) = 1
  water += max(0, 1-1) = 0
  left++

left=2  right=11  left_max=1  right_max=0
  height[left]=0, height[right]=1
  height[left] <= height[right]
  left_max = max(1, 0) = 1
  water += max(0, 1-0) = 1   <-- trapped water!
  left++
...
```

#### Python Solution

```python
def trap(height):
    if not height:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0

    while left < right:
        if height[left] <= height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1

    return water

# Test
print(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))
# Output: 6

print(trap([4, 2, 0, 3, 2, 5]))
# Output: 9
```

#### Java Solution

```java
public class TrappingRainWater {
    public static int trap(int[] height) {
        if (height == null || height.length == 0) return 0;

        int left = 0, right = height.length - 1;
        int leftMax = 0, rightMax = 0;
        int water = 0;

        while (left < right) {
            if (height[left] <= height[right]) {
                leftMax = Math.max(leftMax, height[left]);
                water += leftMax - height[left];
                left++;
            } else {
                rightMax = Math.max(rightMax, height[right]);
                water += rightMax - height[right];
                right--;
            }
        }

        return water;
    }

    public static void main(String[] args) {
        System.out.println(trap(new int[]{0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1}));
        // Output: 6
    }
}
```

**Why it works:** We always process the side with the shorter boundary. If `height[left] <= height[right]`, we know the right side has a boundary at least as tall, so water at `left` depends only on `left_max`.

**Complexity:**
- Time: O(n)
- Space: O(1)

---

## 25.3 Same-Direction Pointers

Both pointers start at the beginning (or same end). One pointer is the "reader" (scans every element), the other is the "writer" (marks where to place valid elements).

### Template

```
writer = 0  # or start condition

for reader in range(len(arr)):
    if should_keep(arr[reader]):
        arr[writer] = arr[reader]
        writer += 1

# writer now points to the new length
```

---

### Problem 4: Remove Duplicates from Sorted Array

**Problem:** Given a sorted array, remove duplicates in-place. Return the count of unique elements.

```
ASCII Diagram:

Input:  [1, 1, 2, 2, 3, 4, 4, 5]
         w
         r

Step 1: r=0, arr[0]=1, first element, w=1
Step 2: r=1, arr[1]=1 == arr[0], skip
Step 3: r=2, arr[2]=2 != arr[1], arr[1]=2, w=2
Step 4: r=3, arr[3]=2 == arr[2], skip
Step 5: r=4, arr[4]=3 != arr[3], arr[2]=3, w=3
Step 6: r=5, arr[5]=4 != arr[4], arr[3]=4, w=4
Step 7: r=6, arr[6]=4 == arr[5], skip
Step 8: r=7, arr[7]=5 != arr[6], arr[4]=5, w=5

Result: [1, 2, 3, 4, 5, ...]  unique count = 5
```

#### Python Solution

```python
def remove_duplicates(nums):
    if not nums:
        return 0

    writer = 1  # first element is always unique

    for reader in range(1, len(nums)):
        if nums[reader] != nums[reader - 1]:
            nums[writer] = nums[reader]
            writer += 1

    return writer

# Test
nums = [1, 1, 2, 2, 3, 4, 4, 5]
k = remove_duplicates(nums)
print(f"Unique count: {k}")
print(f"Array: {nums[:k]}")
# Output:
# Unique count: 5
# Array: [1, 2, 3, 4, 5]
```

#### Java Solution

```java
public class RemoveDuplicates {
    public static int removeDuplicates(int[] nums) {
        if (nums.length == 0) return 0;

        int writer = 1;

        for (int reader = 1; reader < nums.length; reader++) {
            if (nums[reader] != nums[reader - 1]) {
                nums[writer] = nums[reader];
                writer++;
            }
        }

        return writer;
    }

    public static void main(String[] args) {
        int[] nums = {1, 1, 2, 2, 3, 4, 4, 5};
        int k = removeDuplicates(nums);
        System.out.print("Unique count: " + k + ", Array: [");
        for (int i = 0; i < k; i++) {
            System.out.print(nums[i] + (i < k - 1 ? ", " : ""));
        }
        System.out.println("]");
        // Output: Unique count: 5, Array: [1, 2, 3, 4, 5]
    }
}
```

**Complexity:**
- Time: O(n)
- Space: O(1)

---

### Problem 5: Move Zeroes

**Problem:** Move all zeroes to the end of an array while maintaining relative order of non-zero elements. Do it in-place.

```
ASCII Diagram:

Input: [0, 1, 0, 3, 12]

writer=0, reader scans:
  r=0: arr[0]=0, skip
  r=1: arr[1]=1, arr[0]=1, writer=1  --> [1, 1, 0, 3, 12]
  r=2: arr[2]=0, skip
  r=3: arr[3]=3, arr[1]=3, writer=2  --> [1, 3, 0, 3, 12]
  r=4: arr[4]=12, arr[2]=12, writer=3 --> [1, 3, 12, 3, 12]

Fill remaining with 0:
  arr[3]=0, arr[4]=0                  --> [1, 3, 12, 0, 0]
```

#### Python Solution

```python
def move_zeroes(nums):
    writer = 0

    # Move all non-zero elements to the front
    for reader in range(len(nums)):
        if nums[reader] != 0:
            nums[writer] = nums[reader]
            writer += 1

    # Fill the rest with zeroes
    while writer < len(nums):
        nums[writer] = 0
        writer += 1

# Test
nums = [0, 1, 0, 3, 12]
move_zeroes(nums)
print(nums)
# Output: [1, 3, 12, 0, 0]
```

#### Python Solution (Swap Variant)

```python
def move_zeroes_swap(nums):
    writer = 0

    for reader in range(len(nums)):
        if nums[reader] != 0:
            nums[writer], nums[reader] = nums[reader], nums[writer]
            writer += 1

# Test
nums = [0, 1, 0, 3, 12]
move_zeroes_swap(nums)
print(nums)
# Output: [1, 3, 12, 0, 0]
```

#### Java Solution

```java
public class MoveZeroes {
    public static void moveZeroes(int[] nums) {
        int writer = 0;

        for (int reader = 0; reader < nums.length; reader++) {
            if (nums[reader] != 0) {
                int temp = nums[writer];
                nums[writer] = nums[reader];
                nums[reader] = temp;
                writer++;
            }
        }
    }

    public static void main(String[] args) {
        int[] nums = {0, 1, 0, 3, 12};
        moveZeroes(nums);
        System.out.print("[");
        for (int i = 0; i < nums.length; i++) {
            System.out.print(nums[i] + (i < nums.length - 1 ? ", " : ""));
        }
        System.out.println("]");
        // Output: [1, 3, 12, 0, 0]
    }
}
```

**Complexity:**
- Time: O(n)
- Space: O(1)

---

## 25.4 Fast and Slow Pointers (Floyd's Tortoise and Hare)

One pointer moves one step at a time (slow/tortoise), the other moves two steps (fast/hare). If there is a cycle, they will eventually meet.

```
ASCII Diagram --- Cycle Detection:

    1 -> 2 -> 3 -> 4
                    |
              7 <- 5
              |    ^
              v    |
              6 ---+

    slow: 1, 2, 3, 4, 5, 6, 7, 3, 4, 5, ...
    fast: 1, 3, 5, 7, 4, 6, 3, 5, 7, 4, ...

    They meet at node 5 (after enough steps).
```

### Why It Works

Think of two runners on a circular track. The faster runner laps the slower one eventually. If there is no cycle, the fast runner reaches the end (null).

---

### Problem 6: Linked List Cycle Detection

**Problem:** Given a linked list, determine if it has a cycle.

#### Python Solution

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def has_cycle(head):
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next        # 1 step
        fast = fast.next.next   # 2 steps

        if slow == fast:
            return True

    return False  # fast reached the end -- no cycle

# Test: Create a cycle
# 1 -> 2 -> 3 -> 4 -> 2 (cycle back to node 2)
node1 = ListNode(1)
node2 = ListNode(2)
node3 = ListNode(3)
node4 = ListNode(4)
node1.next = node2
node2.next = node3
node3.next = node4
node4.next = node2  # creates cycle

print(has_cycle(node1))
# Output: True

# Test without cycle
a = ListNode(1, ListNode(2, ListNode(3)))
print(has_cycle(a))
# Output: False
```

#### Java Solution

```java
public class LinkedListCycle {
    static class ListNode {
        int val;
        ListNode next;
        ListNode(int val) { this.val = val; }
    }

    public static boolean hasCycle(ListNode head) {
        ListNode slow = head, fast = head;

        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;

            if (slow == fast) return true;
        }

        return false;
    }

    public static void main(String[] args) {
        ListNode n1 = new ListNode(1);
        ListNode n2 = new ListNode(2);
        ListNode n3 = new ListNode(3);
        n1.next = n2;
        n2.next = n3;
        n3.next = n2; // cycle

        System.out.println(hasCycle(n1));
        // Output: true
    }
}
```

**Complexity:**
- Time: O(n)
- Space: O(1)

---

### Problem 7: Happy Number

**Problem:** A number is "happy" if repeatedly replacing it with the sum of squares of its digits eventually reaches 1. Detect if a number is happy (if not, it loops forever).

```
Example: 19

19 -> 1^2 + 9^2 = 1 + 81 = 82
82 -> 8^2 + 2^2 = 64 + 4  = 68
68 -> 6^2 + 8^2 = 36 + 64 = 100
100 -> 1^2 + 0 + 0        = 1   --> HAPPY!

Example: 2

2 -> 4 -> 16 -> 37 -> 58 -> 89 -> 145 -> 42 -> 20 -> 4 ...
                                                       ^
                                    cycle detected! NOT happy.
```

**Key Insight:** This is the same as cycle detection. The sequence of digit-sum-of-squares either reaches 1 or enters a cycle. Use fast/slow pointers.

#### Python Solution

```python
def is_happy(n):
    def get_next(num):
        total = 0
        while num > 0:
            digit = num % 10
            total += digit * digit
            num //= 10
        return total

    slow = n
    fast = get_next(n)

    while fast != 1 and slow != fast:
        slow = get_next(slow)          # 1 step
        fast = get_next(get_next(fast)) # 2 steps

    return fast == 1

# Test
print(is_happy(19))   # Output: True
print(is_happy(2))    # Output: False
print(is_happy(7))    # Output: True
```

#### Java Solution

```java
public class HappyNumber {
    private static int getNext(int n) {
        int total = 0;
        while (n > 0) {
            int digit = n % 10;
            total += digit * digit;
            n /= 10;
        }
        return total;
    }

    public static boolean isHappy(int n) {
        int slow = n;
        int fast = getNext(n);

        while (fast != 1 && slow != fast) {
            slow = getNext(slow);
            fast = getNext(getNext(fast));
        }

        return fast == 1;
    }

    public static void main(String[] args) {
        System.out.println(isHappy(19));  // Output: true
        System.out.println(isHappy(2));   // Output: false
    }
}
```

**Complexity:**
- Time: O(log n) per step, bounded number of steps
- Space: O(1) --- no hash set needed

---

## 25.5 Templates and Pattern Recognition

### Master Template: Opposite Direction

```python
def opposite_direction(arr):
    left, right = 0, len(arr) - 1
    result = None

    while left < right:
        # Process arr[left] and arr[right]
        if condition_to_shrink_right:
            right -= 1
        elif condition_to_grow_left:
            left += 1
        else:
            # Found answer or update result
            # Move one or both pointers
            pass

    return result
```

### Master Template: Same Direction (Reader/Writer)

```python
def same_direction(arr):
    writer = 0

    for reader in range(len(arr)):
        if should_keep(arr[reader]):
            arr[writer] = arr[reader]
            writer += 1

    return writer  # new length
```

### Master Template: Fast/Slow

```python
def fast_slow(head):
    slow, fast = head, head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

        if slow == fast:
            return True  # cycle found

    return False  # no cycle
```

### Pattern Recognition Cheat Sheet

```
+----------------------------------+------------------------+
| Problem Signal                   | Pointer Type           |
+----------------------------------+------------------------+
| Sorted array + target sum        | Opposite direction     |
| Palindrome check                 | Opposite direction     |
| Max area / trapping water        | Opposite direction     |
| Remove elements in-place         | Same direction         |
| Partition array                  | Same direction         |
| Cycle detection                  | Fast / slow            |
| Find middle of linked list       | Fast / slow            |
| Find duplicate number            | Fast / slow            |
+----------------------------------+------------------------+
```

---

## Common Mistakes

1. **Off-by-one in loop condition.** Use `while left < right` (strict) for opposite direction. Using `<=` processes the same element twice when they meet.

2. **Forgetting the sorted requirement.** Opposite-direction two-pointer for sum problems only works on sorted arrays. If unsorted, sort first or use a hash map.

3. **Not handling duplicates.** In problems like 3Sum, you must skip duplicate values to avoid duplicate triplets. Add `while left < right and nums[left] == nums[left - 1]: left += 1`.

4. **Modifying the array while reading.** In same-direction problems, always write through the `writer` pointer and read through the `reader`. Never modify elements ahead of the reader.

5. **Null pointer in fast/slow.** Always check `fast and fast.next` before advancing. Missing the `fast.next` check causes a null pointer exception.

---

## Best Practices

- **Draw it out.** Before coding, trace through 3-5 elements by hand. Two pointers are visual --- use that.
- **Start with brute force.** Write the O(n^2) solution first. Then ask: "Can I avoid rechecking pairs by using sorted order or pointer movement?"
- **Identify the invariant.** What property stays true as pointers move? For Container With Most Water: the answer cannot be improved by moving the taller line's pointer.
- **Test with edge cases.** Empty array, single element, all same elements, all zeroes.
- **Use the swap trick.** For in-place problems, swapping reader and writer values often simplifies the code.

---

## Quick Summary

| Variant | Pointers Start | Movement | Use Case |
|---------|---------------|----------|----------|
| Opposite | Both ends | Toward center | Sum pairs, palindromes, area |
| Same direction | Same end | Both forward | Remove/filter in-place |
| Fast/slow | Same start | Different speeds | Cycle detection, middle finding |

All three variants achieve O(n) time with O(1) space by eliminating redundant work through strategic pointer movement.

---

## Key Points

- Two pointers reduce O(n^2) brute-force pair scanning to O(n) by using structure (sorted order, direction, speed).
- Opposite-direction works when the array is sorted and you need to find pairs satisfying a condition.
- Same-direction (reader/writer) works for in-place filtering, deduplication, and partitioning.
- Fast/slow detects cycles in linked lists and number sequences without extra space.
- The technique applies to arrays, strings, and linked lists --- learn the templates and recognize the signals.

---

## Practice Questions

1. Given a sorted array and a target, can you always find a pair using two pointers? What if the array is unsorted?

2. In the Container With Most Water problem, why do we move the pointer with the shorter line? Prove that we never skip the optimal answer.

3. How would you modify the Remove Duplicates solution to allow at most 2 duplicates instead of 0?

4. Explain why the fast/slow pointer technique guarantees they meet inside a cycle. What is the maximum number of steps before they meet?

5. Can you solve the palindrome check problem ("racecar") using two pointers? What about ignoring non-alphanumeric characters?

---

## LeetCode-Style Problems

### Problem 1: Valid Palindrome (Easy)

**Problem:** Given a string, determine if it is a palindrome considering only alphanumeric characters and ignoring case.

```python
def is_palindrome(s):
    left, right = 0, len(s) - 1

    while left < right:
        # Skip non-alphanumeric
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1

        if s[left].lower() != s[right].lower():
            return False

        left += 1
        right -= 1

    return True

# Test
print(is_palindrome("A man, a plan, a canal: Panama"))  # True
print(is_palindrome("race a car"))                       # False
```

**Complexity:** Time O(n), Space O(1)

---

### Problem 2: 3Sum (Medium)

**Problem:** Find all unique triplets in an array that sum to zero.

```python
def three_sum(nums):
    nums.sort()
    result = []

    for i in range(len(nums) - 2):
        # Skip duplicates for first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        left, right = i + 1, len(nums) - 1

        while left < right:
            total = nums[i] + nums[left] + nums[right]

            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicates
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1

    return result

# Test
print(three_sum([-1, 0, 1, 2, -1, -4]))
# Output: [[-1, -1, 2], [-1, 0, 1]]
```

**Complexity:** Time O(n^2), Space O(1) excluding output

---

### Problem 3: Sort Colors (Medium)

**Problem:** Sort an array of 0s, 1s, and 2s in-place (Dutch National Flag problem).

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
            # Don't increment mid -- need to check swapped value

# Test
nums = [2, 0, 2, 1, 1, 0]
sort_colors(nums)
print(nums)
# Output: [0, 0, 1, 1, 2, 2]
```

**Complexity:** Time O(n), Space O(1)

---

### Problem 4: Find the Duplicate Number (Medium)

**Problem:** Given an array of n+1 integers where each integer is between 1 and n, find the duplicate. Use O(1) space.

```python
def find_duplicate(nums):
    # Phase 1: Find meeting point (cycle detection)
    slow, fast = nums[0], nums[0]

    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break

    # Phase 2: Find cycle entrance
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]

    return slow

# Test
print(find_duplicate([1, 3, 4, 2, 2]))  # Output: 2
print(find_duplicate([3, 1, 3, 4, 2]))  # Output: 3
```

**Complexity:** Time O(n), Space O(1)

---

### Problem 5: Remove Element (Easy)

**Problem:** Remove all instances of a value from an array in-place. Return the new length.

```python
def remove_element(nums, val):
    writer = 0

    for reader in range(len(nums)):
        if nums[reader] != val:
            nums[writer] = nums[reader]
            writer += 1

    return writer

# Test
nums = [3, 2, 2, 3]
k = remove_element(nums, 3)
print(f"Length: {k}, Array: {nums[:k]}")
# Output: Length: 2, Array: [2, 2]
```

**Complexity:** Time O(n), Space O(1)

---

## What Is Next?

You have mastered the two-pointer technique --- one of the most versatile tools in your algorithm toolkit. You have seen how two simple index variables can replace nested loops and hash sets.

In the next chapter, we explore **Tries** --- a tree-like data structure purpose-built for string operations. Tries power autocomplete, spell checkers, and dictionary lookups. If two pointers taught you to scan efficiently, tries will teach you to search strings in ways arrays never could.
