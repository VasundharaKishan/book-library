# Chapter 22: Greedy Algorithms

## What You Will Learn

- What greedy algorithms are and how they differ from dynamic programming
- The two properties that make greedy algorithms correct: greedy choice property and optimal substructure
- How to solve classic greedy problems: activity selection, fractional knapsack, and jump game
- An overview of Huffman encoding as a greedy application
- When greedy works and when you must fall back to DP
- How to solve interview problems using greedy strategies

## Why This Chapter Matters

Greedy algorithms are the simplest optimization strategy: at every step, pick the option that looks best right now. When this works, greedy algorithms are faster and simpler than dynamic programming. The challenge is knowing when "best right now" leads to "best overall."

In interviews, greedy problems are common because they test your ability to identify a correct strategy and prove (or at least argue convincingly) why it works. Many seemingly complex optimization problems have elegant greedy solutions that are just a few lines of code.

Real-world applications include network routing protocols, data compression (Huffman coding), task scheduling in operating systems, and making change with the fewest coins (for standard denominations).

---

## 22.1 What Is a Greedy Algorithm?

A greedy algorithm makes the **locally optimal choice** at each step, hoping this leads to a **globally optimal solution.**

```
The Greedy Strategy:
  1. At each step, pick the best available option
  2. Never look back, never reconsider
  3. Hope that local optimality leads to global optimality

Analogy: Climbing a hill in the fog
  - You cannot see the summit
  - At each step, you go in the steepest upward direction
  - Sometimes this works (single peak)
  - Sometimes you get stuck on a local maximum (multiple peaks)
```

### Greedy vs Dynamic Programming

```
                    Greedy              DP
Strategy:     Best choice NOW     Try ALL choices
Decisions:    One per step        All options considered
Backtrack:    Never               Implicitly (all subproblems)
Speed:        Usually O(n log n)  Usually O(n^2) or more
Correctness:  Only sometimes      Always (if applicable)

When to use greedy:
  The problem has GREEDY CHOICE PROPERTY:
  a locally optimal choice is part of some globally optimal solution.

When greedy FAILS, use DP.
```

### When Does Greedy Work?

A greedy algorithm produces the correct answer when the problem has both:

1. **Greedy Choice Property:** Making the locally best choice leads to a globally optimal solution. You do not need to reconsider past choices.

2. **Optimal Substructure:** An optimal solution to the problem contains optimal solutions to subproblems (same as DP).

```
Example where greedy WORKS:
  Making change with US coins [25, 10, 5, 1] for 41 cents:
  Greedy: 25 + 10 + 5 + 1 = 4 coins (optimal!)

Example where greedy FAILS:
  Making change with coins [1, 3, 4] for 6 cents:
  Greedy: 4 + 1 + 1 = 3 coins
  Optimal: 3 + 3 = 2 coins (DP finds this!)
```

---

## 22.2 Activity Selection / Meeting Rooms

**Problem:** Given a list of activities with start and end times, find the maximum number of non-overlapping activities you can attend.

This is the classic greedy problem. The key insight: **always pick the activity that finishes earliest.** This leaves the most room for future activities.

```
Activities (sorted by end time):
  A: |===|                     (1-3)
  B:   |===|                   (2-4)
  C:     |===|                 (3-5)
  D:       |=======|           (4-8)
  E:           |===|           (6-8)
  F:               |===|      (8-10)

Timeline:
  1  2  3  4  5  6  7  8  9  10
  |--A--|
     |--B--|
        |--C--|
           |----D----|
              |--E--|
                    |--F--|

Greedy choice (earliest end time first):
  Pick A (ends at 3) --> next must start >= 3
  Skip B (starts at 2, overlaps)
  Pick C (starts at 3, ends at 5) --> next must start >= 5
  Skip D (starts at 4, overlaps)
  Pick E (starts at 6, ends at 8) --> next must start >= 8
  Pick F (starts at 8, ends at 10)

Result: A, C, E, F = 4 activities (maximum!)
```

**Python:**

```python
def max_activities(activities):
    """
    Find maximum number of non-overlapping activities.
    activities: list of (start, end) tuples
    """
    # Sort by end time (greedy choice: earliest finish first)
    activities.sort(key=lambda x: x[1])

    count = 0
    last_end = 0  # End time of the last selected activity

    selected = []

    for start, end in activities:
        if start >= last_end:
            count += 1
            last_end = end
            selected.append((start, end))

    return count, selected


# Test
activities = [(1,3), (2,4), (3,5), (4,8), (6,8), (8,10)]
count, selected = max_activities(activities)
print(f"Max activities: {count}")
print(f"Selected: {selected}")
```

**Output:**

```
Max activities: 4
Selected: [(1, 3), (3, 5), (6, 8), (8, 10)]
```

**Java:**

```java
import java.util.*;

public class ActivitySelection {

    public static int maxActivities(int[][] activities) {
        // Sort by end time
        Arrays.sort(activities, (a, b) -> a[1] - b[1]);

        int count = 1;
        int lastEnd = activities[0][1];

        for (int i = 1; i < activities.length; i++) {
            if (activities[i][0] >= lastEnd) {
                count++;
                lastEnd = activities[i][1];
            }
        }

        return count;
    }

    public static void main(String[] args) {
        int[][] activities = {
            {1,3}, {2,4}, {3,5}, {4,8}, {6,8}, {8,10}
        };
        System.out.println("Max activities: " +
            maxActivities(activities));
        // Output: Max activities: 4
    }
}
```

**Time Complexity:** O(n log n) for sorting. **Space Complexity:** O(1) extra.

### Why Earliest Finish Time Works

```
Why not sort by start time?
  |----------A----------|
  |--B--|  |--C--|  |--D--|

  Sorted by start: pick A first (starts earliest).
  But A blocks B, C, D. Only 1 activity!
  Optimal: B, C, D = 3 activities.

Why not sort by shortest duration?
       |--A--|
  |-B-||-C-||-D-|

  Shortest first: pick B, C, D (3 activities).
  But consider:
  |----A----|
      |-B-|
  |--C--|  |--D--|

  Shortest first: pick B, then nothing fits. 1 activity.
  Optimal: C, D = 2 activities.

Earliest finish time avoids both traps!
```

---

## 22.3 Fractional Knapsack

**Problem:** Given items with weights and values and a knapsack capacity, maximize the total value. Unlike 0/1 knapsack, you CAN take fractions of items.

**Greedy strategy:** Sort by value-to-weight ratio (value per unit weight), and take items greedily.

```
Items:
  Item   Weight   Value   Ratio (value/weight)
  A      10       60      6.0
  B      20       100     5.0
  C      30       120     4.0

Capacity: 50

Greedy (by ratio):
  Take ALL of A: weight=10, value=60.  Remaining capacity: 40
  Take ALL of B: weight=20, value=100. Remaining capacity: 20
  Take 20/30 of C: weight=20, value=120*(20/30)=80.

Total value: 60 + 100 + 80 = 240
```

**Python:**

```python
def fractional_knapsack(items, capacity):
    """
    items: list of (weight, value)
    capacity: maximum weight
    Returns: maximum value
    """
    # Sort by value-to-weight ratio (descending)
    items.sort(key=lambda x: x[1] / x[0], reverse=True)

    total_value = 0
    remaining = capacity

    for weight, value in items:
        if remaining <= 0:
            break

        if weight <= remaining:
            # Take the whole item
            total_value += value
            remaining -= weight
        else:
            # Take a fraction
            fraction = remaining / weight
            total_value += value * fraction
            remaining = 0

    return total_value


# Test
items = [(10, 60), (20, 100), (30, 120)]
capacity = 50
print(f"Max value: {fractional_knapsack(items, capacity)}")
```

**Output:**

```
Max value: 240.0
```

**Java:**

```java
import java.util.*;

public class FractionalKnapsack {

    public static double fractionalKnapsack(
            int[][] items, int capacity) {
        // Sort by value/weight ratio descending
        Arrays.sort(items, (a, b) ->
            Double.compare((double)b[1]/b[0],
                          (double)a[1]/a[0]));

        double totalValue = 0;
        int remaining = capacity;

        for (int[] item : items) {
            if (remaining <= 0) break;

            if (item[0] <= remaining) {
                totalValue += item[1];
                remaining -= item[0];
            } else {
                totalValue += (double) item[1] * remaining
                              / item[0];
                remaining = 0;
            }
        }

        return totalValue;
    }

    public static void main(String[] args) {
        int[][] items = {{10,60}, {20,100}, {30,120}};
        System.out.printf("Max value: %.1f%n",
            fractionalKnapsack(items, 50));
        // Output: Max value: 240.0
    }
}
```

**Time Complexity:** O(n log n). **Space Complexity:** O(1).

### Why Greedy Works for Fractional but Not 0/1 Knapsack

```
Fractional: We can take ANY fraction of an item.
  The best ratio item is ALWAYS worth taking.
  If it does not fit entirely, take what fits.
  Greedy choice property holds.

0/1: We must take the WHOLE item or nothing.
  The best ratio item might not leave room for
  a better combination of other items.
  Greedy choice property FAILS.

Example:
  Items: A(weight=6, value=6), B(weight=5, value=5), C(weight=5, value=5)
  Capacity: 10

  Greedy (by ratio, all ratios=1): takes A+B = value 11, weight 11 > 10!
  Actually: takes A (ratio 1), then B does not fit with A.
  Takes A + C? same issue. Best: B+C = value 10.

  Fractional: take all of A (value 6), 4/5 of B (value 4) = 10.
```

---

## 22.4 Jump Game

**Problem:** Given an array where `nums[i]` represents the maximum jump length from position i, determine if you can reach the last index starting from index 0.

**Greedy strategy:** Track the farthest position you can reach. If at any point your current position exceeds the farthest reachable, you are stuck.

```
nums = [2, 3, 1, 1, 4]

Position: 0  1  2  3  4
Value:    2  3  1  1  4

Step 0: at position 0, can jump up to 2. Farthest = max(0, 0+2) = 2
Step 1: at position 1, can jump up to 3. Farthest = max(2, 1+3) = 4
We can reach index 4! Return true.

nums = [3, 2, 1, 0, 4]

Position: 0  1  2  3  4
Value:    3  2  1  0  4

Step 0: farthest = max(0, 0+3) = 3
Step 1: farthest = max(3, 1+2) = 3
Step 2: farthest = max(3, 2+1) = 3
Step 3: farthest = max(3, 3+0) = 3
Cannot reach index 4! Return false.
```

**Python:**

```python
def can_jump(nums):
    farthest = 0

    for i in range(len(nums)):
        # If current position is beyond farthest reachable
        if i > farthest:
            return False

        farthest = max(farthest, i + nums[i])

        # Early exit: can already reach the end
        if farthest >= len(nums) - 1:
            return True

    return True


# Test
print(f"[2,3,1,1,4]: {can_jump([2,3,1,1,4])}")
print(f"[3,2,1,0,4]: {can_jump([3,2,1,0,4])}")
```

**Output:**

```
[2,3,1,1,4]: True
[3,2,1,0,4]: False
```

**Java:**

```java
public class JumpGame {

    public static boolean canJump(int[] nums) {
        int farthest = 0;

        for (int i = 0; i < nums.length; i++) {
            if (i > farthest) return false;
            farthest = Math.max(farthest, i + nums[i]);
            if (farthest >= nums.length - 1) return true;
        }

        return true;
    }

    public static void main(String[] args) {
        System.out.println(canJump(new int[]{2,3,1,1,4}));
        // Output: true
        System.out.println(canJump(new int[]{3,2,1,0,4}));
        // Output: false
    }
}
```

**Time Complexity:** O(n). **Space Complexity:** O(1).

---

## 22.5 Huffman Encoding Overview

Huffman encoding is a greedy algorithm for lossless data compression. It assigns shorter binary codes to more frequent characters and longer codes to less frequent ones.

```
Example: Encoding "aaaaabbbccde"

Character frequencies:
  a: 5, b: 3, c: 2, d: 1, e: 1

Step 1: Put all characters in a min-heap (priority queue) by frequency.
  [d:1, e:1, c:2, b:3, a:5]

Step 2: Repeatedly extract the two smallest, merge them:

  Extract d(1) and e(1), merge into de(2):
  [c:2, de:2, b:3, a:5]

  Extract c(2) and de(2), merge into cde(4):
  [b:3, cde:4, a:5]

  Extract b(3) and cde(4), merge into bcde(7):
  [a:5, bcde:7]

  Extract a(5) and bcde(7), merge into root(12):
  [root:12]

Huffman Tree:
         (12)
        /    \
      a(5)  (7)
           /    \
         b(3)  (4)
              /    \
            c(2)  (2)
                 /    \
               d(1)  e(1)

Codes (left=0, right=1):
  a: 0        (1 bit)
  b: 10       (2 bits)
  c: 110      (3 bits)
  d: 1110     (4 bits)
  e: 1111     (4 bits)

Fixed-length encoding: 12 chars * 3 bits = 36 bits
Huffman encoding: 5*1 + 3*2 + 2*3 + 1*4 + 1*4 = 5+6+6+4+4 = 25 bits
Savings: 30%!
```

**Python:**

```python
import heapq
from collections import Counter

def huffman_encoding(text):
    """Build Huffman tree and return character codes."""
    # Count frequencies
    freq = Counter(text)

    # Create min-heap of (frequency, id, character)
    # id is used to break ties (characters are not comparable)
    heap = [(f, i, char) for i, (char, f)
            in enumerate(freq.items())]
    heapq.heapify(heap)

    if len(heap) == 1:
        return {heap[0][2]: '0'}

    # Build tree
    counter = len(heap)
    while len(heap) > 1:
        freq1, _, left = heapq.heappop(heap)
        freq2, _, right = heapq.heappop(heap)
        merged = (left, right)
        heapq.heappush(heap, (freq1 + freq2, counter, merged))
        counter += 1

    # Generate codes
    codes = {}

    def build_codes(node, code=""):
        if isinstance(node, str):
            codes[node] = code
            return
        build_codes(node[0], code + "0")
        build_codes(node[1], code + "1")

    _, _, root = heap[0]
    build_codes(root)

    return codes


# Test
text = "aaaaabbbccde"
codes = huffman_encoding(text)

print("Huffman codes:")
for char in sorted(codes):
    print(f"  '{char}': {codes[char]}")

# Calculate compression
original_bits = len(text) * 8  # ASCII
huffman_bits = sum(len(codes[c]) for c in text)
print(f"\nOriginal: {original_bits} bits")
print(f"Huffman: {huffman_bits} bits")
print(f"Compression ratio: {huffman_bits/original_bits:.1%}")
```

**Output:**

```
Huffman codes:
  'a': 0
  'b': 10
  'c': 110
  'd': 1110
  'e': 1111

Original: 96 bits
Huffman: 25 bits
Compression ratio: 26.0%
```

**Time Complexity:** O(n log n) where n is the number of unique characters. **Space Complexity:** O(n).

---

## 22.6 Greedy vs DP: A Comparison

```
Problem                    Greedy Works?    Why?
------------------------------------------------------------
Activity Selection         YES              Earliest end time is always safe
Fractional Knapsack        YES              Best ratio item always helps
0/1 Knapsack               NO               Need to try combinations
Coin Change (US coins)     YES              Denominations divide nicely
Coin Change (arbitrary)    NO               Greedy may miss better combos
Jump Game (can reach?)     YES              Farthest reach is monotonic
Jump Game II (min jumps)   YES              Farthest reach per level
Shortest Path (no neg)     YES (Dijkstra)   Closest vertex is always final
Shortest Path (neg wt)     NO               Need Bellman-Ford (relaxation)
Huffman Encoding           YES              Smallest frequencies first
Job Scheduling             YES              Sorted by deadline/profit
```

### How to Tell If Greedy Works

1. **Can you prove the greedy choice is safe?** If choosing the locally best option never eliminates the globally optimal solution, greedy works.

2. **Does the problem have exchange argument?** If you can show that swapping a non-greedy choice for the greedy choice never makes things worse, greedy is correct.

3. **When in doubt, try a counterexample.** Think of a small input where greedy gives the wrong answer. If you find one, use DP instead.

---

## 22.7 Problem: Assign Cookies

**Problem:** You have children with greed factors and cookies with sizes. Each child i is content if they get a cookie with size >= their greed factor. Maximize the number of content children.

**Greedy:** Sort both arrays. Try to satisfy the least greedy child with the smallest sufficient cookie.

**Python:**

```python
def find_content_children(children, cookies):
    children.sort()
    cookies.sort()

    child_i = 0
    cookie_i = 0

    while child_i < len(children) and cookie_i < len(cookies):
        if cookies[cookie_i] >= children[child_i]:
            # This cookie satisfies this child
            child_i += 1
        # Move to next cookie either way
        cookie_i += 1

    return child_i


# Test
print(f"Children [1,2,3], Cookies [1,1]: "
      f"{find_content_children([1,2,3], [1,1])}")
print(f"Children [1,2], Cookies [1,2,3]: "
      f"{find_content_children([1,2], [1,2,3])}")
```

**Output:**

```
Children [1,2,3], Cookies [1,1]: 1
Children [1,2], Cookies [1,2,3]: 2
```

**Java:**

```java
import java.util.Arrays;

public class AssignCookies {

    public static int findContentChildren(
            int[] children, int[] cookies) {
        Arrays.sort(children);
        Arrays.sort(cookies);

        int child = 0, cookie = 0;

        while (child < children.length &&
               cookie < cookies.length) {
            if (cookies[cookie] >= children[child]) {
                child++;
            }
            cookie++;
        }

        return child;
    }

    public static void main(String[] args) {
        System.out.println(findContentChildren(
            new int[]{1,2,3}, new int[]{1,1}));
        // Output: 1
    }
}
```

**Time Complexity:** O(n log n + m log m) for sorting. **Space Complexity:** O(1).

---

## 22.8 Problem: Best Time to Buy and Sell Stock II

**Problem:** You can buy and sell a stock multiple times (but must sell before buying again). Find the maximum profit.

**Greedy:** Collect every upward price movement. If tomorrow's price is higher than today's, "buy" today and "sell" tomorrow.

```
prices = [7, 1, 5, 3, 6, 4]

Day:    0   1   2   3   4   5
Price:  7   1   5   3   6   4
                 ^       ^
                 sell    sell
             ^       ^
             buy    buy

Profit: (5-1) + (6-3) = 4 + 3 = 7
```

**Python:**

```python
def max_profit(prices):
    profit = 0

    for i in range(1, len(prices)):
        # Collect every positive difference
        if prices[i] > prices[i - 1]:
            profit += prices[i] - prices[i - 1]

    return profit


# Test
print(f"[7,1,5,3,6,4]: {max_profit([7,1,5,3,6,4])}")
print(f"[1,2,3,4,5]: {max_profit([1,2,3,4,5])}")
print(f"[7,6,4,3,1]: {max_profit([7,6,4,3,1])}")
```

**Output:**

```
[7,1,5,3,6,4]: 7
[1,2,3,4,5]: 4
[7,6,4,3,1]: 0
```

**Java:**

```java
public class BestTimeToBuySell {

    public static int maxProfit(int[] prices) {
        int profit = 0;

        for (int i = 1; i < prices.length; i++) {
            if (prices[i] > prices[i - 1]) {
                profit += prices[i] - prices[i - 1];
            }
        }

        return profit;
    }

    public static void main(String[] args) {
        System.out.println(maxProfit(
            new int[]{7, 1, 5, 3, 6, 4}));
        // Output: 7
    }
}
```

**Time Complexity:** O(n). **Space Complexity:** O(1).

---

## 22.9 Problem: Gas Station

**Problem:** There are n gas stations along a circular route. `gas[i]` is the fuel at station i, `cost[i]` is the fuel to travel from station i to i+1. Find the starting station index to complete the circuit, or -1 if impossible.

**Greedy insight:** If total gas >= total cost, a solution exists. Start from the station after the point where the running tank becomes most negative.

**Python:**

```python
def can_complete_circuit(gas, cost):
    # If total gas < total cost, impossible
    if sum(gas) < sum(cost):
        return -1

    tank = 0
    start = 0

    for i in range(len(gas)):
        tank += gas[i] - cost[i]

        # If tank goes negative, we cannot start from
        # 'start' or any station between start and i
        if tank < 0:
            start = i + 1
            tank = 0

    return start


# Test
gas = [1, 2, 3, 4, 5]
cost = [3, 4, 5, 1, 2]
print(f"Start station: {can_complete_circuit(gas, cost)}")

gas2 = [2, 3, 4]
cost2 = [3, 4, 3]
print(f"Start station: {can_complete_circuit(gas2, cost2)}")
```

**Output:**

```
Start station: 3
Start station: -1
```

**Java:**

```java
public class GasStation {

    public static int canCompleteCircuit(
            int[] gas, int[] cost) {
        int totalTank = 0, currentTank = 0, start = 0;

        for (int i = 0; i < gas.length; i++) {
            int diff = gas[i] - cost[i];
            totalTank += diff;
            currentTank += diff;

            if (currentTank < 0) {
                start = i + 1;
                currentTank = 0;
            }
        }

        return totalTank >= 0 ? start : -1;
    }

    public static void main(String[] args) {
        System.out.println(canCompleteCircuit(
            new int[]{1,2,3,4,5}, new int[]{3,4,5,1,2}));
        // Output: 3
    }
}
```

**Time Complexity:** O(n). **Space Complexity:** O(1).

---

## 22.10 Problem: Task Scheduler

**Problem:** Given tasks represented by characters and a cooldown period n, find the minimum number of intervals needed to complete all tasks. The same task must have at least n intervals between executions.

**Greedy:** The most frequent task determines the structure. Fill the gaps with other tasks.

```
tasks = ['A','A','A','B','B','B'], n = 2

Most frequent task: A (count = 3)

Frame:  A _ _ | A _ _ | A
        ^       ^       ^
        slots between A's must be n=2

Fill with B:
        A B _ | A B _ | A

Remaining slots: 2 idle slots
Total: 8

Formula: (maxCount - 1) * (n + 1) + numMaxFreq
         (3 - 1) * (2 + 1) + 2 = 2 * 3 + 2 = 8
         (2 tasks have max frequency: A and B)
```

**Python:**

```python
from collections import Counter

def least_interval(tasks, n):
    freq = Counter(tasks)
    max_count = max(freq.values())

    # How many tasks have the maximum frequency?
    num_max_freq = sum(1 for v in freq.values()
                       if v == max_count)

    # Formula: frames of size (n+1), with maxCount-1 full frames
    # plus the last partial frame with numMaxFreq tasks
    result = (max_count - 1) * (n + 1) + num_max_freq

    # If there are more tasks than the formula suggests,
    # no idle time is needed
    return max(result, len(tasks))


# Test
tasks = ['A','A','A','B','B','B']
print(f"Tasks {tasks}, n=2: {least_interval(tasks, 2)}")

tasks2 = ['A','A','A','B','B','B']
print(f"Tasks {tasks2}, n=0: {least_interval(tasks2, 0)}")

tasks3 = ['A','A','A','A','A','A','B','C','D','E','F','G']
print(f"Tasks {tasks3}, n=2: {least_interval(tasks3, 2)}")
```

**Output:**

```
Tasks ['A', 'A', 'A', 'B', 'B', 'B'], n=2: 8
Tasks ['A', 'A', 'A', 'B', 'B', 'B'], n=0: 6
Tasks ['A', 'A', 'A', 'A', 'A', 'A', 'B', 'C', 'D', 'E', 'F', 'G'], n=2: 16
```

**Java:**

```java
public class TaskScheduler {

    public static int leastInterval(char[] tasks, int n) {
        int[] freq = new int[26];
        for (char t : tasks) freq[t - 'A']++;

        int maxCount = 0;
        for (int f : freq) maxCount = Math.max(maxCount, f);

        int numMaxFreq = 0;
        for (int f : freq) {
            if (f == maxCount) numMaxFreq++;
        }

        int result = (maxCount - 1) * (n + 1) + numMaxFreq;

        return Math.max(result, tasks.length);
    }

    public static void main(String[] args) {
        char[] tasks = {'A','A','A','B','B','B'};
        System.out.println("Intervals: " +
            leastInterval(tasks, 2));
        // Output: Intervals: 8
    }
}
```

**Time Complexity:** O(n) where n is the number of tasks. **Space Complexity:** O(1) (26 letters).

---

## Common Mistakes

1. **Assuming greedy always works.** The biggest mistake is applying greedy without verifying the greedy choice property. Always try to find a counterexample before committing to greedy.

2. **Wrong sorting criterion.** In activity selection, sorting by start time or duration gives wrong results. The correct criterion is end time. Always think carefully about WHAT to sort by.

3. **Not handling ties correctly.** When two options have the same greedy score, the tie-breaking strategy matters. Test with inputs that have ties.

4. **Forgetting that greedy needs a proof.** In interviews, you may be asked WHY your greedy approach works. Practice the exchange argument: show that swapping any non-greedy choice for the greedy choice does not make the solution worse.

5. **Using greedy for 0/1 Knapsack.** The fractional knapsack is greedy; the 0/1 knapsack is NOT. This is a classic trap.

---

## Best Practices

1. **Try greedy first, verify with small examples.** If the greedy solution passes small test cases, think about whether it could fail on larger inputs.

2. **Sort the input.** Most greedy algorithms start with sorting. The key question is: sort by WHAT?

3. **Use the exchange argument.** To convince yourself (or an interviewer) that greedy is correct, show that any deviation from the greedy choice cannot improve the solution.

4. **Fall back to DP if greedy fails.** If you find a counterexample, switch to DP. Many problems that look greedy actually need DP.

5. **Know the classic greedy problems.** Activity selection, Huffman coding, fractional knapsack, and interval scheduling are the foundations. Most greedy interview problems are variations of these.

---

## Quick Summary

```
Greedy = always pick the locally best option

Works when:
  1. Greedy choice property (local optimum is globally safe)
  2. Optimal substructure

Classic problems:
  Activity Selection:     sort by end time, pick non-overlapping
  Fractional Knapsack:    sort by value/weight ratio
  Jump Game:              track farthest reachable position
  Task Scheduler:         fill around the most frequent task

Greedy vs DP:
  Greedy: faster, simpler, but only works sometimes
  DP: slower, but always correct when applicable
```

## Key Points

- Greedy algorithms make the locally optimal choice at each step, never reconsidering past decisions.
- A problem is solvable by greedy if it has both the greedy choice property and optimal substructure.
- Most greedy algorithms start by sorting the input. The sorting criterion is the most important design decision.
- Greedy works for fractional knapsack but NOT for 0/1 knapsack. This distinction is a classic interview question.
- When in doubt, try to find a counterexample. If greedy fails on any input, use DP instead.
- The exchange argument is the standard technique for proving a greedy algorithm is correct.

---

## Practice Questions

1. Explain the greedy choice property. Give an example where it holds and one where it does not.

2. Why does sorting by end time work for activity selection, but sorting by start time or duration does not? Give counterexamples.

3. Prove that the greedy algorithm for fractional knapsack is optimal using the exchange argument.

4. Can Jump Game II (minimum number of jumps to reach the end) be solved greedily? If so, describe the strategy.

5. You have n meeting rooms and a list of meetings with start/end times. Find the minimum number of rooms needed. What is the greedy approach?

---

## LeetCode-Style Problems

### Problem 1: Non-overlapping Intervals (Medium)

Given intervals, find the minimum number of intervals to remove so the rest are non-overlapping.

```python
def erase_overlap_intervals(intervals):
    if not intervals:
        return 0

    # Sort by end time (same as activity selection!)
    intervals.sort(key=lambda x: x[1])

    count = 0  # Number to remove
    last_end = intervals[0][1]

    for i in range(1, len(intervals)):
        if intervals[i][0] < last_end:
            # Overlap: remove this interval
            count += 1
        else:
            last_end = intervals[i][1]

    return count


# Test
print(erase_overlap_intervals([[1,2],[2,3],[3,4],[1,3]]))
# Output: 1  (remove [1,3])
print(erase_overlap_intervals([[1,2],[1,2],[1,2]]))
# Output: 2
```

### Problem 2: Queue Reconstruction by Height (Medium)

People are described by (height, number_of_taller_or_equal_people_in_front). Reconstruct the queue.

```python
def reconstruct_queue(people):
    # Sort: tallest first, then by k ascending
    people.sort(key=lambda x: (-x[0], x[1]))

    queue = []
    for person in people:
        # Insert at index = their k value
        queue.insert(person[1], person)

    return queue


# Test
people = [[7,0],[4,4],[7,1],[5,0],[6,1],[5,2]]
result = reconstruct_queue(people)
print(f"Queue: {result}")
# Output: Queue: [[5,0],[7,0],[5,2],[6,1],[4,4],[7,1]]
```

### Problem 3: Minimum Number of Arrows to Burst Balloons (Medium)

Balloons are represented as intervals. Find the minimum number of arrows (vertical lines) to burst all balloons.

```python
def find_min_arrow_shots(points):
    if not points:
        return 0

    # Sort by end point
    points.sort(key=lambda x: x[1])

    arrows = 1
    arrow_pos = points[0][1]

    for start, end in points[1:]:
        if start > arrow_pos:
            # Need a new arrow
            arrows += 1
            arrow_pos = end

    return arrows


# Test
print(find_min_arrow_shots([[10,16],[2,8],[1,6],[7,12]]))
# Output: 2
print(find_min_arrow_shots([[1,2],[3,4],[5,6],[7,8]]))
# Output: 4
```

---

## What Is Next?

Greedy algorithms make a single choice at each step and never look back. But what happens when you need to explore multiple possibilities? In Chapter 23, you will learn about **Backtracking** -- an algorithmic strategy that systematically tries all possible paths, undoes bad choices, and continues searching. It is the tool you need for problems like N-Queens, Sudoku solving, and generating all permutations.
