# Chapter 29: Problem-Solving Patterns

## What You Will Learn

- A catalog of the 10 most important algorithm patterns and when to use each
- A decision flowchart for matching problems to patterns
- A keyword-to-pattern mapping table for quick identification
- 10 example problems matched to their correct patterns with explanations
- How to combine patterns for complex problems
- A systematic approach to recognize patterns from problem descriptions

## Why This Chapter Matters

You have spent the last 28 chapters learning individual data structures and algorithms. Now comes the harder part: given a brand new problem, how do you know which technique to use?

This is the skill that separates someone who has "studied algorithms" from someone who can actually solve problems. Pattern recognition is not magic --- it is a learnable skill. Most coding interview problems fall into about 10 patterns. Once you recognize which pattern applies, the solution structure writes itself.

This chapter is your cheat sheet, your field guide, your decision tree. Come back to it before every practice session and every interview.

---

## 29.1 The 10 Core Patterns

### Pattern 1: Two Pointers

**What it is:** Use two index variables to scan through a sorted array or linked list, moving them based on conditions.

**When to use it:**
- Sorted array + pair/triplet sum
- Palindrome checking
- Removing duplicates in-place
- Linked list cycle detection

**Key signals in problem statement:**
- "Sorted array" + "find pair"
- "In-place" + "remove"
- "Palindrome"
- "Linked list" + "cycle"

**Template:**
```python
left, right = 0, len(arr) - 1
while left < right:
    if condition:
        left += 1
    else:
        right -= 1
```

**Complexity:** Usually O(n) time, O(1) space

**Example problems:** Two Sum II, Container With Most Water, Remove Duplicates, Valid Palindrome, 3Sum

---

### Pattern 2: Sliding Window

**What it is:** Maintain a window (subarray/substring) that slides over the data. Expand the right side, shrink the left side when a condition is violated.

**When to use it:**
- Contiguous subarray/substring problems
- "Maximum/minimum of all subarrays of size k"
- String problems with character frequency constraints

**Key signals in problem statement:**
- "Subarray" or "substring"
- "Contiguous"
- "Maximum/minimum length"
- "At most k distinct"
- "Window" or "consecutive"

**Template:**
```python
left = 0
for right in range(len(arr)):
    # expand window: add arr[right]
    while window_is_invalid():
        # shrink window: remove arr[left]
        left += 1
    # update answer
```

**Complexity:** Usually O(n) time, O(k) space

**Example problems:** Maximum Sum Subarray of Size K, Longest Substring Without Repeating Characters, Minimum Window Substring, Fruit Into Baskets

---

### Pattern 3: Binary Search

**What it is:** Divide the search space in half at each step. Works on sorted data or monotonic functions.

**When to use it:**
- Sorted array search
- "Find minimum/maximum that satisfies condition"
- Search space can be halved at each step

**Key signals in problem statement:**
- "Sorted"
- "Find minimum/maximum"
- "O(log n)" requirement
- "Search" or "find position"
- "Rotated sorted array"

**Template:**
```python
left, right = 0, len(arr) - 1
while left <= right:
    mid = left + (right - left) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
```

**Complexity:** O(log n) time, O(1) space

**Example problems:** Binary Search, Search in Rotated Array, Find Peak Element, Koko Eating Bananas, Median of Two Sorted Arrays

---

### Pattern 4: BFS (Breadth-First Search)

**What it is:** Explore level by level using a queue. Always finds the shortest path in unweighted graphs.

**When to use it:**
- Shortest path in unweighted graph
- Level-order traversal
- Problems asking for "minimum number of steps"
- Grid traversal (nearest exit, shortest path)

**Key signals in problem statement:**
- "Shortest" or "minimum steps"
- "Level by level"
- "Nearest" or "closest"
- Grid with obstacles
- "Minimum moves"

**Template:**
```python
from collections import deque
queue = deque([start])
visited = {start}
steps = 0
while queue:
    for _ in range(len(queue)):
        node = queue.popleft()
        if is_target(node): return steps
        for neighbor in get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    steps += 1
```

**Complexity:** O(V + E) time, O(V) space

**Example problems:** Binary Tree Level Order, Word Ladder, Rotting Oranges, Shortest Path in Grid, Open the Lock

---

### Pattern 5: DFS (Depth-First Search)

**What it is:** Explore as deep as possible before backtracking. Uses recursion or a stack.

**When to use it:**
- "Find all paths" or "count all ways"
- Tree traversal (inorder, preorder, postorder)
- Connected components
- Island counting in grids

**Key signals in problem statement:**
- "All paths" or "all combinations"
- "Connected" or "reachable"
- "Island" or "region"
- Tree problems (depth, height, path sum)

**Template:**
```python
def dfs(node, visited):
    if node is None or node in visited:
        return
    visited.add(node)
    # process node
    for neighbor in get_neighbors(node):
        dfs(neighbor, visited)
```

**Complexity:** O(V + E) time, O(V) space

**Example problems:** Number of Islands, Path Sum, Clone Graph, Course Schedule, Word Search

---

### Pattern 6: Dynamic Programming

**What it is:** Break a problem into overlapping subproblems. Store results to avoid recomputation.

**When to use it:**
- Optimization problems (maximize/minimize)
- Counting problems (number of ways)
- Problems with overlapping subproblems and optimal substructure
- Sequence problems (subsequence, substring)

**Key signals in problem statement:**
- "Maximum/minimum" + "number of ways"
- "How many ways"
- "Can you reach" (yes/no feasibility)
- "Longest/shortest subsequence"
- "Partition" + "optimal"

**Template:**
```python
# Bottom-up
dp = [0] * (n + 1)
dp[0] = base_case
for i in range(1, n + 1):
    dp[i] = best of dp[previous states] + current
return dp[n]
```

**Complexity:** Varies, typically O(n^2) or O(n*m)

**Example problems:** Climbing Stairs, Coin Change, Longest Common Subsequence, 0/1 Knapsack, Edit Distance, House Robber

---

### Pattern 7: Greedy

**What it is:** Make the locally optimal choice at each step, hoping it leads to a globally optimal solution.

**When to use it:**
- Interval scheduling (meetings, events)
- Activity selection
- Huffman coding
- Problems where local optimum = global optimum

**Key signals in problem statement:**
- "Minimum number of intervals"
- "Maximum number of non-overlapping"
- "Schedule" or "assign"
- "Earliest deadline" or "latest start"

**Template:**
```python
items.sort(by=some_criteria)
result = 0
for item in items:
    if can_include(item):
        include(item)
        result += 1
return result
```

**Complexity:** Usually O(n log n) due to sorting

**Example problems:** Jump Game, Meeting Rooms II, Non-overlapping Intervals, Task Scheduler, Gas Station

---

### Pattern 8: Backtracking

**What it is:** Build solutions incrementally, abandoning ("pruning") paths that cannot lead to valid solutions.

**When to use it:**
- Generate all permutations/combinations/subsets
- Constraint satisfaction (Sudoku, N-Queens)
- "Find all valid configurations"

**Key signals in problem statement:**
- "All permutations" or "all combinations"
- "Generate all" or "list all"
- "Valid configurations"
- "Place N items with constraints"

**Template:**
```python
def backtrack(path, choices):
    if is_complete(path):
        result.append(path[:])
        return
    for choice in choices:
        if is_valid(choice):
            path.append(choice)
            backtrack(path, remaining_choices)
            path.pop()  # undo choice
```

**Complexity:** Usually exponential O(2^n) or O(n!)

**Example problems:** Subsets, Permutations, N-Queens, Sudoku Solver, Combination Sum, Letter Combinations of Phone Number

---

### Pattern 9: Monotonic Stack

**What it is:** A stack that maintains elements in sorted order (increasing or decreasing). Elements are popped when a new element violates the monotonic property.

**When to use it:**
- "Next greater/smaller element"
- "Previous greater/smaller element"
- Histogram problems
- Temperature/stock span problems

**Key signals in problem statement:**
- "Next greater" or "next smaller"
- "Span" or "distance to next"
- "Histogram" or "rectangle"
- "Stock prices" + "days until warmer"

**Template:**
```python
stack = []  # stores indices
for i in range(len(arr)):
    while stack and arr[stack[-1]] < arr[i]:
        idx = stack.pop()
        # arr[i] is the next greater element for arr[idx]
    stack.append(i)
```

**Complexity:** O(n) time (each element pushed/popped at most once)

**Example problems:** Daily Temperatures, Next Greater Element, Largest Rectangle in Histogram, Trapping Rain Water (stack approach)

---

### Pattern 10: Prefix Sum / Hash Map

**What it is:** Precompute cumulative sums to answer range queries in O(1), often combined with hash maps for subarray sum problems.

**When to use it:**
- "Subarray sum equals k"
- Range sum queries
- "Number of subarrays with sum X"
- Frequency counting

**Key signals in problem statement:**
- "Subarray sum"
- "Range sum" or "cumulative"
- "Count subarrays"
- "Frequency" or "count occurrences"
- "Two sum" (unsorted)

**Template:**
```python
prefix = {0: 1}  # prefix_sum -> count
current_sum = 0
count = 0
for num in arr:
    current_sum += num
    if current_sum - target in prefix:
        count += prefix[current_sum - target]
    prefix[current_sum] = prefix.get(current_sum, 0) + 1
```

**Complexity:** O(n) time, O(n) space

**Example problems:** Subarray Sum Equals K, Two Sum (unsorted), Contiguous Array, Range Sum Query, Product of Array Except Self

---

## 29.2 Decision Flowchart

Use this flowchart when you see a new problem:

```
                        START
                          |
                    What is the input?
                   /        |        \
                Array     Graph/     String
                /Tree     Grid
                |           |           |
          Is it sorted?   Shortest    Substring/
           /       \      path?       Subarray?
         Yes       No     /    \       /      \
          |         |   Yes    No    Yes      No
    Binary Search   |    |      |     |        |
    or Two Ptrs     |   BFS   DFS  Sliding    Trie or
          |         |         or    Window    Backtracking
          |    What is asked?  Union-Find
          |    /     |     \
          |  Count  All   Optimize
          |  ways   combos (max/min)
          |   |      |       |
          |   DP   Back-   Greedy
          |        tracking  or DP?
          |                  |
          |           Can local optimal
          |           guarantee global?
          |            /          \
          |          Yes          No
          |           |            |
          |        Greedy         DP
          |
    +-----+------ More specific checks: ------+
    |                                          |
    Next greater/smaller?     Subarray sum?
          |                        |
    Monotonic Stack          Prefix Sum +
                             Hash Map
```

---

## 29.3 Keyword-to-Pattern Mapping Table

This table maps common problem keywords to the most likely pattern:

```
+-------------------------------------+------------------------+
| Keywords in Problem                 | Pattern                |
+-------------------------------------+------------------------+
| sorted array, pair, sum             | Two Pointers           |
| palindrome, reverse                 | Two Pointers           |
| in-place, remove duplicates         | Two Pointers           |
| linked list cycle, middle           | Two Pointers (fast/slow)|
+-------------------------------------+------------------------+
| subarray, substring, contiguous     | Sliding Window         |
| window, consecutive, at most k      | Sliding Window         |
| maximum/minimum length substring    | Sliding Window         |
+-------------------------------------+------------------------+
| sorted, O(log n), search            | Binary Search          |
| rotated sorted, find minimum        | Binary Search          |
| minimum satisfying condition        | Binary Search on Answer|
+-------------------------------------+------------------------+
| shortest path, minimum steps        | BFS                    |
| level order, nearest, closest       | BFS                    |
| grid + shortest, maze               | BFS                    |
+-------------------------------------+------------------------+
| all paths, connected, reachable     | DFS                    |
| island, region, flood fill          | DFS                    |
| tree depth, height, path sum        | DFS                    |
+-------------------------------------+------------------------+
| maximum/minimum + ways              | DP                     |
| how many ways, count paths          | DP                     |
| longest subsequence, edit distance  | DP                     |
| knapsack, partition, coin change    | DP                     |
+-------------------------------------+------------------------+
| interval, schedule, merge           | Greedy (+ sorting)     |
| minimum platforms, meeting rooms    | Greedy                 |
| jump game, gas station              | Greedy                 |
+-------------------------------------+------------------------+
| all permutations, combinations      | Backtracking           |
| generate all, subsets               | Backtracking           |
| N-Queens, Sudoku, constraint        | Backtracking           |
+-------------------------------------+------------------------+
| next greater, next smaller          | Monotonic Stack        |
| stock span, daily temperatures      | Monotonic Stack        |
| histogram, rectangle area           | Monotonic Stack        |
+-------------------------------------+------------------------+
| subarray sum equals k               | Prefix Sum + Hash Map  |
| range sum, cumulative               | Prefix Sum             |
| two sum (unsorted), frequency       | Hash Map               |
+-------------------------------------+------------------------+
| prefix match, autocomplete          | Trie                   |
| dictionary of words, spell check    | Trie                   |
+-------------------------------------+------------------------+
| connected components, merge groups  | Union-Find             |
| redundant edge, friend groups       | Union-Find             |
+-------------------------------------+------------------------+
| find unique, XOR trick              | Bit Manipulation       |
| power of 2, binary representation   | Bit Manipulation       |
+-------------------------------------+------------------------+
```

---

## 29.4 Ten Example Problems Matched to Patterns

### Example 1: "Find two numbers in a sorted array that add up to target"

**Keywords:** sorted array, two numbers, sum, target
**Pattern:** Two Pointers (opposite direction)
**Why:** Sorted array + pair sum is the classic two-pointer signal. Place pointers at both ends, move based on sum comparison.
**Time:** O(n)

---

### Example 2: "Find the longest substring with at most k distinct characters"

**Keywords:** longest, substring, at most k, distinct
**Pattern:** Sliding Window
**Why:** "Substring" + "longest" + "at most k" is a textbook sliding window. Expand right, shrink left when distinct count exceeds k.
**Time:** O(n)

---

### Example 3: "Find the minimum in a rotated sorted array"

**Keywords:** minimum, rotated sorted array
**Pattern:** Binary Search
**Why:** "Rotated sorted" + "find minimum" signals binary search. Compare mid with right to decide which half to search.
**Time:** O(log n)

---

### Example 4: "Find the shortest path from top-left to bottom-right of a grid"

**Keywords:** shortest path, grid
**Pattern:** BFS
**Why:** "Shortest path" in an unweighted grid is BFS. Each cell is a node, adjacent cells are edges. BFS guarantees shortest path.
**Time:** O(rows * cols)

---

### Example 5: "Count the number of islands in a 2D grid"

**Keywords:** count, islands, 2D grid
**Pattern:** DFS (or BFS)
**Why:** "Island" = connected component. For each unvisited land cell, run DFS to mark the entire island, increment count.
**Time:** O(rows * cols)

---

### Example 6: "Find the minimum number of coins to make amount n"

**Keywords:** minimum, coins, make amount
**Pattern:** Dynamic Programming
**Why:** "Minimum" + "coins" + "make amount" is the classic Coin Change DP. Subproblems overlap (making amount 5 uses solutions for amounts 1-4).
**Time:** O(amount * number of coins)

---

### Example 7: "Find the maximum number of non-overlapping intervals"

**Keywords:** maximum, non-overlapping, intervals
**Pattern:** Greedy
**Why:** "Intervals" + "non-overlapping" + "maximum" is activity selection. Sort by end time, greedily pick the earliest-ending interval that does not conflict.
**Time:** O(n log n)

---

### Example 8: "Generate all permutations of an array"

**Keywords:** generate all, permutations
**Pattern:** Backtracking
**Why:** "All permutations" means exhaustive search with choices at each position. Backtracking explores all orderings systematically.
**Time:** O(n!)

---

### Example 9: "For each element, find the next greater element"

**Keywords:** next greater element
**Pattern:** Monotonic Stack
**Why:** "Next greater" is the defining signal for monotonic stack. Process elements, pop from stack when current is greater.
**Time:** O(n)

---

### Example 10: "Count subarrays with sum equal to k"

**Keywords:** count, subarrays, sum equal to k
**Pattern:** Prefix Sum + Hash Map
**Why:** "Subarray sum equals k" is solved by tracking prefix sums in a hash map. If `current_sum - k` exists in the map, we found a valid subarray.
**Time:** O(n)

---

## 29.5 Combining Patterns

Many medium and hard problems require combining two or more patterns:

```
+-------------------------------+-------------------------+
| Combination                   | Example Problem         |
+-------------------------------+-------------------------+
| Binary Search + Greedy        | Koko Eating Bananas     |
| DFS + Backtracking            | Word Search             |
| BFS + Hash Map                | Word Ladder             |
| Sorting + Two Pointers        | 3Sum                    |
| Trie + DFS                    | Word Search II          |
| DP + Binary Search            | Longest Increasing Subseq|
| Union-Find + Sorting          | Accounts Merge          |
| Sliding Window + Hash Map     | Min Window Substring    |
| Greedy + Heap                 | Meeting Rooms II        |
| Prefix Sum + Binary Search    | Range Sum Query 2D      |
+-------------------------------+-------------------------+
```

### How to Spot Combinations

1. **Start with the primary pattern** (the one that matches the main question).
2. **Ask: "What sub-operation is expensive?"** --- If a step inside your main loop is slow, apply a secondary pattern to speed it up.
3. **Example:** In Word Search II, the main structure is DFS on the grid (primary pattern), but you need to check if the current path matches any word in a list. A trie (secondary pattern) makes that check O(1) instead of O(words).

---

## 29.6 The Five-Step Problem-Solving Process

When you encounter any problem, follow these steps:

```
Step 1: UNDERSTAND
  - Read the problem twice
  - Identify input/output types
  - Work through examples by hand
  - Ask: "What are the constraints?"

Step 2: MATCH
  - Circle keywords (see mapping table)
  - Match to 1-2 candidate patterns
  - Ask: "Have I seen a similar problem?"

Step 3: PLAN
  - Write pseudocode using the pattern template
  - Walk through your approach with an example
  - Estimate time/space complexity
  - Ask: "Does this complexity meet the constraints?"

Step 4: CODE
  - Translate pseudocode to code
  - Use meaningful variable names
  - Handle edge cases (empty input, single element, etc.)

Step 5: VERIFY
  - Trace through your code with the given examples
  - Test edge cases
  - Check off-by-one errors
  - Verify complexity matches expectations
```

---

## Common Mistakes

1. **Jumping to code too quickly.** Spend 5-10 minutes understanding and planning. Wrong pattern choice wastes more time than careful analysis.

2. **Using DP when greedy works.** If the problem has the greedy-choice property (local optimal = global optimal), DP is overkill. Greedy is simpler and often faster.

3. **Using DFS when BFS is needed.** DFS does not guarantee shortest path. If the problem asks for "minimum steps," use BFS.

4. **Forgetting edge cases.** Empty arrays, single elements, negative numbers, duplicates. These trip up correct algorithms with incorrect boundary handling.

5. **Not recognizing combined patterns.** If your O(n^2) solution is too slow, ask: "Can I replace the inner loop with binary search (O(n log n)) or a hash map (O(n))?"

---

## Best Practices

- **Build a problem log.** After solving each problem, write down: problem name, pattern used, key insight, mistakes made. Review regularly.
- **Practice pattern recognition separately from coding.** Read problem statements and identify the pattern without writing code. This builds speed.
- **Start with brute force.** Even if you recognize the pattern, articulating the brute-force solution first shows your thought process and helps verify the optimized solution.
- **Learn patterns in order of frequency.** Two Pointers and Hash Map appear most often. DP and Backtracking appear in harder problems. Prioritize accordingly.
- **Time yourself.** In interviews, you have 20-25 minutes to code. Practice under time pressure to build comfort.

---

## Quick Summary

| Pattern | Primary Signal | Typical Complexity |
|---------|---------------|-------------------|
| Two Pointers | Sorted array, pair sum, palindrome | O(n) |
| Sliding Window | Subarray/substring, contiguous, at most k | O(n) |
| Binary Search | Sorted, O(log n), min/max condition | O(log n) |
| BFS | Shortest path, minimum steps, level order | O(V+E) |
| DFS | All paths, connected, islands, tree traversal | O(V+E) |
| DP | Optimize + count ways, subsequence, knapsack | O(n^2) |
| Greedy | Intervals, scheduling, local=global | O(n log n) |
| Backtracking | All permutations/combinations, constraints | O(2^n) or O(n!) |
| Monotonic Stack | Next greater/smaller, histogram | O(n) |
| Prefix Sum | Subarray sum, range query, frequency | O(n) |

---

## Key Points

- Most interview problems fit into about 10 patterns. Recognizing the pattern is half the battle.
- Keywords in the problem statement are your strongest signal. "Sorted + pair" = Two Pointers. "Substring + longest" = Sliding Window. "Minimum steps" = BFS.
- When the primary pattern gives O(n^2), look for a secondary pattern (binary search, hash map, monotonic stack) to optimize the inner loop.
- Always start with understanding and pattern matching before writing code. Five minutes of planning saves twenty minutes of debugging.
- Build muscle memory by solving 3-5 problems per pattern. Quantity matters, but deliberate reflection matters more.

---

## Practice Questions

1. Given the problem "Find the kth smallest element in a BST," which pattern would you use? Why not binary search?

2. A problem asks: "Find the minimum window in string S that contains all characters of string T." Identify the primary and secondary patterns.

3. How would you decide between BFS and DFS for a problem that asks "find if a path exists between two nodes"?

4. Why is the greedy approach incorrect for the 0/1 Knapsack problem? What property does it lack?

5. A problem gives you a stream of numbers and asks for the median at each step. Which data structure/pattern would you use?

---

## LeetCode-Style Problems

### Problem 1: Pattern Identification Exercise

For each problem below, identify the primary pattern and explain why:

**a) "Given an array of intervals, merge overlapping intervals."**
- **Pattern:** Greedy (sort by start time, merge greedily)
- **Why:** Sorting + linear scan. Each interval is processed once.

**b) "Given a binary tree, find the maximum path sum."**
- **Pattern:** DFS (post-order traversal)
- **Why:** Tree problem requiring path computation. DFS naturally explores all root-to-leaf paths.

**c) "Given a string, find the length of the longest palindromic substring."**
- **Pattern:** DP or Expand Around Center (Two Pointers variant)
- **Why:** Subproblem overlap (palindrome check for substrings). Expand around center is O(n^2) with O(1) space.

---

### Problem 2: Multi-Pattern Problem

**Problem:** "Given a list of words and a board, find all words that can be formed by tracing adjacent cells."

**Patterns:** Trie + DFS (Backtracking)
**Approach:**
1. Build a trie from the word list (O(total characters))
2. For each cell on the board, run DFS
3. At each DFS step, follow the trie --- if the current path is not a prefix in the trie, prune

```python
# This is Word Search II (LeetCode 212)
# Primary: DFS on the grid
# Secondary: Trie for efficient prefix checking
# Combined: Trie-guided DFS with backtracking
```

---

### Problem 3: Optimization Challenge

**Problem:** "Find the number of pairs (i, j) where i < j and nums[i] + nums[j] == target."

**Brute force:** O(n^2) --- check all pairs.

**Optimized approaches:**
1. **Hash Map:** O(n) time, O(n) space. For each element, check if `target - element` is in the map.
2. **Sort + Two Pointers:** O(n log n) time, O(1) space. Sort first, then use opposite-direction pointers.

```python
# Hash Map approach
def count_pairs(nums, target):
    seen = {}
    count = 0
    for num in nums:
        complement = target - num
        if complement in seen:
            count += seen[complement]
        seen[num] = seen.get(num, 0) + 1
    return count

print(count_pairs([1, 5, 7, -1, 5], 6))  # Output: 3
# Pairs: (1,5), (1,5), (7,-1)
```

---

## What Is Next?

You now have a systematic framework for attacking any algorithm problem. You know the 10 core patterns, their signals, and how to combine them.

In the next chapter, we focus on **Interview Strategies** --- the non-technical skills that are just as important as coding ability. How to clarify problems, manage time, communicate your thinking, and handle moments when you get stuck. Patterns get you the solution; strategy gets you the job.
