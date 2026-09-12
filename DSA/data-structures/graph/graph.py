# DATA STRUCTURE: Graph (adjacency list / matrix / edge list + builders)
# DIFFICULTY: Medium | FREQUENCY: Very High (graph representation underpins most graph problems)

# A graph is a collection of nodes (vertices) connected by edges.
# This file provides adjacency list and adjacency matrix representations,
# plus common helper utilities used across graph problems.

# Time Complexity:
# - Add vertex: O(1)
# - Add edge: O(1)
# - Remove edge: O(E) for adjacency list
# - Has edge: O(degree) for list, O(1) for matrix
# - Get neighbors: O(1) for list, O(V) for matrix
# - Space: O(V + E) for list, O(V^2) for matrix

# When to use:
# - Adjacency List: sparse graphs, most interview problems
# - Adjacency Matrix: dense graphs, Floyd-Warshall, quick edge lookup
# - Edge List: Kruskal's MST, Bellman-Ford

from collections import defaultdict

# COMMON MISTAKES:
# - Forgetting to add the reverse edge for undirected graphs.
# - Assuming a matrix value of 0 means "no edge" when 0 could be a valid weight.
# - Not initializing missing vertices (KeyError on lookup) - defaultdict avoids this.
# - Confusing neighbor tuples (node, weight) ordering across functions.

# RELATED PROBLEMS:
# - Number of Islands (LC 200)
# - Course Schedule (LC 207)
# - Clone Graph (LC 133)
# - Network Delay Time (LC 743)


# === ADJACENCY LIST (most common for interviews) ===

class Graph:
    def __init__(self, directed: bool = False) -> None:
        self.adj: dict[int, list[tuple[int, int]]] = defaultdict(list)
        self.directed = directed

    def add_vertex(self, v: int) -> None:
        # defaultdict creates the entry on first access; touch it to register isolated vertices.
        _ = self.adj[v]

    def add_edge(self, u: int, v: int, weight: int = 1) -> None:
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj[u].append((v, weight))
        if not self.directed:
            self.adj[v].append((u, weight))

    def get_neighbors(self, v: int) -> list[tuple[int, int]]:
        return self.adj.get(v, [])

    def has_edge(self, u: int, v: int) -> bool:
        if u not in self.adj:
            return False
        return any(node == v for node, _ in self.adj[u])

    def get_vertices(self) -> list[int]:
        return list(self.adj.keys())

    @property
    def size(self) -> int:
        return len(self.adj)


# === BUILD FROM COMMON INPUT FORMATS ===

# From edge list: [[0, 1], [1, 2], [2, 0]]
def build_adj_list(n: int, edges: list[list[int]], directed: bool = False) -> list[list[int]]:
    graph: list[list[int]] = [[] for _ in range(n)]

    for u, v in edges:
        graph[u].append(v)
        if not directed:
            graph[v].append(u)

    return graph


# From weighted edge list: [[0, 1, 5], [1, 2, 3]]
def build_weighted_adj_list(n: int, edges: list[list[int]], directed: bool = False) -> list[list[tuple[int, int]]]:
    graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]

    for u, v, w in edges:
        graph[u].append((v, w))
        if not directed:
            graph[v].append((u, w))

    return graph


# From adjacency matrix to adjacency list
def matrix_to_adj_list(matrix: list[list[float]]) -> list[list[int]]:
    n = len(matrix)
    graph: list[list[int]] = [[] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if matrix[i][j] != 0 and matrix[i][j] != float("inf"):
                graph[i].append(j)

    return graph


# === ADJACENCY MATRIX ===

def build_adj_matrix(n: int, edges: list[list[int]], directed: bool = False) -> list[list[int]]:
    matrix: list[list[int]] = [[0] * n for _ in range(n)]

    for edge in edges:
        u, v = edge[0], edge[1]
        w = edge[2] if len(edge) > 2 else 1
        matrix[u][v] = w
        if not directed:
            matrix[v][u] = w

    return matrix


# === UTILITY: COMPUTE INDEGREES (for topological sort / Kahn's) ===

def compute_indegrees(n: int, graph: list[list[int]]) -> list[int]:
    indegree = [0] * n

    for u in range(n):
        for v in graph[u]:
            indegree[v] += 1

    return indegree


# Examples (only run when executed directly)
if __name__ == "__main__":
    g = Graph(directed=True)
    g.add_edge(0, 1, 4)
    g.add_edge(0, 2, 1)
    g.add_edge(2, 1, 2)
    g.add_edge(1, 3, 1)
    print(g.get_neighbors(0))   # [(1, 4), (2, 1)]
    print(g.has_edge(0, 1))     # True
    print(g.has_edge(1, 0))     # False (directed)
    print(g.size)               # 4

    adj = build_adj_list(4, [[0, 1], [1, 2], [2, 3], [3, 0]])
    print(adj)  # [[1, 3], [0, 2], [1, 3], [2, 0]]

    weighted = build_weighted_adj_list(3, [[0, 1, 5], [1, 2, 3], [0, 2, 10]])
    print(weighted)  # [[(1, 5), (2, 10)], [(0, 5), (2, 3)], [(1, 3), (0, 10)]]

    matrix = build_adj_matrix(3, [[0, 1, 2], [1, 2, 3], [0, 2, 7]])
    print(matrix)  # [[0, 2, 7], [2, 0, 3], [7, 3, 0]]
