# ALGORITHM: House Robber
# CATEGORY: 1D DP (Linear)
# DIFFICULTY: Medium | FREQUENCY: Very High (DP staple at Google/Amazon/Microsoft)

# PROBLEM:
# Given an array of non-negative integers representing money at each house, determine the maximum
# amount you can rob without robbing two adjacent houses.

# INTUITION:
# At each house i you either:
#   1. Rob it: nums[i] + dp[i-2] (skip the previous house).
#   2. Skip it: dp[i-1].
# dp[i] = max(dp[i-1], dp[i-2] + nums[i]).

# TIME: O(n)  |  SPACE: O(1) with optimization

# COMMON MISTAKES:
# - Robbing adjacent houses by mixing up prev1/prev2 updates.
# - For House Robber II: forgetting that first and last are adjacent (run two linear passes).

# RELATED PROBLEMS:
# - House Robber (LC 198)
# - House Robber II (LC 213) - circular
# - House Robber III (LC 337) - tree DP
# - Delete and Earn (LC 740)


def rob(nums: list[int]) -> int:
    if len(nums) == 0:
        return 0
    if len(nums) == 1:
        return nums[0]

    prev2 = 0         # dp[i-2]
    prev1 = nums[0]   # dp[i-1]

    for i in range(1, len(nums)):
        cur = max(prev1, prev2 + nums[i])
        prev2 = prev1
        prev1 = cur

    return prev1


# House Robber II (circular arrangement)
# First and last houses are adjacent, so we can't rob both.
# Solution: max(rob(0..n-2), rob(1..n-1)).
def rob_circular(nums: list[int]) -> int:
    if len(nums) == 1:
        return nums[0]

    def rob_range(start: int, end: int) -> int:
        prev2 = 0
        prev1 = 0
        for i in range(start, end + 1):
            cur = max(prev1, prev2 + nums[i])
            prev2 = prev1
            prev1 = cur
        return prev1

    return max(
        rob_range(0, len(nums) - 2),  # exclude last
        rob_range(1, len(nums) - 1),  # exclude first
    )


if __name__ == "__main__":
    print(rob([1, 2, 3, 1]))          # 4 (rob house 0 and 2)
    print(rob([2, 7, 9, 3, 1]))       # 12 (rob house 0, 2, 4)
    print(rob_circular([2, 3, 2]))     # 3
    print(rob_circular([1, 2, 3, 1]))  # 4
