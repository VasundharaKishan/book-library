# Chapter 17: Graphs -- Connecting Everything to Everything

## What You Will Learn

- What a graph is and how it models real-world connections
- Essential graph terminology: vertices, edges, degree, path, cycle, and connected components
- The difference between directed and undirected graphs
- The difference between weighted and unweighted graphs
- How to represent graphs using adjacency matrices and adjacency lists, with a clear trade-offs analysis
- How to implement graph representations in Python and Java
- Real-world applications of graphs: social networks, maps, web pages, and more

## Why This Chapter Matters

Every data structure you have studied so far has limitations. Arrays are linear. Trees are hierarchical with a single path between any two nodes. But the real world is messier than that.

Consider a map of cities connected by roads. City A might connect to cities B, C, and D. City B might connect back to A and also to E. There is no clear "root" city. Multiple paths might exist between any two cities. Some roads might be one-way. Some might be longer than others.

**Graphs** are the data structure that can model all of this. A graph is simply a collection of **vertices** (nodes) connected by **edges** (links). Unlike trees, graphs can have cycles, multiple paths, and no designated root.

Graphs power some of the most important algorithms in computer science:
- **Google Maps** finds shortest routes using graph algorithms
- **Facebook/LinkedIn** models social connections as graphs
- **The internet** is a graph of web pages connected by hyperlinks
- **Compilers** use graphs to determine the order to compile files
- **Airline route planners** optimize connections through graph analysis
- **Recommendation engines** traverse graphs of user preferences

If arrays are one-dimensional and trees are hierarchical, graphs are **relational** -- they capture how things connect to each other in arbitrary ways. Understanding graphs opens the door to the most powerful algorithms you will ever learn.

---

## 17.1 What Is a Graph?

A **graph** `G` is defined by two sets:
- `V` -- a set of **vertices** (also called nodes)
- `E` -- a set of **edges** connecting pairs of vertices

We write `G = (V, E)`.

### The City Map Analogy

```
        [Boston]
       /    |    \
      /     |     \
[New York]--+--[Philadelphia]
      \     |     /
       \    |    /
      [Washington DC]

Vertices: {Boston, New York, Philadelphia, Washington DC}
Edges: {(Boston, New York), (Boston, Philadelphia),
        (Boston, Washington DC), (New York, Philadelphia),
        (New York, Washington DC), (Philadelphia, Washington DC)}
```

Each city is a vertex. Each road between cities is an edge. This graph has 4 vertices and 6 edges.

---

## 17.2 Graph Terminology

Let us define the essential terms using this example graph:

```
     A --- B
     |   / |
     |  /  |
     | /   |
     C --- D --- E

Vertices: {A, B, C, D, E}
Edges: {(A,B), (A,C), (B,C), (B,D), (C,D), (D,E)}
```

### Core Terms

| Term | Definition | Example |
|---|---|---|
| **Vertex (Node)** | A point in the graph | A, B, C, D, E |
| **Edge** | A connection between two vertices | (A, B) |
| **Adjacent** | Two vertices connected by an edge | A and B are adjacent |
| **Degree** | Number of edges connected to a vertex | degree(D) = 3 (connects to B, C, E) |
| **Path** | A sequence of vertices connected by edges | A -> C -> D -> E |
| **Path length** | Number of edges in a path | A -> C -> D -> E has length 3 |
| **Cycle** | A path that starts and ends at the same vertex | A -> B -> C -> A |
| **Connected** | A path exists between two vertices | A and E are connected (A->C->D->E) |
| **Connected component** | A maximal set of connected vertices | See below |

### Connected Components

If some vertices cannot reach each other, the graph has multiple **connected components**:

```
     A --- B        E --- F
     |   /          |
     |  /           |
     C              G

Component 1: {A, B, C}
Component 2: {E, F, G}

No edge connects any vertex in Component 1 to any vertex in Component 2.
```

### Degree

The **degree** of a vertex is the number of edges touching it.

```
     A --- B
     |   / |
     |  /  |
     C --- D --- E

degree(A) = 2  (edges to B and C)
degree(B) = 3  (edges to A, C, D)
degree(C) = 3  (edges to A, B, D)
degree(D) = 3  (edges to B, C, E)
degree(E) = 1  (edge to D only)
```

**Handshaking Lemma**: The sum of all degrees equals twice the number of edges. (Each edge contributes 1 to the degree of each endpoint.)

In our example: 2 + 3 + 3 + 3 + 1 = 12 = 2 * 6 edges.

---

## 17.3 Directed vs. Undirected Graphs

### Undirected Graph

Edges have **no direction**. If A connects to B, then B connects to A. Think of a two-way road.

```
     A --- B
     |     |
     C --- D

Edge (A, B) means A->B AND B->A.
```

### Directed Graph (Digraph)

Edges have a **direction**. If A points to B, it does NOT mean B points to A. Think of a one-way street.

```
     A ---> B
     |      |
     v      v
     C ---> D

Edge (A, B) means A->B only.
A can reach B, but B cannot reach A directly.
```

In a directed graph:
- **In-degree** of a vertex = number of edges pointing INTO it
- **Out-degree** of a vertex = number of edges pointing OUT of it

```
     A ---> B
     |      |
     v      v
     C ---> D

In-degree of D = 2  (from B and C)
Out-degree of A = 2 (to B and C)
In-degree of A = 0  (nothing points to A)
```

### Real-World Examples

| Graph Type | Example | Why |
|---|---|---|
| Undirected | Facebook friendships | If I am your friend, you are mine |
| Undirected | Road network (two-way streets) | Traffic flows both ways |
| Directed | Twitter follows | I can follow you without you following me |
| Directed | Web page links | Page A links to page B; B may not link back |
| Directed | Prerequisites | Course A must come before Course B |
| Directed | Email | I send you an email; it is one-way |

---

## 17.4 Weighted vs. Unweighted Graphs

### Unweighted Graph

All edges are equal. We only care whether an edge exists.

```
     A --- B
     |     |
     C --- D
```

### Weighted Graph

Each edge has a **weight** (cost, distance, time, etc.).

```
     A --5-- B
     |       |
     2       3
     |       |
     C --1-- D

Edge (A, B) has weight 5.
Shortest path A to D: A->C->D with total weight 2+1=3.
                  Not A->B->D with total weight 5+3=8.
```

### Real-World Examples

| Graph Type | Vertices | Edges | Weight |
|---|---|---|---|
| Road network | Cities | Roads | Distance in miles |
| Flight routes | Airports | Flights | Ticket price or flight time |
| Network routing | Routers | Cables | Latency in milliseconds |
| Social network (unweighted) | People | Friendships | None (just connected or not) |

---

## 17.5 Graph Representations

There are two main ways to store a graph in memory: **adjacency matrix** and **adjacency list**.

### Adjacency Matrix

A 2D array where `matrix[i][j] = 1` if there is an edge from vertex i to vertex j, and `0` otherwise.

```
Graph:                     Adjacency Matrix:
     A --- B                   A  B  C  D
     |   / |               A [ 0  1  1  0 ]
     |  /  |               B [ 1  0  1  1 ]
     C --- D               C [ 1  1  0  1 ]
                           D [ 0  1  1  0 ]

matrix[A][B] = 1 (edge exists)
matrix[A][D] = 0 (no edge)
```

For a **weighted graph**, store the weight instead of 1:

```
     A --5-- B              A  B  C  D
     |       |          A [ 0  5  2  0 ]
     2       3          B [ 5  0  0  3 ]
     |       |          C [ 2  0  0  1 ]
     C --1-- D          D [ 0  3  1  0 ]
```

### Adjacency List

Each vertex stores a list of its neighbors. This is typically implemented as a dictionary (hash map) of lists.

```
Graph:                     Adjacency List:
     A --- B               A: [B, C]
     |   / |               B: [A, C, D]
     |  /  |               C: [A, B, D]
     C --- D               D: [B, C]
```

For a **weighted graph**, store (neighbor, weight) pairs:

```
     A --5-- B              A: [(B, 5), (C, 2)]
     |       |              B: [(A, 5), (D, 3)]
     2       3              C: [(A, 2), (D, 1)]
     |       |              D: [(B, 3), (C, 1)]
     C --1-- D
```

### Trade-Offs Comparison

| Operation | Adjacency Matrix | Adjacency List |
|---|---|---|
| **Space** | O(V^2) | O(V + E) |
| **Check if edge exists** | O(1) | O(degree of vertex) |
| **Find all neighbors** | O(V) | O(degree of vertex) |
| **Add edge** | O(1) | O(1) |
| **Remove edge** | O(1) | O(degree of vertex) |
| **Add vertex** | O(V^2) -- resize matrix | O(1) |
| **Best for** | Dense graphs (many edges) | Sparse graphs (few edges) |

### When to Use Which

**Adjacency Matrix** is better when:
- The graph is **dense** (close to V^2 edges)
- You need to frequently check if a specific edge exists
- V is small (the O(V^2) space is acceptable)

**Adjacency List** is better when:
- The graph is **sparse** (far fewer than V^2 edges)
- You frequently need to iterate over a vertex's neighbors
- Memory is a concern
- **Most interview problems use adjacency lists**

### Dense vs. Sparse

A graph with V vertices can have at most V*(V-1)/2 edges (undirected) or V*(V-1) edges (directed).

| V (Vertices) | Max Edges (Undirected) | Sparse Example | Dense Example |
|---|---|---|---|
| 10 | 45 | 15 edges | 40 edges |
| 100 | 4,950 | 200 edges | 4,000 edges |
| 1,000 | 499,500 | 3,000 edges | 400,000 edges |

Most real-world graphs are **sparse**. A social network with 1 billion users does not have each user connected to every other user.

---

## 17.6 Implementation

### Unweighted Graph with Adjacency List

**Python:**

```python
from collections import defaultdict


class Graph:
    """Undirected unweighted graph using adjacency list."""

    def __init__(self):
        self.adj_list = defaultdict(list)

    def add_edge(self, u, v):
        """Add an undirected edge between u and v."""
        self.adj_list[u].append(v)
        self.adj_list[v].append(u)

    def remove_edge(self, u, v):
        """Remove the edge between u and v."""
        self.adj_list[u].remove(v)
        self.adj_list[v].remove(u)

    def has_edge(self, u, v):
        """Check if an edge exists between u and v."""
        return v in self.adj_list[u]

    def neighbors(self, v):
        """Return all neighbors of vertex v."""
        return self.adj_list[v]

    def vertices(self):
        """Return all vertices."""
        return list(self.adj_list.keys())

    def display(self):
        """Print the adjacency list."""
        for vertex in sorted(self.adj_list):
            neighbors = sorted(self.adj_list[vertex])
            print(f"  {vertex}: {neighbors}")


# Build graph:
#     A --- B
#     |   / |
#     |  /  |
#     C --- D --- E

g = Graph()
g.add_edge('A', 'B')
g.add_edge('A', 'C')
g.add_edge('B', 'C')
g.add_edge('B', 'D')
g.add_edge('C', 'D')
g.add_edge('D', 'E')

print("Graph adjacency list:")
g.display()

print(f"\nNeighbors of B: {g.neighbors('B')}")
print(f"Edge A-D exists: {g.has_edge('A', 'D')}")
print(f"Edge A-B exists: {g.has_edge('A', 'B')}")
print(f"All vertices: {g.vertices()}")
```

**Output:**
```
Graph adjacency list:
  A: ['B', 'C']
  B: ['A', 'C', 'D']
  C: ['A', 'B', 'D']
  D: ['B', 'C', 'E']
  E: ['D']

Neighbors of B: ['A', 'C', 'D']
Edge A-D exists: False
Edge A-B exists: True
All vertices: ['A', 'B', 'C', 'D', 'E']
```

**Java:**

```java
import java.util.*;

public class Graph {
    private Map<String, List<String>> adjList;

    public Graph() {
        adjList = new HashMap<>();
    }

    public void addEdge(String u, String v) {
        adjList.computeIfAbsent(u, k -> new ArrayList<>()).add(v);
        adjList.computeIfAbsent(v, k -> new ArrayList<>()).add(u);
    }

    public boolean hasEdge(String u, String v) {
        return adjList.containsKey(u) && adjList.get(u).contains(v);
    }

    public List<String> neighbors(String v) {
        return adjList.getOrDefault(v, Collections.emptyList());
    }

    public Set<String> vertices() {
        return adjList.keySet();
    }

    public void display() {
        for (String vertex : new TreeSet<>(adjList.keySet())) {
            List<String> neighbors = new ArrayList<>(adjList.get(vertex));
            Collections.sort(neighbors);
            System.out.println("  " + vertex + ": " + neighbors);
        }
    }

    public static void main(String[] args) {
        Graph g = new Graph();
        g.addEdge("A", "B");
        g.addEdge("A", "C");
        g.addEdge("B", "C");
        g.addEdge("B", "D");
        g.addEdge("C", "D");
        g.addEdge("D", "E");

        System.out.println("Graph adjacency list:");
        g.display();

        System.out.println("\nNeighbors of B: " + g.neighbors("B"));
        System.out.println("Edge A-D exists: " + g.hasEdge("A", "D"));
        System.out.println("Edge A-B exists: " + g.hasEdge("A", "B"));
    }
}
```

### Directed Graph

```python
class DirectedGraph:
    """Directed graph using adjacency list."""

    def __init__(self):
        self.adj_list = defaultdict(list)

    def add_edge(self, u, v):
        """Add a directed edge from u to v."""
        self.adj_list[u].append(v)
        # Do NOT add v -> u (this is the only difference)

    def display(self):
        for vertex in sorted(self.adj_list):
            print(f"  {vertex} -> {sorted(self.adj_list[vertex])}")


# Build directed graph:
#     A ---> B
#     |      |
#     v      v
#     C ---> D

dg = DirectedGraph()
dg.add_edge('A', 'B')
dg.add_edge('A', 'C')
dg.add_edge('B', 'D')
dg.add_edge('C', 'D')

print("Directed graph:")
dg.display()
```

**Output:**
```
Directed graph:
  A -> ['B', 'C']
  B -> ['D']
  C -> ['D']
```

### Weighted Graph

```python
class WeightedGraph:
    """Undirected weighted graph using adjacency list."""

    def __init__(self):
        self.adj_list = defaultdict(list)

    def add_edge(self, u, v, weight):
        """Add a weighted undirected edge."""
        self.adj_list[u].append((v, weight))
        self.adj_list[v].append((u, weight))

    def display(self):
        for vertex in sorted(self.adj_list):
            edges = [(n, w) for n, w in sorted(self.adj_list[vertex])]
            print(f"  {vertex}: {edges}")


# Build weighted graph:
#     A --5-- B
#     |       |
#     2       3
#     |       |
#     C --1-- D

wg = WeightedGraph()
wg.add_edge('A', 'B', 5)
wg.add_edge('A', 'C', 2)
wg.add_edge('B', 'D', 3)
wg.add_edge('C', 'D', 1)

print("Weighted graph:")
wg.display()
```

**Output:**
```
Weighted graph:
  A: [('B', 5), ('C', 2)]
  B: [('A', 5), ('D', 3)]
  C: [('A', 2), ('D', 1)]
  D: [('B', 3), ('C', 1)]
```

### Adjacency Matrix Implementation

```python
class GraphMatrix:
    """Graph using adjacency matrix."""

    def __init__(self, vertices):
        self.vertices = vertices
        self.v_index = {v: i for i, v in enumerate(vertices)}
        n = len(vertices)
        self.matrix = [[0] * n for _ in range(n)]

    def add_edge(self, u, v, weight=1):
        i, j = self.v_index[u], self.v_index[v]
        self.matrix[i][j] = weight
        self.matrix[j][i] = weight  # Remove for directed graph

    def has_edge(self, u, v):
        i, j = self.v_index[u], self.v_index[v]
        return self.matrix[i][j] != 0

    def display(self):
        header = "    " + "  ".join(self.vertices)
        print(header)
        for i, v in enumerate(self.vertices):
            row = "  ".join(str(x) for x in self.matrix[i])
            print(f"{v} [ {row} ]")


gm = GraphMatrix(['A', 'B', 'C', 'D'])
gm.add_edge('A', 'B')
gm.add_edge('A', 'C')
gm.add_edge('B', 'C')
gm.add_edge('B', 'D')
gm.add_edge('C', 'D')

print("Adjacency Matrix:")
gm.display()
print(f"\nEdge A-B: {gm.has_edge('A', 'B')}")
print(f"Edge A-D: {gm.has_edge('A', 'D')}")
```

**Output:**
```
Adjacency Matrix:
    A  B  C  D
A [ 0  1  1  0 ]
B [ 1  0  1  1 ]
C [ 1  1  0  1 ]
D [ 0  1  1  0 ]

Edge A-B: True
Edge A-D: False
```

---

## 17.7 Graph Representation from Edge List

Many problems give you edges as a list of pairs. Here is how to convert:

```python
def build_adj_list(n, edges, directed=False):
    """Build adjacency list from edge list.

    Args:
        n: number of vertices (0 to n-1)
        edges: list of [u, v] pairs
        directed: whether edges are directed

    Returns:
        adjacency list as dict of lists
    """
    adj = defaultdict(list)

    for u, v in edges:
        adj[u].append(v)
        if not directed:
            adj[v].append(u)

    return adj


# LeetCode-style input
n = 5
edges = [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4]]

adj = build_adj_list(n, edges)
for v in range(n):
    print(f"  {v}: {adj[v]}")
```

**Output:**
```
  0: [1, 2]
  1: [0, 3]
  2: [0, 3]
  3: [1, 2, 4]
  4: [3]
```

---

## 17.8 Real-World Graph Applications

### Social Network

```
Vertices: People
Edges: Friendships (undirected) or Follows (directed)
Use: Friend recommendations, influence analysis, community detection

    Alice --- Bob
      |     / |  \
      |    /  |   \
    Carol    Dave   Eve
```

### Map / Navigation

```
Vertices: Intersections
Edges: Roads (weighted by distance/time)
Use: Shortest path (GPS), traffic routing

    Home --3mi-- Store --2mi-- Office
      |                         |
     5mi                       1mi
      |                         |
    Park -------4mi--------  Gym
```

### Web Pages (The Internet)

```
Vertices: Web pages
Edges: Hyperlinks (directed)
Use: PageRank (Google's algorithm), web crawling

    google.com ---> wikipedia.org
         |              |
         v              v
    youtube.com    wikimedia.org
```

### Course Prerequisites

```
Vertices: Courses
Edges: Prerequisites (directed)
Use: Topological sort, scheduling

    Math 101 ---> Math 201 ---> Math 301
                     |
                     v
                  CS 201 ---> CS 301
```

### Dependency Management

```
Vertices: Software packages
Edges: Dependencies (directed)
Use: Build order, version conflict detection

    react ---> react-dom ---> webpack
      |                        ^
      v                        |
    babel -----> babel-loader --+
```

---

## Common Mistakes

1. **Using an adjacency matrix for a sparse graph.** If your graph has 10,000 vertices but only 20,000 edges, an adjacency matrix wastes 100 million cells. Use an adjacency list.

2. **Forgetting to add both directions for undirected graphs.** When building an adjacency list for an undirected graph, you must add the edge in both directions: `adj[u].append(v)` AND `adj[v].append(u)`.

3. **Confusing vertices and edges.** An edge connects two vertices. The number of edges is NOT the same as the number of vertices. A tree with n vertices has n-1 edges. A complete graph with n vertices has n*(n-1)/2 edges.

4. **Not handling disconnected graphs.** Many graph algorithms assume all vertices are reachable from a starting vertex. If the graph has multiple connected components, you need an outer loop that starts BFS/DFS from every unvisited vertex.

5. **Ignoring self-loops and parallel edges.** Some graphs allow an edge from a vertex to itself (self-loop) or multiple edges between the same pair (multigraph). Clarify with the interviewer whether these exist.

---

## Best Practices

1. **Default to adjacency list.** Unless you have a specific reason to use a matrix (dense graph, need O(1) edge check), adjacency lists are more space-efficient and more common in practice.

2. **Use `defaultdict(list)` in Python.** It eliminates the need to check if a key exists before appending. This is the cleanest way to build adjacency lists.

3. **Always clarify the graph type.** Before coding, ask: Is it directed or undirected? Weighted or unweighted? Can there be cycles? Can there be disconnected components?

4. **Number vertices from 0 to n-1.** This aligns with array indexing and simplifies code. If the problem uses 1-based indexing, adjust accordingly.

5. **Draw the graph.** Just like trees, visualizing the graph is the single most helpful thing you can do when solving graph problems. Even a rough sketch clarifies the structure.

---

## Quick Summary

| Concept | Key Point |
|---|---|
| Graph | Vertices connected by edges |
| Directed | Edges have direction (one-way) |
| Undirected | Edges go both ways |
| Weighted | Edges have costs/distances |
| Adjacency matrix | O(V^2) space, O(1) edge check |
| Adjacency list | O(V+E) space, O(degree) edge check |
| Degree | Number of edges touching a vertex |
| Path | Sequence of vertices connected by edges |
| Cycle | Path that starts and ends at the same vertex |
| Connected component | Maximal group of mutually reachable vertices |

---

## Key Points

- Graphs are the most general data structure for modeling relationships. Trees and linked lists are special cases of graphs.
- Most real-world graphs are **sparse**, making adjacency lists the preferred representation.
- Undirected edges must be added in **both directions** in an adjacency list.
- A graph with V vertices has at most V*(V-1)/2 undirected edges or V*(V-1) directed edges.
- The sum of all vertex degrees equals twice the number of edges (Handshaking Lemma).
- Graph problems dominate technical interviews and real-world applications.

---

## Practice Questions

1. **Draw and classify**: Given edges [(A,B), (B,C), (C,D), (D,A), (A,C)], draw the graph. Is it directed or undirected? Does it have cycles? What is the degree of each vertex?

2. **Matrix to list**: Convert this adjacency matrix to an adjacency list:
   ```
       A  B  C  D
   A [ 0  1  0  1 ]
   B [ 1  0  1  0 ]
   C [ 0  1  0  1 ]
   D [ 1  0  1  0 ]
   ```

3. **Space comparison**: You have a graph with 1,000 vertices and 5,000 edges. How much space does an adjacency matrix use vs. an adjacency list? Which is more efficient?

4. **Connected components**: Given the edges [(0,1), (1,2), (3,4), (5,6), (6,7)], how many connected components are there? List the vertices in each component.

5. **Directed graph properties**: In a directed graph with edges [(A,B), (B,C), (C,A), (C,D)], what is the in-degree and out-degree of each vertex? Is there a cycle?

---

## LeetCode-Style Problems

### Problem 1: Find if Path Exists (LeetCode 1971)

**Problem**: Given n vertices (0 to n-1), a list of edges, and two vertices source and destination, determine if a valid path exists.

```python
from collections import defaultdict, deque


def valid_path(n, edges, source, destination):
    """Check if a path exists using BFS."""
    if source == destination:
        return True

    # Build adjacency list
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # BFS
    visited = set([source])
    queue = deque([source])

    while queue:
        node = queue.popleft()
        if node == destination:
            return True
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return False


print(valid_path(6, [[0,1],[0,2],[3,5],[5,4],[4,3]], 0, 5))  # False
print(valid_path(6, [[0,1],[0,2],[3,5],[5,4],[4,3]], 3, 4))  # True
```

**Output:**
```
False
True
```

```java
public boolean validPath(int n, int[][] edges, int source, int destination) {
    if (source == destination) return true;

    Map<Integer, List<Integer>> adj = new HashMap<>();
    for (int[] edge : edges) {
        adj.computeIfAbsent(edge[0], k -> new ArrayList<>()).add(edge[1]);
        adj.computeIfAbsent(edge[1], k -> new ArrayList<>()).add(edge[0]);
    }

    Set<Integer> visited = new HashSet<>();
    Queue<Integer> queue = new LinkedList<>();
    visited.add(source);
    queue.offer(source);

    while (!queue.isEmpty()) {
        int node = queue.poll();
        if (node == destination) return true;
        for (int neighbor : adj.getOrDefault(node, Collections.emptyList())) {
            if (!visited.contains(neighbor)) {
                visited.add(neighbor);
                queue.offer(neighbor);
            }
        }
    }
    return false;
}
```

**Complexity**: O(V + E) time, O(V + E) space.

---

### Problem 2: Find the Town Judge (LeetCode 997)

**Problem**: In a town of n people (1 to n), there may be a "town judge" who trusts nobody and is trusted by everyone else. Given a list of trust[i] = [a, b] meaning person a trusts person b, find the judge or return -1.

**Key Insight**: The judge has in-degree n-1 and out-degree 0. Track the net trust (in-degree minus out-degree).

```python
def find_judge(n, trust):
    """Find the town judge using degree counting."""
    if n == 1:
        return 1

    # net_trust[i] = in-degree - out-degree
    net_trust = [0] * (n + 1)

    for a, b in trust:
        net_trust[a] -= 1  # a trusts someone (out-degree)
        net_trust[b] += 1  # b is trusted (in-degree)

    for i in range(1, n + 1):
        if net_trust[i] == n - 1:
            return i

    return -1


print(find_judge(3, [[1,3],[2,3]]))           # 3
print(find_judge(3, [[1,3],[2,3],[3,1]]))      # -1
print(find_judge(4, [[1,3],[1,4],[2,3],[2,4],[4,3]]))  # 3
```

**Output:**
```
3
-1
3
```

```java
public int findJudge(int n, int[][] trust) {
    int[] netTrust = new int[n + 1];
    for (int[] t : trust) {
        netTrust[t[0]]--;
        netTrust[t[1]]++;
    }
    for (int i = 1; i <= n; i++) {
        if (netTrust[i] == n - 1) return i;
    }
    return -1;
}
```

**Complexity**: O(V + E) time, O(V) space.

---

### Problem 3: Find Center of Star Graph (LeetCode 1791)

**Problem**: A star graph has one center node connected to every other node. Given the edges, find the center.

**Key Insight**: The center appears in every edge. Just check the first two edges -- the center is the vertex that appears in both.

```python
def find_center(edges):
    """The center vertex appears in every edge."""
    # Check first two edges
    if edges[0][0] in edges[1]:
        return edges[0][0]
    return edges[0][1]


print(find_center([[1,2],[2,3],[4,2]]))  # 2
print(find_center([[1,2],[5,1],[1,3],[1,4]]))  # 1
```

**Output:**
```
2
1
```

**Complexity**: O(1) time, O(1) space.

---

## What Is Next?

You now know what graphs are, how to represent them, and their real-world significance. But a graph sitting in memory is useless until you can **traverse** it -- visit every vertex and edge systematically. In Chapter 18, you will learn the two fundamental graph traversal algorithms: **Breadth-First Search (BFS)** and **Depth-First Search (DFS)**. These algorithms are the foundation for solving nearly every graph problem: finding connected components, detecting cycles, topological sorting, and much more.
