# ALGORITHM: Merge Sort (+ count-smaller-after-self, sort-list)
# CATEGORY: Sorting / Divide and Conquer
# DIFFICULTY: Medium | FREQUENCY: High (stable sort + merge-based counting at Google/Amazon)

# A divide-and-conquer algorithm: split the array in half, sort each half, then merge.

# Time Complexity: O(n log n)
# Space Complexity: O(n) for the temporary arrays used during merging.

# Steps:
# 1. An array of 0 or 1 elements is already sorted.
# 2. Split the array into two halves.
# 3. Recursively merge-sort each half.
# 4. Merge the two sorted halves.

# COMMON MISTAKES:
# - Allocating new lists on every merge without freeing (memory), or merging in the wrong order.
# - For count-smaller: incrementing the count at the wrong pointer (must credit the LEFT element).
# - For sort-list: not cutting the list at the midpoint (prev.next = None) causing infinite recursion.

# RELATED PROBLEMS:
# - Sort an Array (LC 912)
# - Count of Smaller Numbers After Self (LC 315)
# - Sort List (LC 148)
# - Merge Sorted Array (LC 88)

from __future__ import annotations


# === CLASSIC MERGE SORT ===
def merge_sort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return _merge(left, right)


def _merge(left: list[int], right: list[int]) -> list[int]:
    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


# === COUNT OF SMALLER NUMBERS AFTER SELF (LC 315) ===
# counts[i] = number of elements to the right of nums[i] that are smaller than nums[i].
def count_smaller(nums: list[int]) -> list[int]:
    if not nums:
        return []

    counts = [0] * len(nums)
    # Pair each value with its original index to track positions during merge.
    elements = list(enumerate(nums))  # (original_index, value)

    def sort_and_count(left: int, right: int) -> list[tuple[int, int]]:
        if left == right:
            return [elements[left]]

        mid = (left + right) // 2
        sorted_left = sort_and_count(left, mid)
        sorted_right = sort_and_count(mid + 1, right)
        return merge_and_count(sorted_left, sorted_right)

    def merge_and_count(left_arr: list[tuple[int, int]],
                        right_arr: list[tuple[int, int]]) -> list[tuple[int, int]]:
        merged: list[tuple[int, int]] = []
        i = j = 0
        while i < len(left_arr) and j < len(right_arr):
            # If a left element is greater, all remaining right elements are smaller.
            if left_arr[i][1] > right_arr[j][1]:
                counts[left_arr[i][0]] += len(right_arr) - j
                merged.append(left_arr[i])
                i += 1
            else:
                merged.append(right_arr[j])
                j += 1
        merged.extend(left_arr[i:])
        merged.extend(right_arr[j:])
        return merged

    sort_and_count(0, len(nums) - 1)
    return counts


# === SORT LIST (LC 148) - merge sort on a linked list ===
class ListNode:
    def __init__(self, val: int = 0, next: ListNode | None = None) -> None:
        self.val = val
        self.next = next


def sort_list(head: ListNode | None) -> ListNode | None:
    if not head or not head.next:
        return head

    # Split at the middle using slow/fast pointers.
    slow, fast, prev = head, head, head
    while fast and fast.next:
        prev = slow
        slow = slow.next
        fast = fast.next.next
    prev.next = None  # cut the list

    left = sort_list(head)
    right = sort_list(slow)
    return _merge_lists(left, right)


def _merge_lists(left: ListNode | None, right: ListNode | None) -> ListNode | None:
    dummy = ListNode(-1)
    cur = dummy
    while left and right:
        if left.val < right.val:
            cur.next = left
            left = left.next
        else:
            cur.next = right
            right = right.next
        cur = cur.next
    cur.next = left if left else right
    return dummy.next


# Helpers for the linked-list demo
def _build(arr: list[int]) -> ListNode | None:
    dummy = ListNode(0)
    cur = dummy
    for v in arr:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next


def _to_list(head: ListNode | None) -> list[int]:
    out: list[int] = []
    while head:
        out.append(head.val)
        head = head.next
    return out


# Example usage:
if __name__ == "__main__":
    print(merge_sort([5, 2, 6, 1]))       # [1, 2, 5, 6]
    print(count_smaller([5, 2, 6, 1]))    # [2, 1, 1, 0]
    print(count_smaller([-1]))            # [0]
    print(_to_list(sort_list(_build([4, 2, 1, 3]))))  # [1, 2, 3, 4]
