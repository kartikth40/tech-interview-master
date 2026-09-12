# ALGORITHM: Climbing Stairs
# CATEGORY: 1D DP (Linear)
# DIFFICULTY: Easy | FREQUENCY: Very High (intro DP question at all companies)

# PROBLEM:
# You are climbing a staircase that takes n steps to reach the top.
# Each time you can climb 1 or 2 steps. In how many distinct ways can you climb to the top?

# INTUITION:
# To reach step i, you either came from step i-1 (1 step) or step i-2 (2 steps).
# dp[i] = dp[i-1] + dp[i-2]  (same as Fibonacci).

# TIME: O(n)  |  SPACE: O(1) with optimization

# COMMON MISTAKES:
# - Off-by-one on base cases (dp[1] = 1, dp[2] = 2).
# - Recomputing Fibonacci recursively without memoization (exponential blow-up).

# RELATED PROBLEMS:
# - Min Cost Climbing Stairs (LC 746)
# - Fibonacci Number (LC 509)
# - Decode Ways (LC 91)
# - House Robber (LC 198)


# DP approach (O(n) space)
def climb_stairs(n: int) -> int:
    if n <= 2:
        return n

    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2

    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


# Space-optimized (O(1) space)
def climb_stairs_optimized(n: int) -> int:
    if n <= 2:
        return n

    prev2 = 1  # dp[i-2]
    prev1 = 2  # dp[i-1]

    for _ in range(3, n + 1):
        cur = prev1 + prev2
        prev2 = prev1
        prev1 = cur

    return prev1


if __name__ == "__main__":
    print(climb_stairs(5))            # 8
    print(climb_stairs_optimized(5))  # 8
    print(climb_stairs(10))           # 89
