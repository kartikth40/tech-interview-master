# ALGORITHM: Quick Select (Kth smallest/largest in O(n) average)
# CATEGORY: Sorting / Selection / Divide and Conquer
# DIFFICULTY: Medium | FREQUENCY: Very High (Kth-largest, K-closest at Google/Meta/Amazon)

# Quick Select finds the k-th smallest (or largest) element without fully sorting.
# It partitions around a pivot like Quick Sort, then recurses only into the side containing the target.

# Time Complexity: O(n) average, O(n^2) worst case (mitigated by good pivot choice).
# Space Complexity: O(1) iterative, O(log n) recursive.

# Steps (Hoare's partitioning):
# 1. Choose a pivot.
# 2. Partition into < pivot and > pivot.
# 3. Recurse only into the partition containing the target index.

# COMMON MISTAKES:
# - Converting k-th largest to the wrong index (k-th largest = index n-k, 0-indexed).
# - Recursing into both partitions (that's Quick Sort, defeating the O(n) benefit).
# - Comparing distances with sqrt (unnecessary; compare squared distances).

# RELATED PROBLEMS:
# - Kth Largest Element in an Array (LC 215)
# - K Closest Points to Origin (LC 973)
# - Top K Frequent Elements (LC 347)


def quick_select(low: int, high: int, nums: list[int], target: int) -> int:
    i, j = low, high
    pivot = nums[(i + j) // 2]

    while i <= j:
        while i <= j and nums[i] < pivot:
            i += 1
        while i <= j and nums[j] > pivot:
            j -= 1
        if i <= j:
            nums[i], nums[j] = nums[j], nums[i]
            i += 1
            j -= 1

    # After partitioning: [low..j] <= pivot, [i..high] >= pivot, and j < i.
    if i <= target:
        return quick_select(i, high, nums, target)
    if j >= target:
        return quick_select(low, j, nums, target)
    return nums[target]


def find_kth_largest(nums: list[int], k: int) -> int:
    # k-th largest = (n-k)-th smallest (0-indexed)
    target = len(nums) - k
    return quick_select(0, len(nums) - 1, nums, target)


# Problem: K closest points to origin.
# Distance from origin compared as x^2 + y^2 (no sqrt needed for ordering).
def k_closest(points: list[list[int]], k: int) -> list[list[int]]:
    def distance(point: list[int]) -> int:
        return point[0] * point[0] + point[1] * point[1]

    def select(low: int, high: int, target: int) -> list[list[int]]:
        i, j = low, high
        pivot_dist = distance(points[(i + j) // 2])
        while i <= j:
            while i <= j and distance(points[i]) < pivot_dist:
                i += 1
            while i <= j and distance(points[j]) > pivot_dist:
                j -= 1
            if i <= j:
                points[i], points[j] = points[j], points[i]
                i += 1
                j -= 1

        if i <= target:
            return select(i, high, target)
        if j >= target:
            return select(low, j, target)
        return points[:target + 1]

    return select(0, len(points) - 1, k - 1)


# Example usage:
if __name__ == "__main__":
    print("quick select:")
    print(find_kth_largest([3, 2, 1, 5, 6, 4], 2))              # 5
    print(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))     # 4

    print("k closest points to origin:")
    print(k_closest([[1, 3], [-2, 2]], 1))                      # [[-2, 2]]
    print(k_closest([[3, 3], [5, -1], [-2, 4]], 2))             # [[3, 3], [-2, 4]]
