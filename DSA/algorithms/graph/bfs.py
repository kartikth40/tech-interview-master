# ALGORITHM: Breadth-First Search (BFS)
# CATEGORY: Graph / Traversal
# DIFFICULTY: Easy | FREQUENCY: Very High (shortest path in unweighted graphs at all companies)

# PROBLEM:
# Traverse a graph level by level. BFS finds the shortest path (fewest edges) in an unweighted graph.

# INTUITION:
# Use a FIFO queue. Visit a node, enqueue all unvisited neighbors, mark them visited on enqueue
# (not on dequeue) to avoid processing a node twice.

# TIME: O(V + E)  |  SPACE: O(V)

# COMMON MISTAKES:
# - Marking visited on dequeue instead of enqueue (can enqueue the same node many times).
# - Using a list as a queue with pop(0) (O(n)); use collections.deque.
# - Forgetting the state key for multi-dimensional BFS (row, col, remaining).

# RELATED PROBLEMS:
# - Rotting Oranges (LC 994)
# - Word Ladder (LC 127)
# - Shortest Path in a Grid with Obstacles Elimination (LC 1293)

from collections import deque


# useful for shortest path in an unweighted graph
def bfs(start: int, graph: dict[int, list[int]]) -> set[int]:
    q: deque[int] = deque([start])
    visited = {start}

    while q:
        node = q.popleft()
        for nei in graph[node]:
            if nei not in visited:
                visited.add(nei)
                q.append(nei)

    return visited


# example usage:
# shortest path in a grid with obstacles elimination (state = (row, col, remaining))
def shortest_path(grid: list[list[int]], k: int) -> int:
    m, n = len(grid), len(grid[0])

    q: deque[tuple[int, int, int, int]] = deque()
    q.append((0, 0, k, 0))  # (row, col, remaining, distance)

    visited = {(0, 0, k)}

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while q:
        row, col, remaining, distance = q.popleft()
        if row == m - 1 and col == n - 1:
            return distance

        for dr, dc in directions:
            new_r = row + dr
            new_c = col + dc

            if new_r < 0 or new_c < 0 or new_r >= m or new_c >= n:
                continue

            new_remaining = remaining - grid[new_r][new_c]
            key = (new_r, new_c, new_remaining)
            if new_remaining >= 0 and key not in visited:
                visited.add(key)
                q.append((new_r, new_c, new_remaining, distance + 1))

    return -1


if __name__ == "__main__":
    graph = {0: [1, 2], 1: [0, 3], 2: [0, 3], 3: [1, 2]}
    print(sorted(bfs(0, graph)))  # [0, 1, 2, 3]

    grid = [[0, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 1], [0, 0, 0]]
    print(shortest_path(grid, 1))  # 6
