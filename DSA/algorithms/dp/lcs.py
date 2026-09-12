# ALGORITHM: Longest Common Subsequence (LCS)
# CATEGORY: 2D DP (Two Sequences)
# DIFFICULTY: Medium | FREQUENCY: High (two-sequence DP staple at Google/Amazon/Microsoft)

# PROBLEM:
# Given two strings, find the length of their longest common subsequence. A subsequence is derived
# by deleting some (or no) elements without changing the order of the remaining elements.

# INTUITION:
# dp[i][j] = LCS length of text1[0..i-1] and text2[0..j-1].
# If chars match: dp[i][j] = dp[i-1][j-1] + 1.
# If not: dp[i][j] = max(dp[i-1][j], dp[i][j-1]).

# TIME: O(m * n)  |  SPACE: O(m * n), optimizable to O(min(m, n))

# COMMON MISTAKES:
# - Confusing subsequence (order preserved, gaps allowed) with substring (contiguous).
# - Wrong index mapping (dp is 1-indexed, strings are 0-indexed).
# - Backtracking in the wrong direction when reconstructing the actual LCS.

# RELATED PROBLEMS:
# - Longest Common Subsequence (LC 1143)
# - Longest Palindromic Subsequence (LC 516) - LCS(s, reverse(s))
# - Shortest Common Supersequence (LC 1092)
# - Edit Distance (LC 72) - related recurrence


def longest_common_subsequence(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


# Print the actual LCS string (backtrack through the DP table).
def print_lcs(text1: str, text2: str) -> str:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to find the actual subsequence
    i, j = m, n
    lcs = ""
    while i > 0 and j > 0:
        if text1[i - 1] == text2[j - 1]:
            lcs = text1[i - 1] + lcs
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return lcs


# Space-optimized (O(n) space) - only need the previous row.
def lcs_optimized(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    prev = [0] * (n + 1)

    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur

    return prev[n]


if __name__ == "__main__":
    print(longest_common_subsequence("abcde", "ace"))  # 3
    print(print_lcs("abcde", "ace"))                    # "ace"
    print(lcs_optimized("abcde", "ace"))                # 3
