# Chapter 6: Stacks

## What You Will Learn

- What a stack is and how LIFO (Last-In, First-Out) ordering works
- The four core operations: push, pop, peek, and isEmpty
- How to implement a stack using an array and a linked list
- How the call stack powers recursion
- How to solve classic problems: valid parentheses, min stack, evaluate reverse polish notation, and daily temperatures
- The monotonic stack pattern and when to use it

## Why This Chapter Matters

Stacks are deceptively simple -- push and pop, that is it. But this simplicity unlocks an enormous range of problems. The "undo" button in every text editor is a stack. The back button in your browser is a stack. Every function call your program makes uses a stack. In interviews, stack problems test whether you can recognize when LIFO ordering solves a problem that seems complex at first. The monotonic stack pattern alone appears in dozens of interview questions.

---

## 6.1 What Is a Stack?

A stack is like a **stack of plates** in a cafeteria. You can only add a plate to the top or remove a plate from the top. The plate you put on last is the first one you take off. This is called **LIFO: Last-In, First-Out**.

```
    STACK OF PLATES

    Push A, B, C, D:

    +---+
    | D |  <-- Top (most recently added)
    +---+
    | C |
    +---+
    | B |
    +---+
    | A |  <-- Bottom (first added)
    +---+

    Pop: removes D (the top)
    Pop: removes C (the new top)
    Pop: removes B
    Pop: removes A (stack is now empty)

    LIFO: Last In, First Out
    The LAST item pushed is the FIRST item popped.
```

### Real-World Stacks

| Example | Push | Pop |
|---|---|---|
| Plates in a cafeteria | Add plate on top | Take plate from top |
| Undo history | Perform action | Undo last action |
| Browser back button | Visit new page | Go back to previous page |
| Function calls | Call a function | Return from function |
| Pringles can | Put chip in | Take chip out |

---

## 6.2 The Four Core Operations

Every stack supports exactly four operations:

```
    +----------------------------------------------------------+
    | Operation  | Description              | Time Complexity  |
    +----------------------------------------------------------+
    | push(item) | Add item to the top      | O(1)             |
    | pop()      | Remove and return top     | O(1)             |
    | peek()     | Look at top without       | O(1)             |
    |            | removing it               |                  |
    | isEmpty()  | Check if stack is empty   | O(1)             |
    +----------------------------------------------------------+

    All operations are O(1) -- constant time!
```

```
    PUSH and POP walkthrough:

    push(10)     push(20)     push(30)     pop()        pop()
    +----+       +----+       +----+       +----+       +----+
    |    |       |    |       | 30 | <-top |    |       |    |
    +----+       +----+       +----+       +----+       +----+
    |    |       | 20 | <-top | 20 |       | 20 | <-top |    |
    +----+       +----+       +----+       +----+       +----+
    | 10 | <-top | 10 |       | 10 |       | 10 |       | 10 | <-top
    +----+       +----+       +----+       +----+       +----+

    pop() returned 30          pop() returned 20
```

---

## 6.3 Array-Based Stack Implementation

The simplest stack uses an array (or dynamic list). The top of the stack is the end of the array.

**Python**:
```python
class ArrayStack:
    def __init__(self):
        self.items = []

    def push(self, item):
        """O(1) amortized -- append to end."""
        self.items.append(item)

    def pop(self):
        """O(1) -- remove from end."""
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        return self.items.pop()

    def peek(self):
        """O(1) -- look at end without removing."""
        if self.is_empty():
            raise IndexError("Peek at empty stack")
        return self.items[-1]

    def is_empty(self):
        """O(1)."""
        return len(self.items) == 0

    def size(self):
        """O(1)."""
        return len(self.items)

    def __str__(self):
        return f"Stack(top -> {list(reversed(self.items))})"

# Test
stack = ArrayStack()
stack.push(10)
stack.push(20)
stack.push(30)
print(stack)              # Output: Stack(top -> [30, 20, 10])
print(f"Peek: {stack.peek()}")     # Output: Peek: 30
print(f"Pop: {stack.pop()}")       # Output: Pop: 30
print(f"Pop: {stack.pop()}")       # Output: Pop: 20
print(f"Size: {stack.size()}")     # Output: Size: 1
print(f"Empty: {stack.is_empty()}")# Output: Empty: False
print(f"Pop: {stack.pop()}")       # Output: Pop: 10
print(f"Empty: {stack.is_empty()}")# Output: Empty: True
```

**Java**:
```java
import java.util.ArrayList;

public class ArrayStack<T> {
    private ArrayList<T> items;

    public ArrayStack() {
        items = new ArrayList<>();
    }

    public void push(T item) {
        items.add(item); // O(1) amortized
    }

    public T pop() {
        if (isEmpty()) throw new RuntimeException("Pop from empty stack");
        return items.remove(items.size() - 1); // O(1)
    }

    public T peek() {
        if (isEmpty()) throw new RuntimeException("Peek at empty stack");
        return items.get(items.size() - 1); // O(1)
    }

    public boolean isEmpty() {
        return items.isEmpty();
    }

    public int size() {
        return items.size();
    }

    public static void main(String[] args) {
        ArrayStack<Integer> stack = new ArrayStack<>();
        stack.push(10);
        stack.push(20);
        stack.push(30);
        System.out.println("Peek: " + stack.peek()); // 30
        System.out.println("Pop: " + stack.pop());   // 30
        System.out.println("Pop: " + stack.pop());   // 20
        System.out.println("Size: " + stack.size()); // 1
        System.out.println("Empty: " + stack.isEmpty()); // false
    }
}
```

**Output**:
```
Stack(top -> [30, 20, 10])
Peek: 30
Pop: 30
Pop: 20
Size: 1
Empty: False
Pop: 10
Empty: True
```

**Note**: In practice, Python programmers use a plain `list` as a stack (`append` for push, `pop()` for pop). Java programmers use `java.util.Deque` (specifically `ArrayDeque`) rather than the legacy `java.util.Stack` class.

---

## 6.4 Linked-List-Based Stack Implementation

A stack can also be built using a linked list. The top of the stack is the head of the list.

```
    Linked List Stack:

    top -> [30] -> [20] -> [10] -> None

    push(40):
    top -> [40] -> [30] -> [20] -> [10] -> None

    pop():  removes [40], returns 40
    top -> [30] -> [20] -> [10] -> None
```

**Python**:
```python
class StackNode:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedStack:
    def __init__(self):
        self.top = None
        self._size = 0

    def push(self, item):
        """O(1) -- insert at head."""
        new_node = StackNode(item)
        new_node.next = self.top
        self.top = new_node
        self._size += 1

    def pop(self):
        """O(1) -- remove from head."""
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        data = self.top.data
        self.top = self.top.next
        self._size -= 1
        return data

    def peek(self):
        """O(1) -- look at head."""
        if self.is_empty():
            raise IndexError("Peek at empty stack")
        return self.top.data

    def is_empty(self):
        return self.top is None

    def size(self):
        return self._size

# Test
stack = LinkedStack()
stack.push(10)
stack.push(20)
stack.push(30)
print(f"Peek: {stack.peek()}")   # Output: Peek: 30
print(f"Pop: {stack.pop()}")     # Output: Pop: 30
print(f"Size: {stack.size()}")   # Output: Size: 2
```

**Java**:
```java
public class LinkedStack<T> {
    private static class StackNode<T> {
        T data;
        StackNode<T> next;
        StackNode(T data) { this.data = data; }
    }

    private StackNode<T> top;
    private int size;

    public void push(T item) {
        StackNode<T> newNode = new StackNode<>(item);
        newNode.next = top;
        top = newNode;
        size++;
    }

    public T pop() {
        if (isEmpty()) throw new RuntimeException("Pop from empty stack");
        T data = top.data;
        top = top.next;
        size--;
        return data;
    }

    public T peek() {
        if (isEmpty()) throw new RuntimeException("Peek at empty stack");
        return top.data;
    }

    public boolean isEmpty() { return top == null; }
    public int size() { return size; }
}
```

**Output**:
```
Peek: 30
Pop: 30
Size: 2
```

### Array vs Linked List Stack

| Feature | Array-Based | Linked-List-Based |
|---|---|---|
| Push/Pop time | O(1) amortized | O(1) always |
| Memory | Compact, may waste capacity | Extra pointer per node |
| Cache performance | Better (contiguous) | Worse (scattered) |
| Resize overhead | Occasional O(n) resize | None |
| Typical choice | Preferred in practice | When strict O(1) needed |

---

## 6.5 The Call Stack: How Recursion Works

Every time your program calls a function, the computer pushes a **stack frame** onto the **call stack**. When the function returns, its frame is popped. This is why recursion works -- and why infinite recursion causes a "stack overflow."

```
    THE CALL STACK

    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n - 1)

    factorial(4)

    Call Stack Growth:
    +------------------+
    | factorial(1) = 1 |  <-- base case reached, start returning
    +------------------+
    | factorial(2)     |  --> 2 * factorial(1) = 2 * 1 = 2
    +------------------+
    | factorial(3)     |  --> 3 * factorial(2) = 3 * 2 = 6
    +------------------+
    | factorial(4)     |  --> 4 * factorial(3) = 4 * 6 = 24
    +------------------+
    | main()           |
    +------------------+

    The stack GROWS as functions are called.
    The stack SHRINKS as functions return.
    Each frame stores: function parameters, local variables, return address.
```

**Python**:
```python
def factorial(n, depth=0):
    indent = "  " * depth
    print(f"{indent}factorial({n}) called")

    if n <= 1:
        print(f"{indent}factorial({n}) returns 1")
        return 1

    result = n * factorial(n - 1, depth + 1)
    print(f"{indent}factorial({n}) returns {result}")
    return result

print(f"Result: {factorial(4)}")
```

**Output**:
```
factorial(4) called
  factorial(3) called
    factorial(2) called
      factorial(1) called
      factorial(1) returns 1
    factorial(2) returns 2
  factorial(3) returns 6
factorial(4) returns 24
Result: 24
```

### Stack Overflow

If recursion never reaches a base case, the call stack grows until the system runs out of memory:

```python
def infinite_recursion(n):
    return infinite_recursion(n + 1)  # No base case!

# infinite_recursion(1)
# --> RecursionError: maximum recursion depth exceeded
# Python default limit: ~1000 frames
# Java default: depends on JVM, typically ~5000-10000 frames
```

---

## 6.6 Problem: Valid Parentheses

**Problem**: Given a string containing only `(`, `)`, `{`, `}`, `[`, `]`, determine if the input string is valid. A string is valid if:
1. Open brackets are closed by the same type of brackets.
2. Open brackets are closed in the correct order.

**Example**: "({[]})" is valid. "([)]" is NOT valid.

```
    Walkthrough for "({[]})"

    Character: (    Stack: [(]                Push matching closer
    Character: {    Stack: [(, {]             Push matching closer
    Character: [    Stack: [(, {, []          Push matching closer
    Character: ]    Stack: [(, {]             ] matches [  Pop!
    Character: }    Stack: [(]               } matches {  Pop!
    Character: )    Stack: []                ) matches (  Pop!
    End: Stack is empty --> VALID!

    Walkthrough for "([)]"

    Character: (    Stack: [(]
    Character: [    Stack: [(, []
    Character: )    Stack: [(, []  ) does NOT match [  --> INVALID!
```

**Python**:
```python
def is_valid(s):
    stack = []
    matching = {')': '(', '}': '{', ']': '['}

    for char in s:
        if char in matching:
            # It is a closing bracket
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()
        else:
            # It is an opening bracket
            stack.append(char)

    return len(stack) == 0  # Stack must be empty

# Test
print(is_valid("()"))         # Output: True
print(is_valid("()[]{}"))     # Output: True
print(is_valid("(]"))         # Output: False
print(is_valid("([)]"))       # Output: False
print(is_valid("{[]}"))       # Output: True
print(is_valid(""))           # Output: True
print(is_valid("(("))         # Output: False
```

**Java**:
```java
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;

public class ValidParentheses {
    public static boolean isValid(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        Map<Character, Character> matching = Map.of(
            ')', '(', '}', '{', ']', '['
        );

        for (char c : s.toCharArray()) {
            if (matching.containsKey(c)) {
                if (stack.isEmpty() || stack.peek() != matching.get(c)) {
                    return false;
                }
                stack.pop();
            } else {
                stack.push(c);
            }
        }
        return stack.isEmpty();
    }

    public static void main(String[] args) {
        System.out.println(isValid("()"));      // true
        System.out.println(isValid("()[]{}"));  // true
        System.out.println(isValid("(]"));      // false
        System.out.println(isValid("([)]"));    // false
        System.out.println(isValid("{[]}"));    // true
    }
}
```

**Output**:
```
True
True
False
False
True
True
False
```

**Complexity**: Time O(n), Space O(n).

---

## 6.7 Problem: Min Stack

**Problem**: Design a stack that supports push, pop, peek, and retrieving the minimum element, **all in O(1) time**.

```
    The trick: maintain a SECOND stack that tracks the minimum.

    Operations:        Main Stack:    Min Stack:
    push(5)            [5]            [5]         min=5
    push(3)            [5, 3]         [5, 3]      min=3
    push(7)            [5, 3, 7]      [5, 3, 3]   min=3 (3 is still min)
    push(1)            [5, 3, 7, 1]   [5, 3, 3, 1] min=1
    pop() -> 1         [5, 3, 7]      [5, 3, 3]   min=3
    getMin() -> 3
    pop() -> 7         [5, 3]         [5, 3]      min=3
    getMin() -> 3
```

**Python**:
```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []  # Tracks minimum at each level

    def push(self, val):
        self.stack.append(val)
        # Push the new minimum (compare with current min)
        if self.min_stack:
            self.min_stack.append(min(val, self.min_stack[-1]))
        else:
            self.min_stack.append(val)

    def pop(self):
        self.stack.pop()
        self.min_stack.pop()

    def top(self):
        return self.stack[-1]

    def get_min(self):
        return self.min_stack[-1]

# Test
ms = MinStack()
ms.push(-2)
ms.push(0)
ms.push(-3)
print(f"Min: {ms.get_min()}")   # Output: Min: -3
ms.pop()
print(f"Top: {ms.top()}")       # Output: Top: 0
print(f"Min: {ms.get_min()}")   # Output: Min: -2
```

**Java**:
```java
import java.util.ArrayDeque;
import java.util.Deque;

public class MinStack {
    private Deque<Integer> stack;
    private Deque<Integer> minStack;

    public MinStack() {
        stack = new ArrayDeque<>();
        minStack = new ArrayDeque<>();
    }

    public void push(int val) {
        stack.push(val);
        if (minStack.isEmpty()) {
            minStack.push(val);
        } else {
            minStack.push(Math.min(val, minStack.peek()));
        }
    }

    public void pop() {
        stack.pop();
        minStack.pop();
    }

    public int top() {
        return stack.peek();
    }

    public int getMin() {
        return minStack.peek();
    }

    public static void main(String[] args) {
        MinStack ms = new MinStack();
        ms.push(-2);
        ms.push(0);
        ms.push(-3);
        System.out.println("Min: " + ms.getMin()); // -3
        ms.pop();
        System.out.println("Top: " + ms.top());    // 0
        System.out.println("Min: " + ms.getMin()); // -2
    }
}
```

**Output**:
```
Min: -3
Top: 0
Min: -2
```

**Complexity**: All operations are O(1) time. Space O(n) for the second stack.

---

## 6.8 Problem: Evaluate Reverse Polish Notation

**Problem**: Evaluate an arithmetic expression in Reverse Polish Notation (postfix). Valid operators are +, -, *, /. Each operand is an integer.

**Example**: ["2", "1", "+", "3", "*"] evaluates to 9 because ((2 + 1) * 3 = 9).

```
    Walkthrough: ["2", "1", "+", "3", "*"]

    Token: "2"    Stack: [2]            Push number
    Token: "1"    Stack: [2, 1]         Push number
    Token: "+"    Stack: [3]            Pop 1 and 2, push 2+1=3
    Token: "3"    Stack: [3, 3]         Push number
    Token: "*"    Stack: [9]            Pop 3 and 3, push 3*3=9

    Result: 9
```

**Python**:
```python
def eval_rpn(tokens):
    stack = []

    for token in tokens:
        if token in "+-*/":
            b = stack.pop()  # Second operand (popped first!)
            a = stack.pop()  # First operand

            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                # Truncate toward zero (not floor division)
                stack.append(int(a / b))
        else:
            stack.append(int(token))

    return stack[0]

# Test
print(eval_rpn(["2", "1", "+", "3", "*"]))               # Output: 9
print(eval_rpn(["4", "13", "5", "/", "+"]))               # Output: 6
print(eval_rpn(["10", "6", "9", "3", "+", "-11", "*",
                "/", "*", "17", "+", "5", "+"]))           # Output: 22
```

**Java**:
```java
import java.util.ArrayDeque;
import java.util.Deque;

public class EvalRPN {
    public static int evalRPN(String[] tokens) {
        Deque<Integer> stack = new ArrayDeque<>();

        for (String token : tokens) {
            if ("+-*/".contains(token) && token.length() == 1) {
                int b = stack.pop();
                int a = stack.pop();

                switch (token) {
                    case "+": stack.push(a + b); break;
                    case "-": stack.push(a - b); break;
                    case "*": stack.push(a * b); break;
                    case "/": stack.push(a / b); break;
                }
            } else {
                stack.push(Integer.parseInt(token));
            }
        }
        return stack.peek();
    }

    public static void main(String[] args) {
        System.out.println(evalRPN(new String[]{"2","1","+","3","*"}));  // 9
        System.out.println(evalRPN(new String[]{"4","13","5","/","+"})); // 6
    }
}
```

**Output**:
```
9
6
22
```

**Complexity**: Time O(n), Space O(n). Each token is processed once.

**Important detail**: When you pop two operands, the *first* popped value is the *second* operand (b), and the *second* popped value is the *first* operand (a). Getting this wrong flips subtraction and division.

---

## 6.9 Problem: Daily Temperatures

**Problem**: Given an array of daily temperatures, return an array where each element tells you how many days you have to wait for a warmer temperature. If there is no future warmer day, put 0.

**Example**: [73, 74, 75, 71, 69, 72, 76, 73] -> [1, 1, 4, 2, 1, 1, 0, 0]

### Brute Force -- O(n^2)

For each day, scan forward to find the next warmer day.

### Monotonic Stack -- O(n)

Use a stack to keep track of indices of temperatures we have not yet found a warmer day for. When we encounter a warmer temperature, pop all the indices with lower temperatures.

```
    Walkthrough: [73, 74, 75, 71, 69, 72, 76, 73]
    Stack stores INDICES (not temperatures)

    i=0, temp=73: Stack empty, push 0.         Stack: [0]
    i=1, temp=74: 74 > 73(stack top)
                  Pop 0, answer[0] = 1-0 = 1
                  Push 1.                       Stack: [1]
    i=2, temp=75: 75 > 74(stack top)
                  Pop 1, answer[1] = 2-1 = 1
                  Push 2.                       Stack: [2]
    i=3, temp=71: 71 < 75, push 3.             Stack: [2, 3]
    i=4, temp=69: 69 < 71, push 4.             Stack: [2, 3, 4]
    i=5, temp=72: 72 > 69, pop 4, answer[4]=1
                  72 > 71, pop 3, answer[3]=2
                  72 < 75, push 5.              Stack: [2, 5]
    i=6, temp=76: 76 > 72, pop 5, answer[5]=1
                  76 > 75, pop 2, answer[2]=4
                  Push 6.                       Stack: [6]
    i=7, temp=73: 73 < 76, push 7.             Stack: [6, 7]

    Remaining in stack: indices 6 and 7 have no warmer day -> answer stays 0

    Answer: [1, 1, 4, 2, 1, 1, 0, 0]
```

**Python**:
```python
def daily_temperatures(temperatures):
    n = len(temperatures)
    answer = [0] * n
    stack = []  # Stack of indices

    for i in range(n):
        # While current temp is warmer than temp at stack top
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev_index = stack.pop()
            answer[prev_index] = i - prev_index
        stack.append(i)

    return answer

# Test
print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))
# Output: [1, 1, 4, 2, 1, 1, 0, 0]

print(daily_temperatures([30, 40, 50, 60]))
# Output: [1, 1, 1, 0]

print(daily_temperatures([30, 20, 10]))
# Output: [0, 0, 0]
```

**Java**:
```java
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;

public class DailyTemperatures {
    public static int[] dailyTemperatures(int[] temperatures) {
        int n = temperatures.length;
        int[] answer = new int[n];
        Deque<Integer> stack = new ArrayDeque<>();

        for (int i = 0; i < n; i++) {
            while (!stack.isEmpty() &&
                   temperatures[i] > temperatures[stack.peek()]) {
                int prevIndex = stack.pop();
                answer[prevIndex] = i - prevIndex;
            }
            stack.push(i);
        }
        return answer;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(
            dailyTemperatures(new int[]{73,74,75,71,69,72,76,73})));
        // Output: [1, 1, 4, 2, 1, 1, 0, 0]
    }
}
```

**Output**:
```
[1, 1, 4, 2, 1, 1, 0, 0]
[1, 1, 1, 0]
[0, 0, 0]
```

**Complexity**: Time O(n), Space O(n). Each index is pushed and popped at most once.

---

## 6.10 Monotonic Stack Pattern Introduction

The Daily Temperatures problem uses a **monotonic stack** -- a stack where elements are always in sorted order (either all increasing or all decreasing from bottom to top).

```
    MONOTONIC DECREASING STACK (temperatures example)

    At any point, the stack (from bottom to top) holds indices
    whose temperatures are in DECREASING order:

    Stack: [75, 71, 69]  (indices 2, 3, 4)
              ^
    Decreasing from bottom to top

    When a new element is LARGER than the top,
    we pop until the stack property is restored.

    This lets us efficiently find the "next greater element"
    for each position.
```

### When to Use a Monotonic Stack

Use a monotonic stack when you need to find, for each element:

- **Next Greater Element**: The first element to the right that is larger.
- **Next Smaller Element**: The first element to the right that is smaller.
- **Previous Greater Element**: The first element to the left that is larger.
- **Previous Smaller Element**: The first element to the left that is smaller.

| Problem Pattern | Stack Type | Direction |
|---|---|---|
| Next Greater Element | Decreasing stack | Left to right |
| Next Smaller Element | Increasing stack | Left to right |
| Previous Greater Element | Decreasing stack | Right to left |
| Previous Smaller Element | Increasing stack | Right to left |

**Python** -- Next Greater Element:
```python
def next_greater_element(nums):
    """For each element, find the next element that is larger."""
    n = len(nums)
    result = [-1] * n  # Default: no greater element
    stack = []  # Monotonic decreasing stack (stores indices)

    for i in range(n):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result

# Test
print(next_greater_element([4, 5, 2, 10, 8]))
# Output: [5, 10, 10, -1, -1]

print(next_greater_element([3, 2, 1]))
# Output: [-1, -1, -1]

print(next_greater_element([1, 2, 3]))
# Output: [2, 3, -1]
```

**Java**:
```java
import java.util.Arrays;
import java.util.ArrayDeque;
import java.util.Deque;

public class NextGreaterElement {
    public static int[] nextGreater(int[] nums) {
        int n = nums.length;
        int[] result = new int[n];
        Arrays.fill(result, -1);
        Deque<Integer> stack = new ArrayDeque<>();

        for (int i = 0; i < n; i++) {
            while (!stack.isEmpty() && nums[i] > nums[stack.peek()]) {
                result[stack.pop()] = nums[i];
            }
            stack.push(i);
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(nextGreater(new int[]{4,5,2,10,8})));
        // Output: [5, 10, 10, -1, -1]
    }
}
```

**Output**:
```
[5, 10, 10, -1, -1]
[-1, -1, -1]
[2, 3, -1]
```

---

## Common Mistakes

1. **Popping from an empty stack.** Always check `is_empty()` before calling `pop()` or `peek()`. This is the most common runtime error in stack problems.
2. **Confusing the order of operands.** In RPN evaluation, the first value popped is the second operand. `a - b` is NOT the same as `b - a`.
3. **Forgetting that the stack stores indices, not values.** In monotonic stack problems, push indices so you can calculate distances. Access values through the original array.
4. **Using a stack when a simpler approach works.** Not every problem needs a stack. If you only need the last element, a variable suffices.
5. **Stack overflow in recursion.** Python limits recursion to ~1000 calls by default. For deep recursion, convert to an iterative approach with an explicit stack.

## Best Practices

1. **Recognize stack problems by their patterns**: matching pairs (parentheses), processing in reverse order (undo), and "next greater/smaller" queries.
2. **Use the language's built-in stack**: Python `list` with `append/pop`, Java `ArrayDeque` with `push/pop/peek`.
3. **Draw the stack state** at each step when solving a problem. This prevents pointer confusion and off-by-one errors.
4. **Convert recursion to iteration** using an explicit stack when recursion depth might exceed the system limit.
5. **Remember that monotonic stacks give O(n) solutions** to problems that seem to require O(n^2) nested loops.

---

## Quick Summary

A stack is a LIFO data structure supporting push, pop, peek, and isEmpty -- all in O(1). It can be implemented with an array (simpler, better cache performance) or a linked list (guaranteed O(1), no resize). The call stack manages function calls and is why recursion works. Valid parentheses is the canonical stack problem: push opening brackets, pop and match closing brackets. The min stack uses a parallel stack to track minimums. Monotonic stacks efficiently solve "next greater/smaller element" problems in O(n) by maintaining sorted order.

## Key Points

- **LIFO (Last-In, First-Out)** is the defining property. The most recently added item is the first removed.
- **All four operations are O(1)**: push, pop, peek, isEmpty.
- **The call stack** is how your computer manages function calls. Each call pushes a frame; each return pops one.
- **Valid Parentheses**: push opening brackets, pop for closing brackets, match types.
- **Min Stack**: use a second stack that tracks the running minimum at each level.
- **RPN Evaluation**: push numbers, pop two operands for operators, push the result.
- **Monotonic stack** finds the next greater (or smaller) element for every position in O(n).
- In monotonic stacks, **store indices** on the stack, not values, so you can calculate distances.

---

## Practice Questions

1. Trace through the valid parentheses algorithm for the string "([{}])". Show the stack state after processing each character.

2. Explain why the call stack has a size limit. What happens when you exceed it, and how can you prevent it?

3. Given a stack with the push sequence [1, 2, 3, 4, 5], is the pop sequence [4, 5, 3, 2, 1] valid? What about [4, 3, 5, 1, 2]? Explain your reasoning.

4. How would you implement a queue using two stacks? (Hint: one stack for enqueue, one for dequeue.)

5. Trace through the daily temperatures problem with input [65, 70, 68, 72, 69, 75]. Show the stack state and the answer array at each step.

---

## LeetCode-Style Problems

### Problem 1: Next Greater Element I (Easy)

**Problem**: You have two arrays `nums1` (a subset of `nums2`). For each element in `nums1`, find its next greater element in `nums2`. If no greater element exists, return -1.

**Example**: nums1 = [4, 1, 2], nums2 = [1, 3, 4, 2] -> [-1, 3, -1]

**Python**:
```python
def next_greater_element_1(nums1, nums2):
    # Build a map of next greater elements for nums2
    next_greater = {}
    stack = []

    for num in nums2:
        while stack and num > stack[-1]:
            next_greater[stack.pop()] = num
        stack.append(num)

    # Remaining elements in stack have no next greater
    while stack:
        next_greater[stack.pop()] = -1

    return [next_greater[num] for num in nums1]

# Test
print(next_greater_element_1([4, 1, 2], [1, 3, 4, 2]))   # Output: [-1, 3, -1]
print(next_greater_element_1([2, 4], [1, 2, 3, 4]))       # Output: [3, -1]
```

**Java**:
```java
import java.util.*;

public class NextGreaterElementI {
    public static int[] nextGreaterElement(int[] nums1, int[] nums2) {
        Map<Integer, Integer> nextGreater = new HashMap<>();
        Deque<Integer> stack = new ArrayDeque<>();

        for (int num : nums2) {
            while (!stack.isEmpty() && num > stack.peek()) {
                nextGreater.put(stack.pop(), num);
            }
            stack.push(num);
        }

        int[] result = new int[nums1.length];
        for (int i = 0; i < nums1.length; i++) {
            result[i] = nextGreater.getOrDefault(nums1[i], -1);
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(
            nextGreaterElement(new int[]{4,1,2}, new int[]{1,3,4,2})));
        // Output: [-1, 3, -1]
    }
}
```

**Output**:
```
[-1, 3, -1]
[3, -1]
```

**Complexity**: Time O(n + m), Space O(n).

---

### Problem 2: Backspace String Compare (Easy)

**Problem**: Given two strings s and t, return true if they are equal when both are typed into empty text editors. The character '#' represents a backspace.

**Example**: s = "ab#c", t = "ad#c" -> true ("ac" == "ac")

**Python**:
```python
def backspace_compare(s, t):
    def process(string):
        stack = []
        for char in string:
            if char == '#':
                if stack:
                    stack.pop()
            else:
                stack.append(char)
        return stack

    return process(s) == process(t)

# Test
print(backspace_compare("ab#c", "ad#c"))      # Output: True ("ac" == "ac")
print(backspace_compare("ab##", "c#d#"))       # Output: True ("" == "")
print(backspace_compare("a##c", "#a#c"))       # Output: True ("c" == "c")
print(backspace_compare("a#c", "b"))           # Output: False ("c" != "b")
```

**Java**:
```java
import java.util.ArrayDeque;
import java.util.Deque;

public class BackspaceCompare {
    private static String process(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        for (char c : s.toCharArray()) {
            if (c == '#') {
                if (!stack.isEmpty()) stack.pop();
            } else {
                stack.push(c);
            }
        }
        return stack.toString();
    }

    public static boolean backspaceCompare(String s, String t) {
        return process(s).equals(process(t));
    }

    public static void main(String[] args) {
        System.out.println(backspaceCompare("ab#c", "ad#c")); // true
        System.out.println(backspaceCompare("ab##", "c#d#")); // true
        System.out.println(backspaceCompare("a#c", "b"));     // false
    }
}
```

**Output**:
```
True
True
True
False
```

**Complexity**: Time O(n + m), Space O(n + m).

---

### Problem 3: Asteroid Collision (Medium)

**Problem**: Given an array of integers representing asteroids in a row. For each asteroid, the absolute value represents its size, and the sign represents its direction (positive = right, negative = left). When two asteroids meet, the smaller one explodes. If both are the same size, both explode. Find the state of the asteroids after all collisions.

**Example**: [5, 10, -5] -> [5, 10] (10 and -5 collide, 10 survives)

**Python**:
```python
def asteroid_collision(asteroids):
    stack = []

    for asteroid in asteroids:
        alive = True

        # Collision happens when: stack top is positive AND current is negative
        while alive and stack and asteroid < 0 < stack[-1]:
            if stack[-1] < abs(asteroid):
                stack.pop()         # Top asteroid explodes
            elif stack[-1] == abs(asteroid):
                stack.pop()         # Both explode
                alive = False
            else:
                alive = False       # Current asteroid explodes

        if alive:
            stack.append(asteroid)

    return stack

# Test
print(asteroid_collision([5, 10, -5]))       # Output: [5, 10]
print(asteroid_collision([8, -8]))           # Output: []
print(asteroid_collision([10, 2, -5]))       # Output: [10]
print(asteroid_collision([-2, -1, 1, 2]))    # Output: [-2, -1, 1, 2]
```

**Java**:
```java
import java.util.*;

public class AsteroidCollision {
    public static int[] asteroidCollision(int[] asteroids) {
        Deque<Integer> stack = new ArrayDeque<>();

        for (int asteroid : asteroids) {
            boolean alive = true;

            while (alive && !stack.isEmpty() && asteroid < 0 && stack.peek() > 0) {
                if (stack.peek() < Math.abs(asteroid)) {
                    stack.pop();
                } else if (stack.peek() == Math.abs(asteroid)) {
                    stack.pop();
                    alive = false;
                } else {
                    alive = false;
                }
            }

            if (alive) stack.push(asteroid);
        }

        int[] result = new int[stack.size()];
        for (int i = result.length - 1; i >= 0; i--) {
            result[i] = stack.pop();
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(Arrays.toString(
            asteroidCollision(new int[]{5, 10, -5})));   // [5, 10]
        System.out.println(Arrays.toString(
            asteroidCollision(new int[]{10, 2, -5})));   // [10]
    }
}
```

**Output**:
```
[5, 10]
[]
[10]
[-2, -1, 1, 2]
```

**Complexity**: Time O(n), Space O(n). Each asteroid is pushed and popped at most once.

---

### Problem 4: Largest Rectangle in Histogram (Hard)

**Problem**: Given an array of integers representing the histogram's bar heights where the width of each bar is 1, find the area of the largest rectangle in the histogram.

**Example**: [2, 1, 5, 6, 2, 3] -> 10 (the rectangle spans bars with heights 5 and 6, width 2)

**Python**:
```python
def largest_rectangle_area(heights):
    """Monotonic stack approach -- O(n)."""
    stack = []  # Stores indices, monotonically increasing heights
    max_area = 0
    heights.append(0)  # Sentinel to flush remaining bars

    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            # Width is from current position to the new stack top
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)

    heights.pop()  # Remove sentinel
    return max_area

# Test
print(largest_rectangle_area([2, 1, 5, 6, 2, 3]))  # Output: 10
print(largest_rectangle_area([2, 4]))                # Output: 4
print(largest_rectangle_area([1]))                   # Output: 1
```

**Java**:
```java
import java.util.ArrayDeque;
import java.util.Deque;

public class LargestRectangle {
    public static int largestRectangleArea(int[] heights) {
        Deque<Integer> stack = new ArrayDeque<>();
        int maxArea = 0;
        int n = heights.length;

        for (int i = 0; i <= n; i++) {
            int h = (i == n) ? 0 : heights[i];
            while (!stack.isEmpty() && heights[stack.peek()] > h) {
                int height = heights[stack.pop()];
                int width = stack.isEmpty() ? i : i - stack.peek() - 1;
                maxArea = Math.max(maxArea, height * width);
            }
            stack.push(i);
        }
        return maxArea;
    }

    public static void main(String[] args) {
        System.out.println(largestRectangleArea(new int[]{2,1,5,6,2,3})); // 10
        System.out.println(largestRectangleArea(new int[]{2,4}));          // 4
    }
}
```

**Output**:
```
10
4
1
```

**Complexity**: Time O(n), Space O(n). Each bar is pushed and popped at most once. This is a classic monotonic stack problem that frequently appears in hard-level interviews.

---

## What Is Next?

In Chapter 7, you will learn about **Queues** -- the counterpart to stacks. While stacks follow Last-In-First-Out, queues follow First-In-First-Out (FIFO), like a line at a coffee shop. You will implement queues with arrays and linked lists, learn about priority queues, and see how queues power Breadth-First Search (BFS) in graphs.
