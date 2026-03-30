# Chapter 19: Shortest Path Algorithms

## What You Will Learn

- How Dijkstra's algorithm finds the shortest path, just like GPS navigation
- How to implement Dijkstra's using a priority queue for optimal performance
- How Bellman-Ford handles graphs with negative edge weights
- How Floyd-Warshall computes shortest paths between ALL pairs of vertices
- When to choose each algorithm based on your problem constraints
- How to solve classic shortest path interview problems

## Why This Chapter Matters

Every time you open a maps application and ask for directions, a shortest path algorithm runs behind the scenes. Every time a network packet travels across the internet, routers use shortest path algorithms to find the best route. Every time a game character finds its way through a level, pathfinding algorithms guide it.

Shortest path problems appear everywhere in technical interviews and real systems. Understanding these algorithms gives you the ability to model and solve an enormous range of optimization problems: from logistics and routing to network analysis and resource allocation.

This chapter builds directly on the graph fundamentals and traversal techniques from Chapters 17 and 18. BFS already finds shortest paths in unweighted graphs. Now we handle the far more common case: **weighted graphs**, where edges have different costs.

---

## 19.1 The Shortest Path Problem

Given a weighted graph, find the path between two vertices that minimizes the total weight of edges traversed.

```
Example: Getting from City A to City D

        A ---5--- B
        |         |
        2         3
        |         |
        C ---1--- D

Path A -> B -> D: cost = 5 + 3 = 8
Path A -> C -> D: cost = 2 + 1 = 3   <-- Shortest!
```

There are several variations of this problem:

| Variation | Description | Best Algorithm |
|-----------|-------------|----------------|
| Single source, no negative weights | Shortest path from one vertex to all others | Dijkstra's |
| Single source, negative weights allowed | Shortest path from one vertex to all others | Bellman-Ford |
| All pairs | Shortest path between every pair of vertices | Floyd-Warshall |
| Unweighted graph | All edges have weight 1 | BFS (Chapter 18) |

---

## 19.2 Dijkstra's Algorithm

### The Intuition: GPS Navigation

Imagine you are planning a road trip. You start at your city and want to find the shortest route to every other city. Here is your strategy:

1. Mark your starting city with distance 0. Mark all other cities with distance infinity (unknown).
2. Visit the closest unvisited city.
3. From that city, check all neighboring cities. If the path through the current city is shorter than what we previously knew, update the distance.
4. Repeat until all cities are visited.

This is exactly how GPS navigation works: it expands outward from your location, always exploring the closest unvisited point, gradually discovering the shortest routes.

### Step-by-Step Walkthrough

Let us trace Dijkstra's algorithm on this graph:

```
Graph:
        A ---4--- B
       / \        |
      2    1      5
     /      \     |
    C        D ---3--- E
     \      /
      5    2
       \  /
        F

Adjacency list with weights:
A: [(B,4), (C,2), (D,1)]
B: [(A,4), (E,5)]
C: [(A,2), (F,5)]
D: [(A,1), (E,3), (F,2)]
E: [(B,5), (D,3)]
F: [(C,5), (D,2)]
```

**Source vertex: A**

**Initial State:**

```
Vertex:    A    B    C    D    E    F
Distance:  0    inf  inf  inf  inf  inf
Visited:   N    N    N    N    N    N
Parent:    -    -    -    -    -    -
```

**Step 1: Visit A (distance 0, smallest unvisited)**

Check neighbors of A:
- B: 0 + 4 = 4 < inf, update B to 4
- C: 0 + 2 = 2 < inf, update C to 2
- D: 0 + 1 = 1 < inf, update D to 1

```
Vertex:    A    B    C    D    E    F
Distance:  0    4    2    1    inf  inf
Visited:   Y    N    N    N    N    N
Parent:    -    A    A    A    -    -
```

**Step 2: Visit D (distance 1, smallest unvisited)**

Check neighbors of D:
- A: already visited, skip
- E: 1 + 3 = 4 < inf, update E to 4
- F: 1 + 2 = 3 < inf, update F to 3

```
Vertex:    A    B    C    D    E    F
Distance:  0    4    2    1    4    3
Visited:   Y    N    N    Y    N    N
Parent:    -    A    A    A    D    D
```

**Step 3: Visit C (distance 2, smallest unvisited)**

Check neighbors of C:
- A: already visited, skip
- F: 2 + 5 = 7 > 3, no update (current path to F through D is shorter)

```
Vertex:    A    B    C    D    E    F
Distance:  0    4    2    1    4    3
Visited:   Y    N    Y    Y    N    N
Parent:    -    A    A    A    D    D
```

**Step 4: Visit F (distance 3, smallest unvisited)**

Check neighbors of F:
- C: already visited, skip
- D: already visited, skip

No updates.

```
Vertex:    A    B    C    D    E    F
Distance:  0    4    2    1    4    3
Visited:   Y    N    Y    Y    N    Y
Parent:    -    A    A    A    D    D
```

**Step 5: Visit B (distance 4, smallest unvisited)**

Check neighbors of B:
- A: already visited, skip
- E: 4 + 5 = 9 > 4, no update

**Step 6: Visit E (distance 4, smallest unvisited)**

All neighbors visited. Done!

**Final Result:**

```
Vertex:    A    B    C    D    E    F
Distance:  0    4    2    1    4    3
Parent:    -    A    A    A    D    D

Shortest paths from A:
  A -> B: A -> B (cost 4)
  A -> C: A -> C (cost 2)
  A -> D: A -> D (cost 1)
  A -> E: A -> D -> E (cost 4)
  A -> F: A -> D -> F (cost 3)
```

### Implementation with Priority Queue

The naive approach checks all vertices to find the minimum distance, giving O(V^2). Using a min-heap (priority queue), we reduce this to O((V + E) log V).

**Python:**

```python
import heapq
from collections import defaultdict

def dijkstra(graph, source):
    """
    Find shortest paths from source to all other vertices.

    graph: dict of {vertex: [(neighbor, weight), ...]}
    source: starting vertex

    Returns: (distances, parents) dictionaries
    """
    # Initialize distances to infinity
    distances = {vertex: float('inf') for vertex in graph}
    distances[source] = 0

    # Parent tracking for path reconstruction
    parents = {vertex: None for vertex in graph}

    # Priority queue: (distance, vertex)
    # We use a min-heap so the smallest distance is always at the top
    pq = [(0, source)]

    # Set of visited vertices
    visited = set()

    while pq:
        # Get the unvisited vertex with the smallest distance
        current_dist, current = heapq.heappop(pq)

        # Skip if we already found a better path
        if current in visited:
            continue

        visited.add(current)

        # Explore all neighbors
        for neighbor, weight in graph[current]:
            if neighbor in visited:
                continue

            new_dist = current_dist + weight

            # Found a shorter path?
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parents[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))

    return distances, parents


def reconstruct_path(parents, source, target):
    """Reconstruct the shortest path from source to target."""
    path = []
    current = target

    while current is not None:
        path.append(current)
        current = parents[current]

    path.reverse()

    # Check if a valid path exists
    if path[0] != source:
        return []  # No path exists

    return path


# Example usage
graph = {
    'A': [('B', 4), ('C', 2), ('D', 1)],
    'B': [('A', 4), ('E', 5)],
    'C': [('A', 2), ('F', 5)],
    'D': [('A', 1), ('E', 3), ('F', 2)],
    'E': [('B', 5), ('D', 3)],
    'F': [('C', 5), ('D', 2)]
}

distances, parents = dijkstra(graph, 'A')

print("Shortest distances from A:")
for vertex in sorted(distances):
    path = reconstruct_path(parents, 'A', vertex)
    print(f"  A -> {vertex}: distance = {distances[vertex]}, "
          f"path = {' -> '.join(path)}")
```

**Output:**

```
Shortest distances from A:
  A -> A: distance = 0, path = A
  A -> B: distance = 4, path = A -> B
  A -> C: distance = 2, path = A -> C
  A -> D: distance = 1, path = A -> D
  A -> E: distance = 4, path = A -> D -> E
  A -> F: distance = 3, path = A -> D -> F
```

**Java:**

```java
import java.util.*;

public class Dijkstra {

    // Edge representation
    static class Edge {
        String target;
        int weight;

        Edge(String target, int weight) {
            this.target = target;
            this.weight = weight;
        }
    }

    // Node for priority queue
    static class Node implements Comparable<Node> {
        String vertex;
        int distance;

        Node(String vertex, int distance) {
            this.vertex = vertex;
            this.distance = distance;
        }

        @Override
        public int compareTo(Node other) {
            return Integer.compare(this.distance, other.distance);
        }
    }

    public static Map<String, Integer> dijkstra(
            Map<String, List<Edge>> graph, String source) {

        Map<String, Integer> distances = new HashMap<>();
        Map<String, String> parents = new HashMap<>();
        Set<String> visited = new HashSet<>();
        PriorityQueue<Node> pq = new PriorityQueue<>();

        // Initialize all distances to infinity
        for (String vertex : graph.keySet()) {
            distances.put(vertex, Integer.MAX_VALUE);
        }
        distances.put(source, 0);
        pq.offer(new Node(source, 0));

        while (!pq.isEmpty()) {
            Node current = pq.poll();

            if (visited.contains(current.vertex)) {
                continue;
            }
            visited.add(current.vertex);

            for (Edge edge : graph.get(current.vertex)) {
                if (visited.contains(edge.target)) {
                    continue;
                }

                int newDist = current.distance + edge.weight;

                if (newDist < distances.get(edge.target)) {
                    distances.put(edge.target, newDist);
                    parents.put(edge.target, current.vertex);
                    pq.offer(new Node(edge.target, newDist));
                }
            }
        }

        return distances;
    }

    public static void main(String[] args) {
        Map<String, List<Edge>> graph = new HashMap<>();
        graph.put("A", Arrays.asList(
            new Edge("B", 4), new Edge("C", 2), new Edge("D", 1)));
        graph.put("B", Arrays.asList(
            new Edge("A", 4), new Edge("E", 5)));
        graph.put("C", Arrays.asList(
            new Edge("A", 2), new Edge("F", 5)));
        graph.put("D", Arrays.asList(
            new Edge("A", 1), new Edge("E", 3), new Edge("F", 2)));
        graph.put("E", Arrays.asList(
            new Edge("B", 5), new Edge("D", 3)));
        graph.put("F", Arrays.asList(
            new Edge("C", 5), new Edge("D", 2)));

        Map<String, Integer> distances = dijkstra(graph, "A");

        System.out.println("Shortest distances from A:");
        for (String vertex : new TreeSet<>(distances.keySet())) {
            System.out.println("  A -> " + vertex +
                ": distance = " + distances.get(vertex));
        }
    }
}
```

**Output:**

```
Shortest distances from A:
  A -> A: distance = 0
  A -> B: distance = 4
  A -> C: distance = 2
  A -> D: distance = 1
  A -> E: distance = 4
  A -> F: distance = 3
```

### Why Dijkstra's Fails with Negative Weights

```
Consider this graph:
    A --1--> B --(-5)--> C
    |                    ^
    +--------3-----------+

Dijkstra visits B first (distance 1), then goes to C via B (distance -4).
But it already processed A->C as distance 3.
Since B was already "finalized" at distance 1, Dijkstra never reconsiders it.

The greedy assumption ("once a vertex is finalized, its distance is optimal")
breaks when negative edges can create shortcuts.
```

### Time and Space Complexity

| Implementation | Time Complexity | Space Complexity |
|---------------|----------------|-----------------|
| Array (naive) | O(V^2) | O(V) |
| Binary Heap | O((V + E) log V) | O(V + E) |
| Fibonacci Heap | O(V log V + E) | O(V + E) |

For sparse graphs (E is close to V), the binary heap version is best.
For dense graphs (E is close to V^2), the array version can be competitive.

---

## 19.3 Bellman-Ford Algorithm

### The Intuition

Bellman-Ford takes a different approach: instead of greedily picking the closest vertex, it repeatedly relaxes ALL edges, V-1 times. This brute-force approach is slower but handles negative edge weights correctly.

Think of it like this: the shortest path between any two vertices can have at most V-1 edges. In each iteration, we guarantee that paths with one more edge are correctly computed. After V-1 iterations, all shortest paths are found.

### How It Works

```
Relaxation: For each edge (u, v) with weight w:
  if distance[u] + w < distance[v]:
      distance[v] = distance[u] + w
      parent[v] = u

Repeat this for ALL edges, V-1 times.
After V-1 iterations, do one more pass.
If any distance still decreases, there is a NEGATIVE CYCLE.
```

### Step-by-Step Walkthrough

```
Graph (directed, with a negative edge):

    A --6--> B --(-2)--> C
    |        ^           |
    |        |           |
    +--5-->  D  <--3-----+
    |
    +--(-4)--> E

Edges: (A,B,6), (A,D,5), (A,E,-4), (B,C,-2), (C,D,3), (D,B,1)
```

**Source: A, Vertices: A, B, C, D, E**

**Initialization:**

```
Vertex:    A    B    C    D    E
Distance:  0    inf  inf  inf  inf
```

**Iteration 1 (relax all edges):**

```
Edge (A,B,6):  0 + 6 = 6 < inf   -> B = 6
Edge (A,D,5):  0 + 5 = 5 < inf   -> D = 5
Edge (A,E,-4): 0 + (-4) = -4 < inf -> E = -4
Edge (B,C,-2): 6 + (-2) = 4 < inf -> C = 4
Edge (C,D,3):  4 + 3 = 7 > 5     -> no change
Edge (D,B,1):  5 + 1 = 6 = 6     -> no change

Vertex:    A    B    C    D    E
Distance:  0    6    4    5    -4
```

**Iteration 2:**

```
Edge (A,B,6):  0 + 6 = 6 = 6     -> no change
Edge (A,D,5):  0 + 5 = 5 = 5     -> no change
Edge (A,E,-4): 0 + (-4) = -4 = -4 -> no change
Edge (B,C,-2): 6 + (-2) = 4 = 4  -> no change
Edge (C,D,3):  4 + 3 = 7 > 5     -> no change
Edge (D,B,1):  5 + 1 = 6 = 6     -> no change

No changes! Algorithm can terminate early.
```

**Final distances: A=0, B=6, C=4, D=5, E=-4**

### Implementation

**Python:**

```python
def bellman_ford(vertices, edges, source):
    """
    Find shortest paths from source using Bellman-Ford.

    vertices: list of vertex labels
    edges: list of (from, to, weight) tuples
    source: starting vertex

    Returns: (distances, parents, has_negative_cycle)
    """
    # Initialize
    distances = {v: float('inf') for v in vertices}
    distances[source] = 0
    parents = {v: None for v in vertices}

    # Relax all edges V-1 times
    for i in range(len(vertices) - 1):
        updated = False

        for u, v, weight in edges:
            if distances[u] != float('inf') and \
               distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                parents[v] = u
                updated = True

        # Early termination: no updates means we are done
        if not updated:
            break

    # Check for negative cycles (one more pass)
    has_negative_cycle = False
    for u, v, weight in edges:
        if distances[u] != float('inf') and \
           distances[u] + weight < distances[v]:
            has_negative_cycle = True
            break

    return distances, parents, has_negative_cycle


# Example usage
vertices = ['A', 'B', 'C', 'D', 'E']
edges = [
    ('A', 'B', 6),
    ('A', 'D', 5),
    ('A', 'E', -4),
    ('B', 'C', -2),
    ('C', 'D', 3),
    ('D', 'B', 1)
]

distances, parents, has_negative_cycle = bellman_ford(vertices, edges, 'A')

print(f"Negative cycle detected: {has_negative_cycle}")
print("Shortest distances from A:")
for v in sorted(distances):
    print(f"  A -> {v}: {distances[v]}")
```

**Output:**

```
Negative cycle detected: False
Shortest distances from A:
  A -> A: 0
  A -> B: 6
  A -> C: 4
  A -> D: 5
  A -> E: -4
```

**Java:**

```java
import java.util.*;

public class BellmanFord {

    static class Edge {
        String from, to;
        int weight;

        Edge(String from, String to, int weight) {
            this.from = from;
            this.to = to;
            this.weight = weight;
        }
    }

    public static Map<String, Integer> bellmanFord(
            List<String> vertices, List<Edge> edges, String source) {

        Map<String, Integer> distances = new HashMap<>();
        for (String v : vertices) {
            distances.put(v, Integer.MAX_VALUE);
        }
        distances.put(source, 0);

        // Relax all edges V-1 times
        for (int i = 0; i < vertices.size() - 1; i++) {
            boolean updated = false;
            for (Edge e : edges) {
                if (distances.get(e.from) != Integer.MAX_VALUE &&
                    distances.get(e.from) + e.weight <
                    distances.get(e.to)) {
                    distances.put(e.to,
                        distances.get(e.from) + e.weight);
                    updated = true;
                }
            }
            if (!updated) break;
        }

        // Check for negative cycle
        for (Edge e : edges) {
            if (distances.get(e.from) != Integer.MAX_VALUE &&
                distances.get(e.from) + e.weight <
                distances.get(e.to)) {
                System.out.println("Negative cycle detected!");
                return null;
            }
        }

        return distances;
    }

    public static void main(String[] args) {
        List<String> vertices = Arrays.asList("A","B","C","D","E");
        List<Edge> edges = Arrays.asList(
            new Edge("A", "B", 6),
            new Edge("A", "D", 5),
            new Edge("A", "E", -4),
            new Edge("B", "C", -2),
            new Edge("C", "D", 3),
            new Edge("D", "B", 1)
        );

        Map<String, Integer> distances =
            bellmanFord(vertices, edges, "A");

        if (distances != null) {
            System.out.println("Shortest distances from A:");
            for (String v : new TreeSet<>(distances.keySet())) {
                System.out.println("  A -> " + v + ": " +
                    distances.get(v));
            }
        }
    }
}
```

**Output:**

```
Shortest distances from A:
  A -> A: 0
  A -> B: 6
  A -> C: 4
  A -> D: 5
  A -> E: -4
```

### Time and Space Complexity

| Aspect | Complexity |
|--------|-----------|
| Time | O(V * E) |
| Space | O(V) |

---

## 19.4 Floyd-Warshall Algorithm (All Pairs Shortest Paths)

### The Intuition

What if you need the shortest path between EVERY pair of vertices? You could run Dijkstra's V times, but Floyd-Warshall solves this more elegantly using dynamic programming.

The key idea: for each vertex k, check if the path from i to j through k is shorter than the current best path from i to j.

```
For each intermediate vertex k:
    For each pair (i, j):
        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

### Step-by-Step Walkthrough

```
Graph:
    1 ---3--- 2
    |         |
    8         1
    |         |
    3 ---2--- 4

    Also: 1 -> 4 with weight 7 (direct edge)
```

**Initial distance matrix (direct edges only):**

```
     1    2    3    4
1  [ 0    3    8    7  ]
2  [ 3    0    inf  1  ]
3  [ 8    inf  0    2  ]
4  [ 7    1    2    0  ]
```

**k = 1 (consider paths through vertex 1):**

```
Check if i -> 1 -> j is shorter than i -> j:
  dist[2][3] = min(inf, dist[2][1] + dist[1][3]) = min(inf, 3+8) = 11
  dist[3][2] = min(inf, dist[3][1] + dist[1][2]) = min(inf, 8+3) = 11
  dist[2][4] vs 2->1->4 = 3+7 = 10 > 1, no change
  dist[3][4] vs 3->1->4 = 8+7 = 15 > 2, no change
  dist[4][2] vs 4->1->2 = 7+3 = 10 > 1, no change
  dist[4][3] vs 4->1->3 = 7+8 = 15 > 2, no change

     1    2    3    4
1  [ 0    3    8    7  ]
2  [ 3    0    11   1  ]
3  [ 8    11   0    2  ]
4  [ 7    1    2    0  ]
```

**k = 2 (consider paths through vertex 2):**

```
  dist[1][4] vs 1->2->4 = 3+1 = 4 < 7, UPDATE!
  dist[3][1] vs 3->2->1: dist[3][2]=11, dist[2][1]=3, 11+3=14 > 8, no
  dist[4][1] vs 4->2->1 = 1+3 = 4 < 7, UPDATE!
  dist[1][3] vs 1->2->3 = 3+11 = 14 > 8, no
  dist[3][4] vs 3->2->4 = 11+1 = 12 > 2, no
  dist[4][3] vs 4->2->3 = 1+11 = 12 > 2, no

     1    2    3    4
1  [ 0    3    8    4  ]
2  [ 3    0    11   1  ]
3  [ 8    11   0    2  ]
4  [ 4    1    2    0  ]
```

**k = 3 (consider paths through vertex 3):**

```
  dist[1][4] vs 1->3->4 = 8+2 = 10 > 4, no
  dist[2][4] vs 2->3->4 = 11+2 = 13 > 1, no
  dist[1][2] vs 1->3->2 = 8+11 = 19 > 3, no
  dist[4][1] vs 4->3->1 = 2+8 = 10 > 4, no
  dist[4][2] vs 4->3->2 = 2+11 = 13 > 1, no
  dist[2][1] vs 2->3->1 = 11+8 = 19 > 3, no

No changes.
```

**k = 4 (consider paths through vertex 4):**

```
  dist[1][2] vs 1->4->2 = 4+1 = 5 > 3, no
  dist[1][3] vs 1->4->3 = 4+2 = 6 < 8, UPDATE!
  dist[2][1] vs 2->4->1 = 1+4 = 5 > 3, no
  dist[2][3] vs 2->4->3 = 1+2 = 3 < 11, UPDATE!
  dist[3][1] vs 3->4->1 = 2+4 = 6 < 8, UPDATE!
  dist[3][2] vs 3->4->2 = 2+1 = 3 < 11, UPDATE!

Final:
     1    2    3    4
1  [ 0    3    6    4  ]
2  [ 3    0    3    1  ]
3  [ 6    3    0    2  ]
4  [ 4    1    2    0  ]
```

### Implementation

**Python:**

```python
def floyd_warshall(graph_matrix, vertices):
    """
    Find shortest paths between all pairs of vertices.

    graph_matrix: 2D list where graph_matrix[i][j] is the weight
                  of edge from vertex i to vertex j (inf if no edge)
    vertices: list of vertex labels

    Returns: (distance matrix, next-hop matrix for path reconstruction)
    """
    n = len(vertices)

    # Initialize distance and next-hop matrices
    dist = [row[:] for row in graph_matrix]  # Deep copy
    next_hop = [[None] * n for _ in range(n)]

    # Set up next-hop for direct edges
    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] != float('inf'):
                next_hop[i][j] = j

    # Floyd-Warshall: try each vertex as intermediate
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_hop[i][j] = next_hop[i][k]

    return dist, next_hop


def reconstruct_path(next_hop, vertices, start, end):
    """Reconstruct path from start to end using next-hop matrix."""
    start_idx = vertices.index(start)
    end_idx = vertices.index(end)

    if next_hop[start_idx][end_idx] is None:
        return []  # No path

    path = [start]
    current = start_idx
    while current != end_idx:
        current = next_hop[current][end_idx]
        path.append(vertices[current])

    return path


# Example
vertices = [1, 2, 3, 4]
INF = float('inf')
graph = [
    [0,   3,   8,   7  ],  # From vertex 1
    [3,   0,   INF, 1  ],  # From vertex 2
    [8,   INF, 0,   2  ],  # From vertex 3
    [7,   1,   2,   0  ]   # From vertex 4
]

dist, next_hop = floyd_warshall(graph, vertices)

print("All-pairs shortest distances:")
print("     ", "  ".join(str(v) for v in vertices))
for i, v in enumerate(vertices):
    row = "  ".join(f"{dist[i][j]:3}" for j in range(len(vertices)))
    print(f"  {v}: {row}")

print("\nShortest path from 1 to 3:")
path = reconstruct_path(next_hop, vertices, 1, 3)
print(f"  {' -> '.join(map(str, path))} (distance: {dist[0][2]})")
```

**Output:**

```
All-pairs shortest distances:
      1  2  3  4
  1:   0    3    6    4
  2:   3    0    3    1
  3:   6    3    0    2
  4:   4    1    2    0

Shortest path from 1 to 3:
  1 -> 4 -> 3 (distance: 6)
```

**Java:**

```java
import java.util.*;

public class FloydWarshall {

    static final int INF = 99999;

    public static int[][] floydWarshall(int[][] graph) {
        int n = graph.length;
        int[][] dist = new int[n][n];

        // Copy initial distances
        for (int i = 0; i < n; i++) {
            dist[i] = graph[i].clone();
        }

        // Try each vertex as intermediate
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                    }
                }
            }
        }

        return dist;
    }

    public static void main(String[] args) {
        int[][] graph = {
            {0,   3,   8,   7  },
            {3,   0,   INF, 1  },
            {8,   INF, 0,   2  },
            {7,   1,   2,   0  }
        };

        int[][] dist = floydWarshall(graph);

        System.out.println("All-pairs shortest distances:");
        String[] labels = {"1", "2", "3", "4"};
        System.out.print("     ");
        for (String l : labels) System.out.printf("%4s", l);
        System.out.println();

        for (int i = 0; i < dist.length; i++) {
            System.out.printf("  %s:", labels[i]);
            for (int j = 0; j < dist[i].length; j++) {
                System.out.printf("%4d", dist[i][j]);
            }
            System.out.println();
        }
    }
}
```

**Output:**

```
All-pairs shortest distances:
        1   2   3   4
  1:   0   3   6   4
  2:   3   0   3   1
  3:   6   3   0   2
  4:   4   1   2   0
```

### Time and Space Complexity

| Aspect | Complexity |
|--------|-----------|
| Time | O(V^3) |
| Space | O(V^2) |

---

## 19.5 When to Use Which Algorithm

```
Decision Tree:

Need shortest paths between ALL pairs?
├── YES --> Floyd-Warshall  O(V^3)
└── NO (single source)
    ├── Any negative edge weights?
    │   ├── YES --> Bellman-Ford  O(V*E)
    │   └── NO  --> Dijkstra's   O((V+E) log V)
    └── Unweighted graph?
        └── YES --> BFS  O(V+E)     (Chapter 18)
```

| Feature | Dijkstra's | Bellman-Ford | Floyd-Warshall |
|---------|-----------|-------------|----------------|
| Type | Single source | Single source | All pairs |
| Negative weights | No | Yes | Yes |
| Negative cycle detection | No | Yes | Yes |
| Time complexity | O((V+E) log V) | O(V*E) | O(V^3) |
| Space complexity | O(V+E) | O(V) | O(V^2) |
| Best for | GPS, network routing | Currency exchange, checking negative cycles | Small dense graphs, transitive closure |

---

## 19.6 Problem: Network Delay Time

**Problem:** You are given a network of n nodes labeled 1 to n. You are given `times`, a list of directed edges `(source, target, time)`. A signal is sent from node k. Return the minimum time for all nodes to receive the signal. Return -1 if not all nodes can be reached.

This is a classic single-source shortest path problem. We need the maximum shortest distance from k to any reachable node.

**Python:**

```python
import heapq

def network_delay_time(times, n, k):
    """
    Find the time for signal to reach all nodes from node k.

    times: list of [source, target, time]
    n: number of nodes
    k: starting node
    """
    # Build adjacency list
    graph = {i: [] for i in range(1, n + 1)}
    for u, v, w in times:
        graph[u].append((v, w))

    # Dijkstra's from node k
    distances = {i: float('inf') for i in range(1, n + 1)}
    distances[k] = 0
    pq = [(0, k)]
    visited = set()

    while pq:
        dist, node = heapq.heappop(pq)

        if node in visited:
            continue
        visited.add(node)

        for neighbor, weight in graph[node]:
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))

    # The answer is the maximum distance
    max_dist = max(distances.values())
    return max_dist if max_dist != float('inf') else -1


# Example 1
times = [[2,1,1], [2,3,1], [3,4,1]]
n, k = 4, 2
print(f"Network delay: {network_delay_time(times, n, k)}")
# Output: Network delay: 2

# Example 2: Node 1 unreachable
times = [[1,2,1]]
n, k = 2, 2
print(f"Network delay: {network_delay_time(times, n, k)}")
# Output: Network delay: -1
```

**Output:**

```
Network delay: 2
Network delay: -1
```

**Java:**

```java
import java.util.*;

public class NetworkDelayTime {

    public static int networkDelayTime(
            int[][] times, int n, int k) {

        Map<Integer, List<int[]>> graph = new HashMap<>();
        for (int i = 1; i <= n; i++) {
            graph.put(i, new ArrayList<>());
        }
        for (int[] time : times) {
            graph.get(time[0]).add(
                new int[]{time[1], time[2]});
        }

        int[] distances = new int[n + 1];
        Arrays.fill(distances, Integer.MAX_VALUE);
        distances[k] = 0;

        PriorityQueue<int[]> pq = new PriorityQueue<>(
            (a, b) -> a[1] - b[1]);
        pq.offer(new int[]{k, 0});

        Set<Integer> visited = new HashSet<>();

        while (!pq.isEmpty()) {
            int[] curr = pq.poll();
            int node = curr[0], dist = curr[1];

            if (visited.contains(node)) continue;
            visited.add(node);

            for (int[] edge : graph.get(node)) {
                int newDist = dist + edge[1];
                if (newDist < distances[edge[0]]) {
                    distances[edge[0]] = newDist;
                    pq.offer(new int[]{edge[0], newDist});
                }
            }
        }

        int maxDist = 0;
        for (int i = 1; i <= n; i++) {
            if (distances[i] == Integer.MAX_VALUE) return -1;
            maxDist = Math.max(maxDist, distances[i]);
        }

        return maxDist;
    }

    public static void main(String[] args) {
        int[][] times = {{2,1,1}, {2,3,1}, {3,4,1}};
        System.out.println("Network delay: " +
            networkDelayTime(times, 4, 2));
        // Output: Network delay: 2
    }
}
```

**Output:**

```
Network delay: 2
```

**Time Complexity:** O((V + E) log V) using Dijkstra's with a min-heap.

**Space Complexity:** O(V + E) for the graph and priority queue.

---

## 19.7 Problem: Cheapest Flights Within K Stops

**Problem:** There are n cities. You are given flights where `flights[i] = [from, to, price]`. Find the cheapest price from city `src` to city `dst` with at most K stops. Return -1 if no such route exists.

This is a modified shortest path problem with a constraint on the number of edges. We use a modified Bellman-Ford that runs at most K+1 iterations.

```
Example:
    0 --100--> 1 --100--> 2
    |                     ^
    +--------500----------+

src=0, dst=2, K=1
With 1 stop: 0 -> 1 -> 2 = 200
Direct: 0 -> 2 = 500
Answer: 200
```

**Python:**

```python
def find_cheapest_price(n, flights, src, dst, k):
    """
    Find cheapest flight from src to dst with at most k stops.
    Uses modified Bellman-Ford with K+1 iterations.
    """
    # distances[i] = cheapest price to reach city i
    distances = [float('inf')] * n
    distances[src] = 0

    # Run at most K+1 iterations (K stops = K+1 edges)
    for i in range(k + 1):
        # IMPORTANT: use a copy so we only use paths
        # with at most i+1 edges
        temp = distances[:]

        for u, v, price in flights:
            if distances[u] != float('inf') and \
               distances[u] + price < temp[v]:
                temp[v] = distances[u] + price

        distances = temp

    return distances[dst] if distances[dst] != float('inf') else -1


# Example 1
n = 3
flights = [[0,1,100], [1,2,100], [0,2,500]]
src, dst, k = 0, 2, 1
print(f"Cheapest price: {find_cheapest_price(n, flights, src, dst, k)}")

# Example 2
n = 3
flights = [[0,1,100], [1,2,100], [0,2,500]]
src, dst, k = 0, 2, 0
print(f"Cheapest price (0 stops): "
      f"{find_cheapest_price(n, flights, src, dst, k)}")
```

**Output:**

```
Cheapest price: 200
Cheapest price (0 stops): 500
```

**Java:**

```java
import java.util.*;

public class CheapestFlights {

    public static int findCheapestPrice(
            int n, int[][] flights, int src, int dst, int k) {

        int[] distances = new int[n];
        Arrays.fill(distances, Integer.MAX_VALUE);
        distances[src] = 0;

        for (int i = 0; i <= k; i++) {
            int[] temp = distances.clone();

            for (int[] flight : flights) {
                int u = flight[0], v = flight[1],
                    price = flight[2];
                if (distances[u] != Integer.MAX_VALUE &&
                    distances[u] + price < temp[v]) {
                    temp[v] = distances[u] + price;
                }
            }

            distances = temp;
        }

        return distances[dst] == Integer.MAX_VALUE
            ? -1 : distances[dst];
    }

    public static void main(String[] args) {
        int[][] flights = {{0,1,100}, {1,2,100}, {0,2,500}};
        System.out.println("Cheapest price: " +
            findCheapestPrice(3, flights, 0, 2, 1));
        // Output: Cheapest price: 200
    }
}
```

**Output:**

```
Cheapest price: 200
```

**Time Complexity:** O(K * E) where K is the number of allowed stops.

**Space Complexity:** O(V) for the distance arrays.

---

## Common Mistakes

1. **Using Dijkstra's with negative weights.** Dijkstra's greedy approach fails when edges can have negative weights. Use Bellman-Ford instead.

2. **Forgetting to check for visited nodes.** In Dijkstra's with a priority queue, you might pop a vertex that was already processed with a shorter distance. Always check.

3. **Not copying the distance array in modified Bellman-Ford.** When limiting the number of edges (like the cheapest flights problem), you must use a copy to prevent using more edges than allowed in a single iteration.

4. **Integer overflow with infinity.** When using `Integer.MAX_VALUE` as infinity in Java, adding a weight to it causes overflow. Always check `distances[u] != Integer.MAX_VALUE` before adding.

5. **Confusing directed and undirected graphs.** For undirected graphs, remember to add edges in both directions when building the adjacency list.

---

## Best Practices

1. **Start with the right algorithm.** Use the decision tree in Section 19.5 to choose the correct algorithm for your problem constraints.

2. **Use adjacency lists for sparse graphs.** Most real-world graphs are sparse. Adjacency lists use O(V + E) space versus O(V^2) for matrices.

3. **Add early termination.** In Dijkstra's, if you only need the distance to one target, stop as soon as you pop it from the priority queue. In Bellman-Ford, stop if no updates occur in an iteration.

4. **Consider the constraint on path length.** If the problem limits the number of edges you can use, modified Bellman-Ford is the right choice.

5. **Use path reconstruction when needed.** Store parent pointers during relaxation so you can reconstruct the actual shortest path, not just its cost.

---

## Quick Summary

```
Dijkstra's:   Single source, no negative weights
              O((V+E) log V) with priority queue
              Greedy: always process the closest vertex

Bellman-Ford: Single source, handles negative weights
              O(V*E), can detect negative cycles
              Relax all edges V-1 times

Floyd-Warshall: All pairs shortest paths
                O(V^3), simple triple-nested loop
                DP: try each vertex as intermediate
```

## Key Points

- Dijkstra's algorithm is a greedy algorithm that always picks the closest unvisited vertex, similar to how GPS navigation works.
- Dijkstra's requires non-negative edge weights because its greedy assumption breaks with negative edges.
- Bellman-Ford relaxes all edges V-1 times and can detect negative weight cycles.
- Floyd-Warshall computes shortest paths between all pairs using dynamic programming in O(V^3).
- The priority queue implementation of Dijkstra's is critical for performance: O((V+E) log V) versus O(V^2) for the naive approach.
- Path reconstruction requires storing parent/predecessor information during the algorithm.

---

## Practice Questions

1. Explain why Dijkstra's algorithm fails with negative edge weights. Give a concrete example.

2. What is the maximum number of edges in the shortest path between two vertices in a graph with V vertices? Why does Bellman-Ford use exactly V-1 iterations?

3. Can Floyd-Warshall handle negative edge weights? Can it detect negative cycles? If so, how?

4. You need to find the shortest path in a graph with 10 vertices and 15 edges, all with non-negative weights. Which algorithm would you choose and why?

5. How would you modify Dijkstra's algorithm to find the shortest path from a source to a single specific target, rather than to all vertices?

---

## LeetCode-Style Problems

### Problem 1: Path with Minimum Effort (Medium)

You are given a 2D grid of heights. You want to travel from the top-left to the bottom-right. The effort of a path is the maximum absolute difference in heights between consecutive cells. Find the path with the minimum effort.

```python
import heapq

def minimum_effort_path(heights):
    rows, cols = len(heights), len(heights[0])
    # dist[r][c] = minimum effort to reach (r, c)
    dist = [[float('inf')] * cols for _ in range(rows)]
    dist[0][0] = 0

    pq = [(0, 0, 0)]  # (effort, row, col)

    while pq:
        effort, r, c = heapq.heappop(pq)

        if r == rows - 1 and c == cols - 1:
            return effort

        if effort > dist[r][c]:
            continue

        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                new_effort = max(effort,
                    abs(heights[nr][nc] - heights[r][c]))
                if new_effort < dist[nr][nc]:
                    dist[nr][nc] = new_effort
                    heapq.heappush(pq, (new_effort, nr, nc))

    return 0


# Test
heights = [[1,2,2],[3,8,2],[5,3,5]]
print(f"Minimum effort: {minimum_effort_path(heights)}")
# Output: Minimum effort: 2
# Path: 1->3->5->3->5 or 1->2->2->2->5, max diff = 2
```

### Problem 2: Find the City With the Smallest Number of Neighbors (Medium)

Given n cities connected by weighted edges and a distance threshold, find the city with the smallest number of cities reachable within the threshold. If there is a tie, return the city with the greatest number.

```python
def find_the_city(n, edges, distance_threshold):
    INF = float('inf')

    # Initialize distance matrix
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = w
        dist[v][u] = w

    # Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Count reachable cities within threshold
    result = -1
    min_reachable = n + 1

    for i in range(n):
        reachable = sum(1 for j in range(n)
                       if i != j and dist[i][j] <= distance_threshold)
        if reachable <= min_reachable:
            min_reachable = reachable
            result = i

    return result


# Test
n = 4
edges = [[0,1,3],[1,2,1],[1,3,4],[2,3,1]]
threshold = 4
print(f"City: {find_the_city(n, edges, threshold)}")
# Output: City: 3
```

### Problem 3: Shortest Path with Alternating Colors (Medium)

Given a directed graph with red and blue edges, find the shortest path from node 0 to every other node such that the path alternates between red and blue edges.

```python
from collections import deque

def shortest_alternating_paths(n, red_edges, blue_edges):
    # Build separate adjacency lists for red and blue
    red_graph = [[] for _ in range(n)]
    blue_graph = [[] for _ in range(n)]

    for u, v in red_edges:
        red_graph[u].append(v)
    for u, v in blue_edges:
        blue_graph[u].append(v)

    # BFS with state: (node, last_color)
    # 0 = red, 1 = blue
    INF = float('inf')
    # dist[node][color] = shortest distance
    dist = [[INF, INF] for _ in range(n)]
    dist[0][0] = 0
    dist[0][1] = 0

    queue = deque([(0, 0, 0), (0, 1, 0)])
    # (node, last_color, distance)
    visited = set()
    visited.add((0, 0))
    visited.add((0, 1))

    while queue:
        node, color, d = queue.popleft()

        # Next color must be opposite
        if color == 0:  # last was red, next must be blue
            for neighbor in blue_graph[node]:
                if (neighbor, 1) not in visited:
                    visited.add((neighbor, 1))
                    dist[neighbor][1] = d + 1
                    queue.append((neighbor, 1, d + 1))
        else:  # last was blue, next must be red
            for neighbor in red_graph[node]:
                if (neighbor, 0) not in visited:
                    visited.add((neighbor, 0))
                    dist[neighbor][0] = d + 1
                    queue.append((neighbor, 0, d + 1))

    result = []
    for i in range(n):
        min_dist = min(dist[i][0], dist[i][1])
        result.append(min_dist if min_dist != INF else -1)

    return result


# Test
n = 3
red = [[0,1],[1,2]]
blue = [[2,1]]
print(f"Distances: {shortest_alternating_paths(n, red, blue)}")
# Output: Distances: [0, 1, 2]
```

---

## What Is Next?

Now that you can find the shortest path through any weighted graph, you are ready to explore a powerful optimization technique that underlies Floyd-Warshall and many other algorithms: **Dynamic Programming**. In Chapter 20, you will learn how DP works by breaking problems into overlapping subproblems and storing their solutions, transforming exponential algorithms into polynomial ones.
