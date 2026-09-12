# ALGORITHM: kSum (generalized 2Sum/3Sum/4Sum)
# CATEGORY: Array / Two Pointers / Recursion
# DIFFICULTY: Medium | FREQUENCY: Very High (2Sum/3Sum/4Sum family at Google/Meta/Amazon)

# PROBLEM:
# Find all unique k-sized combinations in an array that sum to a target value.
# This reduces the k-sum problem to a 2-sum problem via recursion.

# TIME: O(n^(k-1))  |  SPACE: O(k) for the recursion stack

# INTUITION / STEPS:
# 1. Sort the array to handle duplicates and enable the two-pointer technique.
# 2. Recurse to reduce k-sum down to 2-sum.
# 3. For k > 2, fix one element and recursively solve for k-1.
# 4. For k == 2, use two pointers to find pairs that sum to the (adjusted) target.
# 5. Skip duplicates to ensure unique combinations.

# COMMON MISTAKES:
# - Forgetting to sort first (duplicate-skipping and two-pointer both rely on it).
# - Not skipping duplicate starting numbers (i > start and nums[i] == nums[i-1]).
# - Not skipping duplicates on BOTH ends after finding a valid pair.

# RELATED PROBLEMS:
# - Two Sum II (LC 167)
# - 3Sum (LC 15)
# - 4Sum (LC 18)


def four_sum(nums: list[int], target: int) -> list[list[int]]:
    quads: list[list[int]] = []
    nums.sort()

    def k_sum(start: int, k: int, cur_arr: list[int], cur_sum: int) -> None:
        # BASE CASE: down to 2 numbers -> two-pointer technique
        if k == 2:
            i = start
            j = len(nums) - 1

            while i < j:
                total = nums[i] + nums[j] + cur_sum

                if total == target:
                    quads.append([*cur_arr, nums[i], nums[j]])
                    # Skip duplicates from both ends
                    while i < j and nums[i] == nums[i + 1]:
                        i += 1
                    while i < j and nums[j] == nums[j - 1]:
                        j -= 1
                    i += 1
                    j -= 1
                elif total < target:
                    i += 1  # need a bigger sum
                else:
                    j -= 1  # need a smaller sum
        # RECURSIVE CASE: fix one number, solve (k-1)-sum
        else:
            for i in range(start, len(nums) - k + 1):
                # Skip duplicate starting numbers
                if i > start and nums[i] == nums[i - 1]:
                    continue

                cur_arr.append(nums[i])
                k_sum(i + 1, k - 1, cur_arr, cur_sum + nums[i])
                cur_arr.pop()

    k_sum(0, 4, [], 0)
    return quads


# Example usage:
if __name__ == "__main__":
    # [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]
    print(four_sum([1, 0, -1, 0, -2, 2], 0))
