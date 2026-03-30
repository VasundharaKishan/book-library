# Chapter 31: 50 Must-Solve Problems

## What You Will Learn

- A curated list of 50 essential coding interview problems organized by topic
- The difficulty level, pattern, and key insight for each problem
- Time and space complexity for each solution approach
- A structured practice roadmap from easy to hard
- How to use this list for efficient interview preparation

## Why This Chapter Matters

With thousands of problems available online, it is easy to get lost in an endless grind. More problems does not mean better preparation. What matters is solving the right problems --- the ones that teach you reusable patterns.

This chapter gives you 50 carefully selected problems that cover the most commonly tested topics and patterns. Each problem has a one-line key insight that captures the essential idea. If you can solve all 50 and articulate the key insight for each, you are ready for the vast majority of coding interviews.

These are not full solutions. The goal is to give you a roadmap: know what to practice, in what order, and what to focus on.

---

## How to Use This Chapter

1. **Work through problems by topic.** Complete one section before moving to the next.
2. **Attempt each problem for 20-30 minutes** before looking at the key insight.
3. **After solving, verify:** Can you explain the approach in 2 sentences? Can you code it from scratch?
4. **Track your progress.** Mark each problem as: Solved, Needs Review, or Stuck.
5. **Revisit "Needs Review" problems** after 3 days and 7 days (spaced repetition).

### Difficulty Guide

```
+--------+------------------------------------------+
| Rating | Meaning                                  |
+--------+------------------------------------------+
| Easy   | Should solve in 15 min after studying     |
| Medium | Core interview difficulty, 20-30 min      |
| Hard   | Stretch goal, combines multiple patterns   |
+--------+------------------------------------------+
```

---

## Arrays (8 Problems)

### 1. Two Sum

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Hash Map |
| Key Insight | For each number, check if `target - num` exists in a hash map. One pass, O(n). |
| Complexity | Time O(n), Space O(n) |

### 2. Best Time to Buy and Sell Stock

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Greedy / One Pass |
| Key Insight | Track the minimum price seen so far. At each price, compute profit as `price - min_so_far`. Update max profit. |
| Complexity | Time O(n), Space O(1) |

### 3. Product of Array Except Self

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Prefix / Suffix Products |
| Key Insight | Build left products and right products in two passes. `result[i] = left_product[i] * right_product[i]`. No division needed. |
| Complexity | Time O(n), Space O(1) excluding output |

### 4. Maximum Subarray (Kadane's Algorithm)

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Dynamic Programming / Greedy |
| Key Insight | At each position, decide: extend the current subarray or start fresh. `current = max(num, current + num)`. |
| Complexity | Time O(n), Space O(1) |

### 5. Container With Most Water

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Two Pointers (opposite) |
| Key Insight | Start pointers at both ends. Always move the pointer with the shorter height --- moving the taller one can never increase area. |
| Complexity | Time O(n), Space O(1) |

### 6. 3Sum

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Sort + Two Pointers |
| Key Insight | Sort the array. Fix one element, then use two pointers for the remaining pair. Skip duplicates to avoid duplicate triplets. |
| Complexity | Time O(n^2), Space O(1) |

### 7. Merge Intervals

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Greedy (Sort) |
| Key Insight | Sort by start time. If current interval overlaps with previous, merge by extending the end. Otherwise, add as new interval. |
| Complexity | Time O(n log n), Space O(n) |

### 8. Trapping Rain Water

| Field | Detail |
|-------|--------|
| Difficulty | Hard |
| Pattern | Two Pointers |
| Key Insight | Water at each position = `min(left_max, right_max) - height`. Two pointers from both ends tracking left/right max. |
| Complexity | Time O(n), Space O(1) |

---

## Strings (5 Problems)

### 9. Valid Palindrome

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Two Pointers |
| Key Insight | Two pointers from both ends, skip non-alphanumeric characters, compare case-insensitively. |
| Complexity | Time O(n), Space O(1) |

### 10. Valid Anagram

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Hash Map (Frequency Count) |
| Key Insight | Count character frequencies. Two strings are anagrams if and only if they have identical frequency maps. |
| Complexity | Time O(n), Space O(1) --- fixed 26-char alphabet |

### 11. Longest Substring Without Repeating Characters

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Sliding Window + Hash Set |
| Key Insight | Expand window right. When duplicate found, shrink from left until no duplicate. Track max window size. |
| Complexity | Time O(n), Space O(min(n, alphabet)) |

### 12. Group Anagrams

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Hash Map + Sorting |
| Key Insight | Two words are anagrams if their sorted characters are identical. Use sorted string as hash key to group. |
| Complexity | Time O(n * k log k), Space O(n * k) |

### 13. Minimum Window Substring

| Field | Detail |
|-------|--------|
| Difficulty | Hard |
| Pattern | Sliding Window + Hash Map |
| Key Insight | Expand right to include all required characters. Shrink left to find minimum window. Track "formed" count vs "required" count. |
| Complexity | Time O(n + m), Space O(n + m) |

---

## Linked Lists (5 Problems)

### 14. Reverse Linked List

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Iterative / Recursive |
| Key Insight | Three pointers: prev, curr, next. At each step, reverse curr's pointer, then advance all three. |
| Complexity | Time O(n), Space O(1) iterative |

### 15. Linked List Cycle

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Fast/Slow Pointers |
| Key Insight | Slow moves 1 step, fast moves 2. If they meet, there is a cycle. If fast reaches null, no cycle. |
| Complexity | Time O(n), Space O(1) |

### 16. Merge Two Sorted Lists

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Two Pointers / Merge |
| Key Insight | Compare heads of both lists. Append the smaller one to result. When one list is exhausted, append the rest of the other. |
| Complexity | Time O(n + m), Space O(1) |

### 17. Remove Nth Node From End

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Two Pointers (gap technique) |
| Key Insight | Advance the first pointer n steps ahead. Then move both together. When first reaches end, second is at the target. |
| Complexity | Time O(n), Space O(1) |

### 18. Merge K Sorted Lists

| Field | Detail |
|-------|--------|
| Difficulty | Hard |
| Pattern | Min Heap / Divide and Conquer |
| Key Insight | Put the head of each list into a min heap. Pop the smallest, add its next to the heap. Repeat until empty. |
| Complexity | Time O(n log k), Space O(k) |

---

## Trees (7 Problems)

### 19. Maximum Depth of Binary Tree

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | DFS (Recursion) |
| Key Insight | Depth = 1 + max(depth of left, depth of right). Base case: null node has depth 0. |
| Complexity | Time O(n), Space O(h) |

### 20. Invert Binary Tree

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | DFS (Recursion) |
| Key Insight | At each node, swap left and right children. Then recursively invert subtrees. |
| Complexity | Time O(n), Space O(h) |

### 21. Binary Tree Level Order Traversal

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | BFS (Queue) |
| Key Insight | Use a queue. Process all nodes at current level (queue size at start of level), then move to next level. |
| Complexity | Time O(n), Space O(n) |

### 22. Validate Binary Search Tree

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | DFS with Range |
| Key Insight | Each node must be within a valid range (min, max). Left child narrows the max. Right child narrows the min. |
| Complexity | Time O(n), Space O(h) |

### 23. Lowest Common Ancestor of BST

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | BST Property |
| Key Insight | If both nodes are less than current, go left. If both greater, go right. Otherwise, current node is the LCA. |
| Complexity | Time O(h), Space O(1) iterative |

### 24. Serialize and Deserialize Binary Tree

| Field | Detail |
|-------|--------|
| Difficulty | Hard |
| Pattern | BFS or DFS + String Encoding |
| Key Insight | Preorder DFS with null markers. Serialize: node,left,right. Deserialize: read values sequentially, use null to terminate branches. |
| Complexity | Time O(n), Space O(n) |

### 25. Binary Tree Maximum Path Sum

| Field | Detail |
|-------|--------|
| Difficulty | Hard |
| Pattern | DFS (Post-order) |
| Key Insight | At each node, compute max single-path sum (node + best child). Update global max with node + left + right (path through node). |
| Complexity | Time O(n), Space O(h) |

---

## Graphs (5 Problems)

### 26. Number of Islands

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | DFS / BFS on Grid |
| Key Insight | For each unvisited '1', run DFS/BFS to mark entire island as visited. Count how many times you start a new traversal. |
| Complexity | Time O(rows * cols), Space O(rows * cols) |

### 27. Clone Graph

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | DFS/BFS + Hash Map |
| Key Insight | Use a hash map to track original-to-clone mapping. For each node, create clone if not seen, then recursively clone neighbors. |
| Complexity | Time O(V + E), Space O(V) |

### 28. Course Schedule (Cycle Detection)

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Topological Sort / DFS |
| Key Insight | Build adjacency list. Use DFS with three states (unvisited, in-progress, completed). A back edge to an in-progress node means a cycle. |
| Complexity | Time O(V + E), Space O(V + E) |

### 29. Pacific Atlantic Water Flow

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Multi-source BFS/DFS |
| Key Insight | Instead of flowing water downhill from each cell, flow uphill from ocean borders. Find cells reachable from both oceans. |
| Complexity | Time O(rows * cols), Space O(rows * cols) |

### 30. Word Ladder

| Field | Detail |
|-------|--------|
| Difficulty | Hard |
| Pattern | BFS (Shortest Path) |
| Key Insight | Each word is a node. Two words are connected if they differ by one character. BFS from start word finds shortest transformation sequence. |
| Complexity | Time O(n * m * 26), Space O(n * m) |

---

## Dynamic Programming (7 Problems)

### 31. Climbing Stairs

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | DP (Fibonacci variant) |
| Key Insight | `dp[i] = dp[i-1] + dp[i-2]`. You can reach step i from step i-1 (one step) or step i-2 (two steps). |
| Complexity | Time O(n), Space O(1) |

### 32. Coin Change

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | DP (Unbounded Knapsack) |
| Key Insight | `dp[amount] = min(dp[amount], dp[amount - coin] + 1)` for each coin. Build from amount 0 up. |
| Complexity | Time O(amount * coins), Space O(amount) |

### 33. Longest Common Subsequence

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | 2D DP |
| Key Insight | If chars match, `dp[i][j] = dp[i-1][j-1] + 1`. If not, `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`. |
| Complexity | Time O(m * n), Space O(m * n) |

### 34. Word Break

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | DP + Hash Set |
| Key Insight | `dp[i]` = can we segment `s[0:i]`? For each position j < i, if `dp[j]` is true and `s[j:i]` is in the dictionary, then `dp[i]` is true. |
| Complexity | Time O(n^2 * m), Space O(n) |

### 35. House Robber

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | DP |
| Key Insight | Cannot rob adjacent houses. `dp[i] = max(dp[i-1], dp[i-2] + nums[i])`. Rob current + skip one, or skip current. |
| Complexity | Time O(n), Space O(1) |

### 36. Longest Increasing Subsequence

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | DP or DP + Binary Search |
| Key Insight | DP: `dp[i]` = length of LIS ending at index i. For O(n log n): maintain a "tails" array and use binary search to place elements. |
| Complexity | Time O(n^2) or O(n log n), Space O(n) |

### 37. Edit Distance

| Field | Detail |
|-------|--------|
| Difficulty | Hard |
| Pattern | 2D DP |
| Key Insight | Three operations: insert, delete, replace. `dp[i][j]` = min edits to convert `word1[0:i]` to `word2[0:j]`. If chars match, no edit needed. |
| Complexity | Time O(m * n), Space O(m * n) |

---

## Binary Search (4 Problems)

### 38. Binary Search

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Binary Search |
| Key Insight | Compare target with middle element. Eliminate half the search space each step. Use `mid = left + (right - left) // 2` to avoid overflow. |
| Complexity | Time O(log n), Space O(1) |

### 39. Search in Rotated Sorted Array

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Modified Binary Search |
| Key Insight | One half is always sorted. Check which half is sorted, then check if target falls in that half. Narrow search accordingly. |
| Complexity | Time O(log n), Space O(1) |

### 40. Find Minimum in Rotated Sorted Array

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Binary Search |
| Key Insight | Compare mid with right. If `nums[mid] > nums[right]`, minimum is in the right half. Otherwise, it is in the left half (including mid). |
| Complexity | Time O(log n), Space O(1) |

### 41. Koko Eating Bananas

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Binary Search on Answer |
| Key Insight | Binary search on eating speed k (1 to max pile). For each k, check if Koko can finish in h hours. Find minimum valid k. |
| Complexity | Time O(n * log(max pile)), Space O(1) |

---

## Stack and Queue (4 Problems)

### 42. Valid Parentheses

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Stack |
| Key Insight | Push opening brackets onto stack. For closing brackets, check if top of stack matches. If mismatch or stack empty, invalid. |
| Complexity | Time O(n), Space O(n) |

### 43. Daily Temperatures

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Monotonic Stack (Decreasing) |
| Key Insight | Push indices onto stack. When current temp is higher than stack top, pop and compute days difference. Stack maintains decreasing temps. |
| Complexity | Time O(n), Space O(n) |

### 44. Largest Rectangle in Histogram

| Field | Detail |
|-------|--------|
| Difficulty | Hard |
| Pattern | Monotonic Stack |
| Key Insight | For each bar, find the nearest shorter bar on left and right using a stack. Width = right boundary - left boundary - 1. Area = height * width. |
| Complexity | Time O(n), Space O(n) |

### 45. Implement Queue Using Stacks

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Two Stacks |
| Key Insight | Use an "in" stack for push and an "out" stack for pop. Transfer from in to out only when out is empty. Amortized O(1) per operation. |
| Complexity | Time O(1) amortized, Space O(n) |

---

## Sliding Window (3 Problems)

### 46. Maximum Sum Subarray of Size K

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Fixed Sliding Window |
| Key Insight | Add the new element entering the window, subtract the element leaving. Track the maximum sum seen. |
| Complexity | Time O(n), Space O(1) |

### 47. Longest Repeating Character Replacement

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Sliding Window + Frequency Map |
| Key Insight | Window is valid if `window_size - max_frequency <= k`. If invalid, shrink from left. Track the max frequency character in window. |
| Complexity | Time O(n), Space O(1) |

### 48. Sliding Window Maximum

| Field | Detail |
|-------|--------|
| Difficulty | Hard |
| Pattern | Monotonic Deque |
| Key Insight | Maintain a deque of indices in decreasing order of values. Remove indices outside the window. Front of deque is always the maximum. |
| Complexity | Time O(n), Space O(k) |

---

## Two Pointers (2 Problems)

### 49. Move Zeroes

| Field | Detail |
|-------|--------|
| Difficulty | Easy |
| Pattern | Two Pointers (Same Direction) |
| Key Insight | Writer pointer tracks next non-zero position. Reader scans every element. Swap non-zeroes to the writer position. |
| Complexity | Time O(n), Space O(1) |

### 50. Sort Colors

| Field | Detail |
|-------|--------|
| Difficulty | Medium |
| Pattern | Three Pointers (Dutch National Flag) |
| Key Insight | Three pointers: low (next 0 position), mid (current), high (next 2 position). Swap 0s left, 2s right, skip 1s. |
| Complexity | Time O(n), Space O(1) |

---

## Progress Tracker

Copy this table and mark your progress:

```
+----+-------------------------------------+--------+--------+
| #  | Problem                             | Status | Review |
+----+-------------------------------------+--------+--------+
| 1  | Two Sum                             | [ ]    | [ ]    |
| 2  | Best Time to Buy and Sell Stock      | [ ]    | [ ]    |
| 3  | Product of Array Except Self         | [ ]    | [ ]    |
| 4  | Maximum Subarray                     | [ ]    | [ ]    |
| 5  | Container With Most Water            | [ ]    | [ ]    |
| 6  | 3Sum                                | [ ]    | [ ]    |
| 7  | Merge Intervals                      | [ ]    | [ ]    |
| 8  | Trapping Rain Water                  | [ ]    | [ ]    |
| 9  | Valid Palindrome                     | [ ]    | [ ]    |
| 10 | Valid Anagram                        | [ ]    | [ ]    |
| 11 | Longest Substring No Repeating       | [ ]    | [ ]    |
| 12 | Group Anagrams                       | [ ]    | [ ]    |
| 13 | Minimum Window Substring             | [ ]    | [ ]    |
| 14 | Reverse Linked List                  | [ ]    | [ ]    |
| 15 | Linked List Cycle                    | [ ]    | [ ]    |
| 16 | Merge Two Sorted Lists               | [ ]    | [ ]    |
| 17 | Remove Nth Node From End             | [ ]    | [ ]    |
| 18 | Merge K Sorted Lists                 | [ ]    | [ ]    |
| 19 | Maximum Depth of Binary Tree         | [ ]    | [ ]    |
| 20 | Invert Binary Tree                   | [ ]    | [ ]    |
| 21 | Binary Tree Level Order Traversal    | [ ]    | [ ]    |
| 22 | Validate Binary Search Tree          | [ ]    | [ ]    |
| 23 | Lowest Common Ancestor of BST        | [ ]    | [ ]    |
| 24 | Serialize/Deserialize Binary Tree    | [ ]    | [ ]    |
| 25 | Binary Tree Maximum Path Sum         | [ ]    | [ ]    |
| 26 | Number of Islands                    | [ ]    | [ ]    |
| 27 | Clone Graph                          | [ ]    | [ ]    |
| 28 | Course Schedule                      | [ ]    | [ ]    |
| 29 | Pacific Atlantic Water Flow          | [ ]    | [ ]    |
| 30 | Word Ladder                          | [ ]    | [ ]    |
| 31 | Climbing Stairs                      | [ ]    | [ ]    |
| 32 | Coin Change                          | [ ]    | [ ]    |
| 33 | Longest Common Subsequence           | [ ]    | [ ]    |
| 34 | Word Break                           | [ ]    | [ ]    |
| 35 | House Robber                         | [ ]    | [ ]    |
| 36 | Longest Increasing Subsequence       | [ ]    | [ ]    |
| 37 | Edit Distance                        | [ ]    | [ ]    |
| 38 | Binary Search                        | [ ]    | [ ]    |
| 39 | Search in Rotated Sorted Array       | [ ]    | [ ]    |
| 40 | Find Min in Rotated Sorted Array     | [ ]    | [ ]    |
| 41 | Koko Eating Bananas                  | [ ]    | [ ]    |
| 42 | Valid Parentheses                    | [ ]    | [ ]    |
| 43 | Daily Temperatures                   | [ ]    | [ ]    |
| 44 | Largest Rectangle in Histogram       | [ ]    | [ ]    |
| 45 | Implement Queue Using Stacks         | [ ]    | [ ]    |
| 46 | Maximum Sum Subarray of Size K       | [ ]    | [ ]    |
| 47 | Longest Repeating Char Replacement   | [ ]    | [ ]    |
| 48 | Sliding Window Maximum               | [ ]    | [ ]    |
| 49 | Move Zeroes                          | [ ]    | [ ]    |
| 50 | Sort Colors                          | [ ]    | [ ]    |
+----+-------------------------------------+--------+--------+
```

---

## Common Mistakes

1. **Solving problems randomly.** Without structure, you practice the same patterns repeatedly and miss others. Follow the topic order.

2. **Looking at solutions too quickly.** Spend at least 20 minutes struggling before checking hints. The struggle is where learning happens.

3. **Not reviewing solved problems.** Solving once is not enough. Review after 3 and 7 days to move the solution into long-term memory.

4. **Skipping easy problems.** Easy problems build confidence and reinforce fundamentals. They also appear in real interviews.

5. **Only doing hard problems.** Most interviews feature medium-difficulty problems. Hard problems are stretch goals, not the core.

---

## Best Practices

- **Solve in order within each topic.** Easy problems build intuition for the medium and hard ones.
- **After each problem, write a one-sentence key insight.** If you cannot summarize the approach in one sentence, you have not fully understood it.
- **Time yourself.** 15 minutes for easy, 25 minutes for medium, 40 minutes for hard.
- **Alternate topics** to avoid fatigue. Do not solve 7 DP problems in a row.
- **Celebrate progress.** Mark completed problems. Seeing checkmarks builds momentum.

---

## Quick Summary

| Topic | Count | Easy | Medium | Hard |
|-------|-------|------|--------|------|
| Arrays | 8 | 2 | 4 | 2 |
| Strings | 5 | 2 | 2 | 1 |
| Linked Lists | 5 | 3 | 1 | 1 |
| Trees | 7 | 2 | 3 | 2 |
| Graphs | 5 | 0 | 4 | 1 |
| DP | 7 | 1 | 5 | 1 |
| Binary Search | 4 | 1 | 3 | 0 |
| Stack/Queue | 4 | 2 | 1 | 1 |
| Sliding Window | 3 | 1 | 1 | 1 |
| Two Pointers | 2 | 1 | 1 | 0 |
| **Total** | **50** | **15** | **25** | **10** |

---

## Key Points

- Quality over quantity. 50 well-understood problems beats 200 poorly understood ones.
- Each problem teaches a reusable pattern. The specific problem matters less than the technique it represents.
- The key insight is the most important takeaway. If you can state it from memory, you can reconstruct the solution.
- Use spaced repetition to move solutions from short-term to long-term memory.
- Track your progress visually to maintain motivation and identify weak areas.

---

## What Is Next?

This problem set is your training ground. Work through it methodically, and you will be prepared for the patterns that appear in real interviews.

In the final chapter, we provide a comprehensive **Glossary** of 80+ terms from this book --- a quick-reference guide for every data structure, algorithm, and concept you have learned. It is also a good way to self-test: if you can explain every term in the glossary, you have truly mastered this material.
