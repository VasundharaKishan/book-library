# Chapter 7: Queues

## What You Will Learn

- What a queue is and how it follows the FIFO (First In, First Out) principle
- How to implement a queue using arrays (circular buffer) and linked lists
- Core queue operations: enqueue, dequeue, and peek
- What a deque (double-ended queue) is and when to use it
- A preview of priority queues
- How Breadth-First Search (BFS) relies on queues
- How to solve classic queue-based interview problems

## Why This Chapter Matters

Queues are everywhere in the real world and in computing. Every time you stand in line at a store, you are participating in a queue. The first person to join the line is the first person served. This simple idea -- First In, First Out -- powers everything from print job scheduling and web server request handling to the BFS algorithm that finds shortest paths in graphs.

If stacks (Chapter 6) were about "last in, first out," queues flip that idea on its head. Understanding both data structures gives you a complete toolkit for managing ordered data. Many interview problems that seem complex at first become straightforward once you recognize that a queue is the right tool.

---

## 7.1 What Is a Queue?

A **queue** is a linear data structure that follows the **FIFO** (First In, First Out) principle. The element that enters first is the element that leaves first.

### Real-World Analogy: The Line at a Store

Imagine a checkout line at a grocery store:

```
  FRONT                                    BACK
  (next to                                (end of
   be served)                               line)
    |                                        |
    v                                        v
 +------+   +------+   +------+   +------+
 | Alex |-->| Beth |-->| Carl |-->| Dana |
 +------+   +------+   +------+   +------+

 Alex arrived first   -->   Dana arrived last
 Alex will be served first
```

- **Enqueue**: A new person joins the BACK of the line.
- **Dequeue**: The person at the FRONT is served and leaves.
- **Peek**: You look at who is at the front without removing them.

### Core Operations

| Operation   | Description                          | Time Complexity |
|-------------|--------------------------------------|-----------------|
| `enqueue`   | Add an element to the back           | O(1)            |
| `dequeue`   | Remove and return the front element  | O(1)            |
| `peek`      | View the front element without removing | O(1)         |
| `isEmpty`   | Check if the queue is empty          | O(1)            |
| `size`      | Return the number of elements        | O(1)            |

---

## 7.2 Array-Based Queue (Naive Approach)

The simplest way to build a queue is with a regular array (or list). We add to the end and remove from the front.

### Python -- Naive Array Queue

```python
class NaiveArrayQueue:
    def __init__(self):
        self.data = []

    def enqueue(self, value):
        self.data.append(value)  # O(1) amortized

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.data.pop(0)  # O(n) -- shifts all elements!

    def peek(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.data[0]

    def is_empty(self):
        return len(self.data) == 0

    def size(self):
        return len(self.data)


# Usage
q = NaiveArrayQueue()
q.enqueue(10)
q.enqueue(20)
q.enqueue(30)
print(q.dequeue())  # Output: 10
print(q.peek())     # Output: 20
print(q.size())     # Output: 2
```

### The Problem with pop(0)

When you remove from the front of an array, every remaining element must shift left by one position:

```
Before dequeue:
Index:  0    1    2    3
      [10] [20] [30] [40]
       ^
       Remove this

After dequeue (all elements shift left):
Index:  0    1    2
      [20] [30] [40]
       <--  <--  <--   (n-1 shifts = O(n))
```

This makes dequeue O(n), which is unacceptable for large queues. The solution? A **circular queue**.

---

## 7.3 Array-Based Queue (Circular Buffer)

A circular queue uses a fixed-size array with two pointers -- `front` and `rear` -- that wrap around to the beginning when they reach the end. No element shifting is needed.

### How the Circular Buffer Works

```
Capacity = 5

Step 1: Enqueue 10, 20, 30
  front=0, rear=3
  +----+----+----+----+----+
  | 10 | 20 | 30 |    |    |
  +----+----+----+----+----+
    ^              ^
  front           rear

Step 2: Dequeue -> returns 10
  front=1, rear=3
  +----+----+----+----+----+
  |    | 20 | 30 |    |    |
  +----+----+----+----+----+
         ^         ^
       front      rear

Step 3: Enqueue 40, 50
  front=1, rear=0 (wrapped!)
  +----+----+----+----+----+
  |    | 20 | 30 | 40 | 50 |
  +----+----+----+----+----+
         ^                   ^
       front           rear(wraps to 0)

Step 4: Enqueue 60
  front=1, rear=1 (wrapped!)
  +----+----+----+----+----+
  | 60 | 20 | 30 | 40 | 50 |
  +----+----+----+----+----+
    ^    ^
  rear  front
  Queue is now FULL (size == capacity)
```

### Python -- Circular Queue

```python
class CircularQueue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = [None] * capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    def enqueue(self, value):
        if self.is_full():
            raise OverflowError("Queue is full")
        self.data[self.rear] = value
        self.rear = (self.rear + 1) % self.capacity  # Wrap around
        self.count += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        value = self.data[self.front]
        self.data[self.front] = None  # Optional: clear reference
        self.front = (self.front + 1) % self.capacity  # Wrap around
        self.count -= 1
        return value

    def peek(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.data[self.front]

    def is_empty(self):
        return self.count == 0

    def is_full(self):
        return self.count == self.capacity

    def size(self):
        return self.count


# Usage
cq = CircularQueue(4)
cq.enqueue(1)
cq.enqueue(2)
cq.enqueue(3)
print(cq.dequeue())   # Output: 1
cq.enqueue(4)
cq.enqueue(5)
print(cq.dequeue())   # Output: 2
print(cq.dequeue())   # Output: 3
print(cq.peek())      # Output: 4
print(cq.size())      # Output: 2
```

### Java -- Circular Queue

```java
public class CircularQueue {
    private int[] data;
    private int front, rear, count, capacity;

    public CircularQueue(int capacity) {
        this.capacity = capacity;
        this.data = new int[capacity];
        this.front = 0;
        this.rear = 0;
        this.count = 0;
    }

    public void enqueue(int value) {
        if (isFull()) {
            throw new RuntimeException("Queue is full");
        }
        data[rear] = value;
        rear = (rear + 1) % capacity;  // Wrap around
        count++;
    }

    public int dequeue() {
        if (isEmpty()) {
            throw new RuntimeException("Queue is empty");
        }
        int value = data[front];
        front = (front + 1) % capacity;  // Wrap around
        count--;
        return value;
    }

    public int peek() {
        if (isEmpty()) {
            throw new RuntimeException("Queue is empty");
        }
        return data[front];
    }

    public boolean isEmpty() {
        return count == 0;
    }

    public boolean isFull() {
        return count == capacity;
    }

    public int size() {
        return count;
    }

    public static void main(String[] args) {
        CircularQueue cq = new CircularQueue(4);
        cq.enqueue(1);
        cq.enqueue(2);
        cq.enqueue(3);
        System.out.println(cq.dequeue());  // Output: 1
        cq.enqueue(4);
        cq.enqueue(5);
        System.out.println(cq.dequeue());  // Output: 2
        System.out.println(cq.dequeue());  // Output: 3
        System.out.println(cq.peek());     // Output: 4
        System.out.println(cq.size());     // Output: 2
    }
}
```

### Why `% capacity` Is the Key

The modulo operator creates the "circular" behavior:

```
If rear = 4 and capacity = 5:
  next rear = (4 + 1) % 5 = 0   --> wraps to beginning!

If rear = 2 and capacity = 5:
  next rear = (2 + 1) % 5 = 3   --> normal increment
```

### Time and Space Complexity

| Operation | Time  | Space  |
|-----------|-------|--------|
| enqueue   | O(1)  | O(1)   |
| dequeue   | O(1)  | O(1)   |
| peek      | O(1)  | O(1)   |
| Overall   | --    | O(n)   |

---

## 7.4 Linked-List-Based Queue

A linked list naturally supports O(1) operations at both ends if we maintain both a `head` (front) and a `tail` (rear) pointer.

### How It Works

```
Enqueue 10, 20, 30:

  front                          rear
    |                              |
    v                              v
 +------+    +------+    +------+
 |  10  |--->|  20  |--->|  30  |---> None
 +------+    +------+    +------+

Dequeue -> returns 10:

         front              rear
           |                  |
           v                  v
        +------+    +------+
        |  20  |--->|  30  |---> None
        +------+    +------+

Enqueue 40:

         front                        rear
           |                            |
           v                            v
        +------+    +------+    +------+
        |  20  |--->|  30  |--->|  40  |---> None
        +------+    +------+    +------+
```

### Python -- Linked List Queue

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedListQueue:
    def __init__(self):
        self.front = None
        self.rear = None
        self.count = 0

    def enqueue(self, value):
        new_node = Node(value)
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self.count += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        value = self.front.value
        self.front = self.front.next
        if self.front is None:
            self.rear = None  # Queue is now empty
        self.count -= 1
        return value

    def peek(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.front.value

    def is_empty(self):
        return self.front is None

    def size(self):
        return self.count


# Usage
q = LinkedListQueue()
q.enqueue("Alice")
q.enqueue("Bob")
q.enqueue("Charlie")
print(q.dequeue())  # Output: Alice
print(q.peek())     # Output: Bob
print(q.size())     # Output: 2
```

### Java -- Linked List Queue

```java
public class LinkedListQueue {
    private static class Node {
        int value;
        Node next;

        Node(int value) {
            this.value = value;
            this.next = null;
        }
    }

    private Node front, rear;
    private int count;

    public LinkedListQueue() {
        this.front = null;
        this.rear = null;
        this.count = 0;
    }

    public void enqueue(int value) {
        Node newNode = new Node(value);
        if (rear == null) {
            front = rear = newNode;
        } else {
            rear.next = newNode;
            rear = newNode;
        }
        count++;
    }

    public int dequeue() {
        if (isEmpty()) {
            throw new RuntimeException("Queue is empty");
        }
        int value = front.value;
        front = front.next;
        if (front == null) {
            rear = null;
        }
        count--;
        return value;
    }

    public int peek() {
        if (isEmpty()) {
            throw new RuntimeException("Queue is empty");
        }
        return front.value;
    }

    public boolean isEmpty() {
        return front == null;
    }

    public int size() {
        return count;
    }

    public static void main(String[] args) {
        LinkedListQueue q = new LinkedListQueue();
        q.enqueue(100);
        q.enqueue(200);
        q.enqueue(300);
        System.out.println(q.dequeue());  // Output: 100
        System.out.println(q.peek());     // Output: 200
        System.out.println(q.size());     // Output: 2
    }
}
```

### Array vs Linked List Queue -- Comparison

| Feature            | Array (Circular)          | Linked List               |
|--------------------|---------------------------|---------------------------|
| Memory             | Pre-allocated, fixed      | Dynamic, grows as needed  |
| Cache performance  | Better (contiguous)       | Worse (scattered nodes)   |
| Overflow           | Can happen if fixed size  | Only limited by memory    |
| Extra memory       | May waste unused slots    | Extra pointer per node    |
| Implementation     | Slightly trickier (modulo)| Straightforward           |

---

## 7.5 Using Built-In Queues

In practice, you rarely implement queues from scratch. Both Python and Java provide excellent built-in options.

### Python -- collections.deque

```python
from collections import deque

q = deque()

# Enqueue
q.append(10)
q.append(20)
q.append(30)

# Dequeue
print(q.popleft())  # Output: 10

# Peek
print(q[0])         # Output: 20

# Size
print(len(q))       # Output: 2

# Check empty
print(len(q) == 0)  # Output: False
```

**Why `deque` and not `list`?** `deque.popleft()` is O(1), while `list.pop(0)` is O(n).

### Java -- java.util.LinkedList as Queue

```java
import java.util.LinkedList;
import java.util.Queue;

public class BuiltInQueueDemo {
    public static void main(String[] args) {
        Queue<Integer> queue = new LinkedList<>();

        // Enqueue
        queue.offer(10);
        queue.offer(20);
        queue.offer(30);

        // Dequeue
        System.out.println(queue.poll());  // Output: 10

        // Peek
        System.out.println(queue.peek());  // Output: 20

        // Size
        System.out.println(queue.size());  // Output: 2

        // Check empty
        System.out.println(queue.isEmpty());  // Output: false
    }
}
```

**Note**: In Java, prefer `offer()`/`poll()`/`peek()` over `add()`/`remove()`/`element()`. The first set returns special values on failure; the second set throws exceptions.

---

## 7.6 Deque (Double-Ended Queue)

A **deque** (pronounced "deck") allows insertion and removal at **both** ends in O(1) time.

```
       addFirst          addLast
          |                 |
          v                 v
  +----+----+----+----+----+
  |    | 10 | 20 | 30 |    |
  +----+----+----+----+----+
          ^              ^
     removeFirst    removeLast
```

### Python -- Deque Operations

```python
from collections import deque

d = deque()

# Add to both ends
d.append(2)       # Right: [2]
d.append(3)       # Right: [2, 3]
d.appendleft(1)   # Left:  [1, 2, 3]

# Remove from both ends
print(d.pop())        # Output: 3   -> [1, 2]
print(d.popleft())    # Output: 1   -> [2]

# Peek both ends
d.append(10)
d.appendleft(5)       # [5, 2, 10]
print(d[0])           # Output: 5   (front)
print(d[-1])          # Output: 10  (back)
```

### Java -- ArrayDeque

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class DequeDemo {
    public static void main(String[] args) {
        Deque<Integer> deque = new ArrayDeque<>();

        // Add to both ends
        deque.addLast(2);     // [2]
        deque.addLast(3);     // [2, 3]
        deque.addFirst(1);    // [1, 2, 3]

        // Remove from both ends
        System.out.println(deque.removeLast());   // Output: 3
        System.out.println(deque.removeFirst());  // Output: 1

        // Peek both ends
        deque.addLast(10);
        deque.addFirst(5);   // [5, 2, 10]
        System.out.println(deque.peekFirst());  // Output: 5
        System.out.println(deque.peekLast());   // Output: 10
    }
}
```

### When to Use a Deque

- **Sliding window problems**: Add/remove from both ends efficiently
- **Palindrome checking**: Compare characters from both ends
- **Work stealing algorithms**: Threads steal tasks from the back of other threads' deques
- **Undo/redo with limited history**: Remove oldest entries from one end when the buffer is full

---

## 7.7 Priority Queue Preview

A **priority queue** does not follow FIFO. Instead, elements are dequeued in order of **priority** (highest or lowest value first). We cover priority queues in depth in Chapter 16 (Heaps), but here is a quick taste.

### Python -- heapq (Min-Heap)

```python
import heapq

pq = []
heapq.heappush(pq, 30)
heapq.heappush(pq, 10)
heapq.heappush(pq, 20)

print(heapq.heappop(pq))  # Output: 10  (smallest first)
print(heapq.heappop(pq))  # Output: 20
print(heapq.heappop(pq))  # Output: 30
```

### Java -- PriorityQueue (Min-Heap)

```java
import java.util.PriorityQueue;

public class PriorityQueueDemo {
    public static void main(String[] args) {
        PriorityQueue<Integer> pq = new PriorityQueue<>();
        pq.offer(30);
        pq.offer(10);
        pq.offer(20);

        System.out.println(pq.poll());  // Output: 10
        System.out.println(pq.poll());  // Output: 20
        System.out.println(pq.poll());  // Output: 30
    }
}
```

| Feature        | Regular Queue | Priority Queue |
|----------------|---------------|----------------|
| Order          | FIFO          | By priority    |
| Enqueue        | O(1)          | O(log n)       |
| Dequeue        | O(1)          | O(log n)       |
| Best for       | Fairness      | Scheduling     |

---

## 7.8 BFS Uses Queues

Breadth-First Search is one of the most important algorithms in computer science, and it relies entirely on a queue. BFS explores a graph level by level -- just like ripples spreading outward when you drop a stone in water.

### BFS Step-by-Step

```
Graph:
    1 --- 2
    |     |
    3 --- 4 --- 5

BFS from node 1:

Step 1: Start at 1, enqueue 1
  Queue: [1]         Visited: {1}

Step 2: Dequeue 1, enqueue neighbors 2, 3
  Queue: [2, 3]      Visited: {1, 2, 3}

Step 3: Dequeue 2, enqueue unvisited neighbor 4
  Queue: [3, 4]      Visited: {1, 2, 3, 4}

Step 4: Dequeue 3 (neighbor 4 already visited)
  Queue: [4]          Visited: {1, 2, 3, 4}

Step 5: Dequeue 4, enqueue unvisited neighbor 5
  Queue: [5]          Visited: {1, 2, 3, 4, 5}

Step 6: Dequeue 5 (no unvisited neighbors)
  Queue: []           Visited: {1, 2, 3, 4, 5}

BFS order: 1 -> 2 -> 3 -> 4 -> 5
```

### Python -- BFS Implementation

```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


# Usage
graph = {
    1: [2, 3],
    2: [1, 4],
    3: [1, 4],
    4: [2, 3, 5],
    5: [4]
}
print(bfs(graph, 1))  # Output: [1, 2, 3, 4, 5]
```

---

## 7.9 Common Mistakes

1. **Using `list.pop(0)` in Python**: This is O(n). Always use `collections.deque` for queue operations.

2. **Forgetting to update `rear` to `None` in linked list queue**: When the last element is dequeued, both `front` and `rear` must be set to `None`, or the next enqueue will break.

3. **Off-by-one in circular queue**: The `is_full` check is tricky. Use a separate `count` variable instead of comparing `front == rear` (which also means empty).

4. **Not handling empty queue**: Always check `is_empty()` before calling `dequeue()` or `peek()`.

5. **Confusing stack and queue operations**: Stacks use LIFO (`push`/`pop` from the same end). Queues use FIFO (`enqueue` at back, `dequeue` from front). Mixing them up is a common bug.

---

## 7.10 Best Practices

1. **Use built-in implementations**: `collections.deque` in Python, `LinkedList` or `ArrayDeque` in Java. They are tested, optimized, and correct.

2. **Prefer `deque` over `Queue` in Python**: The `queue.Queue` module is designed for thread-safe multi-threaded programs. For single-threaded code and algorithms, `collections.deque` is faster.

3. **Choose the right variant**: Use a regular queue for FIFO, a deque for double-ended access, and a priority queue when order-by-value matters.

4. **Use `offer`/`poll`/`peek` in Java**: These methods return `null` or `false` on failure instead of throwing exceptions, making your code more robust.

5. **Think "BFS" when you see "shortest path" or "level-by-level"**: If a problem asks you to explore neighbors before going deeper, a queue is almost certainly involved.

---

## Quick Summary

A **queue** is a FIFO data structure -- the first element added is the first removed. You can implement it with a **circular array** (fixed size, great cache performance) or a **linked list** (dynamic size, simple logic). A **deque** extends the queue to allow operations at both ends. **Priority queues** order elements by priority rather than arrival time. The **BFS algorithm** is the most important application of queues.

---

## Key Points

- Queue = FIFO: First In, First Out
- Three core operations: `enqueue` (add to back), `dequeue` (remove from front), `peek` (view front)
- Circular array queues use the modulo operator (`% capacity`) to wrap pointers
- Linked list queues need both `front` and `rear` pointers for O(1) operations
- Python: use `collections.deque`; Java: use `Queue` interface with `LinkedList` or `ArrayDeque`
- Deques allow O(1) insertion and removal at both ends
- BFS traverses graphs level by level using a queue
- All core queue operations run in O(1) time

---

## Practice Questions

1. What happens if you use a regular Python list as a queue and call `pop(0)` on a list with 1 million elements? What is the time complexity, and what should you use instead?

2. In a circular queue with capacity 5, if `front = 3` and `rear = 1`, how many elements are in the queue? Draw the array state.

3. Explain the difference between a queue, a deque, and a priority queue. Give one real-world example of each.

4. Why does a linked list queue need a `rear` pointer? What would happen if you only had a `front` pointer and tried to enqueue?

5. A printer receives jobs from multiple users. Which type of queue would you use if: (a) jobs should be processed in order received, (b) some jobs are marked "urgent" and should print first?

---

## LeetCode-Style Problems

### Problem 1: Implement Queue Using Stacks (LeetCode 232)

**Problem**: Implement a FIFO queue using only two stacks. Support `push`, `pop`, `peek`, and `empty`.

**Approach**: Use two stacks. One stack (`in_stack`) handles pushes. The other (`out_stack`) handles pops. When `out_stack` is empty and we need to pop, we pour all elements from `in_stack` into `out_stack`, which reverses the order -- turning LIFO into FIFO.

```
Push 1, 2, 3:
  in_stack:  [1, 2, 3]  (top = 3)
  out_stack: []

Pop (out_stack empty, so transfer):
  in_stack:  []
  out_stack: [3, 2, 1]  (top = 1)

Pop -> returns 1:
  out_stack: [3, 2]     (top = 2)

Push 4:
  in_stack:  [4]
  out_stack: [3, 2]

Pop -> returns 2 (from out_stack, no transfer needed):
  out_stack: [3]
```

**Python Solution**:

```python
class MyQueue:
    def __init__(self):
        self.in_stack = []
        self.out_stack = []

    def push(self, x):
        self.in_stack.append(x)

    def pop(self):
        self._transfer()
        return self.out_stack.pop()

    def peek(self):
        self._transfer()
        return self.out_stack[-1]

    def empty(self):
        return not self.in_stack and not self.out_stack

    def _transfer(self):
        if not self.out_stack:
            while self.in_stack:
                self.out_stack.append(self.in_stack.pop())


# Test
q = MyQueue()
q.push(1)
q.push(2)
print(q.peek())   # Output: 1
print(q.pop())    # Output: 1
print(q.empty())  # Output: False
```

**Java Solution**:

```java
import java.util.Stack;

class MyQueue {
    private Stack<Integer> inStack;
    private Stack<Integer> outStack;

    public MyQueue() {
        inStack = new Stack<>();
        outStack = new Stack<>();
    }

    public void push(int x) {
        inStack.push(x);
    }

    public int pop() {
        transfer();
        return outStack.pop();
    }

    public int peek() {
        transfer();
        return outStack.peek();
    }

    public boolean empty() {
        return inStack.isEmpty() && outStack.isEmpty();
    }

    private void transfer() {
        if (outStack.isEmpty()) {
            while (!inStack.isEmpty()) {
                outStack.push(inStack.pop());
            }
        }
    }
}
```

**Complexity**: Push is O(1). Pop and peek are **amortized O(1)** -- each element is moved at most twice (once into `in_stack`, once into `out_stack`). Space: O(n).

---

### Problem 2: Moving Average from Data Stream (LeetCode 346)

**Problem**: Given a stream of integers, calculate the moving average of the last `k` numbers.

**Approach**: Use a queue of size `k`. As new numbers arrive, add them to the queue. If the queue exceeds size `k`, remove the oldest number. Maintain a running sum for O(1) average calculation.

```
Window size k = 3

Stream: 1, 10, 3, 5

Step 1: Add 1    -> Queue: [1]        Sum: 1    Avg: 1/1 = 1.0
Step 2: Add 10   -> Queue: [1,10]     Sum: 11   Avg: 11/2 = 5.5
Step 3: Add 3    -> Queue: [1,10,3]   Sum: 14   Avg: 14/3 = 4.667
Step 4: Add 5    -> Queue: [10,3,5]   Sum: 18   Avg: 18/3 = 6.0
                    (1 removed)
```

**Python Solution**:

```python
from collections import deque

class MovingAverage:
    def __init__(self, size):
        self.size = size
        self.queue = deque()
        self.total = 0

    def next(self, val):
        self.queue.append(val)
        self.total += val

        if len(self.queue) > self.size:
            removed = self.queue.popleft()
            self.total -= removed

        return self.total / len(self.queue)


# Test
ma = MovingAverage(3)
print(ma.next(1))   # Output: 1.0
print(ma.next(10))  # Output: 5.5
print(ma.next(3))   # Output: 4.666...
print(ma.next(5))   # Output: 6.0
```

**Java Solution**:

```java
import java.util.LinkedList;
import java.util.Queue;

class MovingAverage {
    private int size;
    private Queue<Integer> queue;
    private double total;

    public MovingAverage(int size) {
        this.size = size;
        this.queue = new LinkedList<>();
        this.total = 0;
    }

    public double next(int val) {
        queue.offer(val);
        total += val;

        if (queue.size() > size) {
            total -= queue.poll();
        }

        return total / queue.size();
    }
}
```

**Complexity**: Time: O(1) per call. Space: O(k) where k is the window size.

---

### Problem 3: Number of Recent Calls (LeetCode 933)

**Problem**: Implement a `RecentCounter` class that counts the number of calls made within the last 3000 milliseconds (inclusive).

**Approach**: Maintain a queue of timestamps. When a new call arrives at time `t`, add `t` to the queue. Then remove all timestamps older than `t - 3000` from the front. The queue size is the answer.

```
ping(1):     Queue: [1]           -> 1 call in [1-3000, 1] = [0, 1]
ping(100):   Queue: [1, 100]      -> 2 calls in [0, 100]
ping(3001):  Queue: [1, 100, 3001] -> 3 calls in [1, 3001]
ping(3002):  Queue: [100, 3001, 3002] -> 3 calls in [2, 3002]
             (1 removed because 1 < 3002-3000 = 2)
```

**Python Solution**:

```python
from collections import deque

class RecentCounter:
    def __init__(self):
        self.queue = deque()

    def ping(self, t):
        self.queue.append(t)
        while self.queue[0] < t - 3000:
            self.queue.popleft()
        return len(self.queue)


# Test
rc = RecentCounter()
print(rc.ping(1))     # Output: 1
print(rc.ping(100))   # Output: 2
print(rc.ping(3001))  # Output: 3
print(rc.ping(3002))  # Output: 3
```

**Java Solution**:

```java
import java.util.LinkedList;
import java.util.Queue;

class RecentCounter {
    private Queue<Integer> queue;

    public RecentCounter() {
        queue = new LinkedList<>();
    }

    public int ping(int t) {
        queue.offer(t);
        while (queue.peek() < t - 3000) {
            queue.poll();
        }
        return queue.size();
    }
}
```

**Complexity**: Time: Amortized O(1) per call (each timestamp is added and removed at most once). Space: O(W) where W is the number of calls within any 3000ms window.

---

## What Is Next?

You now understand how queues manage data in FIFO order and how deques extend this with double-ended access. In the next chapter, we dive into **Hash Tables** -- a data structure that achieves near-magical O(1) average-case lookups by using hash functions to map keys directly to their storage locations. Hash tables power Python dictionaries, Java HashMaps, and are behind some of the most commonly asked interview questions.
