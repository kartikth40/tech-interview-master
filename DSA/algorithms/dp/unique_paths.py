# ALGORITHM: Unique Paths
# CATEGORY: 2D DP (Grid)
# DIFFICULTY: Medium | FREQUENCY: High (grid DP staple at Google/Amazon/Microsoft)

# PROBLEM:
# A robot is at the top-left corner of an m x n grid. It can only move right or down.
# How many unique paths exist to reach the bottom-right corner?

# INTUITION:
# dp[i][j] = number of ways to reach cell (i, j).
# dp[i][j] = dp[i-1][j] + dp[i][j-1]  (from above + from left).

# TIME: O(m * n)  |  SPACE: O(n) with optimization

# COMMON MISTAKES:
# - Forgetting to zero out cells blocked by obstacles.
# - Wrong initialization for the min-path-sum variant (use +inf, seed dp[0]).
# - Mixing up row (m) and column (n) dimensions.

# RELATED PROBLEMS:
# - Unique Paths (LC 62)
# - Unique Paths II (LC 63)
# - Minimum Path Sum (LC 64)
# - Dungeon Game (LC 174)
# - Triangle (LC 120)


def unique_paths(m: int, n: int) -> int:
    dp = [1] * n  # first row is all 1s

    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]

    return dp[n - 1]


# Unique Paths II - with obstacles (grid[i][j] == 1 means obstacle).
def unique_paths_with_obstacles(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])
    if grid[0][0] == 1 or grid[m - 1][n - 1] == 1:
        return 0

    dp = [0] * n
    dp[0] = 1

    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                dp[j] = 0
            elif j > 0:
                dp[j] += dp[j - 1]

    return dp[n - 1]


# Minimum Path Sum - path with the minimum sum from top-left to bottom-right.
def min_path_sum(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])
    dp = [float("inf")] * n
    dp[0] = 0

    for i in range(m):
        dp[0] += grid[i][0]
        for j in range(1, n):
            if i == 0:
                dp[j] = dp[j - 1] + grid[i][j]
            else:
                dp[j] = min(dp[j], dp[j - 1]) + grid[i][j]

    return dp[n - 1]


if __name__ == "__main__":
    print(unique_paths(3, 7))                                          # 28
    print(unique_paths_with_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]))  # 2
    print(min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]))             # 7
