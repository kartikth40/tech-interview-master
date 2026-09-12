# ALGORITHM: Dijkstra's Algorithm (Single Source Shortest Path)
# CATEGORY: Graph / Greedy / Shortest Path
# DIFFICULTY: Medium | FREQUENCY: Very High (graph shortest-path staple at Google/Amazon/Uber)

# Can solve for cyclic and acyclic graphs with non-negative weights.
# Greedy Algorithm.
# Time Complexity: O((V + E) log V) where V is the number of vertices and E is the number of edges.

# Greedy choice: always expand the least costly node first.
# Finds the shortest path from source to all other nodes in the graph.
# Can't find shortest paths with constraints on number of edges or negative weights (Bellman-Ford can).

# NOTE: The JavaScript version used a custom MinPriorityQueue. In Python, the standard library `heapq`
# is the idiomatic min-priority-queue, so we use it directly. Entries are (distance, node) tuples,
# which heapq orders by distance first.

import heapq


def dijkstra(graph: dict[int, list[tuple[int, int]]], src: int) -> list[float]:
    n = len(graph)
    dist: list[float] = [float("inf")] * n
    dist[src] = 0

    pq: list[tuple[float, int]] = [(0, src)]  # (dist, node)

    while pq:
        d, node = heapq.heappop(pq)
        if d > dist[node]:
            continue

        for nei, w in graph[node]:
            nd = d + w
            if nd < dist[nei]:
                dist[nei] = nd
                heapq.heappush(pq, (nd, nei))

    return dist


# COMMON MISTAKES:
# - Using Dijkstra with negative edge weights (use Bellman-Ford instead).
# - Forgetting the "if d > dist[node]: continue" stale-entry check (heapq has no decrease-key).
# - Initializing distances to 0 instead of infinity.
# - Pushing (node, dist) instead of (dist, node) so heapq orders by the wrong field.

# RELATED PROBLEMS:
# - Network Delay Time (LC 743)
# - Path with Maximum Probability (LC 1514)
# - Cheapest Flights Within K Stops (LC 787)
# - Swim in Rising Water (LC 778)


# Example usage:
if __name__ == "__main__":
    graph: dict[int, list[tuple[int, int]]] = {
        0: [(1, 4), (2, 1)],
        1: [(3, 1)],
        2: [(1, 2), (3, 5)],
        3: [],
    }

    print(dijkstra(graph, 0))  # [0, 3, 1, 4]
