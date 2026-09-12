# PATTERN NAME: Sliding Window
# DIFFICULTY: Medium | FREQUENCY: Very High (arrays/strings staple at Google/Meta/Amazon)

# WHEN TO USE:
# - When you need to find a contiguous subarray or substring that satisfies certain conditions.
# - When you need to optimize a brute-force solution that involves nested loops over a linear data structure.
# - When you need to maintain a running total or count of elements in a dynamic window.

# CORE IDEA (INTUITION):
# - Use two pointers to represent the boundaries of the window.
# - Expand and contract the window based on the problem's requirements.
# - Maintain necessary data structures (like dicts or counters) to track elements within the window.

# TEMPLATE / SKELETON:

# Problem: Longest Repeating Character Replacement
# Given a string s that consists of only uppercase English letters, you can perform at most k operations
# on that string. In one operation, you can choose any character of the string and change it to any other
# uppercase English character.


def character_replacement(s: str, k: int) -> int:
    freq: dict[str, int] = {}
    left = 0
    max_len = 0
    max_freq = 0

    for right in range(len(s)):
        char = s[right]
        freq[char] = freq.get(char, 0) + 1
        max_freq = max(max_freq, freq[char])

        # window size - max_freq > k
        while (right - left + 1) - max_freq > k:
            char_to_remove = s[left]
            freq[char_to_remove] -= 1
            if freq[char_to_remove] == 0:
                del freq[char_to_remove]
            left += 1

        max_len = max(max_len, right - left + 1)

    return max_len


# COMMON MISTAKES:
# - Not updating the window boundaries correctly.
# - Forgetting to maintain necessary data structures for tracking elements within the window.
# - Not handling edge cases, such as empty strings or arrays.

# TIME & SPACE:
# - Time Complexity: O(n), where n is the length of the input string or array.
# - Space Complexity: O(1) or O(k), depending on the number of unique elements in the window.

# RELATED PROBLEMS:
# - Minimum Size Subarray Sum
# - Longest Substring Without Repeating Characters
# - Permutation in String
# - Find All Anagrams in a String
# - Sliding Window Maximum
# - Subarrays with K Different Integers
# - Longest Substring with At Most K Distinct Characters


# Problem: Binary Subarrays With Sum
# Given a binary array nums and an integer goal, return the number of non-empty subarrays with a sum goal.
# A subarray is a contiguous part of the array.

# Intuition:
# - We can use the sliding window technique to count the number of subarrays with at most a certain sum.
# - By calculating the number of subarrays with at most 'goal' and subtracting the number of subarrays
#   with at most 'goal - 1', we get the number of subarrays with exactly 'goal' sum.
# - This approach reduces the space complexity compared to using a hashmap to store prefix sums.


def num_subarrays_with_sum(nums: list[int], goal: int) -> int:
    # Can be solved like "subarrays with sum k" (hashmap approach) but that takes O(n) space.
    # Reduce the space:
    #   no. of subarrays with exact sum goal =
    #       (no. of subarrays with at most sum goal)
    #       - (no. of subarrays with at most sum goal - 1)

    def at_most(g: int) -> int:
        if g < 0:
            return 0
        left = 0
        count = 0
        window_sum = 0
        for right in range(len(nums)):
            window_sum += nums[right]
            while window_sum > g:
                window_sum -= nums[left]
                left += 1
            count += right - left + 1
        return count

    return at_most(goal) - at_most(goal - 1)


# Problem: Subarrays with K Different Integers
# Given an array A of positive integers, call a (contiguous, not necessarily distinct) subarray of A good
# if the number of different integers in that subarray is exactly K.
# Return the number of good subarrays of A.

# Intuition:
# - Similar to the previous problem, use the sliding window technique to count the number of subarrays
#   with at most K distinct integers.
# - subarrays with exactly K = at_most(K) - at_most(K - 1)


def subarrays_with_k_distinct(nums: list[int], k: int) -> int:
    def at_most(kk: int) -> int:
        if kk < 0:
            return 0
        left = 0
        freq: dict[int, int] = {}
        count = 0
        for right in range(len(nums)):
            freq[nums[right]] = freq.get(nums[right], 0) + 1
            while len(freq) > kk:
                freq[nums[left]] -= 1
                if freq[nums[left]] == 0:
                    del freq[nums[left]]
                left += 1
            count += right - left + 1
        return count

    return at_most(k) - at_most(k - 1)


# Examples (only run when executed directly)
if __name__ == "__main__":
    print(character_replacement("AABABBA", 1))  # 4
    print(num_subarrays_with_sum([1, 0, 1, 0, 1], 2))  # 4
    print(subarrays_with_k_distinct([1, 2, 1, 2, 3], 2))  # 7
