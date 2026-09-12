# ALGORITHM: Bipartite Graph Check (BFS + DFS 2-coloring)
# CATEGORY: Graph / Coloring
# DIFFICULTY: Medium | FREQUENCY: High (bipartition / conflict-grouping at Google/Amazon/Meta)

# A bipartite graph's vertices split into two disjoint sets U and V such that every edge connects a
# vertex in U to one in V (no edges within a set).
# Equivalent condition: a graph is bipartite iff it has NO odd-length cycle.

# Algorithm (2-coloring):
#   1. Start from an uncolored node, assign color 0.
#   2. Traverse (BFS or DFS), coloring each neighbor the opposite color.
#      If a neighbor already has the SAME color as the current node -> not bipartite.
#   3. Repeat for all components (graph may be disconnected).

# TIME: O(V + E)  |  SPACE: O(V)

# COMMON MISTAKES:
# - Not handling disconnected components (must try every uncolored node).
# - Coloring on dequeue instead of when discovering a neighbor.
# - Treating an already-correctly-colored neighbor as a conflict.

# RELATED PROBLEMS:
# - Is Graph Bipartite? (LC 785)
# - Possible Bipartition (LC 886)

from collections import deque


def is_bipartite(graph: dict[int, list[int]]) -> bool:
    colors: dict[int, int] = {node: -1 for node in graph}  # -1 = uncolored

    def bfs_check(start: int) -> bool:
        queue: deque[int] = deque([start])
        colors[start] = 0

        while queue:
            current = queue.popleft()
            for nei in graph[current]:
                if colors[nei] == -1:
                    colors[nei] = 1 - colors[current]
                    queue.append(nei)
                elif colors[nei] == colors[current]:
                    return False  # coloring conflict
        return True

    for node in graph:
        if colors[node] == -1 and not bfs_check(node):
            return False

    return True


# Bipartite check using DFS
def is_bipartite_dfs(graph: dict[int, list[int]]) -> bool:
    colors: dict[int, int] = {node: -1 for node in graph}

    def dfs_check(node: int, color: int) -> bool:
        colors[node] = color
        for nei in graph[node]:
            if colors[nei] == -1:
                if not dfs_check(nei, 1 - color):
                    return False
            elif colors[nei] == colors[node]:
                return False
        return True

    for node in graph:
        if colors[node] == -1 and not dfs_check(node, 0):
            return False

    return True


if __name__ == "__main__":
    graph = {  # not bipartite (odd-length cycle)
        0: [1, 2],
        1: [0, 3],
        2: [0, 4],
        3: [4, 1],
        4: [3, 2],
    }
    graph2 = {  # bipartite
        0: [1, 2],
        1: [0, 3],
        2: [0, 4],
        3: [5, 1],
        4: [5, 2],
        5: [3, 4],
    }
    print("Graph  - BFS:", is_bipartite(graph))    # False
    print("Graph2 - BFS:", is_bipartite(graph2))   # True
    print("Graph  - DFS:", is_bipartite_dfs(graph))   # False
    print("Graph2 - DFS:", is_bipartite_dfs(graph2))  # True
