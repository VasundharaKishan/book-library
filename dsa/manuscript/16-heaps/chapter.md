# Chapter 16: Heaps -- Priority Queues for Fast Min/Max Access

## What You Will Learn

- What a heap is and how it relates to priority queues
- The difference between min-heaps and max-heaps
- How to store a complete binary tree in an array using index formulas
- How heapify-up and heapify-down operations maintain the heap property
- Insert and extract operations with O(log n) complexity
- Why building a heap from an array is O(n), not O(n log n)
- How to use Python's `heapq` module and Java's `PriorityQueue`
- How heap sort works
- How to solve classic problems: kth largest element, merge K sorted lists, top K frequent elements, and find median from data stream

## Why This Chapter Matters

Imagine you are running a hospital emergency room. Patients arrive at random times with varying urgency levels. You cannot serve them first-come-first-served -- a patient having a heart attack must be seen before someone with a sprained ankle, even if the ankle patient arrived first. You need a system that always gives you the highest-priority patient instantly.

This is exactly what a **priority queue** does, and a **heap** is the most efficient way to implement one.

Heaps appear everywhere in computer science:
- **Operating systems** use heaps to schedule processes by priority
- **Dijkstra's shortest path algorithm** uses a min-heap to pick the next closest vertex
- **Median finding** uses two heaps to maintain a running median
- **Merge K sorted lists** uses a min-heap to efficiently combine ordered data
- **Task schedulers** use heaps to manage job priorities

If you understand heaps, you unlock an entire class of problems that would otherwise require sorting or scanning the entire dataset repeatedly.

---

## 16.1 What Is a Heap?

A **heap** is a **complete binary tree** that satisfies the **heap property**:

- **Min-heap**: Every parent is **less than or equal to** its children. The minimum element is at the root.
- **Max-heap**: Every parent is **greater than or equal to** its children. The maximum element is at the root.

### Min-Heap Example

```
           1           Parent <= Children (everywhere)
          / \
         3   5         1 <= 3, 1 <= 5
        / \ / \
       7  8 9  10      3 <= 7, 3 <= 8, 5 <= 9, 5 <= 10

Root (1) is the MINIMUM of the entire heap.
```

### Max-Heap Example

```
          10           Parent >= Children (everywhere)
         /  \
        8    9         10 >= 8, 10 >= 9
       / \  / \
      3  7 5   1       8 >= 3, 8 >= 7, 9 >= 5, 9 >= 1

Root (10) is the MAXIMUM of the entire heap.
```

### Heap vs. BST

| Feature | Heap | BST |
|---|---|---|
| Property | Parent >= children (max) or parent <= children (min) | Left < parent < right |
| Find min/max | O(1) -- always at root | O(log n) -- go all the way left/right |
| Search | O(n) -- no ordering between siblings | O(log n) -- ordered |
| Insert | O(log n) | O(log n) for balanced |
| Shape | Always a complete binary tree | Can be any shape |
| Primary use | Priority queue, top-K problems | Sorted data, range queries |

A heap is NOT a BST. In a min-heap, the left child can be larger than the right child. The only guarantee is that the parent is smaller than both children.

---

## 16.2 Array Representation

The most elegant property of heaps is that they can be stored in a simple array with no pointers needed. Since a heap is always a complete binary tree, there are no gaps.

### Index Formulas (0-based indexing)

For a node at index `i`:
- **Parent**: `(i - 1) // 2`
- **Left child**: `2 * i + 1`
- **Right child**: `2 * i + 2`

```
Tree view:               Array view:

           1              Index:  0  1  2  3  4  5  6
          / \              Value: [1, 3, 5, 7, 8, 9, 10]
         3   5
        / \ / \
       7  8 9  10

Node 1 (index 0): left = 2*0+1 = 1 (value 3), right = 2*0+2 = 2 (value 5)
Node 3 (index 1): parent = (1-1)//2 = 0 (value 1)
Node 5 (index 2): left = 2*2+1 = 5 (value 9), right = 2*2+2 = 6 (value 10)
Node 8 (index 4): parent = (4-1)//2 = 1 (value 3)
```

### 1-Based Indexing (Alternative)

Some textbooks use 1-based indexing, which gives slightly cleaner formulas:
- **Parent**: `i // 2`
- **Left child**: `2 * i`
- **Right child**: `2 * i + 1`

We will use **0-based indexing** throughout this chapter since that is what Python and Java arrays use.

---

## 16.3 Heapify Operations

Two operations maintain the heap property after modifications:

### Heapify-Up (Bubble Up / Sift Up)

Used after **inserting** a new element at the bottom. The new element may be smaller (min-heap) than its parent, violating the heap property. We fix this by swapping it upward until it finds its correct position.

```
Min-heap insert 2:

Step 0: Add 2 at the next available position (end of array).

           1                    1
          / \                  / \
         3   5       -->      3   5
        / \ / \              / \ / \
       7  8 9  10           7  8 9  10
                           /
                          2    <-- Added here

Step 1: Compare 2 with parent 7. 2 < 7, swap.

           1
          / \
         3   5
        / \ / \
       2  8 9  10
      /
     7

Step 2: Compare 2 with parent 3. 2 < 3, swap.

           1
          / \
         2   5
        / \ / \
       3  8 9  10
      /
     7

Step 3: Compare 2 with parent 1. 2 > 1, STOP.
         2 is in its correct position.
```

### Heapify-Down (Bubble Down / Sift Down)

Used after **extracting** the root. We move the last element to the root and push it down to its correct position by swapping with the smaller child (min-heap).

```
Min-heap extract min:

Step 0: Remove root (1). Move last element (10) to root.

          10                 10
         /  \               /  \
        2    5      -->    2    5
       / \  / \           / \  /
      3   8 9  7         3   8 9
     /                  /
    7                  (removed)

Step 1: Compare 10 with children 2 and 5. Smallest child is 2. 10 > 2, swap.

           2
          / \
        10   5
        / \ /
       3  8 9

Step 2: Compare 10 with children 3 and 8. Smallest child is 3. 10 > 3, swap.

           2
          / \
         3   5
        / \ /
      10  8 9

Step 3: 10 has no children. STOP.
```

---

## 16.4 Implementation from Scratch

**Python:**

```python
class MinHeap:
    """Min-heap implementation using an array."""

    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def insert(self, val):
        """Insert a value into the heap. O(log n)."""
        self.heap.append(val)
        self._heapify_up(len(self.heap) - 1)

    def extract_min(self):
        """Remove and return the minimum value. O(log n)."""
        if not self.heap:
            raise IndexError("Heap is empty")

        if len(self.heap) == 1:
            return self.heap.pop()

        min_val = self.heap[0]
        # Move last element to root
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return min_val

    def peek(self):
        """Return the minimum value without removing it. O(1)."""
        if not self.heap:
            raise IndexError("Heap is empty")
        return self.heap[0]

    def _heapify_up(self, i):
        """Bubble element up to maintain heap property."""
        while i > 0 and self.heap[i] < self.heap[self.parent(i)]:
            self.swap(i, self.parent(i))
            i = self.parent(i)

    def _heapify_down(self, i):
        """Push element down to maintain heap property."""
        size = len(self.heap)

        while True:
            smallest = i
            left = self.left_child(i)
            right = self.right_child(i)

            if left < size and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < size and self.heap[right] < self.heap[smallest]:
                smallest = right

            if smallest == i:
                break

            self.swap(i, smallest)
            i = smallest

    def size(self):
        return len(self.heap)

    def __repr__(self):
        return f"MinHeap({self.heap})"


# Demo
heap = MinHeap()
for val in [10, 4, 15, 1, 7, 3]:
    heap.insert(val)
    print(f"Insert {val:2d}: {heap}")

print()
while heap.size() > 0:
    print(f"Extract min: {heap.extract_min()}, Remaining: {heap}")
```

**Output:**
```
Insert 10: MinHeap([10])
Insert  4: MinHeap([4, 10])
Insert 15: MinHeap([4, 10, 15])
Insert  1: MinHeap([1, 4, 15, 10])
Insert  7: MinHeap([1, 4, 15, 10, 7])
Insert  3: MinHeap([1, 4, 3, 10, 7, 15])

Extract min: 1, Remaining: MinHeap([3, 4, 15, 10, 7])
Extract min: 3, Remaining: MinHeap([4, 7, 15, 10])
Extract min: 4, Remaining: MinHeap([7, 10, 15])
Extract min: 7, Remaining: MinHeap([10, 15])
Extract min: 10, Remaining: MinHeap([15])
Extract min: 15, Remaining: MinHeap([])
```

**Java:**

```java
import java.util.*;

public class MinHeap {
    private List<Integer> heap;

    public MinHeap() {
        heap = new ArrayList<>();
    }

    private int parent(int i) { return (i - 1) / 2; }
    private int leftChild(int i) { return 2 * i + 1; }
    private int rightChild(int i) { return 2 * i + 2; }

    private void swap(int i, int j) {
        int temp = heap.get(i);
        heap.set(i, heap.get(j));
        heap.set(j, temp);
    }

    public void insert(int val) {
        heap.add(val);
        heapifyUp(heap.size() - 1);
    }

    public int extractMin() {
        if (heap.isEmpty()) throw new NoSuchElementException("Heap is empty");

        int min = heap.get(0);
        int last = heap.remove(heap.size() - 1);
        if (!heap.isEmpty()) {
            heap.set(0, last);
            heapifyDown(0);
        }
        return min;
    }

    public int peek() {
        if (heap.isEmpty()) throw new NoSuchElementException("Heap is empty");
        return heap.get(0);
    }

    private void heapifyUp(int i) {
        while (i > 0 && heap.get(i) < heap.get(parent(i))) {
            swap(i, parent(i));
            i = parent(i);
        }
    }

    private void heapifyDown(int i) {
        int size = heap.size();
        while (true) {
            int smallest = i;
            int left = leftChild(i);
            int right = rightChild(i);

            if (left < size && heap.get(left) < heap.get(smallest))
                smallest = left;
            if (right < size && heap.get(right) < heap.get(smallest))
                smallest = right;

            if (smallest == i) break;

            swap(i, smallest);
            i = smallest;
        }
    }

    public int size() { return heap.size(); }

    public static void main(String[] args) {
        MinHeap heap = new MinHeap();
        int[] values = {10, 4, 15, 1, 7, 3};

        for (int val : values) {
            heap.insert(val);
            System.out.println("Insert " + val + ": " + heap.heap);
        }

        System.out.println();
        while (heap.size() > 0) {
            System.out.println("Extract min: " + heap.extractMin());
        }
    }
}
```

### Time and Space Complexity

| Operation | Time | Reason |
|---|---|---|
| Insert | O(log n) | Heapify-up travels at most tree height |
| Extract min/max | O(log n) | Heapify-down travels at most tree height |
| Peek | O(1) | Root is always min/max |
| Build heap | O(n) | NOT O(n log n) -- see next section |
| Space | O(n) | Array of n elements |

---

## 16.5 Building a Heap in O(n)

Building a heap by inserting n elements one by one takes O(n log n). But there is a faster way: start with the array and heapify from the bottom up.

### Why O(n) and Not O(n log n)?

The key insight: most nodes are near the bottom of the tree, and they need very little work.

```
Level 0 (root):     1 node,   heapify-down up to h levels    -> h work
Level 1:            2 nodes,  heapify-down up to h-1 levels  -> 2(h-1) work
Level 2:            4 nodes,  heapify-down up to h-2 levels  -> 4(h-2) work
...
Level h-1:          n/4 nodes, heapify-down up to 1 level    -> n/4 work
Level h (leaves):   n/2 nodes, heapify-down 0 levels          -> 0 work

Total work = sum of (nodes at level k) * (h - k)
           = O(n)  (this sum converges to 2n)
```

Half the nodes are leaves and do zero work. A quarter need one swap. An eighth need two swaps. The math works out to O(n) total.

**Python:**

```python
def build_heap(arr):
    """Build a min-heap from an array in-place. O(n)."""
    n = len(arr)

    # Start from the last non-leaf node and heapify down
    for i in range(n // 2 - 1, -1, -1):
        heapify_down(arr, n, i)


def heapify_down(arr, size, i):
    """Heapify down for min-heap."""
    while True:
        smallest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < size and arr[left] < arr[smallest]:
            smallest = left
        if right < size and arr[right] < arr[smallest]:
            smallest = right

        if smallest == i:
            break

        arr[i], arr[smallest] = arr[smallest], arr[i]
        i = smallest


data = [10, 4, 15, 1, 7, 3, 8]
print(f"Before: {data}")
build_heap(data)
print(f"After:  {data}")
```

**Output:**
```
Before: [10, 4, 15, 1, 7, 3, 8]
After:  [1, 4, 3, 10, 7, 15, 8]
```

---

## 16.6 Using Python's heapq and Java's PriorityQueue

In practice, you rarely implement heaps from scratch. Both Python and Java provide built-in heap implementations.

### Python: heapq (Min-Heap Only)

```python
import heapq

# Create a min-heap from a list
data = [10, 4, 15, 1, 7, 3]
heapq.heapify(data)       # In-place O(n)
print(f"Heapified: {data}")  # [1, 4, 3, 10, 7, 15]

# Insert
heapq.heappush(data, 2)
print(f"After push 2: {data}")

# Extract min
min_val = heapq.heappop(data)
print(f"Popped: {min_val}")
print(f"After pop: {data}")

# Peek (just access index 0)
print(f"Peek: {data[0]}")

# Push and pop in one operation (more efficient)
result = heapq.heappushpop(data, 0)
print(f"Push 0 and pop: {result}")  # Pushes 0, pops 0 (the new min)

# Get n smallest / n largest
numbers = [10, 4, 15, 1, 7, 3, 8, 2, 9, 6]
print(f"3 smallest: {heapq.nsmallest(3, numbers)}")
print(f"3 largest:  {heapq.nlargest(3, numbers)}")
```

**Output:**
```
Heapified: [1, 4, 3, 10, 7, 15]
After push 2: [1, 4, 2, 10, 7, 15, 3]
Popped: 1
After pop: [2, 4, 3, 10, 7, 15]
Peek: 2
Push 0 and pop: 0
3 smallest: [1, 2, 3]
3 largest:  [15, 10, 9]
```

### Python Max-Heap Trick

Python only provides a min-heap. To simulate a max-heap, **negate the values**:

```python
import heapq

# Max-heap using negation
max_heap = []
for val in [10, 4, 15, 1, 7]:
    heapq.heappush(max_heap, -val)  # Negate on insert

# Extract max (negate again)
max_val = -heapq.heappop(max_heap)
print(f"Max: {max_val}")  # 15

# Peek at max
print(f"Current max: {-max_heap[0]}")  # 10
```

**Output:**
```
Max: 15
Current max: 10
```

### Java: PriorityQueue (Min-Heap by Default)

```java
import java.util.*;

public class HeapDemo {
    public static void main(String[] args) {
        // Min-heap (default)
        PriorityQueue<Integer> minHeap = new PriorityQueue<>();
        for (int val : new int[]{10, 4, 15, 1, 7, 3}) {
            minHeap.offer(val);
        }

        System.out.println("Peek min: " + minHeap.peek());     // 1
        System.out.println("Poll min: " + minHeap.poll());      // 1
        System.out.println("Next min: " + minHeap.peek());      // 3
        System.out.println("Size: " + minHeap.size());           // 5

        // Max-heap using reverse comparator
        PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());
        for (int val : new int[]{10, 4, 15, 1, 7, 3}) {
            maxHeap.offer(val);
        }

        System.out.println("\nPeek max: " + maxHeap.peek());    // 15
        System.out.println("Poll max: " + maxHeap.poll());       // 15
        System.out.println("Next max: " + maxHeap.peek());       // 10
    }
}
```

**Output:**
```
Peek min: 1
Poll min: 1
Next min: 3
Size: 5

Peek max: 15
Poll max: 15
Next max: 10
```

---

## 16.7 Heap Sort

Heap sort uses a heap to sort an array in O(n log n) time with O(1) extra space.

### Algorithm

1. **Build a max-heap** from the array in O(n).
2. **Repeatedly extract the max**: swap the root (max) with the last unsorted element, shrink the heap by 1, and heapify-down the new root.

### Step-by-Step Walkthrough

```
Array: [4, 10, 3, 5, 1]

Step 1: Build max-heap
  [10, 5, 3, 4, 1]

Step 2: Swap root (10) with last element (1). Heap size = 4.
  [1, 5, 3, 4, | 10]
  Heapify down: [5, 4, 3, 1, | 10]

Step 3: Swap root (5) with last unsorted (1). Heap size = 3.
  [1, 4, 3, | 5, 10]
  Heapify down: [4, 1, 3, | 5, 10]

Step 4: Swap root (4) with last unsorted (3). Heap size = 2.
  [3, 1, | 4, 5, 10]
  Heapify down: [3, 1, | 4, 5, 10]

Step 5: Swap root (3) with last unsorted (1). Heap size = 1.
  [1, | 3, 4, 5, 10]

Result: [1, 3, 4, 5, 10]  (sorted!)
```

**Python:**

```python
def heap_sort(arr):
    """Sort array in ascending order using heap sort."""
    n = len(arr)

    # Step 1: Build max-heap
    for i in range(n // 2 - 1, -1, -1):
        max_heapify_down(arr, n, i)

    # Step 2: Extract max one by one
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]  # Move max to end
        max_heapify_down(arr, i, 0)       # Heapify reduced heap


def max_heapify_down(arr, size, i):
    """Heapify down for max-heap."""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < size and arr[left] > arr[largest]:
            largest = left
        if right < size and arr[right] > arr[largest]:
            largest = right

        if largest == i:
            break

        arr[i], arr[largest] = arr[largest], arr[i]
        i = largest


data = [4, 10, 3, 5, 1, 8, 7, 2, 9, 6]
print(f"Before: {data}")
heap_sort(data)
print(f"After:  {data}")
```

**Output:**
```
Before: [4, 10, 3, 5, 1, 8, 7, 2, 9, 6]
After:  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

### Heap Sort Complexity

| Metric | Value | Notes |
|---|---|---|
| Time (all cases) | O(n log n) | Build O(n) + n extractions O(n log n) |
| Space | O(1) | In-place sorting |
| Stable? | No | Equal elements may change relative order |

Compared to other sorts:
- **Merge sort**: O(n log n) but needs O(n) extra space
- **Quick sort**: O(n log n) average but O(n^2) worst case
- **Heap sort**: O(n log n) guaranteed with O(1) space -- but slower in practice due to poor cache behavior

---

## Common Mistakes

1. **Forgetting Python's heapq is min-heap only.** To get a max-heap in Python, negate values on insert and negate again on extract. Forgetting to negate back gives wrong results.

2. **Off-by-one errors in index formulas.** With 0-based indexing, the parent of index `i` is `(i-1)//2`, not `i//2`. The left child is `2*i+1`, not `2*i`. Mixing up 0-based and 1-based formulas is the most common heap bug.

3. **Assuming heapq.nsmallest always uses a heap.** For small k, `heapq.nsmallest(k, data)` is efficient. But for k close to n, sorting is faster. Python's implementation is smart about this, but be aware of the trade-off.

4. **Modifying heap elements directly.** If you change an element in the middle of a heap array, the heap property is violated. You must remove and re-insert, or heapify after modification.

5. **Confusing heap with sorted array.** A heap is NOT fully sorted. Only the root is guaranteed to be the min (or max). The second-smallest could be at index 1 or index 2. If you need sorted output, extract all elements one by one.

---

## Best Practices

1. **Use the standard library.** Python's `heapq` and Java's `PriorityQueue` are well-tested and optimized. Only implement from scratch if you need custom behavior or for learning.

2. **Use tuples for custom priority in Python.** `heapq` compares elements directly. Use `(priority, item)` tuples: `heapq.heappush(heap, (3, "task"))`.

3. **Consider a heap when you see "kth largest," "top K," or "streaming" in a problem.** These are classic heap signals. A heap of size K gives O(n log k) which beats O(n log n) sorting when k is small.

4. **Use two heaps for median problems.** A max-heap for the lower half and a min-heap for the upper half gives O(log n) insert and O(1) median access.

5. **Think about whether you need min-heap or max-heap.** For "kth largest," use a min-heap of size k (the root is the kth largest). For "kth smallest," use a max-heap of size k.

---

## Quick Summary

| Concept | Key Point |
|---|---|
| Heap | Complete binary tree with parent-child ordering |
| Min-heap | Root is the minimum; parent <= children |
| Max-heap | Root is the maximum; parent >= children |
| Array storage | Parent = (i-1)//2, Left = 2i+1, Right = 2i+2 |
| Insert | Add at end, heapify up. O(log n) |
| Extract | Remove root, move last to root, heapify down. O(log n) |
| Build heap | Bottom-up heapify. O(n) |
| Heap sort | Build max-heap + repeated extraction. O(n log n), O(1) space |
| Python | `heapq` module (min-heap only) |
| Java | `PriorityQueue` class (min-heap default) |

---

## Key Points

- A heap is a complete binary tree stored in an array -- no pointers needed.
- Min-heap gives O(1) access to the minimum; max-heap gives O(1) access to the maximum.
- Insert and extract are both O(log n) because heapify traverses at most the tree height.
- Building a heap from n elements is O(n), not O(n log n), thanks to the bottom-up approach.
- Python's heapq is min-heap only; negate values for max-heap behavior.
- Heap sort is O(n log n) guaranteed with O(1) extra space, but is not stable.

---

## Practice Questions

1. **Array to tree**: Draw the tree representation of the heap array `[2, 5, 3, 8, 7, 9, 4]`. Is it a valid min-heap? If not, which node violates the property?

2. **Insert trace**: Starting with min-heap `[1, 3, 5, 7, 8]`, insert the value 2. Show the array after each swap during heapify-up.

3. **Extract trace**: Starting with min-heap `[1, 3, 5, 7, 8, 9]`, extract the minimum. Show the array after each swap during heapify-down.

4. **Build heap**: Build a min-heap from the array `[9, 5, 7, 1, 3]` using the bottom-up method. Show the array after processing each non-leaf node.

5. **Max-heap in Python**: Write code using `heapq` to maintain a max-heap that supports push and pop-max operations. Test with values [5, 1, 8, 3, 9, 2].

---

## LeetCode-Style Problems

### Problem 1: Kth Largest Element in an Array (LeetCode 215)

**Problem**: Given an integer array and an integer k, return the kth largest element.

**Key Insight**: Maintain a min-heap of size k. The root is always the kth largest element seen so far. Any element smaller than the root cannot be in the top k.

```python
import heapq


def find_kth_largest(nums, k):
    """Find kth largest using a min-heap of size k."""
    heap = []

    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)  # Remove smallest

    return heap[0]  # Root is the kth largest


# Alternative: one-liner
def find_kth_largest_v2(nums, k):
    return heapq.nlargest(k, nums)[-1]


nums = [3, 2, 1, 5, 6, 4]
print(f"2nd largest: {find_kth_largest(nums, 2)}")  # 5

nums = [3, 2, 3, 1, 2, 4, 5, 5, 6]
print(f"4th largest: {find_kth_largest(nums, 4)}")  # 4
```

**Output:**
```
2nd largest: 5
4th largest: 4
```

```java
public int findKthLargest(int[] nums, int k) {
    PriorityQueue<Integer> minHeap = new PriorityQueue<>();
    for (int num : nums) {
        minHeap.offer(num);
        if (minHeap.size() > k) {
            minHeap.poll();
        }
    }
    return minHeap.peek();
}
```

**Complexity**: O(n log k) time, O(k) space.

---

### Problem 2: Merge K Sorted Lists (LeetCode 23)

**Problem**: Merge k sorted linked lists into one sorted list.

**Key Insight**: Use a min-heap to always pick the smallest element among all k list heads.

```python
import heapq


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def merge_k_lists(lists):
    """Merge k sorted lists using a min-heap."""
    heap = []

    # Add the head of each list to the heap
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


# Helper to create and print linked lists
def create_list(arr):
    dummy = ListNode(0)
    curr = dummy
    for val in arr:
        curr.next = ListNode(val)
        curr = curr.next
    return dummy.next


def print_list(head):
    vals = []
    while head:
        vals.append(str(head.val))
        head = head.next
    return " -> ".join(vals)


lists = [
    create_list([1, 4, 5]),
    create_list([1, 3, 4]),
    create_list([2, 6])
]

result = merge_k_lists(lists)
print(f"Merged: {print_list(result)}")
```

**Output:**
```
Merged: 1 -> 1 -> 2 -> 3 -> 4 -> 4 -> 5 -> 6
```

```java
public ListNode mergeKLists(ListNode[] lists) {
    PriorityQueue<ListNode> heap = new PriorityQueue<>(
        (a, b) -> a.val - b.val
    );

    for (ListNode node : lists) {
        if (node != null) heap.offer(node);
    }

    ListNode dummy = new ListNode(0);
    ListNode current = dummy;

    while (!heap.isEmpty()) {
        ListNode node = heap.poll();
        current.next = node;
        current = current.next;
        if (node.next != null) heap.offer(node.next);
    }

    return dummy.next;
}
```

**Complexity**: O(N log k) time where N = total elements across all lists and k = number of lists. O(k) space.

---

### Problem 3: Top K Frequent Elements (LeetCode 347)

**Problem**: Given an integer array and k, return the k most frequent elements.

```python
import heapq
from collections import Counter


def top_k_frequent(nums, k):
    """Find the k most frequent elements using a min-heap."""
    count = Counter(nums)

    # Use a min-heap of size k based on frequency
    heap = []
    for num, freq in count.items():
        heapq.heappush(heap, (freq, num))
        if len(heap) > k:
            heapq.heappop(heap)

    return [num for freq, num in heap]


nums = [1, 1, 1, 2, 2, 3]
print(f"Top 2 frequent: {top_k_frequent(nums, 2)}")  # [2, 1]

nums = [1]
print(f"Top 1 frequent: {top_k_frequent(nums, 1)}")  # [1]
```

**Output:**
```
Top 2 frequent: [2, 1]
Top 1 frequent: [1]
```

```java
public int[] topKFrequent(int[] nums, int k) {
    Map<Integer, Integer> count = new HashMap<>();
    for (int num : nums) {
        count.merge(num, 1, Integer::sum);
    }

    PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> a[1] - b[1]);
    for (var entry : count.entrySet()) {
        heap.offer(new int[]{entry.getKey(), entry.getValue()});
        if (heap.size() > k) heap.poll();
    }

    int[] result = new int[k];
    for (int i = 0; i < k; i++) {
        result[i] = heap.poll()[0];
    }
    return result;
}
```

**Complexity**: O(n log k) time, O(n) space for the counter.

---

### Problem 4: Find Median from Data Stream (LeetCode 295)

**Problem**: Design a data structure that supports adding numbers and finding the median at any time.

**Key Insight**: Use two heaps:
- A **max-heap** for the lower half of the numbers
- A **min-heap** for the upper half of the numbers

The median is either the top of the max-heap (odd count) or the average of both tops (even count).

```
Numbers added: 1, 5, 2, 8, 3

After 1:   max_heap=[1]          min_heap=[]         median=1
After 5:   max_heap=[1]          min_heap=[5]        median=(1+5)/2=3.0
After 2:   max_heap=[2,1]        min_heap=[5]        median=2
After 8:   max_heap=[2,1]        min_heap=[5,8]      median=(2+5)/2=3.5
After 3:   max_heap=[3,1,2]      min_heap=[5,8]      median=3
```

**Solution:**

```python
import heapq


class MedianFinder:
    def __init__(self):
        # Max-heap for lower half (negate values for Python)
        self.low = []   # max-heap (negated)
        # Min-heap for upper half
        self.high = []  # min-heap

    def add_num(self, num):
        # Always add to max-heap first
        heapq.heappush(self.low, -num)

        # Ensure max of low <= min of high
        if self.low and self.high and (-self.low[0]) > self.high[0]:
            val = -heapq.heappop(self.low)
            heapq.heappush(self.high, val)

        # Balance sizes: low can have at most 1 more than high
        if len(self.low) > len(self.high) + 1:
            val = -heapq.heappop(self.low)
            heapq.heappush(self.high, val)
        elif len(self.high) > len(self.low):
            val = heapq.heappop(self.high)
            heapq.heappush(self.low, -val)

    def find_median(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2


mf = MedianFinder()
for num in [1, 5, 2, 8, 3]:
    mf.add_num(num)
    print(f"Add {num}: median = {mf.find_median()}")
```

**Output:**
```
Add 1: median = 1
Add 5: median = 3.0
Add 2: median = 2
Add 8: median = 3.5
Add 3: median = 3
```

```java
class MedianFinder {
    PriorityQueue<Integer> low;   // max-heap
    PriorityQueue<Integer> high;  // min-heap

    public MedianFinder() {
        low = new PriorityQueue<>(Collections.reverseOrder());
        high = new PriorityQueue<>();
    }

    public void addNum(int num) {
        low.offer(num);

        if (!low.isEmpty() && !high.isEmpty() && low.peek() > high.peek()) {
            high.offer(low.poll());
        }

        if (low.size() > high.size() + 1) {
            high.offer(low.poll());
        } else if (high.size() > low.size()) {
            low.offer(high.poll());
        }
    }

    public double findMedian() {
        if (low.size() > high.size()) {
            return low.peek();
        }
        return (low.peek() + high.peek()) / 2.0;
    }
}
```

**Complexity**: O(log n) per addNum, O(1) for findMedian. O(n) total space.

---

### Problem 5: Last Stone Weight (LeetCode 1046)

**Problem**: You have a collection of stones with integer weights. Each turn, pick the two heaviest stones and smash them. If they are equal, both are destroyed. Otherwise, the lighter one is destroyed and the heavier one loses weight equal to the lighter one. Return the weight of the last remaining stone (or 0).

```python
import heapq


def last_stone_weight(stones):
    """Simulate stone smashing using a max-heap."""
    # Negate for max-heap behavior
    heap = [-s for s in stones]
    heapq.heapify(heap)

    while len(heap) > 1:
        stone1 = -heapq.heappop(heap)  # Heaviest
        stone2 = -heapq.heappop(heap)  # Second heaviest

        if stone1 != stone2:
            heapq.heappush(heap, -(stone1 - stone2))

    return -heap[0] if heap else 0


print(last_stone_weight([2, 7, 4, 1, 8, 1]))  # 1
print(last_stone_weight([1]))                   # 1
print(last_stone_weight([3, 3]))                # 0
```

**Output:**
```
1
1
0
```

```java
public int lastStoneWeight(int[] stones) {
    PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());
    for (int s : stones) maxHeap.offer(s);

    while (maxHeap.size() > 1) {
        int s1 = maxHeap.poll();
        int s2 = maxHeap.poll();
        if (s1 != s2) maxHeap.offer(s1 - s2);
    }

    return maxHeap.isEmpty() ? 0 : maxHeap.peek();
}
```

**Complexity**: O(n log n) time, O(n) space.

---

## What Is Next?

Heaps gave you priority-based access to data. Now it is time to move beyond trees entirely. In Chapter 17, you will learn about **Graphs** -- the most general data structure for representing connections. Cities connected by roads, friends in a social network, web pages linked to each other -- all of these are graphs. You will learn the vocabulary, representation methods, and build the foundation for powerful graph algorithms.
