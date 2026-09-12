# ALGORITHM: Edit Distance (Levenshtein Distance)
# CATEGORY: 2D DP (String DP)
# DIFFICULTY: Hard | FREQUENCY: High (classic string DP at Google/Amazon/Microsoft)

# PROBLEM:
# Given two strings word1 and word2, return the minimum number of operations to convert word1
# into word2. Operations: insert, delete, replace.

# INTUITION:
# dp[i][j] = min operations to convert word1[0..i-1] to word2[0..j-1].
# If chars match: dp[i][j] = dp[i-1][j-1] (no operation needed).
# If not: dp[i][j] = 1 + min(
#   dp[i-1][j],     # delete from word1
#   dp[i][j-1],     # insert into word1
#   dp[i-1][j-1]    # replace in word1
# )

# TIME: O(m * n)  |  SPACE: O(m * n), optimizable to O(n)

# COMMON MISTAKES:
# - Forgetting base cases (empty-string conversions fill row 0 and column 0).
# - Wrong index mapping (dp is 1-indexed, strings are 0-indexed).
# - Confusing which operation maps to which dp transition.

# RELATED PROBLEMS:
# - Edit Distance (LC 72)
# - One Edit Distance (LC 161)
# - Delete Operation for Two Strings (LC 583)
# - Minimum ASCII Delete Sum for Two Strings (LC 712)


def min_distance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases: converting an empty string
    for i in range(m + 1):
        dp[i][0] = i  # delete all chars
    for j in range(n + 1):
        dp[0][j] = j  # insert all chars

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # delete
                    dp[i][j - 1],      # insert
                    dp[i - 1][j - 1],  # replace
                )

    return dp[m][n]


# Space-optimized (O(n) space)
def min_distance_optimized(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    prev = list(range(n + 1))

    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        cur[0] = i
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur

    return prev[n]


if __name__ == "__main__":
    print(min_distance("horse", "ros"))               # 3
    print(min_distance("intention", "execution"))     # 5
    print(min_distance_optimized("horse", "ros"))     # 3
