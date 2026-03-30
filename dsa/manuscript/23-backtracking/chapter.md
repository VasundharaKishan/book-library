# Chapter 23: Backtracking

## What You Will Learn

- What backtracking is and how it explores all possible solutions by undoing bad choices
- The universal backtracking template: choose, explore, unchoose
- How to visualize backtracking with decision tree diagrams
- How to solve N-Queens step by step with constraint checking
- How to build a Sudoku solver using backtracking
- How pruning dramatically improves backtracking performance
- How to solve permutations, combinations, subsets, word search, and palindrome partitioning

## Why This Chapter Matters

Some problems have no clever shortcut. There is no greedy strategy that works, and no DP formulation that avoids exploring all possibilities. For these problems, you need **backtracking**: a systematic way to try every option, abandon dead ends, and continue searching.

Backtracking is the algorithm behind solving Sudoku puzzles, placing queens on a chessboard, finding all permutations, generating valid parentheses, and solving constraint satisfaction problems. In interviews, backtracking problems are extremely common at the medium and hard level.

The good news: once you learn the template, every backtracking problem follows the same structure. The differences are only in what choices you make and what constraints you check.

---

## 23.1 What Is Backtracking?

Backtracking is a refined brute-force approach that builds solutions incrementally and abandons a path as soon as it determines that the path cannot lead to a valid solution.

### The Maze Analogy

```
Imagine solving a maze:

  S . . #
  # . # .
  . . . #
  # # . E

Strategy:
  1. At each intersection, CHOOSE a direction
  2. Walk down that path (EXPLORE)
  3. If you hit a dead end, go back and try another direction (UNCHOOSE)

This is backtracking!
  - You do not randomly wander
  - You systematically try each option
  - You UNDO your choice when it fails
  - You continue until you find the exit (or prove there is none)
```

### The Backtracking Template

Every backtracking problem follows this pattern:

```python
def backtrack(state, choices):
    # Base case: found a valid solution
    if is_solution(state):
        record(state)
        return

    for choice in choices:
        # Pruning: skip invalid choices
        if not is_valid(choice, state):
            continue

        # CHOOSE: make the choice
        make_choice(state, choice)

        # EXPLORE: recurse with the updated state
        backtrack(state, remaining_choices)

        # UNCHOOSE: undo the choice (backtrack!)
        undo_choice(state, choice)
```

```
The three steps in every backtracking algorithm:

  1. CHOOSE:    Add the current option to the partial solution
  2. EXPLORE:   Recurse to extend the partial solution
  3. UNCHOOSE:  Remove the current option (restore state)

This is also called: Make, Recurse, Unmake
```

---

## 23.2 Decision Trees

Every backtracking problem can be visualized as a decision tree. Each node represents a partial solution, each branch represents a choice, and leaves are complete solutions (or dead ends).

### Example: Generating All Subsets of {1, 2, 3}

At each step, decide: include the element or exclude it.

```
Decision Tree for subsets of {1, 2, 3}:

                         {}
                    /          \
               {1}              {}
              /    \          /    \
          {1,2}    {1}     {2}     {}
          /  \    /  \    /  \    /  \
      {1,2,3} {1,2} {1,3} {1} {2,3} {2} {3} {}

All subsets (leaves):
  {1,2,3}, {1,2}, {1,3}, {1}, {2,3}, {2}, {3}, {}
```

### Example: Generating All Permutations of [1, 2, 3]

At each step, choose which unused element to place next.

```
Decision Tree for permutations of [1, 2, 3]:

                    []
              /      |      \
           [1]      [2]     [3]
          /   \    /   \   /   \
       [1,2] [1,3] [2,1] [2,3] [3,1] [3,2]
         |     |     |     |     |     |
     [1,2,3] [1,3,2] [2,1,3] [2,3,1] [3,1,2] [3,2,1]

6 permutations = 3! = 6
```

---

## 23.3 Subsets

**Problem:** Given an array of distinct integers, return all possible subsets.

**Python:**

```python
def subsets(nums):
    result = []

    def backtrack(start, current):
        # Every node in the tree is a valid subset
        result.append(current[:])  # Add a copy

        for i in range(start, len(nums)):
            # CHOOSE
            current.append(nums[i])

            # EXPLORE
            backtrack(i + 1, current)

            # UNCHOOSE
            current.pop()

    backtrack(0, [])
    return result


# Test
print("Subsets of [1,2,3]:")
for s in subsets([1, 2, 3]):
    print(f"  {s}")
```

**Output:**

```
Subsets of [1,2,3]:
  []
  [1]
  [1, 2]
  [1, 2, 3]
  [1, 3]
  [2]
  [2, 3]
  [3]
```

**Java:**

```java
import java.util.*;

public class Subsets {

    public static List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        backtrack(nums, 0, new ArrayList<>(), result);
        return result;
    }

    private static void backtrack(int[] nums, int start,
            List<Integer> current,
            List<List<Integer>> result) {

        result.add(new ArrayList<>(current));

        for (int i = start; i < nums.length; i++) {
            current.add(nums[i]);          // Choose
            backtrack(nums, i + 1,
                current, result);          // Explore
            current.remove(
                current.size() - 1);       // Unchoose
        }
    }

    public static void main(String[] args) {
        List<List<Integer>> result = subsets(
            new int[]{1, 2, 3});
        for (List<Integer> subset : result) {
            System.out.println(subset);
        }
    }
}
```

**Time Complexity:** O(n * 2^n). There are 2^n subsets, each taking O(n) to copy.

**Space Complexity:** O(n) for the recursion stack.

---

## 23.4 Permutations

**Problem:** Given an array of distinct integers, return all possible permutations.

**Python:**

```python
def permutations(nums):
    result = []

    def backtrack(current, remaining):
        # Base case: no more elements to place
        if not remaining:
            result.append(current[:])
            return

        for i in range(len(remaining)):
            # CHOOSE
            current.append(remaining[i])

            # EXPLORE (with the element removed from remaining)
            backtrack(current,
                      remaining[:i] + remaining[i+1:])

            # UNCHOOSE
            current.pop()

    backtrack([], nums)
    return result


# Alternative using a 'used' set (more efficient)
def permutations_v2(nums):
    result = []
    used = [False] * len(nums)

    def backtrack(current):
        if len(current) == len(nums):
            result.append(current[:])
            return

        for i in range(len(nums)):
            if used[i]:
                continue

            used[i] = True            # Choose
            current.append(nums[i])

            backtrack(current)         # Explore

            current.pop()             # Unchoose
            used[i] = False

    backtrack([])
    return result


# Test
print("Permutations of [1,2,3]:")
for p in permutations_v2([1, 2, 3]):
    print(f"  {p}")
```

**Output:**

```
Permutations of [1,2,3]:
  [1, 2, 3]
  [1, 3, 2]
  [2, 1, 3]
  [2, 3, 1]
  [3, 1, 2]
  [3, 2, 1]
```

**Java:**

```java
import java.util.*;

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

            current.remove(current.size() - 1);
            used[i] = false;
        }
    }

    public static void main(String[] args) {
        System.out.println(permute(new int[]{1, 2, 3}));
    }
}
```

**Time Complexity:** O(n * n!). There are n! permutations, each taking O(n) to copy.

**Space Complexity:** O(n) for the recursion stack and the `used` array.

---

## 23.5 Combinations

**Problem:** Given n and k, return all combinations of k numbers chosen from 1 to n.

**Python:**

```python
def combine(n, k):
    result = []

    def backtrack(start, current):
        # Base case: combination is complete
        if len(current) == k:
            result.append(current[:])
            return

        # Pruning: need (k - len(current)) more elements,
        # so do not start too late
        remaining_needed = k - len(current)
        last_valid = n - remaining_needed + 1

        for i in range(start, last_valid + 1):
            current.append(i)        # Choose
            backtrack(i + 1, current)  # Explore
            current.pop()             # Unchoose

    backtrack(1, [])
    return result


# Test
print("C(4, 2):")
for c in combine(4, 2):
    print(f"  {c}")
```

**Output:**

```
C(4, 2):
  [1, 2]
  [1, 3]
  [1, 4]
  [2, 3]
  [2, 4]
  [3, 4]
```

**Java:**

```java
import java.util.*;

public class Combinations {

    public static List<List<Integer>> combine(int n, int k) {
        List<List<Integer>> result = new ArrayList<>();
        backtrack(n, k, 1, new ArrayList<>(), result);
        return result;
    }

    private static void backtrack(int n, int k, int start,
            List<Integer> current,
            List<List<Integer>> result) {

        if (current.size() == k) {
            result.add(new ArrayList<>(current));
            return;
        }

        int remaining = k - current.size();
        for (int i = start; i <= n - remaining + 1; i++) {
            current.add(i);
            backtrack(n, k, i + 1, current, result);
            current.remove(current.size() - 1);
        }
    }

    public static void main(String[] args) {
        System.out.println(combine(4, 2));
    }
}
```

**Time Complexity:** O(k * C(n,k)). **Space Complexity:** O(k) for the recursion stack.

---

## 23.6 N-Queens

**Problem:** Place n queens on an n x n chessboard so that no two queens attack each other (same row, column, or diagonal).

### Step-by-Step Walkthrough for 4-Queens

```
Place queens row by row. At each row, try each column.

Row 0: Try column 0
  . Q . .     Row 0, Col 1 (after col 0 fails quickly)

Row 0: Try col 0
  Board:
  Q . . .
  . . ? .     Row 1: try each column
  . . . .
  . . . .

  Row 1, col 0: same column as Q at (0,0) --> INVALID
  Row 1, col 1: same diagonal as Q at (0,0) --> INVALID
  Row 1, col 2: OK!
    Q . . .
    . . Q .
    . . . .    Row 2: try each column
    . . . .

    Row 2, col 0: diagonal conflict with (1,2) --> INVALID
    Row 2, col 1: column and diagonal conflicts --> INVALID
    Row 2, col 2: same column as (1,2) --> INVALID
    Row 2, col 3: diagonal conflict with (1,2) --> INVALID
    ALL FAIL --> BACKTRACK to row 1

  Row 1, col 3: OK!
    Q . . .
    . . . Q
    . . . .
    . . . .

    Row 2, col 0: diagonal conflict --> INVALID
    Row 2, col 1: OK!
      Q . . .
      . . . Q
      . Q . .
      . . . .

      Row 3, col 0: diagonal conflict with (2,1) --> INVALID
      Row 3, col 1: same column as (2,1) --> INVALID
      Row 3, col 2: diagonal conflicts --> INVALID
      Row 3, col 3: same column as (1,3) --> INVALID
      ALL FAIL --> BACKTRACK

    Row 2, col 2: same diagonal as (1,3) --> INVALID
    Row 2, col 3: same column as (1,3) --> INVALID
    BACKTRACK to row 0

Row 0: Try col 1
  . Q . .
  . . . .
  . . . .
  . . . .

  Row 1, col 3: OK!
    . Q . .
    . . . Q
    . . . .
    . . . .

    Row 2, col 0: OK!
      . Q . .
      . . . Q
      Q . . .
      . . . .

      Row 3, col 2: OK! (no conflicts)
        . Q . .
        . . . Q
        Q . . .
        . . Q .

        SOLUTION FOUND!
```

### Implementation

**Python:**

```python
def solve_n_queens(n):
    result = []
    # Track which columns and diagonals are under attack
    cols = set()
    diag1 = set()  # row - col (identifies / diagonals)
    diag2 = set()  # row + col (identifies \ diagonals)

    board = [['.' for _ in range(n)] for _ in range(n)]

    def backtrack(row):
        # Base case: all queens placed
        if row == n:
            # Record this solution
            result.append(
                [''.join(r) for r in board])
            return

        for col in range(n):
            # Pruning: check if this position is safe
            if col in cols or \
               (row - col) in diag1 or \
               (row + col) in diag2:
                continue

            # CHOOSE
            board[row][col] = 'Q'
            cols.add(col)
            diag1.add(row - col)
            diag2.add(row + col)

            # EXPLORE
            backtrack(row + 1)

            # UNCHOOSE
            board[row][col] = '.'
            cols.remove(col)
            diag1.remove(row - col)
            diag2.remove(row + col)

    backtrack(0)
    return result


# Test
solutions = solve_n_queens(4)
print(f"Number of solutions for 4-Queens: {len(solutions)}")
for i, sol in enumerate(solutions):
    print(f"\nSolution {i + 1}:")
    for row in sol:
        print(f"  {row}")

# Count solutions for larger boards
for n in range(1, 9):
    count = len(solve_n_queens(n))
    print(f"{n}-Queens: {count} solutions")
```

**Output:**

```
Number of solutions for 4-Queens: 2

Solution 1:
  .Q..
  ...Q
  Q...
  ..Q.

Solution 2:
  ..Q.
  Q...
  ...Q
  .Q..

1-Queens: 1 solutions
2-Queens: 0 solutions
3-Queens: 0 solutions
4-Queens: 2 solutions
5-Queens: 10 solutions
6-Queens: 4 solutions
7-Queens: 40 solutions
8-Queens: 92 solutions
```

**Java:**

```java
import java.util.*;

public class NQueens {

    public static List<List<String>> solveNQueens(int n) {
        List<List<String>> result = new ArrayList<>();
        char[][] board = new char[n][n];

        for (char[] row : board) Arrays.fill(row, '.');

        Set<Integer> cols = new HashSet<>();
        Set<Integer> diag1 = new HashSet<>();
        Set<Integer> diag2 = new HashSet<>();

        backtrack(board, 0, cols, diag1, diag2, result);
        return result;
    }

    private static void backtrack(char[][] board, int row,
            Set<Integer> cols, Set<Integer> diag1,
            Set<Integer> diag2,
            List<List<String>> result) {

        if (row == board.length) {
            List<String> solution = new ArrayList<>();
            for (char[] r : board) {
                solution.add(new String(r));
            }
            result.add(solution);
            return;
        }

        for (int col = 0; col < board.length; col++) {
            if (cols.contains(col) ||
                diag1.contains(row - col) ||
                diag2.contains(row + col)) {
                continue;
            }

            board[row][col] = 'Q';
            cols.add(col);
            diag1.add(row - col);
            diag2.add(row + col);

            backtrack(board, row + 1, cols,
                diag1, diag2, result);

            board[row][col] = '.';
            cols.remove(col);
            diag1.remove(row - col);
            diag2.remove(row + col);
        }
    }

    public static void main(String[] args) {
        List<List<String>> solutions = solveNQueens(4);
        System.out.println("Solutions: " + solutions.size());
        for (List<String> sol : solutions) {
            for (String row : sol) {
                System.out.println("  " + row);
            }
            System.out.println();
        }
    }
}
```

**Time Complexity:** O(n!) -- at most n choices for the first row, n-1 for the second, etc.

**Space Complexity:** O(n) for the recursion stack and constraint sets.

---

## 23.7 Sudoku Solver

**Problem:** Fill in a 9x9 Sudoku board so every row, column, and 3x3 box contains digits 1-9.

**Backtracking approach:** Find an empty cell, try digits 1-9, check constraints, recurse, and undo if stuck.

**Python:**

```python
def solve_sudoku(board):
    """
    Solve Sudoku in-place using backtracking.
    board: 9x9 list of lists ('.' for empty cells)
    """
    def is_valid(row, col, num):
        # Check row
        if num in board[row]:
            return False

        # Check column
        for r in range(9):
            if board[r][col] == num:
                return False

        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if board[r][c] == num:
                    return False

        return True

    def backtrack():
        # Find the next empty cell
        for row in range(9):
            for col in range(9):
                if board[row][col] == '.':
                    # Try digits 1-9
                    for num in '123456789':
                        if is_valid(row, col, num):
                            board[row][col] = num  # Choose

                            if backtrack():        # Explore
                                return True

                            board[row][col] = '.'  # Unchoose

                    return False  # No valid digit, backtrack

        return True  # All cells filled

    backtrack()


# Test
board = [
    ['5','3','.','.','7','.','.','.','.'],
    ['6','.','.','1','9','5','.','.','.'],
    ['.','9','8','.','.','.','.','6','.'],
    ['8','.','.','.','6','.','.','.','3'],
    ['4','.','.','8','.','3','.','.','1'],
    ['7','.','.','.','2','.','.','.','6'],
    ['.','6','.','.','.','.','2','8','.'],
    ['.','.','.','4','1','9','.','.','5'],
    ['.','.','.','.','8','.','.','7','9']
]

solve_sudoku(board)

print("Solved Sudoku:")
for row in board:
    print(' '.join(row))
```

**Output:**

```
Solved Sudoku:
5 3 4 6 7 8 9 1 2
6 7 2 1 9 5 3 4 8
1 9 8 3 4 2 5 6 7
8 5 9 7 6 1 4 2 3
4 2 6 8 5 3 7 9 1
7 1 3 9 2 4 8 5 6
9 6 1 5 3 7 2 8 4
2 8 7 4 1 9 6 3 5
3 4 5 2 8 6 1 7 9
```

**Time Complexity:** O(9^(empty_cells)) in the worst case, but pruning makes it much faster in practice.

**Space Complexity:** O(empty_cells) for the recursion stack.

---

## 23.8 Word Search

**Problem:** Given a 2D board of characters and a word, determine if the word can be found by moving horizontally or vertically to adjacent cells (each cell used at most once).

**Python:**

```python
def exist(board, word):
    rows, cols = len(board), len(board[0])

    def backtrack(r, c, index):
        # Base case: all characters matched
        if index == len(word):
            return True

        # Boundary and character check
        if (r < 0 or r >= rows or
            c < 0 or c >= cols or
            board[r][c] != word[index]):
            return False

        # CHOOSE: mark as visited
        temp = board[r][c]
        board[r][c] = '#'

        # EXPLORE: try all 4 directions
        found = (backtrack(r + 1, c, index + 1) or
                 backtrack(r - 1, c, index + 1) or
                 backtrack(r, c + 1, index + 1) or
                 backtrack(r, c - 1, index + 1))

        # UNCHOOSE: restore the cell
        board[r][c] = temp

        return found

    for r in range(rows):
        for c in range(cols):
            if backtrack(r, c, 0):
                return True

    return False


# Test
board = [
    ['A','B','C','E'],
    ['S','F','C','S'],
    ['A','D','E','E']
]

print(f"'ABCCED': {exist(board, 'ABCCED')}")
print(f"'SEE': {exist(board, 'SEE')}")
print(f"'ABCB': {exist(board, 'ABCB')}")
```

**Output:**

```
'ABCCED': True
'SEE': True
'ABCB': False
```

**Java:**

```java
public class WordSearch {

    public static boolean exist(char[][] board, String word) {
        int rows = board.length, cols = board[0].length;

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (backtrack(board, word, r, c, 0)) {
                    return true;
                }
            }
        }
        return false;
    }

    private static boolean backtrack(char[][] board,
            String word, int r, int c, int index) {

        if (index == word.length()) return true;

        if (r < 0 || r >= board.length ||
            c < 0 || c >= board[0].length ||
            board[r][c] != word.charAt(index)) {
            return false;
        }

        char temp = board[r][c];
        board[r][c] = '#';  // Mark visited

        boolean found =
            backtrack(board, word, r+1, c, index+1) ||
            backtrack(board, word, r-1, c, index+1) ||
            backtrack(board, word, r, c+1, index+1) ||
            backtrack(board, word, r, c-1, index+1);

        board[r][c] = temp;  // Restore

        return found;
    }

    public static void main(String[] args) {
        char[][] board = {
            {'A','B','C','E'},
            {'S','F','C','S'},
            {'A','D','E','E'}
        };
        System.out.println(exist(board, "ABCCED"));
        // Output: true
    }
}
```

**Time Complexity:** O(m * n * 4^L) where L is the word length. **Space Complexity:** O(L) for recursion.

---

## 23.9 Palindrome Partitioning

**Problem:** Given a string, partition it such that every substring is a palindrome. Return all possible partitions.

**Python:**

```python
def partition(s):
    result = []

    def is_palindrome(start, end):
        while start < end:
            if s[start] != s[end]:
                return False
            start += 1
            end -= 1
        return True

    def backtrack(start, current):
        # Base case: reached the end of string
        if start == len(s):
            result.append(current[:])
            return

        for end in range(start, len(s)):
            # Pruning: only proceed if substring is a palindrome
            if is_palindrome(start, end):
                current.append(s[start:end + 1])  # Choose
                backtrack(end + 1, current)        # Explore
                current.pop()                      # Unchoose

    backtrack(0, [])
    return result


# Test
print("Partitions of 'aab':")
for p in partition('aab'):
    print(f"  {p}")

print("\nPartitions of 'aaba':")
for p in partition('aaba'):
    print(f"  {p}")
```

**Output:**

```
Partitions of 'aab':
  ['a', 'a', 'b']
  ['aa', 'b']

Partitions of 'aaba':
  ['a', 'a', 'b', 'a']
  ['a', 'aba']
  ['aa', 'b', 'a']
```

**Java:**

```java
import java.util.*;

public class PalindromePartitioning {

    public static List<List<String>> partition(String s) {
        List<List<String>> result = new ArrayList<>();
        backtrack(s, 0, new ArrayList<>(), result);
        return result;
    }

    private static void backtrack(String s, int start,
            List<String> current,
            List<List<String>> result) {

        if (start == s.length()) {
            result.add(new ArrayList<>(current));
            return;
        }

        for (int end = start; end < s.length(); end++) {
            if (isPalindrome(s, start, end)) {
                current.add(s.substring(start, end + 1));
                backtrack(s, end + 1, current, result);
                current.remove(current.size() - 1);
            }
        }
    }

    private static boolean isPalindrome(
            String s, int left, int right) {
        while (left < right) {
            if (s.charAt(left++) != s.charAt(right--)) {
                return false;
            }
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(partition("aab"));
        // Output: [[a, a, b], [aa, b]]
    }
}
```

**Time Complexity:** O(n * 2^n). **Space Complexity:** O(n) for recursion.

---

## 23.10 Pruning: Making Backtracking Fast

Pruning means cutting off branches of the decision tree that cannot lead to valid solutions. Good pruning can make the difference between a solution that runs in seconds and one that takes hours.

```
Without pruning:
                    [root]
              /    |    |    \
             a     b    c     d
           / | \  ...  ...  ...
          ...

  Explores ALL branches. Slow!

With pruning:
                    [root]
              /    |    |    \
             a     b    X     X     <-- c, d pruned early
           / | \  / \
          ... X   ...              <-- some sub-branches pruned

  Skips invalid branches immediately. Fast!
```

### Common Pruning Strategies

| Strategy | Description | Example |
|----------|-------------|---------|
| Constraint checking | Skip choices that violate constraints | N-Queens: skip attacked columns |
| Sorting | Process items in order to prune more | Combination Sum: skip if too large |
| Early termination | Stop if current path cannot beat best | Branch and Bound |
| Symmetry breaking | Avoid exploring symmetric solutions | N-Queens: only try half of first row |
| Feasibility check | Check if remaining elements are sufficient | Combinations: prune if too few left |

### Example: Combinations with Pruning

```python
# Without pruning
def combine_no_prune(n, k):
    result = []
    def backtrack(start, current):
        if len(current) == k:
            result.append(current[:])
            return
        for i in range(start, n + 1):  # Tries too many!
            current.append(i)
            backtrack(i + 1, current)
            current.pop()
    backtrack(1, [])
    return result

# With pruning
def combine_pruned(n, k):
    result = []
    def backtrack(start, current):
        if len(current) == k:
            result.append(current[:])
            return
        # Prune: need (k - len(current)) more elements
        # So stop when not enough elements remain
        remaining_needed = k - len(current)
        for i in range(start, n - remaining_needed + 2):
            current.append(i)
            backtrack(i + 1, current)
            current.pop()
    backtrack(1, [])
    return result

# Both give same results, but pruned version is faster
print(f"C(10,7) without pruning: {len(combine_no_prune(10,7))}")
print(f"C(10,7) with pruning: {len(combine_pruned(10,7))}")
```

**Output:**

```
C(10,7) without pruning: 120
C(10,7) with pruning: 120
```

Both produce 120 combinations, but the pruned version makes far fewer recursive calls.

---

## Common Mistakes

1. **Forgetting to unchoose (undo).** This is the most common backtracking bug. If you add to a set, remove it. If you append to a list, pop it. If you modify the board, restore it.

2. **Not making a copy when recording solutions.** In Python, `result.append(current)` stores a reference, not a copy. The list will change as backtracking continues. Always use `result.append(current[:])` or `result.append(list(current))`.

3. **Missing base cases.** Every backtracking function needs a clear stopping condition. Without it, recursion never terminates.

4. **Not pruning enough.** Without pruning, backtracking degenerates into brute force. Always think about what constraints you can check BEFORE making a recursive call.

5. **Modifying the input without restoring.** When using the input (like a board or grid) to track state, always restore modified cells in the unchoose step.

---

## Best Practices

1. **Always use the choose-explore-unchoose template.** This structure makes your code clean and prevents forgetting the undo step.

2. **Draw the decision tree first.** Before writing code, sketch the tree for a small input. This clarifies what choices you make at each level and what the base case looks like.

3. **Prune as early as possible.** Check constraints before making the recursive call, not after. This avoids unnecessary work.

4. **Use sets for O(1) constraint checking.** In N-Queens, using sets for columns and diagonals gives O(1) checks instead of O(n) scans.

5. **Sort the input when order helps pruning.** For problems like Combination Sum, sorting allows you to break early when the remaining candidates are all too large.

---

## Quick Summary

```
Backtracking = try all options, undo bad choices

Template:
  1. CHOOSE:    make a decision
  2. EXPLORE:   recurse with the decision
  3. UNCHOOSE:  undo the decision

Common problems:
  Subsets:      include/exclude each element
  Permutations: pick unused elements in order
  Combinations: pick k elements from n
  N-Queens:     place queens row by row, check constraints
  Sudoku:       fill cells, try digits 1-9
  Word Search:  traverse grid matching characters

Pruning = skip branches that cannot lead to valid solutions
  - Check constraints BEFORE recursing
  - Use sets for O(1) lookups
  - Sort input to enable early breaks
```

## Key Points

- Backtracking systematically explores all possible solutions by building them incrementally and undoing choices that lead to dead ends.
- The choose-explore-unchoose template applies to every backtracking problem.
- Decision trees help visualize the search space: nodes are partial solutions, branches are choices, and leaves are solutions or dead ends.
- Pruning is essential for performance. The earlier you eliminate invalid branches, the faster the algorithm runs.
- Always make a copy when recording a solution, and always restore state when undoing a choice.
- N-Queens and Sudoku demonstrate how constraint tracking (using sets) enables efficient pruning.

---

## Practice Questions

1. How does backtracking differ from brute force? When is backtracking more efficient?

2. Modify the subsets solution to handle duplicate elements (e.g., [1, 2, 2] should not produce duplicate subsets).

3. Explain why we iterate right-to-left in the N-Queens constraint check. What would happen if we did not track diagonals?

4. How many total nodes does the decision tree have for generating all permutations of n elements? How does pruning reduce this?

5. Design a backtracking solution for the Knight's Tour problem: visit every cell on an n x n chessboard exactly once using a knight.

---

## LeetCode-Style Problems

### Problem 1: Combination Sum (Medium)

Given candidates (no duplicates) and a target, find all unique combinations where the candidates sum to the target. Each candidate may be used unlimited times.

```python
def combination_sum(candidates, target):
    result = []
    candidates.sort()  # Sort for pruning

    def backtrack(start, current, remaining):
        if remaining == 0:
            result.append(current[:])
            return

        for i in range(start, len(candidates)):
            # Pruning: if current candidate exceeds remaining, stop
            if candidates[i] > remaining:
                break

            current.append(candidates[i])
            # Use i (not i+1) because we can reuse candidates
            backtrack(i, current, remaining - candidates[i])
            current.pop()

    backtrack(0, [], target)
    return result


# Test
print(combination_sum([2, 3, 6, 7], 7))
# Output: [[2, 2, 3], [7]]
```

### Problem 2: Letter Combinations of a Phone Number (Medium)

Given a string of digits 2-9, return all possible letter combinations.

```python
def letter_combinations(digits):
    if not digits:
        return []

    phone = {
        '2': 'abc', '3': 'def', '4': 'ghi',
        '5': 'jkl', '6': 'mno', '7': 'pqrs',
        '8': 'tuv', '9': 'wxyz'
    }

    result = []

    def backtrack(index, current):
        if index == len(digits):
            result.append(current)
            return

        for letter in phone[digits[index]]:
            backtrack(index + 1, current + letter)

    backtrack(0, '')
    return result


# Test
print(letter_combinations('23'))
# Output: ['ad','ae','af','bd','be','bf','cd','ce','cf']
```

### Problem 3: Generate Parentheses (Medium)

Generate all valid combinations of n pairs of parentheses.

```python
def generate_parenthesis(n):
    result = []

    def backtrack(current, open_count, close_count):
        if len(current) == 2 * n:
            result.append(current)
            return

        # Can add '(' if we have not used all n
        if open_count < n:
            backtrack(current + '(', open_count + 1,
                      close_count)

        # Can add ')' only if it would not exceed '(' count
        if close_count < open_count:
            backtrack(current + ')', open_count,
                      close_count + 1)

    backtrack('', 0, 0)
    return result


# Test
print(generate_parenthesis(3))
# Output: ['((()))', '(()())', '(())()', '()(())', '()()()']
```

---

## What Is Next?

Backtracking explores all possibilities by trying every path. But many array and string problems have a more efficient approach: instead of checking every combination, you can sweep through the data with a **sliding window**. In Chapter 24, you will learn how this technique processes arrays in O(n) time by maintaining a window of relevant elements.
