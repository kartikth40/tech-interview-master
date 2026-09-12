# DATA STRUCTURE: Singly Linked List & Common Operations
# DIFFICULTY: Medium | FREQUENCY: Very High (pointer manipulation staple at Google/Meta/Amazon)

# A singly linked list where each node points to the next node.
# Fundamental data structure for interviews - tests pointer manipulation skills.

# Time Complexity:
# - Access: O(n)
# - Search: O(n)
# - Insert at head: O(1)
# - Insert at tail: O(n) without tail pointer, O(1) with
# - Delete: O(n) to find, O(1) to remove

# When to use:
# - When you need O(1) insertion/deletion at known positions
# - When you don't need random access
# - Implementing stacks, queues, LRU cache
# - Problems involving pointer manipulation (reverse, merge, cycle detection)

from __future__ import annotations

# COMMON MISTAKES:
# - Losing the rest of the list by reassigning `next` before saving it.
# - Not using a dummy head node for merge/remove problems (causes edge-case bugs).
# - Off-by-one when advancing the fast pointer in "remove Nth from end".
# - Forgetting to terminate the reversed list (last node's next must become None).

# RELATED PROBLEMS:
# - Reverse Linked List (LC 206)
# - Linked List Cycle / Cycle II (LC 141 / LC 142)
# - Middle of the Linked List (LC 876)
# - Merge Two Sorted Lists (LC 21)
# - Remove Nth Node From End of List (LC 19)
# - Palindrome Linked List (LC 234)
# - Add Two Numbers (LC 2)


class ListNode:
    def __init__(self, val: int = 0, next: ListNode | None = None) -> None:
        self.val = val
        self.next = next


# === REVERSE LINKED LIST (iterative) ===
# The single most important linked list operation for interviews.
def reverse_list(head: ListNode | None) -> ListNode | None:
    prev: ListNode | None = None
    curr = head

    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt

    return prev


# === REVERSE LINKED LIST (recursive) ===
def reverse_list_recursive(head: ListNode | None) -> ListNode | None:
    if not head or not head.next:
        return head

    new_head = reverse_list_recursive(head.next)
    head.next.next = head
    head.next = None

    return new_head


# === DETECT CYCLE (Floyd's Tortoise & Hare) ===
def has_cycle(head: ListNode | None) -> bool:
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True

    return False


# === FIND CYCLE START ===
def detect_cycle(head: ListNode | None) -> ListNode | None:
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

        if slow is fast:
            # Move one pointer to head, advance both by 1
            slow = head
            while slow is not fast:
                slow = slow.next
                fast = fast.next
            return slow  # cycle start

    return None


# === FIND MIDDLE NODE ===
def middle_node(head: ListNode | None) -> ListNode | None:
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    return slow


# === MERGE TWO SORTED LISTS ===
def merge_two_lists(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
    dummy = ListNode(0)
    curr = dummy

    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next

    curr.next = l1 if l1 else l2
    return dummy.next


# === REMOVE NTH NODE FROM END ===
# Two pointers: advance fast by n, then move both until fast reaches end.
def remove_nth_from_end(head: ListNode | None, n: int) -> ListNode | None:
    dummy = ListNode(0, head)
    fast = dummy
    slow = dummy

    for _ in range(n + 1):
        fast = fast.next

    while fast:
        fast = fast.next
        slow = slow.next

    slow.next = slow.next.next
    return dummy.next


# === PALINDROME LINKED LIST ===
# Find middle -> reverse second half -> compare.
def is_palindrome(head: ListNode | None) -> bool:
    slow = head
    fast = head

    # Find middle
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # Reverse second half
    prev: ListNode | None = None
    while slow:
        nxt = slow.next
        slow.next = prev
        prev = slow
        slow = nxt

    # Compare both halves
    left, right = head, prev
    while right:
        if left.val != right.val:
            return False
        left = left.next
        right = right.next

    return True


# === ADD TWO NUMBERS (digits stored in reverse) ===
def add_two_numbers(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
    dummy = ListNode(0)
    curr = dummy
    carry = 0

    while l1 or l2 or carry:
        total = (l1.val if l1 else 0) + (l2.val if l2 else 0) + carry
        carry = total // 10
        curr.next = ListNode(total % 10)
        curr = curr.next

        if l1:
            l1 = l1.next
        if l2:
            l2 = l2.next

    return dummy.next


# Helper: build list from a Python list
def build_list(arr: list[int]) -> ListNode | None:
    dummy = ListNode(0)
    curr = dummy
    for val in arr:
        curr.next = ListNode(val)
        curr = curr.next
    return dummy.next


# Helper: linked list to a Python list
def to_array(head: ListNode | None) -> list[int]:
    result: list[int] = []
    while head:
        result.append(head.val)
        head = head.next
    return result


# Examples (only run when executed directly)
if __name__ == "__main__":
    list1 = build_list([1, 2, 4])
    list2 = build_list([1, 3, 4])
    print(to_array(merge_two_lists(list1, list2)))  # [1, 1, 2, 3, 4, 4]

    list3 = build_list([1, 2, 3, 4, 5])
    print(to_array(reverse_list(list3)))  # [5, 4, 3, 2, 1]

    print(middle_node(build_list([1, 2, 3, 4, 5])).val)  # 3

    print(is_palindrome(build_list([1, 2, 2, 1])))  # True
    print(is_palindrome(build_list([1, 2, 3])))     # False
