# ALGORITHM: Kadane's Algorithm (Maximum Subarray Sum)
# CATEGORY: Array / Dynamic Programming
# DIFFICULTY: Easy | FREQUENCY: Very High (classic array DP at Google/Amazon/Microsoft)

# PROBLEM:
# Find the maximum sum of a contiguous subarray within a one-dimensional array of numbers.

# INTUITION:
# - Maintain a running sum of the current subarray and the best sum found so far.
# - At each element, either extend the current subarray or start fresh at the current element:
#   cur = max(x, cur + x).
# - Track the best cur seen.

# TIME: O(n)  |  SPACE: O(1)

# When to use:
# - Maximum sum of a contiguous subarray.
# - Linear-time, constant-space subarray problems.
# - Variants: maximum product subarray, longest subarray with a given sum.

# COMMON MISTAKES:
# - Initializing best to 0 instead of -inf (fails on all-negative arrays).
# - Resetting cur to 0 instead of taking max(x, cur + x) (breaks all-negative case).

# RELATED PROBLEMS:
# - Maximum Subarray (LC 53)
# - Maximum Product Subarray (LC 152)
# - Best Time to Buy and Sell Stock (LC 121)


def kadane(arr: list[int]) -> int:
    best = float("-inf")
    cur = 0

    for x in arr:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


if __name__ == "__main__":
    print(kadane([-2, 1, -3, 4, -1, 2, 1, -5, 4]))  # 6 ([4, -1, 2, 1])
    print(kadane([-3, -1, -2]))                      # -1
