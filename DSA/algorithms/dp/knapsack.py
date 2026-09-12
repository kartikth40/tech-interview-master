# ALGORITHM: 0/1 Knapsack
# CATEGORY: 2D DP / Knapsack
# DIFFICULTY: Medium | FREQUENCY: High (knapsack family + subset-sum at Google/Amazon)

# PROBLEM:
# Given n items with weights and values, and a knapsack of capacity W, find the maximum value you
# can carry. Each item can be used at most once.

# INTUITION:
# dp[i][w] = max value using the first i items with capacity w.
# For each item: take it (if it fits) or skip it.
# dp[i][w] = max(dp[i-1][w], dp[i-1][w - weight[i]] + value[i]).

# TIME: O(n * W)  |  SPACE: O(n * W), optimizable to O(W)

# COMMON MISTAKES:
# - Wrong iteration direction in the 1D optimization (must go right-to-left for 0/1).
# - Confusing 0/1 knapsack (right-to-left) with unbounded (left-to-right).
# - Off-by-one between 1-indexed dp and 0-indexed items.

# RELATED PROBLEMS:
# - Partition Equal Subset Sum (LC 416)
# - Target Sum (LC 494)
# - Last Stone Weight II (LC 1049)
# - Ones and Zeroes (LC 474)


# 2D approach
def knapsack(weights: list[int], values: list[int], W: int) -> int:
    n = len(weights)
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(W + 1):
            dp[i][w] = dp[i - 1][w]  # skip item i
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    dp[i][w],
                    dp[i - 1][w - weights[i - 1]] + values[i - 1],  # take item i
                )

    return dp[n][W]


# Space-optimized 1D approach (O(W) space)
# Key: iterate w from RIGHT to LEFT so we don't overwrite values we still need.
def knapsack_optimized(weights: list[int], values: list[int], W: int) -> int:
    n = len(weights)
    dp = [0] * (W + 1)

    for i in range(n):
        for w in range(W, weights[i] - 1, -1):  # RIGHT to LEFT
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])

    return dp[W]


# Subset Sum - can we make target sum from the array?
# Special case of 0/1 knapsack where value == weight.
def subset_sum(nums: list[int], target: int) -> bool:
    dp = [False] * (target + 1)
    dp[0] = True

    for num in nums:
        for t in range(target, num - 1, -1):  # RIGHT to LEFT
            dp[t] = dp[t] or dp[t - num]

    return dp[target]


# Partition Equal Subset Sum - can we split the array into two equal-sum subsets?
# Reduces to: subset_sum(nums, total // 2).
def can_partition(nums: list[int]) -> bool:
    total = sum(nums)
    if total % 2 != 0:
        return False
    return subset_sum(nums, total // 2)


if __name__ == "__main__":
    print(knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7))            # 9
    print(knapsack_optimized([1, 3, 4, 5], [1, 4, 5, 7], 7))  # 9
    print(subset_sum([3, 34, 4, 12, 5, 2], 9))                # True
    print(can_partition([1, 5, 11, 5]))                       # True
    print(can_partition([1, 2, 3, 5]))                        # False
