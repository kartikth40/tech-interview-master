# DATA STRUCTURE: LRU Cache (Hash Map + Doubly Linked List)
# DIFFICULTY: Medium | FREQUENCY: Very High (top SDE-2 design question at Google/Meta/Amazon)

# Least Recently Used (LRU) Cache - one of the most common SDE-2 interview questions.
# Supports get and put in O(1) time using a Hash Map + Doubly Linked List.

# Time Complexity:
# - get: O(1)
# - put: O(1)
# Space: O(capacity)

# When to use:
# - Cache with fixed capacity that evicts least recently used items
# - Any problem requiring O(1) access + O(1) eviction of oldest entry
# - System design: caching layer, browser history, page replacement

# NOTE: Python's collections.OrderedDict (or a plain dict in 3.7+, using move_to_end) gives an
# LRU cache in a few lines, and functools.lru_cache decorates functions directly. This explicit
# Hash Map + DLL implementation is what interviewers usually expect you to build from scratch.

from typing import Optional

# COMMON MISTAKES:
# - Forgetting to move a node to the front on GET (not just PUT).
# - Not using dummy head/tail sentinels, leading to null-pointer edge cases.
# - Evicting before checking capacity, or evicting the wrong end (LRU is next to tail).
# - Forgetting to delete the evicted key from the map.

# RELATED PROBLEMS:
# - LRU Cache (LC 146)
# - LFU Cache (LC 460)
# - Design Browser History (LC 1472)


class DLLNode:
    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key = key
        self.val = val
        self.prev: Optional["DLLNode"] = None
        self.next: Optional["DLLNode"] = None


class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.map: dict[int, DLLNode] = {}  # key -> DLLNode

        # Dummy head and tail to avoid None checks
        self.head = DLLNode()
        self.tail = DLLNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    # Move node to front (most recently used)
    def _add_to_front(self, node: DLLNode) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    # Remove node from its current position
    def _remove_node(self, node: DLLNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    # Move existing node to front
    def _move_to_front(self, node: DLLNode) -> None:
        self._remove_node(node)
        self._add_to_front(node)

    # Remove and return the least recently used node (before tail)
    def _remove_lru(self) -> DLLNode:
        lru = self.tail.prev
        self._remove_node(lru)
        return lru

    def get(self, key: int) -> int:
        if key not in self.map:
            return -1

        node = self.map[key]
        self._move_to_front(node)  # mark as recently used
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            # Update existing
            node = self.map[key]
            node.val = value
            self._move_to_front(node)
        else:
            # Add new
            if len(self.map) == self.capacity:
                # Evict LRU
                lru = self._remove_lru()
                del self.map[lru.key]

            new_node = DLLNode(key, value)
            self._add_to_front(new_node)
            self.map[key] = new_node


# Examples (only run when executed directly)
if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    print(cache.get(1))    # 1
    cache.put(3, 3)        # evicts key 2
    print(cache.get(2))    # -1 (evicted)
    cache.put(4, 4)        # evicts key 1
    print(cache.get(1))    # -1 (evicted)
    print(cache.get(3))    # 3
    print(cache.get(4))    # 4
