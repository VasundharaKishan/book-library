# Chapter 20: Dynamic Programming Introduction

## What You Will Learn

- What dynamic programming (DP) is and why it is one of the most powerful algorithmic techniques
- The two key properties that make a problem solvable with DP: overlapping subproblems and optimal substructure
- The difference between top-down (memoization) and bottom-up (tabulation) approaches
- How to transform a slow recursive solution into an efficient DP solution
- The DP Recipe: a systematic 5-step process for solving any DP problem
- How to solve classic DP problems like Fibonacci and Climbing Stairs

## Why This Chapter Matters

Dynamic programming is the single most important topic in coding interviews. It appears in roughly 20-30% of medium and hard interview problems. Beyond interviews, DP is the engine behind countless real-world systems: spell checkers, DNA sequence alignment, speech recognition, resource allocation, and financial modeling.

Despite its reputation for being difficult, DP is really just one simple idea: **if you have already solved a subproblem, write down the answer so you never solve it again.** Think of a student doing homework. If problem 5 requires the answer to problem 3, and you already solved problem 3, you do not redo it. You look at your notes.

This chapter takes you from zero DP knowledge to confidently solving foundational DP problems. The patterns you learn here form the basis for the more advanced DP patterns in Chapter 21.

---

## 20.1 What Is Dynamic Programming?

Dynamic programming is an optimization technique that solves complex problems by:

1. Breaking them into smaller **overlapping subproblems**
2. Solving each subproblem **only once**
3. **Storing** the results for future use

The name "dynamic programming" was coined by Richard Bellman in the 1950s. He chose the word "dynamic" to sound impressive to his bosses (seriously!). A more descriptive name would be "smart recursion with a notebook."

### The Homework Analogy

```
Without DP (naive recursion):
  Teacher: "What is fib(5)?"
  Student: "I need fib(4) and fib(3)..."
           "For fib(4), I need fib(3) and fib(2)..."
           "For fib(3) again, I need fib(2) and fib(1)..."
           (Keeps re-solving the same problems!)

With DP (memoization):
  Teacher: "What is fib(5)?"
  Student: "I need fib(4) and fib(3)."
           "For fib(4), I need fib(3) and fib(2)."
           "Wait -- I already solved fib(3). Let me check my notes."
           "And I already have fib(2). Done!"
           (Each problem solved exactly once!)
```

---

## 20.2 The Two Key Properties

A problem can be solved with DP if and only if it has these two properties:

### Property 1: Overlapping Subproblems

The same smaller problems are solved multiple times. This is what makes caching worthwhile.

```
Fibonacci recursion tree for fib(5):

                    fib(5)
                   /      \
              fib(4)      fib(3)       <-- fib(3) computed twice!
             /     \      /    \
         fib(3)  fib(2) fib(2) fib(1)  <-- fib(2) computed 3 times!
        /    \    /  \    /  \
    fib(2) fib(1) f(1) f(0) f(1) f(0)
    /   \
  f(1) f(0)

Total calls without DP: 15
Total calls with DP:     5  (one per unique subproblem)
```

**Without overlap, DP gives no benefit.** Binary search, for example, has non-overlapping subproblems (each recursive call works on a different half), so DP does not apply.

### Property 2: Optimal Substructure

The optimal solution to the problem can be built from optimal solutions to its subproblems.

```
Optimal substructure example:
  Shortest path from A to C through B:
    optimal(A->C) = optimal(A->B) + optimal(B->C)

  If the best path from A to C goes through B,
  then it must use the best path from A to B
  AND the best path from B to C.

NOT optimal substructure:
  Longest simple path (no repeated vertices):
    longest(A->C) != longest(A->B) + longest(B->C)
    because the subpaths might share vertices!
```

---

## 20.3 Top-Down vs Bottom-Up

There are two ways to implement DP:

### Top-Down (Memoization)

Start with the original problem, break it down recursively, and **cache** (memoize) results as you compute them.

```
Approach: Start at fib(5), recurse down, cache on the way back up.

  fib(5) --> needs fib(4) and fib(3)
  fib(4) --> needs fib(3) and fib(2)
  fib(3) --> needs fib(2) and fib(1)
  fib(2) --> needs fib(1) and fib(0)  --> returns 1
  fib(1) --> base case --> returns 1
  fib(0) --> base case --> returns 0

  Now fib(2) = 1, cached!
  fib(3) = fib(2) + fib(1) = 1 + 1 = 2, cached!
  fib(4) = fib(3) + fib(2) = 2 + 1 = 3, cached!  (fib(3) from cache!)
  fib(5) = fib(4) + fib(3) = 3 + 2 = 5, cached!  (both from cache!)
```

**Pros:** Natural to write (just add caching to recursion). Only solves subproblems that are actually needed.

**Cons:** Recursion overhead (function call stack). Risk of stack overflow for deep recursion.

### Bottom-Up (Tabulation)

Start with the smallest subproblems, solve them first, and **build up** to the original problem using a table.

```
Approach: Fill a table from fib(0) up to fib(5).

  Index:  0   1   2   3   4   5
  Value: [0] [1] [ ] [ ] [ ] [ ]    <-- base cases filled

  Step 1: fib(2) = fib(1) + fib(0) = 1
  Index:  0   1   2   3   4   5
  Value: [0] [1] [1] [ ] [ ] [ ]

  Step 2: fib(3) = fib(2) + fib(1) = 2
  Index:  0   1   2   3   4   5
  Value: [0] [1] [1] [2] [ ] [ ]

  Step 3: fib(4) = fib(3) + fib(2) = 3
  Index:  0   1   2   3   4   5
  Value: [0] [1] [1] [2] [3] [ ]

  Step 4: fib(5) = fib(4) + fib(3) = 5
  Index:  0   1   2   3   4   5
  Value: [0] [1] [1] [2] [3] [5]

  Answer: dp[5] = 5
```

**Pros:** No recursion overhead. Often faster in practice due to better cache performance. Easier to optimize space.

**Cons:** Must determine the correct order to fill the table. May solve subproblems that are not needed.

### Comparison

| Feature | Top-Down (Memoization) | Bottom-Up (Tabulation) |
|---------|----------------------|----------------------|
| Implementation | Recursion + cache | Iterative + table |
| Order of solving | Problem decides order | You decide order |
| Subproblems solved | Only needed ones | All of them |
| Stack overflow risk | Yes (deep recursion) | No |
| Space optimization | Harder | Easier |
| Easier to write | Usually yes | Sometimes |

---

## 20.4 Fibonacci: From Naive to Optimized

Let us trace the complete evolution of a DP solution using the Fibonacci sequence.

### Approach 1: Naive Recursion (Exponential)

**Python:**

```python
def fib_naive(n):
    """Naive recursive Fibonacci. DO NOT use for large n!"""
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


# Test
for i in range(10):
    print(f"fib({i}) = {fib_naive(i)}")
```

**Output:**

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

**The problem:** The recursion tree grows exponentially.

```
Number of calls for fib(n):

  n:     5     10      20       30         40         50
calls:  15    177   21,891  2,692,537  331,160,281  ~10^10

Time complexity: O(2^n)  <-- TERRIBLE!
```

### Approach 2: Top-Down with Memoization (Linear)

**Python:**

```python
def fib_memo(n, memo=None):
    """Top-down Fibonacci with memoization."""
    if memo is None:
        memo = {}

    if n <= 1:
        return n

    # Check if already computed
    if n in memo:
        return memo[n]

    # Compute and store
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


# Alternative using Python decorator
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo_decorator(n):
    """Top-down Fibonacci using Python's built-in cache."""
    if n <= 1:
        return n
    return fib_memo_decorator(n - 1) + fib_memo_decorator(n - 2)


# Test
print(f"fib(10) = {fib_memo(10)}")
print(f"fib(50) = {fib_memo(50)}")
print(f"fib(100) = {fib_memo(100)}")
```

**Output:**

```
fib(10) = 55
fib(50) = 12586269025
fib(100) = 354224848179261915075
```

**Java:**

```java
import java.util.HashMap;
import java.util.Map;

public class FibonacciMemo {

    private Map<Integer, Long> memo = new HashMap<>();

    public long fib(int n) {
        if (n <= 1) return n;

        if (memo.containsKey(n)) {
            return memo.get(n);
        }

        long result = fib(n - 1) + fib(n - 2);
        memo.put(n, result);
        return result;
    }

    public static void main(String[] args) {
        FibonacciMemo solver = new FibonacciMemo();
        System.out.println("fib(10) = " + solver.fib(10));
        System.out.println("fib(50) = " + solver.fib(50));
    }
}
```

**Output:**

```
fib(10) = 55
fib(50) = 12586269025
```

**Time complexity: O(n)** -- each subproblem solved exactly once.

**Space complexity: O(n)** -- for the memo dictionary and the recursion stack.

### Approach 3: Bottom-Up with Tabulation (Linear)

**Python:**

```python
def fib_table(n):
    """Bottom-up Fibonacci with tabulation."""
    if n <= 1:
        return n

    # Create table
    dp = [0] * (n + 1)
    dp[0] = 0
    dp[1] = 1

    # Fill table from bottom up
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


# Test
print(f"fib(10) = {fib_table(10)}")
print(f"fib(50) = {fib_table(50)}")
```

**Output:**

```
fib(10) = 55
fib(50) = 12586269025
```

**Java:**

```java
public class FibonacciTable {

    public static long fib(int n) {
        if (n <= 1) return n;

        long[] dp = new long[n + 1];
        dp[0] = 0;
        dp[1] = 1;

        for (int i = 2; i <= n; i++) {
            dp[i] = dp[i - 1] + dp[i - 2];
        }

        return dp[n];
    }

    public static void main(String[] args) {
        System.out.println("fib(10) = " + fib(10));
        System.out.println("fib(50) = " + fib(50));
    }
}
```

**Output:**

```
fib(10) = 55
fib(50) = 12586269025
```

**Time complexity: O(n).** Space complexity: O(n).

### Approach 4: Space-Optimized Bottom-Up (Constant Space)

Key insight: we only ever need the **two most recent values**, not the entire table.

**Python:**

```python
def fib_optimized(n):
    """Space-optimized Fibonacci. O(1) space!"""
    if n <= 1:
        return n

    prev2 = 0  # fib(0)
    prev1 = 1  # fib(1)

    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current

    return prev1


# Test
for i in range(10):
    print(f"fib({i}) = {fib_optimized(i)}")
```

**Output:**

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

**Java:**

```java
public class FibonacciOptimized {

    public static long fib(int n) {
        if (n <= 1) return n;

        long prev2 = 0, prev1 = 1;

        for (int i = 2; i <= n; i++) {
            long current = prev1 + prev2;
            prev2 = prev1;
            prev1 = current;
        }

        return prev1;
    }

    public static void main(String[] args) {
        for (int i = 0; i < 10; i++) {
            System.out.println("fib(" + i + ") = " + fib(i));
        }
    }
}
```

**Output:**

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

**Time complexity: O(n).** Space complexity: O(1).

### Evolution Summary

```
Approach             Time      Space     Notes
---------------------------------------------------
Naive recursion      O(2^n)    O(n)      Terrible for n > 30
Memoization          O(n)      O(n)      Easy to write
Tabulation           O(n)      O(n)      No recursion stack
Space-optimized      O(n)      O(1)      Best for Fibonacci
```

---

## 20.5 The DP Recipe (5 Steps)

Use this systematic approach for every DP problem:

```
THE DP RECIPE
=============

Step 1: DEFINE THE STATE
  What does dp[i] (or dp[i][j]) represent?
  This is the most important step. Get this right and
  the rest follows naturally.

Step 2: FIND THE RECURRENCE RELATION
  How does dp[i] relate to smaller subproblems?
  dp[i] = some function of dp[i-1], dp[i-2], etc.

Step 3: IDENTIFY BASE CASES
  What are the smallest subproblems you can solve directly?
  These are the starting points for your table.

Step 4: DETERMINE THE ORDER OF COMPUTATION
  Fill the table so that when you need dp[i], all
  subproblems it depends on are already solved.

Step 5: EXTRACT THE ANSWER
  Where in the table is the final answer?
  Usually dp[n] or dp[n-1], but sometimes max(dp) or
  dp[n][m].
```

Let us apply this recipe to a new problem.

---

## 20.6 Climbing Stairs

**Problem:** You are climbing a staircase with n steps. Each time you can climb 1 or 2 steps. How many distinct ways can you reach the top?

```
Example: n = 4

Ways to climb 4 stairs:
  1+1+1+1
  1+1+2
  1+2+1
  2+1+1
  2+2

Answer: 5 ways

Visual:
         ___
      __|   |
   __|      |
__|         |
Step: 0  1  2  3  4
```

### Applying the DP Recipe

**Step 1: Define the state.**

`dp[i]` = number of distinct ways to reach step i.

**Step 2: Recurrence relation.**

To reach step i, you can come from step i-1 (one step) or step i-2 (two steps).

`dp[i] = dp[i-1] + dp[i-2]`

**Step 3: Base cases.**

- `dp[0] = 1` (one way to stay at the ground: do nothing)
- `dp[1] = 1` (one way to reach step 1: take one step)

**Step 4: Order of computation.**

Fill from left to right: dp[0], dp[1], dp[2], ..., dp[n].

**Step 5: Extract the answer.**

Return `dp[n]`.

### Walkthrough

```
n = 5

Step:    0    1    2    3    4    5
dp:     [1]  [1]  [ ]  [ ]  [ ]  [ ]

dp[2] = dp[1] + dp[0] = 1 + 1 = 2
dp[3] = dp[2] + dp[1] = 2 + 1 = 3
dp[4] = dp[3] + dp[2] = 3 + 2 = 5
dp[5] = dp[4] + dp[3] = 5 + 3 = 8

Step:    0    1    2    3    4    5
dp:     [1]  [1]  [2]  [3]  [5]  [8]

Answer: dp[5] = 8
```

Wait -- this is just Fibonacci! And that makes sense: the recurrence relation is identical.

### Implementation

**Python:**

```python
# Top-down (memoization)
def climb_stairs_memo(n, memo=None):
    if memo is None:
        memo = {}
    if n <= 1:
        return 1
    if n in memo:
        return memo[n]
    memo[n] = climb_stairs_memo(n - 1, memo) + \
              climb_stairs_memo(n - 2, memo)
    return memo[n]


# Bottom-up (tabulation)
def climb_stairs_table(n):
    if n <= 1:
        return 1

    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1

    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


# Space-optimized
def climb_stairs_optimized(n):
    if n <= 1:
        return 1

    prev2, prev1 = 1, 1

    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current

    return prev1


# Test all three approaches
for n in range(1, 8):
    a = climb_stairs_memo(n)
    b = climb_stairs_table(n)
    c = climb_stairs_optimized(n)
    assert a == b == c
    print(f"climb({n}) = {a}")
```

**Output:**

```
climb(1) = 1
climb(2) = 2
climb(3) = 3
climb(4) = 5
climb(5) = 8
climb(6) = 13
climb(7) = 21
```

**Java:**

```java
public class ClimbingStairs {

    // Bottom-up
    public static int climbStairs(int n) {
        if (n <= 1) return 1;

        int prev2 = 1, prev1 = 1;

        for (int i = 2; i <= n; i++) {
            int current = prev1 + prev2;
            prev2 = prev1;
            prev1 = current;
        }

        return prev1;
    }

    public static void main(String[] args) {
        for (int n = 1; n <= 7; n++) {
            System.out.println("climb(" + n + ") = " +
                climbStairs(n));
        }
    }
}
```

**Output:**

```
climb(1) = 1
climb(2) = 2
climb(3) = 3
climb(4) = 5
climb(5) = 8
climb(6) = 13
climb(7) = 21
```

### The Recursion Tree Shows Why DP Helps

```
Recursion tree for climbStairs(5) WITHOUT memoization:

                        cs(5)
                       /     \
                   cs(4)     cs(3)
                  /    \     /    \
              cs(3)  cs(2) cs(2) cs(1)
             /   \   / \   / \     |
          cs(2) cs(1) . .  . .     1
          / \    |
        cs(1) cs(0)
          |     |
          1     1

Total calls: 15 (many duplicates!)
With memoization: 5 calls (one per unique value of n)
```

### Time and Space Complexity

| Approach | Time | Space |
|----------|------|-------|
| Naive recursion | O(2^n) | O(n) stack |
| Memoization | O(n) | O(n) cache + stack |
| Tabulation | O(n) | O(n) table |
| Space-optimized | O(n) | O(1) |

---

## 20.7 Variant: Climbing Stairs with K Step Sizes

What if you can climb 1, 2, or 3 steps at a time? Or any set of step sizes?

**Python:**

```python
def climb_stairs_k(n, steps):
    """
    Count ways to climb n stairs using any step size in 'steps'.

    steps: list of allowed step sizes, e.g., [1, 2, 3]
    """
    dp = [0] * (n + 1)
    dp[0] = 1  # One way to stay at ground

    for i in range(1, n + 1):
        for step in steps:
            if i - step >= 0:
                dp[i] += dp[i - step]

    return dp[n]


# Test
print(f"Steps [1,2], n=5: {climb_stairs_k(5, [1, 2])}")
print(f"Steps [1,2,3], n=5: {climb_stairs_k(5, [1, 2, 3])}")
print(f"Steps [1,3,5], n=6: {climb_stairs_k(6, [1, 3, 5])}")
```

**Output:**

```
Steps [1,2], n=5: 8
Steps [1,2,3], n=5: 13
Steps [1,3,5], n=6: 8
```

**Java:**

```java
public class ClimbingStairsK {

    public static int climbStairs(int n, int[] steps) {
        int[] dp = new int[n + 1];
        dp[0] = 1;

        for (int i = 1; i <= n; i++) {
            for (int step : steps) {
                if (i - step >= 0) {
                    dp[i] += dp[i - step];
                }
            }
        }

        return dp[n];
    }

    public static void main(String[] args) {
        System.out.println("Steps [1,2], n=5: " +
            climbStairs(5, new int[]{1, 2}));
        System.out.println("Steps [1,2,3], n=5: " +
            climbStairs(5, new int[]{1, 2, 3}));
    }
}
```

**Output:**

```
Steps [1,2], n=5: 8
Steps [1,2,3], n=5: 13
```

---

## 20.8 Minimum Cost Climbing Stairs

**Problem:** Given an array `cost` where `cost[i]` is the cost of stepping on stair i, find the minimum cost to reach the top. You can start at step 0 or step 1, and at each step you can climb 1 or 2 stairs.

### Applying the DP Recipe

**Step 1:** `dp[i]` = minimum cost to reach step i.

**Step 2:** `dp[i] = cost[i] + min(dp[i-1], dp[i-2])`

**Step 3:** `dp[0] = cost[0]`, `dp[1] = cost[1]`

**Step 4:** Left to right.

**Step 5:** `min(dp[n-1], dp[n-2])` (you can reach the top from either of the last two steps).

**Python:**

```python
def min_cost_climbing_stairs(cost):
    n = len(cost)
    if n <= 1:
        return 0

    # Space-optimized approach
    prev2 = cost[0]
    prev1 = cost[1]

    for i in range(2, n):
        current = cost[i] + min(prev1, prev2)
        prev2 = prev1
        prev1 = current

    return min(prev1, prev2)


# Test
cost1 = [10, 15, 20]
print(f"Cost {cost1}: {min_cost_climbing_stairs(cost1)}")

cost2 = [1, 100, 1, 1, 1, 100, 1, 1, 100, 1]
print(f"Cost {cost2}: {min_cost_climbing_stairs(cost2)}")
```

**Output:**

```
Cost [10, 15, 20]: 15
Cost [1, 100, 1, 1, 1, 100, 1, 1, 100, 1]: 6
```

**Java:**

```java
public class MinCostClimbingStairs {

    public static int minCostClimbingStairs(int[] cost) {
        int n = cost.length;
        if (n <= 1) return 0;

        int prev2 = cost[0];
        int prev1 = cost[1];

        for (int i = 2; i < n; i++) {
            int current = cost[i] + Math.min(prev1, prev2);
            prev2 = prev1;
            prev1 = current;
        }

        return Math.min(prev1, prev2);
    }

    public static void main(String[] args) {
        int[] cost = {1, 100, 1, 1, 1, 100, 1, 1, 100, 1};
        System.out.println("Min cost: " +
            minCostClimbingStairs(cost));
        // Output: Min cost: 6
    }
}
```

**Output:**

```
Min cost: 6
```

---

## Common Mistakes

1. **Jumping straight to code without defining the state.** The state definition is the most critical step. Spend time getting `dp[i]` right before writing any code.

2. **Wrong base cases.** Off-by-one errors in base cases are the most common DP bug. Trace through small examples (n=0, n=1, n=2) to verify.

3. **Forgetting to handle edge cases.** Always check what happens when n=0 or n=1. Many DP problems have special handling for small inputs.

4. **Using memoization without a termination condition.** Every recursive path must eventually hit a base case. Missing base cases cause infinite recursion.

5. **Not recognizing when space can be optimized.** If `dp[i]` only depends on the previous one or two entries, you can reduce space from O(n) to O(1). Always look for this optimization.

6. **Confusing "number of ways" with "minimum/maximum."** For counting problems, you add subproblem results. For optimization problems, you take min or max.

---

## Best Practices

1. **Always start with brute force recursion.** Write the naive recursive solution first. This reveals the recurrence relation naturally.

2. **Draw the recursion tree.** This helps you see overlapping subproblems and understand the structure of the problem.

3. **Follow the DP Recipe.** The 5-step process works for every DP problem. Do not skip steps.

4. **Test with small inputs.** Verify your solution with n=0, 1, 2, 3 before running on larger inputs. Trace through the table filling manually.

5. **Start with tabulation in interviews.** Bottom-up solutions are easier to debug and optimize for space. Save memoization for problems where the computation order is unclear.

6. **Look for the Fibonacci pattern.** Many DP problems reduce to "combine the answers from the previous one or two subproblems." Recognizing this speeds up your solution.

---

## Quick Summary

```
Dynamic Programming = solving each subproblem once + storing results

Two required properties:
  1. Overlapping subproblems (same subproblems recur)
  2. Optimal substructure (optimal solution uses optimal sub-solutions)

Two approaches:
  Top-down (memoization):  recursion + cache
  Bottom-up (tabulation):  iterative + table

The DP Recipe:
  1. Define the state (what does dp[i] represent?)
  2. Find the recurrence relation
  3. Identify base cases
  4. Determine computation order
  5. Extract the answer

Evolution:  Brute force -> Memoization -> Tabulation -> Space-optimized
```

## Key Points

- Dynamic programming is about avoiding redundant computation by storing and reusing results of subproblems.
- A problem needs both overlapping subproblems AND optimal substructure for DP to apply.
- Top-down (memoization) adds caching to recursion. Bottom-up (tabulation) builds a table iteratively.
- The DP Recipe (5 steps) provides a systematic framework for solving any DP problem.
- Always start with the state definition. If you define `dp[i]` correctly, the recurrence relation usually follows naturally.
- Space optimization is often possible when `dp[i]` depends only on a fixed number of previous values.

---

## Practice Questions

1. Explain the difference between overlapping subproblems and optimal substructure. Give an example of a problem that has one but not the other.

2. Why does naive recursive Fibonacci have O(2^n) time complexity? Draw the recursion tree for fib(6) and count the total number of calls.

3. Convert the following recursive function to both memoized and tabulated versions:
   ```
   def f(n):
       if n <= 2: return n
       return f(n-1) + f(n-3)
   ```

4. A frog can jump 1, 3, or 5 steps at a time. Write a DP solution to count the number of ways to reach step n.

5. Explain when you would prefer memoization over tabulation, and vice versa.

---

## LeetCode-Style Problems

### Problem 1: Decode Ways (Medium)

A message containing letters A-Z can be encoded as numbers: 'A'->1, 'B'->2, ..., 'Z'->26. Given a string of digits, return the number of ways to decode it.

```python
def num_decodings(s):
    if not s or s[0] == '0':
        return 0

    n = len(s)
    # dp[i] = number of ways to decode s[0:i]
    dp = [0] * (n + 1)
    dp[0] = 1  # Empty string: one way
    dp[1] = 1  # First char (already checked it's not '0')

    for i in range(2, n + 1):
        # Single digit: s[i-1]
        if s[i - 1] != '0':
            dp[i] += dp[i - 1]

        # Two digits: s[i-2:i]
        two_digit = int(s[i - 2:i])
        if 10 <= two_digit <= 26:
            dp[i] += dp[i - 2]

    return dp[n]


# Test
print(f"'12': {num_decodings('12')}")    # AB or L -> 2
print(f"'226': {num_decodings('226')}")  # BZ, VF, BBF -> 3
print(f"'06': {num_decodings('06')}")    # Invalid -> 0
```

**Output:**

```
'12': 2
'226': 3
'06': 0
```

### Problem 2: House Robber (Medium)

You are a robber planning to rob houses along a street. Each house has a certain amount of money. You cannot rob two adjacent houses. Find the maximum amount you can rob.

```python
def rob(nums):
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]

    # dp[i] = max money robbing from houses 0..i
    # Either rob house i (and use dp[i-2]) or skip it (use dp[i-1])
    prev2 = 0
    prev1 = nums[0]

    for i in range(1, len(nums)):
        current = max(prev1, prev2 + nums[i])
        prev2 = prev1
        prev1 = current

    return prev1


# Test
print(f"[1,2,3,1]: {rob([1,2,3,1])}")
print(f"[2,7,9,3,1]: {rob([2,7,9,3,1])}")
```

**Output:**

```
[1,2,3,1]: 4
[2,7,9,3,1]: 12
```

### Problem 3: Tribonacci Number (Easy)

The Tribonacci sequence: T(0)=0, T(1)=1, T(2)=1, and T(n) = T(n-1) + T(n-2) + T(n-3) for n >= 3.

```python
def tribonacci(n):
    if n == 0:
        return 0
    if n <= 2:
        return 1

    a, b, c = 0, 1, 1

    for _ in range(3, n + 1):
        a, b, c = b, c, a + b + c

    return c


# Test
for i in range(10):
    print(f"T({i}) = {tribonacci(i)}")
```

**Output:**

```
T(0) = 0
T(1) = 1
T(2) = 1
T(3) = 2
T(4) = 4
T(5) = 7
T(6) = 13
T(7) = 24
T(8) = 44
T(9) = 81
```

### Problem 4: Maximum Subarray (Kadane's Algorithm) (Medium)

Find the contiguous subarray with the largest sum.

```python
def max_subarray(nums):
    """
    Kadane's algorithm as a DP problem.
    dp[i] = maximum subarray sum ending at index i.
    dp[i] = max(nums[i], dp[i-1] + nums[i])
    """
    max_ending_here = nums[0]
    max_so_far = nums[0]

    for i in range(1, len(nums)):
        # Either extend the previous subarray or start fresh
        max_ending_here = max(nums[i],
                              max_ending_here + nums[i])
        max_so_far = max(max_so_far, max_ending_here)

    return max_so_far


# Test
print(f"[-2,1,-3,4,-1,2,1,-5,4]: "
      f"{max_subarray([-2,1,-3,4,-1,2,1,-5,4])}")
print(f"[1]: {max_subarray([1])}")
print(f"[5,4,-1,7,8]: {max_subarray([5,4,-1,7,8])}")
```

**Output:**

```
[-2,1,-3,4,-1,2,1,-5,4]: 6
[1]: 1
[5,4,-1,7,8]: 23
```

---

## What Is Next?

You now understand the foundations of dynamic programming: the two key properties, top-down versus bottom-up, the DP Recipe, and classic problems like Fibonacci and Climbing Stairs. In Chapter 21, you will tackle **DP Patterns** -- the recurring shapes that DP problems take. You will learn 1D DP, 2D DP, and the famous Knapsack problem, giving you a pattern-recognition toolkit to solve nearly any DP problem you encounter.
