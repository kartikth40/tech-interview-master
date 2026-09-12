# ALGORITHM: Cycle Detection in a Directed Graph (DFS, 3-state)
# CATEGORY: Graph / DFS
# DIFFICULTY: Medium | FREQUENCY: Very High (course schedule / deadlock detection at all companies)

# PROBLEM:
# Determine whether a directed graph contains a cycle.

# INTUITION:
# Track two sets: `visited` (fully processed) and `path_visited` (nodes on the current DFS path,
# i.e. the recursion stack). Revisiting a node that's on the current path means a back edge -> cycle.
# This is the "white/gray/black" 3-coloring idea.

# TIME: O(V + E)  |  SPACE: O(V)

# COMMON MISTAKES:
# - Using a single visited set (works for undirected, NOT directed cycle detection).
# - Forgetting to remove the node from path_visited when backtracking.
# - Not iterating over all nodes for disconnected graphs.

# RELATED PROBLEMS:
# - Course Schedule (LC 207)
# - Find Eventual Safe States (LC 802)
# - Course Schedule II (LC 210)


def has_cycle(graph: dict[int, list[int]]) -> bool:
    visited: set[int] = set()
    path_visited: set[int] = set()  # nodes on the current DFS path

    def dfs(node: int) -> bool:
        if node in path_visited:
            return True   # cycle found
        if node in visited:
            return False  # already processed, no cycle from here

        visited.add(node)
        path_visited.add(node)

        for nei in graph[node]:
            if dfs(nei):
                return True

        path_visited.remove(node)
        return False

    for node in graph:
        if node not in visited and dfs(node):
            return True

    return False


if __name__ == "__main__":
    graph = {
        0: [1],
        1: [2],
        2: [3],
        3: [0, 4],
        4: [],
    }
    print(has_cycle(graph))  # True
