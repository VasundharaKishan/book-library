# Chapter 5: Linked Lists

## What You Will Learn

- What a linked list is and how it differs from an array
- How to build a Node class and a singly linked list from scratch
- How to insert, delete, search, and reverse a linked list with ASCII diagrams showing every pointer change
- Doubly linked lists and circular linked lists
- When to use a linked list versus an array
- How to solve classic problems: reverse a linked list, detect a cycle (Floyd's algorithm), merge two sorted lists, and find the middle node

## Why This Chapter Matters

Linked lists are the first data structure that breaks away from contiguous memory. Understanding them forces you to think about **pointers** (references) -- a concept that underpins trees, graphs, and most advanced data structures. Linked list problems are interview staples because they test your ability to manipulate references without getting confused. If you can reverse a linked list cleanly, you can handle pointer manipulation anywhere.

---

## 5.1 What Is a Linked List?

A linked list is like a **treasure hunt** where each clue points to the next one. Instead of storing elements side by side in memory (like an array), each element (called a **node**) stores its value *and* a reference to the next node.

```
    ARRAY: Elements stored side by side
    +---+---+---+---+---+
    | 1 | 2 | 3 | 4 | 5 |
    +---+---+---+---+---+
    Contiguous memory. Access any by index.

    LINKED LIST: Elements scattered, connected by pointers
    +---+---+    +---+---+    +---+---+    +---+---+    +---+------+
    | 1 | *-+--->| 2 | *-+--->| 3 | *-+--->| 4 | *-+--->| 5 | None |
    +---+---+    +---+---+    +---+---+    +---+---+    +---+------+
    head                                                   tail

    Each box has two parts:
    [data | next pointer]

    The last node's pointer is None/null (end of the list).
```

### Key Properties

1. **No contiguous memory required.** Nodes can be anywhere in memory.
2. **No random access.** To get the 5th element, you must follow 5 pointers. No shortcut.
3. **Efficient insertion/deletion.** Adding or removing a node just changes pointers -- no shifting required.
4. **Dynamic size.** Grows and shrinks as needed, no resizing.

---

## 5.2 The Node Class

Every linked list is built from nodes. A node stores two things: data and a pointer to the next node.

**Python**:
```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None    # Points to the next node (or None)

    def __repr__(self):
        return f"Node({self.data})"

# Create three nodes manually
a = Node(1)
b = Node(2)
c = Node(3)

# Link them together
a.next = b
b.next = c

# Traverse
current = a
while current:
    print(current.data, end=" -> ")
    current = current.next
print("None")
# Output: 1 -> 2 -> 3 -> None
```

**Java**:
```java
public class Node {
    int data;
    Node next;

    public Node(int data) {
        this.data = data;
        this.next = null;
    }

    public static void main(String[] args) {
        Node a = new Node(1);
        Node b = new Node(2);
        Node c = new Node(3);

        a.next = b;
        b.next = c;

        // Traverse
        Node current = a;
        while (current != null) {
            System.out.print(current.data + " -> ");
            current = current.next;
        }
        System.out.println("null");
        // Output: 1 -> 2 -> 3 -> null
    }
}
```

**Output**:
```
1 -> 2 -> 3 -> None
```

---

## 5.3 Singly Linked List: Full Implementation

### Building the LinkedList Class

**Python**:
```python
class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def is_empty(self):
        return self.head is None

    # --- INSERT OPERATIONS ---

    def insert_at_head(self, data):
        """O(1) -- add to the front."""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def insert_at_tail(self, data):
        """O(n) -- must traverse to the end."""
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    # --- DELETE OPERATIONS ---

    def delete_at_head(self):
        """O(1) -- remove from the front."""
        if self.head is None:
            return None
        data = self.head.data
        self.head = self.head.next
        self.size -= 1
        return data

    def delete_by_value(self, value):
        """O(n) -- find and remove."""
        if self.head is None:
            return False

        if self.head.data == value:
            self.head = self.head.next
            self.size -= 1
            return True

        current = self.head
        while current.next:
            if current.next.data == value:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        return False

    # --- SEARCH ---

    def search(self, value):
        """O(n) -- linear search."""
        current = self.head
        index = 0
        while current:
            if current.data == value:
                return index
            current = current.next
            index += 1
        return -1

    # --- REVERSE ---

    def reverse(self):
        """O(n) time, O(1) space -- reverse in place."""
        prev = None
        current = self.head
        while current:
            next_node = current.next   # Save next
            current.next = prev        # Reverse pointer
            prev = current             # Move prev forward
            current = next_node        # Move current forward
        self.head = prev

    # --- DISPLAY ---

    def display(self):
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        print(" -> ".join(elements) + " -> None")

# Test
ll = LinkedList()
ll.insert_at_head(3)
ll.insert_at_head(2)
ll.insert_at_head(1)
ll.insert_at_tail(4)
ll.insert_at_tail(5)
ll.display()  # Output: 1 -> 2 -> 3 -> 4 -> 5 -> None

print(f"Search 3: index {ll.search(3)}")  # Output: Search 3: index 2
print(f"Search 9: index {ll.search(9)}")  # Output: Search 9: index -1

ll.delete_by_value(3)
ll.display()  # Output: 1 -> 2 -> 4 -> 5 -> None

ll.reverse()
ll.display()  # Output: 5 -> 4 -> 2 -> 1 -> None
```

**Java**:
```java
public class LinkedList {
    private Node head;
    private int size;

    public LinkedList() {
        this.head = null;
        this.size = 0;
    }

    public void insertAtHead(int data) {
        Node newNode = new Node(data);
        newNode.next = head;
        head = newNode;
        size++;
    }

    public void insertAtTail(int data) {
        Node newNode = new Node(data);
        if (head == null) {
            head = newNode;
        } else {
            Node current = head;
            while (current.next != null) current = current.next;
            current.next = newNode;
        }
        size++;
    }

    public boolean deleteByValue(int value) {
        if (head == null) return false;
        if (head.data == value) {
            head = head.next;
            size--;
            return true;
        }
        Node current = head;
        while (current.next != null) {
            if (current.next.data == value) {
                current.next = current.next.next;
                size--;
                return true;
            }
            current = current.next;
        }
        return false;
    }

    public void reverse() {
        Node prev = null;
        Node current = head;
        while (current != null) {
            Node nextNode = current.next;
            current.next = prev;
            prev = current;
            current = nextNode;
        }
        head = prev;
    }

    public void display() {
        Node current = head;
        while (current != null) {
            System.out.print(current.data + " -> ");
            current = current.next;
        }
        System.out.println("null");
    }

    public static void main(String[] args) {
        LinkedList ll = new LinkedList();
        ll.insertAtHead(3);
        ll.insertAtHead(2);
        ll.insertAtHead(1);
        ll.insertAtTail(4);
        ll.insertAtTail(5);
        ll.display();  // 1 -> 2 -> 3 -> 4 -> 5 -> null

        ll.deleteByValue(3);
        ll.display();  // 1 -> 2 -> 4 -> 5 -> null

        ll.reverse();
        ll.display();  // 5 -> 4 -> 2 -> 1 -> null
    }
}
```

**Output**:
```
1 -> 2 -> 3 -> 4 -> 5 -> None
Search 3: index 2
Search 9: index -1
1 -> 2 -> 4 -> 5 -> None
5 -> 4 -> 2 -> 1 -> None
```

---

## 5.4 Pointer Manipulation: Detailed Walkthroughs

### Insert at Head

```
    Before: head -> [2] -> [3] -> None

    Step 1: Create new node [1]
            new_node = Node(1)
            [1] -> None

    Step 2: Point new node's next to current head
            new_node.next = head
            [1] -> [2] -> [3] -> None

    Step 3: Update head to new node
            head = new_node
    head -> [1] -> [2] -> [3] -> None
```

### Delete a Middle Node

```
    Before: head -> [1] -> [2] -> [3] -> [4] -> None
    Delete value 3

    Step 1: Find the node BEFORE the target
            current = [2] (because current.next.data == 3)

    Step 2: Skip over the target node
            current.next = current.next.next

    Before:  [1] -> [2] -> [3] -> [4] -> None
                      |              ^
                      +--------------+  (new connection)

    After:   [1] -> [2] ---------> [4] -> None
             [3] is disconnected and will be garbage collected
```

### Reverse a Linked List (Step by Step)

```
    Reverse: 1 -> 2 -> 3 -> None

    Initial state:
    prev = None
    curr = [1] -> [2] -> [3] -> None

    --- Iteration 1 ---
    next_node = curr.next = [2]
    curr.next = prev = None
    prev = curr = [1]
    curr = next_node = [2]

    State: None <- [1]    [2] -> [3] -> None
           prev           curr

    --- Iteration 2 ---
    next_node = curr.next = [3]
    curr.next = prev = [1]
    prev = curr = [2]
    curr = next_node = [3]

    State: None <- [1] <- [2]    [3] -> None
                          prev   curr

    --- Iteration 3 ---
    next_node = curr.next = None
    curr.next = prev = [2]
    prev = curr = [3]
    curr = next_node = None

    State: None <- [1] <- [2] <- [3]    None
                                 prev   curr

    curr is None --> loop ends
    head = prev = [3]

    Result: 3 -> 2 -> 1 -> None
```

---

## 5.5 Doubly Linked List

In a doubly linked list, each node has pointers to both the next *and* the previous node. This allows traversal in both directions.

```
    DOUBLY LINKED LIST

    None <-- +---+---+---+ <--> +---+---+---+ <--> +---+---+---+ --> None
             | P | 1 | N |      | P | 2 | N |      | P | 3 | N |
             +---+---+---+      +---+---+---+      +---+---+---+
    head ->                                                        <- tail

    P = prev pointer, N = next pointer
    Each node knows its predecessor AND successor.
```

**Python**:
```python
class DNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_at_tail(self, data):
        new_node = DNode(data)
        if self.tail is None:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

    def insert_at_head(self, data):
        new_node = DNode(data)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node

    def delete_node(self, node):
        """O(1) -- delete a node when you have a reference to it."""
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

    def display_forward(self):
        current = self.head
        parts = []
        while current:
            parts.append(str(current.data))
            current = current.next
        print("None <-> " + " <-> ".join(parts) + " <-> None")

    def display_backward(self):
        current = self.tail
        parts = []
        while current:
            parts.append(str(current.data))
            current = current.prev
        print("None <-> " + " <-> ".join(parts) + " <-> None")

# Test
dll = DoublyLinkedList()
dll.insert_at_tail(1)
dll.insert_at_tail(2)
dll.insert_at_tail(3)
dll.display_forward()   # Output: None <-> 1 <-> 2 <-> 3 <-> None
dll.display_backward()  # Output: None <-> 3 <-> 2 <-> 1 <-> None
```

**Output**:
```
None <-> 1 <-> 2 <-> 3 <-> None
None <-> 3 <-> 2 <-> 1 <-> None
```

### When to Use Doubly Linked Lists

- When you need to traverse in both directions
- When you need O(1) deletion given a reference to the node (no need to find the previous node)
- Implementing LRU Cache (a very common interview problem)
- Browser forward/back navigation

---

## 5.6 Circular Linked List

In a circular linked list, the last node points back to the first node instead of None/null.

```
    CIRCULAR SINGLY LINKED LIST

    +-> [1] -> [2] -> [3] -> [4] --+
    |                               |
    +-------------------------------+

    There is no "end" -- following next from any node
    eventually brings you back to where you started.

    CIRCULAR DOUBLY LINKED LIST

    +<--> [1] <--> [2] <--> [3] <--> [4] <-->+
    |                                          |
    +------------------------------------------+
```

**Use cases**: Round-robin scheduling, circular buffers, multiplayer game turn order.

---

## 5.7 Array vs Linked List Comparison

| Operation | Array | Linked List |
|---|---|---|
| Access by index | **O(1)** | O(n) |
| Search by value | O(n) | O(n) |
| Insert at beginning | O(n) | **O(1)** |
| Insert at end | O(1) amortized | O(n) singly, **O(1)** with tail |
| Insert in middle | O(n) | **O(1)** if you have the node |
| Delete at beginning | O(n) | **O(1)** |
| Delete at end | O(1) | O(n) singly, **O(1)** doubly |
| Delete in middle | O(n) | **O(1)** if you have the node |
| Memory usage | Compact | Extra space for pointers |
| Cache performance | **Excellent** (contiguous) | Poor (scattered) |

**Rule of thumb**: Use arrays when you need fast access by index and cache-friendly iteration. Use linked lists when you need frequent insertion/deletion at arbitrary positions and do not need random access.

---

## 5.8 Problem: Reverse a Linked List

**Problem**: Reverse a singly linked list.

**Example**: 1 -> 2 -> 3 -> 4 -> 5 -> None becomes 5 -> 4 -> 3 -> 2 -> 1 -> None

### Iterative Approach -- O(n) time, O(1) space

**Python**:
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head):
    prev = None
    current = head

    while current:
        next_node = current.next  # Save next
        current.next = prev       # Reverse pointer
        prev = current            # Advance prev
        current = next_node       # Advance current

    return prev  # prev is the new head

# Helper: create list from array
def create_list(arr):
    if not arr:
        return None
    head = ListNode(arr[0])
    current = head
    for val in arr[1:]:
        current.next = ListNode(val)
        current = current.next
    return head

# Helper: print list
def print_list(head):
    parts = []
    while head:
        parts.append(str(head.val))
        head = head.next
    print(" -> ".join(parts) + " -> None")

# Test
head = create_list([1, 2, 3, 4, 5])
print_list(head)                    # Output: 1 -> 2 -> 3 -> 4 -> 5 -> None
reversed_head = reverse_list(head)
print_list(reversed_head)           # Output: 5 -> 4 -> 3 -> 2 -> 1 -> None
```

**Java**:
```java
public class ReverseLinkedList {
    public static ListNode reverseList(ListNode head) {
        ListNode prev = null;
        ListNode current = head;

        while (current != null) {
            ListNode nextNode = current.next;
            current.next = prev;
            prev = current;
            current = nextNode;
        }
        return prev;
    }
}
```

**Output**:
```
1 -> 2 -> 3 -> 4 -> 5 -> None
5 -> 4 -> 3 -> 2 -> 1 -> None
```

**Complexity**: Time O(n), Space O(1).

### Recursive Approach -- O(n) time, O(n) space

```python
def reverse_list_recursive(head):
    # Base case: empty list or single node
    if head is None or head.next is None:
        return head

    # Reverse the rest of the list
    new_head = reverse_list_recursive(head.next)

    # head.next is now the LAST node of the reversed sublist
    # Make it point back to head
    head.next.next = head
    head.next = None

    return new_head
```

```
    Recursive reversal of 1 -> 2 -> 3 -> None

    Call stack:
    reverse(1->2->3)
      reverse(2->3)
        reverse(3)  --> returns 3 (base case)
      head=2, head.next=3, so 3.next=2, 2.next=None
      Result: 3->2->None, return 3
    head=1, head.next=2, so 2.next=1, 1.next=None
    Result: 3->2->1->None, return 3
```

---

## 5.9 Problem: Detect Cycle (Floyd's Tortoise and Hare)

**Problem**: Given a linked list, determine if it has a cycle (a node's next pointer points to an earlier node).

```
    List with a cycle:

    1 -> 2 -> 3 -> 4 -> 5
                   ^         |
                   |         v
                   8 <- 7 <- 6

    Node 5 points to node 3, creating a cycle.
    Following next from any node loops forever.
```

### Floyd's Algorithm

Use two pointers: a **slow** pointer (moves 1 step) and a **fast** pointer (moves 2 steps). If there is a cycle, they will eventually meet. If there is no cycle, fast will reach the end.

```
    Floyd's Cycle Detection

    1 -> 2 -> 3 -> 4 -> 5 -> 3 (cycle back to 3)

    Step 0: slow=1, fast=1
    Step 1: slow=2, fast=3
    Step 2: slow=3, fast=5
    Step 3: slow=4, fast=4   <-- They meet! Cycle detected.

    Why does this work?
    If there is a cycle, fast "laps" slow.
    In each step, the gap between them shrinks by 1.
    They MUST eventually meet.
```

**Python**:
```python
def has_cycle(head):
    """Floyd's Tortoise and Hare -- O(n) time, O(1) space."""
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next          # Move 1 step
        fast = fast.next.next     # Move 2 steps
        if slow == fast:
            return True

    return False  # fast reached the end -- no cycle

# Test
# Create a cycle: 1 -> 2 -> 3 -> 4 -> 2 (cycle)
node1 = ListNode(1)
node2 = ListNode(2)
node3 = ListNode(3)
node4 = ListNode(4)
node1.next = node2
node2.next = node3
node3.next = node4
node4.next = node2  # Cycle!

print(has_cycle(node1))  # Output: True

# No cycle
head = create_list([1, 2, 3, 4, 5])
print(has_cycle(head))   # Output: False
```

**Java**:
```java
public class DetectCycle {
    public static boolean hasCycle(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;

        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) return true;
        }
        return false;
    }
}
```

**Output**:
```
True
False
```

**Complexity**: Time O(n), Space O(1). This is far better than using a hash set (O(n) space).

---

## 5.10 Problem: Merge Two Sorted Lists

**Problem**: Merge two sorted linked lists into one sorted list.

```
    list1: 1 -> 3 -> 5 -> None
    list2: 2 -> 4 -> 6 -> None

    Compare heads:
    1 < 2  --> take 1, advance list1
    2 < 3  --> take 2, advance list2
    3 < 4  --> take 3, advance list1
    4 < 5  --> take 4, advance list2
    5 < 6  --> take 5, advance list1
    list1 is empty, append rest of list2 (6)

    Result: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> None
```

**Python**:
```python
def merge_two_lists(l1, l2):
    """O(n + m) time, O(1) space (reuse existing nodes)."""
    dummy = ListNode(0)  # Dummy head to simplify logic
    current = dummy

    while l1 and l2:
        if l1.val <= l2.val:
            current.next = l1
            l1 = l1.next
        else:
            current.next = l2
            l2 = l2.next
        current = current.next

    # Attach the remaining nodes
    current.next = l1 if l1 else l2

    return dummy.next  # Skip the dummy head

# Test
l1 = create_list([1, 3, 5])
l2 = create_list([2, 4, 6])
merged = merge_two_lists(l1, l2)
print_list(merged)  # Output: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> None

l1 = create_list([])
l2 = create_list([1, 2, 3])
merged = merge_two_lists(l1, l2)
print_list(merged)  # Output: 1 -> 2 -> 3 -> None
```

**Java**:
```java
public class MergeSortedLists {
    public static ListNode mergeTwoLists(ListNode l1, ListNode l2) {
        ListNode dummy = new ListNode(0);
        ListNode current = dummy;

        while (l1 != null && l2 != null) {
            if (l1.val <= l2.val) {
                current.next = l1;
                l1 = l1.next;
            } else {
                current.next = l2;
                l2 = l2.next;
            }
            current = current.next;
        }
        current.next = (l1 != null) ? l1 : l2;
        return dummy.next;
    }
}
```

**Output**:
```
1 -> 2 -> 3 -> 4 -> 5 -> 6 -> None
1 -> 2 -> 3 -> None
```

**Complexity**: Time O(n + m), Space O(1).

The **dummy node** technique is a pattern you will see repeatedly. It eliminates special-case handling for the head of the result list.

---

## 5.11 Problem: Find the Middle Node

**Problem**: Given a linked list, find its middle node. If there are two middle nodes, return the second one.

### Slow and Fast Pointer Technique

```
    1 -> 2 -> 3 -> 4 -> 5 -> None

    slow moves 1 step, fast moves 2 steps:
    Step 0: slow=1, fast=1
    Step 1: slow=2, fast=3
    Step 2: slow=3, fast=5
    Step 3: fast.next is None --> stop

    slow is at 3 -- the middle!

    Even length: 1 -> 2 -> 3 -> 4 -> None
    Step 0: slow=1, fast=1
    Step 1: slow=2, fast=3
    Step 2: slow=3, fast=None (fast went past end)
    slow is at 3 -- the second middle node
```

**Python**:
```python
def find_middle(head):
    """O(n) time, O(1) space."""
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    return slow

# Test
head = create_list([1, 2, 3, 4, 5])
print(find_middle(head).val)  # Output: 3

head = create_list([1, 2, 3, 4])
print(find_middle(head).val)  # Output: 3 (second middle)
```

**Java**:
```java
public class MiddleNode {
    public static ListNode middleNode(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;

        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        return slow;
    }
}
```

**Output**:
```
3
3
```

**Complexity**: Time O(n), Space O(1). The slow/fast pointer pattern is one of the most useful linked list techniques.

---

## Common Mistakes

1. **Losing the head reference.** If you move `head` forward during traversal, you lose access to the start of the list. Use a separate `current` variable.
2. **Not handling None/null.** Always check if `head` is None before accessing `head.next`. Always check `current.next` before accessing `current.next.next`.
3. **Forgetting to update the head after reversal.** After reversing, `prev` is the new head, not the original `head`.
4. **Creating cycles accidentally.** When manipulating pointers, forgetting to set the old tail's next to None creates an unintended cycle.
5. **Off-by-one in the dummy node pattern.** Remember to return `dummy.next`, not `dummy`.

## Best Practices

1. **Use a dummy node** when building a new list. It eliminates special-case code for the first node.
2. **Draw the pointer changes.** Before writing code, sketch the before and after states for each pointer operation.
3. **Use slow/fast pointers** for middle-finding, cycle detection, and finding the nth-from-end node.
4. **Test with edge cases**: empty list (None), single node, two nodes, and lists with cycles.
5. **Consider using a tail pointer** for singly linked lists if you frequently insert at the end. It reduces O(n) to O(1).

---

## Quick Summary

A linked list stores elements in nodes connected by pointers, allowing O(1) insertion and deletion at known positions but requiring O(n) for access and search. Singly linked lists have one pointer per node; doubly linked lists have two (next and prev). The slow/fast pointer technique solves multiple problems: finding the middle, detecting cycles, and finding the nth node from the end. The dummy node pattern simplifies list construction. Linked lists trade cache performance and random access for flexible, efficient insertion and deletion.

## Key Points

- **Linked lists** use nodes with data + pointer(s), stored non-contiguously in memory.
- **Access is O(n)** (must traverse), but **insertion/deletion at a known node is O(1)**.
- **Reversing** requires three pointers: prev, current, next. The key is saving `current.next` before overwriting it.
- **Floyd's cycle detection** uses slow (1 step) and fast (2 steps) pointers. If they meet, there is a cycle.
- **Merge two sorted lists** using a dummy node and comparing heads.
- **Find the middle** using slow/fast pointers -- when fast reaches the end, slow is at the middle.
- **Doubly linked lists** allow O(1) deletion given a node reference and bidirectional traversal.

---

## Practice Questions

1. What is the advantage of a linked list over an array? When would you choose an array instead?

2. Trace through the reversal of the list 10 -> 20 -> 30 -> 40 -> None. Show the values of prev, current, and next_node at each step.

3. Why does Floyd's cycle detection algorithm guarantee that the slow and fast pointers will meet if a cycle exists? (Hint: think about the relative speed difference.)

4. You need to implement an LRU (Least Recently Used) cache. Which type of linked list would you use, and why?

5. Given a singly linked list, how would you find the kth node from the end in one pass? (Hint: use two pointers with a gap of k.)

---

## LeetCode-Style Problems

### Problem 1: Remove Nth Node from End (Medium)

**Problem**: Remove the nth node from the end of a linked list and return the head.

**Example**: 1 -> 2 -> 3 -> 4 -> 5, n = 2 -> 1 -> 2 -> 3 -> 5

```
    Use two pointers with a gap of n:

    dummy -> 1 -> 2 -> 3 -> 4 -> 5 -> None
    ^                             ^
    slow                         fast  (fast is n+1 ahead of slow)

    Move both until fast reaches None:
    dummy -> 1 -> 2 -> 3 -> 4 -> 5 -> None
                        ^              ^
                       slow           fast

    slow.next = slow.next.next  (skip node 4)
```

**Python**:
```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0)
    dummy.next = head
    slow = dummy
    fast = dummy

    # Move fast n+1 steps ahead
    for _ in range(n + 1):
        fast = fast.next

    # Move both until fast reaches end
    while fast:
        slow = slow.next
        fast = fast.next

    # Skip the target node
    slow.next = slow.next.next

    return dummy.next

# Test
head = create_list([1, 2, 3, 4, 5])
result = remove_nth_from_end(head, 2)
print_list(result)  # Output: 1 -> 2 -> 3 -> 5 -> None
```

**Java**:
```java
public class RemoveNthFromEnd {
    public static ListNode removeNthFromEnd(ListNode head, int n) {
        ListNode dummy = new ListNode(0);
        dummy.next = head;
        ListNode slow = dummy, fast = dummy;

        for (int i = 0; i <= n; i++) fast = fast.next;

        while (fast != null) {
            slow = slow.next;
            fast = fast.next;
        }
        slow.next = slow.next.next;
        return dummy.next;
    }
}
```

**Output**:
```
1 -> 2 -> 3 -> 5 -> None
```

**Complexity**: Time O(n), Space O(1). One pass through the list.

---

### Problem 2: Linked List Cycle II -- Find Cycle Start (Medium)

**Problem**: Given a linked list with a cycle, find the node where the cycle begins.

**Python**:
```python
def detect_cycle_start(head):
    """Floyd's algorithm extended -- O(n) time, O(1) space."""
    slow = head
    fast = head

    # Phase 1: Detect cycle
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None  # No cycle

    # Phase 2: Find the start of the cycle
    # Move one pointer back to head, keep the other at meeting point
    # Both move one step at a time -- they meet at the cycle start
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next

    return slow

# Test
node1 = ListNode(1)
node2 = ListNode(2)
node3 = ListNode(3)
node4 = ListNode(4)
node1.next = node2
node2.next = node3
node3.next = node4
node4.next = node2  # Cycle starts at node2

start = detect_cycle_start(node1)
print(f"Cycle starts at node with value: {start.val}")
# Output: Cycle starts at node with value: 2
```

**Output**:
```
Cycle starts at node with value: 2
```

**Complexity**: Time O(n), Space O(1).

---

### Problem 3: Palindrome Linked List (Easy)

**Problem**: Determine if a singly linked list is a palindrome.

**Example**: 1 -> 2 -> 2 -> 1 -> None is a palindrome.

**Python**:
```python
def is_palindrome_list(head):
    """O(n) time, O(1) space -- reverse second half and compare."""
    if not head or not head.next:
        return True

    # Step 1: Find middle using slow/fast
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    # Step 2: Reverse second half
    second_half = reverse_list(slow.next)

    # Step 3: Compare first and second half
    first_half = head
    while second_half:
        if first_half.val != second_half.val:
            return False
        first_half = first_half.next
        second_half = second_half.next

    return True

# Test
print(is_palindrome_list(create_list([1, 2, 2, 1])))     # Output: True
print(is_palindrome_list(create_list([1, 2, 3, 2, 1])))  # Output: True
print(is_palindrome_list(create_list([1, 2, 3])))         # Output: False
```

**Output**:
```
True
True
False
```

**Complexity**: Time O(n), Space O(1). Combines three techniques: find middle, reverse, and compare.

---

## What Is Next?

In Chapter 6, you will learn about **Stacks** -- a data structure that enforces Last-In-First-Out (LIFO) ordering. Stacks are used everywhere: the undo button in your editor, the back button in your browser, and how your computer manages function calls. You will implement stacks using both arrays and linked lists, and solve classic problems like valid parentheses and the monotonic stack pattern.
