# PATTERN NAME: Matrix / Grid Patterns
# DIFFICULTY: Medium | FREQUENCY: Very High (islands, spiral, rotate, 2D search at all companies)

# WHEN TO USE:
# - 2D grid traversal (islands, shortest path).
# - Matrix rotation, spiral order.
# - Search in a sorted 2D matrix.
# - Flood fill, connected components in a grid.

# CORE IDEA (INTUITION):
# - Grids are implicit graphs - each cell connects to its neighbors.
# - Use DFS/BFS for traversal, a visited marker to avoid revisiting.
# - For sorted matrices: treat as a flattened sorted array or use staircase search.
# - Direction arrays simplify neighbor iteration.

# INVARIANTS:
# - Always check bounds: 0 <= row < m, 0 <= col < n.
# - Mark visited BEFORE enqueuing (BFS) to avoid duplicates.
# - 4-directional array: [(0,1),(0,-1),(1,0),(-1,0)].

# COMMON MISTAKES:
# - Forgetting bounds checks before accessing grid[r][c].
# - Marking visited AFTER enqueuing (causes duplicates in BFS).
# - Wrong direction array (4- vs 8-directional).
# - Spiral order: not re-checking top <= bottom and left <= right after each direction.

# TIME & SPACE:
# - Grid DFS/BFS: O(m*n) time, O(m*n) space.
# - Spiral / Rotate / Set Zeroes: O(m*n) time, O(1) extra space.
# - Staircase search: O(m + n) time, O(1) space.

# RELATED PROBLEMS:
# - Number of Islands (LC 200)
# - Spiral Matrix (LC 54)
# - Rotate Image (LC 48)
# - Search a 2D Matrix II (LC 240)
# - Set Matrix Zeroes (LC 73)
# - Word Search (LC 79)


# === DIRECTION HELPERS ===
DIRS_4 = [(0, 1), (0, -1), (1, 0), (-1, 0)]
DIRS_8 = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def in_bounds(r: int, c: int, m: int, n: int) -> bool:
    return 0 <= r < m and 0 <= c < n


# === NUMBER OF ISLANDS (DFS on grid) ===
def num_islands(grid: list[list[str]]) -> int:
    m, n = len(grid), len(grid[0])
    count = 0

    def dfs(r: int, c: int) -> None:
        if not in_bounds(r, c, m, n) or grid[r][c] == "0":
            return
        grid[r][c] = "0"  # mark visited by sinking
        for dr, dc in DIRS_4:
            dfs(r + dr, c + dc)

    for r in range(m):
        for c in range(n):
            if grid[r][c] == "1":
                dfs(r, c)
                count += 1

    return count


# === SPIRAL ORDER ===
def spiral_order(matrix: list[list[int]]) -> list[int]:
    result: list[int] = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1

        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1

        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1

        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1

    return result


# === ROTATE MATRIX 90 DEGREES CLOCKWISE (in-place) ===
# Step 1: transpose. Step 2: reverse each row.
def rotate(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)

    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]

    for row in matrix:
        row.reverse()

    return matrix


# === SEARCH IN SORTED MATRIX (staircase from top-right) ===
def search_matrix(matrix: list[list[int]], target: int) -> bool:
    r, c = 0, len(matrix[0]) - 1

    while r < len(matrix) and c >= 0:
        if matrix[r][c] == target:
            return True
        if matrix[r][c] > target:
            c -= 1
        else:
            r += 1

    return False


# === SET MATRIX ZEROES (O(1) space using first row/col as markers) ===
def set_zeroes(matrix: list[list[int]]) -> list[list[int]]:
    m, n = len(matrix), len(matrix[0])
    first_row_zero = any(matrix[0][c] == 0 for c in range(n))
    first_col_zero = any(matrix[r][0] == 0 for r in range(m))

    for r in range(1, m):
        for c in range(1, n):
            if matrix[r][c] == 0:
                matrix[r][0] = 0
                matrix[0][c] = 0

    for r in range(1, m):
        for c in range(1, n):
            if matrix[r][0] == 0 or matrix[0][c] == 0:
                matrix[r][c] = 0

    if first_row_zero:
        for c in range(n):
            matrix[0][c] = 0
    if first_col_zero:
        for r in range(m):
            matrix[r][0] = 0

    return matrix


if __name__ == "__main__":
    print(spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
    # [1, 2, 3, 6, 9, 8, 7, 4, 5]

    print(rotate([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
    # [[7, 4, 1], [8, 5, 2], [9, 6, 3]]

    print(search_matrix([[1, 4, 7], [2, 5, 8], [3, 6, 9]], 5))   # True
    print(search_matrix([[1, 4, 7], [2, 5, 8], [3, 6, 9]], 10))  # False
