# PATTERN NAME: Breadth-First Search (BFS)
# DIFFICULTY: Medium | FREQUENCY: Very High (shortest path, level order, grid BFS at all companies)

# WHEN TO USE:
# - Shortest path in unweighted graphs or grids.
# - Level-order traversal of trees.
# - Finding connected components in graphs.
# - Explore all neighbors before going deeper.
# - Examples: Shortest Path in a Grid, Word Ladder, Clone Graph.

# CORE IDEA (INTUITION):
# - Explore all neighbors at the current depth before moving to the next level.
# - Use a queue (collections.deque) to track nodes to visit next.
# - Mark nodes visited to avoid cycles and redundant work.

# INVARIANTS:
# - All nodes at the current depth are processed before the next depth.
# - Each node is visited at most once.
# - The queue maintains exploration order.
# - Distance from the start to any node is minimized (unweighted).

# COMMON MISTAKES:
# - Not marking nodes visited, leading to infinite loops.
# - Forgetting grid boundary checks.
# - Not handling the case when start == target.
# - Mixing up row and column indices.
# - Using list.pop(0) (O(n)) instead of deque.popleft().

# TIME & SPACE:
# - Time: O(V + E) (or O(m*n) on a grid).
# - Space: O(V) for the queue and visited set.

# RELATED PROBLEMS:
# - Word Ladder (LC 127)
# - Clone Graph (LC 133)
# - Rotting Oranges (LC 994)
# - Shortest Path in Binary Matrix (LC 1091)
# - Shortest Path in a Grid with Obstacles Elimination (LC 1293)
# - Sliding Puzzle (LC 773)

from collections import deque


# EXAMPLE: Shortest Path in a Grid with Obstacles Elimination
# State includes remaining eliminations, so the visited key is (row, col, remaining).
def shortest_path(grid: list[list[int]], k: int) -> int:
    m, n = len(grid), len(grid[0])

    q: deque[tuple[int, int, int, int]] = deque()
    q.append((0, 0, 0, k))  # (row, col, steps, remaining eliminations)

    visited = {(0, 0, k)}
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while q:
        row, col, steps, remaining = q.popleft()

        if row == m - 1 and col == n - 1:
            return steps

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if new_row < 0 or new_col < 0 or new_row >= m or new_col >= n:
                continue

            new_remaining = remaining - grid[new_row][new_col]
            key = (new_row, new_col, new_remaining)
            if new_remaining >= 0 and key not in visited:
                visited.add(key)
                q.append((new_row, new_col, steps + 1, new_remaining))

    return -1


if __name__ == "__main__":
    grid = [[0, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 1], [0, 0, 0]]
    print(shortest_path(grid, 1))  # 6
