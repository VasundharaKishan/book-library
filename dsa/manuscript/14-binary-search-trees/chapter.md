# Chapter 14: Binary Search Trees -- Ordered Trees for Fast Lookup

## What You Will Learn

- The Binary Search Tree (BST) property and why it enables fast search
- How to search for a value in a BST in O(log n) time
- How to insert a new value while maintaining the BST property
- How to delete a node, handling all three cases: leaf, one child, and two children
- Why in-order traversal of a BST produces sorted output
- The dramatic performance difference between balanced and unbalanced BSTs
- How to solve classic BST problems: validate BST, kth smallest element, lowest common ancestor, and convert sorted array to BST

## Why This Chapter Matters

In Chapter 13 you learned what trees are. Now you will learn the most important variant: the **Binary Search Tree**. A BST combines the flexibility of a linked structure (easy inserts and deletes) with the speed of binary search (O(log n) lookups). This makes BSTs the backbone of many real-world systems.

Databases use BST-like structures (B-trees) to index millions of records. Programming language standard libraries implement sorted maps and sets with balanced BSTs (Java's `TreeMap`, C++'s `std::map`). File systems use them to locate files. If you want to store data that stays sorted and supports fast insertions, deletions, and lookups, BSTs are the answer.

BST problems are also among the most common in technical interviews. The four problems at the end of this chapter appear in almost every interview preparation list.

---

## 14.1 The BST Property

A **Binary Search Tree** is a binary tree where every node satisfies this rule:

> For any node with value `v`:
> - All values in its **left subtree** are **less than** `v`
> - All values in its **right subtree** are **greater than** `v`

```
Valid BST:                  NOT a valid BST:

         8                        8
        / \                      / \
       3   10                   3   10
      / \    \                 / \    \
     1   6   14               1   9   14
        / \                      / \
       4   7                    4   7

Left subtree of 8:            Node 9 is in the LEFT subtree of 8,
all values (1,3,4,6,7) < 8    but 9 > 8. VIOLATION!
Right subtree of 8:
all values (10,14) > 8
```

**Critical detail**: The rule applies to the **entire subtree**, not just the immediate children. Node 4 is not just less than 6; it must also be less than 8 (since it is in 8's left subtree).

---

## 14.2 Searching in a BST

Searching a BST works exactly like binary search on a sorted array:

1. Start at the root.
2. If the target equals the current node, found it.
3. If the target is smaller, go left.
4. If the target is larger, go right.
5. If you reach `None`, the target is not in the tree.

### Step-by-Step Walkthrough: Search for 6

```
         8
        / \
       3   10
      / \    \
     1   6   14
        / \
       4   7

Step 1: Compare 6 with root 8.  6 < 8, go LEFT.
Step 2: Compare 6 with node 3.  6 > 3, go RIGHT.
Step 3: Compare 6 with node 6.  6 == 6, FOUND!

Only 3 comparisons instead of checking all 7 nodes.
```

### Search for 5 (not in tree)

```
Step 1: Compare 5 with 8.  5 < 8, go LEFT.
Step 2: Compare 5 with 3.  5 > 3, go RIGHT.
Step 3: Compare 5 with 6.  5 < 6, go LEFT.
Step 4: Compare 5 with 4.  5 > 4, go RIGHT.
Step 5: Right child of 4 is None. NOT FOUND.
```

### Implementation

**Python:**

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def search_bst(root, target):
    """Search for a value in a BST. Returns the node or None."""
    if root is None:
        return None

    if target == root.val:
        return root
    elif target < root.val:
        return search_bst(root.left, target)
    else:
        return search_bst(root.right, target)


def search_bst_iterative(root, target):
    """Iterative version -- no recursion stack overhead."""
    current = root
    while current is not None:
        if target == current.val:
            return current
        elif target < current.val:
            current = current.left
        else:
            current = current.right
    return None


# Build BST:
#        8
#       / \
#      3   10
#     / \    \
#    1   6   14
root = TreeNode(8)
root.left = TreeNode(3)
root.right = TreeNode(10)
root.left.left = TreeNode(1)
root.left.right = TreeNode(6)
root.right.right = TreeNode(14)

result = search_bst(root, 6)
print(f"Search 6: {result.val if result else 'Not found'}")

result = search_bst(root, 5)
print(f"Search 5: {result.val if result else 'Not found'}")

result = search_bst_iterative(root, 10)
print(f"Search 10: {result.val if result else 'Not found'}")
```

**Output:**
```
Search 6: 6
Search 5: Not found
Search 10: 10
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

public class BSTSearch {

    // Recursive search
    public static TreeNode searchBST(TreeNode root, int target) {
        if (root == null) return null;

        if (target == root.val) return root;
        else if (target < root.val) return searchBST(root.left, target);
        else return searchBST(root.right, target);
    }

    // Iterative search
    public static TreeNode searchBSTIterative(TreeNode root, int target) {
        TreeNode current = root;
        while (current != null) {
            if (target == current.val) return current;
            else if (target < current.val) current = current.left;
            else current = current.right;
        }
        return null;
    }

    public static void main(String[] args) {
        TreeNode root = new TreeNode(8);
        root.left = new TreeNode(3);
        root.right = new TreeNode(10);
        root.left.left = new TreeNode(1);
        root.left.right = new TreeNode(6);
        root.right.right = new TreeNode(14);

        TreeNode result = searchBST(root, 6);
        System.out.println("Search 6: " + (result != null ? result.val : "Not found"));

        result = searchBST(root, 5);
        System.out.println("Search 5: " + (result != null ? result.val : "Not found"));
    }
}
```

**Output:**
```
Search 6: 6
Search 5: Not found
```

### Time Complexity

| Case | Time | When |
|---|---|---|
| Best | O(1) | Target is the root |
| Average | O(log n) | Tree is reasonably balanced |
| Worst | O(n) | Tree is completely skewed (linked list) |

---

## 14.3 Inserting into a BST

To insert a value, search for where it would be. When you reach `None`, that is where the new node goes.

### Step-by-Step Walkthrough: Insert 5

```
         8                      8
        / \                    / \
       3   10       -->       3   10
      / \    \               / \    \
     1   6   14             1   6   14
                               / \
                              4   7

Wait, let's insert 5 into the tree with node 4 and 7:

Step 1: 5 < 8, go left to 3.
Step 2: 5 > 3, go right to 6.
Step 3: 5 < 6, go left to 4.
Step 4: 5 > 4, go right. Right is None -> insert here!

         8
        / \
       3   10
      / \    \
     1   6   14
        / \
       4   7
        \
         5
```

### Implementation

**Python:**

```python
def insert_bst(root, val):
    """Insert a value into a BST. Returns the root."""
    if root is None:
        return TreeNode(val)

    if val < root.val:
        root.left = insert_bst(root.left, val)
    elif val > root.val:
        root.right = insert_bst(root.right, val)
    # If val == root.val, do nothing (no duplicates)

    return root


def inorder(root):
    """In-order traversal returns sorted values."""
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


# Build a BST by inserting values
root = None
for val in [8, 3, 10, 1, 6, 14, 4, 7]:
    root = insert_bst(root, val)

print("In-order (sorted):", inorder(root))

# Insert 5
root = insert_bst(root, 5)
print("After inserting 5:", inorder(root))
```

**Output:**
```
In-order (sorted): [1, 3, 4, 6, 7, 8, 10, 14]
After inserting 5: [1, 3, 4, 5, 6, 7, 8, 10, 14]
```

**Java:**

```java
public static TreeNode insertBST(TreeNode root, int val) {
    if (root == null) return new TreeNode(val);

    if (val < root.val) {
        root.left = insertBST(root.left, val);
    } else if (val > root.val) {
        root.right = insertBST(root.right, val);
    }

    return root;
}

public static List<Integer> inorder(TreeNode root) {
    List<Integer> result = new ArrayList<>();
    inorderHelper(root, result);
    return result;
}

private static void inorderHelper(TreeNode root, List<Integer> result) {
    if (root == null) return;
    inorderHelper(root.left, result);
    result.add(root.val);
    inorderHelper(root.right, result);
}
```

**Time**: O(h) where h is the tree height. O(log n) for balanced, O(n) for skewed.

---

## 14.4 Deleting from a BST

Deletion is the trickiest BST operation because we must maintain the BST property after removing a node. There are **three cases**:

### Case 1: Deleting a Leaf Node

Simply remove it. No children to worry about.

```
Delete 4:
         8                    8
        / \                  / \
       3   10     -->       3   10
      / \    \             / \    \
     1   6   14           1   6   14
        /                     \
       4                       7
        \
         7

Wait -- 7 was a child of 6, not 4. Let me redo:

Delete 1 (a leaf):
         8                    8
        / \                  / \
       3   10     -->       3   10
      / \    \               \    \
     1   6   14              6   14

Simply set parent's pointer to None.
```

### Case 2: Node Has One Child

Replace the node with its only child.

```
Delete 10 (has one child: 14):
         8                    8
        / \                  / \
       3   10     -->       3   14
      / \    \             / \
     1   6   14           1   6

Node 10 is replaced by its child 14.
```

### Case 3: Node Has Two Children

This is the tricky case. We cannot just remove the node because it has two subtrees. The solution:

1. Find the **in-order successor** (smallest node in the right subtree).
2. Copy the successor's value to the node being deleted.
3. Delete the successor from the right subtree (which is Case 1 or 2).

```
Delete 3 (has two children: 1 and 6):

         8                         8
        / \                       / \
       3   10                    4   10
      / \    \                  / \    \
     1   6   14               1   6   14
        / \                        \
       4   7                        7

Step 1: Find in-order successor of 3.
        Go right to 6, then left as far as possible -> 4.
Step 2: Copy 4's value to node 3's position.
Step 3: Delete node 4 from right subtree (it's a leaf, Case 1).
```

**Why the in-order successor?** It is the smallest value larger than the deleted node. Putting it in the deleted node's position preserves the BST property: everything in the left subtree is still smaller, and everything in the right subtree is still larger.

### Implementation

**Python:**

```python
def delete_bst(root, val):
    """Delete a value from a BST. Returns the root."""
    if root is None:
        return None

    # Search for the node to delete
    if val < root.val:
        root.left = delete_bst(root.left, val)
    elif val > root.val:
        root.right = delete_bst(root.right, val)
    else:
        # Found the node to delete

        # Case 1: Leaf node (no children)
        if root.left is None and root.right is None:
            return None

        # Case 2: One child
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left

        # Case 3: Two children
        # Find in-order successor (smallest in right subtree)
        successor = find_min(root.right)
        root.val = successor.val
        # Delete the successor from right subtree
        root.right = delete_bst(root.right, successor.val)

    return root


def find_min(node):
    """Find the node with the smallest value in a BST."""
    current = node
    while current.left is not None:
        current = current.left
    return current


# Build BST
root = None
for val in [8, 3, 10, 1, 6, 14, 4, 7]:
    root = insert_bst(root, val)

print("Before:", inorder(root))

root = delete_bst(root, 3)  # Delete node with two children
print("After deleting 3:", inorder(root))

root = delete_bst(root, 10)  # Delete node with one child
print("After deleting 10:", inorder(root))

root = delete_bst(root, 1)  # Delete leaf
print("After deleting 1:", inorder(root))
```

**Output:**
```
Before: [1, 3, 4, 6, 7, 8, 10, 14]
After deleting 3: [1, 4, 6, 7, 8, 10, 14]
After deleting 10: [1, 4, 6, 7, 8, 14]
After deleting 1: [4, 6, 7, 8, 14]
```

**Java:**

```java
public static TreeNode deleteBST(TreeNode root, int val) {
    if (root == null) return null;

    if (val < root.val) {
        root.left = deleteBST(root.left, val);
    } else if (val > root.val) {
        root.right = deleteBST(root.right, val);
    } else {
        // Case 1 & 2: No left child or no right child
        if (root.left == null) return root.right;
        if (root.right == null) return root.left;

        // Case 3: Two children
        TreeNode successor = findMin(root.right);
        root.val = successor.val;
        root.right = deleteBST(root.right, successor.val);
    }

    return root;
}

private static TreeNode findMin(TreeNode node) {
    while (node.left != null) {
        node = node.left;
    }
    return node;
}
```

### Deletion Complexity

| Operation | Time | Space |
|---|---|---|
| Delete (balanced) | O(log n) | O(log n) |
| Delete (skewed) | O(n) | O(n) |

---

## 14.5 In-Order Traversal Gives Sorted Output

This is one of the most important properties of a BST. When you perform an **in-order traversal** (left, root, right), you visit nodes in **ascending sorted order**.

```
         8
        / \
       3   10
      / \    \
     1   6   14
        / \
       4   7

In-order: 1, 3, 4, 6, 7, 8, 10, 14  (sorted!)
```

**Why?** In-order traversal visits the left subtree first (all smaller values), then the root, then the right subtree (all larger values). This naturally produces ascending order.

This property is incredibly useful:
- **Kth smallest element**: In-order traversal and stop at the kth element
- **Validate BST**: In-order traversal should produce strictly increasing values
- **Convert BST to sorted array**: Just do in-order traversal

---

## 14.6 Balanced vs. Unbalanced BSTs

The performance of a BST depends entirely on its **shape**. The same set of values can produce very different trees depending on insertion order.

### Inserting [4, 2, 6, 1, 3, 5, 7] (balanced):

```
         4           Height = 2
        / \           Search: O(log n)
       2   6
      / \ / \
     1  3 5  7
```

### Inserting [1, 2, 3, 4, 5, 6, 7] (already sorted -- worst case):

```
     1                Height = 6
      \               Search: O(n)
       2              This is just a linked list!
        \
         3
          \
           4
            \
             5
              \
               6
                \
                 7
```

### Performance Comparison

| Operation | Balanced BST | Skewed BST |
|---|---|---|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Height | O(log n) | O(n) |

**This is why balanced BSTs matter.** Self-balancing trees like AVL trees and Red-Black trees automatically maintain O(log n) height after every insert and delete. Java's `TreeMap` and `TreeSet` use Red-Black trees internally.

### Practical Impact

For n = 1,000,000 (one million) nodes:
- **Balanced BST**: ~20 comparisons to search (log2 of 1,000,000)
- **Skewed BST**: up to 1,000,000 comparisons to search

That is a **50,000x difference** in performance.

---

## Common Mistakes

1. **Checking only immediate children for BST validity.** The BST property requires ALL nodes in the left subtree to be smaller, not just the left child. A tree where node 5 has left child 3 and 3 has right child 7 is NOT a valid BST (7 > 5).

2. **Forgetting Case 3 in deletion.** When deleting a node with two children, you must find the in-order successor (or predecessor), copy its value, and then delete the successor. Simply removing the node destroys the tree.

3. **Not handling duplicates consistently.** Decide upfront: do duplicates go left, go right, or get rejected? Most implementations reject duplicates. Be consistent.

4. **Assuming BST is always balanced.** Unless the problem states the tree is balanced, BST operations can be O(n) in the worst case.

5. **Confusing in-order successor with "right child."** The in-order successor is the SMALLEST node in the right subtree, not the right child itself. You must go right once, then left as far as possible.

---

## Best Practices

1. **Use the iterative search for production code.** Iterative search avoids stack overflow on deep trees and has O(1) space complexity.

2. **Consider using self-balancing BSTs in practice.** Raw BSTs degrade to O(n) with sorted input. Use AVL trees, Red-Black trees, or built-in sorted containers like Python's `sortedcontainers` or Java's `TreeMap`.

3. **Use in-order traversal to verify BST correctness.** After any modification, an in-order traversal should produce strictly increasing values.

4. **Draw the tree when debugging.** Deletion bugs are nearly impossible to find by staring at code. Draw the tree before and after each operation.

5. **Think about insertion order.** If you are building a BST from known data, insert values in a way that produces a balanced tree (e.g., insert the median first, then recurse on halves).

---

## Quick Summary

| Operation | Average Case | Worst Case | Notes |
|---|---|---|---|
| Search | O(log n) | O(n) | Like binary search but on a tree |
| Insert | O(log n) | O(n) | Find position then add node |
| Delete | O(log n) | O(n) | Three cases: leaf, one child, two children |
| In-order | O(n) | O(n) | Always visits all nodes; produces sorted output |
| Find min/max | O(log n) | O(n) | Go all the way left/right |

---

## Key Points

- The BST property states: left subtree values < node value < right subtree values.
- In-order traversal of a BST always produces sorted output.
- Deletion with two children uses the in-order successor: go right once, then left as far as possible.
- Performance depends on tree height: O(log n) when balanced, O(n) when skewed.
- Inserting already-sorted data into a BST produces the worst case (a linked list).
- Self-balancing BSTs (AVL, Red-Black) guarantee O(log n) height.

---

## Practice Questions

1. **Insertion order**: Draw the BST resulting from inserting [5, 3, 7, 1, 4, 6, 8] one at a time. Then draw the BST from inserting [1, 2, 3, 4, 5, 6, 7]. Compare the heights.

2. **Deletion trace**: Starting with the BST from question 1 (first sequence), delete 5 (the root). Show each step of finding the successor and restructuring.

3. **Find min and max**: Write a function to find the minimum and maximum values in a BST without traversing all nodes. What is the time complexity?

4. **Predecessor**: The in-order predecessor is the largest value smaller than a given node. How do you find it? (Hint: it mirrors the successor logic.)

5. **True or false**: If you insert n random values into an initially empty BST, the expected height is O(log n). Explain.

---

## LeetCode-Style Problems

### Problem 1: Validate Binary Search Tree (LeetCode 98)

**Problem**: Given the root of a binary tree, determine if it is a valid BST.

**Key Insight**: Each node must fall within a valid range. The range narrows as you go deeper.

```
Valid BST:             Invalid BST:
     5                      5
    / \                    / \
   1   7                  1   7
      / \                    / \
     6   8                  4   8

                         4 < 5, but 4 is in the
                         RIGHT subtree of 5!
```

**Solution:**

```python
def is_valid_bst(root):
    """Validate BST using range checking."""
    def validate(node, min_val, max_val):
        if node is None:
            return True

        if node.val <= min_val or node.val >= max_val:
            return False

        return (validate(node.left, min_val, node.val) and
                validate(node.right, node.val, max_val))

    return validate(root, float('-inf'), float('inf'))


# Alternative: In-order traversal should be strictly increasing
def is_valid_bst_inorder(root):
    """Validate BST using in-order traversal."""
    prev = [float('-inf')]

    def inorder(node):
        if node is None:
            return True

        if not inorder(node.left):
            return False

        if node.val <= prev[0]:
            return False
        prev[0] = node.val

        return inorder(node.right)

    return inorder(root)


# Test
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

valid_tree = build_tree([5, 1, 7, None, None, 6, 8])
invalid_tree = build_tree([5, 1, 7, None, None, 4, 8])

print(f"Valid BST: {is_valid_bst(valid_tree)}")    # True
print(f"Invalid BST: {is_valid_bst(invalid_tree)}")  # False
```

**Output:**
```
Valid BST: True
Invalid BST: False
```

```java
public boolean isValidBST(TreeNode root) {
    return validate(root, Long.MIN_VALUE, Long.MAX_VALUE);
}

private boolean validate(TreeNode node, long min, long max) {
    if (node == null) return true;
    if (node.val <= min || node.val >= max) return false;
    return validate(node.left, min, node.val)
        && validate(node.right, node.val, max);
}
```

**Complexity**: O(n) time, O(h) space.

---

### Problem 2: Kth Smallest Element in a BST (LeetCode 230)

**Problem**: Given the root of a BST and an integer k, return the kth smallest element.

**Key Insight**: In-order traversal visits BST nodes in ascending order. The kth node visited is the answer.

```
         5
        / \
       3   6
      / \
     2   4
    /
   1

k=1 -> 1, k=2 -> 2, k=3 -> 3, k=4 -> 4, k=5 -> 5, k=6 -> 6
```

**Solution:**

```python
def kth_smallest(root, k):
    """Find kth smallest element using in-order traversal."""
    count = [0]
    result = [None]

    def inorder(node):
        if node is None or result[0] is not None:
            return

        inorder(node.left)

        count[0] += 1
        if count[0] == k:
            result[0] = node.val
            return

        inorder(node.right)

    inorder(root)
    return result[0]


# Iterative version (often preferred in interviews)
def kth_smallest_iterative(root, k):
    """Find kth smallest using iterative in-order traversal."""
    stack = []
    current = root

    while current or stack:
        # Go as far left as possible
        while current:
            stack.append(current)
            current = current.left

        current = stack.pop()
        k -= 1
        if k == 0:
            return current.val

        current = current.right

    return -1  # k is larger than tree size


root = build_tree([5, 3, 6, 2, 4, None, None, 1])
print(f"1st smallest: {kth_smallest(root, 1)}")  # 1
print(f"3rd smallest: {kth_smallest(root, 3)}")  # 3
print(f"5th smallest: {kth_smallest(root, 5)}")  # 5
```

**Output:**
```
1st smallest: 1
3rd smallest: 3
5th smallest: 5
```

```java
public int kthSmallest(TreeNode root, int k) {
    Deque<TreeNode> stack = new ArrayDeque<>();
    TreeNode current = root;

    while (current != null || !stack.isEmpty()) {
        while (current != null) {
            stack.push(current);
            current = current.left;
        }
        current = stack.pop();
        k--;
        if (k == 0) return current.val;
        current = current.right;
    }

    return -1;
}
```

**Complexity**: O(h + k) time, O(h) space.

---

### Problem 3: Lowest Common Ancestor of a BST (LeetCode 235)

**Problem**: Given a BST and two nodes p and q, find their lowest common ancestor (LCA). The LCA is the deepest node that is an ancestor of both p and q.

**Key Insight**: In a BST, use the values to decide direction. If both p and q are smaller than the current node, LCA is in the left subtree. If both are larger, LCA is in the right subtree. Otherwise, the current node is the LCA (the paths to p and q diverge here).

```
         6
        / \
       2   8
      / \ / \
     0  4 7  9
       / \
      3   5

LCA(2, 8) = 6  (paths diverge at root)
LCA(2, 4) = 2  (2 is ancestor of 4)
LCA(3, 5) = 4  (paths diverge at 4)
```

**Solution:**

```python
def lowest_common_ancestor(root, p, q):
    """Find LCA in a BST using the BST property."""
    current = root

    while current:
        if p.val < current.val and q.val < current.val:
            # Both in left subtree
            current = current.left
        elif p.val > current.val and q.val > current.val:
            # Both in right subtree
            current = current.right
        else:
            # Paths diverge (or one is the ancestor)
            return current

    return None


root = build_tree([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
p = root.left        # Node 2
q = root.right       # Node 8
lca = lowest_common_ancestor(root, p, q)
print(f"LCA(2, 8) = {lca.val}")  # 6

p = root.left             # Node 2
q = root.left.right       # Node 4
lca = lowest_common_ancestor(root, p, q)
print(f"LCA(2, 4) = {lca.val}")  # 2

p = root.left.right.left   # Node 3
q = root.left.right.right  # Node 5
lca = lowest_common_ancestor(root, p, q)
print(f"LCA(3, 5) = {lca.val}")  # 4
```

**Output:**
```
LCA(2, 8) = 6
LCA(2, 4) = 2
LCA(3, 5) = 4
```

```java
public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
    TreeNode current = root;
    while (current != null) {
        if (p.val < current.val && q.val < current.val) {
            current = current.left;
        } else if (p.val > current.val && q.val > current.val) {
            current = current.right;
        } else {
            return current;
        }
    }
    return null;
}
```

**Complexity**: O(h) time, O(1) space.

---

### Problem 4: Convert Sorted Array to BST (LeetCode 108)

**Problem**: Given a sorted array, convert it to a height-balanced BST.

**Key Insight**: The middle element of the sorted array becomes the root. The left half becomes the left subtree, and the right half becomes the right subtree. Recurse.

```
Input: [-10, -3, 0, 5, 9]

Step 1: Middle = 0 (root)
Step 2: Left half [-10, -3] -> middle = -3 (left child of 0)
        Right half [5, 9] -> middle = 5 (right child of 0)
Step 3: Left of -3: [-10]
        Right of 5: [9]

Result:
         0
        / \
      -3   5
      /     \
    -10      9
```

**Solution:**

```python
def sorted_array_to_bst(nums):
    """Convert a sorted array to a height-balanced BST."""
    if not nums:
        return None

    mid = len(nums) // 2

    root = TreeNode(nums[mid])
    root.left = sorted_array_to_bst(nums[:mid])
    root.right = sorted_array_to_bst(nums[mid + 1:])

    return root


nums = [-10, -3, 0, 5, 9]
root = sorted_array_to_bst(nums)

# Verify: in-order should give back the sorted array
print("In-order:", inorder(root))

# Verify: tree is balanced
def tree_height(node):
    if node is None:
        return -1
    return 1 + max(tree_height(node.left), tree_height(node.right))

print(f"Height: {tree_height(root)}")
print(f"Root: {root.val}")
```

**Output:**
```
In-order: [-10, -3, 0, 5, 9]
Height: 2
Root: 0
```

```java
public TreeNode sortedArrayToBST(int[] nums) {
    return buildBST(nums, 0, nums.length - 1);
}

private TreeNode buildBST(int[] nums, int left, int right) {
    if (left > right) return null;

    int mid = left + (right - left) / 2;
    TreeNode root = new TreeNode(nums[mid]);
    root.left = buildBST(nums, left, mid - 1);
    root.right = buildBST(nums, mid + 1, right);

    return root;
}
```

**Complexity**: O(n) time, O(log n) space (recursion depth for balanced tree).

---

### Problem 5: Delete Node in a BST (LeetCode 450)

**Problem**: Given a root node of a BST and a key, delete the node with the given key. Return the root of the (possibly modified) BST.

This is the deletion algorithm from Section 14.4, packaged as a complete solution:

```python
def delete_node(root, key):
    """Delete node with given key from BST."""
    if root is None:
        return None

    if key < root.val:
        root.left = delete_node(root.left, key)
    elif key > root.val:
        root.right = delete_node(root.right, key)
    else:
        # Node found
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left

        # Two children: replace with in-order successor
        successor = root.right
        while successor.left:
            successor = successor.left

        root.val = successor.val
        root.right = delete_node(root.right, successor.val)

    return root


root = build_tree([5, 3, 6, 2, 4, None, 7])
print("Before:", inorder(root))
root = delete_node(root, 3)
print("After deleting 3:", inorder(root))
root = delete_node(root, 5)
print("After deleting 5:", inorder(root))
```

**Output:**
```
Before: [2, 3, 4, 5, 6, 7]
After deleting 3: [2, 4, 5, 6, 7]
After deleting 5: [2, 4, 6, 7]
```

**Complexity**: O(h) time, O(h) space.

---

## What Is Next?

You now know how to search, insert, and delete in BSTs. But we only touched on in-order traversal. In Chapter 15, you will master all four tree traversal methods -- **in-order, pre-order, post-order, and level-order** -- both recursively and iteratively. You will learn when to use each one and solve problems that require choosing the right traversal strategy.
