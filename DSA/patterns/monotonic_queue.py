# PATTERN NAME: Monotonic Queue (Deque)
# DIFFICULTY: Hard | FREQUENCY: High (sliding window max/min at Google/Amazon)

# WHEN TO USE:
# - Sliding window maximum / minimum.
# - Constrained subsequence sum.
# - Problems needing the max/min of a moving window in O(1) amortized.

# CORE IDEA (INTUITION):
# - Maintain a deque of INDICES whose values are monotonic.
# - For a max-queue: keep values decreasing (front = max of the window).
# - Before adding a new element, pop smaller elements from the back (they can never be the max).
# - Remove front indices that fall outside the window.

# INVARIANTS:
# - Deque values are monotonic (decreasing for max, increasing for min).
# - The front is always the answer (max/min) for the current window.
# - Indices in the deque are within the current window.

# COMMON MISTAKES:
# - Storing values instead of indices (can't tell when they leave the window).
# - Popping from the wrong end (front for window expiry, back for monotonic property).
# - Not removing expired indices from the front.
# - Using a plain list with pop(0) (O(n)) instead of collections.deque.

# TIME & SPACE:
# - Time: O(n) - each element enters and leaves the deque once.
# - Space: O(k) where k is the window size.

# RELATED PROBLEMS:
# - Sliding Window Maximum (LC 239)
# - Constrained Subsequence Sum (LC 1425)
# - Shortest Subarray with Sum at Least K (LC 862)
# - Jump Game VI (LC 1696)

from collections import deque


# Sliding Window Maximum - max of every window of size k
def max_sliding_window(nums: list[int], k: int) -> list[int]:
    result: list[int] = []
    dq: deque[int] = deque()  # indices, values decreasing

    for i in range(len(nums)):
        # remove indices outside the window
        if dq and dq[0] < i - k + 1:
            dq.popleft()

        # remove smaller values from the back (they can't be the max)
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()

        dq.append(i)

        # front is the max of the current window
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result


# Sliding Window Minimum - min of every window of size k
def min_sliding_window(nums: list[int], k: int) -> list[int]:
    result: list[int] = []
    dq: deque[int] = deque()  # indices, values increasing

    for i in range(len(nums)):
        if dq and dq[0] < i - k + 1:
            dq.popleft()

        while dq and nums[dq[-1]] > nums[i]:
            dq.pop()

        dq.append(i)

        if i >= k - 1:
            result.append(nums[dq[0]])

    return result


if __name__ == "__main__":
    print(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3))
    # [3, 3, 5, 5, 6, 7]
    print(min_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3))
    # [-1, -3, -3, -3, 3, 3]
