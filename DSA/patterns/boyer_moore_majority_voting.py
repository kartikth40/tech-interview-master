# PATTERN NAME: Boyer-Moore Majority Voting
# DIFFICULTY: Easy | FREQUENCY: High (majority element n/2 and n/3 at Google/Amazon/Adobe)

# WHEN TO USE:
# - Finding the majority element (appears more than n/2 times) in O(1) space.
# - Extended form: elements appearing more than n/k times (keep k-1 candidates).

# CORE IDEA (INTUITION):
# - Track a candidate and a counter.
# - Increment on a match, decrement on a mismatch; when the counter hits 0, pick a new candidate.
# - After one pass, the surviving candidate is the majority element (if one exists).

# INVARIANTS:
# - A true majority element appears more than n/2 times.
# - The counter reflects the balance between the candidate and everything else.
# - When count is 0, the current candidate cannot be the majority.

# COMMON MISTAKES:
# - Assuming a majority element exists without verifying (needed for the n/3 variant).
# - Not resetting the count when choosing a new candidate.
# - Misreading the counter's role in tracking dominance.

# TIME & SPACE:
# - Time: O(n).
# - Space: O(1).

# RELATED PROBLEMS:
# - Majority Element (LC 169)
# - Majority Element II (LC 229) - elements appearing more than n/3 times


# EXAMPLE: Majority Element (appears more than floor(n/2) times; assumed to exist).
def majority_element(nums: list[int]) -> int | None:
    candidate = None
    count = 0
    for num in nums:
        if count == 0:
            candidate = num
        count += 1 if num == candidate else -1
    return candidate


# EXAMPLE: Majority Element II (more than floor(n/3) times -> at most 2 such elements).
def majority_element_ii(nums: list[int]) -> list[int]:
    candidate1 = candidate2 = None
    count1 = count2 = 0

    for num in nums:
        if num == candidate1:
            count1 += 1
        elif num == candidate2:
            count2 += 1
        elif count1 == 0:
            candidate1 = num
            count1 = 1
        elif count2 == 0:
            candidate2 = num
            count2 = 1
        else:
            count1 -= 1
            count2 -= 1

    # Verify candidates (no guarantee they exceed n/3)
    count1 = sum(1 for num in nums if num == candidate1)
    count2 = sum(1 for num in nums if num == candidate2)

    result: list[int] = []
    if count1 > len(nums) // 3:
        result.append(candidate1)
    if count2 > len(nums) // 3:
        result.append(candidate2)
    return result


if __name__ == "__main__":
    print(majority_element([2, 2, 1, 1, 1, 2, 2]))  # 2
    print(majority_element_ii([3, 2, 3]))            # [3]
    print(majority_element_ii([1, 1, 1, 3, 3, 2, 2, 2]))  # [1, 2]
