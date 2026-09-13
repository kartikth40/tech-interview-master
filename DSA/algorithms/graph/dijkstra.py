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
    # Size the distance array by the highest node label seen (as a key OR a neighbor), so a sink
    # node that never appears as a key still gets a slot. Assumes nodes are labeled 0..n-1.
    max_node = src
    for node, edges in graph.items():
        max_node = max(max_node, node)
        for nei, _ in edges:
            max_node = max(max_node, nei)
    dist: list[float] = [float("inf")] * (max_node + 1)
    dist[src] = 0

    pq: list[tuple[float, int]] = [(0, src)]  # (dist, node)

    while pq:
        d, node = heapq.heappop(pq)
        if d > dist[node]:
            continue

        # graph.get(node, []) is safe for sink nodes that have no outgoing-edge entry.
        for nei, w in graph.get(node, []):
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
# - Indexing graph[node] directly: a sink node with no outgoing edges may be absent as a key
#   (KeyError). Use graph.get(node, []). This code assumes nodes are labeled 0..n-1.

# RELATED PROBLEMS:
# - Network Delay Time (LC 743)
# - Path with Maximum Probability (LC 1514)
# - Cheapest Flights Within K Stops (LC 787)
# - Swim in Rising Water (LC 778)


# === DIJKSTRA WITH STATE: Cheapest Flights Within K Stops (LC 787) ===
# When the answer depends on MORE than distance (here: number of stops used), add that dimension to
# the heap state. The heap holds (cost, node, stops_remaining). We may revisit a node with more
# stops remaining even at higher cost, so the usual "visited"/stale-entry pruning does NOT apply the
# same way - we prune only when we reach a node with fewer stops remaining than a prior better state.
def find_cheapest_price(n: int, flights: list[list[int]], src: int, dst: int, k: int) -> int:
    graph: dict[int, list[tuple[int, int]]] = {i: [] for i in range(n)}
    for u, v, w in flights:
        graph[u].append((v, w))

    # best[node] = max stops_remaining seen at this node (prune worse states)
    best_stops: dict[int, int] = {}
    pq: list[tuple[int, int, int]] = [(0, src, k + 1)]  # (cost, node, stops_remaining)

    while pq:
        cost, node, stops = heapq.heappop(pq)
        if node == dst:
            return cost
        if stops == 0:
            continue
        # Prune: if we've already reached this node with >= stops remaining, skip.
        if node in best_stops and best_stops[node] >= stops:
            continue
        best_stops[node] = stops
        for nei, w in graph[node]:
            heapq.heappush(pq, (cost + w, nei, stops - 1))

    return -1


# Example usage:
if __name__ == "__main__":
    graph: dict[int, list[tuple[int, int]]] = {
        0: [(1, 4), (2, 1)],
        1: [(3, 1)],
        2: [(1, 2), (3, 5)],
        3: [],
    }

    print(dijkstra(graph, 0))  # [0, 3, 1, 4]

    # Cheapest Flights Within K Stops
    flights = [[0, 1, 100], [1, 2, 100], [0, 2, 500]]
    print(find_cheapest_price(3, flights, 0, 2, 1))  # 200 (0->1->2)
    print(find_cheapest_price(3, flights, 0, 2, 0))  # 500 (direct only)
