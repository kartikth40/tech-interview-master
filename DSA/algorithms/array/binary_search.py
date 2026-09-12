# ALGORITHM: Binary Search (classic)
# CATEGORY: Array / Search
# DIFFICULTY: Easy | FREQUENCY: Very High (fundamental building block at all companies)

# PROBLEM:
# Given a sorted array and a target, return the index of the target, or -1 if not present.

# INTUITION:
# Repeatedly halve the search range: compare the middle element with the target and discard
# the half that cannot contain it.

# TIME: O(log n)  |  SPACE: O(1)

# COMMON MISTAKES:
# - Using (l + r) / 2 in languages that overflow (Python ints are unbounded, but l + (r-l)//2 is a good habit).
# - Wrong loop condition: use while l <= r for exact-match search.
# - Forgetting the array must be sorted.

# RELATED PROBLEMS:
# - Binary Search (LC 704)
# - Search Insert Position (LC 35)
# - See DSA/patterns/binary_search.py for boundary/answer-space variants.


def binary_search(arr: list[int], target: int) -> int:
    l = 0
    r = len(arr) - 1

    while l <= r:
        mid = (l + r) >> 1
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            l = mid + 1
        else:
            r = mid - 1
    return -1


# more patterns in DSA/patterns/binary_search.py
if __name__ == "__main__":
    print(binary_search([1, 3, 5, 7, 9, 11], 7))  # 3
    print(binary_search([1, 3, 5, 7, 9, 11], 8))  # -1
