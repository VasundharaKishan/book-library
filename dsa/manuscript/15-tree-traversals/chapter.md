# Chapter 15: Tree Traversals -- Every Way to Walk a Tree

## What You Will Learn

- The three depth-first traversals: in-order (Left-Root-Right), pre-order (Root-Left-Right), and post-order (Left-Right-Root)
- How to visualize visit order using ASCII diagrams
- Both recursive and iterative implementations using an explicit stack
- When to use each traversal and why it matters
- Level-order traversal (BFS) and its variations
- How to solve classic problems: max depth, symmetric tree, path sum, binary tree paths, invert binary tree, and serialize/deserialize

## Why This Chapter Matters

A tree is only useful if you can visit its nodes. The way you visit them -- the **traversal order** -- determines what problems you can solve.

Need sorted output from a BST? Use in-order. Need to copy or serialize a tree? Use pre-order. Need to calculate sizes or delete a tree safely? Use post-order. Need the shortest path or level-by-level processing? Use level-order.

Choosing the wrong traversal makes problems impossible. Choosing the right one makes them trivial. This chapter gives you the skill to look at any tree problem and immediately know which traversal to reach for.

Iterative traversals using explicit stacks are a frequent interview topic because they test your understanding of how recursion actually works under the hood.

---

## 15.1 The Three Depth-First Traversals

All three depth-first traversals visit the same nodes. The only difference is **when they process the current node** relative to its children.

We will use this tree throughout the chapter:

```
         1
        / \
       2   3
      / \   \
     4   5   6
```

### In-Order: Left, Root, Right

Visit the left subtree first, then the current node, then the right subtree.

```
         1
        / \
       2   3
      / \   \
     4   5   6

Visit order: 4, 2, 5, 1, 3, 6

Trace:
  inorder(1)
    inorder(2)
      inorder(4)
        inorder(None) -> return
        visit 4                   <- 1st
        inorder(None) -> return
      visit 2                     <- 2nd
      inorder(5)
        inorder(None) -> return
        visit 5                   <- 3rd
        inorder(None) -> return
    visit 1                       <- 4th
    inorder(3)
      inorder(None) -> return
      visit 3                     <- 5th
      inorder(6)
        inorder(None) -> return
        visit 6                   <- 6th
        inorder(None) -> return
```

**When to use**: In-order on a BST gives sorted output. Any problem involving sorted order in a BST.

### Pre-Order: Root, Left, Right

Visit the current node first, then the left subtree, then the right subtree.

```
         1
        / \
       2   3
      / \   \
     4   5   6

Visit order: 1, 2, 4, 5, 3, 6

Trace:
  preorder(1)
    visit 1                       <- 1st
    preorder(2)
      visit 2                     <- 2nd
      preorder(4)
        visit 4                   <- 3rd
        preorder(None) -> return
        preorder(None) -> return
      preorder(5)
        visit 5                   <- 4th
        preorder(None) -> return
        preorder(None) -> return
    preorder(3)
      visit 3                     <- 5th
      preorder(None) -> return
      preorder(6)
        visit 6                   <- 6th
        preorder(None) -> return
        preorder(None) -> return
```

**When to use**: Copying or serializing a tree. Pre-order visits the root first, so you can reconstruct the tree by processing nodes in the order they were serialized.

### Post-Order: Left, Right, Root

Visit the left subtree first, then the right subtree, then the current node.

```
         1
        / \
       2   3
      / \   \
     4   5   6

Visit order: 4, 5, 2, 6, 3, 1

Trace:
  postorder(1)
    postorder(2)
      postorder(4)
        postorder(None) -> return
        postorder(None) -> return
        visit 4                   <- 1st
      postorder(5)
        postorder(None) -> return
        postorder(None) -> return
        visit 5                   <- 2nd
      visit 2                     <- 3rd
    postorder(3)
      postorder(None) -> return
      postorder(6)
        postorder(None) -> return
        postorder(None) -> return
        visit 6                   <- 4th
      visit 3                     <- 5th
    visit 1                       <- 6th
```

**When to use**: When you need children's results before processing the parent. Calculating subtree sizes, deleting a tree (delete children before parent), evaluating expression trees.

### Side-by-Side Comparison

```
         1
        / \
       2   3
      / \   \
     4   5   6

In-order   (L, Root, R): 4, 2, 5, 1, 3, 6
Pre-order  (Root, L, R): 1, 2, 4, 5, 3, 6
Post-order (L, R, Root): 4, 5, 2, 6, 3, 1
Level-order (BFS):       1, 2, 3, 4, 5, 6
```

> **Memory Aid**: The name tells you where the **Root** goes. **Pre**-order = root first. **In**-order = root in the middle. **Post**-order = root last.

---

## 15.2 Recursive Implementations

**Python:**

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def inorder(root):
    """In-order: Left -> Root -> Right"""
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


def preorder(root):
    """Pre-order: Root -> Left -> Right"""
    if root is None:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)


def postorder(root):
    """Post-order: Left -> Right -> Root"""
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]


# Build tree:
#        1
#       / \
#      2   3
#     / \   \
#    4   5   6
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)
root.right.right = TreeNode(6)

print("In-order:  ", inorder(root))
print("Pre-order: ", preorder(root))
print("Post-order:", postorder(root))
```

**Output:**
```
In-order:   [4, 2, 5, 1, 3, 6]
Pre-order:  [1, 2, 4, 5, 3, 6]
Post-order: [4, 5, 2, 6, 3, 1]
```

**Java:**

```java
import java.util.*;

class TreeNode {
    int val;
    TreeNode left, right;
    TreeNode(int val) { this.val = val; }
}

public class TreeTraversals {

    public static List<Integer> inorder(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        inorderHelper(root, result);
        return result;
    }

    private static void inorderHelper(TreeNode node, List<Integer> result) {
        if (node == null) return;
        inorderHelper(node.left, result);
        result.add(node.val);
        inorderHelper(node.right, result);
    }

    public static List<Integer> preorder(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        preorderHelper(root, result);
        return result;
    }

    private static void preorderHelper(TreeNode node, List<Integer> result) {
        if (node == null) return;
        result.add(node.val);
        preorderHelper(node.left, result);
        preorderHelper(node.right, result);
    }

    public static List<Integer> postorder(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        postorderHelper(root, result);
        return result;
    }

    private static void postorderHelper(TreeNode node, List<Integer> result) {
        if (node == null) return;
        postorderHelper(node.left, result);
        postorderHelper(node.right, result);
        result.add(node.val);
    }

    public static void main(String[] args) {
        TreeNode root = new TreeNode(1);
        root.left = new TreeNode(2);
        root.right = new TreeNode(3);
        root.left.left = new TreeNode(4);
        root.left.right = new TreeNode(5);
        root.right.right = new TreeNode(6);

        System.out.println("In-order:   " + inorder(root));
        System.out.println("Pre-order:  " + preorder(root));
        System.out.println("Post-order: " + postorder(root));
    }
}
```

**Output:**
```
In-order:   [4, 2, 5, 1, 3, 6]
Pre-order:  [1, 2, 4, 5, 3, 6]
Post-order: [4, 5, 2, 6, 3, 1]
```

---

## 15.3 Iterative Implementations (Using a Stack)

Interviewers love iterative tree traversals because they test whether you truly understand what the recursion stack does behind the scenes. Instead of relying on the call stack, we manage our own stack explicitly.

### Iterative Pre-Order (Easiest)

Pre-order is the easiest to convert because we process the node immediately.

```
Algorithm:
1. Push root onto stack.
2. While stack is not empty:
   a. Pop a node, process it.
   b. Push RIGHT child first (so left is processed first).
   c. Push LEFT child.
```

**Step-by-Step Walkthrough:**

```
         1
        / \
       2   3
      / \   \
     4   5   6

Stack: [1]
  Pop 1, process 1.  Push right=3, push left=2.  Stack: [3, 2]
  Pop 2, process 2.  Push right=5, push left=4.  Stack: [3, 5, 4]
  Pop 4, process 4.  No children.                Stack: [3, 5]
  Pop 5, process 5.  No children.                Stack: [3]
  Pop 3, process 3.  Push right=6, no left.      Stack: [6]
  Pop 6, process 6.  No children.                Stack: []

Output: 1, 2, 4, 5, 3, 6  (matches pre-order!)
```

**Python:**

```python
def preorder_iterative(root):
    """Iterative pre-order traversal using a stack."""
    if root is None:
        return []

    result = []
    stack = [root]

    while stack:
        node = stack.pop()
        result.append(node.val)

        # Push right first so left is processed first
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)

    return result


print("Iterative pre-order:", preorder_iterative(root))
```

**Output:**
```
Iterative pre-order: [1, 2, 4, 5, 3, 6]
```

### Iterative In-Order

In-order is trickier because we cannot process a node until we have visited its entire left subtree.

```
Algorithm:
1. Start at root.
2. Go as far LEFT as possible, pushing each node onto the stack.
3. When you cannot go left, pop from stack, process the node.
4. Move to the RIGHT child and repeat from step 2.
```

**Step-by-Step Walkthrough:**

```
         1
        / \
       2   3
      / \   \
     4   5   6

current=1, push 1, go left.  Stack: [1]
current=2, push 2, go left.  Stack: [1, 2]
current=4, push 4, go left.  Stack: [1, 2, 4]
current=None, pop 4, process 4, go right (None).  Stack: [1, 2]
Pop 2, process 2, go right to 5.  Stack: [1]
current=5, push 5, go left (None).  Stack: [1, 5]
Pop 5, process 5, go right (None).  Stack: [1]
Pop 1, process 1, go right to 3.  Stack: []
current=3, push 3, go left (None).  Stack: [3]
Pop 3, process 3, go right to 6.  Stack: []
current=6, push 6, go left (None).  Stack: [6]
Pop 6, process 6, go right (None).  Stack: []

Output: 4, 2, 5, 1, 3, 6  (matches in-order!)
```

**Python:**

```python
def inorder_iterative(root):
    """Iterative in-order traversal using a stack."""
    result = []
    stack = []
    current = root

    while current or stack:
        # Go as far left as possible
        while current:
            stack.append(current)
            current = current.left

        # Process the leftmost unprocessed node
        current = stack.pop()
        result.append(current.val)

        # Move to right subtree
        current = current.right

    return result


print("Iterative in-order:", inorder_iterative(root))
```

**Output:**
```
Iterative in-order: [4, 2, 5, 1, 3, 6]
```

### Iterative Post-Order

Post-order is the trickiest. One clean approach: do a modified pre-order (Root, Right, Left) and reverse the result.

```
Normal pre-order:   Root, Left, Right   -> 1, 2, 4, 5, 3, 6
Modified pre-order: Root, Right, Left   -> 1, 3, 6, 2, 5, 4
Reverse:            Left, Right, Root   -> 4, 5, 2, 6, 3, 1  (post-order!)
```

**Python:**

```python
def postorder_iterative(root):
    """Iterative post-order using modified pre-order + reverse."""
    if root is None:
        return []

    result = []
    stack = [root]

    while stack:
        node = stack.pop()
        result.append(node.val)

        # Push LEFT first (opposite of pre-order)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)

    return result[::-1]  # Reverse


print("Iterative post-order:", postorder_iterative(root))
```

**Output:**
```
Iterative post-order: [4, 5, 2, 6, 3, 1]
```

**Java (all three):**

```java
import java.util.*;

public class IterativeTraversals {

    public static List<Integer> preorderIterative(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        if (root == null) return result;

        Deque<TreeNode> stack = new ArrayDeque<>();
        stack.push(root);

        while (!stack.isEmpty()) {
            TreeNode node = stack.pop();
            result.add(node.val);
            if (node.right != null) stack.push(node.right);
            if (node.left != null) stack.push(node.left);
        }

        return result;
    }

    public static List<Integer> inorderIterative(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        Deque<TreeNode> stack = new ArrayDeque<>();
        TreeNode current = root;

        while (current != null || !stack.isEmpty()) {
            while (current != null) {
                stack.push(current);
                current = current.left;
            }
            current = stack.pop();
            result.add(current.val);
            current = current.right;
        }

        return result;
    }

    public static List<Integer> postorderIterative(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        if (root == null) return result;

        Deque<TreeNode> stack = new ArrayDeque<>();
        stack.push(root);

        while (!stack.isEmpty()) {
            TreeNode node = stack.pop();
            result.add(node.val);
            if (node.left != null) stack.push(node.left);
            if (node.right != null) stack.push(node.right);
        }

        Collections.reverse(result);
        return result;
    }
}
```

### Complexity for All Traversals

| Traversal | Time | Space (Recursive) | Space (Iterative) |
|---|---|---|---|
| In-order | O(n) | O(h) call stack | O(h) explicit stack |
| Pre-order | O(n) | O(h) call stack | O(h) explicit stack |
| Post-order | O(n) | O(h) call stack | O(h) explicit stack |
| Level-order | O(n) | -- | O(w) queue width |

Where h = tree height, w = max width. For balanced tree h = O(log n), for skewed h = O(n).

---

## 15.4 When to Use Which Traversal

| Traversal | Use When | Examples |
|---|---|---|
| **In-order** | Need sorted order from BST | Kth smallest, validate BST, sorted output |
| **Pre-order** | Need to process parent before children | Serialize tree, copy tree, build expression |
| **Post-order** | Need children's results before parent | Calculate subtree size, delete tree, evaluate expressions |
| **Level-order** | Need level-by-level processing | Shortest path, level averages, right-side view |

### Decision Flowchart

```
Is it a BST problem needing sorted order?
  YES -> In-order

Do you need to process parent before children?
  YES -> Pre-order

Do you need children results to compute parent result?
  YES -> Post-order

Do you need level-by-level information?
  YES -> Level-order (BFS)
```

---

## 15.5 Level-Order Traversal (BFS) Revisited

We covered basic level-order in Chapter 13. Here is the grouped-by-level version, which is what most problems require:

**Python:**

```python
from collections import deque


def level_order(root):
    """Level-order traversal returning values grouped by level."""
    if root is None:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        current_level = []

        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)

    return result


print("Level-order:", level_order(root))
```

**Output:**
```
Level-order: [[1], [2, 3], [4, 5, 6]]
```

---

## Common Mistakes

1. **Mixing up traversal orders.** Pre-order is Root-Left-Right, not Left-Root-Right. Draw it out if unsure. The name tells you where Root goes: pre (before), in (middle), post (after).

2. **Post-order description error.** Post-order is Left-Right-Root, NOT Left-Right-Right. This is a common typo that leads to incorrect implementations.

3. **Forgetting to push right before left in iterative pre-order.** Since a stack is LIFO, if you want to process left first, you must push right first.

4. **Using a stack for level-order.** Level-order (BFS) requires a queue (FIFO). Using a stack gives you DFS behavior, which is wrong for level-by-level processing.

5. **Creating new lists in recursive implementations.** The pattern `inorder(left) + [root] + inorder(right)` creates many temporary lists. For large trees, use a helper function that appends to a shared result list instead.

---

## Best Practices

1. **Start with recursive implementations.** They are simpler, easier to debug, and correct. Only switch to iterative if the problem requires it or the tree is extremely deep.

2. **Learn the iterative in-order pattern by heart.** It appears in many interview problems (kth smallest, BST iterator, validate BST). The "go left, pop, go right" pattern is fundamental.

3. **Use level-order for any "level" keyword.** If the problem mentions levels, minimum depth, or breadth, BFS with a queue is almost certainly the right approach.

4. **Return early when possible.** In problems like "does path sum exist," you can return `True` as soon as you find a valid path instead of traversing the entire tree.

5. **Think about what information flows up vs. down.** If information flows from leaves to root (subtree sizes, heights), use post-order. If information flows from root to leaves (paths, constraints), use pre-order.

---

## Quick Summary

| Traversal | Order | Key Pattern | Primary Use |
|---|---|---|---|
| In-order | Left, Root, Right | Sorted BST output | BST problems |
| Pre-order | Root, Left, Right | Process root first | Serialization, copying |
| Post-order | Left, Right, Root | Process root last | Size calculations, deletion |
| Level-order | Level by level | Queue-based BFS | Level-based problems |

---

## Key Points

- All DFS traversals visit the same nodes in O(n) time; only the processing order differs.
- Iterative traversals use an explicit stack to simulate the call stack.
- In-order traversal of a BST produces sorted output.
- Level-order traversal uses a queue and is the only BFS traversal for trees.
- Pre-order is the easiest to implement iteratively; post-order is the trickiest.
- The choice of traversal determines which problems you can solve efficiently.

---

## Practice Questions

1. **Trace all traversals**: For the tree `[10, 5, 15, 3, 7, 12, 20]`, write the output of in-order, pre-order, post-order, and level-order traversals.

2. **Iterative in-order trace**: Using the tree from question 1, trace through the iterative in-order algorithm step by step, showing the stack state at each iteration.

3. **Traversal identification**: You are given a tree's pre-order output `[1, 2, 4, 5, 3, 6]` and in-order output `[4, 2, 5, 1, 3, 6]`. Can you reconstruct the tree? Draw it.

4. **When to use which**: For each scenario, name the best traversal:
   - Print all values of a BST in sorted order
   - Calculate the size of every subtree
   - Print a tree level by level
   - Create an exact copy of a tree

5. **Stack vs. queue**: Explain why BFS uses a queue while iterative DFS uses a stack. What would happen if you swapped them?

---

## LeetCode-Style Problems

### Problem 1: Maximum Depth of Binary Tree (LeetCode 104)

**Problem**: Return the maximum depth of a binary tree (number of nodes along the longest root-to-leaf path).

**Solution (Post-order -- need children results first):**

```python
def max_depth(root):
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


# BFS alternative
def max_depth_bfs(root):
    if root is None:
        return 0

    depth = 0
    queue = deque([root])

    while queue:
        depth += 1
        for _ in range(len(queue)):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return depth


root = TreeNode(3)
root.left = TreeNode(9)
root.right = TreeNode(20)
root.right.left = TreeNode(15)
root.right.right = TreeNode(7)

print(f"Max depth (recursive): {max_depth(root)}")  # 3
print(f"Max depth (BFS): {max_depth_bfs(root)}")     # 3
```

**Output:**
```
Max depth (recursive): 3
Max depth (BFS): 3
```

```java
public int maxDepth(TreeNode root) {
    if (root == null) return 0;
    return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
}
```

**Complexity**: O(n) time, O(h) space.

---

### Problem 2: Symmetric Tree (LeetCode 101)

**Problem**: Check whether a binary tree is a mirror of itself (symmetric around its center).

```
Symmetric:           Not symmetric:
      1                    1
     / \                  / \
    2   2                2   2
   / \ / \                \   \
  3  4 4  3                3   3
```

**Solution:**

```python
def is_symmetric(root):
    if root is None:
        return True
    return is_mirror(root.left, root.right)


def is_mirror(left, right):
    if left is None and right is None:
        return True
    if left is None or right is None:
        return False
    return (left.val == right.val and
            is_mirror(left.left, right.right) and
            is_mirror(left.right, right.left))


# Symmetric tree
from collections import deque

def build_tree(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root

tree1 = build_tree([1, 2, 2, 3, 4, 4, 3])
tree2 = build_tree([1, 2, 2, None, 3, None, 3])

print(f"Symmetric: {is_symmetric(tree1)}")      # True
print(f"Not symmetric: {is_symmetric(tree2)}")   # False
```

**Output:**
```
Symmetric: True
Not symmetric: False
```

```java
public boolean isSymmetric(TreeNode root) {
    if (root == null) return true;
    return isMirror(root.left, root.right);
}

private boolean isMirror(TreeNode left, TreeNode right) {
    if (left == null && right == null) return true;
    if (left == null || right == null) return false;
    return left.val == right.val
        && isMirror(left.left, right.right)
        && isMirror(left.right, right.left);
}
```

**Complexity**: O(n) time, O(h) space.

---

### Problem 3: Path Sum (LeetCode 112)

**Problem**: Given a binary tree and a target sum, determine if the tree has a root-to-leaf path where the values sum to the target.

```
         5
        / \
       4   8
      /   / \
     11  13  4
    / \       \
   7   2       1

Target = 22
Path: 5 -> 4 -> 11 -> 2 = 22. Return True.
```

**Solution (Pre-order -- pass remaining sum down):**

```python
def has_path_sum(root, target_sum):
    if root is None:
        return False

    # Check if this is a leaf and the sum matches
    remaining = target_sum - root.val
    if root.left is None and root.right is None:
        return remaining == 0

    # Try left and right subtrees
    return (has_path_sum(root.left, remaining) or
            has_path_sum(root.right, remaining))


root = build_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])
print(f"Has path sum 22: {has_path_sum(root, 22)}")  # True
print(f"Has path sum 10: {has_path_sum(root, 10)}")  # False
```

**Output:**
```
Has path sum 22: True
Has path sum 10: False
```

```java
public boolean hasPathSum(TreeNode root, int targetSum) {
    if (root == null) return false;

    int remaining = targetSum - root.val;
    if (root.left == null && root.right == null) {
        return remaining == 0;
    }

    return hasPathSum(root.left, remaining)
        || hasPathSum(root.right, remaining);
}
```

**Complexity**: O(n) time, O(h) space.

---

### Problem 4: Binary Tree Paths (LeetCode 257)

**Problem**: Given the root of a binary tree, return all root-to-leaf paths as strings.

```
         1
        / \
       2   3
        \
         5

Output: ["1->2->5", "1->3"]
```

**Solution (Pre-order -- build path top-down):**

```python
def binary_tree_paths(root):
    result = []

    def dfs(node, path):
        if node is None:
            return

        path.append(str(node.val))

        if node.left is None and node.right is None:
            # Leaf: record the path
            result.append("->".join(path))
        else:
            dfs(node.left, path)
            dfs(node.right, path)

        path.pop()  # Backtrack

    dfs(root, [])
    return result


root = build_tree([1, 2, 3, None, 5])
print("Paths:", binary_tree_paths(root))
```

**Output:**
```
Paths: ['1->2->5', '1->3']
```

```java
public List<String> binaryTreePaths(TreeNode root) {
    List<String> result = new ArrayList<>();
    if (root != null) {
        dfs(root, new StringBuilder(), result);
    }
    return result;
}

private void dfs(TreeNode node, StringBuilder path, List<String> result) {
    int len = path.length();
    if (path.length() > 0) path.append("->");
    path.append(node.val);

    if (node.left == null && node.right == null) {
        result.add(path.toString());
    } else {
        if (node.left != null) dfs(node.left, path, result);
        if (node.right != null) dfs(node.right, path, result);
    }

    path.setLength(len);  // Backtrack
}
```

**Complexity**: O(n) time, O(h) space for recursion (O(n * h) total for path strings).

---

### Problem 5: Serialize and Deserialize Binary Tree (LeetCode 297)

**Problem**: Design an algorithm to serialize a binary tree to a string and deserialize it back.

**Approach**: Use pre-order traversal. Mark null nodes with a sentinel value.

```
         1
        / \
       2   3
          / \
         4   5

Serialize (pre-order): "1,2,#,#,3,4,#,#,5,#,#"
  (# represents null)
```

**Solution:**

```python
class Codec:
    def serialize(self, root):
        """Serialize tree to string using pre-order."""
        result = []

        def preorder(node):
            if node is None:
                result.append("#")
                return
            result.append(str(node.val))
            preorder(node.left)
            preorder(node.right)

        preorder(root)
        return ",".join(result)

    def deserialize(self, data):
        """Deserialize string back to tree."""
        values = iter(data.split(","))

        def build():
            val = next(values)
            if val == "#":
                return None
            node = TreeNode(int(val))
            node.left = build()
            node.right = build()
            return node

        return build()


# Test
codec = Codec()
root = build_tree([1, 2, 3, None, None, 4, 5])

serialized = codec.serialize(root)
print(f"Serialized: {serialized}")

deserialized = codec.deserialize(serialized)
print(f"Deserialized level-order: {level_order(deserialized)}")

# Verify round-trip
print(f"Round-trip: {codec.serialize(deserialized) == serialized}")
```

**Output:**
```
Serialized: 1,2,#,#,3,4,#,#,5,#,#
Deserialized level-order: [[1], [2, 3], [4, 5]]
Round-trip: True
```

```java
public class Codec {
    public String serialize(TreeNode root) {
        StringBuilder sb = new StringBuilder();
        serializeHelper(root, sb);
        return sb.toString();
    }

    private void serializeHelper(TreeNode node, StringBuilder sb) {
        if (node == null) {
            sb.append("#,");
            return;
        }
        sb.append(node.val).append(",");
        serializeHelper(node.left, sb);
        serializeHelper(node.right, sb);
    }

    public TreeNode deserialize(String data) {
        Queue<String> queue = new LinkedList<>(Arrays.asList(data.split(",")));
        return deserializeHelper(queue);
    }

    private TreeNode deserializeHelper(Queue<String> queue) {
        String val = queue.poll();
        if (val.equals("#")) return null;
        TreeNode node = new TreeNode(Integer.parseInt(val));
        node.left = deserializeHelper(queue);
        node.right = deserializeHelper(queue);
        return node;
    }
}
```

**Complexity**: O(n) time and O(n) space for both serialize and deserialize.

---

## What Is Next?

Trees gave us hierarchical structure. Traversals gave us the ability to explore that structure. In Chapter 16, you will learn about **Heaps** -- a special kind of complete binary tree that always keeps the minimum (or maximum) element at the root. Heaps power priority queues, which are essential for algorithms like Dijkstra's shortest path, task scheduling, and finding the kth largest element efficiently.
