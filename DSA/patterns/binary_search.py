# PATTERN NAME: Binary Search
# DIFFICULTY: Medium | FREQUENCY: Very High (search + binary-search-on-answer at all companies)

# WHEN TO USE:
# - Searching in a sorted array or range.
# - Finding an element, boundary conditions, or optimal values (binary search on the answer).

# CORE IDEA (INTUITION):
# - Repeatedly divide the search interval in half.
# - Compare the target to the middle element.
# - Narrow the search to the left or right half based on the comparison.

# INVARIANTS:
# - The array/range is sorted (or the predicate is monotonic).
# - The search space halves each step.
# - The answer, if present, remains within the search space.

# COMMON MISTAKES:
# - Not updating left/right pointers correctly (infinite loop).
# - Off-by-one errors in mid or in the loop condition (< vs <=).
# - Not handling edge cases (single-element array, empty array).
# - For "binary search on answer": wrong feasibility predicate.

# TIME & SPACE:
# - Time: O(log n) (times O(n) predicate cost for search-on-answer variants).
# - Space: O(1).

# RELATED PROBLEMS:
# - Find Peak Element (LC 162)
# - Kth Missing Positive Number (LC 1539)
# - Capacity To Ship Packages Within D Days (LC 1011)
# - Median of Two Sorted Arrays (LC 4)
# - Kth Smallest Element in a Sorted Matrix (LC 378)


# EXAMPLE: Find Peak Element
# A peak element is strictly greater than its neighbors: nums[i] > nums[i-1] and nums[i] > nums[i+1].
def find_peak_element(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1

    while left < right:
        mid = (left + right) // 2
        # If mid < next, a peak must be on the right; otherwise on the left (including mid).
        if nums[mid] < nums[mid + 1]:
            left = mid + 1
        else:
            right = mid

    return left  # left == right points to a peak


# EXAMPLE: Kth Missing Positive Number
# Missing count before arr[mid] = arr[mid] - (mid + 1) (expected value if nothing were missing).
def find_kth_positive(arr: list[int], k: int) -> int:
    l, r = 0, len(arr)

    while l < r:
        mid = (l + r) // 2
        missing = arr[mid] - (mid + 1)
        if missing < k:
            l = mid + 1  # not enough missing yet, search right
        else:
            r = mid       # too many missing (or exactly k), search left

    # l = index where the kth missing number would be inserted; answer = l + k
    return l + k


# EXAMPLE: Capacity To Ship Packages Within D Days
# Binary search on capacity in [max(weights), sum(weights)].
def ship_within_days(weights: list[int], days: int) -> int:
    def can_ship(capacity: int) -> bool:
        days_needed = 1
        current_load = 0
        for w in weights:
            if current_load + w > capacity:
                days_needed += 1
                current_load = w
            else:
                current_load += w
        return days >= days_needed

    i, j = max(weights), sum(weights)
    while i < j:
        cap = (i + j) // 2
        if can_ship(cap):
            j = cap
        else:
            i = cap + 1
    return i


# EXAMPLE: Median in a Row-Wise Sorted Matrix
# Binary search on the VALUE range; count elements <= mid across rows.
def median(mat: list[list[int]]) -> int:
    m, n = len(mat), len(mat[0])

    low = min(mat[i][0] for i in range(m))
    high = max(mat[i][n - 1] for i in range(m))

    target = (m * n) // 2 + 1  # median has this many elements <= it

    def count_le(arr: list[int], limit: int) -> int:
        # number of elements <= limit in a sorted row (upper bound)
        left, right = 0, len(arr)
        while left < right:
            mid = (left + right) // 2
            if arr[mid] <= limit:
                left = mid + 1
            else:
                right = mid
        return left

    while low <= high:
        mid = (low + high) // 2
        count = sum(count_le(mat[i], mid) for i in range(m))
        if count < target:
            low = mid + 1
        else:
            high = mid - 1

    return low


# EXAMPLE: Median of Two Sorted Arrays
# Binary search on the smaller array's partition -> O(log(min(m, n))).
def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    if len(nums1) > len(nums2):
        return find_median_sorted_arrays(nums2, nums1)

    A, B = nums1, nums2
    m, n = len(A), len(B)
    total = m + n
    half = total // 2

    l, r = 0, m - 1
    while True:
        i = (l + r) // 2            # last index on A's left partition
        j = half - (i + 1) - 1      # last index on B's left partition

        a_left = A[i] if i >= 0 else float("-inf")
        a_right = A[i + 1] if i + 1 < m else float("inf")
        b_left = B[j] if j >= 0 else float("-inf")
        b_right = B[j + 1] if j + 1 < n else float("inf")

        if a_left <= b_right and b_left <= a_right:
            if total % 2 == 0:
                return (max(a_left, b_left) + min(a_right, b_right)) / 2
            return min(a_right, b_right)
        elif a_left > b_right:
            r = i - 1  # took too many from A -> move left
        else:
            l = i + 1  # took too few from A -> move right


if __name__ == "__main__":
    print(find_peak_element([1, 2, 3, 1]))                 # 2
    print(find_kth_positive([2, 3, 4, 7, 11], 5))          # 9
    print(ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5))  # 15
    print(median([[1, 3, 5], [2, 6, 9], [3, 6, 9]]))       # 5
    print(find_median_sorted_arrays([1, 3], [2]))          # 2
    print(find_median_sorted_arrays([1, 2], [3, 4]))       # 2.5
