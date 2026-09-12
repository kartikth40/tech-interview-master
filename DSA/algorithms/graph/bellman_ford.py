# ALGORITHM: Bellman-Ford (Single Source Shortest Path with negative weights)
# CATEGORY: Graph / Dynamic Programming / Shortest Path
# DIFFICULTY: Medium | FREQUENCY: Medium (negative weights, cheapest-flights at Amazon/Google)

# WHEN TO USE:
# - Shortest path in a graph that may contain negative-weight edges.
# - When the graph is given as an edge list.
# - When you need to detect negative-weight cycles.

# Dijkstra vs Bellman-Ford:
# - Dijkstra is faster for non-negative weights: O((V + E) log V) with a heap.
# - Bellman-Ford is O(V * E) but handles negative weights and detects negative cycles.
# - Dijkstra is greedy; Bellman-Ford is DP (relax all edges V-1 times).

# CORE IDEA (INTUITION):
# Relax every edge V-1 times. After the i-th pass, the shortest path using at most i edges is known.
# A V-th pass that still relaxes an edge proves a negative cycle exists.

# INVARIANTS:
# - After pass i, shortest paths using at most i edges are correct.
# - If any edge still relaxes after V-1 passes, a negative-weight cycle exists.

# TIME: O(V * E)  |  SPACE: O(V)

# COMMON MISTAKES:
# - Relaxing an edge from an unreachable node (skip when dist[u] is infinity).
# - Running V passes instead of V-1 for the main loop.
# - Forgetting the extra pass that detects negative cycles.

# RELATED PROBLEMS:
# - Cheapest Flights Within K Stops (LC 787)
# - Network Delay Time (LC 743)


def bellman_ford(V: int, edges: list[list[int]], src: int) -> list[float]:
    INF = float("inf")
    dist: list[float] = [INF] * V
    dist[src] = 0

    for _ in range(V - 1):
        for u, v, w in edges:
            if dist[u] == INF:  # must reach u before relaxing v
                continue
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    # Negative-cycle detection
    for u, v, w in edges:
        if dist[u] == INF:
            continue
        if dist[u] + w < dist[v]:
            return [-1]

    return dist


# Example usage:
if __name__ == "__main__":
    V = 5
    edges = [
        [0, 1, 100],
        [1, 2, 100],
        [0, 2, 500],
        [2, 3, 100],
        [3, 4, 100],
        [1, 4, 600],
    ]
    print(bellman_ford(V, edges, 0))  # [0, 100, 200, 300, 400]
