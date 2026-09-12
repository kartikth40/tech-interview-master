# ALGORITHM: Floyd-Warshall (All-Pairs Shortest Path)
# CATEGORY: Graph / Dynamic Programming / Shortest Path
# DIFFICULTY: Medium | FREQUENCY: Medium (all-pairs distances, transitive closure at Google/Amazon)

# Solves cyclic and acyclic graphs with negative weights (but no negative cycles).
# Time Complexity: O(V^3)  |  Space Complexity: O(V^2)
# For multiple sources with non-negative weights, running Dijkstra per source can be faster.

# CORE IDEA (INTUITION):
# DP over intermediate vertices: for each k, a path i->j may improve by going i->k->j.
# dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]).

# INVARIANTS:
# - After considering intermediate vertex k, dist reflects shortest paths using only {0..k} as intermediates.
# - Updates happen in place.

# STEP-BY-STEP:
# 1. Init dist with direct edge weights; inf for no edge, 0 on the diagonal.
# 2. For each intermediate k, for each pair (i, j): relax through k.
# 3. A negative diagonal entry signals a negative-weight cycle.

# COMMON MISTAKES:
# - Wrong loop order: the intermediate k MUST be the outermost loop.
# - Not initializing the diagonal to 0.
# - Ignoring negative-cycle detection (dist[i][i] < 0).

# RELATED PROBLEMS:
# - Find the City With the Smallest Number of Neighbors at a Threshold Distance (LC 1334)
# - Course Schedule IV (LC 1462) - transitive closure variant


def floyd_warshall(graph: dict[int, dict[int, int]]) -> list[list[float]]:
    # Build the distance matrix from an adjacency-map representation.
    node_keys = list(graph.keys())
    V = len(node_keys)
    dist: list[list[float]] = [[float("inf")] * V for _ in range(V)]

    for i in range(V):
        for j in range(V):
            src, dst = node_keys[i], node_keys[j]
            if i == j:
                dist[i][j] = 0
            elif dst in graph.get(src, {}):
                dist[i][j] = graph[src][dst]

    # Core Floyd-Warshall
    for intermediate in range(V):
        for source in range(V):
            for destination in range(V):
                new_path = dist[source][intermediate] + dist[intermediate][destination]
                if new_path < dist[source][destination]:
                    dist[source][destination] = new_path

    # Negative-cycle check
    for i in range(V):
        if dist[i][i] < 0:
            raise ValueError("Graph contains a negative weight cycle")

    return dist


# Example usage:
if __name__ == "__main__":
    graph = {
        0: {1: 3, 2: 6},
        1: {2: 2, 3: 1},
        2: {3: 1},
        3: {0: 4},
    }
    print(floyd_warshall(graph))
    # [[0, 3, 5, 4], [5, 0, 2, 1], [5, 8, 0, 1], [4, 7, 9, 0]]
