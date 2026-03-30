# Chapter 27: Union-Find (Disjoint Set Union)

## What You Will Learn

- What Union-Find is and what problems it solves
- How to implement Find with path compression
- How to implement Union by rank (and by size)
- How path compression flattens trees for near-constant-time operations
- The inverse Ackermann function and why Union-Find is "almost O(1)"
- How to solve classic problems: connected components, redundant connection, accounts merge, and longest consecutive sequence

## Why This Chapter Matters

Imagine you are managing a social network. You need to answer two types of questions constantly:

1. "Are Alice and Bob in the same friend group?" (Find)
2. "Alice just became friends with Bob --- merge their groups." (Union)

You could use BFS/DFS on a graph, but that takes O(n) per query. With Union-Find, both operations run in nearly O(1) amortized time. That is the magic of this data structure.

Union-Find appears in network connectivity, Kruskal's minimum spanning tree algorithm, image processing (connected pixel regions), and numerous interview problems. It is surprisingly simple to implement yet incredibly powerful.

---

## 27.1 What Is Union-Find?

Union-Find (also called Disjoint Set Union or DSU) manages a collection of non-overlapping sets. It supports two operations:

- **Find(x):** Which set does element x belong to? Returns the "representative" (root) of x's set.
- **Union(x, y):** Merge the sets containing x and y into one set.

### The Mental Model

Think of each set as a tree. The root of the tree is the representative of the set. Every element points to its parent, and following parent pointers leads to the root.

```
Initial state: each element is its own set
  0   1   2   3   4   5   6   7

After Union(0, 1):
  0       2   3   4   5   6   7
  |
  1

After Union(2, 3):
  0       2       4   5   6   7
  |       |
  1       3

After Union(0, 2):  (merge the two trees)
      0           4   5   6   7
     / \
    1   2
        |
        3

Find(3) = follow 3 -> 2 -> 0.  Root is 0.
Find(1) = follow 1 -> 0.       Root is 0.
Same root, so 1 and 3 are in the same set!
```

---

## 27.2 Basic Implementation (No Optimization)

```python
class UnionFindBasic:
    def __init__(self, n):
        # Each element is its own parent (its own set)
        self.parent = list(range(n))

    def find(self, x):
        """Find the root of x's set."""
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, x, y):
        """Merge the sets containing x and y."""
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            self.parent[root_x] = root_y  # attach x's tree under y's root

    def connected(self, x, y):
        """Check if x and y are in the same set."""
        return self.find(x) == self.find(y)


# Test
uf = UnionFindBasic(5)
uf.union(0, 1)
uf.union(2, 3)
print(uf.connected(0, 1))  # True
print(uf.connected(0, 2))  # False
uf.union(1, 3)
print(uf.connected(0, 2))  # True (0-1-3-2 are all connected)
```

**Problem:** Without optimization, the tree can become a long chain, making Find O(n) in the worst case.

```
Worst case (chain):
  0 -> 1 -> 2 -> 3 -> 4 -> 5

  Find(0) takes 5 steps!
```

---

## 27.3 Optimization 1: Path Compression

**Idea:** When we call Find(x), we walk up to the root. On the way back, we make every node point directly to the root. Next time, Find is O(1) for all those nodes.

```
Before path compression:          After Find(0) with compression:

      5                                    5
      |                                 / | | \
      4                                0  1  2  4
      |
      3
      |
      2
      |
      1
      |
      0

Find(0): walk 0->1->2->3->4->5 (root)
Then set parent of 0, 1, 2, 3, 4 all to 5.
```

```python
def find(self, x):
    """Find with path compression."""
    if self.parent[x] != x:
        self.parent[x] = self.find(self.parent[x])  # compress
    return self.parent[x]
```

The iterative version:

```python
def find(self, x):
    """Find with path compression (iterative)."""
    root = x
    while self.parent[root] != root:
        root = self.parent[root]

    # Compress: point everything on the path to root
    while self.parent[x] != root:
        next_parent = self.parent[x]
        self.parent[x] = root
        x = next_parent

    return root
```

---

## 27.4 Optimization 2: Union by Rank

**Idea:** When merging two trees, attach the shorter tree under the taller tree. This keeps trees balanced.

```
Union by rank:

  Tree A (rank 2):       Tree B (rank 1):
       0                      3
      / \                     |
     1   2                    4

  Attach B under A (since rank A >= rank B):

       0
      /|\
     1  2  3
           |
           4

  If we attached A under B instead:

       3
       |
       4
       |
       0       <-- tree gets taller unnecessarily
      / \
     1   2
```

**Rank** is an upper bound on the tree height. It only increases when two trees of equal rank are merged.

---

## 27.5 Complete Optimized Implementation

### Python

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # number of distinct sets

    def find(self, x):
        """Find root with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """Union by rank. Returns False if already connected."""
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # already in same set

        # Attach smaller tree under larger tree
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        self.count -= 1
        return True

    def connected(self, x, y):
        """Check if x and y are in the same set."""
        return self.find(x) == self.find(y)

    def get_count(self):
        """Return number of distinct sets."""
        return self.count


# Test
uf = UnionFind(7)
print(f"Sets: {uf.get_count()}")  # 7

uf.union(0, 1)
uf.union(2, 3)
uf.union(4, 5)
print(f"Sets: {uf.get_count()}")  # 4

uf.union(1, 3)
print(f"Sets: {uf.get_count()}")  # 3

print(uf.connected(0, 3))  # True
print(uf.connected(0, 4))  # False

uf.union(3, 5)
print(f"Sets: {uf.get_count()}")  # 2
print(uf.connected(0, 4))  # True (0-1-2-3-4-5 all connected)
```

### Java

```java
public class UnionFind {
    private int[] parent;
    private int[] rank;
    private int count;

    public UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        count = n;
        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }
    }

    public int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]); // path compression
        }
        return parent[x];
    }

    public boolean union(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);

        if (rootX == rootY) return false;

        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
        } else if (rank[rootX] > rank[rootY]) {
            parent[rootY] = rootX;
        } else {
            parent[rootY] = rootX;
            rank[rootX]++;
        }

        count--;
        return true;
    }

    public boolean connected(int x, int y) {
        return find(x) == find(y);
    }

    public int getCount() {
        return count;
    }

    public static void main(String[] args) {
        UnionFind uf = new UnionFind(7);
        System.out.println("Sets: " + uf.getCount()); // 7

        uf.union(0, 1);
        uf.union(2, 3);
        uf.union(4, 5);
        System.out.println("Sets: " + uf.getCount()); // 4

        uf.union(1, 3);
        System.out.println("Sets: " + uf.getCount()); // 3

        System.out.println(uf.connected(0, 3)); // true
        System.out.println(uf.connected(0, 4)); // false
    }
}
```

---

## 27.6 Visualizing Path Compression

Let us trace Find(0) step by step on a tall tree.

```
Initial tree:

        6
        |
        5
        |
        4
        |
        3
        |
        2
        |
        1
        |
        0

Call find(0):
  0's parent is 1
    1's parent is 2
      2's parent is 3
        3's parent is 4
          4's parent is 5
            5's parent is 6
              6's parent is 6 (root!)

  Now unwind recursion, setting each parent to 6:

After compression:

           6
       / / | \ \ \
      0 1  2  3  4  5

All nodes now point directly to root 6.
Next find(0) is O(1)!
Next find(3) is O(1)!
```

---

## 27.7 Time Complexity: The Inverse Ackermann Function

With both path compression and union by rank, any sequence of m operations on n elements takes O(m * alpha(n)) time, where alpha is the inverse Ackermann function.

**What is alpha(n)?** It grows incredibly slowly:
- alpha(1) = 0
- alpha(2) = 1
- alpha(2^65536) = 4
- For any practical value of n, alpha(n) <= 4

This means Union-Find operations are **effectively O(1)** amortized. You will never encounter an input large enough for alpha(n) to reach 5.

```
+-------------------+------------------+
| n                 | alpha(n)         |
+-------------------+------------------+
| 1                 | 0                |
| 2-3               | 1                |
| 4-7               | 2                |
| 8 - 2047          | 3                |
| 2048 - 2^65536    | 4                |
| > 2^65536         | 5 (never needed) |
+-------------------+------------------+
```

---

## 27.8 Union by Size (Alternative to Rank)

Instead of tracking tree height (rank), you can track tree size. Attach the smaller set under the larger set.

```python
class UnionFindBySize:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        # Attach smaller tree under larger tree
        if self.size[root_x] < self.size[root_y]:
            self.parent[root_x] = root_y
            self.size[root_y] += self.size[root_x]
        else:
            self.parent[root_y] = root_x
            self.size[root_x] += self.size[root_y]

        return True

    def get_size(self, x):
        """Return the size of x's set."""
        return self.size[self.find(x)]


# Test
uf = UnionFindBySize(5)
uf.union(0, 1)
uf.union(2, 3)
uf.union(0, 2)
print(uf.get_size(3))  # 4 (set {0,1,2,3})
print(uf.get_size(4))  # 1 (set {4})
```

**Advantage of union by size:** You can query the size of any set in O(1), which some problems require.

---

## Common Mistakes

1. **Forgetting path compression.** Without it, Find degrades to O(n). Always include the one line: `self.parent[x] = self.find(self.parent[x])`.

2. **Union without finding roots first.** You must call `find(x)` and `find(y)` before comparing or linking. Linking x directly to y (instead of their roots) corrupts the structure.

3. **Not checking if already connected.** `union(x, y)` when x and y are already in the same set should be a no-op. Forgetting this check can cause incorrect component counts.

4. **Index mapping errors.** When elements are not 0-indexed integers (like strings or coordinates), you need a mapping from element to integer index. Use a dictionary.

5. **Stack overflow with recursive find.** For very deep trees before compression, the recursive `find` can overflow the stack. Use the iterative version for safety.

---

## Best Practices

- **Always use both optimizations** (path compression + union by rank/size). Each alone gives O(log n), but together they give O(alpha(n)).
- **Track component count.** Many problems ask "how many groups?" Add a counter that decrements on each successful union.
- **Return boolean from union.** Returning whether a union actually merged two different sets is useful for detecting redundant edges.
- **Use a dictionary parent map** when elements are not contiguous integers (strings, coordinates, large sparse IDs).
- **Prefer iterative find** in production code to avoid stack overflow on deep trees.

---

## 27.9 Problem Solutions

### Problem 1: Number of Connected Components

**Problem:** Given n nodes (0 to n-1) and a list of edges, find the number of connected components.

```python
def count_components(n, edges):
    uf = UnionFind(n)

    for u, v in edges:
        uf.union(u, v)

    return uf.get_count()


# Test
print(count_components(5, [[0,1],[1,2],[3,4]]))
# Output: 2  (components: {0,1,2} and {3,4})

print(count_components(5, [[0,1],[1,2],[2,3],[3,4]]))
# Output: 1  (all connected)
```

```java
public static int countComponents(int n, int[][] edges) {
    UnionFind uf = new UnionFind(n);

    for (int[] edge : edges) {
        uf.union(edge[0], edge[1]);
    }

    return uf.getCount();
}
```

**Complexity:** Time O(n + e * alpha(n)) where e = number of edges. Space O(n).

---

### Problem 2: Redundant Connection

**Problem:** Given a tree with one extra edge (creating exactly one cycle), find the edge that can be removed to restore the tree.

**Key Insight:** Process edges one by one. The first edge that connects two already-connected nodes is the redundant edge.

```python
def find_redundant_connection(edges):
    n = len(edges)
    uf = UnionFind(n + 1)  # 1-indexed

    for u, v in edges:
        if not uf.union(u, v):
            return [u, v]  # already connected = redundant

    return []


# Test
print(find_redundant_connection([[1,2],[1,3],[2,3]]))
# Output: [2, 3]

print(find_redundant_connection([[1,2],[2,3],[3,4],[1,4],[1,5]]))
# Output: [1, 4]
```

```
Graph with redundant edge [2,3]:

  1 --- 2
  |   /
  | /
  3

  Processing edges:
  [1,2]: union(1,2) -> merged
  [1,3]: union(1,3) -> merged
  [2,3]: union(2,3) -> already connected! REDUNDANT
```

**Complexity:** Time O(n * alpha(n)). Space O(n).

---

### Problem 3: Accounts Merge

**Problem:** Given a list of accounts where each account has a name and emails, merge accounts that share at least one common email.

```python
def accounts_merge(accounts):
    # Map each email to an index
    email_to_id = {}
    email_to_name = {}
    idx = 0

    for account in accounts:
        name = account[0]
        for email in account[1:]:
            if email not in email_to_id:
                email_to_id[email] = idx
                idx += 1
            email_to_name[email] = name

    # Union all emails in the same account
    uf = UnionFind(idx)
    for account in accounts:
        first_email_id = email_to_id[account[1]]
        for email in account[2:]:
            uf.union(first_email_id, email_to_id[email])

    # Group emails by their root
    from collections import defaultdict
    groups = defaultdict(list)
    for email, eid in email_to_id.items():
        root = uf.find(eid)
        groups[root].append(email)

    # Build result
    result = []
    for root, emails in groups.items():
        emails.sort()
        name = email_to_name[emails[0]]
        result.append([name] + emails)

    return result


# Test
accounts = [
    ["John", "john1@mail.com", "john_common@mail.com"],
    ["John", "john2@mail.com"],
    ["John", "john_common@mail.com", "john3@mail.com"],
    ["Mary", "mary@mail.com"]
]

for account in accounts_merge(accounts):
    print(account)
# Output:
# ['John', 'john1@mail.com', 'john3@mail.com', 'john_common@mail.com']
# ['John', 'john2@mail.com']
# ['Mary', 'mary@mail.com']
```

**Why Union-Find?** Accounts share emails transitively. If account A shares an email with B, and B shares one with C, all three should merge. Union-Find handles transitive connections naturally.

**Complexity:** Time O(n * alpha(n) + n log n) for sorting. Space O(n).

---

### Problem 4: Longest Consecutive Sequence

**Problem:** Given an unsorted array, find the length of the longest consecutive sequence (e.g., [100, 4, 200, 1, 3, 2] has sequence [1, 2, 3, 4], length 4). Must run in O(n).

```python
def longest_consecutive(nums):
    if not nums:
        return 0

    num_set = set(nums)
    val_to_id = {}
    idx = 0
    for num in num_set:
        val_to_id[num] = idx
        idx += 1

    uf = UnionFindBySize(len(num_set))

    for num in num_set:
        if num + 1 in val_to_id:
            uf.union(val_to_id[num], val_to_id[num + 1])

    return max(uf.get_size(i) for i in range(len(num_set)))


# Test
print(longest_consecutive([100, 4, 200, 1, 3, 2]))
# Output: 4

print(longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]))
# Output: 9
```

**Alternative (Hash Set approach --- simpler for this problem):**

```python
def longest_consecutive_hashset(nums):
    num_set = set(nums)
    longest = 0

    for num in num_set:
        # Only start counting from the beginning of a sequence
        if num - 1 not in num_set:
            current = num
            length = 1
            while current + 1 in num_set:
                current += 1
                length += 1
            longest = max(longest, length)

    return longest

print(longest_consecutive_hashset([100, 4, 200, 1, 3, 2]))
# Output: 4
```

**Complexity:** Both approaches O(n) time, O(n) space.

---

## Quick Summary

| Operation | Without Optimization | With Path Compression Only | With Both Optimizations |
|-----------|---------------------|---------------------------|------------------------|
| Find | O(n) worst | O(log n) amortized | O(alpha(n)) amortized |
| Union | O(n) worst | O(log n) amortized | O(alpha(n)) amortized |

Union-Find is a data structure for managing disjoint sets. With path compression and union by rank, it achieves nearly O(1) amortized time per operation. It excels at connectivity queries and dynamic graph problems where you need to merge groups and check membership.

---

## Key Points

- Union-Find manages groups (disjoint sets) with two operations: Find (which group?) and Union (merge groups).
- Path compression flattens trees by pointing every visited node directly to the root.
- Union by rank/size keeps trees balanced by attaching shorter/smaller trees under taller/larger ones.
- Combined, these optimizations give O(alpha(n)) amortized time --- effectively O(1).
- Union-Find is ideal for connectivity, redundant edge detection, and grouping problems.

---

## Practice Questions

1. What happens if you use path compression but not union by rank? What is the time complexity?

2. Explain why path compression does not break the structure of the disjoint set. Can elements end up in the wrong group?

3. How would you implement Union-Find for string elements (like email addresses) instead of integers?

4. In the Redundant Connection problem, why does the first edge that fails to union give us the answer?

5. Compare Union-Find with BFS/DFS for connectivity queries. When would you choose each?

---

## LeetCode-Style Problems

### Problem 1: Number of Provinces --- LeetCode 547 (Medium)

**Problem:** Given an n x n adjacency matrix where `isConnected[i][j] = 1` means city i and j are directly connected, find the number of provinces (groups of connected cities).

```python
def find_circle_num(is_connected):
    n = len(is_connected)
    uf = UnionFind(n)

    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j] == 1:
                uf.union(i, j)

    return uf.get_count()

# Test
print(find_circle_num([[1,1,0],[1,1,0],[0,0,1]]))
# Output: 2

print(find_circle_num([[1,0,0],[0,1,0],[0,0,1]]))
# Output: 3
```

**Complexity:** Time O(n^2 * alpha(n)), Space O(n)

---

### Problem 2: Graph Valid Tree --- LeetCode 261 (Medium)

**Problem:** Given n nodes and a list of edges, determine if these edges form a valid tree (connected, no cycles).

```python
def valid_tree(n, edges):
    if len(edges) != n - 1:
        return False  # a tree with n nodes has exactly n-1 edges

    uf = UnionFind(n)
    for u, v in edges:
        if not uf.union(u, v):
            return False  # cycle detected

    return True

# Test
print(valid_tree(5, [[0,1],[0,2],[0,3],[1,4]]))  # True
print(valid_tree(5, [[0,1],[1,2],[2,3],[1,3],[1,4]]))  # False
```

**Complexity:** Time O(n * alpha(n)), Space O(n)

---

### Problem 3: Earliest Time When Everyone Becomes Friends --- LeetCode 1101 (Medium)

**Problem:** Given n people and timestamped friendships, find the earliest time when all people are in the same friend group.

```python
def earliest_acq(logs, n):
    logs.sort()  # sort by timestamp
    uf = UnionFind(n)

    for timestamp, x, y in logs:
        uf.union(x, y)
        if uf.get_count() == 1:
            return timestamp

    return -1

# Test
logs = [
    [20190101, 0, 1],
    [20190104, 3, 4],
    [20190107, 2, 3],
    [20190211, 1, 5],
    [20190224, 2, 4],
    [20190301, 0, 3],
    [20190312, 1, 2],
    [20190322, 4, 5]
]
print(earliest_acq(logs, 6))
# Output: 20190301
```

**Complexity:** Time O(e log e + e * alpha(n)), Space O(n)

---

## What Is Next?

You have learned Union-Find --- a deceptively simple data structure that solves connectivity and grouping problems in near-constant time. Two arrays, two optimizations, and you can manage millions of elements efficiently.

In the next chapter, we explore **Bit Manipulation** --- the art of working directly with the binary representation of numbers. You will learn tricks that replace complex operations with single CPU instructions, solving problems in ways that feel like magic.
