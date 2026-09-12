# PATTERN NAME: Prefix Sum
# DIFFICULTY: Medium | FREQUENCY: Very High (subarray-sum problems at Google/Meta/Amazon)

# WHEN TO USE:
# - Calculating the sum of subarrays multiple times.
# - Counting subarrays that meet a certain sum condition.
# - Optimizing brute-force solutions with nested sum loops.

# CORE IDEA (INTUITION):
# - Precompute cumulative sums so any subarray sum is a constant-time difference.
# - Use a hash map of prefix-sum frequencies to count subarrays with a specific property.
# - Key identity: sum(i..j) == prefix[j] - prefix[i-1]; a subarray sums to k when a previous
#   prefix equals current_sum - k.

# COMMON MISTAKES:
# - Not seeding the prefix-sum map with the base case {0: 1}.
# - Updating the map before checking (double counts the current element).
# - Misunderstanding the relationship between current sum, target, and previous sums.

# TIME & SPACE:
# - Time: O(n).
# - Space: O(n) for the prefix-sum hash map.

# RELATED PROBLEMS:
# - Subarray Sum Equals K (LC 560)
# - Continuous Subarray Sum (LC 523)
# - Count of Range Sum (LC 327)
# - Contiguous Array (LC 525)
# - Subarray Sums Divisible by K (LC 974)


# Problem: Subarray Sum Equals K
# Count the continuous subarrays whose sum equals k.
def subarray_sum(nums: list[int], k: int) -> int:
    count = 0
    prefix_freq: dict[int, int] = {0: 1}
    total = 0

    for n in nums:
        total += n
        if total - k in prefix_freq:
            count += prefix_freq[total - k]
        prefix_freq[total] = prefix_freq.get(total, 0) + 1

    return count


if __name__ == "__main__":
    print(subarray_sum([1, 1, 1], 2))        # 2
    print(subarray_sum([1, 2, 3], 3))        # 2
    print(subarray_sum([3, 4, 7, 2, -3, 1, 4, 2], 7))  # 4
