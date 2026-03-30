# Chapter 13: Trees -- The Foundation of Hierarchical Data

## What You Will Learn

- What a tree data structure is and how it mirrors real-world hierarchies
- Essential tree terminology: root, parent, child, leaf, height, depth, level, subtree, and degree
- What a binary tree is and how it differs from general trees
- The differences between complete, full, perfect, and balanced binary trees
- How to implement a tree node class in Python and Java
- How to calculate tree height recursively
- How to count all nodes in a tree
- How to perform level-order traversal (BFS) using a queue

## Why This Chapter Matters

Trees are everywhere. Your computer's file system is a tree. The HTML of every web page is a tree. Your company's organizational chart is a tree. Family genealogies, tournament brackets, decision-making processes, and database indexes all use trees.

Up to this point, every data structure you have studied has been linear -- arrays, linked lists, stacks, and queues all arrange elements in a single sequence. Trees break free from that constraint. They organize data **hierarchically**, where one element can connect to multiple elements below it, creating a branching structure.

Mastering trees is not optional if you want to succeed in technical interviews or build efficient software. Binary search trees power fast lookups. Heaps enable priority queues. Tries make autocomplete possible. Parse trees run compilers. DOM trees render web pages. If you understand the fundamentals in this chapter, every tree-based structure that follows will feel natural.

---

## 13.1 What Is a Tree?

A **tree** is a hierarchical data structure consisting of **nodes** connected by **edges**. It has exactly one special node called the **root** at the top, and every other node has exactly one parent.

Think of a family tree:

```
                    Grandma Rose
                   /            \
             Dad Mike          Aunt Sarah
            /        \              |
        You        Sister       Cousin Tom
```

Grandma Rose is at the top (the root). She has two children. Each of those children can have their own children. Nobody has two parents in this simplified tree. That one-parent rule is what makes a tree a **tree** and not a general graph.

### Real-World Examples of Trees

| Real-World Structure | Root | Children | Leaves |
|---|---|---|---|
| File system | `/` (root directory) | Subdirectories | Files |
| Organizational chart | CEO | Vice Presidents | Individual contributors |
| HTML document | `<html>` | `<head>`, `<body>` | Text nodes |
| Family tree | Oldest ancestor | Children | Youngest generation |
| Tournament bracket | Final match | Semifinal matches | First-round matches |

### Formal Definition

A tree `T` is a collection of nodes where:

1. There is one distinguished node called the **root**.
2. Every non-root node is connected to exactly **one parent** node by an edge.
3. There is exactly **one path** from the root to any node.
4. A tree with `n` nodes has exactly `n - 1` edges.

If you remove rule 2 or 3, you get a **graph**, not a tree. We will study graphs in Chapters 17 and 18.

---

## 13.2 Tree Terminology

Let us build a vocabulary using this example tree:

```
              A          <-- Level 0 (Root)
            / | \
           B  C  D       <-- Level 1
          / \    |
         E   F   G       <-- Level 2
        /
       H                 <-- Level 3
```

### Essential Terms

| Term | Definition | Example |
|---|---|---|
| **Root** | The topmost node with no parent | `A` |
| **Parent** | A node that has children below it | `B` is parent of `E` and `F` |
| **Child** | A node directly connected below another node | `E` and `F` are children of `B` |
| **Sibling** | Nodes sharing the same parent | `B`, `C`, `D` are siblings |
| **Leaf** | A node with no children (also called external node) | `C`, `F`, `G`, `H` |
| **Internal node** | A node with at least one child | `A`, `B`, `D`, `E` |
| **Edge** | The connection between a parent and child | The line from `A` to `B` |
| **Path** | A sequence of nodes connected by edges | `A -> B -> E -> H` |
| **Subtree** | A node and all its descendants | Subtree rooted at `B` contains `B, E, F, H` |
| **Degree** | The number of children a node has | Degree of `A` is 3, degree of `C` is 0 |

### Height vs. Depth vs. Level

These three terms confuse many beginners. Here is the clear distinction:

```
              A          depth=0, level=0
            / | \
           B  C  D       depth=1, level=1
          / \    |
         E   F   G       depth=2, level=2
        /
       H                 depth=3, level=3

Height of H = 0  (leaf)
Height of E = 1  (one edge to H)
Height of B = 2  (longest path down: B->E->H)
Height of A = 3  (longest path down: A->B->E->H)
Height of tree = 3
```

| Term | Measured From | Direction | Example |
|---|---|---|---|
| **Depth** of a node | Root to that node | Top-down | Depth of `E` = 2 |
| **Height** of a node | That node to deepest leaf below | Bottom-up | Height of `B` = 2 |
| **Level** | Same as depth | Top-down | Level of `G` = 2 |
| **Height of tree** | Root to deepest leaf | Top-down | Height of tree = 3 |

> **Memory Aid**: **Depth** is how deep you have dived from the surface (root). **Height** is how tall the tree is below you.

---

## 13.3 Binary Trees

A **binary tree** is a tree where each node has **at most two children**, called the **left child** and **right child**.

```
         10
        /  \
       5    15
      / \     \
     3   7    20
```

This is the most commonly studied type of tree because:
- It is simple enough to reason about
- It supports efficient searching (binary search trees, Chapter 14)
- It maps naturally to divide-and-conquer algorithms
- It can be stored efficiently in arrays (heaps, Chapter 16)

### Binary Tree Node Implementation

**Python:**

```python
class TreeNode:
    """A node in a binary tree."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        return f"TreeNode({self.val})"


# Building a tree manually:
#        1
#       / \
#      2   3
#     / \
#    4   5

root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

print(root)          # TreeNode(1)
print(root.left)     # TreeNode(2)
print(root.right)    # TreeNode(3)
```

**Output:**
```
TreeNode(1)
TreeNode(2)
TreeNode(3)
```

**Java:**

```java
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;

    TreeNode(int val) {
        this.val = val;
        this.left = null;
        this.right = null;
    }

    @Override
    public String toString() {
        return "TreeNode(" + val + ")";
    }
}

public class BinaryTreeDemo {
    public static void main(String[] args) {
        //        1
        //       / \
        //      2   3
        //     / \
        //    4   5

        TreeNode root = new TreeNode(1);
        root.left = new TreeNode(2);
        root.right = new TreeNode(3);
        root.left.left = new TreeNode(4);
        root.left.right = new TreeNode(5);

        System.out.println(root);        // TreeNode(1)
        System.out.println(root.left);   // TreeNode(2)
        System.out.println(root.right);  // TreeNode(3)
    }
}
```

**Output:**
```
TreeNode(1)
TreeNode(2)
TreeNode(3)
```

---

## 13.4 Types of Binary Trees

Understanding the different types of binary trees is essential because each type has distinct properties that affect algorithm performance.

### Full Binary Tree

Every node has **either 0 or 2 children**. No node has exactly one child.

```
         1
        / \
       2   3
      / \
     4   5

Full binary tree: YES
(Every node has 0 or 2 children)
```

```
         1
        / \
       2   3
      /
     4

Full binary tree: NO
(Node 2 has only 1 child)
```

**Property**: A full binary tree with `n` internal nodes has `n + 1` leaves.

### Complete Binary Tree

All levels are completely filled **except possibly the last level**, and the last level has nodes filled from **left to right**.

```
         1
        / \
       2   3
      / \ /
     4  5 6

Complete binary tree: YES
(Last level filled left to right)
```

```
         1
        / \
       2   3
      /     \
     4       6

Complete binary tree: NO
(Last level has a gap -- 6 is right child without left sibling)
```

**Why it matters**: Complete binary trees can be stored in arrays without wasting space. This is how heaps work (Chapter 16).

### Perfect Binary Tree

All internal nodes have **exactly 2 children** AND all leaves are at the **same level**.

```
         1
        / \
       2   3
      / \ / \
     4  5 6  7

Perfect binary tree: YES
(All leaves at level 2, all internal nodes have 2 children)
```

**Properties**:
- A perfect binary tree of height `h` has `2^(h+1) - 1` nodes
- Height 0: 1 node
- Height 1: 3 nodes
- Height 2: 7 nodes
- Height 3: 15 nodes
- Number of leaves = `2^h`
- Every perfect binary tree is also complete and full

### Balanced Binary Tree

The height difference between the left and right subtrees of **every node** is at most 1.

```
         1                    1
        / \                  / \
       2   3                2   3
      / \                  /
     4   5                4
                         /
Balanced: YES           5
(Max height diff = 1)
                    Balanced: NO
                    (Left subtree height=2,
                     right subtree height=0,
                     diff=2)
```

**Why it matters**: A balanced binary tree guarantees O(log n) height, which means operations like search, insert, and delete stay fast. An unbalanced tree can degrade to O(n) -- essentially becoming a linked list.

### Comparison Summary

```
Perfect  -->  implies  -->  Complete  -->  implies  -->  Balanced
Perfect  -->  implies  -->  Full

But NOT the reverse! A complete tree is not necessarily perfect.
A balanced tree is not necessarily complete.
```

| Type | Key Rule | Example Use |
|---|---|---|
| Full | Every node: 0 or 2 children | Expression trees |
| Complete | All levels full except last (left-filled) | Binary heaps |
| Perfect | All leaves same depth, all internals have 2 kids | Theoretical analysis |
| Balanced | Height difference <= 1 at every node | AVL trees, Red-Black trees |

---

## 13.5 Calculating Tree Height

The **height** of a tree is the number of edges on the longest path from the root to a leaf. An empty tree has height -1 and a single-node tree has height 0.

### Recursive Approach

The height of a tree rooted at node `n` is:
```
height(n) = 1 + max(height(n.left), height(n.right))
```

**Step-by-Step Walkthrough:**

```
         1
        / \
       2   3
      / \
     4   5

height(4) = 0  (leaf)
height(5) = 0  (leaf)
height(2) = 1 + max(height(4), height(5)) = 1 + max(0, 0) = 1
height(3) = 0  (leaf)
height(1) = 1 + max(height(2), height(3)) = 1 + max(1, 0) = 1 + 1 = 2

Tree height = 2
```

**Python:**

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def tree_height(root):
    """Calculate the height of a binary tree.

    Height = number of edges on longest root-to-leaf path.
    Empty tree returns -1, single node returns 0.
    """
    if root is None:
        return -1

    left_height = tree_height(root.left)
    right_height = tree_height(root.right)

    return 1 + max(left_height, right_height)


# Build tree:
#        1
#       / \
#      2   3
#     / \
#    4   5
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

print(f"Tree height: {tree_height(root)}")         # 2
print(f"Height of left subtree: {tree_height(root.left)}")   # 1
print(f"Height of right subtree: {tree_height(root.right)}") # 0
print(f"Height of empty tree: {tree_height(None)}")          # -1
```

**Output:**
```
Tree height: 2
Height of left subtree: 1
Height of right subtree: 0
Height of empty tree: -1
```

**Java:**

```java
class TreeNode {
    int val;
    TreeNode left, right;

    TreeNode(int val) {
        this.val = val;
    }
}

public class TreeHeight {

    public static int treeHeight(TreeNode root) {
        if (root == null) {
            return -1;
        }

        int leftHeight = treeHeight(root.left);
        int rightHeight = treeHeight(root.right);

        return 1 + Math.max(leftHeight, rightHeight);
    }

    public static void main(String[] args) {
        TreeNode root = new TreeNode(1);
        root.left = new TreeNode(2);
        root.right = new TreeNode(3);
        root.left.left = new TreeNode(4);
        root.left.right = new TreeNode(5);

        System.out.println("Tree height: " + treeHeight(root));         // 2
        System.out.println("Left subtree: " + treeHeight(root.left));   // 1
        System.out.println("Right subtree: " + treeHeight(root.right)); // 0
        System.out.println("Empty tree: " + treeHeight(null));          // -1
    }
}
```

**Output:**
```
Tree height: 2
Left subtree: 1
Right subtree: 0
Empty tree: -1
```

### Time and Space Complexity

| Metric | Value | Reason |
|---|---|---|
| Time | O(n) | Visit every node once |
| Space | O(h) | Recursion stack depth = tree height |
| Best-case space | O(log n) | Balanced tree |
| Worst-case space | O(n) | Skewed tree (like a linked list) |

---

## 13.6 Counting Nodes

### Count All Nodes

**Python:**

```python
def count_nodes(root):
    """Count total number of nodes in a binary tree."""
    if root is None:
        return 0
    return 1 + count_nodes(root.left) + count_nodes(root.right)


# Using the same tree from above
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

print(f"Total nodes: {count_nodes(root)}")  # 5
```

**Output:**
```
Total nodes: 5
```

**Java:**

```java
public static int countNodes(TreeNode root) {
    if (root == null) {
        return 0;
    }
    return 1 + countNodes(root.left) + countNodes(root.right);
}

// In main:
System.out.println("Total nodes: " + countNodes(root));  // 5
```

**Output:**
```
Total nodes: 5
```

### Count Leaf Nodes

```python
def count_leaves(root):
    """Count the number of leaf nodes."""
    if root is None:
        return 0
    if root.left is None and root.right is None:
        return 1  # This is a leaf
    return count_leaves(root.left) + count_leaves(root.right)


print(f"Leaf nodes: {count_leaves(root)}")  # 3 (nodes 3, 4, 5)
```

**Output:**
```
Leaf nodes: 3
```

### Step-by-Step Walkthrough: count_nodes

```
         1
        / \
       2   3
      / \
     4   5

count_nodes(1)
  = 1 + count_nodes(2) + count_nodes(3)
  = 1 + (1 + count_nodes(4) + count_nodes(5)) + (1 + count_nodes(None) + count_nodes(None))
  = 1 + (1 + (1 + 0 + 0) + (1 + 0 + 0)) + (1 + 0 + 0)
  = 1 + (1 + 1 + 1) + 1
  = 1 + 3 + 1
  = 5
```

**Time**: O(n) -- visit every node. **Space**: O(h) -- recursion depth.

---

## 13.7 Level-Order Traversal (BFS)

Level-order traversal visits nodes **level by level, left to right**. This is also called **Breadth-First Search (BFS)** on a tree.

```
         1          Level 0: [1]
        / \
       2   3        Level 1: [2, 3]
      / \   \
     4   5   6      Level 2: [4, 5, 6]

Level-order output: 1, 2, 3, 4, 5, 6
```

### How It Works: Use a Queue

1. Start by adding the root to a queue.
2. While the queue is not empty:
   a. Remove the front node from the queue.
   b. Process (print) that node.
   c. Add its left child to the queue (if it exists).
   d. Add its right child to the queue (if it exists).

### Step-by-Step Walkthrough

```
Tree:
         1
        / \
       2   3
      / \   \
     4   5   6

Step 1: Queue = [1]
  Dequeue 1, print 1, enqueue children 2, 3
  Queue = [2, 3]

Step 2: Queue = [2, 3]
  Dequeue 2, print 2, enqueue children 4, 5
  Queue = [3, 4, 5]

Step 3: Queue = [3, 4, 5]
  Dequeue 3, print 3, enqueue child 6
  Queue = [4, 5, 6]

Step 4: Queue = [4, 5, 6]
  Dequeue 4, print 4, no children
  Queue = [5, 6]

Step 5: Queue = [5, 6]
  Dequeue 5, print 5, no children
  Queue = [6]

Step 6: Queue = [6]
  Dequeue 6, print 6, no children
  Queue = []

Queue is empty -> Done!
Output: 1, 2, 3, 4, 5, 6
```

### Implementation

**Python:**

```python
from collections import deque


def level_order_traversal(root):
    """Perform level-order (BFS) traversal of a binary tree.

    Returns a list of values in level order.
    """
    if root is None:
        return []

    result = []
    queue = deque([root])

    while queue:
        node = queue.popleft()
        result.append(node.val)

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return result


def level_order_by_level(root):
    """Return values grouped by level.

    Returns a list of lists, where each inner list is one level.
    """
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

print("Level-order:", level_order_traversal(root))
print("By level:", level_order_by_level(root))
```

**Output:**
```
Level-order: [1, 2, 3, 4, 5, 6]
By level: [[1], [2, 3], [4, 5, 6]]
```

**Java:**

```java
import java.util.*;

public class LevelOrderTraversal {

    public static List<Integer> levelOrder(TreeNode root) {
        List<Integer> result = new ArrayList<>();
        if (root == null) return result;

        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);

        while (!queue.isEmpty()) {
            TreeNode node = queue.poll();
            result.add(node.val);

            if (node.left != null) queue.offer(node.left);
            if (node.right != null) queue.offer(node.right);
        }

        return result;
    }

    public static List<List<Integer>> levelOrderByLevel(TreeNode root) {
        List<List<Integer>> result = new ArrayList<>();
        if (root == null) return result;

        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);

        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            List<Integer> currentLevel = new ArrayList<>();

            for (int i = 0; i < levelSize; i++) {
                TreeNode node = queue.poll();
                currentLevel.add(node.val);

                if (node.left != null) queue.offer(node.left);
                if (node.right != null) queue.offer(node.right);
            }

            result.add(currentLevel);
        }

        return result;
    }

    public static void main(String[] args) {
        TreeNode root = new TreeNode(1);
        root.left = new TreeNode(2);
        root.right = new TreeNode(3);
        root.left.left = new TreeNode(4);
        root.left.right = new TreeNode(5);
        root.right.right = new TreeNode(6);

        System.out.println("Level-order: " + levelOrder(root));
        System.out.println("By level: " + levelOrderByLevel(root));
    }
}
```

**Output:**
```
Level-order: [1, 2, 3, 4, 5, 6]
By level: [[1], [2, 3], [4, 5, 6]]
```

### Time and Space Complexity

| Metric | Value | Reason |
|---|---|---|
| Time | O(n) | Visit every node exactly once |
| Space | O(w) | Queue holds at most one level; w = max width |
| Worst-case space | O(n/2) = O(n) | Bottom level of a perfect tree has ~n/2 nodes |

---

## 13.8 Building a Tree from a List (Utility)

For testing, it is convenient to build a tree from a list where `None` represents missing nodes (level-order format, same as LeetCode):

**Python:**

```python
from collections import deque


def build_tree(values):
    """Build a binary tree from a level-order list.

    None values represent missing nodes.
    Example: [1, 2, 3, None, 5] builds:
         1
        / \
       2   3
        \
         5
    """
    if not values or values[0] is None:
        return None

    root = TreeNode(values[0])
    queue = deque([root])
    i = 1

    while queue and i < len(values):
        node = queue.popleft()

        # Left child
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1

        # Right child
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1

    return root


# Test it
root = build_tree([1, 2, 3, 4, 5, None, 6])
print("Level-order:", level_order_traversal(root))
print("Height:", tree_height(root))
print("Node count:", count_nodes(root))
```

**Output:**
```
Level-order: [1, 2, 3, 4, 5, 6]
Height: 2
Node count: 6
```

---

## Common Mistakes

1. **Confusing height and depth.** Height measures downward from a node to its deepest leaf. Depth measures upward from the root to that node. They go in opposite directions.

2. **Forgetting the base case.** When writing recursive tree functions, always handle `root is None` first. Every recursive function on a tree needs this check or you will get a null pointer error.

3. **Confusing "complete" and "full."** A full binary tree requires every node to have 0 or 2 children. A complete binary tree requires all levels to be filled except possibly the last, which must be left-filled. They are different properties.

4. **Assuming binary trees are always balanced.** A binary tree can be completely skewed to one side, looking like a linked list. Never assume O(log n) height unless the problem guarantees a balanced tree.

5. **Using a stack instead of a queue for BFS.** Level-order traversal requires a queue (FIFO). Using a stack gives you a depth-first traversal instead. The data structure you choose determines the traversal order.

---

## Best Practices

1. **Always handle the empty tree case.** Check for `None`/`null` root at the start of every tree function. This prevents crashes and handles edge cases cleanly.

2. **Use the `build_tree` utility for testing.** Building trees node by node is tedious. A level-order list builder saves time and makes tests readable.

3. **Think recursively.** Most tree problems follow this pattern: handle the base case, process the current node, and recurse on left and right subtrees. Trust the recursion -- do not try to trace through every call mentally.

4. **Know when to use BFS vs. recursion.** Level-order problems (level averages, right-side view, zigzag traversal) call for BFS with a queue. Depth-related problems (height, path sum, subtree checks) call for recursion.

5. **Draw the tree.** Whenever you are stuck on a tree problem, draw the tree on paper. Trace through your algorithm node by node. Visualization is your most powerful debugging tool.

---

## Quick Summary

| Concept | Key Point |
|---|---|
| Tree | Hierarchical structure: one root, each node has one parent |
| Binary tree | Each node has at most 2 children (left and right) |
| Height | Longest path from node down to a leaf |
| Depth | Distance from root down to a node |
| Full | Every node has 0 or 2 children |
| Complete | All levels full except last (left-filled) |
| Perfect | Full + all leaves at same level |
| Balanced | Height difference <= 1 at every node |
| Level-order | BFS traversal using a queue |
| Height calculation | O(n) time, O(h) space |
| Node counting | O(n) time, O(h) space |

---

## Key Points

- A tree with `n` nodes has exactly `n - 1` edges.
- The height of a balanced binary tree is O(log n), which is why balanced trees enable efficient operations.
- Level-order traversal uses a **queue** and processes nodes level by level. It is O(n) time and O(n) space in the worst case.
- Perfect implies complete implies balanced, but not the reverse.
- Every recursive tree function needs a base case for `None`/`null`.
- Trees are the foundation for BSTs, heaps, tries, and many advanced data structures.

---

## Practice Questions

1. **Draw and classify**: Given the tree `[1, 2, 3, 4, 5, 6, 7]` (level-order), draw it. Is it full? Complete? Perfect? Balanced?

2. **Height calculation**: What is the height of a tree with nodes `[1, 2, 3, None, None, 4, 5, None, None, None, None, 6]`? Trace through the recursive calls.

3. **Node counting**: A perfect binary tree has height 4. How many total nodes does it have? How many leaves?

4. **BFS trace**: Given the tree `[10, 5, 15, 3, 7, None, 20]`, trace through level-order traversal step by step, showing the queue state at each step.

5. **True or false**: Every complete binary tree is also a full binary tree. Explain with a counterexample if false.

---

## LeetCode-Style Problems

### Problem 1: Maximum Depth of Binary Tree (LeetCode 104)

**Problem**: Given the root of a binary tree, return its maximum depth. The maximum depth is the number of **nodes** along the longest path from the root down to the farthest leaf.

> Note: LeetCode defines depth as node count, not edge count. A single node has depth 1.

```
Input:
         3
        / \
       9  20
          / \
         15  7

Output: 3
```

**Solution:**

```python
def max_depth(root):
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


root = build_tree([3, 9, 20, None, None, 15, 7])
print(max_depth(root))  # 3
```

```java
public int maxDepth(TreeNode root) {
    if (root == null) return 0;
    return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
}
```

**Complexity**: O(n) time, O(h) space.

---

### Problem 2: Invert Binary Tree (LeetCode 226)

**Problem**: Given the root of a binary tree, invert the tree (mirror it) and return its root.

```
Input:          Output:
     4               4
    / \             / \
   2   7           7   2
  / \ / \         / \ / \
 1  3 6  9       9  6 3  1
```

**Solution:**

```python
def invert_tree(root):
    if root is None:
        return None

    # Swap left and right children
    root.left, root.right = root.right, root.left

    # Recursively invert subtrees
    invert_tree(root.left)
    invert_tree(root.right)

    return root


root = build_tree([4, 2, 7, 1, 3, 6, 9])
print("Before:", level_order_traversal(root))
invert_tree(root)
print("After:", level_order_traversal(root))
```

**Output:**
```
Before: [4, 2, 7, 1, 3, 6, 9]
After: [4, 7, 2, 9, 6, 3, 1]
```

```java
public TreeNode invertTree(TreeNode root) {
    if (root == null) return null;

    TreeNode temp = root.left;
    root.left = root.right;
    root.right = temp;

    invertTree(root.left);
    invertTree(root.right);

    return root;
}
```

**Complexity**: O(n) time, O(h) space.

---

### Problem 3: Same Tree (LeetCode 100)

**Problem**: Given the roots of two binary trees, check if they are the same. Two trees are the same if they have the same structure and node values.

**Solution:**

```python
def is_same_tree(p, q):
    # Both empty
    if p is None and q is None:
        return True

    # One empty, one not
    if p is None or q is None:
        return False

    # Both non-empty: check value and recurse
    return (p.val == q.val and
            is_same_tree(p.left, q.left) and
            is_same_tree(p.right, q.right))


tree1 = build_tree([1, 2, 3])
tree2 = build_tree([1, 2, 3])
tree3 = build_tree([1, 2, 4])

print(is_same_tree(tree1, tree2))  # True
print(is_same_tree(tree1, tree3))  # False
```

**Output:**
```
True
False
```

```java
public boolean isSameTree(TreeNode p, TreeNode q) {
    if (p == null && q == null) return true;
    if (p == null || q == null) return false;
    return p.val == q.val
        && isSameTree(p.left, q.left)
        && isSameTree(p.right, q.right);
}
```

**Complexity**: O(n) time, O(h) space.

---

### Problem 4: Count Complete Tree Nodes (LeetCode 222)

**Problem**: Given the root of a complete binary tree, count the number of nodes. Do it faster than O(n).

**Insight**: In a complete binary tree, if the left and right subtree heights are equal, the left subtree is a perfect tree and we can calculate its size with `2^h - 1`.

```python
def count_complete_tree_nodes(root):
    if root is None:
        return 0

    left_height = get_left_height(root)
    right_height = get_right_height(root)

    if left_height == right_height:
        # Perfect tree: 2^h - 1 nodes
        return (1 << left_height) - 1
    else:
        # Not perfect: count recursively
        return 1 + count_complete_tree_nodes(root.left) + count_complete_tree_nodes(root.right)


def get_left_height(node):
    height = 0
    while node:
        height += 1
        node = node.left
    return height


def get_right_height(node):
    height = 0
    while node:
        height += 1
        node = node.right
    return height


root = build_tree([1, 2, 3, 4, 5, 6])
print(f"Node count: {count_complete_tree_nodes(root)}")  # 6
```

**Output:**
```
Node count: 6
```

**Complexity**: O(log^2 n) time -- much better than O(n) for large complete trees.

---

### Problem 5: Minimum Depth of Binary Tree (LeetCode 111)

**Problem**: Given a binary tree, find its minimum depth. The minimum depth is the number of nodes along the shortest path from the root to the nearest **leaf** node.

**Trap**: A node with only one child is NOT a leaf. You must go all the way down to a leaf.

```python
def min_depth(root):
    if root is None:
        return 0

    # If one child is missing, we must go to the other side
    if root.left is None:
        return 1 + min_depth(root.right)
    if root.right is None:
        return 1 + min_depth(root.left)

    return 1 + min(min_depth(root.left), min_depth(root.right))


# Tree where naive min would give wrong answer:
#      1
#     /
#    2
#   /
#  3
# Minimum depth = 3 (not 1!)
root = build_tree([1, 2, None, 3])
print(f"Min depth: {min_depth(root)}")  # 3

# Balanced tree:
#      1
#     / \
#    2   3
#   /
#  4
root2 = build_tree([1, 2, 3, 4])
print(f"Min depth: {min_depth(root2)}")  # 2
```

**Output:**
```
Min depth: 3
Min depth: 2
```

```java
public int minDepth(TreeNode root) {
    if (root == null) return 0;
    if (root.left == null) return 1 + minDepth(root.right);
    if (root.right == null) return 1 + minDepth(root.left);
    return 1 + Math.min(minDepth(root.left), minDepth(root.right));
}
```

**Complexity**: O(n) time, O(h) space.

---

## What Is Next?

Now that you understand how trees work, it is time to add structure and rules. In Chapter 14, you will learn about **Binary Search Trees (BSTs)**, where the left child is always smaller than the parent and the right child is always larger. This simple rule transforms a tree into a powerful search structure with O(log n) lookups -- as fast as binary search on a sorted array, but with the flexibility to insert and delete efficiently.
