# ALGORITHM: Quick Sort (Hoare-style partitioning)
# CATEGORY: Sorting / Divide and Conquer
# DIFFICULTY: Medium | FREQUENCY: High (in-place sort fundamentals at Google/Amazon/Microsoft)

# Time Complexity: O(n log n) average, O(n^2) worst case.
# Space Complexity: O(log n) due to the recursion stack.

# Steps (Hoare's partitioning):
# 1. Choose a pivot (here, the middle element).
# 2. Partition: move smaller elements left, larger elements right.
# 3. Recurse on both partitions until sorted.

# COMMON MISTAKES:
# - Always picking the first/last element as pivot (worst case on sorted input).
# - Off-by-one in the partition loop leading to infinite recursion.
# - Recursing on the wrong sub-ranges after pointers cross.

# RELATED PROBLEMS:
# - Sort an Array (LC 912)
# - Sort Colors (LC 75) - Dutch National Flag partitioning
# - Kth Largest Element (LC 215) - see quick_select.py


def quick_sort(nums: list[int]) -> list[int]:
    def sort(low: int, high: int) -> None:
        if low >= high:
            return

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

        sort(low, j)   # left partition (elements <= pivot)
        sort(i, high)  # right partition (elements >= pivot)

    sort(0, len(nums) - 1)
    return nums


# Example usage:
if __name__ == "__main__":
    print("quick sort:")
    print(quick_sort([3, 6, 8, 10, 1, 2, 1]))  # [1, 1, 2, 3, 6, 8, 10]
