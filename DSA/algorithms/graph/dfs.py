# ALGORITHM: Depth-First Search (DFS)
# CATEGORY: Graph / Traversal
# DIFFICULTY: Easy | FREQUENCY: Very High (connected components, flood fill at all companies)

# PROBLEM:
# Traverse all nodes of a graph depth-first. Foundation for connected components, cycle detection,
# topological sort, flood fill, and tree recursion.

# INTUITION:
# Visit a node, mark it, then recurse into each unvisited neighbor. On a grid, treat cells as nodes
# and the 4 (or 8) directions as edges.

# TIME: O(V + E)  |  SPACE: O(V) for the visited set + recursion stack

# COMMON MISTAKES:
# - Forgetting to mark a node visited before recursing (infinite loop on cycles).
# - Grid DFS: missing bounds/visited/obstacle checks at the top of the function.
# - Hitting Python's recursion limit on very deep graphs (use an explicit stack if needed).

# RELATED PROBLEMS:
# - Number of Islands (LC 200)
# - Max Area of Island (LC 695)
# - Clone Graph (LC 133)


# useful for traversing all nodes in a graph depth-wise
def dfs(node: int, graph: dict[int, list[int]], visited: set[int] | None = None) -> None:
    if visited is None:
        visited = set()
    if node in visited:
        return
    visited.add(node)

    for nei in graph[node]:
        dfs(nei, graph, visited)


# example usage:
# number of islands in a grid
def num_islands(grid: list[list[str]]) -> int:
    res = 0
    m, n = len(grid), len(grid[0])

    visited = [[False] * n for _ in range(m)]

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def island_dfs(i: int, j: int) -> None:
        if i < 0 or j < 0 or i >= m or j >= n or visited[i][j] or grid[i][j] == "0":
            return

        visited[i][j] = True

        for dr, dc in directions:
            island_dfs(i + dr, j + dc)

    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1" and not visited[i][j]:
                res += 1
                island_dfs(i, j)
    return res


# example usage:
# get the subtree size for each node in a tree
def get_subtree_sizes(node: int, graph: dict[int, list[int]],
                      visited: set[int] | None = None, sizes: dict[int, int] | None = None) -> int:
    if visited is None:
        visited = set()
    if sizes is None:
        sizes = {}
    if node in visited:
        return 0
    visited.add(node)

    size = 1  # count the current node
    for child in graph[node]:
        if child not in visited:
            size += get_subtree_sizes(child, graph, visited, sizes)

    sizes[node] = size
    return size


if __name__ == "__main__":
    grid = [
        ["1", "1", "0", "0"],
        ["1", "0", "0", "1"],
        ["0", "0", "1", "1"],
    ]
    print(num_islands(grid))  # 2
