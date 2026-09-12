# PATTERN NAME: Two Pointers
# DIFFICULTY: Easy | FREQUENCY: Very High (sorted-array / palindrome / partition staple at all companies)

# WHEN TO USE:
# - Sorted array problems (pair sum, triplet sum, remove duplicates)
# - Palindrome checking
# - Merging two sorted arrays
# - Partitioning (Dutch National Flag)
# - Container with most water, trapping rain water

# CORE IDEA (INTUITION):
# - Use two pointers moving toward each other (opposite direction) or in the same direction
#   (fast/slow) to reduce O(n^2) to O(n).
# - Opposite direction: start from both ends, converge based on a condition.
# - Same direction: fast pointer explores, slow pointer tracks the valid position.

# INVARIANTS:
# - Pointers never cross (opposite) or slow never passes fast (same direction).
# - The search space shrinks with each step.
# - For sorted arrays: moving left pointer right increases the sum, moving right pointer left decreases it.

# COMMON MISTAKES:
# - Forgetting to sort the array first (two pointers on unsorted data gives wrong answers).
# - Off-by-one: using left <= right when it should be left < right.
# - Not skipping duplicates in problems like 3Sum.
# - Moving the wrong pointer (always move the one that improves the condition).
# - In Dutch National Flag: incrementing mid after swapping with high.

# TIME & SPACE:
# - Time: O(n) for a single pass, O(n log n) if sorting is needed first.
# - Space: O(1) - in-place pointer manipulation.

# RELATED PROBLEMS:
# - Two Sum II (LC 167)
# - 3Sum (LC 15)
# - Container With Most Water (LC 11)
# - Trapping Rain Water (LC 42)
# - Valid Palindrome (LC 125)
# - Remove Duplicates from Sorted Array (LC 26)
# - Sort Colors (LC 75)
# - Move Zeroes (LC 283)
# - Squares of a Sorted Array (LC 977)


# === OPPOSITE DIRECTION ===

# Two Sum (sorted array)
def two_sum_sorted(nums: list[int], target: int) -> list[int]:
    left, right = 0, len(nums) - 1

    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left, right]
        if total < target:
            left += 1
        else:
            right -= 1

    return [-1, -1]


# Container With Most Water
def max_area(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    max_water = 0

    while left < right:
        width = right - left
        h = min(height[left], height[right])
        max_water = max(max_water, width * h)

        # Move the shorter side - it's the bottleneck
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return max_water


# Valid Palindrome (with alphanumeric filter)
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1

    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1

        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1

    return True


# === SAME DIRECTION (Fast/Slow) ===

# Remove Duplicates from Sorted Array (in-place)
def remove_duplicates(nums: list[int]) -> int:
    if len(nums) == 0:
        return 0

    slow = 0  # points to the last unique element

    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]

    return slow + 1  # length of the unique portion


# === DUTCH NATIONAL FLAG (3-way partition) ===

# Sort Colors (0s, 1s, 2s)
def sort_colors(nums: list[int]) -> list[int]:
    low, mid, high = 0, 0, len(nums) - 1

    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
            # don't increment mid - the swapped element still needs checking

    return nums


if __name__ == "__main__":
    print(two_sum_sorted([2, 7, 11, 15], 9))                    # [0, 1]
    print(max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]))                # 49
    print(is_palindrome("A man, a plan, a canal: Panama"))      # True
    print(remove_duplicates([1, 1, 2, 2, 3]))                   # 3
    print(sort_colors([2, 0, 2, 1, 1, 0]))                      # [0, 0, 1, 1, 2, 2]
