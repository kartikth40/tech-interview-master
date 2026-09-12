# ALGORITHM: Cycle Detection in an Undirected Graph (DFS)
# CATEGORY: Graph / DFS
# DIFFICULTY: Medium | FREQUENCY: High (redundant-connection / cycle checks at Google/Amazon)

# PROBLEM:
# Determine whether an undirected graph contains a cycle.

# INTUITION:
# DFS while tracking the parent of each node. If we reach an already-visited neighbor that is NOT
# the parent, we've found a back edge -> cycle. (Union-Find is an alternative approach.)

# TIME: O(V + E)  |  SPACE: O(V)

# COMMON MISTAKES:
# - Forgetting to pass/skip the parent (every edge looks like a "cycle" otherwise).
# - Not handling disconnected components (iterate over all nodes).
# - Confusing this with directed cycle detection (which needs the recursion-stack set).

# RELATED PROBLEMS:
# - Graph Valid Tree (LC 261)
# - Redundant Connection (LC 684)
# - Number of Connected Components in an Undirected Graph (LC 323)


def has_cycle(graph: dict[int, list[int]]) -> bool:
    visited: set[int] = set()

    def dfs(node: int, parent: int) -> bool:
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                # back edge -> cycle detected
                return True
        return False

    # Check all nodes to handle disconnected components
    for node in graph:
        if node not in visited:
            if dfs(node, -1):
                return True
    return False


if __name__ == "__main__":
    graph = {
        0: [1, 2],
        1: [0, 3],
        2: [0, 3],
        3: [1, 2],
    }
    print(has_cycle(graph))  # True
