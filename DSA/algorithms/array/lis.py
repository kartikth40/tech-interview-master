# ALGORITHM: Longest Increasing Subsequence (LIS)
# CATEGORY: Array / DP / Binary Search (Patience Sort)
# DIFFICULTY: Medium | FREQUENCY: High (LIS family at Google/Amazon/Microsoft)

# PROBLEM STATEMENT:
# Given an array of integers, find the longest strictly increasing subsequence.
# The DP solution is O(n^2); we optimize to O(n log n) using Patience Sort.

# Patience Sort intuition:
# - Card game: deal cards into piles, each pile sorted (smaller on top).
# - Rule: place a card on the leftmost pile whose top >= card (or start a new pile).
# - Key insight: number of piles = LIS length.
# - Why? Each pile represents a "chain" in the subsequence.

# WHEN TO USE:
# - Longest increasing subsequence or similar problems.
# - When O(n^2) DP is too slow and you need O(n log n).

# CORE IDEA (INTUITION):
# 1. Maintain "tails" where tails[i] = smallest ending value among all LIS of length i+1.
# 2. For each number, binary-search the leftmost tail >= num.
# 3. Replace that tail with num (keeps endings as small as possible), or append if num extends the LIS.
# 4. Number of tails = LIS length. Track parents to reconstruct the actual subsequence.

# INVARIANTS:
# - tails is always sorted in increasing order.
# - len(tails) at the end is the LIS length.

# TIME: O(n log n)  |  SPACE: O(n)

# COMMON MISTAKES:
# - Forgetting binary search (falling back to O(n^2)).
# - Not maintaining the parent array when reconstructing the actual LIS.
# - Confusing the tails array with the actual subsequence (tails only track pile tops).

# RELATED PROBLEMS:
# - Longest Increasing Subsequence (LC 300)
# - Russian Doll Envelopes (LC 354)
# - Number of Longest Increasing Subsequence (LC 673)
# - Longest Decreasing Subsequence: reverse the comparison in binary search.


def get_lis(nums: list[int]) -> list[int]:
    n = len(nums)
    if n == 0:
        return []

    # tails[i] = smallest ending value among all LIS of length i+1 (always sorted)
    tails: list[int] = []
    # To reconstruct: track which element created each tail
    indices: list[int] = []          # indices[i] = array index of tails[i]
    parent = [-1] * n                # link to previous element in the chain

    for i in range(n):
        num = nums[i]

        # Binary search: leftmost pile whose top >= num
        left, right = 0, len(tails)
        while left < right:
            mid = (left + right) // 2
            if tails[mid] < num:
                left = mid + 1  # num is bigger, try a longer LIS
            else:
                right = mid     # num can improve this length

        # Connect to previous element in the chain
        if left > 0:
            parent[i] = indices[left - 1]

        # Update: extend the LIS or replace with a smaller ending
        if left == len(tails):
            tails.append(num)     # new longest LIS
            indices.append(i)
        else:
            tails[left] = num     # better (smaller) ending for this length
            indices[left] = i

    # Trace back the actual sequence
    lis: list[int] = []
    idx = indices[-1]  # start from the longest LIS
    while idx != -1:
        lis.append(nums[idx])
        idx = parent[idx]

    return lis[::-1]


# EXAMPLE:
# Input: [10, 9, 2, 5, 3, 7, 101, 18]
# Output length: 4 (an LIS is [2, 3, 7, 18])
if __name__ == "__main__":
    print(get_lis([10, 9, 2, 5, 3, 7, 101, 18]))  # [2, 3, 7, 18]
