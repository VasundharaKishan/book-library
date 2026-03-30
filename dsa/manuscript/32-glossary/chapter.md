# Chapter 32: Glossary

## What You Will Learn

- Concise definitions for 80+ data structure and algorithm terms
- Quick-reference explanations you can revisit before interviews
- Connections between related concepts
- A self-test tool: if you can explain every term here, you have mastered this book

## Why This Chapter Matters

This glossary serves two purposes. First, it is a quick reference when you encounter an unfamiliar term while solving problems. Second, it is a self-assessment tool. Skim through the list. If any term makes you pause, revisit the relevant chapter. If you can explain every term from memory, you are ready.

---

## Terms A-B

**Adjacency List**
A graph representation where each vertex stores a list of its neighbors. Uses O(V + E) space. More efficient than an adjacency matrix for sparse graphs. See Chapter 17.

**Adjacency Matrix**
A 2D array where `matrix[i][j] = 1` (or a weight) if there is an edge from vertex i to vertex j. Uses O(V^2) space. Efficient for dense graphs or when you need O(1) edge lookup. See Chapter 17.

**Amortized Analysis**
A technique for analyzing the average time per operation over a sequence of operations. Individual operations may be expensive, but the average cost per operation is low. Example: dynamic array resizing is O(1) amortized even though occasional resizes are O(n). See Chapter 3.

**Array**
A contiguous block of memory storing elements of the same type. Access by index is O(1). Insertion/deletion at arbitrary positions is O(n) due to shifting. The most fundamental data structure. See Chapter 3.

**AVL Tree**
A self-balancing binary search tree where the heights of the left and right subtrees of any node differ by at most 1. Guarantees O(log n) for search, insert, and delete. Rebalances using rotations after each modification. See Chapter 14.

**Backtracking**
An algorithmic technique that builds solutions incrementally and abandons (prunes) partial solutions that cannot lead to valid complete solutions. Used for combinatorial problems like permutations, subsets, N-Queens, and Sudoku. See Chapter 23.

**BFS (Breadth-First Search)**
A graph/tree traversal algorithm that explores all neighbors at the current depth before moving to the next depth level. Uses a queue. Guarantees the shortest path in unweighted graphs. Time O(V + E). See Chapter 18.

**Big O Notation**
A mathematical notation describing the upper bound of an algorithm's growth rate. O(n) means the time grows linearly with input size. O(1) means constant time. Used to compare algorithm efficiency independently of hardware. See Chapter 2.

**Binary Search**
An algorithm that finds a target value in a sorted array by repeatedly dividing the search space in half. Time O(log n). Requires the input to be sorted or the search space to be monotonic. See Chapter 12.

**Binary Tree**
A tree where each node has at most two children, called left and right. The foundation for BSTs, heaps, and expression trees. See Chapter 13.

**Bit Manipulation**
Techniques for operating directly on the binary representation of numbers using bitwise operators (AND, OR, XOR, NOT, shift). Enables O(1) tricks for checking parity, counting bits, and finding unique elements. See Chapter 28.

**BST (Binary Search Tree)**
A binary tree where for every node, all values in the left subtree are smaller and all values in the right subtree are larger. Enables O(log n) search, insert, and delete when balanced. See Chapter 14.

**Bucket Sort**
A sorting algorithm that distributes elements into buckets, sorts each bucket individually, then concatenates the results. Time O(n + k) where k is the number of buckets. Efficient when elements are uniformly distributed. See Chapter 11.

---

## Terms C-D

**Cache**
A storage layer that keeps frequently accessed data for fast retrieval. In algorithms, caching (memoization) stores computed results to avoid redundant calculations. LRU cache is a common implementation using a hash map + doubly linked list.

**Collision**
In a hash table, when two different keys hash to the same index. Resolved by chaining (linked lists at each index) or open addressing (probing for the next empty slot). See Chapter 8.

**Complete Binary Tree**
A binary tree where every level is fully filled except possibly the last, which is filled from left to right. Heaps are always complete binary trees. See Chapter 16.

**Connected Component**
A maximal set of vertices in an undirected graph such that every pair of vertices is connected by a path. Found using BFS, DFS, or Union-Find. See Chapters 18, 27.

**Cycle**
A path in a graph that starts and ends at the same vertex. In directed graphs, cycles prevent topological sorting. In linked lists, cycles cause infinite traversal. Detected using DFS (back edges) or Floyd's algorithm (fast/slow pointers). See Chapters 18, 25.

**DAG (Directed Acyclic Graph)**
A directed graph with no cycles. DAGs support topological sorting and are used to model dependencies (build systems, course prerequisites, task scheduling). See Chapter 19.

**Deque (Double-Ended Queue)**
A data structure that supports insertion and deletion at both ends in O(1) time. Used in sliding window maximum (monotonic deque) and BFS optimizations. See Chapter 7.

**DFS (Depth-First Search)**
A graph/tree traversal algorithm that explores as far as possible along each branch before backtracking. Uses recursion or a stack. Time O(V + E). Used for connectivity, cycle detection, topological sort, and pathfinding. See Chapter 18.

**Dijkstra's Algorithm**
A shortest-path algorithm for graphs with non-negative edge weights. Uses a priority queue (min heap) to greedily process the nearest unvisited vertex. Time O((V + E) log V) with a binary heap. See Chapter 19.

**Divide and Conquer**
An algorithm design paradigm that breaks a problem into smaller subproblems, solves each recursively, then combines the results. Examples: merge sort, quick sort, binary search. See Chapters 11, 12.

**Dynamic Programming (DP)**
An optimization technique for problems with overlapping subproblems and optimal substructure. Solves each subproblem once and stores the result (memoization or tabulation). Examples: Fibonacci, coin change, knapsack. See Chapters 20, 21.

---

## Terms E-G

**Edge**
A connection between two vertices in a graph. Can be directed (one-way) or undirected (two-way). Can have weights representing costs, distances, or capacities. See Chapter 17.

**Graph**
A data structure consisting of vertices (nodes) and edges (connections). Can be directed or undirected, weighted or unweighted. Represented using adjacency lists or adjacency matrices. See Chapter 17.

**Greedy Algorithm**
An algorithm that makes the locally optimal choice at each step, hoping to find the globally optimal solution. Works when the problem has the greedy-choice property. Examples: activity selection, Huffman coding, Dijkstra's algorithm. See Chapter 22.

---

## Terms H-I

**Hash Function**
A function that maps data of arbitrary size to a fixed-size value (hash code). A good hash function distributes keys uniformly across the hash table to minimize collisions. See Chapter 8.

**Hash Map (Hash Table)**
A data structure that stores key-value pairs with O(1) average-case insert, delete, and lookup. Uses a hash function to compute the index for each key. Handles collisions via chaining or open addressing. See Chapter 8.

**Heap**
A complete binary tree that satisfies the heap property: in a min heap, every parent is smaller than or equal to its children; in a max heap, every parent is larger. The root is always the minimum (or maximum). Supports insert and extract in O(log n). See Chapter 16.

**In-order Traversal**
A binary tree traversal that visits the left subtree, then the node, then the right subtree (Left-Node-Right). For BSTs, in-order traversal produces elements in sorted order. See Chapter 15.

---

## Terms K-L

**Knapsack Problem**
A classic optimization problem: given items with weights and values, maximize value without exceeding a weight limit. The 0/1 knapsack (each item used once) is solved with DP in O(n * W). The unbounded knapsack (unlimited copies) uses a similar approach. See Chapter 21.

**Linked List**
A linear data structure where each element (node) contains data and a pointer to the next node. Supports O(1) insertion/deletion at known positions but O(n) access by index. Variants: singly linked, doubly linked, circular. See Chapter 5.

---

## Terms M-N

**Memoization**
A top-down DP technique where recursive function results are cached (stored) to avoid redundant computation. Typically uses a hash map or array. Contrast with tabulation (bottom-up). See Chapter 20.

**Merge Sort**
A divide-and-conquer sorting algorithm. Recursively split the array in half, sort each half, then merge the sorted halves. Time O(n log n) guaranteed. Space O(n). Stable sort. See Chapter 11.

**Min Heap**
A heap where the parent is always less than or equal to its children. The root contains the minimum element. Used to implement priority queues. Extract-min and insert both run in O(log n). See Chapter 16.

**Monotonic Stack**
A stack that maintains elements in a strictly increasing or decreasing order. Used to efficiently find the next greater/smaller element for each position in an array. Each element is pushed and popped at most once, giving O(n) total time. See Chapter 29.

**Node**
A fundamental unit in data structures like linked lists, trees, and graphs. Contains data and references (pointers) to other nodes. In a tree, each node has at most one parent and zero or more children.

**NP (Nondeterministic Polynomial)**
A complexity class of problems whose solutions can be verified in polynomial time. NP-complete problems (like the Traveling Salesman Problem) have no known polynomial-time algorithm. Understanding NP-hardness helps recognize when an exact solution is impractical and approximation is needed.

---

## Terms O-P

**O(n)**
Linear time complexity. The algorithm's running time grows proportionally with the input size. Example: scanning every element in an array once. See Chapter 2.

**Path**
A sequence of vertices connected by edges in a graph. A simple path visits each vertex at most once. The shortest path is the path with minimum total edge weight (or minimum edge count in unweighted graphs). See Chapter 19.

**Pointer**
A variable that stores the memory address of another variable or object. In linked lists, pointers connect nodes. In two-pointer techniques, "pointer" refers to an index variable used to traverse a data structure. See Chapters 5, 25.

**Prefix Sum**
A precomputed array where `prefix[i]` stores the sum of elements from index 0 to i. Enables O(1) range sum queries: `sum(l, r) = prefix[r] - prefix[l-1]`. See Chapter 29.

**Pre-order Traversal**
A binary tree traversal that visits the node first, then the left subtree, then the right subtree (Node-Left-Right). Used for tree serialization and creating copies of trees. See Chapter 15.

**Post-order Traversal**
A binary tree traversal that visits the left subtree, then the right subtree, then the node (Left-Right-Node). Used for deleting trees and evaluating expression trees. See Chapter 15.

**Priority Queue**
An abstract data type where each element has a priority and the element with the highest (or lowest) priority is served first. Typically implemented with a heap. Used in Dijkstra's algorithm, Huffman coding, and task scheduling. See Chapter 16.

---

## Terms Q-R

**Queue**
A linear data structure following FIFO (First In, First Out) order. Elements are added at the rear (enqueue) and removed from the front (dequeue). Used in BFS, task scheduling, and buffering. See Chapter 7.

**Quick Sort**
A divide-and-conquer sorting algorithm that selects a pivot, partitions elements into those less than and greater than the pivot, then recursively sorts each partition. Average time O(n log n), worst case O(n^2). In-place. See Chapter 11.

**Recursion**
A technique where a function calls itself to solve a smaller instance of the same problem. Requires a base case (to stop) and a recursive case (to reduce). The call stack tracks active function calls. See Chapter 9.

---

## Terms S

**Sliding Window**
A technique for processing subarrays or substrings by maintaining a window (range) that slides across the data. The window expands from the right and shrinks from the left. Converts O(n * k) brute-force approaches to O(n). See Chapter 24.

**Sort**
The process of arranging elements in a defined order (ascending or descending). Common algorithms: bubble sort O(n^2), insertion sort O(n^2), merge sort O(n log n), quick sort O(n log n) average, heap sort O(n log n). See Chapters 10, 11.

**Stack**
A linear data structure following LIFO (Last In, First Out) order. Elements are added (push) and removed (pop) from the top. Used in DFS, expression evaluation, undo operations, and backtracking. See Chapter 6.

**Subarray**
A contiguous portion of an array. `[2, 3, 4]` is a subarray of `[1, 2, 3, 4, 5]`, but `[1, 3, 5]` is not (not contiguous). Important distinction from subsequence.

**Subsequence**
A sequence derived from another sequence by deleting some or no elements without changing the order of the remaining elements. `[1, 3, 5]` is a subsequence of `[1, 2, 3, 4, 5]`. Does not need to be contiguous. See Chapter 21.

---

## Terms T

**Tabulation**
A bottom-up DP technique that fills a table iteratively, starting from the smallest subproblems. Avoids recursion overhead. Contrast with memoization (top-down). See Chapter 20.

**Topological Sort**
A linear ordering of vertices in a DAG such that for every directed edge (u, v), u appears before v. Used for dependency resolution (build systems, course scheduling). Implemented using DFS or Kahn's algorithm (BFS with in-degrees). See Chapter 19.

**Tree**
A connected acyclic graph. One node is designated as the root. Each non-root node has exactly one parent. Trees with n nodes have exactly n-1 edges. Variants: binary tree, BST, AVL tree, trie, B-tree. See Chapter 13.

**Trie (Prefix Tree)**
A tree-like data structure where each path from root to a marked node represents a word. Each node stores children for each character. Supports O(m) insert, search, and prefix matching where m is the word length. Used in autocomplete and spell checkers. See Chapter 26.

**Two Pointers**
A technique using two index variables to traverse a data structure. Variants: opposite direction (converging from both ends), same direction (reader/writer), fast/slow (cycle detection). Reduces O(n^2) to O(n) for many problems. See Chapter 25.

---

## Terms U-V

**Union-Find (Disjoint Set Union / DSU)**
A data structure for managing non-overlapping sets with two operations: Find (which set does an element belong to?) and Union (merge two sets). With path compression and union by rank, operations run in O(alpha(n)) amortized time --- effectively O(1). See Chapter 27.

**Vertex (Node)**
A fundamental unit in a graph. Also called a node. Connected to other vertices by edges. Each vertex can store data and has properties like degree (number of edges), in-degree, and out-degree (for directed graphs). See Chapter 17.

---

## Terms W-X

**XOR (Exclusive OR)**
A bitwise operator that returns 1 when bits differ and 0 when they are the same. Key properties: `a ^ a = 0`, `a ^ 0 = a`, commutative and associative. Used to find unique elements (Single Number), swap without temp, and toggle bits. See Chapter 28.

---

## Self-Test Checklist

Go through this list and rate yourself on each term: "Can I explain this to a beginner in 30 seconds?"

```
[ ] Adjacency List        [ ] Memoization
[ ] Adjacency Matrix       [ ] Merge Sort
[ ] Amortized Analysis     [ ] Min Heap
[ ] Array                  [ ] Monotonic Stack
[ ] AVL Tree               [ ] Node
[ ] Backtracking           [ ] NP
[ ] BFS                    [ ] O(n)
[ ] Big O Notation         [ ] Path
[ ] Binary Search          [ ] Pointer
[ ] Binary Tree            [ ] Prefix Sum
[ ] Bit Manipulation       [ ] Pre-order Traversal
[ ] BST                    [ ] Post-order Traversal
[ ] Bucket Sort            [ ] Priority Queue
[ ] Cache                  [ ] Queue
[ ] Collision              [ ] Quick Sort
[ ] Complete Binary Tree   [ ] Recursion
[ ] Connected Component    [ ] Sliding Window
[ ] Cycle                  [ ] Sort
[ ] DAG                    [ ] Stack
[ ] Deque                  [ ] Subarray
[ ] DFS                    [ ] Subsequence
[ ] Dijkstra's Algorithm   [ ] Tabulation
[ ] Divide and Conquer     [ ] Topological Sort
[ ] Dynamic Programming    [ ] Tree
[ ] Edge                   [ ] Trie
[ ] Graph                  [ ] Two Pointers
[ ] Greedy Algorithm       [ ] Union-Find
[ ] Hash Function          [ ] Vertex
[ ] Hash Map               [ ] XOR
[ ] Heap
[ ] In-order Traversal
[ ] Knapsack Problem
[ ] Linked List
```

---

## Congratulations

You have made it to the end of "Data Structures and Algorithms: A Complete Guide."

Take a moment to appreciate how far you have come. You started with the basics --- what an array is, what Big O means --- and built your way up through linked lists, trees, graphs, dynamic programming, and beyond. You learned 10 core algorithm patterns, practiced 50 essential problems, and developed a systematic approach to technical interviews.

Here is what you now know:

- **Data structures** are the building blocks: arrays, linked lists, stacks, queues, hash maps, trees, graphs, heaps, tries, and Union-Find.
- **Algorithms** are the strategies: sorting, searching, BFS, DFS, dynamic programming, greedy, backtracking, and bit manipulation.
- **Patterns** are the shortcuts: Two Pointers, Sliding Window, Binary Search, Monotonic Stack, and Prefix Sum.
- **Problem-solving** is the skill: Clarify, Plan, Code, Test.

### What to Do Next

1. **Practice consistently.** Solve 2-3 problems per day for the next 4-8 weeks. Use the 50-problem list in Chapter 31 as your starting point.

2. **Do mock interviews.** Practice with a partner or use online platforms. The difference between solo practice and mock interviews is enormous.

3. **Build projects.** Apply data structures in real software: implement a search engine (tries + hash maps), build a social network feature (graphs + Union-Find), or create a task scheduler (heaps + topological sort).

4. **Teach others.** The best way to solidify your understanding is to explain concepts to someone else. Write blog posts, mentor a beginner, or record tutorial videos.

5. **Stay curious.** This book covers the fundamentals, but the field is vast. Explore advanced topics like segment trees, Fenwick trees, suffix arrays, network flow, and approximation algorithms when you are ready.

### A Final Thought

Algorithms are not just interview tricks. They are tools for thinking clearly about problems. The ability to break a complex challenge into subproblems, recognize patterns, and build systematic solutions is valuable far beyond coding interviews. It is the foundation of engineering.

You have invested significant time and effort to reach this point. That investment will pay dividends throughout your career --- in interviews, in building software, and in solving problems that do not yet have names.

Good luck. You are ready.
