# PATTERN NAME: DP - Dynamic Programming

# DIFFICULTY: Hard | FREQUENCY: Very High (broad DP family at Google/Meta/Amazon/Microsoft)

# WHEN TO USE:
# - Problems that can be broken down into overlapping subproblems.
# - Optimal substructure property.
# - Problems involving sequences, paths, or combinations.
# - Examples: Fibonacci, Knapsack, Coin Change, Longest Common Subsequence.

# CORE IDEA (INTUITION):
# - Store results of subproblems to avoid redundant calculations.
# - Build up solutions to larger problems using solutions to smaller problems.

# INVARIANTS:
# - Subproblem solutions are reused.
# - Optimal solutions are constructed from optimal subproblem solutions.
# - State representation is crucial (e.g., indices, remaining capacity).

# COMMON MISTAKES:
# - Not identifying overlapping subproblems.
# - Ignoring base cases.
# - Incorrect state representation.
# - Failing to memoize or store subproblem results.
# - Off-by-one errors in indexing.
# - Not considering all possible transitions between states.

# TIME & SPACE:
# - Depends on state space * transition cost; typically O(states * transitions).

# RELATED PROBLEMS:
# - Jump Game II (LC 45)
# - Best Time to Buy and Sell Stock with Cooldown (LC 309)
# - Edit Distance (LC 72)
# - Longest Common Subsequence (LC 1143)
# - Best Time to Buy and Sell Stock III (LC 123)
# - Word Break (LC 139)
# - Palindrome Partitioning II (LC 132)
# - Minimum Edge Reversals (LC 2858) - rerooting DP

from functools import lru_cache


# === Jump Game II ===

# Greedy Optimal - O(n)
def jump_greedy(nums: list[int]) -> int:
    far = end = jumps = 0
    for i in range(len(nums) - 1):
        far = max(far, i + nums[i])
        if i == end:
            jumps += 1
            end = far
    return jumps


# Top-Down DP (Memoization) - O(n^2) worst
def jump_memo(nums: list[int]) -> int:
    n = len(nums)

    @lru_cache(maxsize=None)
    def dfs(i: int) -> int:
        if i >= n - 1:
            return 0
        min_jumps = float("inf")
        for step in range(1, nums[i] + 1):
            if i + step < n:
                min_jumps = min(min_jumps, 1 + dfs(i + step))
        return min_jumps

    return dfs(0)


# Bottom-Up - O(n^2) worst
def jump_bottom_up(nums: list[int]) -> int:
    n = len(nums)
    dp = [float("inf")] * n
    dp[n - 1] = 0
    for i in range(n - 2, -1, -1):
        for step in range(1, nums[i] + 1):
            if i + step < n:
                dp[i] = min(dp[i], 1 + dp[i + step])
    return int(dp[0])


# === Best Time to Buy and Sell Stock with Cooldown ===
# State: (day, can_buy). Selling forces a cooldown (skip the next day).
def max_profit_cooldown(prices: list[int]) -> int:
    n = len(prices)

    @lru_cache(maxsize=None)
    def dfs(day: int, can_buy: int) -> int:
        if day >= n:
            return 0
        if can_buy:
            buy = dfs(day + 1, 0) - prices[day]
            skip = dfs(day + 1, 1)
            return max(buy, skip)
        sell = dfs(day + 2, 1) + prices[day]  # cooldown: jump 2 days
        hold = dfs(day + 1, 0)
        return max(sell, hold)

    return dfs(0, 1)


# === Edit Distance (Bottom-Up) ===
def min_distance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


# === Best Time to Buy and Sell Stock III (at most 2 transactions) ===
def max_profit_two_transactions(prices: list[int]) -> int:
    n = len(prices)

    @lru_cache(maxsize=None)
    def dfs(day: int, holding: int, transactions_left: int) -> int:
        if day == n or transactions_left == 0:
            return 0
        if holding == 0:  # can buy
            return max(
                -prices[day] + dfs(day + 1, 1, transactions_left),
                dfs(day + 1, 0, transactions_left),
            )
        return max(  # can sell
            prices[day] + dfs(day + 1, 0, transactions_left - 1),
            dfs(day + 1, 1, transactions_left),
        )

    return dfs(0, 0, 2)


# === Word Break (Bottom-Up) ===
def word_break(s: str, word_dict: list[str]) -> bool:
    dp = [False] * (len(s) + 1)
    dp[0] = True
    words = set(word_dict)
    for i in range(len(s)):
        if not dp[i]:
            continue
        for j in range(i, len(s)):
            if s[i:j + 1] in words:
                dp[j + 1] = True
    return dp[len(s)]


# === Palindrome Partitioning II (minimum cuts) ===
def min_cut(s: str) -> int:
    n = len(s)
    if n <= 1:
        return 0

    pal = [[False] * n for _ in range(n)]
    for i in range(n):        # end index
        for j in range(i + 1):  # start index
            if s[i] == s[j] and (i - j <= 2 or pal[j + 1][i - 1]):
                pal[j][i] = True

    @lru_cache(maxsize=None)
    def get_min_cuts(i: int) -> int:
        if i == n:
            return 0
        best = float("inf")
        for j in range(i, n):
            if pal[i][j]:
                best = min(best, 1 + get_min_cuts(j + 1))
        return best

    return get_min_cuts(0) - 1  # cuts = partitions - 1


# === Rerooting DP: Minimum Edge Reversals ===
def min_edge_reversals(n: int, edges: list[list[int]]) -> list[int]:
    graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append((v, 0))  # forward edge (cost 0)
        graph[v].append((u, 1))  # backward edge (cost 1)

    dp = [0] * n

    def calculate_root(node: int, parent: int) -> int:
        reversals = 0
        for nei, cost in graph[node]:
            if nei == parent:
                continue
            reversals += cost + calculate_root(nei, node)
        return reversals

    def reroot(node: int, parent: int) -> None:
        for nei, cost in graph[node]:
            if nei == parent:
                continue
            dp[nei] = dp[node] + (1 if cost == 0 else -1)
            reroot(nei, node)

    dp[0] = calculate_root(0, -1)
    reroot(0, -1)
    return dp


if __name__ == "__main__":
    print(jump_greedy([2, 3, 1, 1, 4]))       # 2
    print(jump_memo([2, 3, 1, 1, 4]))         # 2
    print(jump_bottom_up([2, 3, 1, 1, 4]))    # 2
    print(max_profit_cooldown([1, 2, 3, 0, 2]))  # 3
    print(min_distance("horse", "ros"))       # 3
    print(max_profit_two_transactions([3, 3, 5, 0, 0, 3, 1, 4]))  # 6
    print(word_break("leetcode", ["leet", "code"]))  # True
    print(min_cut("aab"))                     # 1
    print(min_edge_reversals(6, [[2, 0], [2, 1], [1, 3], [3, 4], [0, 5]]))  # [1, 1, 0, 2, 3, 2]
