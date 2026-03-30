# Chapter 9: Recursion

## What You Will Learn

- What recursion is and how it works (the Russian doll analogy)
- The two essential parts: base case and recursive case
- How the call stack manages recursive function calls
- How to trace through factorial and Fibonacci step by step
- Recursion vs iteration: when to choose each
- A preview of memoization to fix slow recursion
- What causes stack overflow errors and how to prevent them
- How to draw recursion trees using ASCII art
- How to solve five classic recursive interview problems

## Why This Chapter Matters

Recursion is one of the most elegant and powerful ideas in computer science. It is also one of the most confusing for beginners. Many students learn the definition -- "a function that calls itself" -- but never develop the intuition for when and how to use it.

Here is the truth: recursion is not magic. It is a technique where you solve a big problem by breaking it into smaller versions of the same problem, over and over, until you reach a problem so small that the answer is obvious. If you can think this way, you unlock entire families of algorithms -- tree traversals, divide and conquer, backtracking, dynamic programming -- that are nearly impossible to understand without recursion.

---

## 9.1 What Is Recursion?

**Recursion** is when a function calls itself to solve a smaller version of the same problem.

### The Russian Doll Analogy

Imagine a set of Russian nesting dolls (matryoshka). You open the outermost doll and find a smaller doll inside. You open that one and find an even smaller doll. You keep opening until you reach the tiniest doll that cannot be opened -- that is the **base case**.

```
Open doll of size 5:
  Inside is a doll of size 4:
    Inside is a doll of size 3:
      Inside is a doll of size 2:
        Inside is a doll of size 1:
          This is the smallest doll. Stop! (BASE CASE)
        Close doll of size 2
      Close doll of size 3
    Close doll of size 4
  Close doll of size 5
```

### The Two Essential Parts

Every recursive function must have:

1. **Base case**: The condition where the function stops calling itself and returns a direct answer. Without this, recursion runs forever (or until your program crashes).

2. **Recursive case**: The part where the function calls itself with a smaller or simpler input, making progress toward the base case.

```python
def countdown(n):
    if n <= 0:          # Base case
        print("Go!")
        return
    print(n)
    countdown(n - 1)    # Recursive case: smaller problem

countdown(3)
# Output:
# 3
# 2
# 1
# Go!
```

---

## 9.2 The Call Stack: How Recursion Actually Works

When a function calls itself, each call is placed on the **call stack** -- a stack of function frames, each waiting for the next one to return.

### Factorial: Step-by-Step

The factorial of n (written n!) is defined as: `n! = n * (n-1) * (n-2) * ... * 1`, with `0! = 1`.

```python
def factorial(n):
    if n <= 1:           # Base case
        return 1
    return n * factorial(n - 1)  # Recursive case

print(factorial(5))  # Output: 120
```

### Call Stack Visualization

```
factorial(5)  is called

CALL PHASE (building up the stack):

  +-------------------+
  | factorial(1)      |  <- Base case: return 1
  +-------------------+
  | factorial(2)      |  <- waiting for factorial(1), will compute 2 * ?
  +-------------------+
  | factorial(3)      |  <- waiting for factorial(2), will compute 3 * ?
  +-------------------+
  | factorial(4)      |  <- waiting for factorial(3), will compute 4 * ?
  +-------------------+
  | factorial(5)      |  <- waiting for factorial(4), will compute 5 * ?
  +-------------------+

RETURN PHASE (unwinding the stack):

  factorial(1) returns 1
  factorial(2) returns 2 * 1 = 2
  factorial(3) returns 3 * 2 = 6
  factorial(4) returns 4 * 6 = 24
  factorial(5) returns 5 * 24 = 120

Final answer: 120
```

### Java -- Factorial

```java
public class Factorial {
    public static int factorial(int n) {
        if (n <= 1) {
            return 1;  // Base case
        }
        return n * factorial(n - 1);  // Recursive case
    }

    public static void main(String[] args) {
        System.out.println(factorial(5));  // Output: 120
    }
}
```

---

## 9.3 Fibonacci: The Classic Example

The Fibonacci sequence is: 0, 1, 1, 2, 3, 5, 8, 13, 21, ...

Each number is the sum of the two before it: `fib(n) = fib(n-1) + fib(n-2)`.

### Naive Recursive Fibonacci

```python
def fib(n):
    if n <= 0:
        return 0      # Base case 1
    if n == 1:
        return 1      # Base case 2
    return fib(n - 1) + fib(n - 2)  # Recursive case

print(fib(6))  # Output: 8
# Sequence: 0, 1, 1, 2, 3, 5, 8
```

### Recursion Tree for fib(5)

```
                          fib(5)
                        /        \
                   fib(4)         fib(3)
                  /      \        /     \
             fib(3)    fib(2)  fib(2)  fib(1)
            /     \    /    \   /    \     |
        fib(2) fib(1) fib(1) fib(0) fib(1) fib(0)  1
        /    \    |     |      |      |      |
    fib(1) fib(0) 1     1      0      1      0
       |      |
       1      0
```

Notice the massive duplication! `fib(3)` is computed twice, `fib(2)` is computed three times. This is why naive recursive Fibonacci is **O(2^n)** -- exponentially slow.

### Java -- Fibonacci

```java
public class Fibonacci {
    public static int fib(int n) {
        if (n <= 0) return 0;
        if (n == 1) return 1;
        return fib(n - 1) + fib(n - 2);
    }

    public static void main(String[] args) {
        System.out.println(fib(6));  // Output: 8
    }
}
```

---

## 9.4 Recursion vs Iteration

Any recursive algorithm can be rewritten as an iterative one (using loops), and vice versa. The choice depends on clarity, performance, and the problem structure.

### Factorial -- Iterative Version

```python
def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_iterative(5))  # Output: 120
```

### Fibonacci -- Iterative Version

```python
def fib_iterative(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1

    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current

    return prev1

print(fib_iterative(6))  # Output: 8
```

### Comparison Table

| Aspect          | Recursion                     | Iteration                    |
|-----------------|-------------------------------|------------------------------|
| Readability     | Often cleaner for trees/graphs| Better for simple loops      |
| Memory          | Uses call stack (O(depth))    | Constant extra space         |
| Speed           | Function call overhead        | Usually faster               |
| Stack overflow  | Risk with deep recursion      | Not a concern                |
| When to use     | Trees, divide & conquer       | Simple counting, traversal   |

**Rule of thumb**: Use recursion when the problem has a naturally recursive structure (trees, nested data, divide and conquer). Use iteration when a simple loop suffices.

---

## 9.5 Memoization Preview

**Memoization** is caching the results of expensive function calls so that the same inputs are never computed twice. It transforms the exponential Fibonacci into O(n).

```python
def fib_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 0:
        return 0
    if n == 1:
        return 1

    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]

print(fib_memo(50))  # Output: 12586269025 (instant!)
# Without memoization, fib(50) would take hours
```

### With Memoization: The Tree Is Pruned

```
                    fib(5)
                   /      \
              fib(4)      fib(3)  <-- already in memo, return immediately
             /      \
        fib(3)     fib(2)  <-- already in memo
       /      \
  fib(2)    fib(1) = 1
  /     \
fib(1)  fib(0)
  1       0
```

Each value is computed only once: O(n) time, O(n) space.

### Java -- Memoized Fibonacci

```java
import java.util.HashMap;
import java.util.Map;

public class FibMemo {
    private static Map<Integer, Long> memo = new HashMap<>();

    public static long fib(int n) {
        if (memo.containsKey(n)) return memo.get(n);
        if (n <= 0) return 0;
        if (n == 1) return 1;

        long result = fib(n - 1) + fib(n - 2);
        memo.put(n, result);
        return result;
    }

    public static void main(String[] args) {
        System.out.println(fib(50));  // Output: 12586269025
    }
}
```

We will cover memoization and dynamic programming in full in Chapters 20-21.

---

## 9.6 Stack Overflow: When Recursion Goes Wrong

Every recursive call adds a frame to the call stack. The stack has a limited size (typically a few thousand to tens of thousands of frames). If recursion is too deep, you get a **stack overflow**.

### Python Example

```python
import sys
print(sys.getrecursionlimit())  # Default: 1000

def infinite_recursion(n):
    return infinite_recursion(n + 1)

# infinite_recursion(0)  # RecursionError: maximum recursion depth exceeded
```

### Java Example

```java
public class StackOverflowDemo {
    public static void infinite(int n) {
        infinite(n + 1);  // Never stops
    }

    public static void main(String[] args) {
        // infinite(0);  // StackOverflowError
    }
}
```

### How to Prevent Stack Overflow

1. **Always have a base case**: This is the most common cause of stack overflow -- forgetting the stopping condition.

2. **Ensure progress toward the base case**: Each recursive call must bring you closer to the base case. If `n` does not decrease, you never reach `n == 0`.

3. **Use iteration for deep recursion**: If you need recursion depth > 1000, convert to an iterative approach using an explicit stack.

4. **Increase the limit (Python only, use cautiously)**:
   ```python
   import sys
   sys.setrecursionlimit(10000)  # Only if you know the depth is manageable
   ```

---

## 9.7 Drawing Recursion Trees

Recursion trees are the best tool for understanding how recursive functions execute. Here is how to draw one:

### Step-by-Step Process

1. Draw the initial call at the top
2. For each recursive call, draw a child node below
3. Write the return value at each node
4. Trace the execution order (left children first for most algorithms)

### Example: sum_array([3, 1, 4, 1, 5])

```python
def sum_array(arr, i=0):
    if i == len(arr):   # Base case
        return 0
    return arr[i] + sum_array(arr, i + 1)

print(sum_array([3, 1, 4, 1, 5]))  # Output: 14
```

```
Recursion tree:

sum([3,1,4,1,5], i=0)  -->  3 + 11 = 14
        |
sum([3,1,4,1,5], i=1)  -->  1 + 10 = 11
        |
sum([3,1,4,1,5], i=2)  -->  4 + 6 = 10
        |
sum([3,1,4,1,5], i=3)  -->  1 + 5 = 6
        |
sum([3,1,4,1,5], i=4)  -->  5 + 0 = 5
        |
sum([3,1,4,1,5], i=5)  -->  0 (base case)
```

This is a **linear** recursion tree (one branch). Fibonacci has a **binary** tree (two branches per call). Permutation problems have **n-ary** trees (n branches per call).

---

## 9.8 Time and Space Complexity of Recursion

### How to Analyze

1. **Time**: Count the total number of recursive calls times the work per call.
2. **Space**: The maximum depth of the call stack (plus any auxiliary data).

| Algorithm          | Time       | Space     | Tree Shape   |
|--------------------|------------|-----------|--------------|
| Factorial          | O(n)       | O(n)      | Linear       |
| Fibonacci (naive)  | O(2^n)     | O(n)      | Binary       |
| Fibonacci (memo)   | O(n)       | O(n)      | Pruned       |
| Binary search      | O(log n)   | O(log n)  | Linear       |
| Merge sort         | O(n log n) | O(n)      | Binary       |
| Permutations       | O(n!)      | O(n)      | n-ary        |

---

## 9.9 Common Mistakes

1. **Missing base case**: The most common mistake. Without a base case, recursion runs until stack overflow.

2. **Base case that is never reached**: For example, decrementing when you should be incrementing, or passing the wrong argument to the recursive call.

3. **Modifying shared mutable state**: If multiple recursive branches modify the same list or variable, results can be unpredictable. Pass copies or use immutable data.

4. **Not returning the recursive result**: A common bug:
   ```python
   # WRONG:
   def factorial(n):
       if n <= 1: return 1
       factorial(n - 1) * n  # Missing return!

   # CORRECT:
   def factorial(n):
       if n <= 1: return 1
       return factorial(n - 1) * n
   ```

5. **Using recursion when iteration is simpler**: Not everything needs recursion. A simple loop to sum numbers is clearer than a recursive function.

---

## 9.10 Best Practices

1. **Write the base case first**: Before writing any recursive logic, define when the recursion stops. This prevents infinite recursion.

2. **Trust the recursion**: Assume the recursive call returns the correct answer for the smaller problem. Focus on how to use that answer to solve the current problem. Do not try to trace every call in your head.

3. **Make the problem smaller**: Every recursive call must reduce the problem size. If `n` starts at 10, the next call should use 9, or `n/2`, or a shorter list.

4. **Use memoization when you see repeated subproblems**: If your recursion tree has duplicate nodes, add a cache.

5. **Convert to iteration for production code with deep recursion**: In performance-critical code or when recursion depth could be large, use an explicit stack and a loop.

---

## Quick Summary

**Recursion** is a technique where a function solves a problem by calling itself on smaller inputs. Every recursive function needs a **base case** (when to stop) and a **recursive case** (how to break the problem down). The **call stack** tracks each pending function call. Naive recursion can be exponentially slow (Fibonacci), but **memoization** caches results to avoid redundant work. **Stack overflow** occurs when recursion is too deep. Draw **recursion trees** to visualize execution.

---

## Key Points

- Recursion = solving a problem by solving smaller versions of the same problem
- Two essential parts: base case (stop) and recursive case (divide and recurse)
- The call stack grows with each recursive call and unwinds as calls return
- Factorial: O(n) time, O(n) space
- Naive Fibonacci: O(2^n) time -- exponentially slow due to duplicate work
- Memoization caches results, turning O(2^n) into O(n)
- Stack overflow happens when recursion depth exceeds the limit
- Recursion trees visualize the structure of recursive calls
- Trust the recursion: assume the smaller call returns the right answer

---

## Practice Questions

1. What are the two essential parts of every recursive function? What happens if you forget the base case?

2. Trace the call stack for `factorial(4)`. Draw each frame being pushed and then popped.

3. Why is naive recursive Fibonacci O(2^n)? Draw the recursion tree for `fib(6)` and count the total calls.

4. Convert the following recursive function to an iterative one:
   ```python
   def sum_to(n):
       if n <= 0:
           return 0
       return n + sum_to(n - 1)
   ```

5. A recursive function has this code: `return f(n) + f(n-1)`. Is this making progress toward a base case? What is wrong?

---

## LeetCode-Style Problems

### Problem 1: Power of a Number (LeetCode 50 -- Pow(x, n))

**Problem**: Implement `pow(x, n)` which calculates x raised to the power n.

**Approach**: Use **fast exponentiation**. Instead of multiplying x by itself n times (O(n)), use the insight that `x^n = (x^(n/2))^2`. This gives O(log n).

```
x^10 = (x^5)^2
x^5  = x * (x^2)^2
x^2  = (x^1)^2
x^1  = x * (x^0)^2
x^0  = 1

Total multiplications: 4 (log2(10) ~= 3.3)
```

**Python Solution**:

```python
def my_pow(x, n):
    if n == 0:
        return 1
    if n < 0:
        x = 1 / x
        n = -n

    def helper(x, n):
        if n == 0:
            return 1
        half = helper(x, n // 2)
        if n % 2 == 0:
            return half * half
        else:
            return half * half * x

    return helper(x, n)


print(my_pow(2, 10))    # Output: 1024
print(my_pow(2.1, 3))   # Output: 9.261
print(my_pow(2, -2))    # Output: 0.25
```

**Java Solution**:

```java
public class Power {
    public static double myPow(double x, int n) {
        long N = n;  // Handle Integer.MIN_VALUE
        if (N < 0) {
            x = 1 / x;
            N = -N;
        }
        return helper(x, N);
    }

    private static double helper(double x, long n) {
        if (n == 0) return 1.0;
        double half = helper(x, n / 2);
        if (n % 2 == 0) {
            return half * half;
        } else {
            return half * half * x;
        }
    }

    public static void main(String[] args) {
        System.out.println(myPow(2, 10));   // Output: 1024.0
        System.out.println(myPow(2, -2));   // Output: 0.25
    }
}
```

**Complexity**: Time: O(log n). Space: O(log n) for the call stack.

---

### Problem 2: Reverse String Recursively (LeetCode 344)

**Problem**: Reverse a character array in-place using recursion.

**Approach**: Swap the first and last characters, then recursively reverse the middle portion.

```
['h', 'e', 'l', 'l', 'o']

Step 1: Swap index 0 and 4: ['o', 'e', 'l', 'l', 'h']
Step 2: Swap index 1 and 3: ['o', 'l', 'l', 'e', 'h']
Step 3: left=2, right=2 -> base case (left >= right)

Result: ['o', 'l', 'l', 'e', 'h']
```

**Python Solution**:

```python
def reverse_string(s):
    def helper(left, right):
        if left >= right:
            return  # Base case
        s[left], s[right] = s[right], s[left]  # Swap
        helper(left + 1, right - 1)             # Recurse on middle

    helper(0, len(s) - 1)


chars = ['h', 'e', 'l', 'l', 'o']
reverse_string(chars)
print(chars)  # Output: ['o', 'l', 'l', 'e', 'h']
```

**Java Solution**:

```java
public class ReverseString {
    public static void reverseString(char[] s) {
        helper(s, 0, s.length - 1);
    }

    private static void helper(char[] s, int left, int right) {
        if (left >= right) return;  // Base case
        char temp = s[left];
        s[left] = s[right];
        s[right] = temp;
        helper(s, left + 1, right - 1);  // Recurse
    }

    public static void main(String[] args) {
        char[] s = {'h', 'e', 'l', 'l', 'o'};
        reverseString(s);
        System.out.println(new String(s));  // Output: olleh
    }
}
```

**Complexity**: Time: O(n). Space: O(n) for the call stack (could be O(1) with iteration).

---

### Problem 3: Generate Parentheses (LeetCode 22)

**Problem**: Given n pairs of parentheses, generate all valid combinations.

**Approach**: Use recursion with two counters: `open` (number of `(` used) and `close` (number of `)` used). Add `(` if open < n. Add `)` if close < open (ensures validity).

```
n = 3
Recursion tree (partial):

                    ""
                    |
                   "("
                 /     \
             "(("       "()"
            /   \         |
         "((("  "(()"    "()"  -> can add ( or )
           |     / \
        "((()""(()(" "(())"
           |
        "((())""
           |
        "((()))"  <- valid!
```

**Python Solution**:

```python
def generate_parenthesis(n):
    result = []

    def backtrack(current, open_count, close_count):
        if len(current) == 2 * n:
            result.append(current)  # Base case: used all parentheses
            return

        if open_count < n:
            backtrack(current + "(", open_count + 1, close_count)

        if close_count < open_count:
            backtrack(current + ")", open_count, close_count + 1)

    backtrack("", 0, 0)
    return result


print(generate_parenthesis(3))
# Output: ['((()))', '(()())', '(())()', '()(())', '()()()']
```

**Java Solution**:

```java
import java.util.ArrayList;
import java.util.List;

public class GenerateParentheses {
    public static List<String> generateParenthesis(int n) {
        List<String> result = new ArrayList<>();
        backtrack(result, new StringBuilder(), 0, 0, n);
        return result;
    }

    private static void backtrack(List<String> result, StringBuilder current,
                                   int open, int close, int n) {
        if (current.length() == 2 * n) {
            result.add(current.toString());
            return;
        }

        if (open < n) {
            current.append('(');
            backtrack(result, current, open + 1, close, n);
            current.deleteCharAt(current.length() - 1);  // Undo
        }

        if (close < open) {
            current.append(')');
            backtrack(result, current, open, close + 1, n);
            current.deleteCharAt(current.length() - 1);  // Undo
        }
    }

    public static void main(String[] args) {
        System.out.println(generateParenthesis(3));
        // Output: [((())), (()()), (())(), ()(()), ()()()]
    }
}
```

**Complexity**: Time: O(4^n / sqrt(n)) -- the n-th Catalan number. Space: O(n) for the recursion depth.

---

### Problem 4: Subsets (LeetCode 78)

**Problem**: Given an integer array of unique elements, return all possible subsets (the power set).

**Approach**: For each element, you have two choices: include it or exclude it. Recursively build subsets by making this choice at each index.

```
nums = [1, 2, 3]

                         []
                       /    \
                 [1]           []
               /    \        /    \
           [1,2]   [1]    [2]    []
           / \     / \    / \   / \
       [1,2,3][1,2][1,3][1][2,3][2][3][]
```

**Python Solution**:

```python
def subsets(nums):
    result = []

    def backtrack(index, current):
        if index == len(nums):
            result.append(current[:])  # Add copy of current subset
            return

        # Choice 1: Include nums[index]
        current.append(nums[index])
        backtrack(index + 1, current)

        # Choice 2: Exclude nums[index]
        current.pop()
        backtrack(index + 1, current)

    backtrack(0, [])
    return result


print(subsets([1, 2, 3]))
# Output: [[1,2,3], [1,2], [1,3], [1], [2,3], [2], [3], []]
```

**Java Solution**:

```java
import java.util.ArrayList;
import java.util.List;

public class Subsets {
    public static List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        backtrack(nums, 0, new ArrayList<>(), result);
        return result;
    }

    private static void backtrack(int[] nums, int index,
                                   List<Integer> current,
                                   List<List<Integer>> result) {
        if (index == nums.length) {
            result.add(new ArrayList<>(current));
            return;
        }

        // Include nums[index]
        current.add(nums[index]);
        backtrack(nums, index + 1, current, result);

        // Exclude nums[index]
        current.remove(current.size() - 1);
        backtrack(nums, index + 1, current, result);
    }

    public static void main(String[] args) {
        System.out.println(subsets(new int[]{1, 2, 3}));
        // Output: [[1,2,3], [1,2], [1,3], [1], [2,3], [2], [3], []]
    }
}
```

**Complexity**: Time: O(2^n) -- there are 2^n subsets. Space: O(n) for recursion depth.

---

### Problem 5: Permutations (LeetCode 46)

**Problem**: Given an array of distinct integers, return all possible permutations.

**Approach**: At each position, try every unused number. Track which numbers are used and backtrack after each attempt.

```
nums = [1, 2, 3]

                          []
                    /      |      \
               [1]        [2]       [3]
              /   \      /   \     /   \
          [1,2] [1,3] [2,1] [2,3] [3,1] [3,2]
           |      |     |     |     |      |
        [1,2,3][1,3,2][2,1,3][2,3,1][3,1,2][3,2,1]
```

**Python Solution**:

```python
def permutations(nums):
    result = []

    def backtrack(current, remaining):
        if not remaining:
            result.append(current[:])  # Base case
            return

        for i in range(len(remaining)):
            current.append(remaining[i])
            # Recurse with the chosen element removed
            backtrack(current, remaining[:i] + remaining[i+1:])
            current.pop()  # Undo choice (backtrack)

    backtrack([], nums)
    return result


print(permutations([1, 2, 3]))
# Output: [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]
```

**Java Solution**:

```java
import java.util.ArrayList;
import java.util.List;

public class Permutations {
    public static List<List<Integer>> permute(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        boolean[] used = new boolean[nums.length];
        backtrack(nums, used, new ArrayList<>(), result);
        return result;
    }

    private static void backtrack(int[] nums, boolean[] used,
                                   List<Integer> current,
                                   List<List<Integer>> result) {
        if (current.size() == nums.length) {
            result.add(new ArrayList<>(current));
            return;
        }

        for (int i = 0; i < nums.length; i++) {
            if (used[i]) continue;

            used[i] = true;
            current.add(nums[i]);
            backtrack(nums, used, current, result);
            current.remove(current.size() - 1);  // Undo
            used[i] = false;                       // Undo
        }
    }

    public static void main(String[] args) {
        System.out.println(permute(new int[]{1, 2, 3}));
        // Output: [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]
    }
}
```

**Complexity**: Time: O(n! * n) -- there are n! permutations, each of length n. Space: O(n) for recursion depth.

---

## What Is Next?

Now that you understand recursion, you are ready to see it in action with **sorting algorithms**. In the next chapter, we start with the simpler sorting methods -- **Bubble Sort, Selection Sort, and Insertion Sort** -- each of which can be understood step by step with small arrays. These O(n^2) algorithms are the building blocks for understanding the more powerful O(n log n) sorts that follow.
