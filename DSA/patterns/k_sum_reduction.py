# PATTERN NAME: k-Sum Reduction (Recursive Two Pointer)
# DIFFICULTY: Medium | FREQUENCY: High (generalizes 2Sum/3Sum/4Sum at Google/Meta/Amazon)

# INTUITION:
# - Reduce a k-Sum problem to 2-Sum by recursively fixing elements.
# - Use the two-pointer technique for the base case (2-Sum).
# - Sort the array to enable two pointers and easy duplicate skipping.

# ALGORITHM:
# 1. Sort the array.
# 2. Recursively reduce k-Sum to (k-1)-Sum by fixing one element at a time.
# 3. Base case (k == 2): two pointers from both ends, moving based on the sum vs target.
# 4. Skip duplicates to avoid duplicate tuples.

# TIME COMPLEXITY: O(n^(k-1))  (4-Sum: O(n^3); sorting O(n log n); recursion depth k-2)
# SPACE COMPLEXITY: O(k) for recursion depth + current tuple.

# KEY TECHNIQUES: reduction, two pointers, duplicate skipping, tightened loop bound (len - k + 1).
# GENERALIZABLE: works for any k-Sum - just change the initial call k_sum(0, k, [], 0).

# COMMON MISTAKES:
# - Forgetting to sort before applying two pointers / duplicate skipping.
# - Not skipping duplicate starting elements (i > start and nums[i] == nums[i-1]).
# - Not skipping duplicates on both ends after recording a match.

# RELATED PROBLEMS:
# - Two Sum II (LC 167)
# - 3Sum (LC 15)
# - 4Sum (LC 18)


def four_sum(nums: list[int], target: int) -> list[list[int]]:
    quads: list[list[int]] = []
    nums.sort()

    def k_sum(start: int, k: int, cur_arr: list[int], cur_sum: int) -> None:
        if k <= 2:
            i, j = start, len(nums) - 1
            while i < j:
                total = nums[i] + nums[j] + cur_sum
                if total == target:
                    quads.append([*cur_arr, nums[i], nums[j]])
                    while i < j and nums[i] == nums[i + 1]:
                        i += 1
                    while i < j and nums[j] == nums[j - 1]:
                        j -= 1
                    i += 1
                    j -= 1
                elif total < target:
                    i += 1
                else:
                    j -= 1
        else:
            for i in range(start, len(nums) - k + 1):
                if i > start and nums[i] == nums[i - 1]:
                    continue
                cur_arr.append(nums[i])
                k_sum(i + 1, k - 1, cur_arr, cur_sum + nums[i])
                cur_arr.pop()

    k_sum(0, 4, [], 0)
    return quads


if __name__ == "__main__":
    # [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]
    print(four_sum([1, 0, -1, 0, -2, 2], 0))
