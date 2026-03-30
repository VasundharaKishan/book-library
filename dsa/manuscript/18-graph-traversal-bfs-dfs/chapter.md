# Chapter 18: Graph Traversal -- BFS and DFS

## What You Will Learn

- How Breadth-First Search (BFS) explores a graph level by level, like ripples spreading in water
- How Depth-First Search (DFS) explores as deep as possible before backtracking, like navigating a maze
- Step-by-step ASCII walkthroughs of both algorithms
- Queue-based BFS implementation
- Stack-based and recursion-based DFS implementations
- The critical role of the visited set in preventing infinite loops
- Applications: connected components, cycle detection, topological sort, and bipartite checking
- How to solve classic problems: number of islands, clone graph, course schedule, and word ladder

## Why This Chapter Matters

A graph is just data sitting in memory until you can **traverse** it. Traversal means visiting every vertex and edge in a systematic way. The two fundamental traversal algorithms -- BFS and DFS -- are the foundation of nearly every graph algorithm.

**BFS** answers questions like: What is the shortest path? What is reachable within k steps? What are the nearest neighbors?

**DFS** answers questions like: Is there a cycle? Can I reach a dead end? What is the dependency order?

Together, they solve an enormous range of problems:
- **Social networks**: Find all friends within 2 degrees of separation (BFS)
- **Web crawling**: Systematically visit every page on a website (BFS or DFS)
- **Maze solving**: Find a path from start to exit (DFS)
- **Build systems**: Determine compilation order (DFS + topological sort)
- **Network analysis**: Find disconnected components (BFS or DFS)

These are not just interview staples -- they are the tools that power real systems you use every day.

---

## 18.1 Breadth-First Search (BFS)

### The Intuition: Ripples in Water

Imagine dropping a stone into a still pond. Ripples spread outward in concentric circles. The closest points to the impact are reached first, then the next ring, then the next.

BFS works the same way. Starting from a source vertex, it visits:
1. All vertices at distance 1 (direct neighbors)
2. Then all vertices at distance 2
3. Then all vertices at distance 3
4. And so on...

This level-by-level exploration guarantees that BFS finds the **shortest path** (in terms of number of edges) from the source to any reachable vertex.

### The Algorithm

```
BFS(graph, start):
    Create a queue and add start to it
    Create a visited set and add start to it

    While queue is not empty:
        Dequeue a vertex v
        Process v
        For each neighbor u of v:
            If u is not visited:
                Mark u as visited
                Enqueue u
```

### Step-by-Step Walkthrough

```
Graph:
    0 --- 1 --- 3
    |     |     |
    2     4     5
          |
          6

BFS from vertex 0:

Step 1: Queue = [0], Visited = {0}
  Dequeue 0. Neighbors: 1, 2.
  Enqueue 1 (new), 2 (new).
  Queue = [1, 2], Visited = {0, 1, 2}

Step 2: Queue = [1, 2]
  Dequeue 1. Neighbors: 0, 3, 4.
  0 already visited. Enqueue 3 (new), 4 (new).
  Queue = [2, 3, 4], Visited = {0, 1, 2, 3, 4}

Step 3: Queue = [2, 3, 4]
  Dequeue 2. Neighbors: 0.
  0 already visited. Nothing to enqueue.
  Queue = [3, 4], Visited = {0, 1, 2, 3, 4}

Step 4: Queue = [3, 4]
  Dequeue 3. Neighbors: 1, 5.
  1 already visited. Enqueue 5 (new).
  Queue = [4, 5], Visited = {0, 1, 2, 3, 4, 5}

Step 5: Queue = [4, 5]
  Dequeue 4. Neighbors: 1, 6.
  1 already visited. Enqueue 6 (new).
  Queue = [5, 6], Visited = {0, 1, 2, 3, 4, 5, 6}

Step 6: Queue = [5, 6]
  Dequeue 5. Neighbors: 3.
  3 already visited. Nothing to enqueue.
  Queue = [6], Visited = {0, 1, 2, 3, 4, 5, 6}

Step 7: Queue = [6]
  Dequeue 6. Neighbors: 4.
  4 already visited. Nothing to enqueue.
  Queue = [], Visited = {0, 1, 2, 3, 4, 5, 6}

Queue empty -> Done!

BFS visit order: 0, 1, 2, 3, 4, 5, 6

Distance from 0:
  0: distance 0
  1, 2: distance 1
  3, 4: distance 2
  5, 6: distance 3
```

### Implementation

**Python:**

```python
from collections import deque, defaultdict


def bfs(graph, start):
    """Perform BFS from start vertex. Returns visit order."""
    visited = set([start])
    queue = deque([start])
    order = []

    while queue:
        vertex = queue.popleft()
        order.append(vertex)

        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


def bfs_with_distance(graph, start):
    """BFS that also tracks shortest distance from start."""
    visited = set([start])
    queue = deque([(start, 0)])
    distances = {start: 0}

    while queue:
        vertex, dist = queue.popleft()

        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                distances[neighbor] = dist + 1
                queue.append((neighbor, dist + 1))

    return distances


# Build graph
graph = defaultdict(list)
edges = [(0,1), (0,2), (1,3), (1,4), (3,5), (4,6)]
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)

print("BFS order from 0:", bfs(graph, 0))
print("Distances from 0:", bfs_with_distance(graph, 0))
```

**Output:**
```
BFS order from 0: [0, 1, 2, 3, 4, 5, 6]
Distances from 0: {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3}
```

**Java:**

```java
import java.util.*;

public class BFS {

    public static List<Integer> bfs(Map<Integer, List<Integer>> graph, int start) {
        List<Integer> order = new ArrayList<>();
        Set<Integer> visited = new HashSet<>();
        Queue<Integer> queue = new LinkedList<>();

        visited.add(start);
        queue.offer(start);

        while (!queue.isEmpty()) {
            int vertex = queue.poll();
            order.add(vertex);

            for (int neighbor : graph.getOrDefault(vertex, Collections.emptyList())) {
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor);
                    queue.offer(neighbor);
                }
            }
        }

        return order;
    }

    public static void main(String[] args) {
        Map<Integer, List<Integer>> graph = new HashMap<>();
        int[][] edges = {{0,1}, {0,2}, {1,3}, {1,4}, {3,5}, {4,6}};

        for (int[] edge : edges) {
            graph.computeIfAbsent(edge[0], k -> new ArrayList<>()).add(edge[1]);
            graph.computeIfAbsent(edge[1], k -> new ArrayList<>()).add(edge[0]);
        }

        System.out.println("BFS from 0: " + bfs(graph, start: 0));
    }
}
```

### BFS Complexity

| Metric | Value | Reason |
|---|---|---|
| Time | O(V + E) | Visit every vertex and examine every edge |
| Space | O(V) | Queue and visited set can hold all vertices |

---

## 18.2 Depth-First Search (DFS)

### The Intuition: Maze Exploration

Imagine exploring a maze. You pick a path and follow it as far as possible. When you hit a dead end, you backtrack to the last junction and try a different path. You keep going until you have explored every reachable passage.

DFS does exactly this. It goes **as deep as possible** along one path before backtracking.

### The Algorithm

```
DFS(graph, start):
    Create a visited set

    def explore(vertex):
        Mark vertex as visited
        Process vertex
        For each neighbor u of vertex:
            If u is not visited:
                explore(u)    # Go deeper

    explore(start)
```

Or iteratively with a stack:

```
DFS_iterative(graph, start):
    Create a stack and push start
    Create a visited set

    While stack is not empty:
        Pop a vertex v
        If v is not visited:
            Mark v as visited
            Process v
            For each neighbor u of v:
                If u is not visited:
                    Push u onto stack
```

### Step-by-Step Walkthrough

```
Graph:
    0 --- 1 --- 3
    |     |     |
    2     4     5
          |
          6

DFS from vertex 0 (recursive, processing neighbors in order):

explore(0): Visit 0. Neighbors: [1, 2].
  explore(1): Visit 1. Neighbors: [0, 3, 4].
    0 visited. Skip.
    explore(3): Visit 3. Neighbors: [1, 5].
      1 visited. Skip.
      explore(5): Visit 5. Neighbors: [3].
        3 visited. Skip.
      Return from 5.
    Return from 3.
    explore(4): Visit 4. Neighbors: [1, 6].
      1 visited. Skip.
      explore(6): Visit 6. Neighbors: [4].
        4 visited. Skip.
      Return from 6.
    Return from 4.
  Return from 1.
  explore(2): Visit 2. Neighbors: [0].
    0 visited. Skip.
  Return from 2.
Return from 0.

DFS visit order: 0, 1, 3, 5, 4, 6, 2

Notice: DFS goes DEEP (0->1->3->5) before backtracking.
        BFS goes WIDE (0, then 1,2, then 3,4, etc.)
```

### Implementation

**Python:**

```python
def dfs_recursive(graph, start, visited=None):
    """Recursive DFS. Returns visit order."""
    if visited is None:
        visited = set()

    visited.add(start)
    order = [start]

    for neighbor in graph[start]:
        if neighbor not in visited:
            order.extend(dfs_recursive(graph, neighbor, visited))

    return order


def dfs_iterative(graph, start):
    """Iterative DFS using a stack."""
    visited = set()
    stack = [start]
    order = []

    while stack:
        vertex = stack.pop()
        if vertex in visited:
            continue
        visited.add(vertex)
        order.append(vertex)

        # Push neighbors in reverse order so we process
        # the first neighbor first (matches recursive behavior)
        for neighbor in reversed(graph[vertex]):
            if neighbor not in visited:
                stack.append(neighbor)

    return order


# Build graph
graph = defaultdict(list)
edges = [(0,1), (0,2), (1,3), (1,4), (3,5), (4,6)]
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)

print("DFS recursive from 0:", dfs_recursive(graph, 0))
print("DFS iterative from 0:", dfs_iterative(graph, 0))
```

**Output:**
```
DFS recursive from 0: [0, 1, 3, 5, 4, 6, 2]
DFS iterative from 0: [0, 1, 3, 5, 4, 6, 2]
```

**Java:**

```java
import java.util.*;

public class DFS {

    public static List<Integer> dfsRecursive(Map<Integer, List<Integer>> graph, int start) {
        List<Integer> order = new ArrayList<>();
        Set<Integer> visited = new HashSet<>();
        dfsHelper(graph, start, visited, order);
        return order;
    }

    private static void dfsHelper(Map<Integer, List<Integer>> graph,
                                   int vertex, Set<Integer> visited,
                                   List<Integer> order) {
        visited.add(vertex);
        order.add(vertex);

        for (int neighbor : graph.getOrDefault(vertex, Collections.emptyList())) {
            if (!visited.contains(neighbor)) {
                dfsHelper(graph, neighbor, visited, order);
            }
        }
    }

    public static List<Integer> dfsIterative(Map<Integer, List<Integer>> graph, int start) {
        List<Integer> order = new ArrayList<>();
        Set<Integer> visited = new HashSet<>();
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(start);

        while (!stack.isEmpty()) {
            int vertex = stack.pop();
            if (visited.contains(vertex)) continue;
            visited.add(vertex);
            order.add(vertex);

            List<Integer> neighbors = graph.getOrDefault(vertex, Collections.emptyList());
            for (int i = neighbors.size() - 1; i >= 0; i--) {
                if (!visited.contains(neighbors.get(i))) {
                    stack.push(neighbors.get(i));
                }
            }
        }

        return order;
    }
}
```

### DFS Complexity

| Metric | Value | Reason |
|---|---|---|
| Time | O(V + E) | Visit every vertex and examine every edge |
| Space | O(V) | Stack (recursion or explicit) and visited set |

---

## 18.3 BFS vs. DFS Comparison

```
BFS (Level by level):          DFS (Go deep, then backtrack):

    0                              0
   / \                            |
  1   2                           1
 / \                             / \
3   4                           3   4
|   |                           |   |
5   6                           5   6
                                    |
Visit: 0,1,2,3,4,5,6              2

Visit: 0,1,3,5,4,6,2
```

| Feature | BFS | DFS |
|---|---|---|
| Data structure | Queue (FIFO) | Stack (LIFO) / Recursion |
| Exploration | Level by level (wide) | Path by path (deep) |
| Shortest path (unweighted) | Yes, guaranteed | No |
| Memory | O(width) -- can be large | O(height/depth) -- usually smaller |
| Complete | Finds all reachable nodes | Finds all reachable nodes |
| Best for | Shortest path, level-order, nearest | Cycle detection, topological sort, backtracking |
| Analogy | Ripples in water | Maze exploration |

### When to Use Which

| Problem Type | Use | Why |
|---|---|---|
| Shortest path (unweighted) | BFS | Guarantees minimum edges |
| Level-by-level processing | BFS | Natural level grouping |
| Finding nearest of something | BFS | Explores closest first |
| Cycle detection | DFS | Easier to track back edges |
| Topological sort | DFS | Natural post-order gives reverse topo |
| Path finding (any path) | DFS | Simpler, less memory |
| Connected components | Either | Both work; DFS is simpler |
| Maze/puzzle solving | DFS | Natural backtracking |
| Word ladder / transformations | BFS | Shortest transformation |

---

## 18.4 The Visited Set: Why It Matters

Without a visited set, traversal on a cyclic graph loops forever:

```
Without visited set:
    0 --- 1
    |     |
    2 --- 3

BFS from 0: Visit 0, enqueue 1, 2.
  Visit 1, enqueue 0 (again!), 3.
  Visit 2, enqueue 0 (again!), 3 (again!).
  Visit 0 (again!), enqueue 1, 2...
  INFINITE LOOP!
```

**Rule**: Always mark a vertex as visited **before** or **when** you add it to the queue/stack, not when you process it.

**Important distinction**:
- **BFS**: Mark visited **when enqueuing** (before processing). This prevents adding the same vertex to the queue multiple times.
- **DFS iterative**: Check visited **when popping**. Since a vertex might be pushed multiple times from different paths, we check at pop time.
- **DFS recursive**: Mark visited **at the start** of the recursive call.

---

## 18.5 Applications

### Application 1: Finding Connected Components

A connected component is a group of vertices where every vertex can reach every other vertex. To find all components, start BFS/DFS from each unvisited vertex.

```python
def find_connected_components(n, edges):
    """Find all connected components in an undirected graph."""
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    visited = set()
    components = []

    for vertex in range(n):
        if vertex not in visited:
            # BFS to find all vertices in this component
            component = []
            queue = deque([vertex])
            visited.add(vertex)

            while queue:
                node = queue.popleft()
                component.append(node)
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            components.append(component)

    return components


# Graph with 3 components:
# Component 1: {0, 1, 2}
# Component 2: {3, 4}
# Component 3: {5}
edges = [(0,1), (1,2), (3,4)]
components = find_connected_components(6, edges)
print(f"Components: {components}")
print(f"Number of components: {len(components)}")
```

**Output:**
```
Components: [[0, 1, 2], [3, 4], [5]]
Number of components: 3
```

### Application 2: Cycle Detection

**Undirected graph**: During DFS, if we encounter a neighbor that is already visited and it is NOT the parent of the current node, we have found a cycle.

```python
def has_cycle_undirected(n, edges):
    """Detect cycle in an undirected graph using DFS."""
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    visited = set()

    def dfs(node, parent):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                # Visited neighbor that is not the parent = cycle
                return True
        return False

    for vertex in range(n):
        if vertex not in visited:
            if dfs(vertex, -1):
                return True
    return False


# Graph with cycle: 0-1-2-0
print(has_cycle_undirected(3, [(0,1), (1,2), (2,0)]))  # True

# Graph without cycle (tree)
print(has_cycle_undirected(3, [(0,1), (1,2)]))  # False
```

**Output:**
```
True
False
```

**Directed graph**: Use three colors -- white (unvisited), gray (in current DFS path), black (fully processed). A back edge (pointing to a gray node) indicates a cycle.

```python
def has_cycle_directed(n, edges):
    """Detect cycle in a directed graph using DFS with 3 colors."""
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def dfs(node):
        color[node] = GRAY  # Currently exploring

        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                return True  # Back edge = cycle
            if color[neighbor] == WHITE:
                if dfs(neighbor):
                    return True

        color[node] = BLACK  # Done exploring
        return False

    for vertex in range(n):
        if color[vertex] == WHITE:
            if dfs(vertex):
                return True
    return False


# Directed cycle: 0->1->2->0
print(has_cycle_directed(3, [(0,1), (1,2), (2,0)]))  # True

# No cycle: 0->1->2
print(has_cycle_directed(3, [(0,1), (1,2)]))  # False
```

**Output:**
```
True
False
```

### Application 3: Topological Sort

A **topological sort** of a directed acyclic graph (DAG) is a linear ordering of vertices such that for every edge (u, v), u comes before v. It represents a valid execution order for tasks with dependencies.

```
Course prerequisites:
    CS101 -> CS201 -> CS301
                  \-> CS202

Topological order: CS101, CS201, CS301, CS202
  (or: CS101, CS201, CS202, CS301)
```

```python
def topological_sort(n, edges):
    """Topological sort using DFS (reverse post-order)."""
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)

    visited = set()
    result = []

    def dfs(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)
        result.append(node)  # Post-order: add AFTER processing children

    for vertex in range(n):
        if vertex not in visited:
            dfs(vertex)

    return result[::-1]  # Reverse post-order = topological order


# 0 -> 1 -> 3
# 0 -> 2 -> 3
# 2 -> 4
edges = [(0,1), (0,2), (1,3), (2,3), (2,4)]
order = topological_sort(5, edges)
print(f"Topological order: {order}")
```

**Output:**
```
Topological order: [0, 2, 4, 1, 3]
```

### Application 4: Bipartite Check

A graph is **bipartite** if its vertices can be divided into two groups such that every edge connects vertices from different groups. Equivalent to being 2-colorable.

```
Bipartite:              Not bipartite:
  0 --- 1                 0 --- 1
  |     |                 |   / |
  3 --- 2                 3 --- 2

Group A: {0, 2}          Cannot split into two groups
Group B: {1, 3}          because of the triangle 0-1-3
```

```python
def is_bipartite(n, edges):
    """Check if graph is bipartite using BFS coloring."""
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    color = [-1] * n  # -1 = uncolored, 0 = group A, 1 = group B

    for start in range(n):
        if color[start] != -1:
            continue

        queue = deque([start])
        color[start] = 0

        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if color[neighbor] == -1:
                    color[neighbor] = 1 - color[node]  # Opposite color
                    queue.append(neighbor)
                elif color[neighbor] == color[node]:
                    return False  # Same color = not bipartite

    return True


print(is_bipartite(4, [(0,1), (1,2), (2,3), (3,0)]))  # True (even cycle)
print(is_bipartite(3, [(0,1), (1,2), (2,0)]))          # False (odd cycle)
```

**Output:**
```
True
False
```

---

## Common Mistakes

1. **Forgetting the visited set.** Without it, BFS and DFS loop forever on cyclic graphs. Always track which vertices you have already processed.

2. **Marking visited too late in BFS.** Mark a vertex as visited when you **enqueue** it, not when you dequeue it. Otherwise, the same vertex can be enqueued multiple times from different neighbors, wasting time and space.

3. **Using BFS when DFS is needed (and vice versa).** BFS finds shortest paths; DFS is better for cycle detection and topological sort. Using the wrong algorithm gives correct traversal but wrong answers for specific problems.

4. **Forgetting to handle disconnected graphs.** If the graph has multiple connected components, a single BFS/DFS from one vertex will not visit all vertices. You need an outer loop over all vertices.

5. **Stack overflow with recursive DFS on large graphs.** Python has a default recursion limit of ~1000. For large graphs, use iterative DFS with an explicit stack, or increase the recursion limit with `sys.setrecursionlimit()`.

---

## Best Practices

1. **Default to BFS for shortest-path problems.** If the problem asks for the minimum number of steps, edges, or moves, BFS is almost always the answer.

2. **Default to DFS for backtracking and exhaustive search.** If the problem requires exploring all possible paths or checking for cycles, DFS is more natural.

3. **Build the adjacency list first.** Before running any traversal, convert the edge list to an adjacency list. This makes neighbor iteration O(1) per neighbor instead of O(E).

4. **Track distance/level in BFS by processing one level at a time.** Use the `for _ in range(len(queue))` pattern to process all vertices at the same distance together.

5. **For directed cycle detection, use three colors.** White = unvisited, gray = in current path, black = finished. A back edge (to a gray node) means a cycle. This is more reliable than the parent-based approach used for undirected graphs.

---

## Quick Summary

| Algorithm | Data Structure | Explores | Finds Shortest Path | Best For |
|---|---|---|---|---|
| BFS | Queue | Level by level | Yes (unweighted) | Shortest path, nearest, level problems |
| DFS | Stack / Recursion | Path by path | No | Cycles, topological sort, backtracking |

| Application | Algorithm | Key Idea |
|---|---|---|
| Connected components | BFS or DFS | Traverse from each unvisited vertex |
| Cycle detection (undirected) | DFS | Visited neighbor that is not the parent |
| Cycle detection (directed) | DFS | Back edge to a gray (in-progress) node |
| Topological sort | DFS | Reverse post-order |
| Bipartite check | BFS | Two-color the graph; conflict = not bipartite |
| Shortest path (unweighted) | BFS | Distance equals BFS level |

---

## Key Points

- BFS uses a **queue** and explores level by level. DFS uses a **stack** (or recursion) and explores depth-first.
- Both BFS and DFS run in **O(V + E)** time and **O(V)** space.
- BFS guarantees the **shortest path** in unweighted graphs. DFS does not.
- The **visited set** prevents infinite loops in cyclic graphs and is mandatory for both algorithms.
- For disconnected graphs, run BFS/DFS from every unvisited vertex.
- Topological sort requires a **DAG** (directed acyclic graph) and uses DFS in reverse post-order.
- A graph is bipartite if and only if it contains no odd-length cycles.

---

## Practice Questions

1. **BFS trace**: For the graph with edges [(0,1), (0,3), (1,2), (2,3), (3,4)], trace BFS from vertex 0. Show the queue state and visit order at each step.

2. **DFS trace**: Using the same graph, trace DFS from vertex 0 (recursive). Show the call stack at each step.

3. **BFS vs DFS paths**: In the same graph, what path does BFS find from 0 to 4? What path does DFS find? Which is shorter?

4. **Component counting**: Given 8 vertices and edges [(0,1), (2,3), (4,5), (5,6), (6,7)], how many connected components exist? Use BFS or DFS to find them.

5. **Cycle detection**: For the directed graph with edges [(0,1), (1,2), (2,3), (3,1)], does a cycle exist? Trace through the three-color DFS algorithm to prove it.

---

## LeetCode-Style Problems

### Problem 1: Number of Islands (LeetCode 200)

**Problem**: Given an m x n grid of '1's (land) and '0's (water), count the number of islands. An island is surrounded by water and is formed by connecting adjacent land cells horizontally or vertically.

```
Grid:
  1 1 0 0 0
  1 1 0 0 0
  0 0 1 0 0
  0 0 0 1 1

Islands: 3
```

**Key Insight**: Each island is a connected component of '1' cells. BFS/DFS from each unvisited '1' cell to find and mark all cells in that island.

**Solution:**

```python
from collections import deque


def num_islands(grid):
    """Count islands using BFS."""
    if not grid:
        return 0

    rows, cols = len(grid), len(grid[0])
    count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                count += 1
                # BFS to mark all connected land
                queue = deque([(r, c)])
                grid[r][c] = '0'  # Mark as visited

                while queue:
                    row, col = queue.popleft()
                    for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                        nr, nc = row + dr, col + dc
                        if (0 <= nr < rows and 0 <= nc < cols
                                and grid[nr][nc] == '1'):
                            grid[nr][nc] = '0'
                            queue.append((nr, nc))

    return count


grid = [
    ['1','1','0','0','0'],
    ['1','1','0','0','0'],
    ['0','0','1','0','0'],
    ['0','0','0','1','1']
]
print(f"Number of islands: {num_islands(grid)}")  # 3
```

**Output:**
```
Number of islands: 3
```

```java
public int numIslands(char[][] grid) {
    int count = 0;
    int rows = grid.length, cols = grid[0].length;

    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
            if (grid[r][c] == '1') {
                count++;
                // BFS
                Queue<int[]> queue = new LinkedList<>();
                queue.offer(new int[]{r, c});
                grid[r][c] = '0';

                while (!queue.isEmpty()) {
                    int[] cell = queue.poll();
                    int[][] dirs = {{0,1},{0,-1},{1,0},{-1,0}};
                    for (int[] d : dirs) {
                        int nr = cell[0] + d[0], nc = cell[1] + d[1];
                        if (nr >= 0 && nr < rows && nc >= 0 && nc < cols
                                && grid[nr][nc] == '1') {
                            grid[nr][nc] = '0';
                            queue.offer(new int[]{nr, nc});
                        }
                    }
                }
            }
        }
    }
    return count;
}
```

**Complexity**: O(m * n) time, O(min(m, n)) space for BFS queue.

---

### Problem 2: Clone Graph (LeetCode 133)

**Problem**: Given a reference to a node in a connected undirected graph, return a deep copy (clone) of the graph.

**Key Insight**: Use BFS or DFS with a hash map to track which nodes have been cloned. The map serves as both a visited set and a lookup for cloned nodes.

```python
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def clone_graph(node):
    """Clone graph using BFS."""
    if not node:
        return None

    # Map from original node to its clone
    clones = {node: Node(node.val)}
    queue = deque([node])

    while queue:
        current = queue.popleft()

        for neighbor in current.neighbors:
            if neighbor not in clones:
                clones[neighbor] = Node(neighbor.val)
                queue.append(neighbor)
            # Connect clone to cloned neighbor
            clones[current].neighbors.append(clones[neighbor])

    return clones[node]


# Build graph: 1 -- 2
#              |    |
#              4 -- 3
node1 = Node(1)
node2 = Node(2)
node3 = Node(3)
node4 = Node(4)
node1.neighbors = [node2, node4]
node2.neighbors = [node1, node3]
node3.neighbors = [node2, node4]
node4.neighbors = [node1, node3]

clone = clone_graph(node1)
print(f"Original node 1 neighbors: {[n.val for n in node1.neighbors]}")
print(f"Cloned node 1 neighbors: {[n.val for n in clone.neighbors]}")
print(f"Are they different objects? {clone is not node1}")
```

**Output:**
```
Original node 1 neighbors: [2, 4]
Cloned node 1 neighbors: [2, 4]
Are they different objects? True
```

```java
public Node cloneGraph(Node node) {
    if (node == null) return null;

    Map<Node, Node> clones = new HashMap<>();
    clones.put(node, new Node(node.val));
    Queue<Node> queue = new LinkedList<>();
    queue.offer(node);

    while (!queue.isEmpty()) {
        Node current = queue.poll();
        for (Node neighbor : current.neighbors) {
            if (!clones.containsKey(neighbor)) {
                clones.put(neighbor, new Node(neighbor.val));
                queue.offer(neighbor);
            }
            clones.get(current).neighbors.add(clones.get(neighbor));
        }
    }

    return clones.get(node);
}
```

**Complexity**: O(V + E) time, O(V) space.

---

### Problem 3: Course Schedule (LeetCode 207)

**Problem**: There are numCourses courses (0 to numCourses-1). Given prerequisites[i] = [a, b] meaning you must take course b before course a, determine if it is possible to finish all courses. (Is there a valid ordering, i.e., no cycles in the prerequisite graph?)

```
numCourses = 4
prerequisites = [[1,0], [2,0], [3,1], [3,2]]

0 -> 1 -> 3
0 -> 2 -> 3

Valid order: 0, 1, 2, 3 (or 0, 2, 1, 3)
Output: True
```

```
numCourses = 2
prerequisites = [[0,1], [1,0]]

0 -> 1 -> 0  (cycle!)
Output: False
```

**Solution (BFS -- Kahn's Algorithm for Topological Sort):**

```python
from collections import deque, defaultdict


def can_finish(num_courses, prerequisites):
    """Determine if all courses can be finished (no cycle)."""
    # Build graph and compute in-degrees
    graph = defaultdict(list)
    in_degree = [0] * num_courses

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    # Start with courses that have no prerequisites
    queue = deque()
    for i in range(num_courses):
        if in_degree[i] == 0:
            queue.append(i)

    courses_taken = 0

    while queue:
        course = queue.popleft()
        courses_taken += 1

        for next_course in graph[course]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)

    return courses_taken == num_courses


print(can_finish(4, [[1,0],[2,0],[3,1],[3,2]]))  # True
print(can_finish(2, [[0,1],[1,0]]))                # False
```

**Output:**
```
True
False
```

```java
public boolean canFinish(int numCourses, int[][] prerequisites) {
    Map<Integer, List<Integer>> graph = new HashMap<>();
    int[] inDegree = new int[numCourses];

    for (int[] pre : prerequisites) {
        graph.computeIfAbsent(pre[1], k -> new ArrayList<>()).add(pre[0]);
        inDegree[pre[0]]++;
    }

    Queue<Integer> queue = new LinkedList<>();
    for (int i = 0; i < numCourses; i++) {
        if (inDegree[i] == 0) queue.offer(i);
    }

    int count = 0;
    while (!queue.isEmpty()) {
        int course = queue.poll();
        count++;
        for (int next : graph.getOrDefault(course, Collections.emptyList())) {
            if (--inDegree[next] == 0) queue.offer(next);
        }
    }

    return count == numCourses;
}
```

**Complexity**: O(V + E) time, O(V + E) space.

---

### Problem 4: Word Ladder (LeetCode 127)

**Problem**: Given a beginWord, endWord, and a dictionary wordList, find the length of the shortest transformation sequence from beginWord to endWord, where each step changes exactly one letter and each intermediate word must be in the word list.

```
beginWord = "hit"
endWord = "cog"
wordList = ["hot","dot","dog","lot","log","cog"]

Shortest transformation: "hit" -> "hot" -> "dot" -> "dog" -> "cog"
Length: 5
```

**Key Insight**: This is a shortest-path problem. Build a graph where words are vertices and edges connect words that differ by one letter. Then BFS from beginWord to endWord.

**Solution:**

```python
from collections import deque, defaultdict


def ladder_length(begin_word, end_word, word_list):
    """Find shortest word transformation using BFS."""
    word_set = set(word_list)
    if end_word not in word_set:
        return 0

    queue = deque([(begin_word, 1)])
    visited = set([begin_word])

    while queue:
        word, steps = queue.popleft()

        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]

                if next_word == end_word:
                    return steps + 1

                if next_word in word_set and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, steps + 1))

    return 0


print(ladder_length("hit", "cog",
                     ["hot","dot","dog","lot","log","cog"]))  # 5

print(ladder_length("hit", "cog",
                     ["hot","dot","dog","lot","log"]))         # 0
```

**Output:**
```
5
0
```

```java
public int ladderLength(String beginWord, String endWord, List<String> wordList) {
    Set<String> wordSet = new HashSet<>(wordList);
    if (!wordSet.contains(endWord)) return 0;

    Queue<String> queue = new LinkedList<>();
    Set<String> visited = new HashSet<>();
    queue.offer(beginWord);
    visited.add(beginWord);
    int steps = 1;

    while (!queue.isEmpty()) {
        int size = queue.size();
        for (int i = 0; i < size; i++) {
            String word = queue.poll();
            char[] chars = word.toCharArray();

            for (int j = 0; j < chars.length; j++) {
                char original = chars[j];
                for (char c = 'a'; c <= 'z'; c++) {
                    chars[j] = c;
                    String next = new String(chars);

                    if (next.equals(endWord)) return steps + 1;

                    if (wordSet.contains(next) && !visited.contains(next)) {
                        visited.add(next);
                        queue.offer(next);
                    }
                }
                chars[j] = original;
            }
        }
        steps++;
    }

    return 0;
}
```

**Complexity**: O(M^2 * N) time where M = word length and N = number of words. O(M * N) space.

---

### Problem 5: Rotting Oranges (LeetCode 994)

**Problem**: In a grid, 0 = empty, 1 = fresh orange, 2 = rotten orange. Every minute, a rotten orange rots all adjacent fresh oranges. Return the minimum time until no fresh oranges remain, or -1 if impossible.

**Key Insight**: Multi-source BFS. Start BFS from ALL rotten oranges simultaneously (like multiple ripples starting at once). Each BFS level = 1 minute.

```python
from collections import deque


def oranges_rotting(grid):
    """Find time for all oranges to rot using multi-source BFS."""
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh = 0

    # Find all rotten oranges and count fresh ones
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1

    if fresh == 0:
        return 0

    minutes = 0

    while queue and fresh > 0:
        minutes += 1
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and grid[nr][nc] == 1):
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))

    return minutes if fresh == 0 else -1


grid1 = [[2,1,1],[1,1,0],[0,1,1]]
print(f"Minutes to rot all: {oranges_rotting(grid1)}")  # 4

grid2 = [[2,1,1],[0,1,1],[1,0,1]]
print(f"Minutes to rot all: {oranges_rotting(grid2)}")  # -1

grid3 = [[0,2]]
print(f"Minutes to rot all: {oranges_rotting(grid3)}")  # 0
```

**Output:**
```
Minutes to rot all: 4
Minutes to rot all: -1
Minutes to rot all: 0
```

```java
public int orangesRotting(int[][] grid) {
    int rows = grid.length, cols = grid[0].length;
    Queue<int[]> queue = new LinkedList<>();
    int fresh = 0;

    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
            if (grid[r][c] == 2) queue.offer(new int[]{r, c});
            else if (grid[r][c] == 1) fresh++;
        }
    }

    if (fresh == 0) return 0;
    int minutes = 0;
    int[][] dirs = {{0,1},{0,-1},{1,0},{-1,0}};

    while (!queue.isEmpty() && fresh > 0) {
        minutes++;
        int size = queue.size();
        for (int i = 0; i < size; i++) {
            int[] cell = queue.poll();
            for (int[] d : dirs) {
                int nr = cell[0] + d[0], nc = cell[1] + d[1];
                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols
                        && grid[nr][nc] == 1) {
                    grid[nr][nc] = 2;
                    fresh--;
                    queue.offer(new int[]{nr, nc});
                }
            }
        }
    }

    return fresh == 0 ? minutes : -1;
}
```

**Complexity**: O(m * n) time, O(m * n) space.

---

## What Is Next?

You now have the two most fundamental graph algorithms in your toolkit. In Chapter 19, you will build on BFS to solve **shortest path problems in weighted graphs** using **Dijkstra's algorithm**. While BFS finds shortest paths when all edges have equal weight, Dijkstra's handles edges with different weights -- like finding the fastest driving route when roads have different speed limits and distances.
