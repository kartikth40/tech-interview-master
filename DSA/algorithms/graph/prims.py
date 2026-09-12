# ALGORITHM: Prim's Minimum Spanning Tree (MST)
# CATEGORY: Graph / Greedy / MST
# DIFFICULTY: Medium | FREQUENCY: High (MST / connecting-points problems at Google/Amazon)

# Solves undirected, connected, cyclic graphs with non-negative weights.
# Greedy: always expand the least-costly edge that connects a new vertex to the growing MST.
# Time Complexity: O(E log V) with a min-heap.

# CORE IDEA (INTUITION):
# Start from an arbitrary vertex. Repeatedly pull the cheapest edge crossing from the MST to a
# vertex not yet included, add that vertex, and push its outgoing edges.

# INVARIANTS:
# - The included vertices always form a connected subtree of minimum total weight so far.
# - The heap holds candidate edges from the MST to outside vertices.

# NOTE: The JavaScript version used a custom MinPriorityQueue; here we use the standard library
# `heapq` with (weight, node) tuples so the heap orders by weight.

import heapq


def spanning_tree(V: int, edges: list[list[int]]) -> int:
    graph: list[list[tuple[int, int]]] = [[] for _ in range(V)]
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))

    visited = [False] * V
    pq: list[tuple[int, int]] = [(0, 0)]  # (weight, node)
    total = 0

    while pq:
        weight, node = heapq.heappop(pq)

        if visited[node]:
            continue
        visited[node] = True
        total += weight

        for nei, wei in graph[node]:
            if not visited[nei]:
                heapq.heappush(pq, (wei, nei))

    return total


# Example usage:
if __name__ == "__main__":
    V = 5
    edges = [
        [0, 1, 2],
        [0, 3, 6],
        [1, 2, 3],
        [1, 3, 8],
        [1, 4, 5],
        [2, 4, 7],
        [3, 4, 9],
    ]
    print(spanning_tree(V, edges))  # 16
