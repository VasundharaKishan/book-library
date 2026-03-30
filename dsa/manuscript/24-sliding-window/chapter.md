# Chapter 24: Sliding Window

## What You Will Learn

- What the sliding window technique is and why it turns O(n^2) solutions into O(n)
- How to implement fixed-size sliding windows (e.g., max sum of K consecutive elements)
- How to implement variable-size sliding windows (e.g., smallest subarray with sum >= target)
- Reusable templates for both fixed and variable windows
- How to solve classic sliding window problems: longest substring without repeating characters, minimum window substring, and more

## Why This Chapter Matters

The sliding window technique is one of the most commonly tested patterns in coding interviews. It applies to a wide range of array and string problems, and once you recognize the pattern, the solution is almost always O(n).

The core idea is simple: instead of recalculating everything from scratch for each position, maintain a "window" that slides across the data, adding new elements on one side and removing old elements on the other. This avoids redundant computation.

Sliding window problems appear constantly in interviews at top companies. Mastering the two templates (fixed-size and variable-size) gives you a reliable framework for solving these problems quickly and correctly.

---

## 24.1 What Is a Sliding Window?

A sliding window is a contiguous subarray or substring that moves through the data from left to right. Instead of examining every possible subarray independently, we efficiently update the window by:

1. **Expanding** the window by including the next element
2. **Shrinking** the window by removing the leftmost element (when needed)

```
Array: [2, 1, 5, 1, 3, 2]

Fixed window of size 3, sliding across:

  Step 1: [2, 1, 5] 1  3  2    sum = 8
  Step 2:  2 [1, 5, 1] 3  2    sum = 8 - 2 + 1 = 7
  Step 3:  2  1 [5, 1, 3] 2    sum = 7 - 1 + 3 = 9
  Step 4:  2  1  5 [1, 3, 2]   sum = 9 - 5 + 2 = 6
                 ^         ^
                 |         |
              left       right

Instead of recalculating the sum from scratch each time (O(k)),
we just subtract the element leaving and add the element entering (O(1)).
```

### Brute Force vs Sliding Window

```
Problem: Find the maximum sum of any K consecutive elements.

Brute Force: O(n * k)
  For each starting position i:
    sum elements from i to i+k-1
  Track the maximum sum.

Sliding Window: O(n)
  Calculate sum of first K elements.
  Slide the window: subtract arr[left], add arr[right].
  Track the maximum sum.

For n = 1,000,000 and k = 1,000:
  Brute force: ~1,000,000,000 operations
  Sliding window: ~1,000,000 operations
  That is 1000x faster!
```

---

## 24.2 Fixed-Size Sliding Window

In a fixed-size window, the window always contains exactly K elements. You slide it one position at a time.

### Template

```python
def fixed_window(arr, k):
    # Step 1: Process the first window
    window_result = process(arr[0:k])

    # Step 2: Slide the window
    for i in range(k, len(arr)):
        # Add the new element (entering from the right)
        add(arr[i])

        # Remove the old element (leaving from the left)
        remove(arr[i - k])

        # Update the answer
        update(window_result)

    return answer
```

### Problem: Maximum Sum of K Consecutive Elements

**Python:**

```python
def max_sum_subarray(arr, k):
    """Find the maximum sum of any K consecutive elements."""
    if len(arr) < k:
        return -1

    # Calculate sum of the first window
    window_sum = sum(arr[:k])
    max_sum = window_sum

    # Slide the window
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]
        max_sum = max(max_sum, window_sum)

    return max_sum


# Test
arr = [2, 1, 5, 1, 3, 2]
k = 3
print(f"Max sum of {k} consecutive elements: "
      f"{max_sum_subarray(arr, k)}")
print(f"Array: {arr}")
```

**Output:**

```
Max sum of 3 consecutive elements: 9
Array: [2, 1, 5, 1, 3, 2]
```

**Java:**

```java
public class MaxSumSubarray {

    public static int maxSumSubarray(int[] arr, int k) {
        if (arr.length < k) return -1;

        int windowSum = 0;
        for (int i = 0; i < k; i++) {
            windowSum += arr[i];
        }

        int maxSum = windowSum;

        for (int i = k; i < arr.length; i++) {
            windowSum += arr[i] - arr[i - k];
            maxSum = Math.max(maxSum, windowSum);
        }

        return maxSum;
    }

    public static void main(String[] args) {
        int[] arr = {2, 1, 5, 1, 3, 2};
        System.out.println("Max sum: " +
            maxSumSubarray(arr, 3));
        // Output: Max sum: 9
    }
}
```

**Time Complexity:** O(n). **Space Complexity:** O(1).

### Problem: Maximum of Each Window of Size K

**Python:**

```python
from collections import deque

def max_sliding_window(nums, k):
    """
    Find the maximum in each window of size k.
    Uses a monotonic deque for O(n) total time.
    """
    result = []
    dq = deque()  # Stores indices, front is always max

    for i in range(len(nums)):
        # Remove indices outside the current window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove elements smaller than current
        # (they can never be the max)
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()

        dq.append(i)

        # Window is complete (have at least k elements)
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result


# Test
nums = [1, 3, -1, -3, 5, 3, 6, 7]
k = 3
print(f"Input: {nums}, k={k}")
print(f"Max of each window: {max_sliding_window(nums, k)}")
```

**Output:**

```
Input: [1, 3, -1, -3, 5, 3, 6, 7], k=3
Max of each window: [3, 3, 5, 5, 6, 7]
```

```
Walkthrough:
  Window [1, 3, -1]      -> max = 3
  Window [3, -1, -3]     -> max = 3
  Window [-1, -3, 5]     -> max = 5
  Window [-3, 5, 3]      -> max = 5
  Window [5, 3, 6]       -> max = 6
  Window [3, 6, 7]       -> max = 7
```

**Java:**

```java
import java.util.*;

public class SlidingWindowMax {

    public static int[] maxSlidingWindow(int[] nums, int k) {
        int n = nums.length;
        int[] result = new int[n - k + 1];
        Deque<Integer> dq = new ArrayDeque<>();

        for (int i = 0; i < n; i++) {
            // Remove indices out of window
            while (!dq.isEmpty() && dq.peekFirst() < i - k + 1) {
                dq.pollFirst();
            }

            // Remove smaller elements
            while (!dq.isEmpty() &&
                   nums[dq.peekLast()] < nums[i]) {
                dq.pollLast();
            }

            dq.offerLast(i);

            if (i >= k - 1) {
                result[i - k + 1] = nums[dq.peekFirst()];
            }
        }

        return result;
    }

    public static void main(String[] args) {
        int[] nums = {1, 3, -1, -3, 5, 3, 6, 7};
        int[] result = maxSlidingWindow(nums, 3);
        System.out.println(Arrays.toString(result));
        // Output: [3, 3, 5, 5, 6, 7]
    }
}
```

**Time Complexity:** O(n). **Space Complexity:** O(k) for the deque.

---

## 24.3 Variable-Size Sliding Window

In a variable-size window, the window expands and shrinks dynamically based on a condition. The right pointer always moves forward. The left pointer moves forward when the window condition is violated.

### Template

```python
def variable_window(arr, condition):
    left = 0
    window_state = initial_state

    for right in range(len(arr)):
        # Expand: add arr[right] to the window
        update_window(arr[right])

        # Shrink: while the window violates the condition
        while window_violates_condition():
            remove(arr[left])
            left += 1

        # Update the answer
        update_answer()

    return answer
```

```
Variable window visualization:

  Array: [2, 3, 1, 2, 4, 3]
  Goal: smallest subarray with sum >= 7

  Step 1:  [2] 3  1  2  4  3    sum=2, too small, expand
  Step 2:  [2  3] 1  2  4  3    sum=5, too small, expand
  Step 3:  [2  3  1] 2  4  3    sum=6, too small, expand
  Step 4:  [2  3  1  2] 4  3    sum=8 >= 7! Record len=4
           Shrink: remove 2
  Step 5:   2 [3  1  2] 4  3    sum=6, too small, expand
  Step 6:   2 [3  1  2  4] 3    sum=10 >= 7! Record len=4
           Shrink: remove 3
  Step 7:   2  3 [1  2  4] 3    sum=7 >= 7! Record len=3
           Shrink: remove 1
  Step 8:   2  3  1 [2  4] 3    sum=6, too small, expand
  Step 9:   2  3  1 [2  4  3]   sum=9 >= 7! Record len=3
           Shrink: remove 2
  Step 10:  2  3  1  2 [4  3]   sum=7 >= 7! Record len=2 <-- best!
           Shrink: remove 4
  Step 11:  2  3  1  2  4 [3]   sum=3, done

  Answer: 2
```

### Problem: Smallest Subarray with Sum >= Target

**Python:**

```python
def min_subarray_len(target, nums):
    """Find length of the smallest subarray with sum >= target."""
    left = 0
    window_sum = 0
    min_len = float('inf')

    for right in range(len(nums)):
        # Expand: add the right element
        window_sum += nums[right]

        # Shrink: while sum is sufficient, try smaller window
        while window_sum >= target:
            min_len = min(min_len, right - left + 1)
            window_sum -= nums[left]
            left += 1

    return min_len if min_len != float('inf') else 0


# Test
print(f"Target=7, nums=[2,3,1,2,4,3]: "
      f"{min_subarray_len(7, [2,3,1,2,4,3])}")
print(f"Target=4, nums=[1,4,4]: "
      f"{min_subarray_len(4, [1,4,4])}")
print(f"Target=11, nums=[1,1,1,1,1]: "
      f"{min_subarray_len(11, [1,1,1,1,1])}")
```

**Output:**

```
Target=7, nums=[2,3,1,2,4,3]: 2
Target=4, nums=[1,4,4]: 1
Target=11, nums=[1,1,1,1,1]: 0
```

**Java:**

```java
public class MinSubarrayLen {

    public static int minSubArrayLen(int target, int[] nums) {
        int left = 0, windowSum = 0;
        int minLen = Integer.MAX_VALUE;

        for (int right = 0; right < nums.length; right++) {
            windowSum += nums[right];

            while (windowSum >= target) {
                minLen = Math.min(minLen, right - left + 1);
                windowSum -= nums[left];
                left++;
            }
        }

        return minLen == Integer.MAX_VALUE ? 0 : minLen;
    }

    public static void main(String[] args) {
        System.out.println(minSubArrayLen(7,
            new int[]{2, 3, 1, 2, 4, 3}));
        // Output: 2
    }
}
```

**Time Complexity:** O(n). Each element is added and removed at most once.

**Space Complexity:** O(1).

---

## 24.4 Problem: Longest Substring Without Repeating Characters

**Problem:** Given a string, find the length of the longest substring without any repeating characters.

```
Example: "abcabcbb"

  Window slides:
  [a] b c a b c b b         len=1
  [a b] c a b c b b         len=2
  [a b c] a b c b b         len=3
  a [b c a] b c b b         len=3  (removed 'a', added 'a')
  a b [c a b] c b b         len=3
  a b c [a b c] b b         len=3
  a b c a [b c] b b         len=2  (removed until no dup 'b')
  ... and so on

  Longest: 3 ("abc")
```

**Python:**

```python
def length_of_longest_substring(s):
    char_index = {}  # Character -> its most recent index
    left = 0
    max_len = 0

    for right in range(len(s)):
        # If character is in the window, shrink from left
        if s[right] in char_index and \
           char_index[s[right]] >= left:
            left = char_index[s[right]] + 1

        char_index[s[right]] = right
        max_len = max(max_len, right - left + 1)

    return max_len


# Test
print(f"'abcabcbb': "
      f"{length_of_longest_substring('abcabcbb')}")
print(f"'bbbbb': "
      f"{length_of_longest_substring('bbbbb')}")
print(f"'pwwkew': "
      f"{length_of_longest_substring('pwwkew')}")
print(f"'': {length_of_longest_substring('')}")
```

**Output:**

```
'abcabcbb': 3
'bbbbb': 1
'pwwkew': 3
'': 0
```

**Java:**

```java
import java.util.*;

public class LongestSubstringNoRepeat {

    public static int lengthOfLongestSubstring(String s) {
        Map<Character, Integer> charIndex = new HashMap<>();
        int left = 0, maxLen = 0;

        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);

            if (charIndex.containsKey(c) &&
                charIndex.get(c) >= left) {
                left = charIndex.get(c) + 1;
            }

            charIndex.put(c, right);
            maxLen = Math.max(maxLen, right - left + 1);
        }

        return maxLen;
    }

    public static void main(String[] args) {
        System.out.println(
            lengthOfLongestSubstring("abcabcbb"));
        // Output: 3
    }
}
```

**Time Complexity:** O(n). **Space Complexity:** O(min(n, alphabet_size)).

---

## 24.5 Problem: Minimum Window Substring

**Problem:** Given strings s and t, find the minimum window in s that contains all characters of t (including duplicates).

This is one of the hardest sliding window problems, and a frequent interview question.

```
s = "ADOBECODEBANC", t = "ABC"

Slide the window, tracking character counts:

  [A] D O B E C O D E B A N C    has A, need B C
  [A D O B E C] O D E B A N C    has all! len=6
  A [D O B E C O D E B A N C]    shrink...
  ...
  A D O B E C O D E [B A N C]    has all! len=4

  Answer: "BANC"
```

**Python:**

```python
from collections import Counter

def min_window(s, t):
    if not s or not t or len(s) < len(t):
        return ""

    # Count characters needed
    need = Counter(t)
    missing = len(t)  # Total characters still needed

    left = 0
    min_len = float('inf')
    min_start = 0

    for right in range(len(s)):
        # Expand: add s[right] to window
        if need[s[right]] > 0:
            missing -= 1
        need[s[right]] -= 1

        # Shrink: while window contains all characters of t
        while missing == 0:
            # Update answer
            window_len = right - left + 1
            if window_len < min_len:
                min_len = window_len
                min_start = left

            # Remove s[left] from window
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1

    return "" if min_len == float('inf') \
           else s[min_start:min_start + min_len]


# Test
print(f"s='ADOBECODEBANC', t='ABC': "
      f"'{min_window('ADOBECODEBANC', 'ABC')}'")
print(f"s='a', t='a': '{min_window('a', 'a')}'")
print(f"s='a', t='aa': '{min_window('a', 'aa')}'")
```

**Output:**

```
s='ADOBECODEBANC', t='ABC': 'BANC'
s='a', t='a': 'a'
s='a', t='aa': ''
```

**Java:**

```java
import java.util.*;

public class MinWindowSubstring {

    public static String minWindow(String s, String t) {
        if (s.length() < t.length()) return "";

        int[] need = new int[128];
        for (char c : t.toCharArray()) need[c]++;

        int missing = t.length();
        int left = 0, minLen = Integer.MAX_VALUE,
            minStart = 0;

        for (int right = 0; right < s.length(); right++) {
            if (need[s.charAt(right)] > 0) missing--;
            need[s.charAt(right)]--;

            while (missing == 0) {
                int windowLen = right - left + 1;
                if (windowLen < minLen) {
                    minLen = windowLen;
                    minStart = left;
                }

                need[s.charAt(left)]++;
                if (need[s.charAt(left)] > 0) missing++;
                left++;
            }
        }

        return minLen == Integer.MAX_VALUE ? ""
            : s.substring(minStart, minStart + minLen);
    }

    public static void main(String[] args) {
        System.out.println(minWindow(
            "ADOBECODEBANC", "ABC"));
        // Output: BANC
    }
}
```

**Time Complexity:** O(n + m) where n is the length of s and m is the length of t.

**Space Complexity:** O(m) for the frequency counter.

---

## 24.6 Problem: Max Consecutive Ones III

**Problem:** Given a binary array and an integer k, return the maximum number of consecutive 1s if you can flip at most k 0s.

**Insight:** This is a variable-size window problem. Maintain a window with at most k zeros.

```
nums = [1,1,1,0,0,0,1,1,1,1,0], k = 2

  [1 1 1 0 0] 0 1 1 1 1 0    zeros=2, len=5
  1 [1 1 0 0 0] 1 1 1 1 0    zeros=3 > k=2, shrink!
  1 1 [1 0 0 0] 1 1 1 1 0    zeros=3, shrink!
  1 1 1 [0 0 0] 1 1 1 1 0    zeros=3, shrink!
  1 1 1 0 [0 0 1] 1 1 1 0    zeros=2, len=3
  1 1 1 0 [0 0 1 1] 1 1 0    zeros=2, len=4
  1 1 1 0 [0 0 1 1 1] 1 0    zeros=2, len=5
  1 1 1 0 [0 0 1 1 1 1] 0    zeros=2, len=6
  1 1 1 0 0 [0 1 1 1 1 0]    zeros=2, len=6

  Answer: 6
```

**Python:**

```python
def longest_ones(nums, k):
    left = 0
    zero_count = 0
    max_len = 0

    for right in range(len(nums)):
        if nums[right] == 0:
            zero_count += 1

        # Shrink window if too many zeros
        while zero_count > k:
            if nums[left] == 0:
                zero_count -= 1
            left += 1

        max_len = max(max_len, right - left + 1)

    return max_len


# Test
print(f"[1,1,1,0,0,0,1,1,1,1,0], k=2: "
      f"{longest_ones([1,1,1,0,0,0,1,1,1,1,0], 2)}")
print(f"[0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1], k=3: "
      f"{longest_ones([0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1], 3)}")
```

**Output:**

```
[1,1,1,0,0,0,1,1,1,1,0], k=2: 6
[0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1], k=3: 10
```

**Java:**

```java
public class MaxConsecutiveOnesIII {

    public static int longestOnes(int[] nums, int k) {
        int left = 0, zeroCount = 0, maxLen = 0;

        for (int right = 0; right < nums.length; right++) {
            if (nums[right] == 0) zeroCount++;

            while (zeroCount > k) {
                if (nums[left] == 0) zeroCount--;
                left++;
            }

            maxLen = Math.max(maxLen, right - left + 1);
        }

        return maxLen;
    }

    public static void main(String[] args) {
        System.out.println(longestOnes(
            new int[]{1,1,1,0,0,0,1,1,1,1,0}, 2));
        // Output: 6
    }
}
```

**Time Complexity:** O(n). **Space Complexity:** O(1).

---

## 24.7 Problem: Fruit Into Baskets

**Problem:** You have a row of trees, each producing one type of fruit. You have 2 baskets, each can hold only one type of fruit. Starting from any tree, pick fruits from consecutive trees. You must stop when you encounter a third type. Find the maximum number of fruits you can pick.

**Translation:** Find the longest subarray with at most 2 distinct elements.

**Python:**

```python
from collections import defaultdict

def total_fruit(fruits):
    basket = defaultdict(int)  # fruit_type -> count
    left = 0
    max_fruits = 0

    for right in range(len(fruits)):
        basket[fruits[right]] += 1

        # Shrink while more than 2 types
        while len(basket) > 2:
            basket[fruits[left]] -= 1
            if basket[fruits[left]] == 0:
                del basket[fruits[left]]
            left += 1

        max_fruits = max(max_fruits, right - left + 1)

    return max_fruits


# Test
print(f"[1,2,1]: {total_fruit([1,2,1])}")
print(f"[0,1,2,2]: {total_fruit([0,1,2,2])}")
print(f"[1,2,3,2,2]: {total_fruit([1,2,3,2,2])}")
print(f"[3,3,3,1,2,1,1,2,3,3,4]: "
      f"{total_fruit([3,3,3,1,2,1,1,2,3,3,4])}")
```

**Output:**

```
[1,2,1]: 3
[0,1,2,2]: 3
[1,2,3,2,2]: 4
[3,3,3,1,2,1,1,2,3,3,4]: 5
```

**Java:**

```java
import java.util.*;

public class FruitIntoBaskets {

    public static int totalFruit(int[] fruits) {
        Map<Integer, Integer> basket = new HashMap<>();
        int left = 0, maxFruits = 0;

        for (int right = 0; right < fruits.length; right++) {
            basket.merge(fruits[right], 1, Integer::sum);

            while (basket.size() > 2) {
                int leftFruit = fruits[left];
                basket.put(leftFruit,
                    basket.get(leftFruit) - 1);
                if (basket.get(leftFruit) == 0) {
                    basket.remove(leftFruit);
                }
                left++;
            }

            maxFruits = Math.max(maxFruits,
                right - left + 1);
        }

        return maxFruits;
    }

    public static void main(String[] args) {
        System.out.println(totalFruit(
            new int[]{3,3,3,1,2,1,1,2,3,3,4}));
        // Output: 5
    }
}
```

**Time Complexity:** O(n). **Space Complexity:** O(1) since at most 3 types in the map.

---

## 24.8 Problem: Permutation in String

**Problem:** Given two strings s1 and s2, return true if s2 contains a permutation of s1. In other words, return true if one of s1's permutations is a substring of s2.

**Insight:** This is a fixed-size window of length `len(s1)`. Slide it across s2 and check if the character frequencies match.

```
s1 = "ab", s2 = "eidbaooo"

  Window of size 2 sliding across s2:
  [e i] d b a o o o    freq: {e:1,i:1} != {a:1,b:1}
  e [i d] b a o o o    freq: {i:1,d:1} != {a:1,b:1}
  e i [d b] a o o o    freq: {d:1,b:1} != {a:1,b:1}
  e i d [b a] o o o    freq: {b:1,a:1} == {a:1,b:1} --> TRUE!
```

**Python:**

```python
from collections import Counter

def check_inclusion(s1, s2):
    if len(s1) > len(s2):
        return False

    s1_count = Counter(s1)
    window_count = Counter(s2[:len(s1)])

    if window_count == s1_count:
        return True

    for i in range(len(s1), len(s2)):
        # Add new character
        window_count[s2[i]] += 1

        # Remove old character
        old_char = s2[i - len(s1)]
        window_count[old_char] -= 1
        if window_count[old_char] == 0:
            del window_count[old_char]

        if window_count == s1_count:
            return True

    return False


# Alternative: use a "matches" counter for O(1) comparison
def check_inclusion_v2(s1, s2):
    if len(s1) > len(s2):
        return False

    s1_count = [0] * 26
    window_count = [0] * 26

    for c in s1:
        s1_count[ord(c) - ord('a')] += 1
    for i in range(len(s1)):
        window_count[ord(s2[i]) - ord('a')] += 1

    # Count how many character frequencies match
    matches = sum(1 for i in range(26)
                  if s1_count[i] == window_count[i])

    for i in range(len(s1), len(s2)):
        if matches == 26:
            return True

        # Add new character
        idx = ord(s2[i]) - ord('a')
        window_count[idx] += 1
        if window_count[idx] == s1_count[idx]:
            matches += 1
        elif window_count[idx] == s1_count[idx] + 1:
            matches -= 1

        # Remove old character
        idx = ord(s2[i - len(s1)]) - ord('a')
        window_count[idx] -= 1
        if window_count[idx] == s1_count[idx]:
            matches += 1
        elif window_count[idx] == s1_count[idx] - 1:
            matches -= 1

    return matches == 26


# Test
print(f"s1='ab', s2='eidbaooo': "
      f"{check_inclusion('ab', 'eidbaooo')}")
print(f"s1='ab', s2='eidboaoo': "
      f"{check_inclusion('ab', 'eidboaoo')}")
```

**Output:**

```
s1='ab', s2='eidbaooo': True
s1='ab', s2='eidboaoo': False
```

**Java:**

```java
public class PermutationInString {

    public static boolean checkInclusion(
            String s1, String s2) {
        if (s1.length() > s2.length()) return false;

        int[] s1Count = new int[26];
        int[] windowCount = new int[26];

        for (int i = 0; i < s1.length(); i++) {
            s1Count[s1.charAt(i) - 'a']++;
            windowCount[s2.charAt(i) - 'a']++;
        }

        int matches = 0;
        for (int i = 0; i < 26; i++) {
            if (s1Count[i] == windowCount[i]) matches++;
        }

        for (int i = s1.length(); i < s2.length(); i++) {
            if (matches == 26) return true;

            int idx = s2.charAt(i) - 'a';
            windowCount[idx]++;
            if (windowCount[idx] == s1Count[idx]) matches++;
            else if (windowCount[idx] == s1Count[idx]+1)
                matches--;

            idx = s2.charAt(i - s1.length()) - 'a';
            windowCount[idx]--;
            if (windowCount[idx] == s1Count[idx]) matches++;
            else if (windowCount[idx] == s1Count[idx]-1)
                matches--;
        }

        return matches == 26;
    }

    public static void main(String[] args) {
        System.out.println(checkInclusion(
            "ab", "eidbaooo"));
        // Output: true
    }
}
```

**Time Complexity:** O(n) where n is the length of s2 (with the matches counter approach).

**Space Complexity:** O(1) (fixed-size arrays of 26).

---

## 24.9 Sliding Window Cheat Sheet

```
FIXED-SIZE WINDOW (window always has k elements)
=================================================
Use when: problem says "k consecutive elements"

Template:
  1. Compute result for first window (indices 0 to k-1)
  2. For i = k to n-1:
     - Add arr[i] to window
     - Remove arr[i-k] from window
     - Update result

Examples:
  - Max sum of k elements
  - Max of each window of size k
  - Permutation in string (window = len(s1))
  - Average of each window


VARIABLE-SIZE WINDOW (window grows and shrinks)
=================================================
Use when: problem asks for "longest/shortest subarray" with a condition

Template:
  left = 0
  for right in range(n):
      # Expand: process arr[right]
      while condition_violated:
          # Shrink: remove arr[left]
          left += 1
      # Update answer

Examples:
  - Longest substring without repeating chars
  - Smallest subarray with sum >= target
  - Longest substring with at most k distinct chars
  - Max consecutive ones with k flips
```

### When to Use Sliding Window

| Signal in Problem | Window Type |
|-------------------|-------------|
| "K consecutive elements" | Fixed |
| "Subarray/substring of size K" | Fixed |
| "Longest subarray/substring with condition" | Variable |
| "Shortest subarray/substring with condition" | Variable |
| "At most K distinct elements" | Variable |
| "Contains all characters of" | Variable (fixed size also works) |

---

## Common Mistakes

1. **Off-by-one errors with window boundaries.** The window `[left, right]` is inclusive on both ends. The window size is `right - left + 1`, not `right - left`.

2. **Forgetting to shrink the window.** In variable-size problems, the left pointer must advance when the condition is violated. Forgetting this makes the window grow forever.

3. **Not cleaning up the frequency map.** When a character count drops to zero, remove it from the map. Otherwise, `len(map)` gives the wrong count of distinct characters.

4. **Using a sliding window when the data has negative numbers.** The "smallest subarray with sum >= target" approach assumes all positive numbers. With negatives, the prefix sum approach or other techniques are needed.

5. **Confusing when to update the answer.** For "longest" problems, update inside the for loop (after shrinking). For "shortest" problems, update inside the while loop (before shrinking further).

---

## Best Practices

1. **Identify fixed vs variable window first.** If the window size is given, it is fixed. If you need to find the optimal window size, it is variable.

2. **Use hash maps for character counting.** For problems involving character frequencies, a hash map (or array of size 26/128) is the standard tool.

3. **Track a "matches" counter for O(1) comparison.** Instead of comparing two frequency arrays (O(26)), track how many positions match and update incrementally.

4. **Always verify the window invariant.** After each expansion and shrinking, the window should satisfy the problem's constraints. Add assertions during debugging.

5. **Handle edge cases first.** Check for empty input, window size larger than array, and single-element arrays before the main logic.

---

## Quick Summary

```
Sliding Window = maintain a moving subarray/substring

Fixed-size:
  Window always has K elements
  Slide by adding right element, removing left element
  O(n) time, O(1) space

Variable-size:
  Window grows (right pointer) and shrinks (left pointer)
  Expand until condition met, then shrink until condition lost
  O(n) time because each element added/removed at most once

Key data structures:
  Hash map for character frequencies
  Deque for sliding window maximum
  Counter variable for tracking matches
```

## Key Points

- The sliding window technique converts O(n * k) or O(n^2) brute-force solutions into O(n) by reusing computation from the previous window position.
- Fixed-size windows are used when the window length is given. Variable-size windows are used when you need to find the optimal window length.
- In variable-size windows, both pointers only move forward. Each element is processed at most twice (once when added, once when removed), guaranteeing O(n) time.
- Frequency maps are the primary data structure for character-based sliding window problems.
- The "matches counter" optimization allows O(1) window comparison instead of O(alphabet_size).

---

## Practice Questions

1. Why is the time complexity of a variable-size sliding window O(n) even though it has a nested while loop? Explain using the amortized analysis argument.

2. How would you modify the "longest substring without repeating characters" solution to find the actual substring, not just its length?

3. Can sliding window be used with negative numbers? If not, what alternative technique would you use for "smallest subarray with sum >= target" when negatives are present?

4. Explain the difference between the "minimum window substring" and the "permutation in string" problems. Why does one use a variable window and the other a fixed window?

5. Design a sliding window solution for: "Given a string and an integer k, find the longest substring with at most k distinct characters."

---

## LeetCode-Style Problems

### Problem 1: Longest Repeating Character Replacement (Medium)

Given a string and an integer k, find the length of the longest substring where you can replace at most k characters to make all characters the same.

```python
def character_replacement(s, k):
    count = {}
    left = 0
    max_freq = 0  # Frequency of the most common char in window
    max_len = 0

    for right in range(len(s)):
        count[s[right]] = count.get(s[right], 0) + 1
        max_freq = max(max_freq, count[s[right]])

        # Window size - max_freq = characters to replace
        # If this exceeds k, shrink
        window_size = right - left + 1
        if window_size - max_freq > k:
            count[s[left]] -= 1
            left += 1

        max_len = max(max_len, right - left + 1)

    return max_len


# Test
print(f"'ABAB', k=2: {character_replacement('ABAB', 2)}")
print(f"'AABABBA', k=1: {character_replacement('AABABBA', 1)}")
```

**Output:**

```
'ABAB', k=2: 4
'AABABBA', k=1: 4
```

### Problem 2: Subarrays with K Different Integers (Hard)

Find the number of subarrays with exactly k different integers. Use the trick: exactly(k) = atMost(k) - atMost(k-1).

```python
from collections import defaultdict

def subarrays_with_k_distinct(nums, k):
    def at_most_k(k):
        count = defaultdict(int)
        left = 0
        result = 0

        for right in range(len(nums)):
            if count[nums[right]] == 0:
                k -= 1
            count[nums[right]] += 1

            while k < 0:
                count[nums[left]] -= 1
                if count[nums[left]] == 0:
                    k += 1
                left += 1

            result += right - left + 1

        return result

    return at_most_k(k) - at_most_k(k - 1)


# Test
print(f"[1,2,1,2,3], k=2: "
      f"{subarrays_with_k_distinct([1,2,1,2,3], 2)}")
print(f"[1,2,1,3,4], k=3: "
      f"{subarrays_with_k_distinct([1,2,1,3,4], 3)}")
```

**Output:**

```
[1,2,1,2,3], k=2: 7
[1,2,1,3,4], k=3: 3
```

### Problem 3: Minimum Size Subarray Sum (Medium)

Find the minimum length subarray with sum >= target. (Covered in Section 24.3, included here as a complete solution with both languages.)

```python
def min_sub_array_len(target, nums):
    left = 0
    current_sum = 0
    min_len = float('inf')

    for right in range(len(nums)):
        current_sum += nums[right]

        while current_sum >= target:
            min_len = min(min_len, right - left + 1)
            current_sum -= nums[left]
            left += 1

    return min_len if min_len != float('inf') else 0


# Test
print(f"target=7, [2,3,1,2,4,3]: "
      f"{min_sub_array_len(7, [2,3,1,2,4,3])}")
# Output: 2

print(f"target=11, [1,1,1,1,1,1,1,1]: "
      f"{min_sub_array_len(11, [1,1,1,1,1,1,1,1])}")
# Output: 0
```

**Output:**

```
target=7, [2,3,1,2,4,3]: 2
target=11, [1,1,1,1,1,1,1,1]: 0
```

---

## What Is Next?

The sliding window technique gives you a powerful tool for processing contiguous subarrays and substrings in linear time. In Chapter 25, you will learn a closely related technique: **Two Pointers**. While sliding window uses two pointers moving in the same direction, the two-pointer technique often uses pointers moving toward each other or at different speeds, enabling efficient solutions for sorted arrays, linked lists, and string problems.
