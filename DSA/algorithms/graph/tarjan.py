# ALGORITHM: Tarjan's Algorithm for Bridges (Critical Connections)
# CATEGORY: Graph / DFS / Low-Link
# DIFFICULTY: Hard | FREQUENCY: Medium (critical-connections / network-reliability at Google/Meta)

# PROBLEM STATEMENT:
# Given a graph with n vertices and a list of connections (edges), find all critical connections.
# A critical connection (bridge) is an edge whose removal disconnects some vertices.

# WHEN TO USE:
# - Find all bridges in an undirected graph.
# - Analyze network reliability / critical connections.
# - Connectivity problems (articulation points are a close variant).

# CORE IDEA (INTUITION):
# 1. DFS assigning each vertex a discovery time.
# 2. Track low[v] = earliest discovery time reachable from v's subtree (via tree + back edges).
# 3. Edge (u, v) is a bridge iff low[v] > disc[u]: v cannot reach u or an ancestor without (u, v).

# INVARIANTS:
# - Each vertex is visited once during DFS.
# - Discovery times increase as vertices are first visited.
# - low values are updated from back edges and child subtrees.

# TIME: O(V + E)  |  SPACE: O(V) (+ recursion stack)

# COMMON MISTAKES:
# - Not updating low correctly from back edges.
# - Forgetting the bridge check after returning from a child DFS.
# - Mishandling the parent edge in an undirected graph.

# RELATED PROBLEMS:
# - Critical Connections in a Network (LC 1192)
# - Articulation points (classic variant)


def critical_connections(n: int, connections: list[list[int]]) -> list[list[int]]:
    # Build adjacency list
    graph: list[list[int]] = [[] for _ in range(n)]
    for u, v in connections:
        graph[u].append(v)
        graph[v].append(u)

    disc = [-1] * n  # discovery time
    low = [-1] * n   # lowest reachable discovery time
    time = 0
    result: list[list[int]] = []

    def dfs(node: int, parent: int) -> None:
        nonlocal time
        disc[node] = time
        low[node] = time
        time += 1

        for neighbor in graph[node]:
            if neighbor == parent:
                continue  # skip the edge we came from

            if disc[neighbor] == -1:
                # tree edge
                dfs(neighbor, node)
                low[node] = min(low[node], low[neighbor])
                # bridge condition
                if low[neighbor] > disc[node]:
                    result.append([node, neighbor])
            else:
                # back edge
                low[node] = min(low[node], disc[neighbor])

    dfs(0, -1)  # graph assumed connected
    return result


if __name__ == "__main__":
    print(critical_connections(4, [[0, 1], [1, 2], [2, 0], [1, 3]]))  # [[1, 3]]
