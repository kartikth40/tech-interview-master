# ALGORITHM: Coin Change
# CATEGORY: Unbounded Knapsack / 1D DP
# DIFFICULTY: Medium | FREQUENCY: Very High (DP staple at Google/Amazon/Microsoft)

# PROBLEM:
# Given coins of different denominations and a total amount, find the fewest number of coins
# needed to make up that amount. Return -1 if it's not possible.

# INTUITION:
# dp[amount] = minimum coins to make 'amount'.
# For each amount, try every coin: dp[a] = min(dp[a], dp[a - coin] + 1).
# This is unbounded knapsack - each coin can be used unlimited times.

# TIME: O(amount * len(coins))  |  SPACE: O(amount)

# COMMON MISTAKES:
# - Initializing dp with 0 instead of infinity (for min problems).
# - Iterating coins in the inner loop for Coin Change II (gives permutations, not combinations).
# - Forgetting dp[0] = 0 (or dp[0] = 1 for counting).

# RELATED PROBLEMS:
# - Coin Change (LC 322)
# - Coin Change II (LC 518)
# - Perfect Squares (LC 279)
# - Minimum Cost For Tickets (LC 983)


def coin_change(coins: list[int], amount: int) -> int:
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0

    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a and dp[a - coin] != float("inf"):
                dp[a] = min(dp[a], dp[a - coin] + 1)

    return -1 if dp[amount] == float("inf") else dp[amount]


# Coin Change II - count the number of combinations that make up amount.
# dp[a] = number of ways to make amount 'a'.
# Key: iterate coins in the OUTER loop to avoid counting permutations.
def coin_change_ii(coins: list[int], amount: int) -> int:
    dp = [0] * (amount + 1)
    dp[0] = 1

    for coin in coins:              # outer: coins (combinations, not permutations)
        for a in range(coin, amount + 1):
            dp[a] += dp[a - coin]

    return dp[amount]


if __name__ == "__main__":
    print(coin_change([1, 5, 10, 25], 30))  # 2 (25 + 5)
    print(coin_change([2], 3))               # -1
    print(coin_change_ii([1, 2, 5], 5))      # 4 ways
